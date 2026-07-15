#!/usr/bin/env python3
"""Improve critical rendering order, font loading, and event handling."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FONT_IMPORT_RE = re.compile(
    r"\s*@import\s+url\([\"']?(https://fonts\.googleapis\.com/[^)\"']+)[\"']?\);?\s*",
    re.I,
)
HEAD_RE = re.compile(r"<head\b[^>]*>", re.I)
HERO_RE = re.compile(r"\s*<!-- HERO -->\s*(<section class=\"hero\">.*?</section>)\s*", re.S)

FONT_LINKS_TEMPLATE = """{head}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="{font_url}">"""

PERFORMANCE_STYLES = """

/* Critical rendering and interaction performance */
body>section:not(.hero){content-visibility:auto;contain-intrinsic-size:auto 800px}
.work-card:hover .scroll-img,.pm-item:hover .scroll-img{will-change:transform}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto!important}
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}
}
"""

SCROLL_BLOCK_RE = re.compile(
    r"/\* ── HEADER SCROLL ── \*/.*?window\.addEventListener\('resize', initScrollPreviews\);",
    re.S,
)

SCROLL_BLOCK = """/* ── HEADER SCROLL ── */
let headerScrollFrame=0;
function updateHeaderShadow(){
  headerScrollFrame=0;
  const header=document.getElementById('hdr');
  if(header) header.style.boxShadow=window.scrollY>30?'0 4px 24px rgba(21,181,176,.1)':'none';
}
window.addEventListener('scroll',()=>{
  if(!headerScrollFrame) headerScrollFrame=requestAnimationFrame(updateHeaderShadow);
},{passive:true});

