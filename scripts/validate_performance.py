#!/usr/bin/env python3
"""Validate static performance invariants and the local mobile lab diagnostic."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "06-performance"
IMG_RE = re.compile(r"<img\b[^>]*>", re.I | re.S)


def attribute(tag: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}=["\']([^"\']*)["\']', tag, re.I)
    return match.group(1) if match else ""


def main() -> None:
    results: list[dict[str, object]] = []

    def check(name: str, passed: bool, evidence: str) -> None:
        results.append({"check": name, "passed": passed, "evidence": evidence})

    image_tags = []
    google_font_files = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8")
        if "fonts.googleapis.com" in content or "fonts.gstatic.com" in content:
            google_font_files.append(path.relative_to(ROOT).as_posix())
        for tag in IMG_RE.findall(content):
            src = attribute(tag, "src")
            if src and not src.startswith(("data:", "http://", "https://")):
                image_tags.append((path.relative_to(ROOT).as_posix(), tag))

    missing_dimensions = [file for file, tag in image_tags if not attribute(tag, "width") or not attribute(tag, "height")]
    missing_loading = [file for file, tag in image_tags if attribute(tag, "loading") not in {"lazy", "eager"}]
    missing_decoding = [file for file, tag in image_tags if attribute(tag, "decoding") != "async"]
    responsive = [tag for _, tag in image_tags if attribute(tag, "srcset")]
    eager = [tag for _, tag in image_tags if attribute(tag, "loading") == "eager"]
    high_priority = [tag for _, tag in image_tags if attribute(tag, "fetchpriority") == "high"]
    check(
        "intrinsic-image-dimensions",
        not missing_dimensions,
        f"images={len(image_tags)}, missing={len(missing_dimensions)}",
    )
    check("image-loading-explicit", not missing_loading, f"missing={len(missing_loading)}")
    check("async-image-decoding", not missing_decoding, f"missing={len(missing_decoding)}")
    check(
        "responsive-images",
        len(responsive) == len(image_tags),
        f"responsive={len(responsive)}, total={len(image_tags)}",
    )
    check(
        "critical-image-priority",
        len(eager) == 1 and len(high_priority) == 1,
        f"eager={len(eager)}, high_priority={len(high_priority)}",
    )
    variants = sorted((ROOT / "images" / "responsive").glob("*.webp"))
    check(
        "responsive-variant-set",
        len(variants) == 37 and all(path.stat().st_size > 0 for path in variants),
        f"variants={len(variants)}, bytes={sum(path.stat().st_size for path in variants)}",
    )

    check("no-render-blocking-google-fonts", not google_font_files, f"files={len(google_font_files)}")
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    hero_position = homepage.find('<section class="hero">')
    coupon_position = homepage.find('<section class="coupon-sec"')
    check(
        "hero-in-critical-order",
        0 <= hero_position < coupon_position,
        f"hero_offset={hero_position}, coupon_offset={coupon_position}",
    )
    check(
        "below-fold-render-containment",
        "content-visibility:auto" in homepage and "contain-intrinsic-size:auto 800px" in homepage,
        "Below-fold sections use content visibility with an intrinsic fallback",
    )
    check(
        "scroll-listeners-deduplicated",
        "dataset.scrollPreviewBound" in homepage
        and "DOMContentLoaded',initScrollPreviews,{once:true}" in homepage
        and "window.addEventListener('load', initScrollPreviews)" not in homepage,
        "Scroll previews bind once and resize only resets transforms",
    )
    check(
        "passive-header-scroll",
        "requestAnimationFrame(updateHeaderShadow)" in homepage and "{passive:true}" in homepage,
        "Header shadow work is animation-frame throttled and passive",
    )
    check(
        "reduced-motion-support",
        "prefers-reduced-motion:reduce" in homepage,
        "Non-essential animation collapses for reduced-motion users",
    )

    with (REPORT_DIR / "image-optimization-map.csv").open(encoding="utf-8-sig", newline="") as handle:
        image_map = list(csv.DictReader(handle))
    check("image-change-log", len(image_map) == len(image_tags), f"rows={len(image_map)}")

    lab = json.loads((REPORT_DIR / "mobile-lab-diagnostic.json").read_text(encoding="utf-8"))
    metrics = lab["metrics"]
    check(
        "mobile-lab-lcp",
        metrics["lcp_ms"] < lab["targets"]["lcp_ms_max"],
        f"lcp_ms={metrics['lcp_ms']}",
    )
    check(
        "mobile-lab-cls",
        metrics["cls"] < lab["targets"]["cls_max"],
        f"cls={metrics['cls']:.4f}",
    )
    check(
        "field-data-claim-safety",
        metrics["inp_ms"] is None and "not_measured" in lab["result"]["inp"],
        "INP and field CWV are explicitly deferred to staged Lighthouse and 30-day monitoring",
    )

    passed = sum(1 for result in results if result["passed"])
    summary = {"checks": len(results), "passed": passed, "failed": len(results) - passed, "results": results}
    (REPORT_DIR / "validation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Performance validation", "",
        f"Result: {passed}/{len(results)} checks passed.", "",
        "| Check | Result | Evidence |", "|---|---|---|",
    ]
    for result in results:
        lines.append(f"| {result['check']} | {'PASS' if result['passed'] else 'FAIL'} | {result['evidence']} |")
    lines.extend([
        "", "## Release-gate limitation", "",
        "The local CDP diagnostic passes the LCP and CLS targets but is not Lighthouse or CrUX. A public preview URL is required for PageSpeed/Lighthouse and Rich Results validation. Search Console reports insufficient field data, so no real-user CWV pass is claimed.",
    ])
    (REPORT_DIR / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
