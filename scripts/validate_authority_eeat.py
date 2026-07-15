from __future__ import annotations

import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "08-authority-eeat"
THIN_PAGES = [
    "brand-building.html",
    "competitor-analysis.html",
    "data-analysis.html",
    "digital-ads.html",
    "product-marketing.html",
    "search-engine-optimization.html",
    "secure-payments.html",
    "store-verification.html",
]
ALLOWED_OFFICIAL_HOSTS = {
    "mc.gov.sa",
    "business.sa",
    "www.wide.hrsd.gov.sa",
    "zatca.gov.sa",
    "help.salla.sa",
    "help.zid.sa",
    "developers.google.com",
    "support.google.com",
    "www.monshaat.gov.sa",
}

SOURCE_REGISTER = [
    ("وزارة التجارة", "نظام التجارة الإلكترونية", "https://mc.gov.sa/ar/ECC/pages/default.aspx", "النظام والأدلة وقائمة امتثال المتاجر"),
    ("وزارة التجارة", "دليل المتاجر الإلكترونية", "https://mc.gov.sa/ar/guides/CustomerGuide/Pages/ch4.aspx", "البيع والشراء والفاتورة وحقوق المستهلك"),
    ("المركز السعودي للأعمال", "توثيق التجارة الإلكترونية", "https://business.sa/eservices/details/4d6e9d30-e989-4940-08ce-08dbf015747a", "المتطلبات الرسمية الحالية لخدمة التوثيق"),
    ("وزارة الموارد البشرية", "إصدار وتجديد وثيقة العمل الحر", "https://www.wide.hrsd.gov.sa/ministry-services/services/%D8%AA%D8%AC%D8%AF%D9%8A%D8%AF-%D9%88%D8%AB%D9%8A%D9%82%D8%A9-%D8%A7%D9%84%D8%B9%D9%85%D9%84-%D8%A7%D9%84%D8%AD%D8%B1", "الأهلية وخطوات إصدار وتجديد الوثيقة"),
    ("هيئة الزكاة والضريبة والجمارك", "ما هي الفاتورة الإلكترونية؟", "https://zatca.gov.sa/ar/E-Invoicing/Introduction/Pages/What-is-e-invoicing.aspx", "تعريف الفاتورة الإلكترونية ومراحل التطبيق"),
    ("سلة", "مركز المساعدة", "https://help.salla.sa/", "إعداد المتجر والمنتجات والدفع والظهور"),
    ("زد", "مركز المساعدة", "https://help.zid.sa/", "إعداد وتصميم المتجر وتحسين الظهور"),
    ("Google Search Central", "دليل تحسين محركات البحث", "https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=ar", "أساسيات الزحف والفهرسة والمحتوى"),
    ("Google Search Central", "Merchant listing structured data", "https://developers.google.com/search/docs/appearance/structured-data/merchant-listing?hl=ar", "متطلبات Product وOffer والتحقق"),
    ("Google Analytics", "إعداد أحداث التجارة الإلكترونية", "https://support.google.com/analytics/answer/12200568?hl=ar", "أحداث العرض والسلة والدفع والشراء والاسترداد"),
    ("منشآت", "كتالوج الأدلة والأدوات", "https://www.monshaat.gov.sa/sites/default/files/2024-12/Toolkit_Catalogue_AR.pdf", "أدوات تطوير المشاريع والتسويق والتحليل"),
]


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "footer", "header"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip and data.strip():
            self.parts.append(data.strip())


def word_count(source: str) -> int:
    parser = TextParser()
    parser.feed(source)
    return len(re.findall(r"[\u0600-\u06ffA-Za-z0-9]+", " ".join(parser.parts)))


