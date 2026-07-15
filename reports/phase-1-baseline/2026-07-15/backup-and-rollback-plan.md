# Backup and Rollback Plan

## Baseline anchors

- Git commit: `4505cfe89a5ae5766f94a0b7933ffeeb7b3edfa7`
- Pre-change file hashes: `file-checksums.txt`
- Baseline package hashes: `baseline-package-checksums.txt`
- Live and repository copies of `robots.txt` and `sitemap.xml`
- Redirect, canonical, metadata, structured-data, URL-status, and response-header inventories
- Production-serving platform: Vercel, inferred from live response headers

## Pre-release requirement

Before any production deployment, record the exact current production deployment identifier from the owner-controlled Vercel project. A request-level `x-vercel-id` is not a deployment identifier and is not sufficient for rollback.

## Atomic release requirement

The production alias may move only after the complete immutable candidate deployment passes all staging gates. Redirects, canonicals, internal links, robots, sitemap, structured data, and headers must ship in the same candidate release.

## Immediate rollback triggers

- Any baseline production URL unexpectedly returns 404, 5xx, or soft-404 content.
- A redirect chain, loop, irrelevant destination, or host conflict is introduced.
- Robots, canonical, or sitemap behavior blocks or misdirects indexable pages.
- Critical structured data becomes invalid.
- Material mobile rendering or Core Web Vitals regression appears.
- Search Console detects an unexpected indexing/canonical issue attributable to the release.

## Rollback procedure

1. Move the production alias back to the last verified immutable deployment.
2. Confirm homepage, critical service pages, top organic pages, robots, sitemap, and redirect samples.
3. Run the full baseline URL inventory against production and compare status/final URL/canonical behavior.
4. Record the incident and corrective patch before any further structural change.

No rollback, production deployment, commit, push, or merge has been performed during baseline generation.

