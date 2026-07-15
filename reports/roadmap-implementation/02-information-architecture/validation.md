# Information architecture validation

Result: 15/15 checks passed.

| Check | Result | Evidence |
|---|---|---|
| redirect-map-count | PASS | map=204, vercel_path_rules=204 |
| redirect-sources-unique | PASS | unique=204, total=204 |
| redirect-status-permanent | PASS | All redirect-map and Vercel path rules are permanent |
| redirect-destinations-exist | PASS | missing=0 |
| no-redirect-chains | PASS | chains=0 |
| canonical-host-rule | PASS | host_rules=1 |
| firebase-redirect-parity | PASS | mismatched_targets=0 |
| search-console-exclusions-covered | PASS | checked=32, uncovered=0 |
| canonical-coverage | PASS | valid=119, errors=0 |
| sitemap-valid-canonical-urls | PASS | urls=119, unique=119, missing=0, redirected=0 |
| sitemap-lastmod-complete | PASS | lastmods=119 |
| blog-legacy-links-repaired | PASS | legacy=0, broken=0 |
| robots-sitemap-canonical | PASS | Robots references the canonical sitemap |
| error-page-noindex | PASS | 404 page is noindex and has no canonical declaration |
| telegram-token-scan | PASS | potential_live_token_patterns=0 |
