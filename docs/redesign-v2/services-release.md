# Service catalog release — 2026-11-25

## Delivered

- `/services.html`: 28 static service cards, five categories, Arabic search, price/name sorting, empty-state reset and shareable filter URLs.
- Each service has an independent canonical landing page, original store cover, scope, requirements, exclusions, specific FAQs, related services and store/WhatsApp CTAs.
- Three established URLs are reused: SEO, digital ads and store verification. No existing URL was removed.
- The homepage previews six services and links to all categories; shared navigation links to the catalog.
- Store package scope is now Launch 599 SAR / 10 products / 2 banners; Growth Silver 1099 SAR / 25 products / 3 banners; Gold Pro 1980 SAR / 35 products / 6 banners.
- The discontinued/unlisted Professional product 2132256496 is not presented as a currently verified service. Internal advisor IDs remain compatible with stored state.
- All 28 current product descriptions and three full category listings were read in the browser. Store category pagination was exhausted.
- Original covers were exported from the rendered store, optimized to 320/500 WebP, and saved under `/images/services/`. Source URLs and hashes are retained in `service-image-sources.json`.
- TikTok business-account conversion is explicitly distinguished from blue-badge verification. Government assistance fees are distinguished from official fees; official documentation links are provided where relevant.
- Variable-price services have no zero-price offer schema. No FAQPage schema, invented reviews, ranking promises or revenue guarantees.

## Validation

- HTML audit: 153 HTML files, zero errors/warnings.
- Metadata audit: 149 indexable pages, unique complete titles/descriptions, valid JSON-LD, 38 Service schemas, 148 breadcrumb pages.
- Automated tests: 11 passed (advisor and catalog filtering/search/sorting/scope).
- Browser responsive checks at 375/768/1024/1440 and Lighthouse remain pending. The previous local connection and Vercel preview certificate issue prevent claiming a visual or Lighthouse pass.
- Source is prepared on the feature branch; production deployment must follow the normal pull-request merge.

## Rebuild

Run `node scripts/build_services.js`, then `node scripts/sync_service_packages.js`. Committed covers and source metadata allow rebuilding without the temporary browser asset exports. Initial cover import requires the original browser-exported assets.

## Source mapping

