#!/usr/bin/env python3
"""Normalize social metadata and valid JSON-LD for every indexable page."""

from __future__ import annotations

import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.ezhalhe-sa.com"
SITE_NAME = "إزهلها"
SOCIAL_IMAGE = f"{ORIGIN}/images/og-cover.webp"
LOGO = f"{ORIGIN}/images/logo.webp"
TODAY = date.today().isoformat()
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "04-metadata-structured-data"

EXCLUDED = {
    "404.html",
    "_new_testi.html",
    "data-analysis.html",
    "google387142411d334808.html",
}
COLLECTION_PAGES = {"blog.html", "articles.html"}
SERVICE_PAGES = {
    "brand-building.html",
    "competitor-analysis.html",
    "digital-ads.html",
    "product-marketing.html",
    "salla-store-design.html",
    "salla-store-design-dammam.html",
    "salla-store-design-jeddah.html",
    "salla-store-design-makkah.html",
    "salla-store-design-riyadh.html",
    "search-engine-optimization.html",
    "secure-payments.html",
    "store-verification.html",
    "zid-store-design.html",
}

TITLE_OVERRIDES = {
    "index.html": "تصميم متجر سلة وزد | إنشاء متجر إلكتروني احترافي — إزهلها",
    "salla-store-design-dammam.html": "تصميم متجر سلة في الدمام | إزهلها",
    "salla-store-design-makkah.html": "تصميم متجر سلة في مكة | إزهلها",
    "salla-store-design-riyadh.html": "تصميم متجر سلة في الرياض | إزهلها",
    "articles/أهمية-تتبع-التحويلات-في-الحملات-الإعلانية-قياس-العائد-على-الاستثمار-roi.html": "تتبع التحويلات وقياس ROI للحملات الإعلانية | إزهلها",
    "articles/استخدام-linktree-أو-بدائله-لتحسين-الروابط-في-حسابات-التواصل-الاجتماعي.html": "استخدام Linktree وبدائله للمتاجر الإلكترونية | إزهلها",
    "articles/استراتيجيات-إدارة-حسابات-التواصل-الاجتماعي-لمتجرك-زيادة-التفاعل-والمبيعات.html": "إدارة حسابات التواصل للمتاجر وزيادة المبيعات | إزهلها",
    "articles/الخدمات-المصرفية-الرقمية-المتاحة-لأصحاب-المتاجر-في-الراجحي-والإنماء.html": "الخدمات المصرفية الرقمية للمتاجر | إزهلها",
    "articles/الخطوات-التفصيلية-لربط-خدمة-تمارا-بمتجرك-الإلكتروني-على-سلة-أو-زد.html": "ربط تمارا بمتجر سلة أو زد خطوة بخطوة | إزهلها",
    "articles/الدليل-الشامل-لإعداد-وربط-البكسلات-التحويلية-فيسبوك-سناب-شات-تيك-توك.html": "ربط بكسلات فيسبوك وسناب وتيك توك بالمتجر | إزهلها",
    "articles/الوثائق-المطلوبة-لفتح-حساب-بنكي-للأعمال-في-المملكة-العربية-السعودية.html": "وثائق فتح حساب بنكي للأعمال في السعودية | إزهلها",
    "articles/بناء-مجتمع-حول-متجرك-الإلكتروني-عبر-استراتيجيات-التواصل-الاجتماعي.html": "بناء مجتمع حول متجرك عبر التواصل الاجتماعي | إزهلها",
    "articles/تحليل-أداء-المتجر-وحسابات-التواصل-الاجتماعي-مؤشرات-الأداء-الرئيسية-kpis.html": "تحليل أداء المتجر ومؤشرات KPIs الأساسية | إزهلها",
    "articles/تصميم-متجر-إلكتروني-متوافق-مع-الجوال-mobile-first-design-على-زد.html": "تصميم متجر زد متوافق مع الجوال Mobile First | إزهلها",
}

