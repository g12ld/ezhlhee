# Search Console and organic monitoring: first 30 days

## Baseline

Use `01-search-console-baseline/` and the approved Phase 0 workbook as the before-state. Preserve query, page, country, device, indexing, redirect, 404, sitemap, crawl, manual-action, security, backlink, and critical-URL evidence.

## Schedule

- Release day: run immediate URL, crawl, redirect, schema, metadata, sitemap, and canonical validation; inspect critical URLs in Search Console.
- Days 1-3: check Page Indexing, Sitemaps, Crawl Stats, Manual Actions, Security Issues, critical URL Inspection, traffic, and priority rankings daily.
- Days 4-7: repeat daily for indexing/canonical anomalies; prepare a corrective patch before any structural follow-up if an unexpected issue appears.
- Days 8-14: review twice weekly, including Core Web Vitals and query/page comparison.
- Days 15-30: review weekly and produce the final before/after report on day 30.

## Required Search Console views

Coverage/Page Indexing, Core Web Vitals, Sitemaps, Manual Actions, Security Issues, Crawl Stats, Links, Performance, and URL Inspection for the homepage, Salla, Zid, SEO, article index, contact page, and representative cluster articles.

## Success criteria

- No production URLs are lost and no new indexing errors are introduced.
- No redirect chains, broken internal links, or Rich Results errors appear.
- Lab and field Core Web Vitals do not regress; target field values remain LCP < 2.5 s, INP < 200 ms, and CLS < 0.1.
- Organic traffic and priority rankings remain stable or improve relative to the approved baseline.
- Google accepts the 119-URL sitemap and selects the intended `https://www.ezhalhe-sa.com` canonicals.

If an unexpected indexing, canonical, traffic, or ranking issue appears, freeze additional structural changes, document the affected URLs and queries, and prepare a minimal corrective patch or rollback.
