# generate_reel.py — 1080x1920 Instagram reel/story cover renderer
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw

from composer import (
    CREAM, CREAM_DARK, INK, INK_SOFT, GOLD, GOLD_LIGHT, WHITE, BLACK, OVERLAY_AMBER,
    REPO_DIR,
    font_display, font_display_it, font_display_reg, font_body, font_body_bold,
    load_photo, apply_bottom_gradient, apply_top_gradient, draw_logo,
    draw_divider, draw_stars, draw_bottom_strip,
    draw_text_block, draw_multiline_text, text_height, text_width,
)
import content as C

SIZE   = (1080, 1920)
W, H   = SIZE
MARGIN = 64
CONTENT_W = W - MARGIN * 2

OUTPUT_DIR = REPO_DIR / "output" / "reels"

# Text block starts at bottom third — keeps top for the photo to breathe
TEXT_START = H - 860
STRIP_H    = 120


def _save(img: Image.Image, filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    img.save(str(path), "JPEG", quality=95)
    print(f"  saved: {path.name}")
    return path


def _base_canvas(photo_file: str, tint: float = 0.20) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Full-bleed photo with dark gradient at bottom for legibility."""
    photo = load_photo(photo_file, SIZE, warm_tint=tint)
    img = Image.new("RGB", SIZE, BLACK)
    img.paste(photo, (0, 0))
    # Strong dark gradient covers bottom 55% for text contrast
    apply_bottom_gradient(img, int(H * 0.38), color=(20, 10, 4), max_alpha=240)
    # Subtle top vignette
    apply_top_gradient(img, 180, color=BLACK, max_alpha=80)
    return img, ImageDraw.Draw(img)


# ── Treatment spotlight ───────────────────────────────────────────────────────

def render_treatment(t: dict) -> Path:
    img, draw = _base_canvas(t["photo"])
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START

    # Category eyebrow
    eyebrow = f"{t['category']['id'].upper()}  ·  {t['category']['en'].upper()}"
    draw.text((MARGIN, y), eyebrow, font=font_body_bold(22), fill=GOLD)
    y += 34

    # Treatment name — large, bilingual
    name_id = t["name"]["id"]
    name_en = t["name"]["en"]
    y = draw_multiline_text(draw, name_id, font_display(66), MARGIN, y, CONTENT_W, WHITE, line_spacing=6)
    y += 6
    y = draw_multiline_text(draw, name_en, font_display_it(40), MARGIN, y, CONTENT_W, (210, 185, 145), line_spacing=4)
    y += 28

    draw_divider(draw, MARGIN, y, 100, GOLD, thickness=3)
    y += 24

    # Description (shorter — space is tight)
    desc_id = t["desc"]["id"]
    desc_en = t["desc"]["en"]
    y = draw_text_block(draw, desc_id, font_body(28), MARGIN, y, CONTENT_W, (230, 215, 195), line_spacing=6)
    y += 8
    y = draw_text_block(draw, desc_en, font_body(24), MARGIN, y, CONTENT_W, (190, 170, 140), line_spacing=4)
    y += 24

    # Prices
    for dur, price in t["prices"]:
        draw.text((MARGIN, y), f"{dur}  ·  {price}", font=font_body_bold(32), fill=WHITE)
        y += 44

    # Footer strip
    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, f"treatment-{t['slug']}.jpg")


# ── Testimonial ───────────────────────────────────────────────────────────────

def render_testimonial(review: dict, photo: str, index: int) -> Path:
    img, draw = _base_canvas(photo, tint=0.25)
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START - 40

    y = draw_stars(draw, MARGIN, y, review["rating"], size=40, color=GOLD_LIGHT)

    source = f"{review['source']} Review"
    draw.text((MARGIN, y), source, font=font_body_bold(22), fill=GOLD)
    y += 36

    # Bilingual quote — give space
    quote_id = f'"{review["text"]["id"]}"'
    quote_en = f'"{review["text"]["en"]}"'
    y = draw_text_block(draw, quote_id, font_display_reg(38), MARGIN, y, CONTENT_W, WHITE, line_spacing=8)
    y += 12
    y = draw_text_block(draw, quote_en, font_display_it(30), MARGIN, y, CONTENT_W, (200, 180, 150), line_spacing=6)
    y += 24

    # Name
    draw.text((MARGIN, y), f"— {review['name']}", font=font_body_bold(30), fill=WHITE)
    y += 52

    # Rating badges
    draw.text((MARGIN, y), "Google 4.9★  ·  Tripadvisor 5.0★", font=font_body(24), fill=(180, 160, 130))

    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, f"testimonial-{index+1}.jpg")


# ── Promo ─────────────────────────────────────────────────────────────────────

def render_promo() -> Path:
    img, draw = _base_canvas("hero.jpg", tint=0.10)
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START - 60

    draw.text((MARGIN, y), "PROMO SPESIAL  ·  SPECIAL PROMO", font=font_body_bold(22), fill=GOLD)
    y += 38

    label_id = C.PROMO["label"]["id"]
    label_en = C.PROMO["label"]["en"]
    draw.text((MARGIN, y), label_id, font=font_display(72), fill=WHITE)
    y += 86
    draw.text((MARGIN, y), label_en, font=font_display_it(46), fill=(210, 185, 145))
    y += 68

    draw_divider(draw, MARGIN, y, 100, GOLD, thickness=3)
    y += 30

    terms_id = C.PROMO["terms"]["id"]
    terms_en = C.PROMO["terms"]["en"]
    draw.text((MARGIN, y), terms_id, font=font_body(30), fill=WHITE)
    y += 44
    draw.text((MARGIN, y), terms_en, font=font_body(26), fill=(200, 180, 150))
    y += 56

    draw.text((MARGIN, y), "Chat via WhatsApp  ·  Hubungi kami →", font=font_body_bold(26), fill=GOLD)

    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, "promo-30off.jpg")


# ── Ambiance ──────────────────────────────────────────────────────────────────

def render_ambiance(photo_file: str, index: int) -> Path:
    img, draw = _base_canvas(photo_file, tint=0.12)
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START + 60

    draw.text((MARGIN, y), "DJAYA MASSAGE & REFLEXOLOGY", font=font_body_bold(22), fill=GOLD)
    y += 36

    draw.text((MARGIN, y), "Ketenangan yang\nberakar pada tradisi.", font=font_display(60), fill=WHITE)
    y += 156

    draw.text((MARGIN, y), "Calm, rooted in tradition.", font=font_display_it(38), fill=(210, 185, 145))
    y += 60

    draw_divider(draw, MARGIN, y, 100, GOLD, thickness=3)
    y += 30

    sub = "Premium spa di Penuin Centre, Batam\nBuka setiap hari · 10.00 – 22.00"
    draw_text_block(draw, sub, font_body(26), MARGIN, y, CONTENT_W, (200, 180, 150), line_spacing=6)

    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, f"ambiance-{index+1}.jpg")


# ── Location ──────────────────────────────────────────────────────────────────

def render_location() -> Path:
    img, draw = _base_canvas("about.jpg", tint=0.15)
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START - 40

    draw.text((MARGIN, y), "LOKASI  ·  LOCATION", font=font_body_bold(22), fill=GOLD)
    y += 38

    draw.text((MARGIN, y), "Kunjungi Kami\ndi Batam", font=font_display(66), fill=WHITE)
    y += 148

    draw.text((MARGIN, y), "Visit Us in Batam", font=font_display_it(40), fill=(210, 185, 145))
    y += 60

    draw_divider(draw, MARGIN, y, 100, GOLD, thickness=3)
    y += 28

    for line in ["Jl. Komp. Penuin Centre No. 14, Blok A", "Lubuk Baja, Kota Batam, Kepri 29411"]:
        draw.text((MARGIN, y), line, font=font_body(26), fill=WHITE)
        y += 38

    y += 12
    draw.text((MARGIN, y), C.BUSINESS["landmark"]["id"], font=font_body_bold(26), fill=GOLD)
    y += 38
    draw.text((MARGIN, y), C.BUSINESS["landmark"]["en"], font=font_body(24), fill=(200, 180, 150))
    y += 48

    draw.text((MARGIN, y), C.BUSINESS["hours"]["id"], font=font_body_bold(28), fill=WHITE)
    y += 40
    draw.text((MARGIN, y), C.BUSINESS["hours"]["en"], font=font_body(24), fill=(200, 180, 150))

    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, "location.jpg")


# ── Booking reminder ──────────────────────────────────────────────────────────

def render_booking_reminder() -> Path:
    img, draw = _base_canvas("Hero.jpeg", tint=0.08)
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START - 40

    draw.text((MARGIN, y), "RESERVASI  ·  BOOK NOW", font=font_body_bold(22), fill=GOLD)
    y += 38

    draw.text((MARGIN, y), "Siap untuk\nBeristirahat?", font=font_display(68), fill=WHITE)
    y += 150

    draw.text((MARGIN, y), "Ready to Unwind?", font=font_display_it(42), fill=(210, 185, 145))
    y += 62

    draw_divider(draw, MARGIN, y, 100, GOLD, thickness=3)
    y += 28

    body_id = "Booking langsung lewat WhatsApp. Tim kami bantu pilih waktu & treatment terbaik."
    body_en = "Book on WhatsApp. Our team helps you pick the best time and treatment."
    y = draw_text_block(draw, body_id, font_body(28), MARGIN, y, CONTENT_W, WHITE, line_spacing=6)
    y += 8
    y = draw_text_block(draw, body_en, font_body(24), MARGIN, y, CONTENT_W, (200, 180, 150), line_spacing=5)
    y += 36

    draw.text((MARGIN, y), C.BUSINESS["hours"]["id"], font=font_body_bold(30), fill=GOLD)
    y += 44
    draw.text((MARGIN, y), C.BUSINESS["hours"]["en"], font=font_body(26), fill=(200, 180, 150))

    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, "booking-reminder.jpg")


# ── Signature ─────────────────────────────────────────────────────────────────

def render_signature() -> Path:
    t = C.TREATMENTS["signature"][0]
    img, draw = _base_canvas(t["photo"], tint=0.12)
    draw_logo(img, 36, 40, size=80)

    y = TEXT_START - 50

    draw.text((MARGIN, y), "DJAYA SIGNATURE", font=font_body_bold(22), fill=GOLD)
    y += 36

    draw.text((MARGIN, y), "3-in-1 Healing\nRitual", font=font_display(70), fill=WHITE)
    y += 152

    draw_divider(draw, MARGIN, y, 100, GOLD, thickness=3)
    y += 28

    y = draw_text_block(draw, t["desc"]["id"], font_body(28), MARGIN, y, CONTENT_W, (230, 215, 195), line_spacing=6)
    y += 8
    y = draw_text_block(draw, t["desc"]["en"], font_body(24), MARGIN, y, CONTENT_W, (190, 170, 140), line_spacing=5)
    y += 28

    draw.text((MARGIN, y), "150 min  ·  Rp 420.000", font=font_body_bold(36), fill=WHITE)

    draw_bottom_strip(img, strip_h=STRIP_H, on_photo=True)
    return _save(img, "signature-3in1.jpg")
