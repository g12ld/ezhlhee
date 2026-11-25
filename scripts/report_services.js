"use strict";
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');const c=require('../data/services.json');
const lines=['# Service catalog release — 2026-11-25','','## Delivered','',
'- `/services.html`: 28 static service cards, five categories, Arabic search, price/name sorting, empty-state reset and shareable filter URLs.',
'- Each service has an independent canonical landing page, original store cover, scope, requirements, exclusions, specific FAQs, related services and store/WhatsApp CTAs.',
'- Three established URLs are reused: SEO, digital ads and store verification. No existing URL was removed.',
'- The homepage previews six services and links to all categories; shared navigation links to the catalog.',
'- Store package scope is now Launch 599 SAR / 10 products / 2 banners; Growth Silver 1099 SAR / 25 products / 3 banners; Gold Pro 1980 SAR / 35 products / 6 banners.',
'- The discontinued/unlisted Professional product 2132256496 is not presented as a currently verified service. Internal advisor IDs remain compatible with stored state.',
'- All 28 current product descriptions and three full category listings were read in the browser. Store category pagination was exhausted.',
'- Original covers were exported from the rendered store, optimized to 320/500 WebP, and saved under `/images/services/`. Source URLs and hashes are retained in `service-image-sources.json`.',
'- TikTok business-account conversion is explicitly distinguished from blue-badge verification. Government assistance fees are distinguished from official fees; official documentation links are provided where relevant.',
'- Variable-price services have no zero-price offer schema. No FAQPage schema, invented reviews, ranking promises or revenue guarantees.',
'','## Validation','',
'- HTML audit: 153 HTML files, zero errors/warnings.',
'- Metadata audit: 149 indexable pages, unique complete titles/descriptions, valid JSON-LD, 38 Service schemas, 148 breadcrumb pages.',
'- Automated tests: 11 passed (advisor and catalog filtering/search/sorting/scope).',
'- Browser responsive checks at 375/768/1024/1440 and Lighthouse remain pending. The previous local connection and Vercel preview certificate issue prevent claiming a visual or Lighthouse pass.',
'- Source is prepared on the feature branch; production deployment must follow the normal pull-request merge.',
'','## Rebuild','',
'Run `node scripts/build_services.js`, then `node scripts/sync_service_packages.js`. Committed covers and source metadata allow rebuilding without the temporary browser asset exports. Initial cover import requires the original browser-exported assets.',
'','## Source mapping','',
'| Service | Landing page | Displayed price (SAR) | Store product |','| --- | --- | ---: | --- |',
...c.services.map(s=>`| ${s.name} | ${s.path} | ${s.price===null?'By options':s.price} | [${s.id}](${s.sourceUrl}) |`),
'','Official references used to correct outdated store language:','',
'- https://mc.gov.sa/ar/mediacenter/News/Pages/29-03-23-02.aspx',
'- https://scbc.gov.sa/eservices/details/4d6e9d30-e989-4940-08ce-08dbf015747a',
'- https://freelance.sa/ar/faqs',
'- https://mc.gov.sa/ar/mediacenter/News/Pages/03-04-25-01.aspx',
'- https://www.sdb.gov.sa/ar/individuals-financing/cash-financing/faqs',''];
fs.writeFileSync(path.join(root,'docs/redesign-v2/services-release.md'),lines.join('\n'));
const bytes=c.services.reduce((n,s)=>n+fs.statSync(path.join(root,s.image.slice(1))).size+fs.statSync(path.join(root,s.imageSmall.slice(1))).size,0);
console.log(JSON.stringify({services:c.services.length,optimized_images:c.services.length*2,total_image_bytes:bytes}));
