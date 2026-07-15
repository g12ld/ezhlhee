# Performance validation

Result: 16/16 checks passed.

| Check | Result | Evidence |
|---|---|---|
| intrinsic-image-dimensions | PASS | images=269, missing=0 |
| image-loading-explicit | PASS | missing=0 |
| async-image-decoding | PASS | missing=0 |
| responsive-images | PASS | responsive=269, total=269 |
| critical-image-priority | PASS | eager=1, high_priority=1 |
| responsive-variant-set | PASS | variants=37, bytes=2647170 |
| no-render-blocking-google-fonts | PASS | files=0 |
| hero-in-critical-order | PASS | hero_offset=65381, coupon_offset=67825 |
| below-fold-render-containment | PASS | Below-fold sections use content visibility with an intrinsic fallback |
| scroll-listeners-deduplicated | PASS | Scroll previews bind once and resize only resets transforms |
| passive-header-scroll | PASS | Header shadow work is animation-frame throttled and passive |
| reduced-motion-support | PASS | Non-essential animation collapses for reduced-motion users |
| image-change-log | PASS | rows=269 |
| mobile-lab-lcp | PASS | lcp_ms=564 |
| mobile-lab-cls | PASS | cls=0.0049 |
| field-data-claim-safety | PASS | INP and field CWV are explicitly deferred to staged Lighthouse and 30-day monitoring |

## Release-gate limitation

The local CDP diagnostic passes the LCP and CLS targets but is not Lighthouse or CrUX. A public preview URL is required for PageSpeed/Lighthouse and Rich Results validation. Search Console reports insufficient field data, so no real-user CWV pass is claimed.
