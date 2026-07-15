# Approved roadmap requirement traceability

**Status:** READY_FOR_OWNER_RELEASE_GATES

**Requirements traced:** 92

## Status summary

- BLOCKED_BY_OWNER_CREDENTIAL: 1
- NOT_APPLICABLE_CURRENT_SCALE: 2
- NOT_APPLICABLE_NO_OWNER_KEY: 1
- NOT_APPLICABLE_NO_SITE_SEARCH: 1
- NOT_APPLICABLE_SINGLE_LANGUAGE: 1
- NOT_APPLICABLE_UNVERIFIED_ENTITY: 1
- OWNER_ACTION_REQUIRED: 1
- OWNER_APPROVAL_REQUIRED: 1
- PASS: 76
- POST_RELEASE: 7

## Requirement matrix

| ID | Area | Requirement | Status | Evidence / remaining gate |
|---|---|---|---|---|
| REQ-001 | Baseline | Complete pre-change URL, metadata, canonical, schema, redirect, sitemap and checksum package | PASS | reports/phase-1-baseline/2026-07-15/ |
| REQ-002 | Baseline | Approved Excel workbook preserved | PASS | outputs/ezhalha-phase1-baseline-20260715/ezhalha-phase1-baseline.xlsx |
| REQ-003 | Baseline | Authenticated Search Console performance/indexing baseline | PASS | 01-search-console-baseline/authenticated-baseline.json |
| REQ-004 | Baseline | Keyword and ranking baseline captured for before/after comparison | PASS | 01-search-console-baseline/performance-queries.csv |
| REQ-005 | Baseline | Backlink targets identified and protected | PASS | 01-search-console-baseline/authenticated-baseline.json; Phase 0 backlink-targets.csv |
| REQ-006 | Release safety | All work performed on a separate feature branch | PASS | codex/phase-1-information-architecture |
| REQ-007 | Release safety | Protected staging environment is non-indexable | PASS | https://ezhlhee-mxb4rvkuv-g12lds-projects.vercel.app |
| REQ-008 | Release safety | Production remains outside the implementation release | PASS | 09-staging-release/staging-validation.json |
| REQ-009 | Release safety | Atomic deployment and immediate rollback procedure documented | PASS | 09-staging-release/deployment-rollback-runbook.md |
| REQ-010 | Release safety | Detailed file/redirect/canonical/SEO decision logs maintained | PASS | 09-staging-release/file-change-inventory.csv; 02-information-architecture/*.csv; change-log.md |
| REQ-011 | Sitemap | Sitemap rebuilt from canonical indexable URLs | PASS | sitemap.xml; 02-information-architecture/sitemap-inventory.csv |
| REQ-012 | Sitemap | Duplicates, redirects and missing/404 destinations excluded | PASS | 02-information-architecture/validation.json |
| REQ-013 | Sitemap | Every URL has an automated valid lastmod | PASS | sitemap.xml; scripts/apply_information_architecture.py |
| REQ-014 | Sitemap | Split to a sitemap index before standard size limits | NOT_APPLICABLE_CURRENT_SCALE | 02-information-architecture/implementation-manifest.json; Current sitemap has 119 URLs; index policy is documented before 50,000 URLs/50 MB. |
| REQ-015 | Sitemap | Publish gzip members when sitemap index scale requires them | NOT_APPLICABLE_CURRENT_SCALE | 02-information-architecture/implementation-manifest.json; Current small XML uses CDN HTTP compression; gzip-member policy is documented for indexed scale. |
| REQ-016 | Robots | robots.txt references the canonical sitemap | PASS | robots.txt |
| REQ-017 | Robots | Non-public endpoint and legacy fragment crawl rules are explicit | PASS | robots.txt |
| REQ-018 | Canonicals | A single www HTTPS canonical origin is used | PASS | vercel.json; 02-information-architecture/canonical-map.csv |
| REQ-019 | Canonicals | All 119 indexable pages have one exact self-canonical | PASS | 02-information-architecture/validation.json |
| REQ-020 | Redirects | Complete redirect map exists | PASS | 02-information-architecture/redirect-map.csv |
| REQ-021 | Redirects | All redirect rules are permanent | PASS | vercel.json; firebase.json |
| REQ-022 | Redirects | Redirect chains are eliminated | PASS | 02-information-architecture/validation.json |
| REQ-023 | Redirects | Redirect destinations exist and known Search Console exclusions are covered | PASS | 02-information-architecture/validation.json |
| REQ-024 | URL preservation | No indexable production content URL is removed | PASS | 09-staging-release/staging-crawl.csv |
| REQ-025 | URL preservation | Existing legacy /_new_testi.html URL remains available | PASS | 09-staging-release/staging-validation.json |
| REQ-026 | URL preservation | Unknown URLs return a genuine 404 | PASS | 09-staging-release/staging-validation.json |
| REQ-027 | Search Console | Coverage/Page Indexing, sitemap, CWV, crawl, manual action, security and URL Inspection baseline captured | PASS | 01-search-console-baseline/authenticated-baseline.json |
| REQ-028 | Search Console | Critical pre-release URL Inspection completed | PASS | 09-staging-release/search-console-pre-release-check.json |
| REQ-029 | Search Console | Submit the new sitemap and confirm acceptance | POST_RELEASE | 09-staging-release/search-console-30-day-monitoring.md; Must occur only after atomic production validation. |
| REQ-030 | Search Console | Confirm Google-selected canonical URLs | POST_RELEASE | 09-staging-release/search-console-30-day-monitoring.md; Requires public production recrawl. |
| REQ-031 | Search Console | Monitor all approved Search Console areas for 30 days | POST_RELEASE | 09-staging-release/search-console-30-day-monitoring.md; The monitoring clock starts after production release. |
| REQ-032 | Structured data | Organization and WebSite schema cover all indexable pages | PASS | 04-metadata-structured-data/metadata-schema-map.csv |
| REQ-033 | Structured data | Service schema covers all 13 service pages | PASS | 04-metadata-structured-data/validation.json |
| REQ-034 | Structured data | BreadcrumbList covers all 118 non-home indexable pages | PASS | 04-metadata-structured-data/validation.json |
| REQ-035 | Structured data | Article covers all 101 articles | PASS | 04-metadata-structured-data/validation.json |
| REQ-036 | Structured data | Product/Offer is present where package products are represented | PASS | index.html; 04-metadata-structured-data/validation.json |
| REQ-037 | Structured data | Prohibited FAQPage schema is removed | PASS | 04-metadata-structured-data/validation.json |
| REQ-038 | Structured data | LocalBusiness is used only if a verified public office exists | NOT_APPLICABLE_UNVERIFIED_ENTITY | 04-metadata-structured-data/implementation-manifest.json; Omitted to avoid an unsupported physical-location claim. |
| REQ-039 | Structured data | SearchAction is used only if working site search exists | NOT_APPLICABLE_NO_SITE_SEARCH | 04-metadata-structured-data/implementation-manifest.json; Omitted because the site has no working search action. |
| REQ-040 | Structured data | Google Rich Results required fields pass static validation | PASS | 04-metadata-structured-data/validation.json |
| REQ-041 | Structured data | Validate eligible public URLs in Google Rich Results Test | POST_RELEASE | 09-staging-release/deployment-rollback-runbook.md; Google cannot crawl the protected noindex preview; execute immediately after release. |
| REQ-042 | Metadata | Unique bounded title and meta description on all 119 pages | PASS | 04-metadata-structured-data/metadata-schema-map.csv |
| REQ-043 | Metadata | Complete Open Graph and Twitter large-card metadata | PASS | 04-metadata-structured-data/validation.json |
| REQ-044 | Metadata | Canonical-aligned 1200x630 social image exists | PASS | images/og-cover.webp |
| REQ-045 | Metadata | Hreflang is added if the site becomes multilingual | NOT_APPLICABLE_SINGLE_LANGUAGE | 04-metadata-structured-data/validation.json; Arabic-only site; hreflang is intentionally omitted. |
| REQ-046 | Browser files | Favicon, manifest aliases and browserconfig are valid and served | PASS | favicon.svg; site.webmanifest; manifest.json; browserconfig.xml |
| REQ-047 | Browser files | Google verification file is preserved | PASS | google387142411d334808.html |
| REQ-048 | Browser files | Bing verification | NOT_APPLICABLE_NO_OWNER_KEY | Phase 0 important-files-inventory.csv; Optional verification file is not fabricated without an owner-provided key. |
| REQ-049 | Images | Every image has intrinsic width and height | PASS | 06-performance/image-optimization-map.csv |
| REQ-050 | Images | Every image has explicit loading and async decoding | PASS | 06-performance/validation.json |
| REQ-051 | Images | Responsive WebP variants and srcset/sizes are implemented | PASS | images/responsive/; 06-performance/image-optimization-map.csv |
| REQ-052 | Images | Critical LCP image receives eager/high fetch priority | PASS | index.html |
| REQ-053 | Performance | Mobile Lighthouse LCP is below 2.5 seconds | PASS | 09-staging-release/lighthouse-summary.json |
| REQ-054 | Performance | Mobile Lighthouse CLS is below 0.1 | PASS | 09-staging-release/lighthouse-summary.json |
| REQ-055 | Performance | Field INP is below 200 ms | POST_RELEASE | 09-staging-release/search-console-30-day-monitoring.md; Search Console reports insufficient current field data; measure during the 30-day window. |
| REQ-056 | Performance | Unused JavaScript and render-blocking resources are eliminated in Lighthouse | PASS | 09-staging-release/lighthouse-mobile-performance-release.report.json |
| REQ-057 | Performance | CSS is optimized without removing deferred/interactive component styling | PASS | index.html; 09-staging-release/lighthouse-mobile-performance-release.report.json |
| REQ-058 | Performance | DOM/layout work is reduced while retaining all approved content | PASS | 07-ui-accessibility-cro/validation.json; release-browser-validation.json |
| REQ-059 | Performance | Event listeners are deduplicated/passive/throttled | PASS | 06-performance/validation.json |
| REQ-060 | Performance | External render-blocking font dependency is removed and critical image is preloaded | PASS | index.html; 06-performance/validation.json |
| REQ-061 | Accessibility | Semantic main/navigation landmarks and one H1 are enforced | PASS | 07-ui-accessibility-cro/validation.json |
| REQ-062 | Accessibility | Labels, ARIA names/states and live form status are present | PASS | index.html; 03-security/validation.json |
| REQ-063 | Accessibility | Keyboard navigation, focus restoration, Escape and dialog behavior pass | PASS | 07-ui-accessibility-cro/viewport-validation.json |
| REQ-064 | Accessibility | Exact brand colors and computed contrast pass | PASS | 07-ui-accessibility-cro/brand-color-inventory.csv; viewport-validation.json |
| REQ-065 | Accessibility | Mobile-first RTL layouts pass at 375, 768, 1024 and 1440 | PASS | 07-ui-accessibility-cro/viewport-validation.json |
| REQ-066 | Accessibility | Mobile and desktop Lighthouse accessibility score 100 | PASS | 09-staging-release/lighthouse-summary.json |
| REQ-067 | Content | Every article has visible author, review/update date and official sources | PASS | 08-authority-eeat/content-change-map.csv |
| REQ-068 | Content | Regulated topics contain limitations/disclaimers | PASS | 08-authority-eeat/validation.json |
| REQ-069 | Content | All 101 articles are assigned to crawlable Saudi-intent topic clusters | PASS | 05-content-architecture/content-cluster-map.csv |
| REQ-070 | Content | Contextual internal links and topic hub navigation are complete | PASS | 05-content-architecture/validation.json |
| REQ-071 | Content | No broken, redirecting or orphaned indexable pages remain | PASS | 05-content-architecture/validation.json |
| REQ-072 | Content | Authority/service pages are substantive and unsupported guarantees are removed | PASS | 08-authority-eeat/validation.json |
| REQ-073 | UI/UX and CRO | Homepage hierarchy and primary Gold Pro hero CTA are implemented | PASS | index.html; 07-ui-accessibility-cro/validation.json |
| REQ-074 | UI/UX and CRO | Package comparison and mobile deferred comparison remain available | PASS | index.html; 07-ui-accessibility-cro/validation.json |
| REQ-075 | UI/UX and CRO | Portfolio, testimonials, services and trust proof remain complete | PASS | 09-staging-release/release-browser-validation.json |
| REQ-076 | UI/UX and CRO | Lana, Lara Alsaad Boutique and Duk Altayeb appear first as Gold Pro Salla work | PASS | index.html; images/*-salla-gold-pro.webp |
| REQ-077 | UI/UX and CRO | WhatsApp and consultation/contact conversion paths remain visible | PASS | index.html |
| REQ-078 | UI/UX and CRO | Intrusive automatic popup behavior is removed | PASS | 07-ui-accessibility-cro/viewport-validation.json |
| REQ-079 | Security | Client-side Telegram secrets and Telegram calls are removed | PASS | 03-security/validation.json |
| REQ-080 | Security | Contact submission uses a same-origin server endpoint with origin/rate/honeypot/timing defenses | PASS | api/contact.js; 03-security/validation.json |
| REQ-081 | Security | Telegram response payload is validated and failures remain fail-closed | PASS | scripts/test_contact_endpoint.js; 09-staging-release/staging-validation.json |
| REQ-082 | Security | CSP, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy and related headers pass | PASS | vercel.json; 09-staging-release/staging-validation.json |
| REQ-083 | Security | Revoke the compromised token and configure replacement preview/production secrets | OWNER_ACTION_REQUIRED | 03-security/validation.json; Requires owner-controlled BotFather and Vercel environment access; the endpoint intentionally returns 503 until complete. |
| REQ-084 | Security | Run one credentialed preview form-delivery test | BLOCKED_BY_OWNER_CREDENTIAL | 09-staging-release/deployment-rollback-runbook.md; Run after replacement environment variables exist and before production approval. |
| REQ-085 | Validation | All 119 sitemap pages pass the protected preview crawl | PASS | 09-staging-release/staging-crawl.csv |
| REQ-086 | Validation | All 204 redirect rules are static-validated and runtime samples pass | PASS | 09-staging-release/redirect-runtime-sample.csv |
| REQ-087 | Validation | Mobile Lighthouse performance/accessibility/best-practices/SEO gates pass | PASS | 09-staging-release/lighthouse-summary.json |
| REQ-088 | Validation | Desktop Lighthouse scores 100 in all four categories | PASS | 09-staging-release/lighthouse-summary.json |
| REQ-089 | Validation | Repository implementation and protected staging requirement audit passes | PASS | 10-completion-audit/completion-audit.json |
| REQ-090 | Production gate | Explicitly approve atomic production promotion | OWNER_APPROVAL_REQUIRED | 09-staging-release/deployment-rollback-runbook.md; Production deployment is intentionally outside the current objective boundary. |
| REQ-091 | Post-release | Immediate crawl/redirect/canonical/schema/Search Console validation | POST_RELEASE | 09-staging-release/deployment-rollback-runbook.md; Start within five minutes of the production alias switch. |
| REQ-092 | Post-release | No new indexing errors; traffic/rankings stable or improved | POST_RELEASE | 09-staging-release/search-console-30-day-monitoring.md; Compare with the authenticated baseline for 30 days; prepare a corrective patch before further structural work if needed. |

No item marked POST_RELEASE or OWNER_ACTION_REQUIRED is represented as completed before its evidence can exist. Production remains unchanged.