DESCRIPTION_OVERRIDES = {
    "articles.html": "تصفح أدلة إزهلها العملية لأصحاب المتاجر السعودية حول تصميم متاجر سلة وزد، التوثيق، الدفع، التسويق، السيو وإدارة المتجر.",
    "blog.html": "مكتبة إزهلها لأصحاب المتاجر في السعودية: أدلة عملية عن تصميم المتاجر، سلة وزد، تحسين الظهور، التوثيق، الدفع والتسويق.",
    "brand-building.html": "خدمة بناء هوية وعلامة تجارية متناسقة لمتجرك الإلكتروني في السعودية، من الرسالة البصرية حتى تطبيق الهوية داخل متجر سلة أو زد.",
    "competitor-analysis.html": "تحليل عملي لمنافسي متجرك الإلكتروني في السعودية يشمل تجربة المستخدم، الأسعار، المحتوى والظهور في البحث لتحديد فرص التميز.",
    "digital-ads.html": "إعداد وتتبع حملات إعلانية لمتجرك الإلكتروني على المنصات المناسبة في السعودية، مع ربط البكسلات وقياس التحويلات وتحسين النتائج.",
    "product-marketing.html": "تسويق منتجات متجرك الإلكتروني بمحتوى وصفحات وعروض تدعم قرار الشراء وتناسب سلوك العملاء في السوق السعودي.",
    "secure-payments.html": "ربط وتفعيل حلول الدفع الآمنة لمتاجر سلة وزد في السعودية، بما يشمل مدى وApple Pay والبطاقات وتابي وتمارا حسب أهلية المتجر.",
    "store-verification.html": "مساعدة أصحاب المتاجر السعودية في تجهيز متطلبات التوثيق وربط الدومين والبيانات التجارية لمنصتي سلة وزد بخطوات واضحة.",
    "index.html": "إزهلها وكالة سعودية لتصميم وتطوير متاجر سلة وزد وووكومرس، مع باقات تشمل الهوية والسيو وربط الدفع والتحليلات وإطلاق المتجر.",
    "discount-salla-plus.html": "تعرف على طريقة استخدام كود خصم باقة سلة بلس، شروط الاستفادة، خطوات التفعيل والفرق بينها وبين الباقات الأخرى قبل الاشتراك.",
    "discount-salla-pro.html": "دليل استخدام كود خصم باقة سلة برو مع توضيح المميزات وخطوات التفعيل وأهم الشروط التي يحتاجها صاحب المتجر قبل الترقية.",
    "articles/أهمية-تتبع-التحويلات-في-الحملات-الإعلانية-قياس-العائد-على-الاستثمار-roi.html": "تعرف على إعداد تتبع التحويلات وقراءة العائد على الاستثمار للحملات الإعلانية، وربط النتائج بالمبيعات الفعلية في متجرك الإلكتروني.",
    "articles/استخدام-linktree-أو-بدائله-لتحسين-الروابط-في-حسابات-التواصل-الاجتماعي.html": "دليل اختيار Linktree أو بديل مناسب لتنظيم روابط متجرك وحساباتك، وتحسين وصول العملاء إلى المنتجات ووسائل التواصل والطلب.",
    "articles/استراتيجيات-إدارة-حسابات-التواصل-الاجتماعي-لمتجرك-زيادة-التفاعل-والمبيعات.html": "استراتيجيات عملية لإدارة حسابات متجر إلكتروني، تنظيم المحتوى، رفع التفاعل وتحويل المتابعين إلى زيارات ومبيعات قابلة للقياس.",
    "articles/الدليل-الشامل-لإعداد-وربط-البكسلات-التحويلية-فيسبوك-سناب-شات-تيك-توك.html": "خطوات إعداد وربط بكسلات فيسبوك وسناب شات وتيك توك بمتجرك، واختبار الأحداث الأساسية لتحسين الاستهداف وقياس التحويلات.",
    "articles/تحليل-أداء-المتجر-وحسابات-التواصل-الاجتماعي-مؤشرات-الأداء-الرئيسية-kpis.html": "تعرف على أهم مؤشرات أداء المتجر وحسابات التواصل، وكيف تقرأ الزيارات والتحويل ومتوسط الطلب والتفاعل لاتخاذ قرارات أفضل.",
}

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESCRIPTION_RE = re.compile(
    r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\']([^"\']*)',
    re.I,
)
CANONICAL_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']+)',
    re.I,
)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
SOCIAL_META_RE = re.compile(
    r"\s*<meta\b(?:(?=[^>]*\bproperty=[\"']og:)|(?=[^>]*\bname=[\"']twitter:))[^>]*>\s*",
    re.I,
)
AUTHOR_META_RE = re.compile(
    r"\s*<meta\b(?=[^>]*\bname=[\"']author[\"'])[^>]*>\s*", re.I
)
JSONLD_RE = re.compile(
    r"\s*<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>.*?</script>\s*",
    re.I | re.S,
)
FAQ_COMMENT_RE = re.compile(r"\s*<!--[^>]*FAQPage[^>]*-->\s*", re.I)
CANONICAL_TAG_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', re.I
)
HTML_TAG_RE = re.compile(r"<[^>]+>")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(HTML_TAG_RE.sub(" ", value))).strip()


