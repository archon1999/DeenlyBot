# Search visibility and public learning

## Scope and privacy

The root page remains the automatic guest dashboard. The server-rendered
`/learn/{uz,ru,en}/` library is the public search surface. It reads only published
names, Arabic lessons, Quran passages and duas with an actual translation in
the requested language. It never creates a guest, reads private progress or
renders profile data. Its HTML is identical for people and search crawlers.

Public pages provide real links, source attribution, language alternatives,
self-referencing canonical URLs, Open Graph and truthful LearningResource /
CollectionPage / BreadcrumbList structured data. No invented reviews, ratings,
scholarly endorsements or completion statistics are advertised. Summary
meanings remain marked as summaries. Existing editorial content is not rewritten.

`/sitemap.xml` is generated from published database records. Removed or
untranslated records are excluded. Unavailable public pages return real 404s.
Other unknown URLs also return HTTP 404 while displaying the branded app error
page. Personal app URLs have server-side `X-Robots-Tag: noindex, follow` and
client-side noindex metadata. Robots can fetch these URLs to read that directive.
`/api/`, `/auth/`, `/admin/` and `/health/` are disallowed in robots.txt; this is
not an authorization mechanism, and existing authentication remains required.

The canonical origin is fixed to https://deenly.uz rather than derived from
untrusted request headers. Public responses do not set session cookies. Nginx
routes only `/learn/` and `/sitemap.xml` to these anonymous Django views.
`ops/nginx/host-default.conf` and other projects' host virtual hosts are untouched.

## Google and AI search

Search Console URL-prefix property: `https://deenly.uz/`. Its verification meta
tag is intentionally public and must remain in the built root HTML. Submit
`https://deenly.uz/sitemap.xml` after production verification. Property ownership,
sitemap acceptance, indexing and ranking are separate states; do not claim one
from evidence of another. Google decides whether and when to index pages.

Google documents that AI Overviews / AI Mode use normal search eligibility:
https://developers.google.com/search/docs/appearance/ai-features

There is no special AI schema, payment or guaranteed placement. `llms.txt` is a
convenience map of public source material, not a Google ranking requirement.
No agent catalog or privileged automation API is advertised. Nonexistent crawl
resource URLs must return 404, never the SPA HTML fallback.

## Performance and checks

Baseline Google PageSpeed report (2026-10-22):
https://pagespeed.web.dev/analysis/https-deenly-uz/x5vfbgic67

- Mobile: performance 80, accessibility 94, best practices 100, SEO 91.
- Desktop: performance 89, accessibility 94, best practices 100, SEO 91.
- Field Core Web Vitals: insufficient data, not a passing or failing verdict.

The public reader has no JavaScript runtime, third-party widgets or required
web fonts. The application defers the Telegram SDK, preloads its main Arabic
and Latin fonts, and includes the entry dashboard in the initial dependency graph
to avoid a serial view-code download after startup. Other feature pages remain
lazy. Existing session and signed Telegram authentication behavior is retained.
Gzip is enabled inside the frontend container. Fingerprinted assets retain their
immutable cache policy. Dashboard headings and progress labels are accessible.

Run backend tests (especially `test_public_learning.py`), frontend typecheck,
lint, tests and build. Verify Nginx syntax and production responses for robots,
sitemap, all three library languages, a real content page, a missing content
page, a missing arbitrary URL, private routes and raw IP fallback. Re-run
PageSpeed on the dashboard and a public page on both device profiles; scores
vary and must not be inferred from local build success.

## Verified launch (2026-10-22)

Search Console ownership was verified with the approved Google account using
the HTML tag. Google successfully processed `/sitemap.xml` and discovered 646
URLs. This is discovery, not confirmation that all URLs are indexed.

The public learning home scored 100 performance, 100 accessibility, 100 best
practices and 100 SEO in the mobile lab report:
https://pagespeed.web.dev/analysis/https-deenly-uz-learn-uz/paikom459t?form_factor=mobile

Production checks confirmed three-language public HTML, lesson HTML, real 404s,
private-route noindex and raw-IP 404. CI passed SQLite and PostgreSQL tests.
