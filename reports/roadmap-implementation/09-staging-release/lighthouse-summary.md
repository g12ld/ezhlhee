# Lighthouse release summary

All measurements are lab results against the release candidate. Mobile performance uses the performance-only preset; mobile accessibility, best-practices, and SEO use the separate full-category run against the same site build.

| Profile | Performance | Accessibility | Best practices | SEO | FCP | LCP | TBT | CLS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mobile 375x812 | 97 | 100 | 100 | 100 | 2059 ms | 2073 ms | 0 ms | 0 |
| desktop | 100 | 100 | 100 | 100 | 431 ms | 440 ms | 0 ms | 0 |

Targets passed: LCP < 2.5 s and CLS < 0.1. Field INP and real-user Core Web Vitals require the approved 30-day post-release monitoring window.
