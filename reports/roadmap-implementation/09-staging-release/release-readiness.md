# Production release readiness

**Status:** READY FOR OWNER RELEASE GATES

**Protected preview:** `https://ezhlhee-50bcrj1ix-g12lds-projects.vercel.app`

Production has not been modified. The preview is protected from indexing and represents the validated release candidate.

## Validation evidence

| Area | Status | Evidence |
|---|---|---|
| Information architecture | PASS | 16/16 checks |
| Security | PASS | 10/10 checks |
| Metadata and structured data | PASS | 14/14 checks |
| Content and internal links | PASS | 13/13 checks |
| Performance | PASS | 16/16 checks |
| UI, accessibility, and CRO | PASS | 19 file-level checks + 13 homepage CRO checks; failed_files=0 |
| Authority and E-E-A-T | PASS | 8/8 checks |
| Protected staging runtime | PASS | 17/17 checks |

## Runtime staging result

- 119/119 sitemap pages returned HTTP 200.
- 204/204 path redirects are permanent and have zero static chains; 12 runtime samples matched.
- The apex host has one atomic redirect to `www`.
- Required security headers, robots.txt, sitemap.xml, WebP delivery, and a real 404 passed.
- The contact API returns 405 for GET, 422 for invalid input, and 503 fail-closed while release credentials are absent.

## Owner release gates

- Revoke the exposed Telegram bot token in BotFather and create a replacement.
- Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID for Vercel Preview and Production without placing values in the repository.
- Approve the final production promotion after a credentialed preview contact-form test passes.

Google Rich Results URL testing, sitemap acceptance, intended-canonical confirmation, field INP/CrUX, and the 30-day ranking comparison are post-production measurements and are not represented as completed before release.