| Service | Landing page | Displayed price (SAR) | Store product |
| --- | --- | ---: | --- |
| باقة انطلاقة لتصميم متجر سلة | /services/launch-package.html | 599 | [377589337](https://ezhalhe.com/p377589337-%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D8%A8%D8%A7%D9%82%D8%A9-%D8%A7%D9%84%D8%A7%D9%86%D8%B7%D9%84%D8%A7%D9%82%D8%A9) |
| باقة نمو الفضية لتصميم متجر سلة | /services/growth-package.html | 1099 | [560117077](https://ezhalhe.com/p560117077-%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D8%A8%D8%A7%D9%82%D8%A9-%D9%86%D9%85%D9%88-%D8%A7%D9%84%D9%81%D8%B6%D9%8A%D8%A9) |
| الباقة الذهبية برو لتصميم المتاجر | /services/gold-package.html | 1980 | [1934611542](https://ezhalhe.com/p1934611542-%D8%AA%D8%B7%D9%88%D9%8A%D8%B1-%D9%88%D8%A7%D9%84%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D9%85%D8%AA%D8%AC%D8%B1-%D8%A7%D9%84%D8%A7%D9%84%D9%83%D8%AA%D8%B1%D9%88%D9%86%D9%8A-%D8%A7%D9%84%D8%A8%D8%A7%D9%82%D8%A9-%D8%A7%D9%84%D8%B0%D9%87%D8%A8%D9%8A%D8%A9-%D8%A8%D8%A7%D9%82%D8%A9-%D8%A8%D8%B1%D9%88) |
| تصميم متجر WooCommerce على ووردبريس | /services/woocommerce-store-design.html | 3000 | [305127015](https://ezhalhe.com/p305127015-%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D9%85%D8%AA%D8%AC%D8%B1-%D8%A5%D9%84%D9%83%D8%AA%D8%B1%D9%88%D9%86%D9%8A-%D8%A7%D8%AD%D8%AA%D8%B1%D8%A7%D9%81%D9%8A-%D8%B9%D9%84%D9%89-%D9%88%D9%88%D8%B1%D8%AF%D8%A8%D8%B1%D9%8A%D8%B3---woocommerce-%D8%A8%D9%83%D8%A7%D9%85%D9%84-%D8%A7%D9%84%D9%85%D9%85%D9%8A%D8%B2%D8%A7%D8%AA) |
| تحسين SEO لمتاجر سلة وزد | /search-engine-optimization.html | 359 | [1541556300](https://ezhalhe.com/p1541556300-%D8%AA%D8%AD%D8%B3%D9%8A%D9%86-%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D9%81%D9%8A-%D9%85%D8%AD%D8%B1%D9%83%D8%A7%D8%AA-%D8%A8%D8%AD%D8%AB-%D9%82%D9%88%D9%82%D9%84-%D8%A7%D9%84%D8%B3%D9%8A%D9%88-seo) |
| إنشاء مدونة SEO داخل متجر سلة | /services/salla-seo-blog.html | 399 | [1605247093](https://ezhalhe.com/p1605247093-%D9%85%D8%AF%D9%88%D9%86%D8%A9-%D9%85%D8%AD%D8%B3%D9%91%D9%86%D8%A9-%D8%A8%D8%A7%D9%84%D9%80seo-%D8%AF%D8%A7%D8%AE%D9%84-%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D9%81%D9%8A-%D8%B3%D9%84%D8%A9) |
| إعداد حملة إعلانية لمتجرك | /digital-ads.html | By options | [29889399](https://ezhalhe.com/p29889399-%D8%A7%D9%86%D8%B4%D8%A7%D8%A1-%D8%AD%D9%85%D9%84%D8%A9-%D8%AA%D8%B3%D9%88%D9%8A%D9%82%D9%8A%D8%A9-%D8%B9%D9%84%D9%89-%D9%85%D9%88%D8%A7%D9%82%D8%B9-%D8%A7%D9%84%D8%AA%D9%88%D8%A7%D8%B5%D9%84-%D8%A7%D9%84%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%D9%8A-%D8%B3%D9%86%D8%A7%D8%A8-%D8%B4%D8%A7%D8%AA-%D9%88%D8%A7%D9%86%D8%B3%D8%AA%D8%A7%D8%AC%D8%B1%D8%A7%D9%85) |
| إدارة المتجر والسوشيال ميديا شهريًا | /services/monthly-store-management.html | By options | [1701323826](https://ezhalhe.com/p1701323826-%D8%A5%D8%AF%D8%A7%D8%B1%D8%A9-%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D9%88%D8%AD%D8%B3%D8%A7%D8%A8%D8%A7%D8%AA-%D8%A7%D9%84%D8%AA%D9%88%D8%A7%D8%B5%D9%84-%D8%A7%D9%84%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%D9%8A-%E2%80%94-%D8%B4%D9%87%D8%B1%D9%8A%D8%A7%D9%8B) |
| تفعيل السلات المتروكة في المتجر | /services/abandoned-carts.html | 119 | [1264219688](https://ezhalhe.com/p1264219688-%D8%AA%D9%81%D8%B9%D9%8A%D9%84-%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%A7%D9%84%D9%85%D8%AA%D8%B1%D9%88%D9%83%D8%A9) |
| باقة ربط بكسل سناب وتيك توك | /services/snap-tiktok-pixel-bundle.html | 179 | [1060059214](https://ezhalhe.com/p1060059214-%D8%A7%D8%B1%D9%81%D8%B9-%D9%85%D8%A8%D9%8A%D8%B9%D8%A7%D8%AA%D9%83-%D8%A8%D8%B0%D9%83%D8%A7%D8%A1-%E2%80%93-%D8%A8%D9%83%D8%AC-%D8%B1%D8%A8%D8%B7-%D8%A8%D9%83%D8%B3%D9%84-%D8%AA%D9%8A%D9%83-%D8%AA%D9%88%D9%83-%D9%88%D8%B3%D9%86%D8%A7%D8%A8-%D8%B4%D8%A7%D8%AA) |
| تركيب TikTok Pixel لمتجر سلة | /services/tiktok-pixel.html | 249 | [1375743607](https://ezhalhe.com/p1375743607-%D8%AA%D8%B1%D9%83%D9%8A%D8%A8-%D9%88%D8%AA%D9%81%D8%B9%D9%8A%D9%84-%D8%AA%D9%8A%D9%83-%D8%AA%D9%88%D9%83-%D8%A8%D9%83%D8%B3%D9%84-(tiktok-pixel)-%D9%84%D9%85%D8%AA%D8%AC%D8%B1%D9%83) |
| تركيب Snap Pixel لمتجر سلة | /services/snapchat-pixel.html | 249 | [166288191](https://ezhalhe.com/p166288191-%D8%AA%D8%B1%D9%83%D9%8A%D8%A8-%D9%88%D8%AA%D9%81%D8%B9%D9%8A%D9%84-%D8%A8%D9%83%D8%B3%D9%84-(pixel)-%D9%84%D9%85%D8%AA%D8%AC%D8%B1%D9%83) |
| ربط Google Analytics بالمتجر | /services/google-analytics.html | 99 | [313092457](https://ezhalhe.com/p313092457-%D8%B1%D8%A8%D8%B7-%D9%82%D9%88%D9%82%D9%84-%D8%A7%D9%86%D8%A7%D9%84%D8%AA%D9%8A%D9%83%D8%B3-%D9%85%D8%B9%D8%B1%D9%81%D8%A9-%D8%B9%D8%AF%D8%AF-%D8%B2%D9%88%D8%A7%D8%B1-%D9%88%D8%AA%D8%AD%D8%B1%D9%83%D8%A7%D8%AA%D9%87%D9%85-%D8%A8%D9%85%D8%AA%D8%AC%D8%B1%D9%83) |
| تفعيل Google Merchant Center لسلة | /services/google-merchant-center.html | 350 | [1173309150](https://ezhalhe.com/p1173309150-%D8%AA%D9%81%D8%B9%D9%8A%D9%84-google-merchant-center-%D9%84%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D9%81%D9%8A-%D8%B3%D9%84%D8%A9) |
| حجز وربط دومين .com للمتجر | /services/store-domain.html | 149 | [1510397301](https://ezhalhe.com/p1510397301-%D8%AD%D8%AC%D8%B2-%D9%88%D8%B1%D8%A8%D8%B7-%D8%AF%D9%88%D9%85%D9%8A%D9%86-%D8%AE%D8%A7%D8%B5-%D8%A8%D9%85%D8%AA%D8%AC%D8%B1%D9%83) |
| إنشاء بريد تجاري باسم الدومين | /services/business-email.html | 350 | [766767169](https://ezhalhe.com/p766767169-%D8%A5%D9%86%D8%B4%D8%A7%D8%A1-%D8%A5%D9%8A%D9%85%D9%8A%D9%84-%D8%AA%D8%AC%D8%A7%D8%B1%D9%8A-%D8%A7%D8%AD%D8%AA%D8%B1%D8%A7%D9%81%D9%8A-%D8%A8%D8%A7%D8%B3%D9%85-%D9%86%D8%B7%D8%A7%D9%82-%D9%85%D8%AA%D8%AC%D8%B1%D9%83) |
| تصميم صفحة Linktree احترافية | /services/linktree-page.html | 199 | [925829032](https://ezhalhe.com/p925829032-%D8%A5%D9%86%D8%B4%D8%A7%D8%A1-linktree-%D8%A7%D8%AD%D8%AA%D8%B1%D8%A7%D9%81%D9%8A---%D8%B1%D8%A7%D8%A8%D8%B7-%D9%88%D8%A7%D8%AD%D8%AF-%D9%84%D9%83%D9%84-%D8%AD%D8%B3%D8%A7%D8%A8%D8%A7%D8%AA%D9%83-%D9%88%D9%85%D8%AA%D8%AC%D8%B1%D9%83) |
| تحويل حساب تيك توك إلى تجاري | /services/tiktok-business-account.html | 149 | [1090328070](https://ezhalhe.com/p1090328070-%D8%AA%D9%88%D8%AB%D9%8A%D9%82-%D8%AA%D9%8A%D9%83-%D8%AA%D9%88%D9%83) |
| صياغة سياسة الاسترجاع والاستبدال | /services/return-exchange-policy.html | 149 | [606867619](https://ezhalhe.com/p606867619-%D9%83%D8%AA%D8%A7%D8%A8%D8%A9-%D8%B3%D9%8A%D8%A7%D8%B3%D8%A9-%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%B1%D8%AC%D8%A7%D8%B9-%D9%88%D8%A7%D9%84%D8%AA%D8%A8%D8%AF%D9%8A%D9%84-%D9%84%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D8%A7%D9%84%D8%A5%D9%84%D9%83%D8%AA%D8%B1%D9%88%D9%86%D9%8A) |
| باقة التأسيس والتوثيق الشاملة | /services/business-verification-package.html | 329 | [724723998](https://ezhalhe.com/p724723998-%D8%A8%D8%A7%D9%82%D8%A9-%D8%A7%D9%84%D8%AA%D9%88%D8%AB%D9%8A%D9%82-%D8%A7%D9%84%D8%B4%D8%A7%D9%85%D9%84%D8%A9) |
| توثيق متجر إلكتروني في منصة الأعمال | /store-verification.html | 119 | [1402286704](https://ezhalhe.com/p1402286704-%D8%B1%D8%A8%D8%B7-%D9%88%D8%AA%D9%88%D8%AB%D9%8A%D9%82-%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D8%A8%D9%88%D8%B2%D8%A7%D8%B1%D8%A9-%D8%A7%D9%84%D8%AA%D8%AC%D8%A7%D8%B1%D8%A9-(%D9%85%D8%B9%D8%B1%D9%88%D9%81)) |
| تحديث المالك وتوثيق متجر سلة | /services/salla-owner-verification.html | 79 | [980169495](https://ezhalhe.com/p980169495-%D8%AA%D8%AD%D8%AF%D9%8A%D8%AB-%D8%A8%D9%8A%D8%A7%D9%86%D8%A7%D8%AA-%D8%A7%D9%84%D9%85%D8%A7%D9%84%D9%83-%D9%88%D8%AA%D9%88%D8%AB%D9%8A%D9%82-%D9%85%D8%AA%D8%AC%D8%B1%D9%83-%D9%81%D9%8A-%D9%85%D9%86%D8%B5%D8%A9-%D8%B3%D9%84%D8%A9) |
| المساعدة في إصدار وثيقة العمل الحر | /services/freelance-document.html | 119 | [1404796305](https://ezhalhe.com/p1404796305-%D8%A7%D8%B3%D8%AA%D8%AE%D8%B1%D8%A7%D8%AC-%D9%88%D8%AA%D9%82%D8%AF%D9%8A%D9%85-%D8%B9%D9%84%D9%89-%D9%88%D8%AB%D9%8A%D9%82%D8%A9-%D8%A7%D9%84%D8%B9%D9%85%D9%84-%D8%A7%D9%84%D8%AD%D8%B1) |
| المساعدة في إصدار سجل تجاري | /services/commercial-registration.html | 249 | [909274787](https://ezhalhe.com/p909274787-%D9%81%D8%AA%D8%AD-%D9%88%D8%A7%D8%B5%D8%AF%D8%A7%D8%B1-%D8%B3%D8%AC%D9%84-%D8%AA%D8%AC%D8%A7%D8%B1%D9%8A) |
| المساعدة في حساب أعمال لدى الإنماء | /services/alinma-business-account.html | 179 | [801295278](https://ezhalhe.com/p801295278-%D9%81%D8%AA%D8%AD-%D8%AD%D8%B3%D8%A7%D8%A8-%D8%AA%D8%AC%D8%A7%D8%B1%D9%8A-%D8%A7%D9%84%D8%A7%D9%86%D9%85%D8%A7%D8%A1) |
| المساعدة في حساب أعمال لدى الراجحي | /services/rajhi-business-account.html | 179 | [453164668](https://ezhalhe.com/p453164668-%D9%81%D8%AA%D8%AD-%D8%AD%D8%B3%D8%A7%D8%A8-%D8%A8%D9%86%D9%83%D9%8A-%D8%A7%D9%84%D8%B1%D8%A7%D8%AC%D8%AD%D9%8A) |
| تجهيز وربط تابي وتمارا للمتجر | /services/tabby-tamara-setup.html | By options | [1652439672](https://ezhalhe.com/p1652439672-%D9%81%D8%AA%D8%AD-%D8%AD%D8%B3%D8%A7%D8%A8-%D8%AA%D8%A7%D8%A8%D9%8A-%D8%A3%D9%88-%D8%AA%D9%85%D8%A7%D8%B1%D8%A7-%D9%84%D9%84%D8%A3%D8%B9%D9%85%D8%A7%D9%84-(%D8%AA%D9%81%D8%B9%D9%8A%D9%84-%D8%A7%D9%84%D8%AF%D9%81%D8%B9-%D8%A7%D9%84%D8%A2%D8%AC%D9%84)) |
| المساعدة في طلب تمويل العمل الحر | /services/freelance-finance-application.html | 359 | [834660524](https://ezhalhe.com/p834660524-%D8%AA%D9%82%D8%AF%D9%8A%D9%85-%D9%82%D8%B1%D8%B6-%D8%A7%D9%84%D8%B9%D9%85%D9%84-%D8%A7%D9%84%D8%AD%D8%B1) |

Official references used to correct outdated store language:

- https://mc.gov.sa/ar/mediacenter/News/Pages/29-03-23-02.aspx
- https://scbc.gov.sa/eservices/details/4d6e9d30-e989-4940-08ce-08dbf015747a
- https://freelance.sa/ar/faqs
- https://mc.gov.sa/ar/mediacenter/News/Pages/03-04-25-01.aspx
- https://www.sdb.gov.sa/ar/individuals-financing/cash-financing/faqs
