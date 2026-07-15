"""Apply the shared UI system to all public HTML pages.

The script is intentionally idempotent so future page additions can reuse the
same design layer without duplicating tags.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_ROOT_FILES = {"_new_testi.html", "google387142411d334808.html"}
STYLE_TAG = '  <link rel="stylesheet" href="/ui-system.css" data-ui-system>\n'
SCRIPT_TAG = '  <script src="/ui-system.js" defer data-ui-system></script>\n'
BROKEN_FAVICON_FRAGMENT = (
    "<rect width='100' height='100' rx='20' fill='%2304B5B8'/>"
    "<text y='.9em' font-size='70' text-anchor='middle' x='50'>🛒</text></svg>\">"
)
FAVICON_TAG = '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
BODY_TAG = re.compile(r"<body(?P<attributes>[^>]*)>", re.IGNORECASE)


def public_pages() -> list[Path]:
    root_pages = [
        path
        for path in ROOT.glob("*.html")
        if path.name not in EXCLUDED_ROOT_FILES
    ]
    article_pages = list((ROOT / "articles").glob("*.html"))
    return sorted(root_pages + article_pages)


def desired_body_classes(path: Path) -> list[str]:
    classes = ["ui-pro", "ui-pending"]
    if path.name == "index.html":
        return [*classes, "ui-home", "ui-page-home"]
    if path.parent.name == "articles":
        return [*classes, "ui-inner-page", "ui-page-article"]
    if path.name in {"articles.html", "blog.html"}:
        return [*classes, "ui-inner-page", "ui-page-articles"]
    return [*classes, "ui-inner-page", "ui-page-inner"]


def apply_ui_tags(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    updated = source.replace(BROKEN_FAVICON_FRAGMENT, "")
    while updated.count(FAVICON_TAG) > 1:
        duplicate_at = updated.rfind(FAVICON_TAG)
        updated = updated[:duplicate_at] + updated[duplicate_at + len(FAVICON_TAG):]

    body_match = BODY_TAG.search(updated)
    if body_match:
        attributes = body_match.group("attributes")
        class_match = re.search(r'class=["\'](?P<classes>[^"\']*)["\']', attributes, re.IGNORECASE)
        required_classes = desired_body_classes(path)
        if class_match:
            current_classes = class_match.group("classes").split()
            merged_classes = " ".join(dict.fromkeys([*current_classes, *required_classes]))
            attributes = (
                attributes[:class_match.start()]
                + f'class="{merged_classes}"'
                + attributes[class_match.end():]
            )
        else:
            attributes = f'{attributes} class="{" ".join(required_classes)}"'
        updated = updated[:body_match.start()] + f"<body{attributes}>" + updated[body_match.end():]

    if "data-ui-system" not in updated:
        if "</head>" not in updated or "</body>" not in updated:
            raise ValueError(f"Missing head or body terminator: {path}")
        updated = updated.replace("</head>", f"{STYLE_TAG}</head>", 1)
        updated = updated.replace("</body>", f"{SCRIPT_TAG}</body>", 1)

    if updated == source:
        return False

    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    pages = public_pages()
    changed = sum(apply_ui_tags(path) for path in pages)
    print(f"UI system present on {len(pages)} public pages; {changed} updated.")


if __name__ == "__main__":
    main()
