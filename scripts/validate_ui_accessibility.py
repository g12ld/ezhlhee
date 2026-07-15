from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "07-ui-accessibility-cro"
EXCLUDED = {"_new_testi.html", "google387142411d334808.html"}
ALLOWED_RGB = {
    (21, 181, 176): "#15B5B0",
    (13, 34, 36): "#0D2224",
    (59, 187, 194): "#3BBBC2",
    (255, 255, 255): "#FFFFFF",
    (85, 85, 85): "#555555",
}


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.ids: list[str] = []
        self.buttons: list[dict[str, str]] = []
        self.button_text: list[str] = []
        self._button_depth = 0
        self._button_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self.tags.append((tag, data))
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "button":
            self.buttons.append(data)
            self._button_depth += 1
            self._button_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._button_depth:
            self.button_text.append(" ".join(self._button_parts).strip())
            self._button_depth -= 1
            self._button_parts = []

    def handle_data(self, data: str) -> None:
        if self._button_depth and data.strip():
            self._button_parts.append(data.strip())


def html_files() -> list[Path]:
    files = [path for path in ROOT.glob("*.html") if path.name not in EXCLUDED]
    files.extend((ROOT / "articles").glob("*.html"))
    return sorted(files)


def css_files() -> list[Path]:
    return sorted(path for path in (ROOT / "images").glob("*.css")) + [ROOT / "style.css", ROOT / "pages.css"]


def canonical(source: str) -> str | None:
    match = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', source, re.I)
    return match.group(1) if match else None


def rgb_values(source: str) -> list[tuple[int, int, int]]:
    values: list[tuple[int, int, int]] = []
    for raw in re.findall(r"#([0-9a-fA-F]{3,8})(?![0-9a-fA-F])", source):
        if len(raw) in {3, 4}:
            raw = "".join(char * 2 for char in raw)
        if len(raw) >= 6:
            values.append(tuple(int(raw[index:index + 2], 16) for index in (0, 2, 4)))
    for match in re.finditer(r"\brgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", source, re.I):
        values.append(tuple(int(value) for value in match.groups()))
    return values


