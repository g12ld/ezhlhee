# Authenticated Google Search Console baseline

Generated: 2026-07-15  
Property: `sc-domain:ezhalhe-sa.com`  
Access level: verified owner

## Executive baseline

- Search performance (2026-04-14 through 2026-07-13): 73 clicks, 2,156 impressions, 3.4% CTR, average position 16.
- Saudi Arabia accounts for 70 clicks and 1,795 impressions.
- Mobile accounts for 62 clicks and 1,431 impressions.
- Page indexing: 44 indexed and 60 not indexed.
- Indexing exclusions: 27 not found (404), 15 crawled but not indexed, 13 redirected pages, and 5 redirect errors.
- Crawl activity (90 days): 676 requests, 157 ms average response time; 33% of responses were 301 and 8% were 404.
- The submitted sitemap uses the apex host and reports 122 discovered pages. A stale HTTP homepage submission reports one error.
- Core Web Vitals has insufficient 90-day field data for both mobile and desktop; lab validation is therefore required during implementation.
- Search Console reports no manual actions and no security issues.

## Canonical-host decision evidence

The intended canonical origin for this implementation is `https://www.ezhalhe-sa.com` because:

- The `www` homepage generated 56 clicks, compared with 9 clicks for the apex homepage and 2 clicks for the apex `/index.html` duplicate.
- Both known external backlinks point to the `www` homepage.
- Google already recognizes the inspected `www` homepage canonical correctly.
- Crawl host reporting shows no current host problem for `www`, while the apex host has historical crawl problems.

No content path is removed by this decision. Existing paths are preserved or redirected in one hop to their exact canonical equivalent.

## Release invariants

- Preserve every valid production content path.
- Replace duplicate apex and `/index.html` variants with permanent one-hop redirects.
- Deploy redirects, canonicals, internal links, robots, sitemap, and security headers atomically.
- Do not submit the replacement sitemap or change production before staging validation and explicit release approval.
- Recheck the critical inspected URLs immediately after deployment, then monitor the property for 30 days.

## Evidence files

- `authenticated-baseline.json`: machine-readable summary and inspected URL results.
- `performance-queries.csv`: first 100 of 104 reported search queries.
- `performance-pages.csv`: all 43 reported search-result pages.
- `performance-countries.csv`: all 51 reported countries.
- `performance-devices.csv`: mobile, desktop, and tablet metrics.
- `indexing-404-examples.csv`: 27 Search Console 404 examples.
- `indexing-redirect-errors.csv`: 5 redirect-error examples.
- `indexing-redirected-pages.csv`: 13 redirected-page examples.
- `indexing-crawled-not-indexed.csv`: 15 crawled-but-not-indexed examples.

This package is a read-only baseline. It contains no account email, credential, secret, or authentication token.
