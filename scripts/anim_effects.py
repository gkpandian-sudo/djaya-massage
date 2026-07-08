# anim_effects.py — animation primitives for Djaya reel generation
# No moviepy dependency here — pure numpy/PIL so these are fast and testable.
from __future__ import annotations
import math
from pathlib import Path
from functools import lru_cache
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPTS_DIR  = Path(__file__).resolve().parent
REPO_DIR     = SCRIPTS_DIR.parent
ASSETS_DIR   = REPO_DIR / "assets"
PHOTOS_DIR   = ASSETS_DIR / "photos"
AUDIO_DIR    = ASSETS_DIR / "audio"
FONTS_DIR    = Path("C:/Windows/Fonts")

# ── Brand palette ─────────────────────────────────────────────────────────────
CREAM      = (242, 232, 218)
INK        = (52,  38,  24)
GOLD       = (193, 152,  28)
GOLD_LIGHT = (230, 190,  80)
WHITE      = (255, 255, 255)
TEAL       = (27,  78,  82)
BLACK      = (10,   6,   2)
AMBER_TINT = (60,  30,  10)

REEL_SIZE  = (1080, 1920)


# ── Easing ────────────────────────────────────────────────────────────────────

def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_in_out_sine(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return -(math.cos(math.pi * t) - 1) / 2

def ease_out_back(t: float, s: float = 1.70158) -> float:
    t = max(0.0, min(1.0, t))
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def linear(t: float) -> float:
    return max(0.0, min(1.0, t))


# ── Ken Burns ─────────────────────────────────────────────────────────────────

def _load_src(img_path: str, canvas: Tuple[int,int], margin: int = 80) -> np.ndarray:
    """Load + cover-resize image to canvas + margin for zoom/drift room."""
    W, H = canvas
    img = Image.open(img_path).convert("RGB")
    target_w, target_h = W + margin, H + margin
    scale = max(target_w / img.width, target_h / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    # Center crop to exact target
    cx, cy = nw // 2, nh // 2
    img = img.crop((cx - target_w//2, cy - target_h//2,
                    cx + target_w//2, cy + target_h//2))
    return np.array(img)


def ken_burns_frame(
    src: np.ndarray,
    t: float,
    duration: float,
    zoom_start: float = 1.0,
    zoom_end:   float = 1.08,
    size: Tuple[int,int] = REEL_SIZE,
    drift: Tuple[int,int] = (0, -30),
) -> np.ndarray:
    """Return a numpy H×W×3 frame: Ken Burns zoom+drift at time t."""
    W, H = size
    p  = ease_in_out_sine(min(t / max(duration, 1e-6), 1.0))
    z  = zoom_start + (zoom_end - zoom_start) * p
    # Crop a (W/z × H/z) region, then resize to (W×H)
    crop_w = max(1, int(W / z))
    crop_h = max(1, int(H / z))
    ah, aw  = src.shape[:2]
    dx = int(drift[0] * p)
    dy = int(drift[1] * p)
    cx = aw // 2 + dx
    cy = ah // 2 + dy
    x1 = max(0, min(cx - crop_w // 2, aw - crop_w))
    y1 = max(0, min(cy - crop_h // 2, ah - crop_h))
    crop = src[y1 : y1 + crop_h, x1 : x1 + crop_w]
    return np.array(Image.fromarray(crop).resize((W, H), Image.BILINEAR))


# ── Photo effects ─────────────────────────────────────────────────────────────

def warm_tint(frame: np.ndarray, strength: float = 0.15) -> np.ndarray:
    tint = np.array(AMBER_TINT, dtype=np.float32)
    out  = frame.astype(np.float32) * (1 - strength) + tint * strength
    return np.clip(out, 0, 255).astype(np.uint8)


def dark_gradient(frame: np.ndarray, start_y: int, color: Tuple = BLACK, max_alpha: float = 0.92) -> np.ndarray:
    """Apply a dark gradient from start_y to bottom."""
    H, W = frame.shape[:2]
    out  = frame.astype(np.float32)
    c    = np.array(color, dtype=np.float32)
    span = max(H - start_y, 1)
    for i in range(span):
        alpha = max_alpha * ((i / span) ** 0.6)
        y = start_y + i
        if 0 <= y < H:
            out[y] = out[y] * (1 - alpha) + c * alpha
    return np.clip(out, 0, 255).astype(np.uint8)


def top_vignette(frame: np.ndarray, end_y: int = 200, max_alpha: float = 0.5) -> np.ndarray:
    """Subtle dark vignette at top."""
    out = frame.astype(np.float32)
    c   = np.array(BLACK, dtype=np.float32)
    for i in range(end_y):
        alpha = max_alpha * ((1 - i / end_y) ** 0.8)
        out[i] = out[i] * (1 - alpha) + c * alpha
    return np.clip(out, 0, 255).astype(np.uint8)


# ── Text rendering ────────────────────────────────────────────────────────────

def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONTS_DIR / name), size)
    except OSError:
        return ImageFont.load_default()

def _wrap(text: str, font: ImageFont.FreeTypeFont, max_px: int, dummy: ImageDraw.ImageDraw) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bb = dummy.textbbox((0,0), test, font=font)
        if bb[2] - bb[0] <= max_px:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def render_text_block(
    text: str,
    font_name: str = "georgia.ttf",
    font_size: int = 52,
    color: Tuple = WHITE,
    max_width: int = 952,
    line_spacing: int = 10,
    padding: int = 0,
) -> np.ndarray:
    """Render text to an RGBA numpy array sized to fit."""
    font = _font(font_name, font_size)
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    segments = text.split("\n")
    all_lines = []
    for seg in segments:
        all_lines.extend(_wrap(seg, font, max_width, dummy_draw) if seg else [""])

    # Measure
    sample_bb = dummy_draw.textbbox((0,0), "Ag", font=font)
    line_h = sample_bb[3] - sample_bb[1]
    total_h = len(all_lines) * (line_h + line_spacing) + padding * 2
    total_w = max_width + padding * 2

    img  = Image.new("RGBA", (total_w, total_h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    y = padding
    for line in all_lines:
        draw.text((padding, y), line, font=font, fill=(*color, 255))
        y += line_h + line_spacing
    return np.array(img)


def render_stars(count: int, size: int = 52, color: Tuple = GOLD_LIGHT) -> np.ndarray:
    return render_text_block("★" * count, "segoeuib.ttf", size, color, max_width=500)


def render_price_ticker(prices: list, size: int = 42, color: Tuple = WHITE) -> np.ndarray:
    lines = "  ·  ".join(f"{dur}  {price}" for dur, price in prices)
    return render_text_block(lines, "segoeuib.ttf", size, color, max_width=952)


# ── Compositing ───────────────────────────────────────────────────────────────

def composite(
    base: np.ndarray,          # H×W×3 uint8
    overlay: np.ndarray,       # h×w×4 uint8 RGBA
    x: int,
    y: int,
    alpha: float = 1.0,
) -> np.ndarray:
    """Alpha-composite RGBA overlay onto RGB base at pixel (x, y)."""
    BH, BW = base.shape[:2]
    OH, OW = overlay.shape[:2]
    # Clip to canvas bounds
    ox0 = max(0, -x);  oy0 = max(0, -y)
    bx0 = max(0,  x);  by0 = max(0,  y)
    ox1 = min(OW, BW - x);  oy1 = min(OH, BH - y)
    bx1 = bx0 + (ox1 - ox0);  by1 = by0 + (oy1 - oy0)
    if ox1 <= ox0 or oy1 <= oy0:
        return base
    out  = base.copy().astype(np.float32)
    src  = overlay[oy0:oy1, ox0:ox1].astype(np.float32)
    a    = np.clip((src[:, :, 3:4] / 255.0) * np.clip(alpha, 0.0, 1.0), 0.0, 1.0)
    rgb  = src[:,:,:3]
    out[by0:by1, bx0:bx1] = out[by0:by1, bx0:bx1] * (1 - a) + rgb * a
    return np.clip(out, 0, 255).astype(np.uint8)


def fade_alpha(start: float, dur: float, t: float, easing=ease_out_cubic) -> float:
    """Compute fade-in alpha at time t (0→1 over [start, start+dur])."""
    if t < start:
        return 0.0
    return easing(min((t - start) / max(dur, 1e-6), 1.0))


def paint_scrim(
    frame: np.ndarray,
    y: int,
    h: int,
    color: Tuple = BLACK,
    alpha: float = 0.60,
    feather: int = 24,
) -> np.ndarray:
    """Semi-transparent dark band at (y, y+h) to improve text legibility.
    feather: pixels over which the top edge fades in (soft edge up top, hard at bottom)."""
    H_f = frame.shape[0]
    y0, y1 = max(0, y), min(H_f, y + h)
    out = frame.copy().astype(np.float32)
    c   = np.array(color, dtype=np.float32)
    span = y1 - y0
    for i in range(span):
        if i < feather:
            a = alpha * (i / feather)
        else:
            a = alpha
        out[y0 + i] = out[y0 + i] * (1 - a) + c * a
    return np.clip(out, 0, 255).astype(np.uint8)


def render_text_shadowed(
    text: str,
    font_name: str = "georgia.ttf",
    font_size: int = 52,
    color: Tuple = WHITE,
    max_width: int = 952,
    line_spacing: int = 10,
    shadow_alpha: float = 0.75,
) -> np.ndarray:
    """Render text RGBA with a dark blurred drop shadow for any-background legibility."""
    offset = max(3, font_size // 16)
    shadow = render_text_block(text, font_name, font_size, BLACK, max_width, line_spacing, padding=offset)
    main   = render_text_block(text, font_name, font_size, color,  max_width, line_spacing, padding=0)

    # Blur shadow
    sh_img = Image.fromarray(shadow, "RGBA")
    sh_img = sh_img.filter(ImageFilter.GaussianBlur(radius=max(2, font_size // 18)))
    sh_arr = np.array(sh_img)
    sh_arr[:, :, 3] = (sh_arr[:, :, 3].astype(np.float32) * shadow_alpha).astype(np.uint8)

    OH, OW = shadow.shape[:2]
    canvas = np.zeros((OH, OW, 4), dtype=np.uint8)

    # Composite shadow then main text
    for arr in (sh_arr, main):
        ah, aw = arr.shape[:2]
        ch = min(ah, OH)
        cw = min(aw, OW)
        a  = arr[:ch, :cw, 3:4].astype(np.float32) / 255.0
        for ch_idx in range(3):
            canvas[:ch, :cw, ch_idx] = np.clip(
                canvas[:ch, :cw, ch_idx].astype(np.float32) * (1 - a[:, :, 0])
                + arr[:ch, :cw, ch_idx].astype(np.float32) * a[:, :, 0],
                0, 255,
            ).astype(np.uint8)
        canvas[:ch, :cw, 3] = np.clip(
            canvas[:ch, :cw, 3].astype(np.float32) + arr[:ch, :cw, 3].astype(np.float32),
            0, 255,
        ).astype(np.uint8)
    return canvas


# ── Logo ──────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=4)
def _logo_rgba(size: int) -> np.ndarray | None:
    logo_path = ASSETS_DIR / "logo.png"
    if not logo_path.exists():
        return None
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0,0,0,0))
    off_x = (size - logo.width)  // 2
    off_y = (size - logo.height) // 2
    out.paste(logo, (off_x, off_y), logo)
    return np.array(out)


def draw_logo(frame: np.ndarray, x: int = 36, y: int = 44, size: int = 80, alpha: float = 1.0) -> np.ndarray:
    logo = _logo_rgba(size)
    if logo is None:
        return frame
    return composite(frame, logo, x, y, alpha)


# ── End card ──────────────────────────────────────────────────────────────────

def end_card_frame(size: Tuple[int,int] = REEL_SIZE) -> np.ndarray:
    """Cream end card with logo + WA line."""
    W, H = size
    img  = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    # Gold divider
    draw.rectangle([64, H//2 - 4, W - 64, H//2], fill=GOLD)
    # WA text
    font_wa = _font("segoeuib.ttf", 38)
    font_ig = _font("segoeui.ttf",  30)
    draw.text((64, H//2 + 24), "wa.me/6285278355590", font=font_wa, fill=INK)
    draw.text((64, H//2 + 76), "@djayamassage  ·  Penuin Centre, Batam", font=font_ig, fill=(120,96,68))
    frame = np.array(img)
    frame = draw_logo(frame, 64, H//2 - 140, size=100)
    return frame


# ── Bottom strip ──────────────────────────────────────────────────────────────

def bottom_strip(frame: np.ndarray, strip_h: int = 130) -> np.ndarray:
    """Branded footer bar on photo background."""
    H, W = frame.shape[:2]
    out  = frame.copy().astype(np.float32)
    # Semi-transparent dark band
    out[H-strip_h:] = out[H-strip_h:] * 0.35 + np.array(BLACK, dtype=np.float32) * 0.65
    out  = np.clip(out, 0, 255).astype(np.uint8)

    wa_txt  = render_text_block("WhatsApp  +62 852-7835-5590", "segoeuib.ttf", 28, (220,195,150), max_width=900)
    ig_txt  = render_text_block("@djayamassage  ·  Penuin Centre, Batam", "segoeui.ttf", 24, (180,158,125), max_width=900)
    out = composite(out, wa_txt,  48, H - strip_h + 16)
    out = composite(out, ig_txt,  48, H - strip_h + 60)
    return out


# ── Audio ─────────────────────────────────────────────────────────────────────

# Maps reel template → audio track in assets/audio/
# Mood rationale:
#   r1 Treatment Showcase → momentum  (confident, driving — earns trust)
#   r2 Testimonial        → reflect   (measured, thoughtful — builds credibility)
#   r3 BTS                → calm      (clean, focused — behind-the-scenes authenticity)
#   r4 Promo Countdown    → pulse     (upbeat, energetic — urgency drives action)
#   r5 Ambiance           → rise      (hopeful, building — emotional brand feel)
MOOD_FILES = {
    "r1": "momentum.mp3",
    "r2": "reflect.mp3",
    "r3": "calm.mp3",
    "r4": "pulse.mp3",
    "r5": "rise.mp3",
}

def load_audio(mood: str, duration: float):
    """Return a trimmed/looped AudioFileClip or None if file missing."""
    try:
        from moviepy import AudioFileClip
        from moviepy.audio.fx import AudioFadeIn, AudioFadeOut
    except ImportError:
        return None

    path = AUDIO_DIR / MOOD_FILES.get(mood, "")
    if not path.exists():
        return None

    try:
        audio = AudioFileClip(str(path))
        # Loop if shorter than duration
        if audio.duration < duration:
            loops = int(math.ceil(duration / audio.duration))
            from moviepy import concatenate_audioclips
            audio = concatenate_audioclips([audio] * loops)
        audio = audio.subclipped(0, duration)
        audio = audio.with_effects([AudioFadeIn(0.5), AudioFadeOut(1.5)])
        return audio
    except Exception:
        return None