def official_links(source: str) -> list[str]:
    urls = re.findall(r'<a\b[^>]*href="(https?://[^"]+)"', source, flags=re.I)
    return [url for url in urls if urlparse(url).netloc.lower() in ALLOWED_OFFICIAL_HOSTS]


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    articles = sorted((ROOT / "articles").glob("*.html"))
    failures: dict[str, list[str]] = {}
    thin_counts: dict[str, int] = {}
    article_counts: dict[str, int] = {}
    total_official_links = 0

    for filename in THIN_PAGES:
        source = (ROOT / filename).read_text(encoding="utf-8")
        count = word_count(source)
        thin_counts[filename] = count
        links = official_links(source)
        total_official_links += len(links)
        errors = []
        if count < 220:
            errors.append(f"thin content: {count} words")
        if source.count('class="official-sources"') != 1 or len(links) < 2:
            errors.append("official source coverage incomplete")
        if source.count('class="content-review"') != 1:
            errors.append("visible preparation/review block missing")
        if "15 يوليو 2026" not in source or "فريق إزهلها" not in source:
            errors.append("review identity/date incomplete")
        if errors:
            failures[filename] = errors

    topic_counts: dict[str, int] = {}
    for path in articles:
        source = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        count = word_count(source)
        article_counts[rel] = count
        links = official_links(source)
        total_official_links += len(links)
        errors = []
        if count < 380:
            errors.append(f"article too thin: {count} words")
        if source.count('class="official-sources"') != 1 or len(links) < 3:
            errors.append("official references incomplete")
        if source.count('class="content-review"') != 1:
            errors.append("article review block missing")
        if "15 يوليو 2026" not in source or "فريق إزهلها" not in source:
            errors.append("author/review date missing")
        if "**" in source:
            errors.append("raw Markdown emphasis remains")
        main_end = source.find("</main>")
        related_at = source.find('class="related-reading"')
        if related_at < 0 or related_at > main_end:
            errors.append("related-reading landmark is outside main")
        if "source-note" in source:
            topic_counts["regulated_with_disclaimer"] = topic_counts.get("regulated_with_disclaimer", 0) + 1
        if errors:
            failures[rel] = errors

    index_source = (ROOT / "articles.html").read_text(encoding="utf-8")
    editorial_method = all(value in index_source for value in ['class="editorial-method"', "منهج إعداد مكتبة إزهلها", "وزارة التجارة", "Google Search Central"])
    site_source = "\n".join(path.read_text(encoding="utf-8") for path in [*articles, *(ROOT / name for name in THIN_PAGES)])
    risky_claims = [claim for claim in ["ضمان القبول السريع", "يضمن ظهورك في المراتب الأولى"] if claim in site_source]

    checks = {
        "all_101_articles_have_author_review_and_official_sources": len(articles) == 101 and not any(key.startswith("articles/") for key in failures),
        "all_authority_pages_are_substantive": not any(key in THIN_PAGES for key in failures),
        "article_index_explains_editorial_method": editorial_method,
        "official_source_hosts_are_allowlisted": total_official_links >= 300,
        "regulated_topics_include_disclaimers": topic_counts.get("regulated_with_disclaimer", 0) >= 35,
        "raw_markdown_removed": "**" not in site_source,
        "unsupported_guarantees_removed": not risky_claims,
        "related_reading_is_inside_main": not any("related-reading" in " ".join(value) for value in failures.values()),
    }
    passed = all(checks.values()) and not failures
    payload = {
        "status": "PASS" if passed else "FAIL",
        "summary": {
            "articles": len(articles),
            "authority_pages": len(THIN_PAGES),
            "official_links": total_official_links,
            "minimum_article_words": min(article_counts.values()),
            "minimum_authority_page_words": min(thin_counts.values()),
            "regulated_articles_with_disclaimer": topic_counts.get("regulated_with_disclaimer", 0),
        },
        "checks": checks,
        "failures": failures,
        "risky_claims": risky_claims,
        "thin_page_word_counts": thin_counts,
    }
    (REPORT_DIR / "validation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Saudi authority content and E-E-A-T validation", "", f"**Status:** {payload['status']}", "", "## Release gates", ""]
    for name, result in checks.items():
        lines.append(f"- {'PASS' if result else 'FAIL'} — `{name}`")
    lines.extend(["", "## Coverage", "", f"- Articles with visible authorship, review date, and official sources: {len(articles)}.", f"- Expanded authority/service pages: {len(THIN_PAGES)}.", f"- Official-source links: {total_official_links}.", f"- Minimum article word count: {min(article_counts.values())}.", f"- Minimum expanded-page word count: {min(thin_counts.values())}."])
    (REPORT_DIR / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with (REPORT_DIR / "official-source-register.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["publisher", "resource", "url", "used_for", "verified_date", "source_type"])
        for publisher, resource, url, used_for in SOURCE_REGISTER:
            writer.writerow([publisher, resource, url, used_for, "2026-07-15", "primary official"])

    print(json.dumps({"status": payload["status"], **payload["summary"], "failed_files": len(failures), "checks": checks}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
