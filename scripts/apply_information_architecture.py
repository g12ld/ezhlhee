#!/usr/bin/env python3
"""Apply the approved canonical-host and one-hop redirect architecture."""

from __future__ import annotations

import csv
import html
import json
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ORIGIN = "https://www.ezhalhe-sa.com"
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "02-information-architecture"

ANALYTICS_ARTICLE = (
    "articles/تحليل-أداء-المتجر-وحسابات-التواصل-الاجتماعي-"
    "مؤشرات-الأداء-الرئيسية-kpis.html"
)

ANCHOR_TARGETS = {
    "10 طرق لتحسين واجهة متجرك الإلكتروني": "articles/عناصر-التصميم-التي-تزيد-من-معدل-التحويل-في-المتاجر-الإلكترونية.html",
    "أفضل ألوان واجهة متجر لزيادة المبيعات": "articles/دور-الهوية-البصرية-في-نجاح-متجرك-الإلكتروني-الاحترافي.html",
    "أهمية الصور الاحترافية في المتجر": "articles/أسرار-تصميم-صفحات-المنتجات-الجذابة-على-منصة-سلة.html",
    "SEO للمتاجر: أساسيات مهمة": "articles/تحسين-seo-للمتاجر-الإلكترونية-على-سلة-دليل-شامل-للبداية.html",
    "كيفية اختيار الباقات المناسبة لتطوير المتجر": "articles/مقارنة-شاملة-بين-باقات-تصميم-متجر-سلة-بيسك-بلس-برو-ذهبية.html",
    "أدوات تصميم سهلة وسريعة": "articles/كيف-تختار-قالب-متجر-زد-المناسب-لمنتجاتك-دليل-عملي.html",
    "تحسين سرعة المتجر على جميع الأجهزة": "articles/تصميم-متجر-إلكتروني-متوافق-مع-الجوال-mobile-first-design-على-زد.html",
    "تجربة المستخدم UX للمتاجر الإلكترونية": "articles/تصميم-تجربة-المستخدم-ux-في-متجرك-الإلكتروني-خطوات-التنفيذ.html",
    "تصميم المتاجر للهواتف المحمولة": "articles/تصميم-متجر-إلكتروني-متوافق-مع-الجوال-mobile-first-design-على-زد.html",
    "أخطاء شائعة في تصميم المتاجر وتجنبها": "articles/أخطاء-شائعة-في-تصميم-المتاجر-الإلكترونية-وكيفية-تجنبها.html",
    "إدارة المتاجر: نصائح عملية": "articles/كيف-تضمن-إدارة-متجرك-الإلكتروني-بكفاءة-عالية-لمدة-شهر.html",
    "توثيق المتاجر: دليل شامل": "store-verification.html",
    "مدفوعات آمنة: كيفية التفعيل": "secure-payments.html",
    "تحليل البيانات: تحسين الأداء": ANALYTICS_ARTICLE,
    "تسويق المنتجات: استراتيجيات فعالة": "product-marketing.html",
    "تحسين محركات البحث: خطوات متقدمة": "search-engine-optimization.html",
    "خدمة العملاء: أفضل الممارسات": "articles/إدارة-خدمة-العملاء-عبر-التواصل-الاجتماعي-نصائح-لرضا-العميل.html",
    "تحليل المنافسين: كيف تتفوق": "competitor-analysis.html",
    "الإعلانات الرقمية: تحقيق النتائج": "digital-ads.html",
    "بناء العلامة التجارية: استراتيجيات مبتكرة": "brand-building.html",
    "التصميم البسيط: نصائح لتحقيق التناسق": "articles/تصميم-متجر-احترافي-استراتيجيات-لتمييز-متجرك-عن-المنافسين.html",
    "استخدام الخطوط بشكل صحيح: أهم النصائح": "articles/دور-الهوية-البصرية-في-نجاح-متجرك-الإلكتروني-الاحترافي.html",
    "الألوان النفسية: كيف تؤتر على الزوار؟": "articles/دور-الهوية-البصرية-في-نجاح-متجرك-الإلكتروني-الاحترافي.html",
    "تصميم الشعارات: دليل سريع": "brand-building.html",
    "الرسوم البيانية: كيف استخدامها بفعالية": ANALYTICS_ARTICLE,
    "تصميم الهوية البصرية: أساسيات مهمة": "brand-building.html",
    "التفاعل مع المستخدمين: كيف تعزيز التجربة": "articles/تصميم-تجربة-المستخدم-ux-في-متجرك-الإلكتروني-خطوات-التنفيذ.html",
    "تحسين صفحات الهبوط: نصائح وأسرار": "articles/عناصر-التصميم-التي-تزيد-من-معدل-التحويل-في-المتاجر-الإلكترونية.html",
    "تحليل التصميم: أدوات مفيدة": "articles/تصميم-متجر-احترافي-استراتيجيات-لتمييز-متجرك-عن-المنافسين.html",
    "التصميم المتجاوب: كيف التنفيذ": "articles/تصميم-متجر-إلكتروني-متوافق-مع-الجوال-mobile-first-design-على-زد.html",
}

