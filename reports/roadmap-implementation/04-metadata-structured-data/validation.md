# Metadata and structured data validation

Result: 14/14 checks passed.

| Check | Result | Evidence |
|---|---|---|
| indexable-page-count | PASS | pages=119 |
| metadata-complete-and-bounded | PASS | valid=119, errors=0 |
| metadata-unique | PASS | duplicate_titles=0, duplicate_descriptions=0 |
| structured-data-json-valid | PASS | errors=0 |
| google-rich-result-required-fields | PASS | errors=0 |
| faqpage-prohibited | PASS | pages=0 |
| article-schema-coverage | PASS | articles=101, expected=101 |
| service-schema-coverage | PASS | services=13 |
| breadcrumb-schema-coverage | PASS | pages=118 |
| required-schema-types | PASS | types=Article|BreadcrumbList|City|CollectionPage|ContactPoint|Country|ImageObject|ItemList|ListItem|Offer|Organization|Product|Service|WebPage|WebSite |
| social-image-present | PASS | bytes=27084 |
| single-language-hreflang-decision | PASS | Arabic-only site: hreflang intentionally omitted |
| browser-identity-metadata-coverage | PASS | valid=119, errors=0 |
| browser-identity-files-valid | PASS | favicon.svg, site.webmanifest, manifest.json, browserconfig.xml, and logo asset |

## Deployment validation still required

- Run Google Rich Results Test against the staged homepage, one service page, and one article.
- Confirm the staged social preview image is publicly fetchable at 1200×630.
- Reinspect critical pages in Search Console after production release.
