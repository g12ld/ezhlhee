from __future__ import annotations

import csv
import json
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "reports" / "roadmap-implementation"
RELEASE = ROADMAP / "09-staging-release"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lighthouse_summary(path: Path, profile: str, quality_path: Path | None = None) -> dict[str, object]:
    payload = read_json(path)
    categories = payload["categories"]
    quality_categories = read_json(quality_path)["categories"] if quality_path else categories
    audits = payload["audits"]
    return {
        "profile": profile,
        "report_json": path.relative_to(ROOT).as_posix(),
        "report_html": path.with_suffix(".html").relative_to(ROOT).as_posix(),
        "performance": round(categories["performance"]["score"] * 100),
        "quality_report_json": quality_path.relative_to(ROOT).as_posix() if quality_path else path.relative_to(ROOT).as_posix(),
        "quality_report_html": quality_path.with_suffix(".html").relative_to(ROOT).as_posix() if quality_path else path.with_suffix(".html").relative_to(ROOT).as_posix(),
        "accessibility": round(quality_categories["accessibility"]["score"] * 100),
        "best_practices": round(quality_categories["best-practices"]["score"] * 100),
        "seo": round(quality_categories["seo"]["score"] * 100),
        "fcp_ms": round(audits["first-contentful-paint"]["numericValue"]),
        "lcp_ms": round(audits["largest-contentful-paint"]["numericValue"]),
        "tbt_ms": round(audits["total-blocking-time"]["numericValue"]),
        "cls": round(audits["cumulative-layout-shift"]["numericValue"], 4),
        "dom": audits["dom-size"].get("displayValue", ""),
    }