LEGACY_LINK_RE = re.compile(
    r'<a(?P<before>[^>]*?)href="(?P<source>articles/service\d+-article\d+\.html)"'
    r'(?P<after>[^>]*)>(?P<anchor>[^<]+)</a>',
    re.IGNORECASE,
)
CANONICAL_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', re.IGNORECASE
)
ROBOTS_RE = re.compile(
    r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', re.IGNORECASE
)
TITLE_RE = re.compile(r'</title\s*>', re.IGNORECASE)


def write_text(path: Path, content: str) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    return True


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def canonical_url(target: str) -> str:
    return f"{CANONICAL_ORIGIN}/{target.lstrip('/')}" if target else f"{CANONICAL_ORIGIN}/"


def local_target_exists(target: str) -> bool:
    parsed = urlsplit(target)
    path = unquote(parsed.path).lstrip("/")
    if not path:
        return (ROOT / "index.html").is_file()
    return (ROOT / path).is_file()


def extract_legacy_links() -> list[dict[str, str]]:
    blog_path = ROOT / "blog.html"
    source = blog_path.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        anchor = html.unescape(match.group("anchor")).strip()
        target = ANCHOR_TARGETS.get(anchor)
        if not target:
            raise RuntimeError(f"No semantic redirect target for blog anchor: {anchor}")
        if not (ROOT / target).is_file():
            raise RuntimeError(f"Redirect target does not exist: {target}")
        rows.append(
            {
                "source": f"/{match.group('source')}",
                "anchor_text": anchor,
                "destination": canonical_url(target),
                "internal_link_destination": target,
                "reason": "Legacy blog reference mapped to the closest live topical page",
            }
        )
        return (
            f'<a{match.group("before")}href="{target}"{match.group("after")}>'
            f'{match.group("anchor")}</a>'
        )

    updated = LEGACY_LINK_RE.sub(replace, source)
    if not rows:
        baseline = subprocess.run(
            ["git", "show", "HEAD:blog.html"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if baseline.returncode == 0:
            LEGACY_LINK_RE.sub(replace, baseline.stdout)
    if len(rows) != 100:
        raise RuntimeError(f"Expected 100 legacy blog references, found {len(rows)}")
    write_text(blog_path, updated)
    return rows


def build_redirects(legacy_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    redirect_rows: list[dict[str, str]] = [
        {
            "source": "/index.html",
            "destination": canonical_url(""),
            "status": "301",
            "reason": "Consolidate the duplicate homepage URL",
            "evidence": "Search Console reports the apex /index.html as separately indexed",
        },
        {
            "source": "/data-analysis.html",
            "destination": canonical_url(ANALYTICS_ARTICLE),
            "status": "301",
            "reason": "Replace a homepage redirect with the closest topical successor",
            "evidence": "Existing production redirect preserved with improved relevance",
        },
        {
            "source": "/articles/guide-design-store.html",
            "destination": canonical_url("salla-store-design.html"),
            "status": "301",
            "reason": "Preserve the legacy guide path with a relevant Salla service successor",
            "evidence": "Search Console 404 example",
        },
        {
            "source": "/articles/guide-design-store",
            "destination": canonical_url("salla-store-design.html"),
            "status": "301",
            "reason": "Cover the extensionless legacy guide variant",
            "evidence": "Redirect-normalization rule",
        },
    ]

    seen = {row["source"] for row in redirect_rows}
    for row in legacy_rows:
        for source in (row["source"], row["source"].removesuffix(".html")):
            if source in seen:
                continue
            seen.add(source)
            redirect_rows.append(
                {
                    "source": source,
                    "destination": row["destination"],
                    "status": "301",
                    "reason": row["reason"],
                    "evidence": "Blog inventory and Search Console exclusion examples",
                }
            )

    for row in redirect_rows:
        if not local_target_exists(row["destination"]):
            raise RuntimeError(f"Redirect destination is not a live local page: {row}")
    return redirect_rows


def update_vercel(redirect_rows: list[dict[str, str]]) -> None:
    path = ROOT / "vercel.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    redirects = [
        {
            "source": row["source"],
            "destination": row["destination"],
            "permanent": True,
        }
        for row in redirect_rows
    ]
    redirects.append(
        {
            "source": "/:path*",
            "has": [{"type": "host", "value": "ezhalhe-sa.com"}],
            "destination": f"{CANONICAL_ORIGIN}/:path*",
            "permanent": True,
        }
    )
    config["redirects"] = redirects
    write_text(path, json.dumps(config, ensure_ascii=False, indent=2) + "\n")


def update_firebase(redirect_rows: list[dict[str, str]]) -> None:
    path = ROOT / "firebase.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    redirects = [
        {
            "source": row["source"],
            "destination": row["destination"],
            "type": 301,
        }
        for row in redirect_rows
    ]
    for hosting in config.get("hosting", []):
        hosting["redirects"] = redirects
    write_text(path, json.dumps(config, ensure_ascii=False, indent=2) + "\n")


def page_canonical(path: Path) -> str | None:
    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return canonical_url("")
    if relative in {
        "404.html",
        "_new_testi.html",
        "data-analysis.html",
        "google387142411d334808.html",
    }:
        return None
    return canonical_url(relative)


def update_canonicals() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        expected = page_canonical(path)
        if expected is None:
            continue
        content = path.read_text(encoding="utf-8")
        existing_match = CANONICAL_RE.search(content)
        existing = ""
        if existing_match:
            href_match = re.search(r'href=["\']([^"\']+)', existing_match.group(0), re.I)
            existing = href_match.group(1) if href_match else ""
            updated = CANONICAL_RE.sub(
                f'<link rel="canonical" href="{expected}">', content, count=1
            )
            action = "updated" if existing != expected else "unchanged"
        else:
            replacement = f'</title>\n    <link rel="canonical" href="{expected}">'
            updated, count = TITLE_RE.subn(replacement, content, count=1)
            if count != 1:
                raise RuntimeError(f"Cannot insert canonical into {path}")
            action = "added"
        write_text(path, updated)
        rows.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "previous_canonical": existing,
                "canonical": expected,
                "action": action,
            }
        )
    return rows


