#!/usr/bin/env python3
"""Generate responsive WebP variants and add intrinsic image attributes."""

from __future__ import annotations

import csv
import html
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "images"
VARIANT_DIR = IMAGE_DIR / "responsive"
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "06-performance"
IMG_RE = re.compile(r"<img\b[^>]*>", re.I | re.S)


def attribute(tag: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}=["\']([^"\']*)["\']', tag, re.I)
    return html.unescape(match.group(1)) if match else ""


def strip_attribute(tag: str, name: str) -> str:
    return re.sub(rf'\s+\b{re.escape(name)}=["\'][^"\']*["\']', "", tag, flags=re.I)


def encoded_relative(source_file: Path, target: Path) -> str:
    relative = Path(os.path.relpath(target, start=source_file.parent)).as_posix()
    return quote(relative, safe="/._-")


def generate_variants(image_path: Path) -> list[tuple[Path, int]]:
    with Image.open(image_path) as image:
        width, height = image.size
        square_asset = abs(width - height) <= max(width, height) * 0.08
        desired = (128, 256) if square_asset else (360, 720)
        outputs = []
        for target_width in desired:
            if target_width >= width:
                continue
            target_height = max(1, round(height * target_width / width))
            output = VARIANT_DIR / f"{image_path.stem}-{target_width}.webp"
            if not output.exists():
                resized = image.convert("RGBA" if image.mode in {"RGBA", "LA"} else "RGB")
                resized = resized.resize((target_width, target_height), Image.Resampling.LANCZOS)
                resized.save(output, "WEBP", quality=82, method=6)
            outputs.append((output, target_width))
        return outputs


def update_page(path: Path, dimensions: dict[Path, tuple[int, int]], variants: dict[Path, list[tuple[Path, int]]]) -> list[dict[str, str]]:
    content = path.read_text(encoding="utf-8")
    rows = []
    image_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal image_index
        tag = match.group(0)
        src = attribute(tag, "src")
        if not src or src.startswith(("data:", "http://", "https://")):
            return tag
        parsed = urlsplit(src)
        local = (path.parent / unquote(parsed.path)).resolve()
        if local not in dimensions:
            return tag
        image_index += 1
        width, height = dimensions[local]
        eager = path.name == "index.html" and path.parent == ROOT and image_index == 1
        loading = "eager" if eager else "lazy"
        updated = tag
        for name in ("width", "height", "loading", "decoding", "fetchpriority", "srcset", "sizes"):
            updated = strip_attribute(updated, name)
        closing = "/>" if updated.rstrip().endswith("/>") else ">"
        updated = updated.rstrip()
        updated = updated[:-2].rstrip() if closing == "/>" else updated[:-1].rstrip()
        extra = [
            f'width="{width}"',
            f'height="{height}"',
            f'loading="{loading}"',
            'decoding="async"',
        ]
        sources = [
            (encoded_relative(path, variant_path), variant_width)
            for variant_path, variant_width in variants.get(local, [])
        ]
        sources.append((src, width))
        unique_sources = []
        seen_widths = set()
        for source, source_width in sources:
            if source_width not in seen_widths:
                seen_widths.add(source_width)
                unique_sources.append((source, source_width))
        if len(unique_sources) > 1:
            extra.append('srcset="' + ", ".join(f"{source} {source_width}w" for source, source_width in unique_sources) + '"')
            square = abs(width - height) <= max(width, height) * 0.08
            sizes = "72px" if square else "(max-width: 767px) 92vw, (max-width: 1100px) 46vw, 380px"
            extra.append(f'sizes="{sizes}"')
        if eager:
            extra.append('fetchpriority="high"')
        updated = f"{updated} {' '.join(extra)}{closing}"
        rows.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "src": src,
                "width": str(width),
                "height": str(height),
                "loading": loading,
                "decoding": "async",
                "fetchpriority": "high" if eager else "auto",
                "responsive_candidates": str(len(unique_sources)),
            }
        )
        return updated

    updated = IMG_RE.sub(replace, content)
    path.write_text(updated, encoding="utf-8", newline="")
    return rows


def main() -> None:
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    originals = sorted(IMAGE_DIR.glob("*.webp"))
    dimensions = {}
    variants = {}
    for image_path in originals:
        with Image.open(image_path) as image:
            dimensions[image_path.resolve()] = image.size
        variants[image_path.resolve()] = generate_variants(image_path)

    rows = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        rows.extend(update_page(path, dimensions, variants))

    with (REPORT_DIR / "image-optimization-map.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fields = ["file", "src", "width", "height", "loading", "decoding", "fetchpriority", "responsive_candidates"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    original_bytes = sum(path.stat().st_size for path in originals)
    variant_files = sorted(VARIANT_DIR.glob("*.webp"))
    print(
        {
            "image_occurrences_updated": len(rows),
            "original_images": len(originals),
            "responsive_variants": len(variant_files),
            "original_bytes": original_bytes,
            "variant_bytes": sum(path.stat().st_size for path in variant_files),
        }
    )


if __name__ == "__main__":
    main()