def inline_script_errors(source: str) -> list[str]:
    errors: list[str] = []
    scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", source, flags=re.I | re.S)
    for index, (attrs, body) in enumerate(scripts, start=1):
        if "src=" in attrs.lower() or "application/ld+json" in attrs.lower() or not body.strip():
            continue
        result = subprocess.run(
            ["node", "--check", "-"],
            input=body,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
            check=False,
        )
        if result.returncode:
            errors.append(f"script-{index}: {result.stderr.strip().splitlines()[-1]}")
    return errors


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    files = html_files()
    results: dict[str, dict[str, object]] = {}
    color_inventory: Counter[str] = Counter()

    for path in files:
        source = path.read_text(encoding="utf-8")
        parser = AuditParser()
        parser.feed(source)
        rel = path.relative_to(ROOT).as_posix()
        tags = parser.tags
        html_attrs = next((attrs for tag, attrs in tags if tag == "html"), {})
        mains = [attrs for tag, attrs in tags if tag == "main"]
        images = [attrs for tag, attrs in tags if tag == "img"]
        navs = [attrs for tag, attrs in tags if tag == "nav"]
        blank_links = [attrs for tag, attrs in tags if tag == "a" and attrs.get("target") == "_blank"]
        inputs = [attrs for tag, attrs in tags if tag in {"input", "select", "textarea"}]
        clickable_divs = [attrs for tag, attrs in tags if tag == "div" and attrs.get("onclick")]
        labels_for = {attrs.get("for") for tag, attrs in tags if tag == "label" and attrs.get("for")}
        indexable = canonical(source) is not None

        unlabeled_controls = []
        for attrs in inputs:
            if attrs.get("type") == "hidden" or attrs.get("name") == "website":
                continue
            if not (attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("id") in labels_for):
                unlabeled_controls.append(attrs.get("name") or attrs.get("id") or "unknown")

        unnamed_buttons = []
        for index, attrs in enumerate(parser.buttons):
            text = parser.button_text[index] if index < len(parser.button_text) else ""
            if not (text or attrs.get("aria-label") or attrs.get("title")):
                unnamed_buttons.append(attrs.get("class") or "button")

        file_rgb = rgb_values(source)
        unapproved = sorted({rgb for rgb in file_rgb if rgb not in ALLOWED_RGB})
        script_errors = inline_script_errors(source)
        for rgb in file_rgb:
            if rgb in ALLOWED_RGB:
                color_inventory[ALLOWED_RGB[rgb]] += 1

        checks = {
            "arabic_rtl": html_attrs.get("lang", "").lower() in {"ar", "ar-sa"} and html_attrs.get("dir", "").lower() == "rtl",
            "single_main_landmark": len(mains) == 1 and mains[0].get("id") == "main-content",
            "skip_link": 'class="skip-link"' in source and 'href="#main-content"' in source,
            "labeled_navigation": bool(navs) and all(nav.get("aria-label") or nav.get("aria-labelledby") for nav in navs),
            "image_alt": all("alt" in image and image["alt"].strip() for image in images),
            "image_dimensions": all(image.get("width") and image.get("height") for image in images),
            "image_loading": all(image.get("loading") in {"lazy", "eager"} and image.get("decoding") == "async" for image in images),
            "external_link_safety": all("noopener" in link.get("rel", "") and "noreferrer" in link.get("rel", "") for link in blank_links),
            "labeled_form_controls": not unlabeled_controls,
            "named_buttons": not unnamed_buttons,
            "click_targets_semantic": all(
                div.get("role") == "button" and div.get("tabindex") == "0"
                for div in clickable_divs
                if set(div.get("class", "").split()).intersection({"adv-card", "work-card", "mini-work-card"})
            ),
            "unique_ids": len(parser.ids) == len(set(parser.ids)),
            "focus_visible": ":focus-visible" in source,
            "reduced_motion": "prefers-reduced-motion:reduce" in source,
            "approved_brand_colors": not unapproved,
            "no_faq_schema": "FAQPage" not in source,
            "no_invalid_x_frame_meta": not re.search(r'<meta\s+http-equiv=["\']X-Frame-Options["\']', source, re.I),
            "inline_script_syntax": not script_errors,
            "single_h1_if_indexable": not indexable or len(re.findall(r"<h1\b", source, re.I)) == 1,
        }
        results[rel] = {
            "indexable": indexable,
            "checks": checks,
            "details": {
                "images": len(images),
                "unlabeled_controls": unlabeled_controls,
                "unnamed_buttons": unnamed_buttons,
                "duplicate_ids": sorted(key for key, count in Counter(parser.ids).items() if count > 1),
                "unapproved_rgb": unapproved,
                "inline_script_errors": script_errors,
            },
        }

    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    footer_match = re.search(r"<footer\b.*?</footer>", homepage, re.I | re.S)
    footer = footer_match.group(0) if footer_match else ""
    new_store_assets = [
        "lana-badawood-salla-gold-pro.webp",
        "lara-alsaad-boutique-salla-gold-pro.webp",
        "duk-altayeb-salla-gold-pro.webp",
    ]
    portfolio_start = homepage.find('<div class="work-grid" id="wGrid">')
    portfolio_template = homepage.find('<template id="morePortfolio">', portfolio_start)
    visible_portfolio = homepage[portfolio_start:portfolio_template]
    gold_start = homepage.find('<section class="pro-section sec" id="pro">')
    gold_template = homepage.find('<template id="moreGoldProWorks">', gold_start)
    visible_gold = homepage[gold_start:gold_template]
    homepage_checks = {
        "gold_pro_primary_cta": 'href="#pro" class="btn-primary">اطلب الباقة الذهبية برو' in homepage,
        "accessible_mobile_menu": all(value in homepage for value in ['id="burg"', 'aria-controls="nav"', 'aria-expanded="false"', "event.key==='Escape'"]),
        "accessible_portfolio_dialog": all(value in homepage for value in ['role="dialog"', 'aria-modal="true"', 'aria-hidden="true"', 'aria-labelledby="lbTitle"']),
        "keyboard_portfolio_cards": "[role=\"button\"][onclick]" in homepage and "event.key==='Enter'" in homepage,
        "user_initiated_consultation": "after 8s" not in homepage and "setTimeout(()=>{if(!consultOpen)" not in homepage,
        "no_intrusive_auto_popup": "Consultation choices remain user-initiated" in homepage,
        "hidden_interactive_regions_inert": all(
            value in homepage
            for value in [
                'id="lb" role="dialog" aria-modal="true" aria-hidden="true" inert',
                'id="consultPopup" role="region" aria-label="خيارات التواصل" aria-hidden="true" inert',
                "popup.inert=!consultOpen",
                "dialog.inert=false",
                "dialog.inert=true",
            ]
        ),
        "keyboard_handler_deduplicated": homepage.count("const target=event.target.closest('[role=\"button\"][onclick]')") == 1,
        "deferred_dom_preserves_content": all(
            [
                'id="moreTestimonials"' in homepage,
                'id="morePortfolio"' in homepage,
                len(re.findall(r'<div class="testi-card">', homepage)) == 50,
                len(re.findall(r'<div class="work-card(?:\s|\")', homepage)) == 19,
                "function loadMoreTestimonials()" in homepage,
                "function loadMorePortfolio(moveFocus)" in homepage,
            ]
        ),
        "new_gold_pro_salla_stores": (
            min(portfolio_start, portfolio_template, gold_start, gold_template) >= 0
            and all(asset in visible_portfolio for asset in new_store_assets)
            and all(asset in visible_gold for asset in new_store_assets)
            and [visible_portfolio.find(asset) for asset in new_store_assets]
            == sorted(visible_portfolio.find(asset) for asset in new_store_assets)
            and all(homepage.count(asset) >= 2 for asset in new_store_assets)
        ),
        "deferred_package_and_service_catalogs": all(
            value in homepage
            for value in [
                'id="moreGoldProWorks"',
                'id="moreServices"',
                "function loadMoreGoldProWorks()",
                "function loadMoreServices()",
                'id="comparisonTab0"',
                'id="comparisonTab2"',
            ]
        ),
        "footer_heading_order": bool(footer) and "<h4>" not in footer and footer.count("<h3>") == 3,
        "minimum_touch_targets": all(value in homepage for value in [".ann-close{min-width:44px;min-height:44px", "min-height:48px"]),
    }

    aggregate_checks = {
        "all_file_checks_pass": all(all(item["checks"].values()) for item in results.values()),
        "homepage_cro_checks_pass": all(homepage_checks.values()),
        "maintained_html_count": len(files) == 121,
        "indexable_html_count": sum(bool(item["indexable"]) for item in results.values()) == 119,
    }
    failures = {
        rel: [name for name, passed in item["checks"].items() if not passed]
        for rel, item in results.items()
        if not all(item["checks"].values())
    }
    passed = all(aggregate_checks.values()) and not failures

    payload = {
        "status": "PASS" if passed else "FAIL",
        "summary": {
            "maintained_html": len(files),
            "indexable_html": sum(bool(item["indexable"]) for item in results.values()),
            "file_level_checks": 19,
            "homepage_cro_checks": len(homepage_checks),
            "failed_files": len(failures),
        },
        "aggregate_checks": aggregate_checks,
        "homepage_checks": homepage_checks,
        "failures": failures,
        "files": results,
    }
    (REPORT_DIR / "validation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# UI, accessibility, and CRO validation",
        "",
        f"**Status:** {payload['status']}",
        "",
        f"Validated {len(files)} maintained HTML files ({payload['summary']['indexable_html']} indexable) against 19 repeatable file-level checks.",
        "",
        "## Aggregate release gates",
        "",
    ]
    for name, result in aggregate_checks.items():
        lines.append(f"- {'PASS' if result else 'FAIL'} — `{name}`")
    lines.extend(["", "## Homepage CRO and interaction gates", ""])
    for name, result in homepage_checks.items():
        lines.append(f"- {'PASS' if result else 'FAIL'} — `{name}`")
    lines.extend(["", "## Notes", "", "- Computed contrast and viewport evidence are recorded separately in `viewport-validation.json`.", "- WCAG AA is treated as the target; final automated and manual assistive-technology validation remains a staging release gate."])
    (REPORT_DIR / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with (REPORT_DIR / "brand-color-inventory.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["approved_color", "occurrences"])
        for color, count in sorted(color_inventory.items()):
            writer.writerow([color, count])

    with (REPORT_DIR / "ui-file-inventory.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "ui_accessibility_scope"])
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            if rel == "index.html":
                scope = "brand normalization; landmarks; keyboard interactions; dialog/menu accessibility; Gold Pro CRO"
            elif rel == "blog.html":
                scope = "brand normalization; landmarks; accessible primary navigation"
            else:
                scope = "brand normalization; landmarks; focus/reduced-motion; accessible link safeguards"
            writer.writerow([rel, scope])
        writer.writerow(["pages.css", "shared semantic color tokens and approved brand palette"])
        writer.writerow(["style.css", "approved brand palette normalization"])

    print(json.dumps({"status": payload["status"], **payload["summary"], "failures": failures}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
