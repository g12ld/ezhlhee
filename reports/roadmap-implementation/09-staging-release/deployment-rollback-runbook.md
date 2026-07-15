# Atomic production deployment and rollback runbook

## Preconditions

1. The exposed Telegram token is revoked in BotFather and a replacement is created.
2. `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are configured in Vercel Preview and Production. Values must never be written to a file, report, command log, or client-side response.
3. A new protected preview is built after the environment variables are configured.
4. The full staging validator passes, including one valid contact submission that receives a successful Telegram API response.
5. The owner explicitly approves production deployment.

## Atomic release

Promote the exact validated Vercel deployment to production so HTML, redirects, canonicals, robots.txt, sitemap.xml, headers, assets, and the server endpoint switch together. Do not upload or replace files individually. The production alias change is the release boundary.

## Immediate validation (start within five minutes)

1. Crawl all 119 canonical sitemap URLs and require HTTP 200.
2. Validate all 204 redirect rules plus the apex-to-`www` host redirect; require one hop and HTTP 301/308.
3. Verify representative old backlink URLs, internal links, canonical tags, robots.txt, sitemap.xml, headers, real 404 behavior, and contact submission.
4. Validate JSON-LD syntax and eligible critical pages with Google Rich Results Test.
5. Inspect the homepage, Salla, Zid, SEO, article index, contact page, and representative article in Search Console.
6. Submit the canonical sitemap only after these checks pass.

## Rollback trigger

Rollback immediately for a critical 404/5xx/soft-404, redirect loop or chain, robots/indexing block, wrong canonical, missing sitemap, security-header failure, broken navigation, invalid critical schema, or failed lead endpoint.

## Rollback method

Reassign the production alias to the previously known-good Vercel deployment. Re-run the immediate validation checklist after rollback. Preserve logs and prepare a corrective patch on the feature branch before any second release attempt.

## Validated candidate

Protected preview: `https://ezhlhee-4802eiajs-g12lds-projects.vercel.app`. It must be rebuilt after credentials are configured; the resulting deployment becomes the promotion candidate only after validation passes again.
