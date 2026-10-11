# Deenly production deployment

> Legacy SQLite deployment reference. Current PostgreSQL / CI/CD instructions:
> [Production runbook](PRODUCTION_RUNBOOK.md). Keep this reference for the
> retained pre-migration SQLite release, not for new production deployments.

## Invariants

- Use Compose project `deenlybot` and the existing `deenlybot_deenly_data` volume.
- Never replace the production SQLite database with a development database.
- Keep production bot token, owner ID, proxy and Django secret from the server.
- Build release-tagged images before stopping the old bot or worker.
- Stop only Deenly web/bot/worker while backing up and migrating the database.
- Audit all original application columns, row counts and fingerprints before
  starting the new processes. Added columns/tables are allowed; changed progress
  is not. `ops/verify_sqlite.py` opens the source database read-only.
- Keep the previous code, image and a consistent SQLite backup for rollback.
- Do not prune images, volumes or services belonging to other projects.

## Layout

The original deployment lives at `/home/DeenlyBot`. New source releases live
under `releases/`; `current` points to the verified active release. Backups live
under `backups/` with root-only access. Each release has a root `.env` with
non-secret image tags/volume name and `backend/.env` with the existing secrets.

```sh
cd /home/DeenlyBot/current
docker compose -p deenlybot -f docker-compose.yml -f docker-compose.production.yml ps
docker compose -p deenlybot -f docker-compose.yml -f docker-compose.production.yml logs --tail=80 web bot worker frontend
```

The production override uses Django's production settings and skips content
reseeding because this bot database is already populated. Reviewed translations,
favorites and existing auth data are audited along with progress. Run
`bootstrap_bot` only when intentionally initializing an empty installation.
The website and
API use one origin, secure session/CSRF cookies, and a single Gunicorn worker.
Frontend/API container ports remain loopback-only on the host.

## DNS and TLS

Domain: `deenly.uz`, with `www.deenly.uz` redirecting to the apex.
Cloudflare Free DNS uses proxied A/CNAME records. Assigned nameservers are
`alina.ns.cloudflare.com` and `boyd.ns.cloudflare.com`, configured at aHost.

Host Nginx uses `ops/nginx/deenly-http.conf` during ACME issuance, then
`ops/nginx/deenly-https.conf`. The certificate must cover both names. The HTTP
ACME location is retained for renewal; all other HTTP traffic redirects to HTTPS.
The host proxy replaces `X-Forwarded-Proto` with its actual connection scheme.

If registrar activation is pending, a narrowly scoped systemd timer checks the
public ACME probe every 30 minutes. It does not access the bot database or
secrets. Once both domains reach the configured origin, it obtains the domain's
certificate using the server's existing Certbot account, validates the names
and expiry, installs the HTTPS vhost, tests/reloads Nginx and disables its own
timer. It refuses to replace an externally modified Deenly vhost. The pending
HTTPS vhost rejects TLS handshakes so another site's default vhost is never
served for Deenly. Existing Certbot renewal timers remain untouched.
Where the host uses an authenticated outbound proxy, the TLS unit receives only
those existing proxy variables from a root-only `/etc/deenly/tls-proxy.env`;
the file is not part of source, images or the browser bundle. Docker dependency
builds receive proxy variables through predefined build arguments by name only.

Validate `nginx -t` before reloading. Check authoritative nameservers, public
DNS, the origin certificate, Cloudflare's encryption mode, public HTTPS,
application health and unauthenticated session behavior before calling a
deployment complete. Pending DNS/edge certificates are not successful deployment.

## Backup and progress verification

Run while the Deenly writers are stopped, using explicit checked paths:

```sh
python3 ops/verify_sqlite.py /var/lib/docker/volumes/deenlybot_deenly_data/_data/db.sqlite3 \
  --write-snapshot /home/DeenlyBot/backups/RELEASE/progress-before.json \
  --backup-to /home/DeenlyBot/backups/RELEASE/db.sqlite3
# Run migrations (without reseeding) with the new image against the same volume.
python3 ops/verify_sqlite.py /var/lib/docker/volumes/deenlybot_deenly_data/_data/db.sqlite3 \
  --compare /home/DeenlyBot/backups/RELEASE/progress-before.json
```

Never run `docker compose down -v` or restore a backup after new real user
activity without assessing the records that would be lost.
