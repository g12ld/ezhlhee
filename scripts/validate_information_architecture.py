#!/usr/bin/env python3
"""Validate canonical, redirect, robots, sitemap, and legacy-link invariants."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.ezhalhe-sa.com"
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "02-information-architecture"
CANONICAL_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']+)',
    re.IGNORECASE,
)
HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.IGNORECASE)
TOKEN_RE = re.compile(r'\b\d{8,12}:[A-Za-z0-9_-]{30,}\b')


def load_csv(name: str) -> list[dict[str, str]]:
    with (REPORT_DIR / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def expected_canonical(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return f"{ORIGIN}/" if relative == "index.html" else f"{ORIGIN}/{relative}"


def local_file_for_url(url: str) -> Path:
    parsed = urlsplit(url)
    relative = unquote(parsed.path).lstrip("/")
    return ROOT / (relative or "index.html")


def main() -> None:
    results: list[dict[str, object]] = []

    def check(name: str, passed: bool, evidence: str) -> None:
        results.append({"check": name, "passed": passed, "evidence": evidence})

    vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    firebase = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))
    redirect_map = load_csv("redirect-map.csv")
    vercel_paths = [row for row in vercel["redirects"] if "has" not in row]
    host_rules = [row for row in vercel["redirects"] if "has" in row]
    redirect_sources = {row["source"] for row in redirect_map}

    check(
        "redirect-map-count",
        len(redirect_map) == 204 and len(vercel_paths) == 204,
        f"map={len(redirect_map)}, vercel_path_rules={len(vercel_paths)}",
    )
    check(
        "redirect-sources-unique",
        len(redirect_sources) == len(redirect_map),
        f"unique={len(redirect_sources)}, total={len(redirect_map)}",
    )
    check(
        "redirect-status-permanent",
        all(row["status"] == "301" for row in redirect_map)
        and all(row.get("permanent") is True for row in vercel_paths),
        "All redirect-map and Vercel path rules are permanent",
    )
    missing_destinations = [
        row["destination"]
        for row in redirect_map
        if not local_file_for_url(row["destination"]).is_file()
    ]
    check(
        "redirect-destinations-exist",
        not missing_destinations,
        f"missing={len(missing_destinations)}",
    )
    chained = []
    for row in redirect_map:
        destination_path = urlsplit(row["destination"]).path
        if destination_path in redirect_sources:
            chained.append(f"{row['source']} -> {destination_path}")
    check("no-redirect-chains", not chained, f"chains={len(chained)}")
    check(
        "canonical-host-rule",
        len(host_rules) == 1
        and host_rules[0].get("destination") == f"{ORIGIN}/:path*"
        and host_rules[0].get("permanent") is True,
        f"host_rules={len(host_rules)}",
    )

    firebase_mismatch = []
    expected_pairs = {(r["source"], r["destination"]) for r in redirect_map}
    for hosting in firebase.get("hosting", []):
        actual_pairs = {
            (r.get("source"), r.get("destination")) for r in hosting.get("redirects", [])
        }
        if actual_pairs != expected_pairs or any(
            r.get("type") != 301 for r in hosting.get("redirects", [])
        ):
            firebase_mismatch.append(hosting.get("target", "unknown"))
    check(
        "firebase-redirect-parity",
        not firebase_mismatch,
        f"mismatched_targets={len(firebase_mismatch)}",
    )

    gsc_urls: list[str] = []
    gsc_dir = ROOT / "reports" / "roadmap-implementation" / "01-search-console-baseline"
    for filename in ("indexing-404-examples.csv", "indexing-redirect-errors.csv"):
        with (gsc_dir / filename).open(encoding="utf-8-sig", newline="") as handle:
            gsc_urls.extend(row["url"] for row in csv.DictReader(handle))
    uncovered = []
    for url in gsc_urls:
        path = unquote(urlsplit(url).path)
        local = ROOT / path.lstrip("/")
        if path not in redirect_sources and not local.is_file():
            uncovered.append(url)
    check(
        "search-console-exclusions-covered",
        not uncovered,
        f"checked={len(gsc_urls)}, uncovered={len(uncovered)}",
    )

    excluded = {
        "404.html",
        "_new_testi.html",
        "data-analysis.html",
        "google387142411d334808.html",
    }
    canonical_errors = []
    canonical_count = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in excluded:
            continue
        matches = CANONICAL_RE.findall(path.read_text(encoding="utf-8"))
        if len(matches) != 1 or matches[0] != expected_canonical(path):
            canonical_errors.append(relative)
        else:
            canonical_count += 1
    check(
        "canonical-coverage",
        not canonical_errors and canonical_count == 119,
        f"valid={canonical_count}, errors={len(canonical_errors)}",
    )

    sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [node.text or "" for node in sitemap_root.findall("sm:url/sm:loc", namespace)]
    sitemap_missing = [url for url in sitemap_urls if not local_file_for_url(url).is_file()]
    sitemap_redirected = [
        url for url in sitemap_urls if urlsplit(url).path in redirect_sources
    ]
    check(
        "sitemap-valid-canonical-urls",
        len(sitemap_urls) == 119
        and len(set(sitemap_urls)) == 119
        and all(url.startswith(f"{ORIGIN}/") for url in sitemap_urls)
        and not sitemap_missing
        and not sitemap_redirected,
        (
            f"urls={len(sitemap_urls)}, unique={len(set(sitemap_urls))}, "
            f"missing={len(sitemap_missing)}, redirected={len(sitemap_redirected)}"
        ),
    )
    lastmods = [
        node.text or "" for node in sitemap_root.findall("sm:url/sm:lastmod", namespace)
    ]
    check(
        "sitemap-lastmod-complete",
        len(lastmods) == len(sitemap_urls)
        and all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) for value in lastmods),
        f"lastmods={len(lastmods)}",
    )

    blog = (ROOT / "blog.html").read_text(encoding="utf-8")
    legacy_count = len(re.findall(r'articles/service\d+-article\d+', blog))
    broken_blog = []
    for href in HREF_RE.findall(blog):
        if href.startswith(("#", "http://", "https://", "mailto:", "tel:", "javascript:")):
            continue
        target = unquote(href.split("#", 1)[0].split("?", 1)[0])
        target = target.lstrip("/") or "index.html"
        if target and not (ROOT / target).is_file():
            broken_blog.append(href)
    check(
        "blog-legacy-links-repaired",
        legacy_count == 0 and not broken_blog,
        f"legacy={legacy_count}, broken={len(broken_blog)}",
    )

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    check(
        "robots-sitemap-canonical",
        f"Sitemap: {ORIGIN}/sitemap.xml" in robots,
        "Robots references the canonical sitemap",
    )
    page_404 = (ROOT / "404.html").read_text(encoding="utf-8")
    check(
        "error-page-noindex",
        'content="noindex, follow"' in page_404 and "canonical" not in page_404.lower(),
        "404 page is noindex and has no canonical declaration",
    )

    secret_hits = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "reports"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".html", ".txt", ".js", ".json", ".py"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        secret_hits += len(TOKEN_RE.findall(content))
    check(
        "telegram-token-scan",
        secret_hits == 0,
        f"potential_live_token_patterns={secret_hits}",
    )

    passed = sum(1 for result in results if result["passed"])
    summary = {
        "checks": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
    (REPORT_DIR / "validation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Information architecture validation",
        "",
        f"Result: {passed}/{len(results)} checks passed.",
        "",
        "| Check | Result | Evidence |",
        "|---|---|---|",
    ]
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"| {result['check']} | {status} | {result['evidence']} |")
    (REPORT_DIR / "validation.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
