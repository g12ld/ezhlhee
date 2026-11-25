# Smart advisor

The homepage combines a guided questionnaire with an Arabic chat and a WhatsApp order preview. Chat commands are handled in the browser: viewing a recommendation opens its details, and requesting WhatsApp expands a preview. The visitor opens WhatsApp and sends the message themselves.

`js/advisor-data.js` is the shared package catalog. `js/advisor-conversation.js` extracts common Arabic answers and picks the next unanswered question. Both the browser fallback and the API use it. `js/advisor-engine.js` builds recommendations and the WhatsApp summary; a package must cover the selected product range. Requests above 35 products explicitly require additional pricing.

## Configuration

Set `GEMINI_API_KEY` as a server-side environment variable in the existing Vercel project. Never place it in HTML, browser JavaScript, or committed files. `GEMINI_MODEL` overrides the default `gemini-3.8-flash`. The API uses Google's REST `generateContent` endpoint with an `x-goog-api-key` header and requests JSON output. Package facts come from the catalog rather than a duplicated prompt list.

Without a key, on provider errors, or after a timeout, the advisor continues using local conversation rules. The fallback handles common answers; flexible natural-language interpretation requires Gemini. This change has not been tested against a live Gemini account.

## Verification

Run `node --test scripts/test_advisor.js` for conversation flows, Arabic product counts, package capacity, request validation, provider failure, output sanitization, and chat action integration. Run `node scripts/validate_godmode_site.js` for the existing static site checks.

Before merging, run responsive browser checks at 375, 768, 1024, and 1440 pixels and Lighthouse on a working preview. The implementation session could not open its loopback preview, so these checks remain outstanding. The existing production site has not been deployed or changed by this work.