def page_url(relative: str) -> str:
    return f"{ORIGIN}/" if relative == "index.html" else f"{ORIGIN}/{relative}"


def earliest_git_date(path: Path) -> str:
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%cs", "--", path.relative_to(ROOT).as_posix()],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    dates = [value for value in result.stdout.splitlines() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)]
    return dates[-1] if dates else TODAY


def organization() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{ORIGIN}/#organization",
        "name": SITE_NAME,
        "alternateName": "Ezhalha",
        "url": f"{ORIGIN}/",
        "logo": {
            "@type": "ImageObject",
            "url": LOGO,
            "width": 1024,
            "height": 1024,
        },
        "image": {"@id": f"{ORIGIN}/#socialimage"},
        "description": "وكالة سعودية متخصصة في تصميم وتطوير وتهيئة متاجر سلة وزد وووكومرس.",
        "areaServed": {"@type": "Country", "name": "المملكة العربية السعودية"},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+966501940155",
            "contactType": "sales",
            "areaServed": "SA",
            "availableLanguage": "Arabic",
        },
    }


def website() -> dict:
    return {
        "@type": "WebSite",
        "@id": f"{ORIGIN}/#website",
        "url": f"{ORIGIN}/",
        "name": SITE_NAME,
        "publisher": {"@id": f"{ORIGIN}/#organization"},
        "inLanguage": "ar-SA",
    }


def image_object() -> dict:
    return {
        "@type": "ImageObject",
        "@id": f"{ORIGIN}/#socialimage",
        "url": SOCIAL_IMAGE,
        "contentUrl": SOCIAL_IMAGE,
        "width": 1200,
        "height": 630,
        "caption": "إزهلها لتصميم وتطوير المتاجر الإلكترونية في السعودية",
    }


def breadcrumbs(relative: str, title: str) -> dict | None:
    if relative == "index.html":
        return None
    items = [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{ORIGIN}/"}
    ]
    if relative.startswith("articles/"):
        items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": "المقالات",
                "item": f"{ORIGIN}/articles.html",
            }
        )
    elif relative.startswith("salla-store-design-"):
        items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": "تصميم متجر سلة",
                "item": f"{ORIGIN}/salla-store-design.html",
            }
        )
    items.append(
        {
            "@type": "ListItem",
            "position": len(items) + 1,
            "name": title,
            "item": page_url(relative),
        }
    )
    return {
        "@type": "BreadcrumbList",
        "@id": f"{page_url(relative)}#breadcrumb",
        "itemListElement": items,
    }


def service_name(relative: str, h1: str) -> str:
    names = {
        "brand-building.html": "بناء الهوية والعلامة التجارية للمتاجر الإلكترونية",
        "competitor-analysis.html": "تحليل منافسي المتاجر الإلكترونية",
        "digital-ads.html": "إعداد وإدارة الإعلانات الرقمية للمتاجر الإلكترونية",
        "product-marketing.html": "تسويق منتجات المتاجر الإلكترونية",
        "search-engine-optimization.html": "تهيئة متاجر سلة وزد لمحركات البحث",
        "secure-payments.html": "ربط وتفعيل حلول الدفع الآمنة للمتاجر الإلكترونية",
        "store-verification.html": "توثيق المتاجر الإلكترونية في السعودية",
    }
    return names.get(relative, h1)


def city_from_filename(relative: str) -> str | None:
    for slug, city in {
        "riyadh": "الرياض",
        "jeddah": "جدة",
        "makkah": "مكة المكرمة",
        "dammam": "الدمام",
    }.items():
        if slug in relative:
            return city
    return None


def service_schema(relative: str, title: str, description: str, h1: str) -> dict:
    city = city_from_filename(relative)
    area_served = (
        {"@type": "City", "name": city}
        if city
        else {"@type": "Country", "name": "المملكة العربية السعودية"}
    )
    schema = {
        "@type": "Service",
        "@id": f"{page_url(relative)}#service",
        "name": service_name(relative, h1),
        "description": description,
        "url": page_url(relative),
        "provider": {"@id": f"{ORIGIN}/#organization"},
        "areaServed": area_served,
        "serviceType": title,
    }
    if relative in {"salla-store-design.html", "zid-store-design.html"}:
        schema["offers"] = [
            {
                "@type": "Offer",
                "name": "باقة بلس",
                "price": "1099",
                "priceCurrency": "SAR",
                "availability": "https://schema.org/InStock",
                "url": f"{page_url(relative)}#packages",
            },
            {
                "@type": "Offer",
                "name": "الباقة الاحترافية",
                "price": "1490",
                "priceCurrency": "SAR",
                "availability": "https://schema.org/InStock",
                "url": f"{page_url(relative)}#packages",
            },
            {
                "@type": "Offer",
                "name": "الباقة الذهبية برو",
                "price": "1980",
                "priceCurrency": "SAR",
                "availability": "https://schema.org/InStock",
                "url": f"{page_url(relative)}#packages",
            },
        ]
    return schema


