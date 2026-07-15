# Portfolio Update Change Log

Date: 2026-07-15 (Asia/Riyadh)  
Branch: `codex/phase-1-information-architecture`

## Scope

Added three owner-supplied portfolio examples. All three are classified as Salla platform projects completed under the Gold Pro package.

## Existing file modified

- `index.html`
  - Added LANA to the top of the main portfolio gallery.
  - Added Lara Alsaad Boutique to the top of the main portfolio gallery.
  - Added Duk Altayeb to the top of the main portfolio gallery.
  - Added all three stores to the Gold Pro package mini-gallery.
  - Updated the Gold Pro work count from `9+` to `12`.
  - Added meaningful Arabic alternative text, explicit image dimensions, lazy loading, and asynchronous decoding to every new image occurrence.
  - Updated the existing lightbox function to apply its supplied project title as the expanded image alternative text.

## Image files created

- `images/lana-badawood-salla-gold-pro.webp` — 525 × 10,697 px; copied unchanged from the owner-supplied WebP.
- `images/lara-alsaad-boutique-salla-gold-pro.webp` — 525 × 10,817 px; copied unchanged from the owner-supplied WebP.
- `images/duk-altayeb-salla-gold-pro.webp` — 525 × 6,441 px; copied unchanged from the owner-supplied WebP.

## URL, redirect, canonical, and indexing record

- Production URLs changed: none.
- Existing files renamed or deleted: none.
- Redirects introduced or modified: none.
- Canonicals introduced or modified: none.
- Sitemap or robots directives changed: none.
- Structured data changed: none.
- Internal navigation changed: none.
- Production deployment performed: no.

## SEO and content decisions

- Each entry uses `data-pkg="pro"` and `data-plat="salla"`, so both the Gold Pro and Salla filters include it.
- New portfolio images retain WebP format and use explicit intrinsic dimensions to reduce layout-shift risk.
- LANA is displayed as a Salla project without an external destination because the address inferred from the screenshot filename did not resolve during verification.
- The Lara Alsaad Boutique and Duk Altayeb addresses returned successful HTTP responses during read-only verification.
- The immutable pre-change baseline package under `reports/phase-1-baseline/2026-07-15/` was not altered.

## Validation results

- Source-to-repository SHA-256 comparison: passed for all three WebP files; each repository asset is byte-for-byte identical to its owner-supplied source.
- Main portfolio classification: three new cards, each marked `pro` and `salla`.
- Gold Pro mini-gallery: 12 cards after the addition, matching the displayed count.
- Asset reference check: each new WebP has four references—main-card action, main-card image, mini-card action, and mini-card image.
- New image markup check: all six image elements contain Arabic alternative text, width, height, `loading="lazy"`, and `decoding="async"`.
- Lightbox accessibility check: the project title is assigned to the expanded image alternative text.
- Whitespace and patch integrity check: passed.
- Production deployment and hosting actions: not run.
