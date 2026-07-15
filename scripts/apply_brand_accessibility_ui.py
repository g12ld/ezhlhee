from __future__ import annotations

import colorsys
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_FILES = {"_new_testi.html", "google387142411d334808.html"}
BRAND = {
    "primary": "#15B5B0",
    "secondary": "#0D2224",
    "cta": "#3BBBC2",
    "background": "#FFFFFF",
    "text": "#555555",
}
ALLOWED_RGB = {
    (21, 181, 176): "#15B5B0",
    (13, 34, 36): "#0D2224",
    (59, 187, 194): "#3BBBC2",
    (255, 255, 255): "#FFFFFF",
    (85, 85, 85): "#555555",
}


def site_html_files() -> list[Path]:
    files = [path for path in ROOT.glob("*.html") if path.name not in EXCLUDED_FILES]
    files.extend((ROOT / "articles").glob("*.html"))
    return sorted(files)


def css_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.css")
        if not {"reports", "scratch", "node_modules"}.intersection(path.parts)
    )


def normalize_hex(match: re.Match[str]) -> str:
    raw = match.group(1)
    if len(raw) in {3, 4}:
        raw = "".join(char * 2 for char in raw)
    alpha = raw[6:] if len(raw) == 8 else ""
    red, green, blue = (int(raw[index:index + 2], 16) for index in (0, 2, 4))
    replacement = choose_brand_color(red, green, blue).lstrip("#")
    return f"#{replacement}{alpha.upper()}"


def choose_brand_color(red: int, green: int, blue: int) -> str:
    exact = ALLOWED_RGB.get((red, green, blue))
    if exact:
        return exact

    maximum = max(red, green, blue)
    minimum = min(red, green, blue)
    luminance = (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)
    saturation = 0 if maximum == 0 else (maximum - minimum) / maximum

    if luminance >= 218:
        return BRAND["background"]
    if luminance <= 72:
        return BRAND["secondary"]
    if saturation <= 0.18:
        return BRAND["text"]

    hue = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)[0] * 360
    if 160 <= hue <= 210:
        return BRAND["cta"] if luminance >= 150 else BRAND["primary"]
    return BRAND["cta"] if luminance >= 135 else BRAND["primary"]


def normalize_function_color(match: re.Match[str]) -> str:
    function = match.group(1).lower()
    values = [part.strip() for part in match.group(2).split(",")]
    if len(values) < 3 or any(not re.fullmatch(r"\d+(?:\.\d+)?", value) for value in values[:3]):
        return match.group(0)
    red, green, blue = (max(0, min(255, round(float(value)))) for value in values[:3])
    target = choose_brand_color(red, green, blue)
    target_rgb = tuple(int(target[index:index + 2], 16) for index in (1, 3, 5))
    if function == "rgba" and len(values) == 4:
        return f"rgba({target_rgb[0]},{target_rgb[1]},{target_rgb[2]},{values[3]})"
    return f"rgb({target_rgb[0]},{target_rgb[1]},{target_rgb[2]})"


def normalize_colors(source: str) -> str:
    source = re.sub(r"#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?![0-9a-fA-F])", normalize_hex, source)
    source = re.sub(r"\b(rgb|rgba)\(([^)]+)\)", normalize_function_color, source, flags=re.IGNORECASE)
    return source


def enforce_semantic_tokens(source: str) -> str:
    """Keep palette values exact while assigning accessible semantic roles."""
    replacements = {
        "pd": BRAND["secondary"],
        "ink": BRAND["secondary"],
        "ink2": BRAND["secondary"],
        "muted": BRAND["text"],
        "bg": BRAND["background"],
        "bg2": "rgba(21,181,176,.06)",
        "white": BRAND["background"],
    }
    for token, value in replacements.items():
        source = re.sub(
            rf"(--{re.escape(token)}\s*:\s*)[^;}}]+",
            rf"\g<1>{value}",
            source,
            flags=re.IGNORECASE,
        )
    return source


SHARED_ACCESSIBILITY_CSS = """
<style id="ez-accessibility-system">
.skip-link{position:fixed;inset-inline-start:16px;top:-80px;z-index:10000;background:#0D2224;color:#FFFFFF;padding:12px 18px;border-radius:8px;text-decoration:none;font-weight:800}
.skip-link:focus{top:16px}
:where(a,button,input,select,textarea,[tabindex]):focus-visible{outline:3px solid #3BBBC2;outline-offset:3px}
:where(button,[role="button"]){font:inherit}
[role="button"]{cursor:pointer}
.burger{border:0;background:#FFFFFF;color:#0D2224}
.ann-code{border:1px solid #15B5B0;font:inherit;cursor:pointer}
.ann-bar{background:#0D2224 !important;color:#FFFFFF !important}
.btn-primary,.nav-cta,.btn-copy-hero,.btn-consult,.nav-dd-badge{color:#0D2224 !important}
.btn-consult svg{fill:#0D2224 !important}
.hero h1 em,.hstat-n,.btn-outline{color:#0D2224 !important}
.simple-site-nav{display:flex;align-items:center;justify-content:center;gap:18px;flex-wrap:wrap;padding:14px 20px;background:#FFFFFF;border-bottom:1px solid rgba(21,181,176,.18)}
.simple-site-nav a{color:#0D2224;text-decoration:none;font-weight:700}
.visually-hidden{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
</style>
""".strip()