def apply_noindex(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    tag = '<meta name="robots" content="noindex, follow">'
    if ROBOTS_RE.search(content):
        updated = ROBOTS_RE.sub(tag, content, count=1)
    else:
        updated, count = TITLE_RE.subn(f"</title>\n    {tag}", content, count=1)
        if count != 1:
            updated, count = re.subn(
                r'(<head\b[^>]*>)', rf'\1\n    {tag}', content, count=1, flags=re.I
            )
        if count != 1:
            raise RuntimeError(f"Cannot add robots directive to {path}")
    write_text(path, updated)


def git_lastmod(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", relative],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    value = result.stdout.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def sitemap_pages() -> list[dict[str, str]]:
    excluded = {
        "404.html",
        "_new_testi.html",
        "data-analysis.html",
        "google387142411d334808.html",
        "index.html",
    }
    index_path = ROOT / "index.html"
    rows = [
        {
            "path": "/",
            "url": canonical_url(""),
            "lastmod": git_lastmod(index_path),
            "changefreq": "weekly",
            "priority": "1.0",
        }
    ]
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in excluded:
            continue
        if relative in {row["source"].lstrip("/") for row in []}:
            continue
        if relative in {"blog.html", "articles.html"}:
            changefreq, priority = "weekly", "0.9"
        elif relative in {
            "salla-store-design.html",
            "zid-store-design.html",
            "search-engine-optimization.html",
            "store-verification.html",
            "secure-payments.html",
        }:
            changefreq, priority = "monthly", "0.9"
        elif relative.startswith("articles/"):
            changefreq, priority = "monthly", "0.7"
        else:
            changefreq, priority = "monthly", "0.8"
        rows.append(
            {
                "path": f"/{relative}",
                "url": canonical_url(relative),
                "lastmod": git_lastmod(path),
                "changefreq": changefreq,
                "priority": priority,
            }
        )
    return rows


def write_sitemap(rows: list[dict[str, str]]) -> None:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for row in rows:
        parts.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(row['url'])}</loc>",
                f"    <lastmod>{row['lastmod']}</lastmod>",
                f"    <changefreq>{row['changefreq']}</changefreq>",
                f"    <priority>{row['priority']}</priority>",
                "  </url>",
            ]
        )
    parts.append("</urlset>")
    write_text(ROOT / "sitemap.xml", "\n".join(parts) + "\n")


def write_robots() -> None:
    content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /_new_testi.html

Sitemap: https://www.ezhalhe-sa.com/sitemap.xml
"""
    write_text(ROOT / "robots.txt", content)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    legacy_rows = extract_legacy_links()
    redirects = build_redirects(legacy_rows)
    update_vercel(redirects)
    update_firebase(redirects)
    canonical_rows = update_canonicals()
    apply_noindex(ROOT / "404.html")
    sitemap_rows = sitemap_pages()
    write_sitemap(sitemap_rows)
    write_robots()

    write_csv(
        REPORT_DIR / "redirect-map.csv",
        redirects,
        ["source", "destination", "status", "reason", "evidence"],
    )
    write_csv(
        REPORT_DIR / "legacy-blog-link-map.csv",
        legacy_rows,
        ["source", "anchor_text", "destination", "internal_link_destination", "reason"],
    )
    write_csv(
        REPORT_DIR / "canonical-map.csv",
        canonical_rows,
        ["file", "previous_canonical", "canonical", "action"],
    )
    write_csv(
        REPORT_DIR / "sitemap-inventory.csv",
        sitemap_rows,
        ["path", "url", "lastmod", "changefreq", "priority"],
    )
    manifest = {
        "generated_at": date.today().isoformat(),
        "canonical_origin": CANONICAL_ORIGIN,
        "legacy_blog_links_repaired": len(legacy_rows),
        "permanent_path_redirects": len(redirects),
        "host_redirect_rules": 1,
        "canonical_pages": len(canonical_rows),
        "sitemap_urls": len(sitemap_rows),
        "production_modified": False,
    }
    write_text(
        REPORT_DIR / "implementation-manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
