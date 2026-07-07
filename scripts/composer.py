# composer.py — PIL canvas utilities for Djaya Massage content generation
from __future__ import annotations
import textwrap
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_DIR    = SCRIPTS_DIR.parent
ASSETS_DIR  = REPO_DIR / "assets"
PHOTOS_DIR  = ASSETS_DIR / "photos"
FONTS_DIR   = Path("C:/Windows/Fonts")

# ── Palette (matches djaya-apps.vercel.app) ──────────────────────────────────

CREAM      = (242, 232, 218)
CREAM_DARK = (220, 206, 186)
INK        = (52, 38, 24)
INK_SOFT   = (120, 96, 68)
GOLD       = (193, 152, 28)
GOLD_LIGHT = (230, 190, 80)
WHITE      = (255, 255, 255)
BLACK      = (10, 6, 2)
OVERLAY_AMBER = (60, 30, 10)   # warm tint for photo overlay

# ── Fonts ────────────────────────────────────────────────────────────────────

def _f(name: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONTS_DIR / name), size)
    except OSError:
        return ImageFont.load_default()

def font_display(size: int)      -> ImageFont.FreeTypeFont: return _f("georgiab.ttf",   size)
def font_display_it(size: int)   -> ImageFont.FreeTypeFont: return _f("georgiai.ttf",   size)
def font_display_reg(size: int)  -> ImageFont.FreeTypeFont: return _f("georgia.ttf",    size)
def font_body(size: int)         -> ImageFont.FreeTypeFont: return _f("segoeui.ttf",    size)
def font_body_bold(size: int)    -> ImageFont.FreeTypeFont: return _f("segoeuib.ttf",   size)

# ── Text helpers ─────────────────────────────────────────────────────────────

def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]

def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_px: int) -> list[str]:
    """Word-wrap text to fit within max_px width."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if text_width(draw, test, font) <= max_px:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    max_width: int,
    color: Tuple,
    line_spacing: int = 6,
    align: str = "left",
) -> int:
    """Draw wrapped text, return the y position after the last line."""
    lines = wrap_text(draw, text, font, max_width)
    for line in lines:
        if align == "center":
            lw = text_width(draw, line, font)
            draw.text((x + (max_width - lw) // 2, y), line, font=font, fill=color)
        else:
            draw.text((x, y), line, font=font, fill=color)
        y += text_height(draw, line, font) + line_spacing
    return y

def draw_multiline_text(
    draw: ImageDraw.ImageDraw,
    text: str,                  # may contain \n for explicit breaks
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    max_width: int,
    color: Tuple,
    line_spacing: int = 8,
    align: str = "left",
) -> int:
    """Handle \n in text + auto-wrap each segment."""
    for segment in text.split("\n"):
        y = draw_text_block(draw, segment, font, x, y, max_width, color, line_spacing, align)
    return y

# ── Photo helpers ─────────────────────────────────────────────────────────────

def load_photo(filename: str, size: Tuple[int, int], warm_tint: float = 0.18) -> Image.Image:
    """Load a photo from assets/photos/, resize+crop to fill size, apply warm tint."""
    path = PHOTOS_DIR / filename
    if not path.exists():
        img = Image.new("RGB", size, CREAM)
        return img
    photo = Image.open(path).convert("RGB")
    # Scale to cover (aspect-fill)
    tw, th = size
    pw, ph = photo.size
    scale = max(tw / pw, th / ph)
    new_w, new_h = int(pw * scale), int(ph * scale)
    photo = photo.resize((new_w, new_h), Image.LANCZOS)
    # Center crop
    left = (new_w - tw) // 2
    top  = (new_h - th) // 2
    photo = photo.crop((left, top, left + tw, top + th))
    # Warm amber tint overlay
    if warm_tint > 0:
        tint = Image.new("RGB", size, OVERLAY_AMBER)
        photo = Image.blend(photo, tint, warm_tint)
    return photo

def gradient_overlay(img: Image.Image, start_y: int, end_y: int, start_alpha: int, end_alpha: int, color: Tuple[int,int,int]) -> None:
    """Draw a vertical gradient rectangle (for fade effects)."""
    overlay = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(overlay)
    h = end_y - start_y
    if h <= 0:
        return
    for i in range(h):
        alpha = int(start_alpha + (end_alpha - start_alpha) * (i / h))
        draw.line([(0, start_y + i), (img.width, start_y + i)], fill=(*color, alpha))
    img.paste(overlay.convert("RGB"), (0, 0), overlay.split()[3] if overlay.mode == "RGBA" else None)

def apply_bottom_gradient(img: Image.Image, gradient_start: int, color: Tuple[int,int,int] = BLACK, max_alpha: int = 210) -> None:
    """Fade the bottom of the image to a solid color."""
    w, h = img.size
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grad)
    span = h - gradient_start
    for i in range(span):
        alpha = int(max_alpha * (i / span) ** 0.7)
        draw.line([(0, gradient_start + i), (w, gradient_start + i)], fill=(*color, alpha))
    base = img.convert("RGBA")
    combined = Image.alpha_composite(base, grad)
    img.paste(combined.convert("RGB"))

def apply_top_gradient(img: Image.Image, gradient_end: int, color: Tuple[int,int,int] = BLACK, max_alpha: int = 160) -> None:
    """Fade the top of the image from a solid color."""
    w, h = img.size
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grad)
    for i in range(gradient_end):
        alpha = int(max_alpha * (1 - i / gradient_end) ** 0.8)
        draw.line([(0, i), (w, i)], fill=(*color, alpha))
    base = img.convert("RGBA")
    combined = Image.alpha_composite(base, grad)
    img.paste(combined.convert("RGB"))

# ── Logo ──────────────────────────────────────────────────────────────────────

def draw_logo(img: Image.Image, x: int, y: int, size: int = 72) -> None:
    logo_path = ASSETS_DIR / "logo.png"
    if not logo_path.exists():
        return
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((size, size), Image.LANCZOS)
    # Paste with alpha mask
    img.paste(logo, (x, y), logo)

# ── Decorative elements ───────────────────────────────────────────────────────

def draw_divider(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, color: Tuple, thickness: int = 2) -> None:
    draw.rectangle([x, y, x + width, y + thickness], fill=color)

def draw_gold_dot(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 4) -> None:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)

def draw_stars(draw: ImageDraw.ImageDraw, x: int, y: int, count: int, size: int = 28, color: Tuple = None) -> int:
    color = color or GOLD_LIGHT
    font = font_body_bold(size)
    stars = "★" * count
    draw.text((x, y), stars, font=font, fill=color)
    return y + text_height(draw, stars, font) + 4

# ── Bottom strip (shared between post + reel) ─────────────────────────────────

def draw_bottom_strip(img: Image.Image, strip_h: int = 100, on_photo: bool = False) -> None:
    """Draw the branded footer strip at the bottom of the canvas."""
    w, h = img.size
    y0 = h - strip_h
    draw = ImageDraw.Draw(img)

    if not on_photo:
        # Cream divider line
        draw.rectangle([0, y0, w, y0 + 2], fill=CREAM_DARK)
        draw.rectangle([0, y0 + 2, w, h], fill=CREAM)
        text_color = INK_SOFT
    else:
        text_color = (200, 180, 150)

    wa_line  = "WhatsApp  +62 852-7835-5590"
    ig_line  = "@djayamassage  ·  Penuin Centre, Batam"
    font_wa  = font_body_bold(22)
    font_ig  = font_body(20)

    draw.text((40, y0 + 12), wa_line, font=font_wa, fill=text_color)
    draw.text((40, y0 + 48), ig_line, font=font_ig, fill=text_color)