def add_shared_accessibility(source: str) -> str:
    if "id=\"ez-accessibility-system\"" in source:
        source = re.sub(
            r'<style id="ez-accessibility-system">.*?</style>',
            SHARED_ACCESSIBILITY_CSS,
            source,
            count=1,
            flags=re.DOTALL,
        )
    else:
        source = source.replace("</head>", f"{SHARED_ACCESSIBILITY_CSS}\n</head>", 1)
    if "class=\"skip-link\"" not in source:
        source = re.sub(
            r"(<body\b[^>]*>)",
            r'\1\n<a class="skip-link" href="#main-content">تجاوز إلى المحتوى الرئيسي</a>',
            source,
            count=1,
            flags=re.IGNORECASE,
        )

    if re.search(r"<main\b", source, flags=re.IGNORECASE):
        source = re.sub(
            r"<main\b(?![^>]*\bid=)([^>]*)>",
            r'<main id="main-content"\1>',
            source,
            count=1,
            flags=re.IGNORECASE,
        )
    elif re.search(r"</header>", source, flags=re.IGNORECASE) and re.search(r"<footer\b", source, flags=re.IGNORECASE):
        source = re.sub(r"</header>", '</header>\n<main id="main-content">', source, count=1, flags=re.IGNORECASE)
        source = re.sub(r"<footer\b", '</main>\n<footer', source, count=1, flags=re.IGNORECASE)
    else:
        source = re.sub(r"(<body\b[^>]*>.*?<a class=\"skip-link\"[^>]*>.*?</a>)", r'\1\n<main id="main-content">', source, count=1, flags=re.IGNORECASE | re.DOTALL)
        source = source.replace("</body>", "</main>\n</body>", 1)

    source = re.sub(
        r"<nav\b(?![^>]*\baria-label)([^>]*)>",
        r'<nav aria-label="التنقل الرئيسي"\1>',
        source,
        flags=re.IGNORECASE,
    )
    def secure_blank_link(match: re.Match[str]) -> str:
        opening = match.group(0)
        rel = re.search(r'\brel="([^"]*)"', opening, flags=re.IGNORECASE)
        if rel:
            tokens = rel.group(1).split()
            for token in ("noopener", "noreferrer"):
                if token not in tokens:
                    tokens.append(token)
            return opening[:rel.start(1)] + " ".join(tokens) + opening[rel.end(1):]
        return opening[:-1] + ' rel="noopener noreferrer">'

    source = re.sub(
        r'<a\b(?=[^>]*target="_blank")[^>]*>',
        secure_blank_link,
        source,
        flags=re.IGNORECASE,
    )
    source = re.sub(
        r'<div class="burger" onclick="toggleNav\(\)"(?: id="burg")?>\s*(<span></span><span></span><span></span>)\s*</div>',
        r'<button type="button" class="burger" id="burg" onclick="toggleNav()" aria-label="فتح القائمة" aria-controls="nav" aria-expanded="false">\1</button>',
        source,
        flags=re.IGNORECASE,
    )
    source = source.replace(
        "function toggleNav(){document.getElementById('nav').classList.toggle('mob-open')}",
        "function toggleNav(){const nav=document.getElementById('nav');const button=document.querySelector('.burger');const open=nav.classList.toggle('mob-open');button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?'إغلاق القائمة':'فتح القائمة');}",
    )
    if 'class="burger"' in source and 'id="ez-menu-accessibility"' not in source:
        menu_script = """
<script id="ez-menu-accessibility">
(()=>{const button=document.querySelector('.burger');const nav=document.getElementById('nav');if(!button||!nav)return;
const sync=()=>{const open=nav.classList.contains('mob-open')||nav.classList.contains('active');button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?'إغلاق القائمة':'فتح القائمة');};
button.addEventListener('click',()=>setTimeout(sync,0));
nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>setTimeout(sync,0)));
document.addEventListener('keydown',event=>{if(event.key==='Escape'){nav.classList.remove('mob-open','active');button.classList.remove('active');sync();button.focus();}});
})();
</script>
""".strip()
        source = source.replace("</body>", f"{menu_script}\n</body>", 1)
    return source


