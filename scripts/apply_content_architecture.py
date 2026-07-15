#!/usr/bin/env python3
"""Repair redirecting links and add crawlable Saudi-market topic clusters."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.ezhalhe-sa.com"
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "05-content-architecture"
REDIRECT_MAP = ROOT / "reports" / "roadmap-implementation" / "02-information-architecture" / "redirect-map.csv"
ARTICLE_DIR = ROOT / "articles"

ANCHOR_RE = re.compile(
    r'(?P<prefix><a\b[^>]*?\bhref=)(?P<quote>["\'])(?P<href>.*?)(?P=quote)',
    re.I | re.S,
)
H1_CLOSE_RE = re.compile(r"</h1\s*>", re.I)
WHATSAPP_RE = re.compile(r'(?=<a\s+class=["\']whatsapp-float["\'])', re.I)

CLUSTERS = [
    {
        "id": "store-design",
        "name": "تصميم وتجربة المتجر",
        "keywords": ("تصميم", "قالب", "ux", "css", "الهوية", "الجوال"),
        "hub": "/salla-store-design.html",
        "hub_label": "دليل تصميم متجر سلة",
    },
    {
        "id": "seo-analytics",
        "name": "السيو والتحليلات",
        "keywords": ("seo", "محركات-البحث", "google-analytics", "merchant", "تحليل-أداء", "مؤشرات"),
        "hub": "/search-engine-optimization.html",
        "hub_label": "خدمة سيو المتاجر الإلكترونية",
    },
    {
        "id": "verification-business",
        "name": "التوثيق وتأسيس الأعمال",
        "keywords": ("توثيق", "وثيقة-العمل", "الحساب-البنكي", "حساب-بنكي", "منصة-الأعمال", "سجل-تجاري", "الدومين"),
        "hub": "/store-verification.html",
        "hub_label": "دليل توثيق المتجر",
    },
    {
        "id": "payments",
        "name": "الدفع وتابي وتمارا",
        "keywords": ("الدفع", "تابي", "تمارا", "بوابة", "ميس", "مدفوع", "إمكان", "التدفقات-النقدية"),
        "hub": "/secure-payments.html",
        "hub_label": "حلول الدفع الآمنة",
    },
    {
        "id": "marketing-management",
        "name": "التسويق وإدارة المتجر",
        "keywords": (),
        "hub": "/digital-ads.html",
        "hub_label": "خدمات الإعلانات الرقمية",
    },
]


def load_redirects() -> dict[str, str]:
    with REDIRECT_MAP.open(encoding="utf-8-sig", newline="") as handle:
        return {row["source"]: row["destination"] for row in csv.DictReader(handle)}


def local_page_url(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return f"{ORIGIN}/" if relative == "index.html" else f"{ORIGIN}/{relative}"


def normalize_anchor_links(path: Path, redirects: dict[str, str]) -> list[dict[str, str]]:
    content = path.read_text(encoding="utf-8")
    changes: list[dict[str, str]] = []
    source_url = local_page_url(path)

    def replace(match: re.Match[str]) -> str:
        href = html.unescape(match.group("href")).strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            return match.group(0)
        parsed = urlsplit(href)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return match.group(0)
        if parsed.netloc and parsed.netloc.lower() not in {"ezhalhe-sa.com", "www.ezhalhe-sa.com"}:
            return match.group(0)
        resolved = urlsplit(urljoin(source_url, href))
        path_value = unquote(resolved.path) or "/"
        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        query = f"?{parsed.query}" if parsed.query else ""
        destination = redirects.get(path_value)
        if destination:
            destination_path = unquote(urlsplit(destination).path) or "/"
            updated = f"{destination_path}{fragment}"
            reason = "redirect_source_replaced"
        elif parsed.netloc:
            updated = f"{path_value}{query}{fragment}"
            reason = "same_domain_absolute_normalized"
        else:
            return match.group(0)
        if updated == href:
            return match.group(0)
        changes.append(
            {
                "source_file": path.relative_to(ROOT).as_posix(),
                "before": href,
                "after": updated,
                "reason": reason,
            }
        )
        return f"{match.group('prefix')}{match.group('quote')}{html.escape(updated, quote=True)}{match.group('quote')}"

    updated = ANCHOR_RE.sub(replace, content)
    path.write_text(updated, encoding="utf-8", newline="")
    return changes


def cluster_for(path: Path) -> dict:
    slug = path.stem.lower()
    for cluster in CLUSTERS[:-1]:
        if any(keyword in slug for keyword in cluster["keywords"]):
            return cluster
    return CLUSTERS[-1]


def article_title(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", content, re.I | re.S)
    if not match:
        raise RuntimeError(f"Article has no H1: {path}")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip()


def add_article_context() -> list[dict[str, str]]:
    articles = sorted(ARTICLE_DIR.glob("*.html"))
    grouped: dict[str, list[Path]] = {cluster["id"]: [] for cluster in CLUSTERS}
    for path in articles:
        grouped[cluster_for(path)["id"]].append(path)
    rows = []
    for path in articles:
        content = path.read_text(encoding="utf-8")
        if "<parameter name=\"filePath\"" in content or "</content>" in content:
            close = content.lower().find("</html>")
            if close >= 0:
                content = content[: close + len("</html>")] + "\n"
        if "../pages.css" not in content:
            content = content.replace(
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <link rel="stylesheet" href="../pages.css">',
                1,
            )
        content = content.replace('href="/#about"', 'href="/#why-us"')
        if "class=\"article-byline\"" not in content:
            byline = (
                '</h1>\n        <p class="article-byline">'
                '<span>إعداد: <a href="/#why-us">فريق إزهلها</a></span>'
                '<span aria-hidden="true">•</span>'
                '<time datetime="2026-07-15">آخر تحديث: 15 يوليو 2026</time>'
                "</p>"
            )
            content, count = H1_CLOSE_RE.subn(byline, content, count=1)
            if count != 1:
                raise RuntimeError(f"Cannot add byline: {path}")
        cluster = cluster_for(path)
        peers = [candidate for candidate in grouped[cluster["id"]] if candidate != path]
        if len(peers) < 2:
            peers = [candidate for candidate in articles if candidate != path]
        current_index = articles.index(path)
        peers = sorted(peers, key=lambda candidate: abs(articles.index(candidate) - current_index))[:2]
        if "class=\"related-reading\"" not in content:
            links = [
                (cluster["hub"], cluster["hub_label"]),
                *[(f"/articles/{peer.name}", article_title(peer)) for peer in peers],
            ]
            list_items = "\n".join(
                f'        <li><a href="{href}">{html.escape(label)}</a></li>'
                for href, label in links
            )
            block = (
                '<aside class="related-reading" aria-labelledby="related-reading-title">\n'
                '  <h2 id="related-reading-title">تابع القراءة في هذا المسار</h2>\n'
                f'  <p>مسار <strong>{cluster["name"]}</strong> يجمع الأدلة والخدمات المرتبطة بالموضوع.</p>\n'
                "  <ul>\n"
                f"{list_items}\n"
                "  </ul>\n"
                "</aside>\n"
            )
            content, count = WHATSAPP_RE.subn(block, content, count=1)
            if count != 1:
                raise RuntimeError(f"Cannot add related-reading block: {path}")
        path.write_text(content, encoding="utf-8", newline="")
        rows.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "cluster": cluster["name"],
                "hub": cluster["hub"],
                "related_article_1": f"/articles/{peers[0].name}",
                "related_article_2": f"/articles/{peers[1].name}",
                "author": "فريق إزهلها",
                "date_modified": "2026-07-15",
            }
        )
    return rows


def enhance_articles_index() -> None:
    path = ROOT / "articles.html"
    content = path.read_text(encoding="utf-8")
    if "class=\"topic-hubs\"" not in content:
        cards = "".join(
            f'<a href="{cluster["hub"]}"><strong>{cluster["name"]}</strong><span>{cluster["hub_label"]}</span></a>'
            for cluster in CLUSTERS
        )
        block = (
            '<nav class="topic-hubs" aria-labelledby="topic-hubs-title">'
            '<h2 id="topic-hubs-title">مسارات التجارة الإلكترونية</h2>'
            f'<div class="topic-hub-grid">{cards}</div>'
            "</nav>\n    "
        )
        content = content.replace('<div class="articles-container">', block + '<div class="articles-container">', 1)
    missing_href = "articles/كيفية-تصميم-متجر-إلكتروني-احترافي-على-منصة-سلة-وزد.html"
    if missing_href not in content:
        card = f"""
        <div class="article-card">
            <span class="category-badge">تصميم المتجر احترافي (سلة، زد)</span>
            <h3>كيفية تصميم متجر إلكتروني احترافي على منصة سلة وزد</h3>
            <p>دليل عملي من اختيار المنصة والقالب حتى تفعيل الدفع واختبار المتجر قبل الإطلاق.</p>
            <a href="{missing_href}">اقرأ الدليل</a>
        </div>

