"""
add_canonical.py - adds canonical + OG + robots to all /articles/ files
Works on existing files without changing design or content
"""
import sys
import re
from pathlib import Path
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://ezhalhe-sa.com"
ARTICLES_DIR = Path("articles")

def get_canonical_url(filename: str) -> str:
    """Builds canonical URL with raw Arabic chars to match sitemap format."""
    return f"{BASE_URL}/articles/{filename}"

def get_og_url(filename: str) -> str:
    return get_canonical_url(filename)

def extract_title(html: str) -> str:
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""

def extract_description(html: str) -> str:
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.DOTALL | re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""

def has_tag(html: str, tag: str) -> bool:
    return tag.lower() in html.lower()

def process_file(file_path: Path) -> bool:
    try:
        html = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  FAIL read: {file_path.name} - {e}")
        return False

    filename = file_path.name
    canonical_url = get_canonical_url(filename)
    title = extract_title(html)
    description = extract_description(html)

    # skip if canonical already exists
    if has_tag(html, 'rel="canonical"') or has_tag(html, "rel='canonical'"):
        print(f"  SKIP (canonical exists): {filename}")
        return False

    # بناء الوسوم الجديدة
    new_tags = f"""    <link rel="canonical" href="{canonical_url}">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="ازهلها - تصميم متاجر سلة وزد">
    <meta property="og:locale" content="ar_SA">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">"""

    # أدخل الوسوم بعد أول <meta charset ...> أو بعد <meta viewport...>
    # نبحث عن </head> ونضيف قبلها كحل آمن
    if re.search(r'<meta\s+name=["\']viewport["\']', html, re.IGNORECASE):
        pattern = r'(<meta\s+name=["\']viewport["\'][^>]*>)'
        replacement = r'\1\n' + new_tags
        new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.IGNORECASE)
    elif '</head>' in html.lower():
        new_html = re.sub(r'</head>', new_tags + '\n</head>', html, count=1, flags=re.IGNORECASE)
        count = 1
    else:
        print(f"  FAIL no insert point: {filename}")
        return False

    if count == 0:
        print(f"  FAIL no match: {filename}")
        return False

    try:
        file_path.write_text(new_html, encoding="utf-8")
        print(f"  OK {filename}")
        return True
    except Exception as e:
        print(f"  FAIL write: {filename} - {e}")
        return False


def main():
    if not ARTICLES_DIR.is_dir():
        print(f"Directory not found: {ARTICLES_DIR}")
        return

    files = sorted(ARTICLES_DIR.glob("*.html"))
    print(f"Found {len(files)} articles\n")

    updated = skipped = failed = 0
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        already = has_tag(raw, 'rel="canonical"') or has_tag(raw, "rel='canonical'")
        result = process_file(f)
        if result is True:
            updated += 1
        elif already:
            skipped += 1
        else:
            failed += 1

    print(f"\n{'='*50}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")


if __name__ == "__main__":
    main()
