# Phase 1 Baseline Review Checklist

Phase 1 implementation must remain paused until the owner reviews this package and explicitly approves the baseline.

## Package review

- [ ] Confirm the URL inventory is complete enough to serve as the rollback comparison set.
- [ ] Confirm the metadata, canonical, structured-data, redirect, sitemap, robots, image, content, and internal-link inventories are accepted as the pre-change baseline.
- [ ] Confirm the existing file checksum inventory is accepted as the repository rollback reference.
- [ ] Confirm the documented live-site findings match the current production state.
- [ ] Confirm the preferred canonical host before any host normalization is implemented.
- [ ] Confirm whether `_new_testi.html`, `404.html`, and other suspected non-indexable/test URLs should remain indexable, be redirected, or receive `noindex` treatment. No action will be taken without approval.

## Required owner-supplied evidence

- [ ] Grant access to the URL-prefix Search Console property for `https://www.ezhalhe-sa.com/`, or provide exports for Performance, Page Indexing, Sitemaps, Core Web Vitals, Crawl Stats, Manual Actions, Security Issues, and URL Inspection for critical pages.
- [ ] Provide the current keyword/ranking export covering the agreed Saudi target queries.
- [ ] Provide a backlink export from Search Console Links, Ahrefs, Semrush, Majestic, or an equivalent trusted source.
- [ ] Identify the critical URLs that must be checked with URL Inspection immediately before and after release.

The Search Console account available during this audit did not have access to the requested property. The backlink list therefore contains URL targets and preservation gates, not verified backlink counts.

## Critical decisions before implementation

- [ ] Approve the canonical host (`www` or non-`www`) and the corresponding redirect policy.
- [ ] Approve every proposed URL change and its one-hop permanent redirect before implementation.
- [ ] Approve the containment and rotation plan for the exposed Telegram credential before any production security change.
- [ ] Confirm the staging environment and atomic deployment/rollback mechanism.
- [ ] Confirm that redirects, canonicals, robots, sitemap, headers, and internal-link updates will ship in the same validated release.

## Approval statement

Approval of this checklist authorizes Phase 1 implementation on the feature branch/staging environment only. It does not authorize a production deployment, Phase 2, deletion of content, or any unlisted URL change.
