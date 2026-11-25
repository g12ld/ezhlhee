# Atomic production deployment and rollback runbook

## Preconditions

1. The WhatsApp Business account for +966 50 322 8029 is active and can receive new chats.
2. A new protected preview is built from the final source.
3. The full staging validator passes, including the homepage WhatsApp handoff check.
4. A manual preview contact-form test opens WhatsApp with the customer's request prefilled.
5. The owner explicitly approves production deployment.

## Atomic release

Promote the exact validated Vercel deployment to production so HTML, redirects, canonicals, robots.txt, sitemap.xml, headers, assets, and contact links switch together. Do not upload or replace files individually. The production alias change is the release boundary.

## Immediate validation (start within five minutes)

1. Crawl all 119 canonical sitemap URLs and require HTTP 200.
2. Validate all 204 redirect rules plus the apex-to-`www` host redirect; require one hop and HTTP 301/308.
3. Verify representative old backlink URLs, internal links, canonical tags, robots.txt, sitemap.xml, headers, real 404 behavior, and the WhatsApp contact flow.
4. Validate JSON-LD syntax and eligible critical pages with Google Rich Results Test.
5. Inspect the homepage, Salla, Zid, SEO, article index, contact page, and representative article in Search Console.
6. Submit the canonical sitemap only after these checks pass.

## Rollback trigger

Rollback immediately for a critical 404/5xx/soft-404, redirect loop or chain, robots/indexing block, wrong canonical, missing sitemap, security-header failure, broken navigation, invalid critical schema, or failed WhatsApp lead flow.

## Rollback method

Reassign the production alias to the previously known-good Vercel deployment. Re-run the immediate validation checklist after rollback. Preserve logs and prepare a corrective patch on the feature branch before any second release attempt.

## Validated candidate

Protected preview: `https://ezhlhee-50bcrj1ix-g12lds-projects.vercel.app`. It must be rebuilt from the final source; the resulting deployment becomes the promotion candidate only after validation passes again.