def enhance_homepage(source: str) -> str:
    source = source.replace('<a href="#" class="logo">', '<a href="/" class="logo" aria-label="إزهلها — الصفحة الرئيسية">')
    source = source.replace(
        '<span class="ann-code" onclick="copyAnnCode(this)" title="انقر للنسخ">F-SJA3KGL7</span>',
        '<button type="button" class="ann-code" onclick="copyAnnCode(this)" title="نسخ كود الخصم" aria-label="نسخ كود الخصم F-SJA3KGL7">F-SJA3KGL7</button>',
    )
    source = source.replace(
        '<div class="burger" onclick="toggleNav()" id="burg">\n      <span></span><span></span><span></span>\n    </div>',
        '<button type="button" class="burger" onclick="toggleNav()" id="burg" aria-label="فتح القائمة" aria-controls="nav" aria-expanded="false">\n      <span></span><span></span><span></span>\n    </button>',
    )
    source = source.replace('<nav id="nav">', '<nav id="nav" aria-label="التنقل الرئيسي">', 1)
    source = source.replace('<img id="lbImg" src="" alt="">', '<img id="lbImg" alt="معاينة تصميم متجر إلكتروني" width="1100" height="2200" loading="lazy" decoding="async">')
    platform_alts = {"salla": "سلة", "zid": "زد", "shopify": "Shopify", "wordpress": "WordPress"}
    for platform, alt in platform_alts.items():
        source = re.sub(
            rf'<div class="partner-chip"><img\s+src="images/{platform}\.webp".*?</div>',
            f'<div class="partner-chip"><img src="images/{platform}.webp" alt="{alt}" width="1000" height="1000" loading="lazy" decoding="async" srcset="images/responsive/{platform}-128.webp 128w, images/responsive/{platform}-256.webp 256w, images/{platform}.webp 1000w" sizes="72px"></div>',
            source,
            count=1,
        )
    source = source.replace('<a href="#professional" class="btn-primary">اطلب الباقة الاحترافية ←</a>', '<a href="#pro" class="btn-primary">اطلب الباقة الذهبية برو ←</a>')

    source = re.sub(
        r'<div class="adv-card" onclick="([^"]+)"',
        r'<div class="adv-card" role="button" tabindex="0" aria-label="اختيار الخدمة" onclick="\1"',
        source,
    )

    def interactive_card(match: re.Match[str]) -> str:
        opening = match.group(1)
        source_argument = match.group(2)
        title_argument = match.group(3)
        title = title_argument.strip("'")
        return f'<div{opening} role="button" tabindex="0" aria-label="عرض {title}" onclick="openLb({source_argument},{title_argument}'

    source = re.sub(
        r'<div((?![^>]*\brole=)[^>]*class="(?:work-card|mini-work-card)[^"]*"[^>]*) onclick="openLb\((\'[^\']+\'),(\'[^\']+\')',
        interactive_card,
        source,
    )

    source = source.replace(
        '<div id="lb" onclick="closeLb()">',
        '<div id="lb" role="dialog" aria-modal="true" aria-hidden="true" aria-labelledby="lbTitle" onclick="closeLb()">\n  <h2 id="lbTitle" class="visually-hidden">معاينة تصميم المتجر</h2>',
    )
    source = source.replace('<button class="lb-x" onclick="closeLb()">✕</button>', '<button type="button" class="lb-x" onclick="closeLb()" aria-label="إغلاق معاينة التصميم">✕</button>')
    source = source.replace('<div class="consult-popup" id="consultPopup">', '<div class="consult-popup" id="consultPopup" role="region" aria-label="خيارات التواصل" aria-hidden="true">')
    source = source.replace('<button class="cp-close" onclick="toggleConsult()">✕</button>', '<button type="button" class="cp-close" onclick="toggleConsult()" aria-label="إغلاق خيارات التواصل">✕</button>')

    source = source.replace(
        "function toggleNav(){document.getElementById('nav').classList.toggle('mob-open')}",
        "function toggleNav(){const nav=document.getElementById('nav');const button=document.getElementById('burg');const open=nav.classList.toggle('mob-open');button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?'إغلاق القائمة':'فتح القائمة');}",
    )
    source = source.replace(
        "  document.getElementById('consultPopup').classList.toggle('open',consultOpen);",
        "  const popup=document.getElementById('consultPopup');popup.classList.toggle('open',consultOpen);popup.setAttribute('aria-hidden',String(!consultOpen));",
    )
    source = re.sub(
        r"// Show popup on wa button long press or after 8s\s*setTimeout\(\(\)=>\{if\(!consultOpen\)document\.getElementById\('consultPopup'\)\.classList\.add\('open'\)\},8000\);",
        "// Consultation choices remain user-initiated; no timed interruption.",
        source,
    )
    if "let lastLightboxTrigger=null;" not in source:
        source = source.replace(
            "let consultOpen=false;",
            "let consultOpen=false;\nlet lastLightboxTrigger=null;",
        )
    source = source.replace(
        "function openLb(src,title,url){\n  document.getElementById('lbImg').src=src;",
        "function openLb(src,title,url){\n  lastLightboxTrigger=document.activeElement;\n  document.getElementById('lbImg').src=src;",
    )
    source = source.replace(
        "  document.getElementById('lb').classList.add('on');\n  document.body.style.overflow='hidden';",
        "  const dialog=document.getElementById('lb');dialog.classList.add('on');dialog.setAttribute('aria-hidden','false');\n  document.body.style.overflow='hidden';",
    )
    source = source.replace(
        "  document.querySelector('.lb-frame').scrollTop=0;\n}",
        "  document.querySelector('.lb-frame').scrollTop=0;\n  dialog.querySelector('.lb-x').focus();\n}",
        1,
    )
    source = source.replace(
        "  document.getElementById('lb').classList.remove('on');\n  document.body.style.overflow='';",
        "  const dialog=document.getElementById('lb');dialog.classList.remove('on');dialog.setAttribute('aria-hidden','true');\n  document.body.style.overflow='';\n  if(lastLightboxTrigger&&typeof lastLightboxTrigger.focus==='function')lastLightboxTrigger.focus();",
    )
    source = source.replace(
        "document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLb()});",
        "document.addEventListener('keydown',e=>{const dialog=document.getElementById('lb');if(e.key==='Escape'&&dialog.classList.contains('on'))closeLb();if(e.key==='Tab'&&dialog.classList.contains('on')){e.preventDefault();dialog.querySelector('.lb-x').focus();}});",
    )
    keyboard_script = """
document.addEventListener('keydown',function(event){
  const target=event.target.closest('[role="button"][onclick]');
  if(target&&(event.key==='Enter'||event.key===' ')){
    event.preventDefault();
    target.click();
  }
});
document.querySelectorAll('#nav a').forEach(link=>link.addEventListener('click',()=>{
  const nav=document.getElementById('nav');const button=document.getElementById('burg');
  nav.classList.remove('mob-open');button.setAttribute('aria-expanded','false');button.setAttribute('aria-label','فتح القائمة');
}));
""".strip()
    source = source.replace("/* ── HEADER SCROLL ── */", f"{keyboard_script}\n\n/* ── HEADER SCROLL ── */")
    return source


