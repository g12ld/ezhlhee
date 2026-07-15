# Ezhalha Phase 1 Baseline Package

Generated: 2026-07-15 (Asia/Riyadh)  
Production origin under review: `https://www.ezhalhe-sa.com`  
Baseline Git commit: `4505cfe89a5ae5766f94a0b7933ffeeb7b3edfa7`  
Working branch: `codex/phase-1-information-architecture`

## Release status

The repository and live technical baseline is generated. Production has not been modified, deployed, or reconfigured. No existing tracked site file has been changed. Phase 1 structural implementation remains paused pending review of this package.

Authenticated external evidence is not yet complete:

- The authenticated read-only Search Console check returned no access to the `https://www.ezhalhe-sa.com/` URL-prefix property. No Search Console data was read.
- No Search Console Links export or approved third-party backlink export is available.
- Therefore, no URL may be removed, renamed, consolidated, or redirected on backlink or ranking assumptions.

## Baseline scope

- 123 local HTML files inventoried.
- 479 live URLs and assets tested with redirect following and response-header capture.
- 122 sitemap entries captured, representing 120 unique URLs.
- 170 pre-existing project files hashed for rollback comparison.
- Metadata, canonicals, structured data, redirects, sitemap, robots, internal links, images, important files, headers, content signals, colors, keywords, and backlink gates captured.

## Critical findings and Phase 1 gates

1. **Canonical host conflict:** 110 pages declare non-`www` canonicals, 12 pages have no canonical, and only one local HTML page currently aligns with the intended `www` host.
2. **Sitemap conflict:** every sitemap entry uses the non-`www` host and therefore redirects before reaching the selected production origin. Two extensionless coupon URLs finish at 404. Two service URLs are duplicated.
3. **Internal-link debt:** 1,337 internal link occurrences were recorded. There are 78 broken internal-link occurrences, all originating from `blog.html`. There are 778 redirected internal-link occurrences; 755 point to `/index.html` instead of `/`.
4. **Redirect relevance risk:** 25 unique redirect rules exist in each hosting configuration. Twenty-four source URLs map to the homepage; 22 legacy service/article sources require relevance review because blanket homepage redirects can be treated as soft 404s.
5. **Metadata incompleteness:** 120 pages lack a complete Open Graph set and 121 lack a complete Twitter set. Two files lack titles and descriptions. Author data is missing on 121 pages; publication and modification dates are missing on all 123 local HTML files.
6. **Structured-data coverage:** only nine pages contain JSON-LD. The captured JSON is syntactically valid, but seven pages contain prohibited `FAQPage` markup. LocalBusiness usage requires physical-location verification before it can be retained.
7. **Image performance debt:** 264 image occurrences were recorded; 258 lack explicit width and height, and 230 have no `loading` attribute. The homepage Open Graph image is missing in both the repository and production.
8. **Important files:** `robots.txt`, `sitemap.xml`, and Google verification are present. File-based favicon, manifest files, browserconfig, and Bing verification are absent; optional verification files must not be fabricated. The inline homepage favicon requires brand-color compliance review.
9. **Brand conflict:** 73 distinct hexadecimal colors are present and 71 are outside the approved five-color identity. The required Primary, Secondary, and CTA colors currently have zero exact occurrences; White and Text are present.
10. **Security blocker:** the live homepage exposes a Telegram bot credential and chat destination in client-side code. Secret values are intentionally excluded from this package. Rotation and a server-side form endpoint require separate approval before implementation.
11. **Performance risk:** the Phase 0 mobile diagnostic did not meet LCP or CLS targets. The Phase 1 throttled CDP diagnostic also confirms a very large DOM and high main-thread/layout cost. These are diagnostic baselines, not CrUX or Lighthouse reports.

## Search Console and backlink evidence required before URL decisions

Please provide exports or authorized property access for:

- Search performance by query and page for the last 28 and 90 days, segmented by Saudi Arabia and device where available.
- Page indexing, sitemap status, Core Web Vitals, crawl statistics, manual actions, and security issues.
- URL Inspection results for the homepage, core service pages, city pages, blog index, articles index, and highest-traffic articles.
- Search Console Links: top linked pages, top linking sites, and top linking text.
- Optional Ahrefs, Semrush, or Majestic exports for referring pages/domains and linked target URLs.

Until this evidence is attached, every production URL is marked `url_change_allowed = No` in `backlink-targets.csv`.

## Package contents

The machine-readable package includes:

- URL, metadata, canonical, redirect, sitemap, header, content, image, color, and important-file inventories.
- Complete captured JSON-LD blocks and JSON validation results.
- Internal-link graph, broken links, redirected links, and orphan candidates.
- Live and repository snapshots of `robots.txt` and `sitemap.xml`.
- Pre-existing project checksums, package checksums, and a package manifest.
- Search Console, keyword, and backlink evidence gates.
- Performance, security, accessibility, rollback, change, and SEO-decision records.

## Review outcome required

Approval of this baseline permits Phase 1 implementation planning only after the missing Search Console and backlink evidence is supplied or the owner explicitly accepts a no-URL-change Phase 1 scope. Production behavior remains unchanged until a later, separately validated release is approved.