def package_products() -> dict:
    products = []
    for position, (name, price) in enumerate(
        (("باقة بلس", "1099"), ("الباقة الاحترافية", "1490"), ("الباقة الذهبية برو", "1980")),
        start=1,
    ):
        products.append(
            {
                "@type": "ListItem",
                "position": position,
                "item": {
                    "@type": "Product",
                    "name": f"{name} لتصميم متجر إلكتروني",
                    "brand": {"@id": f"{ORIGIN}/#organization"},
                    "category": "خدمات تصميم المتاجر الإلكترونية",
                    "url": f"{ORIGIN}/#packages",
                    "offers": {
                        "@type": "Offer",
                        "price": price,
                        "priceCurrency": "SAR",
                        "availability": "https://schema.org/InStock",
                        "url": f"{ORIGIN}/#packages",
                    },
                },
            }
        )
    return {
        "@type": "ItemList",
        "@id": f"{ORIGIN}/#packages-list",
        "name": "باقات تصميم المتاجر الإلكترونية",
        "itemListElement": products,
    }


def graph_for(path: Path, title: str, description: str, h1: str) -> dict:
    relative = path.relative_to(ROOT).as_posix()
    url = page_url(relative)
    graph: list[dict] = [organization(), website(), image_object()]
    page_type = "CollectionPage" if relative in COLLECTION_PAGES else "WebPage"
    web_page = {
        "@type": page_type,
        "@id": f"{url}#webpage",
        "url": url,
        "name": title,
        "description": description,
        "isPartOf": {"@id": f"{ORIGIN}/#website"},
        "about": {"@id": f"{ORIGIN}/#organization"},
        "primaryImageOfPage": {"@id": f"{ORIGIN}/#socialimage"},
        "inLanguage": "ar-SA",
    }
    breadcrumb = breadcrumbs(relative, h1 or title)
    if breadcrumb:
        web_page["breadcrumb"] = {"@id": breadcrumb["@id"]}
    graph.append(web_page)
    if breadcrumb:
        graph.append(breadcrumb)

    if relative.startswith("articles/"):
        graph.append(
            {
                "@type": "Article",
                "@id": f"{url}#article",
                "headline": h1 or title,
                "description": description,
                "mainEntityOfPage": {"@id": f"{url}#webpage"},
                "image": {"@id": f"{ORIGIN}/#socialimage"},
                "datePublished": earliest_git_date(path),
                "dateModified": TODAY,
                "author": {
                    "@type": "Organization",
                    "name": "فريق إزهلها",
                    "url": f"{ORIGIN}/#about",
                },
                "publisher": {"@id": f"{ORIGIN}/#organization"},
                "inLanguage": "ar-SA",
            }
        )
    elif relative in SERVICE_PAGES:
        graph.append(service_schema(relative, title, description, h1))
    elif relative == "index.html":
        graph.append(
            {
                "@type": "Service",
                "@id": f"{ORIGIN}/#store-design-service",
                "name": "تصميم وتطوير المتاجر الإلكترونية",
                "description": description,
                "provider": {"@id": f"{ORIGIN}/#organization"},
                "areaServed": {"@type": "Country", "name": "المملكة العربية السعودية"},
                "serviceType": ["تصميم متجر سلة", "تصميم متجر زد", "تهيئة المتاجر لمحركات البحث"],
            }
        )
        graph.append(package_products())
    return {"@context": "https://schema.org", "@graph": graph}


