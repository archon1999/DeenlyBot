# Production deployment

## Database modes

- Local development defaults to SQLite (`DATABASE_ENGINE=sqlite`). WAL and
  `IMMEDIATE` transactions remain enabled only for SQLite.
- Production requires PostgreSQL and rejects silent SQLite fallback. PostgreSQL
  17 runs in its own Deenly container, with no host port. Django, Telegram bot and
  Django Q share it. The application role cannot create databases or roles and is
  not a PostgreSQL superuser.
- `POSTGRES_PASSWORD_FILE` points to a Docker-mounted secret; credentials never
  enter source, images, frontend bundles or GitHub logs.
- CI runs the same backend tests against both engines, including concurrent
  idempotent writes and Telegram login.

## Production layout

Root: `/home/DeenlyBot`; Compose project: `deenlybot`.

- `releases/<commit-sha>`: immutable source release, private backend `.env`.
- `current`: verified active release link.
- `shared/postgres`: root-only parent holding Docker-readable password files.
- `shared/quran-foundation`: server-only optional API credential export.
- `backups/<timestamp>-<release>`: consistent SQLite backup or PostgreSQL dump,
  private exact fixture, row hashes and previous release pointer.
- Existing `deenlybot_deenly_data` SQLite volume is retained and mounted read-only
  after migration. New data lives in `deenlybot_deenly_postgres`.

Never run `docker compose down -v`, prune other projects, replace production with
a local database, or rotate live bot/DB/API credentials as a deployment side effect.

## First SQLite → PostgreSQL migration

`ops/deploy_release.py` builds/pulls images and starts PostgreSQL before stopping
any existing application service. It then:

1. Stops only Deenly writers/frontend for a short maintenance window.
2. Takes a consistent backup of the actual production SQLite volume.
3. Migrates a working copy, leaving the original SQLite file untouched.
4. Adds new curriculum/content without overwriting reviewed existing rows.
5. Audits every original column/record against the original SQLite snapshot.
6. Exports an exact private fixture; datetime microseconds, IDs, foreign keys,
   translations, auth users/sessions, favorites and progress are preserved.
7. Imports into an empty PostgreSQL application database. Import refuses to
   overwrite real data, runs atomically, checks constraints and resets sequences.
8. Verifies every exported row using canonical hashes, then starts the new web.
9. Switches `current` after local health succeeds and resumes public services.

The record audit happens before real bot/web/worker activity resumes. New
activity is allowed to change records afterward. Both databases/backups are
retained; no automatic database rollback occurs after public writers resume.

If a pre-exposure step fails, old services are restarted against the unchanged
original database. Failed imports are atomic; a retained provisional target is
never blindly cleared on retry.

## Ongoing CI/CD

Workflow: `.github/workflows/ci-cd.yml`.

- Pull requests: read-only permissions; quality/tests and container builds,
  without production keys, registry publishing or deployment.
- Main: tests → SHA-tagged GHCR images → serialized production deployment.
- Actions are pinned to immutable full commit SHAs.
- Repository secrets: `DEPLOY_HOST`, `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`.
  No bot, QF or database password is uploaded to GitHub.
- The dedicated SSH key has a forced command and cannot request a shell, PTY,
  forwarding or arbitrary root commands. `ops/ci_dispatch.py` accepts only a
  40-character commit SHA and validated source archive for this project.
- Registry authentication is release-scoped, root-only, and removed afterward.
- Every update takes a PostgreSQL dump and a private record audit before
  migrations and additive seeds. Existing rows must remain unchanged; compatible
  added columns and new permissions/content are allowed.

## Status and recovery

```sh
cd /home/DeenlyBot/current
docker compose -p deenlybot -f docker-compose.yml -f docker-compose.production.yml ps
docker compose -p deenlybot -f docker-compose.yml -f docker-compose.production.yml logs --tail=80 web bot worker frontend
```

Check saved `previous-release.txt`, audit and database type before restoring
anything. Restoring an older DB after new user activity would discard that
activity; assess and obtain explicit direction first. Restoring code alone does
not reverse database migrations.

## DNS and TLS

Domain: `deenly.uz` / `www.deenly.uz`. Existing host Nginx proxies only this
domain to Deenly's loopback frontend. TLS remains strict; another site's
certificate or an invalid certificate is not accepted.

The existing `deenly-tls-activation.timer` waits for registrar/DNS activation,
then performs normal ACME issuance, validates the certificate, tests Nginx and
activates HTTPS. Assigned Cloudflare nameservers: `alina.ns.cloudflare.com` and
`boyd.ns.cloudflare.com`. The user is activating DNS separately.

CI reports DNS activation as pending rather than claiming the public URL works
when DNS does not resolve. Once DNS is active, public HTTPS health must pass.
Origin health and public DNS/HTTPS are separate verification results.

### Shared-host default virtual host

`ops/nginx/host-default.conf` is the versioned copy of the host's
`/etc/nginx/conf.d/00-default-host.conf` (not the frontend container's
`ops/nginx/default.conf`). It returns HTTP 404 for unmatched hosts/IP access
and rejects unmatched HTTPS handshakes on IPv4 and IPv6. It never redirects
requests to Deenly. Named virtual hosts for all applications remain separate.

Every deployment verifies that this exact fallback is present, included and
passes `nginx -T` **before** preparing the release or changing containers/data.
Deploy never overwrites shared-host configuration: if the file is missing,
modified, symlinked or not included, deployment stops for operator review.
Normal releases and TLS activation leave this file untouched.

The forced SSH dispatcher executes `/usr/local/lib/deenly/deploy_release.py`,
not the copy inside a release. When updating this guard, back up that installed
helper, verify its existing contents, and install the reviewed repository copy
there as root (mode 0755); a Git push alone does not update this trusted helper.

For a fresh host or a missing-file recovery, first inspect `nginx -T` for
existing default listeners. Do not replace another application's default host.
With no competing defaults and the destination confirmed absent, install the
reviewed template as root, mode 0644, at the exact path above. Run `nginx -t`
before `systemctl reload nginx`. If validation fails, move only the newly added
file outside `conf.d` and retain it for diagnosis; do not reload invalid config.
Modified existing files require explicit reconciliation, not blind replacement.

Afterward verify raw-IP HTTP gives 404 without a Location header, raw-IP HTTPS
is rejected, Deenly's domain still works, and the other named virtual hosts'
status/redirect behavior matches their pre-change baseline. Browsers may cache
the old permanent redirect; use curl or a fresh browser session for verification.

## Publication

Private env files, secrets, databases, backups, runtime artifacts and vendor ZIPs
are ignored by Git and Docker. Scan staged files and all Git history before
making a repository public. Retain third-party license and attribution notices;
this repository does not place a blanket open-source license on template code.
