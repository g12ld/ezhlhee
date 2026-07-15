from __future__ import annotations

import colorsys
import re
import subprocess
import sys
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
INITIAL_TESTIMONIALS = 2
INITIAL_PORTFOLIO_ITEMS = 3
INITIAL_GOLD_PRO_WORKS = 3
INITIAL_ADDITIONAL_SERVICES = 6


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


def strip_trailing_whitespace(source: str) -> str:
    """Normalize generated markup without changing document line endings."""
    trailing_newline = "\n" if source.endswith("\n") else ""
    return "\n".join(line.rstrip() for line in source.splitlines()) + trailing_newline


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
.ann-code{border:1px solid #15B5B0;font:inherit;cursor:pointer;background:#FFFFFF!important;color:#0D2224!important;min-height:44px;padding-inline:12px}
.ann-close{min-width:44px;min-height:44px;color:#FFFFFF!important}
.ann-bar{background:#0D2224 !important;color:#FFFFFF !important}
.btn-primary,.nav-cta,.btn-copy-hero,.btn-consult,.nav-dd-badge{color:#0D2224 !important}
.btn-consult svg{fill:#0D2224 !important}
.hero h1 em,.hstat-n,.btn-outline{color:#0D2224 !important}
#testimonials .testi-head .sh span,#testimonials .testi-score{color:#0D2224!important}
.btn-submit{color:#0D2224!important}
footer .ft-col a,footer .ft-col a[style]{color:#FFFFFF!important}
footer .ft-copy{color:#FFFFFF!important}
footer .ft-col h3{font-size:.75rem;font-weight:800;color:#FFFFFF;text-transform:uppercase;letter-spacing:.8px;margin-bottom:16px}
#testimonials .testi-marquee{overflow-x:auto!important;scrollbar-width:thin;mask:none!important;-webkit-mask:none!important}
#testimonials .testi-track{animation:none!important;width:100%!important}
#testimonials .testi-track-set{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x proximity;padding:4px}
#testimonials .testi-card{scroll-snap-align:start}
.deferred-content-action{display:flex;justify-content:center;margin:24px auto 0;padding:0 20px}
.load-more-btn{min-height:48px;border:1px solid #15B5B0;border-radius:10px;background:#FFFFFF;color:#0D2224;padding:12px 24px;font-weight:800;cursor:pointer}
.load-more-btn:hover{background:rgba(21,181,176,.06)}
.consult-trigger{position:fixed;inset-inline-end:18px;bottom:100px;z-index:890;min-height:44px;border:1px solid #15B5B0;border-radius:50px;background:#FFFFFF;color:#0D2224;padding:10px 16px;font-weight:800;box-shadow:0 8px 24px rgba(13,34,36,.18);cursor:pointer}
.consult-trigger[aria-expanded="true"]{background:#15B5B0;color:#0D2224}
.cp-close{min-width:44px!important;min-height:44px!important}
.simple-site-nav{display:flex;align-items:center;justify-content:center;gap:18px;flex-wrap:wrap;padding:14px 20px;background:#FFFFFF;border-bottom:1px solid rgba(21,181,176,.18)}
.simple-site-nav a{color:#0D2224;text-decoration:none;font-weight:700}
.visually-hidden{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
@supports (content-visibility:auto){#work,#pro,#professional,#plus,#compare,#services,#testimonials,#articles,#faq,#contact,footer{content-visibility:auto;contain-intrinsic-size:auto 900px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
</style>
""".strip()


def add_shared_accessibility(source: str) -> str:
    source = re.sub(
        r'<meta\s+http-equiv=["\']X-Frame-Options["\'][^>]*>\s*',
        "",
        source,
        flags=re.IGNORECASE,
    )
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


def balanced_div_end(source: str, start: int) -> int:
    """Return the end of a div block that starts at ``start``."""
    depth = 0
    for match in re.finditer(r"<div\b[^>]*>|</div\s*>", source[start:], flags=re.IGNORECASE):
        token = match.group(0).lower()
        depth += -1 if token.startswith("</div") else 1
        if depth == 0:
            return start + match.end()
    raise ValueError(f"Unbalanced div starting at offset {start}")


def defer_testimonials(source: str) -> str:
    """Render priority reviews initially and retain the remainder in an on-demand template."""
    if 'id="moreTestimonials"' in source:
        first_start = source.find('<div class="testi-track-set">')
        first_end = balanced_div_end(source, first_start)
        first_open_end = source.find(">", first_start) + 1
        first_inner = source[first_open_end:first_end - len("</div>")]
        cards: list[tuple[int, int]] = []
        cursor = 0
        while True:
            card_start = first_inner.find('<div class="testi-card">', cursor)
            if card_start < 0:
                break
            card_end = balanced_div_end(first_inner, card_start)
            cards.append((card_start, card_end))
            cursor = card_end
        if len(cards) <= INITIAL_TESTIMONIALS:
            return source
        moved = "\n".join(first_inner[start:end].strip() for start, end in cards[INITIAL_TESTIMONIALS:])
        visible_inner = first_inner[:cards[INITIAL_TESTIMONIALS][0]] + first_inner[cards[-1][1]:]
        template_start = source.find('<template id="moreTestimonials">', first_end)
        template_open_end = source.find(">", template_start) + 1
        template_close = source.find("</template>", template_open_end)
        existing = source[template_open_end:template_close].strip()
        combined = "\n".join(part for part in (moved, existing) if part)
        return source[:first_open_end] + visible_inner + "</div>" + source[first_end:template_open_end] + "\n" + combined + "\n" + source[template_close:]

    track_start = source.find('<div class="testi-track">')
    first_start = source.find('<div class="testi-track-set">', track_start)
    duplicate_start = source.find('<div class="testi-track-set" aria-hidden="true">', first_start)
    if min(track_start, first_start, duplicate_start) < 0:
        return source

    track_end = balanced_div_end(source, track_start)
    first_end = balanced_div_end(source, first_start)
    duplicate_end = balanced_div_end(source, duplicate_start)
    first_open_end = source.find(">", first_start) + 1
    first_inner = source[first_open_end:first_end - len("</div>")]

    cards: list[tuple[int, int]] = []
    cursor = 0
    while True:
        card_start = first_inner.find('<div class="testi-card">', cursor)
        if card_start < 0:
            break
        card_end = balanced_div_end(first_inner, card_start)
        cards.append((card_start, card_end))
        cursor = card_end
    if len(cards) <= INITIAL_TESTIMONIALS:
        return source

    deferred = "\n".join(first_inner[start:end].strip() for start, end in cards[INITIAL_TESTIMONIALS:])
    trimmed_inner = first_inner[:cards[INITIAL_TESTIMONIALS][0]] + first_inner[cards[-1][1]:]
    first_block = source[first_start:first_open_end] + trimmed_inner + "</div>"
    outer_tail = source[duplicate_end:track_end]
    replacement = (
        source[track_start:first_start]
        + first_block
        + source[first_end:duplicate_start]
        + outer_tail
        + '\n<template id="moreTestimonials">\n'
        + deferred
        + '\n</template>\n'
        + '<div class="deferred-content-action"><button type="button" class="load-more-btn" '
          'id="loadMoreTestimonials" onclick="loadMoreTestimonials()">عرض جميع آراء العملاء</button></div>'
    )
    return source[:track_start] + replacement + source[track_end:]


def defer_portfolio(source: str) -> str:
    """Keep the priority portfolio visible and defer older cards until requested."""
    if 'id="morePortfolio"' in source:
        grid_start = source.find('<div class="work-grid" id="wGrid">')
        grid_end = balanced_div_end(source, grid_start)
        grid_open_end = source.find(">", grid_start) + 1
        grid_inner = source[grid_open_end:grid_end - len("</div>")]
        cards: list[tuple[int, int]] = []
        cursor = 0
        pattern = re.compile(r'<div class="work-card(?:\s|\")')
        while True:
            match = pattern.search(grid_inner, cursor)
            if not match:
                break
            card_start = match.start()
            card_end = balanced_div_end(grid_inner, card_start)
            cards.append((card_start, card_end))
            cursor = card_end
        if len(cards) <= INITIAL_PORTFOLIO_ITEMS:
            return source
        moved = "\n".join(grid_inner[start:end].strip() for start, end in cards[INITIAL_PORTFOLIO_ITEMS:])
        visible_inner = grid_inner
        for start, end in reversed(cards[INITIAL_PORTFOLIO_ITEMS:]):
            visible_inner = visible_inner[:start] + visible_inner[end:]
        template_start = source.find('<template id="morePortfolio">', grid_end)
        template_open_end = source.find(">", template_start) + 1
        template_close = source.find("</template>", template_open_end)
        existing = source[template_open_end:template_close].strip()
        combined = "\n".join(part for part in (moved, existing) if part)
        return source[:grid_open_end] + visible_inner + "</div>" + source[grid_end:template_open_end] + "\n" + combined + "\n" + source[template_close:]

    grid_start = source.find('<div class="work-grid" id="wGrid">')
    if grid_start < 0:
        return source
    grid_end = balanced_div_end(source, grid_start)
    grid_open_end = source.find(">", grid_start) + 1
    grid_inner = source[grid_open_end:grid_end - len("</div>")]

    cards: list[tuple[int, int]] = []
    cursor = 0
    card_pattern = re.compile(r'<div class="work-card(?:\s|\")')
    while True:
        match = card_pattern.search(grid_inner, cursor)
        if not match:
            break
        card_start = match.start()
        card_end = balanced_div_end(grid_inner, card_start)
        cards.append((card_start, card_end))
        cursor = card_end
    if len(cards) <= INITIAL_PORTFOLIO_ITEMS:
        return source

    deferred = "\n".join(grid_inner[start:end].strip() for start, end in cards[INITIAL_PORTFOLIO_ITEMS:])
    visible_inner = grid_inner
    for start, end in reversed(cards[INITIAL_PORTFOLIO_ITEMS:]):
        visible_inner = visible_inner[:start] + visible_inner[end:]
    replacement = (
        source[grid_start:grid_open_end]
        + visible_inner
        + "</div>"
        + '\n<template id="morePortfolio">\n'
        + deferred
        + '\n</template>\n'
        + '<div class="deferred-content-action"><button type="button" class="load-more-btn" '
          'id="loadMorePortfolio" onclick="loadMorePortfolio(true)">عرض جميع الأعمال السابقة</button></div>'
    )
    return source[:grid_start] + replacement + source[grid_end:]


def defer_gold_pro_works(source: str) -> str:
    """Keep the three newest Gold Pro stores visible and defer repeated older previews."""
    if 'id="moreGoldProWorks"' in source:
        return source
    section_start = source.find('<section class="pro-section sec" id="pro">')
    grid_start = source.find('<div class="pkg-works-grid">', section_start)
    if min(section_start, grid_start) < 0:
        return source
    grid_end = balanced_div_end(source, grid_start)
    grid_open_end = source.find(">", grid_start) + 1
    grid_inner = source[grid_open_end:grid_end - len("</div>")]
    cards: list[tuple[int, int]] = []
    cursor = 0
    while True:
        card_start = grid_inner.find('<div class="mini-work-card"', cursor)
        if card_start < 0:
            break
        card_end = balanced_div_end(grid_inner, card_start)
        cards.append((card_start, card_end))
        cursor = card_end
    if len(cards) <= INITIAL_GOLD_PRO_WORKS:
        return source
    deferred = "\n".join(grid_inner[start:end].strip() for start, end in cards[INITIAL_GOLD_PRO_WORKS:])
    visible_inner = grid_inner
    for start, end in reversed(cards[INITIAL_GOLD_PRO_WORKS:]):
        visible_inner = visible_inner[:start] + visible_inner[end:]
    replacement = (
        source[grid_start:grid_open_end]
        + visible_inner
        + "</div>"
        + '\n<template id="moreGoldProWorks">\n'
        + deferred
        + '\n</template>\n'
        + '<div class="deferred-content-action"><button type="button" class="load-more-btn" '
          'id="loadMoreGoldProWorks" onclick="loadMoreGoldProWorks()">عرض جميع أعمال الذهبية برو</button></div>'
    )
    return source[:grid_start] + replacement + source[grid_end:]


def defer_inactive_comparison_tabs(source: str) -> str:
    """Keep the selected mobile package in the DOM and hydrate other tabs on demand."""
    if 'id="comparisonTab0"' in source:
        return source
    tabs_start = source.find('<div class="ct-mobile-tabs reveal">')
    if tabs_start < 0:
        return source
    tabs_end = balanced_div_end(source, tabs_start)
    matches = list(re.finditer(r'<div class="ct-tab-content(?: active)?">', source[tabs_start:tabs_end]))
    if len(matches) != 3:
        return source
    replacements: list[tuple[int, int, str]] = []
    for index in (0, 2):
        start = tabs_start + matches[index].start()
        end = balanced_div_end(source, start)
        open_end = source.find(">", start) + 1
        inner = source[open_end:end - len("</div>")]
        replacements.append(
            (
                start,
                end,
                f'<div class="ct-tab-content" data-deferred-template="comparisonTab{index}"></div>'
                f'\n<template id="comparisonTab{index}">{inner}</template>',
            )
        )
    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    return source


def defer_additional_services(source: str) -> str:
    """Show the first service choices immediately and retain the complete catalog on demand."""
    if 'id="moreServices"' in source:
        return source
    section_start = source.find('<section class="srv-section sec" id="services">')
    grid_start = source.find('<div class="srv-grid"', section_start)
    if min(section_start, grid_start) < 0:
        return source
    grid_end = balanced_div_end(source, grid_start)
    grid_open_end = source.find(">", grid_start) + 1
    grid_inner = source[grid_open_end:grid_end - len("</div>")]
    cards: list[tuple[int, int]] = []
    cursor = 0
    while True:
        card_start = grid_inner.find('<div class="srv-card', cursor)
        if card_start < 0:
            break
        card_end = balanced_div_end(grid_inner, card_start)
        cards.append((card_start, card_end))
        cursor = card_end
    if len(cards) <= INITIAL_ADDITIONAL_SERVICES:
        return source
    deferred = "\n".join(grid_inner[start:end].strip() for start, end in cards[INITIAL_ADDITIONAL_SERVICES:])
    visible_inner = grid_inner
    for start, end in reversed(cards[INITIAL_ADDITIONAL_SERVICES:]):
        visible_inner = visible_inner[:start] + visible_inner[end:]
    replacement = (
        source[grid_start:grid_open_end]
        + visible_inner
        + "</div>"
        + '\n<template id="moreServices">\n'
        + deferred
        + '\n</template>\n'
        + '<div class="deferred-content-action"><button type="button" class="load-more-btn" '
          'id="loadMoreServices" onclick="loadMoreServices()">عرض جميع الخدمات الإضافية</button></div>'
    )
    return source[:grid_start] + replacement + source[grid_end:]


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
        '<div id="lb" role="dialog" aria-modal="true" aria-hidden="true" inert aria-labelledby="lbTitle" onclick="closeLb()">\n  <h2 id="lbTitle" class="visually-hidden">معاينة تصميم المتجر</h2>',
    )
    source = re.sub(
        r'(<div id="lb"[^>]*aria-hidden="true")(?![^>]*\binert)([^>]*>)',
        r'\1 inert\2',
        source,
        count=1,
    )
    source = source.replace('<button class="lb-x" onclick="closeLb()">✕</button>', '<button type="button" class="lb-x" onclick="closeLb()" aria-label="إغلاق معاينة التصميم">✕</button>')
    source = source.replace('<div class="consult-popup" id="consultPopup">', '<div class="consult-popup" id="consultPopup" role="region" aria-label="خيارات التواصل" aria-hidden="true" inert>')
    source = re.sub(
        r'(<div class="consult-popup"[^>]*aria-hidden="true")(?![^>]*\binert)([^>]*>)',
        r'\1 inert\2',
        source,
        count=1,
    )
    source = source.replace('<button class="cp-close" onclick="toggleConsult()">✕</button>', '<button type="button" class="cp-close" onclick="toggleConsult()" aria-label="إغلاق خيارات التواصل">✕</button>')
    if 'id="consultTrigger"' not in source:
        source = source.replace(
            '<!-- CONSULTATION POPUP -->',
            '<button type="button" class="consult-trigger" id="consultTrigger" onclick="toggleConsult()" aria-controls="consultPopup" aria-expanded="false">استشارة سريعة</button>\n\n<!-- CONSULTATION POPUP -->',
            1,
        )

    def repair_footer_headings(match: re.Match[str]) -> str:
        footer = match.group(0)
        return footer.replace("<h4>", "<h3>").replace("</h4>", "</h3>")

    source = re.sub(r"<footer\b.*?</footer>", repair_footer_headings, source, count=1, flags=re.DOTALL)
    source = re.sub(
        r'(<div class="mini-work-card"[^>]*>\s*<img\b[^>]*\balt=")(?!(?:معاينة واجهة))([^"\r\n]*)(")',
        r'\1معاينة واجهة \2\3',
        source,
    )

    source = source.replace(
        "function toggleNav(){document.getElementById('nav').classList.toggle('mob-open')}",
        "function toggleNav(){const nav=document.getElementById('nav');const button=document.getElementById('burg');const open=nav.classList.toggle('mob-open');button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?'إغلاق القائمة':'فتح القائمة');}",
    )
    source = source.replace(
        "  document.getElementById('consultPopup').classList.toggle('open',consultOpen);",
        "  const popup=document.getElementById('consultPopup');popup.classList.toggle('open',consultOpen);popup.setAttribute('aria-hidden',String(!consultOpen));popup.inert=!consultOpen;",
    )
    source = source.replace(
        "  const popup=document.getElementById('consultPopup');popup.classList.toggle('open',consultOpen);popup.setAttribute('aria-hidden',String(!consultOpen));",
        "  const popup=document.getElementById('consultPopup');popup.classList.toggle('open',consultOpen);popup.setAttribute('aria-hidden',String(!consultOpen));popup.inert=!consultOpen;",
    )
    source = source.replace(
        "  const popup=document.getElementById('consultPopup');popup.classList.toggle('open',consultOpen);popup.setAttribute('aria-hidden',String(!consultOpen));popup.inert=!consultOpen;",
        "  const popup=document.getElementById('consultPopup');const trigger=document.getElementById('consultTrigger');popup.classList.toggle('open',consultOpen);popup.setAttribute('aria-hidden',String(!consultOpen));popup.inert=!consultOpen;trigger.setAttribute('aria-expanded',String(consultOpen));",
    )
    source = source.replace(
        "    consultOpen=false;document.getElementById('consultPopup').classList.remove('open');",
        "    consultOpen=false;const popup=document.getElementById('consultPopup');popup.classList.remove('open');popup.setAttribute('aria-hidden','true');popup.inert=true;",
    )
    close_trigger_state = "document.getElementById('consultTrigger').setAttribute('aria-expanded','false');"
    source = re.sub(
        rf"(?:{re.escape(close_trigger_state)})+",
        close_trigger_state,
        source,
    )
    close_popup_state = "    consultOpen=false;const popup=document.getElementById('consultPopup');popup.classList.remove('open');popup.setAttribute('aria-hidden','true');popup.inert=true;"
    if close_popup_state + close_trigger_state not in source:
        source = source.replace(close_popup_state, close_popup_state + close_trigger_state)
    source = source.replace(
        "  if(consultOpen&&!document.getElementById('consultPopup').contains(event.target)){",
        "  if(consultOpen&&!document.getElementById('consultPopup').contains(event.target)&&!document.getElementById('consultTrigger').contains(event.target)){",
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
        "  const dialog=document.getElementById('lb');dialog.classList.add('on');dialog.setAttribute('aria-hidden','false');dialog.inert=false;\n  document.body.style.overflow='hidden';",
    )
    source = source.replace(
        "  const dialog=document.getElementById('lb');dialog.classList.add('on');dialog.setAttribute('aria-hidden','false');\n  document.body.style.overflow='hidden';",
        "  const dialog=document.getElementById('lb');dialog.classList.add('on');dialog.setAttribute('aria-hidden','false');dialog.inert=false;\n  document.body.style.overflow='hidden';",
    )
    source = source.replace(
        "  document.querySelector('.lb-frame').scrollTop=0;\n}",
        "  document.querySelector('.lb-frame').scrollTop=0;\n  dialog.querySelector('.lb-x').focus();\n}",
        1,
    )
    source = source.replace(
        "  document.getElementById('lb').classList.remove('on');\n  document.body.style.overflow='';",
        "  const dialog=document.getElementById('lb');dialog.classList.remove('on');dialog.setAttribute('aria-hidden','true');dialog.inert=true;\n  document.body.style.overflow='';\n  if(lastLightboxTrigger&&typeof lastLightboxTrigger.focus==='function')lastLightboxTrigger.focus();",
    )
    source = source.replace(
        "  const dialog=document.getElementById('lb');dialog.classList.remove('on');dialog.setAttribute('aria-hidden','true');\n  document.body.style.overflow='';",
        "  const dialog=document.getElementById('lb');dialog.classList.remove('on');dialog.setAttribute('aria-hidden','true');dialog.inert=true;\n  document.body.style.overflow='';",
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
    source = re.sub(re.escape(keyboard_script) + r"\s*", "", source)
    source = source.replace("/* ── HEADER SCROLL ── */", f"{keyboard_script}\n\n/* ── HEADER SCROLL ── */")
    if "function loadMoreTestimonials()" not in source:
        deferred_script = """
function loadMoreTestimonials(){
  const template=document.getElementById('moreTestimonials');
  const target=document.querySelector('#testimonials .testi-track-set');
  const button=document.getElementById('loadMoreTestimonials');
  if(template&&target){target.append(template.content.cloneNode(true));template.remove();}
  if(button)button.closest('.deferred-content-action').remove();
}
function loadMorePortfolio(moveFocus){
  const template=document.getElementById('morePortfolio');
  const target=document.getElementById('wGrid');
  const button=document.getElementById('loadMorePortfolio');
  if(template&&target){
    target.append(template.content.cloneNode(true));template.remove();
    initScrollPreviews();
    target.querySelectorAll('.reveal:not(.in)').forEach(card=>{card.classList.add('in');obs.observe(card);});
  }
  if(button)button.closest('.deferred-content-action').remove();
  if(moveFocus&&target){const firstDeferred=target.querySelectorAll('.work-card')[9];if(firstDeferred)firstDeferred.focus();}
}
""".strip()
        source = source.replace("/* ── FILTER ── */", f"{deferred_script}\n\n/* ── FILTER ── */")
    source = re.sub(
        r"if\(moveFocus&&target\)\{const firstDeferred=target\.querySelectorAll\('\.work-card'\)\[\d+\];if\(firstDeferred\)firstDeferred\.focus\(\);\}",
        f"if(moveFocus&&target){{const firstDeferred=target.querySelectorAll('.work-card')[{INITIAL_PORTFOLIO_ITEMS}];if(firstDeferred)firstDeferred.focus();}}",
        source,
    )
    if "function loadMoreGoldProWorks()" not in source:
        gold_works_script = """
function loadMoreGoldProWorks(){
  const template=document.getElementById('moreGoldProWorks');
  const target=document.querySelector('#pro .pkg-works-grid');
  const button=document.getElementById('loadMoreGoldProWorks');
  if(template&&target){
    target.append(template.content.cloneNode(true));template.remove();
    initScrollPreviews();
    target.querySelectorAll('.reveal:not(.in)').forEach(card=>{card.classList.add('in');obs.observe(card);});
  }
  if(button)button.closest('.deferred-content-action').remove();
}
""".strip()
        source = source.replace("/* ── FILTER ── */", f"{gold_works_script}\n\n/* ── FILTER ── */")
    if "function loadMoreServices()" not in source:
        services_script = """
function loadMoreServices(){
  const template=document.getElementById('moreServices');
  const target=document.querySelector('#services .srv-grid');
  const button=document.getElementById('loadMoreServices');
  if(template&&target){
    target.append(template.content.cloneNode(true));template.remove();
    target.querySelectorAll('.reveal:not(.in)').forEach(card=>{card.classList.add('in');obs.observe(card);});
  }
  if(button)button.closest('.deferred-content-action').remove();
}
""".strip()
        source = source.replace("/* ── FILTER ── */", f"{services_script}\n\n/* ── FILTER ── */")
    source = source.replace(
        "function filterWork(type,btn){\n  document.querySelectorAll('.wf-btn').forEach",
        "function filterWork(type,btn){\n  if(document.getElementById('morePortfolio'))loadMorePortfolio(false);\n  document.querySelectorAll('.wf-btn').forEach",
    )
    source = defer_testimonials(source)
    source = defer_portfolio(source)
    source = defer_gold_pro_works(source)
    source = defer_inactive_comparison_tabs(source)
    source = defer_additional_services(source)
    source = source.replace(
        """function switchTab(idx, btn){
  const tabs = document.querySelectorAll('.ct-tab-content');
  const btns = document.querySelectorAll('.ct-tab-btn');

  // Remove active from all
  tabs.forEach(t => t.classList.remove('active'));
  btns.forEach(b => b.classList.remove('active'));

  // Add active to current
  tabs[idx].classList.add('active');
  btn.classList.add('active');
}""",
        """function switchTab(idx, btn){
  const tabs=document.querySelectorAll('.ct-tab-content');
  const btns=document.querySelectorAll('.ct-tab-btn');
  const selected=tabs[idx];
  const templateId=selected.dataset.deferredTemplate;
  if(templateId){const template=document.getElementById(templateId);if(template){selected.append(template.content.cloneNode(true));template.remove();}delete selected.dataset.deferredTemplate;}
  tabs.forEach(tab=>tab.classList.remove('active'));
  btns.forEach(button=>button.classList.remove('active'));
  selected.classList.add('active');
  btn.classList.add('active');
}""",
    )
    comparison_mode_script = """
const comparisonMedia=window.matchMedia('(max-width:767px)');
const desktopComparison=document.querySelector('#compare .ct');
const mobileComparison=document.querySelector('#compare .ct-mobile-tabs');
const desktopComparisonMarker=document.createComment('desktop comparison');
const mobileComparisonMarker=document.createComment('mobile comparison');
const desktopComparisonStore=document.createDocumentFragment();
const mobileComparisonStore=document.createDocumentFragment();
desktopComparison.before(desktopComparisonMarker);
mobileComparison.before(mobileComparisonMarker);
function syncComparisonRepresentation(){
  if(comparisonMedia.matches){
    if(desktopComparison.isConnected)desktopComparisonStore.append(desktopComparison);
    if(!mobileComparison.isConnected)mobileComparisonMarker.after(mobileComparison);
  }else{
    if(!desktopComparison.isConnected)desktopComparisonMarker.after(desktopComparison);
    if(mobileComparison.isConnected)mobileComparisonStore.append(mobileComparison);
  }
}
syncComparisonRepresentation();
comparisonMedia.addEventListener('change',syncComparisonRepresentation);
""".strip()
    source = source.replace(f"{comparison_mode_script}\n\n", "")
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
        updated = strip_trailing_whitespace(updated)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} site files with exact-brand colors and accessibility improvements.")


def restore_homepage_from_preview(deployment: str) -> None:
    """Restore the homepage from a validated protected preview after a local transform failure."""
    result = subprocess.run(
        ["vercel.cmd", "curl", "/", "--deployment", deployment],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=90,
        check=False,
    )
    raw = result.stdout.lstrip("\ufeff")
    document_start = raw.find("<!DOCTYPE html>")
    document_end = raw.rfind("</html>")
    homepage = raw[document_start:document_end + len("</html>")] if min(document_start, document_end) >= 0 else ""
    if result.returncode != 0 or homepage.count("<!DOCTYPE html>") != 1 or not homepage.endswith("</html>"):
        raise RuntimeError(f"Validated preview recovery failed: {result.stderr[-500:]}")
    (ROOT / "index.html").write_text(homepage, encoding="utf-8")
    print(f"Restored index.html from protected preview {deployment}.")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--restore-index-from-preview":
        restore_homepage_from_preview(sys.argv[2])
    else:
        main()
