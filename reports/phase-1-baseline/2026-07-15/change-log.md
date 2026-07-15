# Phase 1 Baseline Change Log

Generated: 2026-07-15 (Asia/Riyadh)

## Release state

- Working branch: `codex/phase-1-information-architecture`
- Production deployment: **not performed**
- Existing tracked site files modified: **none**
- Production URLs changed: **none**
- Redirects introduced: **none**
- Canonicals updated: **none**
- Robots or sitemap behavior changed: **none**
- Phase 1 structural implementation: **paused pending baseline review and approval**

The pre-existing untracked `AGENTS.md` file was read for project constraints and was not modified.

## Baseline report files created

All files below are review evidence only and are not part of the production site:

- `reports/phase-1-baseline/2026-07-15/accessibility-baseline.csv`
- `reports/phase-1-baseline/2026-07-15/audit-metrics.json`
- `reports/phase-1-baseline/2026-07-15/backlink-targets.csv`
- `reports/phase-1-baseline/2026-07-15/backup-and-rollback-plan.md`
- `reports/phase-1-baseline/2026-07-15/baseline-manifest.json`
- `reports/phase-1-baseline/2026-07-15/baseline-package-checksums.txt`
- `reports/phase-1-baseline/2026-07-15/baseline-summary.md`
- `reports/phase-1-baseline/2026-07-15/brand-color-inventory.csv`
- `reports/phase-1-baseline/2026-07-15/broken-links.csv`
- `reports/phase-1-baseline/2026-07-15/canonical-map.csv`
- `reports/phase-1-baseline/2026-07-15/change-log.md`
- `reports/phase-1-baseline/2026-07-15/content-inventory.csv`
- `reports/phase-1-baseline/2026-07-15/file-checksums.txt`
- `reports/phase-1-baseline/2026-07-15/http-status-and-headers.csv`
- `reports/phase-1-baseline/2026-07-15/image-inventory.csv`
- `reports/phase-1-baseline/2026-07-15/important-files-inventory.csv`
- `reports/phase-1-baseline/2026-07-15/internal-link-graph.csv`
- `reports/phase-1-baseline/2026-07-15/keyword-baseline.csv`
- `reports/phase-1-baseline/2026-07-15/metadata-inventory.csv`
- `reports/phase-1-baseline/2026-07-15/orphan-pages.csv`
- `reports/phase-1-baseline/2026-07-15/performance-baseline.json`
- `reports/phase-1-baseline/2026-07-15/redirect-baseline.csv`
- `reports/phase-1-baseline/2026-07-15/redirected-internal-links.csv`
- `reports/phase-1-baseline/2026-07-15/repository-robots-snapshot.txt`
- `reports/phase-1-baseline/2026-07-15/repository-sitemap-snapshot.xml`
- `reports/phase-1-baseline/2026-07-15/repository-state.txt`
- `reports/phase-1-baseline/2026-07-15/review-checklist.md`
- `reports/phase-1-baseline/2026-07-15/robots-snapshot.txt`
- `reports/phase-1-baseline/2026-07-15/search-console-baseline.csv`
- `reports/phase-1-baseline/2026-07-15/security-findings.csv`
- `reports/phase-1-baseline/2026-07-15/seo-decision-log.csv`
- `reports/phase-1-baseline/2026-07-15/sitemap-inventory.csv`
- `reports/phase-1-baseline/2026-07-15/sitemap-snapshot.xml`
- `reports/phase-1-baseline/2026-07-15/structured-data-inventory.json`
- `reports/phase-1-baseline/2026-07-15/url-inventory.csv`

`baseline-manifest.json` and `baseline-package-checksums.txt` are regenerated after the package is finalized so that the review copy can be integrity-checked.

## Review workbook and supporting files created

- `outputs/ezhalha-phase1-baseline-20260715/ezhalha-phase1-baseline.xlsx`
- `outputs/ezhalha-phase1-baseline-20260715/ezhalha-phase1-baseline.xlsx.inspect.ndjson`
- Twenty rendered workbook previews under `outputs/ezhalha-phase1-baseline-20260715/previews/`, one for each workbook sheet.

## Audit tooling and temporary support files created

These files support reproducibility and quality assurance. They are not deployment files:

- `scripts/generate_phase1_baseline.py`
- `scripts/__pycache__/generate_phase1_baseline.cpython-312.pyc`
- `scratch/phase1-baseline-20260715/build_workbook.mjs`
- `scratch/phase1-baseline-20260715/node_modules` — local directory junction to the bundled workbook runtime.

## SEO decisions recorded during baseline generation

- No preferred-host migration has been implemented. The evidence shows a mismatch between the live `www` host and non-`www` sitemap/canonical references; the target host decision remains an implementation gate.
- No URL has been deleted, renamed, redirected, or de-indexed.
- No canonical has been rewritten.
- No sitemap or robots directive has been changed.
- No structured data has been added or removed.
- Search Console and backlink preservation remain release gates because authenticated source data was unavailable in this session.
- A publicly exposed Telegram credential was detected in existing client-side production code. Its value was not copied into this package. Containment or rotation requires a separate approved production change.

## Validation performed on the baseline package

- Workbook formulas scanned for spreadsheet errors: no formula errors found.
- All twenty workbook sheets rendered and visually reviewed.
- Browser throttling and device overrides were reset after performance collection.
- The production site was crawled read-only; no authenticated production API or deployment action was performed.
- JSON, CSV, checksum, repository-state, and secret-leak checks are recorded in the final validation run.
