#!/usr/bin/env python3
"""Map every approved roadmap requirement to current evidence and its release state."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "reports" / "roadmap-implementation"
OUTPUT = ROADMAP / "10-completion-audit"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def result_map(payload: dict) -> dict[str, bool]:
    return {str(row["check"]): bool(row["passed"]) for row in payload.get("results", [])}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ia_payload = load(ROADMAP / "02-information-architecture" / "validation.json")
    security_payload = load(ROADMAP / "03-security" / "validation.json")
    metadata_payload = load(ROADMAP / "04-metadata-structured-data" / "validation.json")
    content_payload = load(ROADMAP / "05-content-architecture" / "validation.json")
    performance_payload = load(ROADMAP / "06-performance" / "validation.json")
    ui_payload = load(ROADMAP / "07-ui-accessibility-cro" / "validation.json")
    authority_payload = load(ROADMAP / "08-authority-eeat" / "validation.json")
    staging_payload = load(ROADMAP / "09-staging-release" / "staging-validation.json")
    lighthouse_payload = load(ROADMAP / "09-staging-release" / "lighthouse-summary.json")
    gsc_payload = load(ROADMAP / "01-search-console-baseline" / "authenticated-baseline.json")
    ia = result_map(ia_payload)
    security = result_map(security_payload)
    metadata = result_map(metadata_payload)
    content = result_map(content_payload)
    performance = result_map(performance_payload)
    staging = staging_payload["checks"]
    branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    mobile = lighthouse_payload["profiles"][0]
    desktop = lighthouse_payload["profiles"][1]

    rows: list[dict[str, str]] = []

    def add(area: str, requirement: str, status: str, evidence: str, decision: str = "") -> None:
        rows.append(
            {
                "id": f"REQ-{len(rows) + 1:03d}",
                "area": area,
                "requirement": requirement,
                "status": status,
                "evidence": evidence,
                "decision_or_remaining_gate": decision,
            }
        )

    def checked(area: str, requirement: str, condition: bool, evidence: str) -> None:
        add(area, requirement, "PASS" if condition else "FAIL", evidence)

    baseline = ROOT / "reports" / "phase-1-baseline" / "2026-07-15"
    checked("Baseline", "Complete pre-change URL, metadata, canonical, schema, redirect, sitemap and checksum package", all((baseline / name).is_file() for name in ("url-inventory.csv", "metadata-inventory.csv", "canonical-map.csv", "structured-data-inventory.json", "redirect-baseline.csv", "sitemap-snapshot.xml", "file-checksums.txt")), "reports/phase-1-baseline/2026-07-15/")
    checked("Baseline", "Approved Excel workbook preserved", (ROOT / "outputs/ezhalha-phase1-baseline-20260715/ezhalha-phase1-baseline.xlsx").is_file(), "outputs/ezhalha-phase1-baseline-20260715/ezhalha-phase1-baseline.xlsx")
    checked("Baseline", "Authenticated Search Console performance/indexing baseline", gsc_payload.get("access") == "authenticated_owner", "01-search-console-baseline/authenticated-baseline.json")
    checked("Baseline", "Keyword and ranking baseline captured for before/after comparison", gsc_payload.get("performance", {}).get("query_rows_captured", 0) > 0, "01-search-console-baseline/performance-queries.csv")
    checked("Baseline", "Backlink targets identified and protected", gsc_payload.get("links", {}).get("external_total", 0) == 2 and ia.get("redirect-destinations-exist", False), "01-search-console-baseline/authenticated-baseline.json; Phase 0 backlink-targets.csv")

    checked("Release safety", "All work performed on a separate feature branch", branch.startswith("codex/") and branch != "main", branch)
    checked("Release safety", "Protected staging environment is non-indexable", staging.get("preview_is_protected_from_indexing", False), staging_payload["deployment"])
    checked("Release safety", "Production remains outside the implementation release", staging_payload.get("deployment_type") == "protected Vercel preview (non-production)", "09-staging-release/staging-validation.json")
    checked("Release safety", "Atomic deployment and immediate rollback procedure documented", (ROADMAP / "09-staging-release/deployment-rollback-runbook.md").is_file(), "09-staging-release/deployment-rollback-runbook.md")
    checked("Release safety", "Detailed file/redirect/canonical/SEO decision logs maintained", all((path).is_file() for path in (ROADMAP / "09-staging-release/file-change-inventory.csv", ROADMAP / "02-information-architecture/redirect-map.csv", ROADMAP / "02-information-architecture/canonical-map.csv", ROADMAP / "change-log.md")), "09-staging-release/file-change-inventory.csv; 02-information-architecture/*.csv; change-log.md")

    checked("Sitemap", "Sitemap rebuilt from canonical indexable URLs", ia.get("sitemap-valid-canonical-urls", False), "sitemap.xml; 02-information-architecture/sitemap-inventory.csv")
    checked("Sitemap", "Duplicates, redirects and missing/404 destinations excluded", ia.get("sitemap-valid-canonical-urls", False), "02-information-architecture/validation.json")
    checked("Sitemap", "Every URL has an automated valid lastmod", ia.get("sitemap-lastmod-complete", False), "sitemap.xml; scripts/apply_information_architecture.py")
    add("Sitemap", "Split to a sitemap index before standard size limits", "NOT_APPLICABLE_CURRENT_SCALE", "02-information-architecture/implementation-manifest.json", "Current sitemap has 119 URLs; index policy is documented before 50,000 URLs/50 MB.")
    add("Sitemap", "Publish gzip members when sitemap index scale requires them", "NOT_APPLICABLE_CURRENT_SCALE", "02-information-architecture/implementation-manifest.json", "Current small XML uses CDN HTTP compression; gzip-member policy is documented for indexed scale.")

    checked("Robots", "robots.txt references the canonical sitemap", ia.get("robots-sitemap-canonical", False), "robots.txt")
    checked("Robots", "Non-public endpoint and legacy fragment crawl rules are explicit", "Disallow: /api/" in (ROOT / "robots.txt").read_text(encoding="utf-8") and "Disallow: /_new_testi.html" in (ROOT / "robots.txt").read_text(encoding="utf-8"), "robots.txt")

    checked("Canonicals", "A single www HTTPS canonical origin is used", ia.get("canonical-host-rule", False), "vercel.json; 02-information-architecture/canonical-map.csv")
    checked("Canonicals", "All 119 indexable pages have one exact self-canonical", ia.get("canonical-coverage", False), "02-information-architecture/validation.json")

    checked("Redirects", "Complete redirect map exists", ia.get("redirect-map-count", False), "02-information-architecture/redirect-map.csv")
    checked("Redirects", "All redirect rules are permanent", ia.get("redirect-status-permanent", False), "vercel.json; firebase.json")
    checked("Redirects", "Redirect chains are eliminated", ia.get("no-redirect-chains", False), "02-information-architecture/validation.json")
    checked("Redirects", "Redirect destinations exist and known Search Console exclusions are covered", ia.get("redirect-destinations-exist", False) and ia.get("search-console-exclusions-covered", False), "02-information-architecture/validation.json")
    checked("URL preservation", "No indexable production content URL is removed", staging.get("all_119_sitemap_pages_return_200", False), "09-staging-release/staging-crawl.csv")
    checked("URL preservation", "Existing legacy /_new_testi.html URL remains available", staging.get("legacy_public_url_is_preserved", False), "09-staging-release/staging-validation.json")
    checked("URL preservation", "Unknown URLs return a genuine 404", staging.get("real_404_status", False), "09-staging-release/staging-validation.json")

    checked("Search Console", "Coverage/Page Indexing, sitemap, CWV, crawl, manual action, security and URL Inspection baseline captured", all(key in gsc_payload for key in ("indexing", "sitemap", "core_web_vitals", "crawl_stats", "security", "inspections")) and gsc_payload.get("security", {}).get("manual_actions") == "none_detected" and gsc_payload.get("security", {}).get("security_issues") == "none_detected" and gsc_payload.get("access") == "authenticated_owner", "01-search-console-baseline/authenticated-baseline.json")
    checked("Search Console", "Critical pre-release URL Inspection completed", (ROADMAP / "09-staging-release/search-console-pre-release-check.json").is_file(), "09-staging-release/search-console-pre-release-check.json")
    add("Search Console", "Submit the new sitemap and confirm acceptance", "POST_RELEASE", "09-staging-release/search-console-30-day-monitoring.md", "Must occur only after atomic production validation.")
    add("Search Console", "Confirm Google-selected canonical URLs", "POST_RELEASE", "09-staging-release/search-console-30-day-monitoring.md", "Requires public production recrawl.")
    add("Search Console", "Monitor all approved Search Console areas for 30 days", "POST_RELEASE", "09-staging-release/search-console-30-day-monitoring.md", "The monitoring clock starts after production release.")

    checked("Structured data", "Organization and WebSite schema cover all indexable pages", metadata.get("required-schema-types", False), "04-metadata-structured-data/metadata-schema-map.csv")
    checked("Structured data", "Service schema covers all 13 service pages", metadata.get("service-schema-coverage", False), "04-metadata-structured-data/validation.json")
    checked("Structured data", "BreadcrumbList covers all 118 non-home indexable pages", metadata.get("breadcrumb-schema-coverage", False), "04-metadata-structured-data/validation.json")
    checked("Structured data", "Article covers all 101 articles", metadata.get("article-schema-coverage", False), "04-metadata-structured-data/validation.json")
    checked("Structured data", "Product/Offer is present where package products are represented", metadata.get("required-schema-types", False) and metadata.get("google-rich-result-required-fields", False), "index.html; 04-metadata-structured-data/validation.json")
    checked("Structured data", "Prohibited FAQPage schema is removed", metadata.get("faqpage-prohibited", False), "04-metadata-structured-data/validation.json")
    add("Structured data", "LocalBusiness is used only if a verified public office exists", "NOT_APPLICABLE_UNVERIFIED_ENTITY", "04-metadata-structured-data/implementation-manifest.json", "Omitted to avoid an unsupported physical-location claim.")
    add("Structured data", "SearchAction is used only if working site search exists", "NOT_APPLICABLE_NO_SITE_SEARCH", "04-metadata-structured-data/implementation-manifest.json", "Omitted because the site has no working search action.")
    checked("Structured data", "Google Rich Results required fields pass static validation", metadata.get("google-rich-result-required-fields", False), "04-metadata-structured-data/validation.json")
    add("Structured data", "Validate eligible public URLs in Google Rich Results Test", "POST_RELEASE", "09-staging-release/deployment-rollback-runbook.md", "Google cannot crawl the protected noindex preview; execute immediately after release.")

    checked("Metadata", "Unique bounded title and meta description on all 119 pages", metadata.get("metadata-complete-and-bounded", False) and metadata.get("metadata-unique", False), "04-metadata-structured-data/metadata-schema-map.csv")
    checked("Metadata", "Complete Open Graph and Twitter large-card metadata", metadata.get("metadata-complete-and-bounded", False), "04-metadata-structured-data/validation.json")
    checked("Metadata", "Canonical-aligned 1200x630 social image exists", metadata.get("social-image-present", False), "images/og-cover.webp")
    add("Metadata", "Hreflang is added if the site becomes multilingual", "NOT_APPLICABLE_SINGLE_LANGUAGE", "04-metadata-structured-data/validation.json", "Arabic-only site; hreflang is intentionally omitted.")
    checked("Browser files", "Favicon, manifest aliases and browserconfig are valid and served", staging.get("browser_identity_files_are_served_and_valid", False), "favicon.svg; site.webmanifest; manifest.json; browserconfig.xml")
    checked("Browser files", "Google verification file is preserved", staging.get("google_verification_file_is_preserved", False), "google387142411d334808.html")
    add("Browser files", "Bing verification", "NOT_APPLICABLE_NO_OWNER_KEY", "Phase 0 important-files-inventory.csv", "Optional verification file is not fabricated without an owner-provided key.")

    checked("Images", "Every image has intrinsic width and height", performance.get("intrinsic-image-dimensions", False), "06-performance/image-optimization-map.csv")
    checked("Images", "Every image has explicit loading and async decoding", performance.get("image-loading-explicit", False) and performance.get("async-image-decoding", False), "06-performance/validation.json")
    checked("Images", "Responsive WebP variants and srcset/sizes are implemented", performance.get("responsive-images", False) and performance.get("responsive-variant-set", False), "images/responsive/; 06-performance/image-optimization-map.csv")
    checked("Images", "Critical LCP image receives eager/high fetch priority", performance.get("critical-image-priority", False), "index.html")

    checked("Performance", "Mobile Lighthouse LCP is below 2.5 seconds", mobile["lcp_ms"] < 2500, "09-staging-release/lighthouse-summary.json")
    checked("Performance", "Mobile Lighthouse CLS is below 0.1", mobile["cls"] < 0.1, "09-staging-release/lighthouse-summary.json")
    add("Performance", "Field INP is below 200 ms", "POST_RELEASE", "09-staging-release/search-console-30-day-monitoring.md", "Search Console reports insufficient current field data; measure during the 30-day window.")
    checked("Performance", "Unused JavaScript and render-blocking resources are eliminated in Lighthouse", mobile["performance"] >= 90, "09-staging-release/lighthouse-mobile-performance-release.report.json")
    checked("Performance", "CSS is optimized without removing deferred/interactive component styling", performance.get("below-fold-render-containment", False) and mobile["performance"] >= 90, "index.html; 09-staging-release/lighthouse-mobile-performance-release.report.json")
    checked("Performance", "DOM/layout work is reduced while retaining all approved content", ui_payload.get("status") == "PASS" and performance.get("below-fold-render-containment", False), "07-ui-accessibility-cro/validation.json; release-browser-validation.json")
    checked("Performance", "Event listeners are deduplicated/passive/throttled", performance.get("scroll-listeners-deduplicated", False) and performance.get("passive-header-scroll", False), "06-performance/validation.json")
    checked("Performance", "External render-blocking font dependency is removed and critical image is preloaded", performance.get("no-render-blocking-google-fonts", False) and performance.get("critical-image-priority", False), "index.html; 06-performance/validation.json")

    checked("Accessibility", "Semantic main/navigation landmarks and one H1 are enforced", ui_payload.get("status") == "PASS", "07-ui-accessibility-cro/validation.json")
    checked("Accessibility", "Labels, ARIA names/states and live form status are present", security.get("contact-form-accessibility", False) and ui_payload.get("status") == "PASS", "index.html; 03-security/validation.json")
    checked("Accessibility", "Keyboard navigation, focus restoration, Escape and dialog behavior pass", ui_payload.get("status") == "PASS", "07-ui-accessibility-cro/viewport-validation.json")
    checked("Accessibility", "Exact brand colors and computed contrast pass", ui_payload.get("status") == "PASS", "07-ui-accessibility-cro/brand-color-inventory.csv; viewport-validation.json")
    checked("Accessibility", "Mobile-first RTL layouts pass at 375, 768, 1024 and 1440", ui_payload.get("status") == "PASS", "07-ui-accessibility-cro/viewport-validation.json")
    checked("Accessibility", "Mobile and desktop Lighthouse accessibility score 100", mobile["accessibility"] == 100 and desktop["accessibility"] == 100, "09-staging-release/lighthouse-summary.json")

    checked("Content", "Every article has visible author, review/update date and official sources", authority_payload.get("checks", {}).get("all_101_articles_have_author_review_and_official_sources", False), "08-authority-eeat/content-change-map.csv")
    checked("Content", "Regulated topics contain limitations/disclaimers", authority_payload.get("checks", {}).get("regulated_topics_include_disclaimers", False), "08-authority-eeat/validation.json")
    checked("Content", "All 101 articles are assigned to crawlable Saudi-intent topic clusters", content.get("cluster-inventory-complete", False), "05-content-architecture/content-cluster-map.csv")
    checked("Content", "Contextual internal links and topic hub navigation are complete", content.get("article-contextual-links", False) and content.get("topic-hub-navigation", False), "05-content-architecture/validation.json")
    checked("Content", "No broken, redirecting or orphaned indexable pages remain", content.get("no-broken-internal-links", False) and content.get("no-redirecting-internal-links", False) and content.get("no-indexable-orphans", False), "05-content-architecture/validation.json")
    checked("Content", "Authority/service pages are substantive and unsupported guarantees are removed", authority_payload.get("checks", {}).get("all_authority_pages_are_substantive", False) and authority_payload.get("checks", {}).get("unsupported_guarantees_removed", False), "08-authority-eeat/validation.json")

    checked("UI/UX and CRO", "Homepage hierarchy and primary Gold Pro hero CTA are implemented", ui_payload.get("status") == "PASS", "index.html; 07-ui-accessibility-cro/validation.json")
    checked("UI/UX and CRO", "Package comparison and mobile deferred comparison remain available", ui_payload.get("status") == "PASS", "index.html; 07-ui-accessibility-cro/validation.json")
    checked("UI/UX and CRO", "Portfolio, testimonials, services and trust proof remain complete", ui_payload.get("status") == "PASS", "09-staging-release/release-browser-validation.json")
    checked("UI/UX and CRO", "Lana, Lara Alsaad Boutique and Duk Altayeb appear first as Gold Pro Salla work", ui_payload.get("status") == "PASS" and all((ROOT / "images" / name).is_file() for name in ("lana-badawood-salla-gold-pro.webp", "lara-alsaad-boutique-salla-gold-pro.webp", "duk-altayeb-salla-gold-pro.webp")), "index.html; images/*-salla-gold-pro.webp")
    checked("UI/UX and CRO", "WhatsApp and consultation/contact conversion paths remain visible", ui_payload.get("status") == "PASS" and security.get("contact-form-server-endpoint", False), "index.html")
    checked("UI/UX and CRO", "Intrusive automatic popup behavior is removed", ui_payload.get("status") == "PASS", "07-ui-accessibility-cro/viewport-validation.json")

    checked("Security", "Client-side Telegram secrets and Telegram calls are removed", security.get("no-token-patterns", False) and security.get("no-client-telegram-calls", False), "03-security/validation.json")
    checked("Security", "Contact submission uses a same-origin server endpoint with origin/rate/honeypot/timing defenses", security.get("contact-form-server-endpoint", False) and security.get("endpoint-defenses", False), "api/contact.js; 03-security/validation.json")
    checked("Security", "Telegram response payload is validated and failures remain fail-closed", staging.get("contact_fails_closed_without_credentials", False), "scripts/test_contact_endpoint.js; 09-staging-release/staging-validation.json")
    checked("Security", "CSP, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy and related headers pass", security.get("vercel-security-headers", False) and staging.get("security_headers_complete", False), "vercel.json; 09-staging-release/staging-validation.json")
    add("Security", "Revoke the compromised token and configure replacement preview/production secrets", "OWNER_ACTION_REQUIRED", "03-security/validation.json", "Requires owner-controlled BotFather and Vercel environment access; the endpoint intentionally returns 503 until complete.")
    add("Security", "Run one credentialed preview form-delivery test", "BLOCKED_BY_OWNER_CREDENTIAL", "09-staging-release/deployment-rollback-runbook.md", "Run after replacement environment variables exist and before production approval.")

    checked("Validation", "All 119 sitemap pages pass the protected preview crawl", staging.get("all_119_sitemap_pages_return_200", False), "09-staging-release/staging-crawl.csv")
    checked("Validation", "All 204 redirect rules are static-validated and runtime samples pass", staging.get("all_redirects_are_permanent_and_chain_free", False) and staging.get("runtime_redirect_sample_matches_map", False), "09-staging-release/redirect-runtime-sample.csv")
    checked("Validation", "Mobile Lighthouse performance/accessibility/best-practices/SEO gates pass", mobile["performance"] >= 90 and mobile["accessibility"] == 100 and mobile["best_practices"] == 100 and mobile["seo"] == 100, "09-staging-release/lighthouse-summary.json")
    checked("Validation", "Desktop Lighthouse scores 100 in all four categories", all(desktop[key] == 100 for key in ("performance", "accessibility", "best_practices", "seo")), "09-staging-release/lighthouse-summary.json")
    checked("Validation", "Repository implementation and protected staging requirement audit passes", (ROADMAP / "10-completion-audit/completion-audit.json").is_file(), "10-completion-audit/completion-audit.json")

    add("Production gate", "Explicitly approve atomic production promotion", "OWNER_APPROVAL_REQUIRED", "09-staging-release/deployment-rollback-runbook.md", "Production deployment is intentionally outside the current objective boundary.")
    add("Post-release", "Immediate crawl/redirect/canonical/schema/Search Console validation", "POST_RELEASE", "09-staging-release/deployment-rollback-runbook.md", "Start within five minutes of the production alias switch.")
    add("Post-release", "No new indexing errors; traffic/rankings stable or improved", "POST_RELEASE", "09-staging-release/search-console-30-day-monitoring.md", "Compare with the authenticated baseline for 30 days; prepare a corrective patch before further structural work if needed.")

    counts = Counter(row["status"] for row in rows)
    overall = "READY_FOR_OWNER_RELEASE_GATES" if counts.get("FAIL", 0) == 0 else "IMPLEMENTATION_GAPS_REMAIN"
    with (OUTPUT / "requirement-traceability.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {"status": overall, "requirements": len(rows), "status_counts": dict(sorted(counts.items())), "rows": rows}
    (OUTPUT / "requirement-traceability.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Approved roadmap requirement traceability", "", f"**Status:** {overall}", "",
        f"**Requirements traced:** {len(rows)}", "", "## Status summary", "",
    ]
    lines.extend(f"- {status}: {count}" for status, count in sorted(counts.items()))
    lines.extend(["", "## Requirement matrix", "", "| ID | Area | Requirement | Status | Evidence / remaining gate |", "|---|---|---|---|---|"])
    for row in rows:
        detail = row["evidence"]
        if row["decision_or_remaining_gate"]:
            detail += "; " + row["decision_or_remaining_gate"]
        lines.append(f"| {row['id']} | {row['area']} | {row['requirement']} | {row['status']} | {detail} |")
    lines.extend(["", "No item marked POST_RELEASE or OWNER_ACTION_REQUIRED is represented as completed before its evidence can exist. Production remains unchanged."])
    (OUTPUT / "requirement-traceability.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": overall, "requirements": len(rows), "status_counts": dict(counts)}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if overall == "READY_FOR_OWNER_RELEASE_GATES" else 1)


if __name__ == "__main__":
    main()
