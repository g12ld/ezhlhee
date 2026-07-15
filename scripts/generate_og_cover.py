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

# Isolated, final, initial, and medial Arabic presentation forms.
ARABIC_FORMS = {
    "ا": ("ﺍ", "ﺎ", None, None), "إ": ("ﺇ", "ﺈ", None, None),
    "ب": ("ﺏ", "ﺐ", "ﺑ", "ﺒ"), "ة": ("ﺓ", "ﺔ", None, None),
    "ت": ("ﺕ", "ﺖ", "ﺗ", "ﺘ"), "ث": ("ﺙ", "ﺚ", "ﺛ", "ﺜ"),
    "ج": ("ﺝ", "ﺞ", "ﺟ", "ﺠ"), "ح": ("ﺡ", "ﺢ", "ﺣ", "ﺤ"),
    "خ": ("ﺥ", "ﺦ", "ﺧ", "ﺨ"), "د": ("ﺩ", "ﺪ", None, None),
    "ذ": ("ﺫ", "ﺬ", None, None), "ر": ("ﺭ", "ﺮ", None, None),
    "ز": ("ﺯ", "ﺰ", None, None), "س": ("ﺱ", "ﺲ", "ﺳ", "ﺴ"),
    "ش": ("ﺵ", "ﺶ", "ﺷ", "ﺸ"), "ص": ("ﺹ", "ﺺ", "ﺻ", "ﺼ"),
    "ض": ("ﺽ", "ﺾ", "ﺿ", "ﻀ"), "ط": ("ﻁ", "ﻂ", "ﻃ", "ﻄ"),
    "ظ": ("ﻅ", "ﻆ", "ﻇ", "ﻈ"), "ع": ("ﻉ", "ﻊ", "ﻋ", "ﻌ"),
    "غ": ("ﻍ", "ﻎ", "ﻏ", "ﻐ"), "ف": ("ﻑ", "ﻒ", "ﻓ", "ﻔ"),
    "ق": ("ﻕ", "ﻖ", "ﻗ", "ﻘ"), "ك": ("ﻙ", "ﻚ", "ﻛ", "ﻜ"),
    "ل": ("ﻝ", "ﻞ", "ﻟ", "ﻠ"), "م": ("ﻡ", "ﻢ", "ﻣ", "ﻤ"),
    "ن": ("ﻥ", "ﻦ", "ﻧ", "ﻨ"), "ه": ("ﻩ", "ﻪ", "ﻫ", "ﻬ"),
    "و": ("ﻭ", "ﻮ", None, None), "ى": ("ﻯ", "ﻰ", None, None),
    "ي": ("ﻱ", "ﻲ", "ﻳ", "ﻴ"),
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size=size)


def shaped(text: str) -> str:
    logical = list(text)
    output = []
    for index, character in enumerate(logical):
        forms = ARABIC_FORMS.get(character)
        if not forms:
            output.append(character)
            continue
        previous = logical[index - 1] if index else ""
        following = logical[index + 1] if index + 1 < len(logical) else ""
        previous_forms = ARABIC_FORMS.get(previous)
        following_forms = ARABIC_FORMS.get(following)
        joins_previous = bool(previous_forms and previous_forms[2] and forms[1])
        joins_following = bool(forms[2] and following_forms and following_forms[1])
        if joins_previous and joins_following:
            output.append(forms[3])
        elif joins_previous:
            output.append(forms[1])
        elif joins_following:
            output.append(forms[2])
        else:
            output.append(forms[0])
    return "".join(reversed(output))


def draw_arabic(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, **kwargs) -> None:
    draw.text(xy, shaped(text), anchor="mm", **kwargs)


canvas = Image.new("RGB", (WIDTH, HEIGHT), DARK)
draw = ImageDraw.Draw(canvas)
draw.rectangle((0, 0, 26, HEIGHT), fill=PRIMARY)
draw.rectangle((26, 0, 38, HEIGHT), fill=CTA)
draw.rounded_rectangle((665, 72, 1055, 122), radius=25, fill=PRIMARY)
draw_arabic(draw, (860, 97), "وكالة سعودية متخصصة", font=font("arialbd.ttf", 27), fill=WHITE)

logo = Image.open(ROOT / "images" / "logo.webp").convert("RGBA")
pixels = []
for red, green, blue, alpha in logo.get_flattened_data():
    pixels.append((red, green, blue, 0 if red < 24 and green < 24 and blue < 24 else alpha))
logo.putdata(pixels)
logo.thumbnail((430, 430), Image.Resampling.LANCZOS)
canvas.paste(logo, (75, 105), logo)

draw_arabic(draw, (860, 250), "تصميم وتطوير", font=font("arialbd.ttf", 62), fill=WHITE)
draw_arabic(draw, (860, 335), "المتاجر الإلكترونية", font=font("arialbd.ttf", 62), fill=PRIMARY)
draw.rectangle((660, 385, 1060, 389), fill=CTA)
draw_arabic(draw, (1015, 440), "سلة", font=font("arial.ttf", 34), fill=WHITE)
draw.text((955, 440), "•", anchor="mm", font=font("arial.ttf", 30), fill=WHITE)
draw_arabic(draw, (910, 440), "زد", font=font("arial.ttf", 34), fill=WHITE)
draw.text((860, 440), "•", anchor="mm", font=font("arial.ttf", 30), fill=WHITE)
draw_arabic(draw, (760, 440), "ووكومرس", font=font("arial.ttf", 34), fill=WHITE)
draw.text((860, 505), "ezhalhe-sa.com", anchor="mm", font=font("arial.ttf", 26), fill=CTA)

output = ROOT / "images" / "og-cover.webp"
canvas.save(output, "WEBP", quality=92, method=6)
print(f"{output.name}\t{output.stat().st_size}\t{WIDTH}x{HEIGHT}")
