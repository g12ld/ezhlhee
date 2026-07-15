#!/usr/bin/env python3
"""Generate the deterministic 1200x630 Ezhalha social preview image."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 630
DARK = "#0D2224"
PRIMARY = "#15B5B0"
CTA = "#3BBBC2"
WHITE = "#FFFFFF"
TEXT = "#555555"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size=size)


canvas = Image.new("RGB", (WIDTH, HEIGHT), DARK)
draw = ImageDraw.Draw(canvas)

draw.rectangle((0, 0, 26, HEIGHT), fill=PRIMARY)
draw.rectangle((26, 0, 38, HEIGHT), fill=CTA)
draw.rounded_rectangle((700, 72, 1100, 122), radius=25, fill=PRIMARY)
draw.text(
    (1080, 97),
    "وكالة سعودية متخصصة",
    font=font("arialbd.ttf", 27),
    fill=WHITE,
    anchor="rm",
    direction="rtl",
    language="ar",
)

logo = Image.open(ROOT / "images" / "logo.webp").convert("RGBA")
logo.thumbnail((420, 420), Image.Resampling.LANCZOS)
logo_x = 90
logo_y = (HEIGHT - logo.height) // 2
canvas.paste(logo, (logo_x, logo_y), logo)

draw.text(
    (1100, 250),
    "تصميم وتطوير",
    font=font("arialbd.ttf", 62),
    fill=WHITE,
    anchor="ra",
    direction="rtl",
    language="ar",
)
draw.text(
    (1100, 335),
    "المتاجر الإلكترونية",
    font=font("arialbd.ttf", 62),
    fill=PRIMARY,
    anchor="ra",
    direction="rtl",
    language="ar",
)
draw.line((700, 385, 1100, 385), fill=CTA, width=4)
draw.text(
    (1100, 435),
    "سلة  •  زد  •  ووكومرس",
    font=font("arial.ttf", 34),
    fill=WHITE,
    anchor="ra",
    direction="rtl",
    language="ar",
)
draw.text(
    (1100, 500),
    "ezhalhe-sa.com",
    font=font("arial.ttf", 26),
    fill=CTA,
    anchor="ra",
)

output = ROOT / "images" / "og-cover.webp"
canvas.save(output, "WEBP", quality=92, method=6)
print(f"{output.name}\t{output.stat().st_size}\t{WIDTH}x{HEIGHT}")