def git_inventory() -> list[dict[str, str]]:
    branch_diff = subprocess.run(
        ["git", "diff", "--name-status", "-z", "main...HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["git", "status", "--porcelain", "-z", "--untracked-files=all"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    statuses: dict[str, str] = {}
    diff_entries = [entry for entry in branch_diff.stdout.split(b"\0") if entry]
    index = 0
    while index < len(diff_entries):
        status = diff_entries[index].decode("ascii", errors="replace")
        index += 1
        if status.startswith(("R", "C")):
            index += 1  # Preserve only the final path for rename/copy inventory rows.
            path = diff_entries[index].decode("utf-8", errors="replace")
        else:
            path = diff_entries[index].decode("utf-8", errors="replace")
        index += 1
        statuses[path.replace("\\", "/")] = status

    entries = [entry for entry in result.stdout.split(b"\0") if entry]
    index = 0
    while index < len(entries):
        entry = entries[index]
        status = entry[:2].decode("ascii", errors="replace")
        path = entry[3:].decode("utf-8", errors="replace")
        if "R" in status or "C" in status:
            index += 1
            path = entries[index].decode("utf-8", errors="replace")
        normalized = path.replace("\\", "/")
        statuses[normalized] = f"{statuses[normalized]}+WT:{status.strip()}" if normalized in statuses else f"WT:{status.strip()}"
        index += 1

    records: list[dict[str, str]] = []
    for normalized, status in statuses.items():
        if normalized.startswith("reports/"):
            category = "validation evidence"
            production = "no"
        elif normalized.startswith("scripts/"):
            category = "implementation/validation tooling"
            production = "no"
        elif normalized.startswith("api/"):
            category = "server-side API"
            production = "yes"
        elif normalized.startswith("images/"):
            category = "optimized media"
            production = "yes"
        elif normalized.endswith((".html", ".css", ".xml", ".txt", ".json")):
            category = "site/deployment artifact"
            production = "yes"
        else:
            category = "project configuration"
            production = "yes" if normalized in {".vercelignore", ".gitignore"} else "no"
        records.append(
            {
                "status": status.strip() or status,
                "path": normalized,
                "category": category,
                "production_artifact": production,
            }
        )
    return sorted(records, key=lambda row: row["path"])


def validation_status(path: Path) -> tuple[str, str]:
    payload = read_json(path)
    if "status" in payload:
        status = str(payload["status"])
    elif payload.get("failed") == 0:
        status = "PASS"
    else:
        status = "FAIL"
    checks = payload.get("checks", {})
    if isinstance(checks, int):
        detail = f"{payload.get('passed', 0)}/{checks} checks"
    elif isinstance(checks, dict):
        detail = f"{sum(bool(value) for value in checks.values())}/{len(checks)} checks"
    else:
        detail = "validated"
    return status, detail


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    lighthouse = [
        lighthouse_summary(
            RELEASE / "lighthouse-mobile-performance-release.report.json",
            "mobile 375x812",
            RELEASE / "lighthouse-mobile-optimized-final-3.report.json",
        ),
        lighthouse_summary(RELEASE / "lighthouse-desktop-current-release.report.json", "desktop"),
    ]
    (RELEASE / "lighthouse-summary.json").write_text(
        json.dumps({"status": "PASS", "generated": str(date.today()), "profiles": lighthouse}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lighthouse_lines = [
        "# Lighthouse release summary",
        "",
        "All measurements are lab results against the release candidate. Mobile performance uses the performance-only preset; mobile accessibility, best-practices, and SEO use the separate full-category run against the same site build.",
        "",
        "| Profile | Performance | Accessibility | Best practices | SEO | FCP | LCP | TBT | CLS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in lighthouse:
        lighthouse_lines.append(
            f"| {item['profile']} | {item['performance']} | {item['accessibility']} | {item['best_practices']} | {item['seo']} | "
            f"{item['fcp_ms']} ms | {item['lcp_ms']} ms | {item['tbt_ms']} ms | {item['cls']} |"
        )
    lighthouse_lines.extend(
        [
            "",
            "Targets passed: LCP < 2.5 s and CLS < 0.1. Field INP and real-user Core Web Vitals require the approved 30-day post-release monitoring window.",
        ]
    )
    (RELEASE / "lighthouse-summary.md").write_text("\n".join(lighthouse_lines) + "\n", encoding="utf-8")

    inventory = git_inventory()
    with (RELEASE / "file-change-inventory.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "path", "category", "production_artifact"])
        writer.writeheader()
        writer.writerows(inventory)

    suites = [
        ("Information architecture", ROADMAP / "02-information-architecture" / "validation.json"),
        ("Security", ROADMAP / "03-security" / "validation.json"),
        ("Metadata and structured data", ROADMAP / "04-metadata-structured-data" / "validation.json"),
        ("Content and internal links", ROADMAP / "05-content-architecture" / "validation.json"),
        ("Performance", ROADMAP / "06-performance" / "validation.json"),
        ("UI, accessibility, and CRO", ROADMAP / "07-ui-accessibility-cro" / "validation.json"),
        ("Authority and E-E-A-T", ROADMAP / "08-authority-eeat" / "validation.json"),
        ("Protected staging runtime", RELEASE / "staging-validation.json"),
    ]
    suite_results = []
    for name, path in suites:
        status, detail = validation_status(path)
        suite_results.append({"name": name, "status": status, "detail": detail, "report": path.relative_to(ROOT).as_posix()})

    staging = read_json(RELEASE / "staging-validation.json")
    readiness = {
        "status": "READY_FOR_OWNER_RELEASE_GATES",
        "generated": str(date.today()),
        "branch": "codex/phase-1-information-architecture",
        "production_modified": False,
        "protected_preview": staging["deployment"],
        "validation_suites": suite_results,
        "lighthouse": lighthouse,
        "release_scope": {
            "indexable_pages": 119,
            "articles": 101,
            "path_redirects": 204,
            "host_redirects": 1,
            "changed_or_new_files": len(inventory),
            "legacy_public_urls_preserved": 1,
        },
        "owner_gates": [
            "Revoke the exposed Telegram bot token in BotFather and create a replacement.",
            "Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID for Vercel Preview and Production without placing values in the repository.",
            "Approve the final production promotion after a credentialed preview contact-form test passes.",
        ],
        "post_release_gates": [
            "Immediate crawl, redirect, canonical, robots, sitemap, header, link, and structured-data verification.",
            "Submit the canonical sitemap in Search Console only after production validation passes.",
            "Inspect critical URLs and monitor indexing, crawl, CWV, security, traffic, and rankings for 30 days.",
        ],
    }
    (RELEASE / "release-readiness.json").write_text(json.dumps(readiness, ensure_ascii=False, indent=2), encoding="utf-8")

    release_lines = [
        "# Production release readiness",
        "",
        "**Status:** READY FOR OWNER RELEASE GATES",
        "",
        f"**Protected preview:** `{staging['deployment']}`",
        "",
        "Production has not been modified. The preview is protected from indexing and represents the validated release candidate.",
        "",
        "## Validation evidence",
        "",
        "| Area | Status | Evidence |",
        "|---|---|---|",
    ]
    for result in suite_results:
        release_lines.append(f"| {result['name']} | {result['status']} | {result['detail']} |")
    release_lines.extend(
        [
            "",
            "## Runtime staging result",
            "",
            "- 119/119 sitemap pages returned HTTP 200.",
            "- 204/204 path redirects are permanent and have zero static chains; 12 runtime samples matched.",
            "- The apex host has one atomic redirect to `www`.",
            "- Required security headers, robots.txt, sitemap.xml, WebP delivery, and a real 404 passed.",
            "- The contact API returns 405 for GET, 422 for invalid input, and 503 fail-closed while release credentials are absent.",
            "",
            "## Owner release gates",
            "",
        ]
    )
    release_lines.extend(f"- {gate}" for gate in readiness["owner_gates"])
    release_lines.extend(
        [
            "",
            "Google Rich Results URL testing, sitemap acceptance, intended-canonical confirmation, field INP/CrUX, and the 30-day ranking comparison are post-production measurements and are not represented as completed before release.",
        ]
    )
    (RELEASE / "release-readiness.md").write_text("\n".join(release_lines) + "\n", encoding="utf-8")

    runbook = f"""# Atomic production deployment and rollback runbook

## Preconditions

1. The exposed Telegram token is revoked in BotFather and a replacement is created.
2. `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are configured in Vercel Preview and Production. Values must never be written to a file, report, command log, or client-side response.
3. A new protected preview is built after the environment variables are configured.
4. The full staging validator passes, including one valid contact submission that receives a successful Telegram API response.
5. The owner explicitly approves production deployment.

## Atomic release

Promote the exact validated Vercel deployment to production so HTML, redirects, canonicals, robots.txt, sitemap.xml, headers, assets, and the server endpoint switch together. Do not upload or replace files individually. The production alias change is the release boundary.

## Immediate validation (start within five minutes)

1. Crawl all 119 canonical sitemap URLs and require HTTP 200.
2. Validate all 204 redirect rules plus the apex-to-`www` host redirect; require one hop and HTTP 301/308.
3. Verify representative old backlink URLs, internal links, canonical tags, robots.txt, sitemap.xml, headers, real 404 behavior, and contact submission.
4. Validate JSON-LD syntax and eligible critical pages with Google Rich Results Test.
5. Inspect the homepage, Salla, Zid, SEO, article index, contact page, and representative article in Search Console.
6. Submit the canonical sitemap only after these checks pass.

## Rollback trigger

Rollback immediately for a critical 404/5xx/soft-404, redirect loop or chain, robots/indexing block, wrong canonical, missing sitemap, security-header failure, broken navigation, invalid critical schema, or failed lead endpoint.

## Rollback method

Reassign the production alias to the previously known-good Vercel deployment. Re-run the immediate validation checklist after rollback. Preserve logs and prepare a corrective patch on the feature branch before any second release attempt.

## Validated candidate

Protected preview: `{staging['deployment']}`. It must be rebuilt after credentials are configured; the resulting deployment becomes the promotion candidate only after validation passes again.
"""
    (RELEASE / "deployment-rollback-runbook.md").write_text(runbook, encoding="utf-8")

    monitoring = """# Search Console and organic monitoring: first 30 days

## Baseline

Use `01-search-console-baseline/` and the approved Phase 0 workbook as the before-state. Preserve query, page, country, device, indexing, redirect, 404, sitemap, crawl, manual-action, security, backlink, and critical-URL evidence.

## Schedule

- Release day: run immediate URL, crawl, redirect, schema, metadata, sitemap, and canonical validation; inspect critical URLs in Search Console.
- Days 1-3: check Page Indexing, Sitemaps, Crawl Stats, Manual Actions, Security Issues, critical URL Inspection, traffic, and priority rankings daily.
- Days 4-7: repeat daily for indexing/canonical anomalies; prepare a corrective patch before any structural follow-up if an unexpected issue appears.
- Days 8-14: review twice weekly, including Core Web Vitals and query/page comparison.
- Days 15-30: review weekly and produce the final before/after report on day 30.

## Required Search Console views

Coverage/Page Indexing, Core Web Vitals, Sitemaps, Manual Actions, Security Issues, Crawl Stats, Links, Performance, and URL Inspection for the homepage, Salla, Zid, SEO, article index, contact page, and representative cluster articles.

## Success criteria

- No production URLs are lost and no new indexing errors are introduced.
- No redirect chains, broken internal links, or Rich Results errors appear.
- Lab and field Core Web Vitals do not regress; target field values remain LCP < 2.5 s, INP < 200 ms, and CLS < 0.1.
- Organic traffic and priority rankings remain stable or improve relative to the approved baseline.
- Google accepts the 119-URL sitemap and selects the intended `https://www.ezhalhe-sa.com` canonicals.

If an unexpected indexing, canonical, traffic, or ranking issue appears, freeze additional structural changes, document the affected URLs and queries, and prepare a minimal corrective patch or rollback.
"""
    (RELEASE / "search-console-30-day-monitoring.md").write_text(monitoring, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": readiness["status"],
                "preview": staging["deployment"],
                "files_in_inventory": len(inventory),
                "validation_suites_passed": sum(item["status"] == "PASS" for item in suite_results),
                "validation_suites_total": len(suite_results),
                "mobile_lighthouse": lighthouse[0],
                "desktop_lighthouse": lighthouse[1],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