def social_block(title: str, description: str, url: str, article: bool) -> str:
    values = [
        ("property", "og:locale", "ar_SA"),
        ("property", "og:type", "article" if article else "website"),
        ("property", "og:site_name", SITE_NAME),
        ("property", "og:title", title),
        ("property", "og:description", description),
        ("property", "og:url", url),
        ("property", "og:image", SOCIAL_IMAGE),
        ("property", "og:image:width", "1200"),
        ("property", "og:image:height", "630"),
        ("property", "og:image:alt", "إزهلها لتصميم وتطوير المتاجر الإلكترونية"),
        ("name", "twitter:card", "summary_large_image"),
        ("name", "twitter:title", title),
        ("name", "twitter:description", description),
        ("name", "twitter:image", SOCIAL_IMAGE),
        ("name", "twitter:image:alt", "إزهلها لتصميم وتطوير المتاجر الإلكترونية"),
    ]
    lines = [
        f'<meta {attribute}="{name}" content="{html.escape(value, quote=True)}">'
        for attribute, name, value in values
    ]
    if article:
        lines.append('<meta name="author" content="فريق إزهلها">')
    return "\n    ".join(lines)


def update_html_attributes(content: str) -> str:
    match = re.search(r"<html\b([^>]*)>", content, re.I)
    if not match:
        raise RuntimeError("Missing html element")
    attributes = match.group(1)
    attributes = re.sub(r"\s+lang=[\"'][^\"']*[\"']", "", attributes, flags=re.I)
    attributes = re.sub(r"\s+dir=[\"'][^\"']*[\"']", "", attributes, flags=re.I)
    replacement = f'<html lang="ar-SA" dir="rtl"{attributes}>'
    return content[: match.start()] + replacement + content[match.end() :]


def update_page(path: Path) -> dict[str, str]:
    relative = path.relative_to(ROOT).as_posix()
    content = path.read_text(encoding="utf-8")
    title_match = TITLE_RE.search(content)
    description_match = DESCRIPTION_RE.search(content)
    canonical_match = CANONICAL_RE.search(content)
    if not title_match or not description_match or not canonical_match:
        raise RuntimeError(f"Required metadata missing in {relative}")
    title = TITLE_OVERRIDES.get(relative, clean_text(title_match.group(1)))
    description = DESCRIPTION_OVERRIDES.get(relative, clean_text(description_match.group(1)))
    canonical = canonical_match.group(1)
    h1_match = H1_RE.search(content)
    h1 = clean_text(h1_match.group(1)) if h1_match else title
    article = relative.startswith("articles/")

    content = update_html_attributes(content)
    content = TITLE_RE.sub(f"<title>{html.escape(title)}</title>", content, count=1)
    description_tag = f'<meta name="description" content="{html.escape(description, quote=True)}">'
    content = re.sub(
        r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*>',
        description_tag,
        content,
        count=1,
        flags=re.I,
    )
    content = SOCIAL_META_RE.sub("\n", content)
    content = AUTHOR_META_RE.sub("\n", content)
    content = JSONLD_RE.sub("\n", content)
    content = FAQ_COMMENT_RE.sub("\n", content)
    block = social_block(title, description, canonical, article)
    canonical_tag = CANONICAL_TAG_RE.search(content)
    if not canonical_tag:
        raise RuntimeError(f"Canonical tag missing after cleanup: {relative}")
    insert_at = canonical_tag.end()
    content = content[:insert_at] + f"\n    {block}" + content[insert_at:]
    schema = graph_for(path, title, description, h1)
    schema_text = json.dumps(schema, ensure_ascii=False, indent=2).replace("</", "<\\/")
    content = content.replace(
        "</head>", f'    <script type="application/ld+json">\n{schema_text}\n    </script>\n</head>', 1
    )
    path.write_text(content, encoding="utf-8", newline="")
    schema_types = sorted(
        {
            item.get("@type", "")
            for item in schema["@graph"]
            if isinstance(item, dict) and item.get("@type")
        }
    )
    return {
        "file": relative,
        "url": canonical,
        "title": title,
        "title_length": str(len(title)),
        "description_length": str(len(description)),
        "og_type": "article" if article else "website",
        "schema_types": "|".join(schema_types),
        "author": "فريق إزهلها" if article else "إزهلها",
    }


def main() -> None:
    rows = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED:
            continue
        rows.append(update_page(path))
    if len(rows) != 119:
        raise RuntimeError(f"Expected 119 indexable pages, updated {len(rows)}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    import csv

    with (REPORT_DIR / "metadata-schema-map.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "pages_updated": len(rows),
        "faqpage_remaining": 0,
        "canonical_origin": ORIGIN,
        "social_image": SOCIAL_IMAGE,
        "hreflang": "not_applicable_single_arabic_site",
        "localbusiness": "not_asserted_without_verified_public_office",
    }
    (REPORT_DIR / "implementation-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