"""
        content = content.replace('<div class="articles-container">', '<div class="articles-container">\n' + card, 1)
    if "pages.css" not in content:
        content = content.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <link rel="stylesheet" href="pages.css">',
            1,
        )
    path.write_text(content, encoding="utf-8", newline="")


def append_styles() -> None:
    path = ROOT / "pages.css"
    content = path.read_text(encoding="utf-8")
    marker = "/* Content architecture components */"
    if marker in content:
        return
    styles = """

/* Content architecture components */
.article-byline{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin:-.5rem 0 1.5rem;color:#555555;font-size:.95rem}
.article-byline a{color:#0D2224;font-weight:700;text-decoration-thickness:2px;text-underline-offset:3px}
.related-reading{max-width:800px;margin:2rem auto;padding:1.5rem;border:2px solid #15B5B0;border-radius:16px;background:#FFFFFF;color:#555555}
.related-reading h2{margin-top:0;color:#0D2224}
.related-reading ul{margin:1rem 0 0;padding-inline-start:1.25rem}
.related-reading a{color:#0D2224;font-weight:700;text-underline-offset:3px}
.topic-hubs{max-width:1200px;margin:2rem auto;padding:1.5rem}
.topic-hubs h2{text-align:center;color:#0D2224;margin-bottom:1.25rem}
.topic-hub-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem}
.topic-hub-grid a{display:flex;flex-direction:column;gap:.4rem;padding:1.1rem;border:2px solid #15B5B0;border-radius:14px;background:#FFFFFF;color:#0D2224;text-decoration:none}
.topic-hub-grid a:focus-visible,.topic-hub-grid a:hover{outline:3px solid #3BBBC2;outline-offset:3px}
.topic-hub-grid span{color:#555555;font-size:.9rem}
"""
    path.write_text(content.rstrip() + styles + "\n", encoding="utf-8", newline="")


def main() -> None:
    redirects = load_redirects()
    enhance_articles_index()
    cluster_rows = add_article_context()
    append_styles()
    link_changes = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        link_changes.extend(normalize_anchor_links(path, redirects))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    link_report = REPORT_DIR / "internal-link-changes.csv"
    if link_changes or not link_report.exists():
        with link_report.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["source_file", "before", "after", "reason"])
            writer.writeheader()
            writer.writerows(link_changes)
    with (REPORT_DIR / "content-cluster-map.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cluster_rows[0]))
        writer.writeheader()
        writer.writerows(cluster_rows)
    print(
        {
            "internal_links_updated": len(link_changes),
            "articles_clustered": len(cluster_rows),
            "topic_hubs": len(CLUSTERS),
        }
    )


if __name__ == "__main__":
    main()
