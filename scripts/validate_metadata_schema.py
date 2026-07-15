#!/usr/bin/env python3
"""Validate metadata uniqueness, social cards, and JSON-LD coverage."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.ezhalhe-sa.com"
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "04-metadata-structured-data"
EXCLUDED = {"404.html", "_new_testi.html", "data-analysis.html", "google387142411d334808.html"}
SERVICE_PAGES = {
    "brand-building.html", "competitor-analysis.html", "digital-ads.html",
    "product-marketing.html", "salla-store-design.html", "salla-store-design-dammam.html",
    "salla-store-design-jeddah.html", "salla-store-design-makkah.html",
    "salla-store-design-riyadh.html", "search-engine-optimization.html",
    "secure-payments.html", "store-verification.html", "zid-store-design.html",
}


def tags(content: str, attribute: str, name: str) -> list[str]:
    pattern = re.compile(
        rf'<meta\b(?=[^>]*\b{attribute}=["\']{re.escape(name)}["\'])[^>]*\bcontent=["\']([^"\']*)',
        re.I,
    )
    return pattern.findall(content)


def simple(content: str, pattern: str) -> list[str]:
    return re.findall(pattern, content, re.I | re.S)


def walk_types(value) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        item_type = value.get("@type")
        if isinstance(item_type, str):
            found.add(item_type)
        elif isinstance(item_type, list):
            found.update(item for item in item_type if isinstance(item, str))
        for child in value.values():
            found.update(walk_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(walk_types(child))
    return found


def walk_nodes(value, requested_type: str) -> list[dict]:
    """Return every JSON-LD object carrying the requested @type, including nested nodes."""
    found: list[dict] = []
    if isinstance(value, dict):
        item_type = value.get("@type")
        if item_type == requested_type or (
            isinstance(item_type, list) and requested_type in item_type
        ):
            found.append(value)
        for child in value.values():
            found.extend(walk_nodes(child, requested_type))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_nodes(child, requested_type))
    return found


def resolve_reference(value, schema) -> dict:
    """Resolve a same-document JSON-LD @id reference for field validation."""
    if not isinstance(value, dict):
        return {}
    reference = value.get("@id")
    if reference and len(value) == 1:
        return next(
            (node for node in walk_nodes(schema, "Organization") if node.get("@id") == reference),
            value,
        )
    return value


def main() -> None:
    results: list[dict[str, object]] = []

    def check(name: str, passed: bool, evidence: str) -> None:
        results.append({"check": name, "passed": passed, "evidence": evidence})

    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative not in EXCLUDED:
            pages.append((relative, path))
    check("indexable-page-count", len(pages) == 119, f"pages={len(pages)}")

    required_social = {
        "og:locale", "og:type", "og:site_name", "og:title", "og:description", "og:url",
        "og:image", "og:image:width", "og:image:height", "og:image:alt",
    }
    required_twitter = {
        "twitter:card", "twitter:title", "twitter:description", "twitter:image", "twitter:image:alt",
    }
    titles, descriptions = [], []
    metadata_errors, schema_errors, rich_result_errors, browser_identity_errors = [], [], [], []
    faq_pages, article_count, service_count, breadcrumb_count = [], 0, 0, 0
    all_types: set[str] = set()

    for relative, path in pages:
        content = path.read_text(encoding="utf-8")
        title_values = [re.sub(r"\s+", " ", value).strip() for value in simple(content, r"<title>(.*?)</title>")]
        description_values = tags(content, "name", "description")
        canonical_values = simple(
            content,
            r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']+)',
        )
        expected_url = f"{ORIGIN}/" if relative == "index.html" else f"{ORIGIN}/{relative}"
        html_ok = bool(re.search(r'<html\b(?=[^>]*\blang="ar-SA")(?=[^>]*\bdir="rtl")', content, re.I))
        if (
            len(title_values) != 1
            or not 25 <= len(title_values[0]) <= 65
            or len(description_values) != 1
            or not 90 <= len(description_values[0]) <= 170
            or canonical_values != [expected_url]
            or not html_ok
        ):
            metadata_errors.append(relative)

        icon_hrefs = simple(content, r'<link\b(?=[^>]*\brel=["\']icon["\'])[^>]*\bhref=["\']([^"\']+)')
        manifest_hrefs = simple(content, r'<link\b(?=[^>]*\brel=["\']manifest["\'])[^>]*\bhref=["\']([^"\']+)')
        if (
            set(icon_hrefs) != {"/favicon.svg", "/images/logo.webp"}
            or manifest_hrefs != ["/site.webmanifest"]
            or tags(content, "name", "theme-color") != ["#0D2224"]
            or tags(content, "name", "msapplication-config") != ["/browserconfig.xml"]
        ):
            browser_identity_errors.append(relative)
            continue
        titles.append(title_values[0])
        descriptions.append(description_values[0])

        for name in required_social:
            if len(tags(content, "property", name)) != 1:
                metadata_errors.append(relative)
                break
        for name in required_twitter:
            if len(tags(content, "name", name)) != 1:
                metadata_errors.append(relative)
                break
        if (
            tags(content, "property", "og:url") != [expected_url]
            or tags(content, "property", "og:image") != [f"{ORIGIN}/images/og-cover.webp"]
            or tags(content, "name", "twitter:image") != [f"{ORIGIN}/images/og-cover.webp"]
            or tags(content, "name", "twitter:card") != ["summary_large_image"]
        ):
            metadata_errors.append(relative)

        blocks = simple(
            content,
            r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        )
        if len(blocks) != 1:
            schema_errors.append(relative)
            continue
        try:
            schema = json.loads(blocks[0].replace("<\\/", "</"))
        except json.JSONDecodeError:
            schema_errors.append(relative)
            continue
        types = walk_types(schema)
        all_types.update(types)
        if "FAQPage" in types:
            faq_pages.append(relative)
        required = {"Organization", "WebSite", "ImageObject", "WebPage"}
        if relative in {"blog.html", "articles.html"}:
            required.remove("WebPage")
            required.add("CollectionPage")
        if relative != "index.html":
            required.add("BreadcrumbList")
            breadcrumb_count += int("BreadcrumbList" in types)
        if relative.startswith("articles/"):
            required.add("Article")
            article_count += int("Article" in types)
            article_node = next(
                (item for item in schema.get("@graph", []) if item.get("@type") == "Article"),
                {},
            )
            if not all(
                article_node.get(key)
                for key in ("headline", "description", "datePublished", "dateModified", "author", "publisher", "image", "mainEntityOfPage")
            ):
                schema_errors.append(relative)
        elif relative in SERVICE_PAGES:
            required.add("Service")
            service_count += int("Service" in types)
        elif relative == "index.html":
            required.update({"Service", "ItemList", "Product", "Offer"})
        if not required <= types:
            schema_errors.append(relative)
        serialized = json.dumps(schema, ensure_ascii=False)
        if "https://ezhalhe-sa.com" in serialized:
            schema_errors.append(relative)
        if "SearchAction" in types or "LocalBusiness" in types:
            schema_errors.append(relative)

        page_rich_errors: list[str] = []
        for article in walk_nodes(schema, "Article"):
            author = article.get("author", {})
            publisher = resolve_reference(article.get("publisher", {}), schema)
            if not all(
                article.get(key)
                for key in (
                    "headline", "description", "datePublished", "dateModified",
                    "image", "mainEntityOfPage",
                )
            ):
                page_rich_errors.append("Article required fields")
            if not isinstance(author, dict) or not author.get("name"):
                page_rich_errors.append("Article author")
            if not isinstance(publisher, dict) or not publisher.get("name") or not publisher.get("logo"):
                page_rich_errors.append("Article publisher")
        for product in walk_nodes(schema, "Product"):
            offers = product.get("offers")
            offer_nodes = offers if isinstance(offers, list) else [offers]
            if not product.get("name") or not offer_nodes or offer_nodes == [None]:
                page_rich_errors.append("Product name/offers")
                continue
            for offer in offer_nodes:
                if not isinstance(offer, dict) or not all(
                    offer.get(key) for key in ("price", "priceCurrency", "availability", "url")
                ):
                    page_rich_errors.append("Offer required fields")
                elif offer.get("priceCurrency") != "SAR" or not str(offer.get("availability", "")).startswith("https://schema.org/"):
                    page_rich_errors.append("Offer currency/availability")
        for breadcrumb in walk_nodes(schema, "BreadcrumbList"):
            items = breadcrumb.get("itemListElement")
            if not isinstance(items, list) or not items:
                page_rich_errors.append("Breadcrumb items")
                continue
            for position, item in enumerate(items, start=1):
                if (
                    not isinstance(item, dict)
                    or item.get("@type") != "ListItem"
                    or item.get("position") != position
                    or not item.get("name")
                    or not item.get("item")
                ):
                    page_rich_errors.append("Breadcrumb ListItem")
        if page_rich_errors:
            rich_result_errors.append(f"{relative}: {', '.join(sorted(set(page_rich_errors)))}")

    title_duplicates = [title for title, count in Counter(titles).items() if count > 1]
    description_duplicates = [value for value, count in Counter(descriptions).items() if count > 1]
    check(
        "metadata-complete-and-bounded",
        not metadata_errors and len(titles) == 119,
        f"valid={len(titles)}, errors={len(set(metadata_errors))}",
    )
    check(
        "metadata-unique",
        not title_duplicates and not description_duplicates,
        f"duplicate_titles={len(title_duplicates)}, duplicate_descriptions={len(description_duplicates)}",
    )
    check(
        "structured-data-json-valid",
        not schema_errors,
        f"errors={len(set(schema_errors))}",
    )
    check(
        "google-rich-result-required-fields",
        not rich_result_errors,
        f"errors={len(rich_result_errors)}",
    )
    check("faqpage-prohibited", not faq_pages and "FAQPage" not in all_types, f"pages={len(faq_pages)}")
    expected_article_count = sum(1 for relative, _ in pages if relative.startswith("articles/"))
    check(
        "article-schema-coverage",
        article_count == expected_article_count,
        f"articles={article_count}, expected={expected_article_count}",
    )
    check("service-schema-coverage", service_count == len(SERVICE_PAGES), f"services={service_count}")
    check("breadcrumb-schema-coverage", breadcrumb_count == 118, f"pages={breadcrumb_count}")
    check(
        "required-schema-types",
        {"Organization", "WebSite", "WebPage", "CollectionPage", "Service", "Product", "Article", "BreadcrumbList", "Offer"} <= all_types,
        "types=" + "|".join(sorted(all_types)),
    )
    image = ROOT / "images" / "og-cover.webp"
    check(
        "social-image-present",
        image.is_file() and image.stat().st_size > 10_000,
        f"bytes={image.stat().st_size if image.exists() else 0}",
    )
    check(
        "single-language-hreflang-decision",
        not any("hreflang=" in path.read_text(encoding="utf-8").lower() for _, path in pages),
        "Arabic-only site: hreflang intentionally omitted",
    )
    check(
        "browser-identity-metadata-coverage",
        not browser_identity_errors,
        f"valid={119 - len(set(browser_identity_errors))}, errors={len(set(browser_identity_errors))}",
    )
    identity_files_ok = False
    try:
        webmanifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
        manifest_alias = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        browserconfig = ET.fromstring((ROOT / "browserconfig.xml").read_text(encoding="utf-8"))
        favicon = ET.fromstring((ROOT / "favicon.svg").read_text(encoding="utf-8"))
        icon = webmanifest.get("icons", [{}])[0]
        identity_files_ok = (
            webmanifest == manifest_alias
            and webmanifest.get("lang") == "ar-SA"
            and webmanifest.get("dir") == "rtl"
            and webmanifest.get("theme_color") == "#0D2224"
            and webmanifest.get("background_color") == "#FFFFFF"
            and icon.get("src") == "/images/logo.webp"
            and (ROOT / "images" / "logo.webp").is_file()
            and browserconfig.findtext("./msapplication/tile/TileColor") == "#0D2224"
            and favicon.tag.endswith("svg")
        )
    except (OSError, ValueError, ET.ParseError, json.JSONDecodeError):
        identity_files_ok = False
    check(
        "browser-identity-files-valid",
        identity_files_ok,
        "favicon.svg, site.webmanifest, manifest.json, browserconfig.xml, and logo asset",
    )

    passed = sum(1 for result in results if result["passed"])
    summary = {"checks": len(results), "passed": passed, "failed": len(results) - passed, "results": results}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "validation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Metadata and structured data validation", "",
        f"Result: {passed}/{len(results)} checks passed.", "",
        "| Check | Result | Evidence |", "|---|---|---|",
    ]
    for result in results:
        lines.append(f"| {result['check']} | {'PASS' if result['passed'] else 'FAIL'} | {result['evidence']} |")
    lines.extend([
        "", "## Deployment validation still required", "",
        "- Run Google Rich Results Test against the staged homepage, one service page, and one article.",
        "- Confirm the staged social preview image is publicly fetchable at 1200×630.",
        "- Reinspect critical pages in Search Console after production release.",
    ])
    (REPORT_DIR / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
