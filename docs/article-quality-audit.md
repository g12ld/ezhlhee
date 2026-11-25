# Ezhalha Article Quality Audit

Date: 2026-09-05

Scope: current files under `articles/` plus the `articles.html` index. This audit preserves all existing article URLs. No article URL was deleted, renamed, or redirected in this implementation pass.

## Decision Rules

- KEEP: Closely supports Ezhalha's core commercial authority around Salla, Zid, store design, UX, SEO, analytics, product pages, or platform selection.
- IMPROVE: Relevant to Saudi e-commerce but needs fresher sources, clearer owner expertise, better screenshots, stronger examples, or removal of generic filler.
- MERGE: Multiple pages answer the same practical question and should eventually become one stronger guide with redirects only after search data is checked.
- POTENTIAL REMOVE / REDIRECT: Thin, risky, or claim-heavy pages. Do not remove without Google Search Console evidence, inbound-link check, and a redirect target.

## KEEP

- Salla and Zid design guidance.
- UX, mobile-first design, product-page design, store conversion, and visual identity articles.
- Technical SEO, Search Console, GA4, Google Merchant Center, analytics, tracking, and conversion measurement articles.
- Salla/Zid platform choice and package-comparison content where it supports purchase decisions.

## IMPROVE

- Payment gateway articles, including Mيس, مدفوع, إمكان, تابي, وتمارا, should be reviewed against current provider requirements before making acceptance or fee claims.
- Business setup articles around documentation, bank accounts, and freelancing documents need clearer scope: explain what Ezhalha can help with and where official government or bank action remains the merchant's responsibility.
- Social media and campaign articles should include concrete store examples, channel-fit guidance for Saudi merchants, and avoid broad marketing advice.
- Articles using broad claims such as "زيادة المبيعات" should be rewritten to explain mechanism and uncertainty instead of implying guaranteed revenue impact.

## MERGE

- Multiple bank-account articles should become one stronger Saudi e-commerce banking guide, with sections for الراجحي, الإنماء, personal vs commercial account, approval readiness, and cash-flow operations.
- Multiple freelance-document articles should become one practical guide covering requirements, activity selection, renewal, and relationship to store documentation.
- Multiple business-documentation articles should become one pillar guide for توثيق المتجر, منصة الأعمال, متطلبات سلة/زد, and common rejection causes.
- Multiple payment-activation articles should become one payment pillar with supporting sections for gateways and buy-now-pay-later providers.
- Multiple ad-pixel and retargeting articles should become one measurement pillar with separate sections for Meta, Snapchat, TikTok, GA4, and conversion tracking.

## POTENTIAL REMOVE / REDIRECT

- Claim-heavy service articles with titles containing "ضمان القبول السريع" require review. Rewrite them first if they still receive impressions; redirect only if they are thin and have no organic value.
- Articles whose only value is a near-duplicate checklist should be merged into the strongest relevant pillar.
- Any page making legal, banking, provider-acceptance, or guaranteed-performance claims should be reviewed by the owner before production expansion.

## New Knowledge Architecture

- Salla cluster: design, setup, product pages, Salla SEO, customization, Salla vs Zid.
- Zid cluster: setup, themes, customization, product organization, Zid vs Salla.
- Store growth cluster: technical SEO, GA4, Search Console, product content, conversion, performance.
- Saudi operations cluster: payment, business documentation, domain, bank account, store verification, and platform compliance.

## Next Editorial Pass

1. Export Google Search Console performance for all article URLs.
2. Keep or improve pages with impressions, backlinks, or clear topical value.
3. Merge duplicate low-value pages into pillar guides.
4. Implement 301 redirects only after target mapping is final.
5. Update sitemap after redirects are implemented.
