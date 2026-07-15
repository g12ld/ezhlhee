#!/usr/bin/env python3
"""Generate the final requirement-by-requirement implementation and release-gate audit."""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "reports" / "roadmap-implementation"
OUTPUT = ROADMAP / "10-completion-audit"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def suite_passed(path: Path) -> bool:
    payload = read_json(path)
    if "status" in payload:
        return payload["status"] == "PASS"
    if "failed" in payload:
        return payload["failed"] == 0
    checks = payload.get("checks")
    return isinstance(checks, dict) and all(checks.values())


def lighthouse(path: Path) -> dict:
    payload = read_json(path)
    audits = payload["audits"]

    def metric(name: str, digits: int = 0):
        value = audits.get(name, {}).get("numericValue")
        return round(value, digits) if value is not None else None

    return {
        "categories": {name: round(item["score"] * 100) for name, item in payload["categories"].items()},
        "lcp_ms": metric("largest-contentful-paint"),
        "tbt_ms": metric("total-blocking-time"),
        "cls": metric("cumulative-layout-shift", 4),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    baseline = ROOT / "reports" / "phase-1-baseline" / "2026-07-15"
    workbook = ROOT / "outputs" / "ezhalha-phase1-baseline-20260715" / "ezhalha-phase1-baseline.xlsx"
    gsc = read_json(ROADMAP / "01-search-console-baseline" / "authenticated-baseline.json")
    staging = read_json(ROADMAP / "09-staging-release" / "staging-validation.json")
    metadata = read_json(ROADMAP / "04-metadata-structured-data" / "validation.json")
    content = read_json(ROADMAP / "05-content-architecture" / "validation.json")
    security = read_json(ROADMAP / "03-security" / "validation.json")
    mobile = lighthouse(ROADMAP / "09-staging-release" / "lighthouse-mobile-performance-release.report.json")
    mobile_quality = lighthouse(ROADMAP / "09-staging-release" / "lighthouse-mobile-optimized-final-3.report.json")
    desktop = lighthouse(ROADMAP / "09-staging-release" / "lighthouse-desktop-current-release.report.json")
    branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()

    suite_paths = [
        ROADMAP / "02-information-architecture" / "validation.json",
        ROADMAP / "03-security" / "validation.json",
        ROADMAP / "04-metadata-structured-data" / "validation.json",
        ROADMAP / "05-content-architecture" / "validation.json",
        ROADMAP / "06-performance" / "validation.json",
        ROADMAP / "07-ui-accessibility-cro" / "validation.json",
        ROADMAP / "08-authority-eeat" / "validation.json",
        ROADMAP / "09-staging-release" / "staging-validation.json",
    ]
    baseline_required = {
        "baseline-manifest.json", "url-inventory.csv", "metadata-inventory.csv",
        "canonical-map.csv", "structured-data-inventory.json", "redirect-baseline.csv",
        "sitemap-snapshot.xml", "baseline-package-checksums.txt",
    }
    metadata_checks = {item["check"]: item["passed"] for item in metadata["results"]}
    content_checks = {item["check"]: item["passed"] for item in content["results"]}

    implementation = {
        "approved_baseline_package_and_workbook_preserved": baseline_required.issubset({p.name for p in baseline.iterdir()}) and workbook.stat().st_size > 0,
        "authenticated_search_console_baseline_preserved": gsc.get("access") == "authenticated_owner" and gsc.get("property") == "sc-domain:ezhalhe-sa.com",
        "separate_feature_branch_used": branch.startswith("codex/") and branch != "main",
        "all_cross_phase_validation_suites_pass": all(suite_passed(path) for path in suite_paths),
        "protected_nonproduction_preview_passes": staging.get("status") == "PASS" and staging.get("deployment_type") == "protected Vercel preview (non-production)",
        "all_119_canonical_pages_return_200": staging["checks"].get("all_119_sitemap_pages_return_200") is True,
        "redirect_map_is_permanent_and_chain_free": staging["checks"].get("all_redirects_are_permanent_and_chain_free") is True,
        "legacy_public_url_is_not_lost": staging["checks"].get("legacy_public_url_is_preserved") is True,
        "browser_and_verification_files_are_preserved": staging["checks"].get("browser_identity_files_are_served_and_valid") is True and staging["checks"].get("google_verification_file_is_preserved") is True,
        "security_headers_and_fail_closed_endpoint_pass": staging["checks"].get("security_headers_complete") is True and security.get("failed") == 0 and staging["checks"].get("contact_fails_closed_without_credentials") is True,
        "metadata_and_rich_result_required_fields_pass": metadata_checks.get("metadata-complete-and-bounded") is True and metadata_checks.get("google-rich-result-required-fields") is True,
        "no_prohibited_faqpage_schema": metadata_checks.get("faqpage-prohibited") is True,
        "no_broken_redirecting_or_orphan_internal_links": all(content_checks.get(name) is True for name in ("no-broken-internal-links", "no-redirecting-internal-links", "no-indexable-orphans")),
        "mobile_lab_cwv_targets_pass": mobile["lcp_ms"] < 2500 and mobile["cls"] < 0.1 and mobile["categories"].get("performance", 0) >= 90,
        "mobile_quality_scores_are_100": all(mobile_quality["categories"].get(name) == 100 for name in ("accessibility", "best-practices", "seo")),
        "desktop_lighthouse_scores_are_100": all(desktop["categories"].get(name) == 100 for name in ("performance", "accessibility", "best-practices", "seo")),
        "atomic_release_and_rollback_runbook_exists": (ROADMAP / "09-staging-release" / "deployment-rollback-runbook.md").is_file(),
        "thirty_day_search_console_plan_exists": (ROADMAP / "09-staging-release" / "search-console-30-day-monitoring.md").is_file(),
        "production_not_deployed_by_this_roadmap": staging.get("deployment", "").endswith("vercel.app") and staging.get("deployment_type", "").startswith("protected"),
    }

    external_release_gates = [
        {
            "gate": "Rotate the compromised Telegram bot token and configure TELEGRAM_BOT_TOKEN plus TELEGRAM_CHAT_ID in Vercel Preview and Production.",
            "status": "OWNER_ACTION_REQUIRED",
            "reason": "Secret rotation requires the owner-controlled BotFather account; no replacement credential is stored in the repository.",
        },
        {
            "gate": "Run one credentialed preview contact submission after environment variables are configured.",
            "status": "BLOCKED_BY_CREDENTIAL_GATE",
            "reason": "The endpoint correctly fails closed with HTTP 503 until credentials exist.",
        },
        {
            "gate": "Explicitly approve the atomic production promotion.",
            "status": "OWNER_APPROVAL_REQUIRED",
            "reason": "The user prohibited production deployment before final approval.",
        },
    ]
    post_release_measurements = [
        "Google Rich Results URL Test on public production URLs (static required-field validation already passes).",
        "Submit the canonical sitemap and confirm Google acceptance plus intended canonical selection.",
        "Measure field LCP, INP, and CLS after sufficient CrUX data exists.",
        "Compare traffic and rankings with the approved baseline during the 30-day monitoring window.",
    ]
    passed = sum(implementation.values())
    status = "READY_FOR_OWNER_RELEASE_GATES" if passed == len(implementation) else "IMPLEMENTATION_GAPS_REMAIN"
    payload = {
        "status": status,
        "generated": str(date.today()),
        "branch": branch,
        "protected_preview": staging["deployment"],
        "implementation_checks": implementation,
        "summary": {"passed": passed, "total": len(implementation), "failed": len(implementation) - passed},
        "lighthouse": {"mobile_performance": mobile, "mobile_quality": mobile_quality, "desktop": desktop},
        "external_release_gates": external_release_gates,
        "post_release_measurements": post_release_measurements,
    }
    (OUTPUT / "completion-audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Roadmap completion audit", "", f"**Status:** {status}", "",
        f"**Protected preview:** `{staging['deployment']}`", "",
        f"**Implementation result:** {passed}/{len(implementation)} checks passed.", "",
        "## Implemented and validated", "", "| Requirement | Result |", "|---|---|",
    ]
    for name, result in implementation.items():
        lines.append(f"| `{name}` | {'PASS' if result else 'FAIL'} |")
    lines.extend(["", "## External release gates", ""])
    for item in external_release_gates:
        lines.append(f"- **{item['status']}:** {item['gate']} {item['reason']}")
    lines.extend(["", "## Post-release measurements", ""])
    lines.extend(f"- {item}" for item in post_release_measurements)
    lines.extend([
        "", "These post-release items cannot truthfully pass before the public atomic release. Production remains unchanged, and no Search Console sitemap submission was altered.",
    ])
    (OUTPUT / "completion-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": passed, "total": len(implementation), "preview": staging["deployment"]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status == "READY_FOR_OWNER_RELEASE_GATES" else 1)


if __name__ == "__main__":
    main()
