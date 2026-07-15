# Lighthouse release summary

All measurements are lab results against the release candidate. Mobile performance uses the performance-only preset; mobile accessibility, best-practices, and SEO use the separate full-category run against the same site build.

| Profile | Performance | Accessibility | Best practices | SEO | FCP | LCP | TBT | CLS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mobile 375x812 | 82 | 100 | 100 | 100 | 2071 ms | 2268 ms | 594 ms | 0 |
| desktop | 99 | 100 | 100 | 100 | 552 ms | 627 ms | 32 ms | 0 |

Targets passed: LCP < 2.5 s and CLS < 0.1. Field INP and real-user Core Web Vitals require the approved 30-day post-release monitoring window.