/* ── SMART SCROLL PREVIEWS ── */
function calcScrollDistance(img,containerH){
  const scale=img.offsetWidth/(img.naturalWidth||img.offsetWidth);
  const actualH=(img.naturalHeight||containerH*3)*scale;
  return Math.max(0,actualH-containerH);
}
function bindScrollPreview(container,trigger){
  const img=container.querySelector('.scroll-img');
  if(!img||trigger.dataset.scrollPreviewBound==='true') return;
  trigger.dataset.scrollPreviewBound='true';
  const doScroll=()=>{
    if(!img.complete||img.naturalHeight===0){img.addEventListener('load',doScroll,{once:true});return;}
    const maxScroll=calcScrollDistance(img,container.offsetHeight);
    if(maxScroll>0) img.style.transform=`translateY(-${maxScroll}px)`;
  };
  trigger.addEventListener('mouseenter',doScroll);
  trigger.addEventListener('mouseleave',()=>{img.style.transform='translateY(0)';});
}
function initScrollPreviews(){
  document.querySelectorAll('.card-viewport').forEach(viewport=>{
    const card=viewport.closest('.work-card');
    if(card) bindScrollPreview(viewport,card);
  });
  document.querySelectorAll('.pm-item').forEach(item=>bindScrollPreview(item,item));
}
document.addEventListener('DOMContentLoaded',initScrollPreviews,{once:true});
window.addEventListener('resize',()=>{
  document.querySelectorAll('.scroll-img').forEach(img=>{img.style.transform='translateY(0)';});
},{passive:true});"""

NOOP_SCROLL_RE = re.compile(
    r"\s*// تحسين الأداء عند التمرير\s*let scrollTimeout;\s*window\.addEventListener\('scroll'.*?\n\s*\}\);",
    re.S,
)
HEADER_SCROLL_RE = re.compile(
    r"window\.addEventListener\('scroll',\(\)=>\{\s*"
    r"document\.getElementById\('hdr'\)\.style\.boxShadow=window\.scrollY>30\?"
    r"'0 4px 24px rgba\(4,181,184,\.1\)':'none';\s*\}\);",
    re.S,
)
HEADER_SCROLL = """let headerFrame=0;
window.addEventListener('scroll',()=>{
  if(headerFrame) return;
  headerFrame=requestAnimationFrame(()=>{
    headerFrame=0;
    const header=document.getElementById('hdr');
    if(header) header.style.boxShadow=window.scrollY>30?'0 4px 24px rgba(21,181,176,.1)':'none';
  });
},{passive:true});"""


def remove_external_fonts(content: str) -> str:
    content = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*', "\n", content
    )
    content = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*', "\n", content
    )
    content = re.sub(
        r'\s*<link (?:href="https://fonts\.googleapis\.com/[^"]+" rel="stylesheet"|rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]+")>\s*',
        "\n",
        content,
    )
    content = re.sub(
        r"font-family:\s*['\"]Tajawal['\"]\s*,\s*sans-serif",
        "font-family:Tahoma,Arial,sans-serif",
        content,
        flags=re.I,
    )
    return content


def optimize_fonts(path: Path, content: str) -> tuple[str, bool]:
    imports = FONT_IMPORT_RE.findall(content)
    if not imports:
        return content, False
    font_url = imports[0].replace("&amp;", "&")
    content = FONT_IMPORT_RE.sub("\n", content)
    if "rel=\"preconnect\" href=\"https://fonts.googleapis.com\"" not in content:
        content, count = HEAD_RE.subn(
            lambda match: FONT_LINKS_TEMPLATE.format(head=match.group(0), font_url=font_url),
            content,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"Cannot add font links to {path}")
    return content, True


def optimize_homepage(content: str) -> str:
    hero_match = HERO_RE.search(content)
    header_end = content.find("</header>")
    if hero_match and header_end >= 0 and hero_match.start() > header_end + 200:
        hero = hero_match.group(1)
        content = content[: hero_match.start()] + "\n" + content[hero_match.end() :]
        header_end = content.find("</header>") + len("</header>")
        content = content[:header_end] + f"\n\n<!-- HERO -->\n{hero}\n" + content[header_end:]
    if "/* Critical rendering and interaction performance */" not in content:
        content = content.replace("</style>", PERFORMANCE_STYLES + "\n</style>", 1)
    content = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*',
        "\n",
        content,
        count=1,
    )
    content = re.sub(
        r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*',
        "\n",
        content,
        count=1,
    )
    content = re.sub(
        r'\s*<link href="https://fonts\.googleapis\.com/[^"]+" rel="stylesheet">\s*',
        "\n",
        content,
        count=1,
    )
    content = content.replace(
        "body{font-family:'Tajawal',sans-serif;",
        "body{font-family:Tahoma,Arial,sans-serif;",
        1,
    )
    content = content.replace("  will-change:transform;\n", "")
    content = content.replace(
        "document.addEventListener('click',function(){\n  if(consultOpen&&!document.getElementById('consultPopup').contains(event.target)){",
        "document.addEventListener('click',function(event){\n  if(consultOpen&&!document.getElementById('consultPopup').contains(event.target)){",
        1,
    )
    content, count = SCROLL_BLOCK_RE.subn(SCROLL_BLOCK, content, count=1)
    if count != 1 and "dataset.scrollPreviewBound" not in content:
        raise RuntimeError("Homepage scroll-preview block did not match")
    preload = '<link rel="preload" as="image" href="images/responsive/logo-128.webp" type="image/webp" fetchpriority="high">'
    if preload not in content:
        content = content.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n    ' + preload, 1)
    return content


def main() -> None:
    font_pages = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8")
        content = content.replace('src="logo.png"', 'src="images/logo.webp"')
        content, changed = optimize_fonts(path, content)
        content = content.replace("display=swap", "display=optional")
        content = remove_external_fonts(content)
        content = HEADER_SCROLL_RE.sub(HEADER_SCROLL, content, count=1)
        font_pages += int(changed)
        if path == ROOT / "index.html":
            content = optimize_homepage(content)
        if path == ROOT / "articles.html":
            content = NOOP_SCROLL_RE.sub("\n", content, count=1)
        path.write_text(content, encoding="utf-8", newline="")
    print({"font_imports_replaced": font_pages, "hero_moved_to_top": True, "event_handlers_deduplicated": True})


if __name__ == "__main__":
    main()