def enhance_blog_index(source: str) -> str:
    if 'class="simple-site-nav"' not in source:
        navigation = (
            '<nav class="simple-site-nav" aria-label="التنقل الرئيسي">'
            '<a href="/">الرئيسية</a>'
            '<a href="/salla-store-design.html">تصميم متجر سلة</a>'
            '<a href="/zid-store-design.html">تصميم متجر زد</a>'
            '<a href="/articles.html">مكتبة المقالات</a>'
            '</nav>'
        )
        source = re.sub(r'<header>\s*</header>', f'<header>{navigation}</header>', source, count=1)
    return source


def repair_card_arguments(source: str) -> str:
    """Repair the short-lived malformed card call produced by an early local transform."""
    pattern = re.compile(
        r'(?P<opening><div[^>]*aria-label="عرض (?P<title>[^"]+)"[^>]*onclick="openLb\(,\'(?P<url>[^\']*)\'\)"[^>]*>)'
        r'(?P<body>.*?<img\b[^>]*\bsrc="(?P<src>[^"]+)")',
        flags=re.DOTALL,
    )

    def restore(match: re.Match[str]) -> str:
        opening = match.group("opening")
        title = match.group("title")
        url = match.group("url")
        src = match.group("src")
        fixed = opening.replace(
            f'onclick="openLb(,\'{url}\')"',
            f'onclick="openLb(\'{src}\',\'{title}\',\'{url}\')"',
        )
        return fixed + match.group("body")

    return pattern.sub(restore, source)


def main() -> None:
    changed = 0
    for path in [*site_html_files(), *css_files()]:
        original = path.read_text(encoding="utf-8")
        updated = enforce_semantic_tokens(normalize_colors(original))
        if path.suffix == ".html":
            updated = add_shared_accessibility(updated)
            if path == ROOT / "index.html":
                updated = repair_card_arguments(updated)
                updated = enhance_homepage(updated)
            elif path == ROOT / "blog.html":
                updated = enhance_blog_index(updated)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} site files with exact-brand colors and accessibility improvements.")


if __name__ == "__main__":
    main()
