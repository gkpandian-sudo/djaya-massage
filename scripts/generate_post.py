# generate_post.py — 1080x1080 Instagram post renderer
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw

from composer import (
    CREAM, CREAM_DARK, INK, INK_SOFT, GOLD, GOLD_LIGHT, WHITE, BLACK,
    PHOTOS_DIR, REPO_DIR,
    font_display, font_display_it, font_display_reg, font_body, font_body_bold,
    load_photo, apply_bottom_gradient, draw_logo,
    draw_divider, draw_gold_dot, draw_stars, draw_bottom_strip,
    draw_text_block, draw_multiline_text, text_height, text_width,
)
import content as C

SIZE   = (1080, 1080)
W, H   = SIZE
MARGIN = 52
CONTENT_W = W - MARGIN * 2

PHOTO_H   = 560   # top photo section height
TEXT_TOP  = PHOTO_H + 36

OUTPUT_DIR = REPO_DIR / "output" / "posts"


def _save(img: Image.Image, filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    img.save(str(path), "JPEG", quality=95)
    print(f"  saved: {path.name}")
    return path


# ── Treatment spotlight ───────────────────────────────────────────────────────

def render_treatment(t: dict) -> Path:
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    # ── Photo panel (top 560px) ──
    photo = load_photo(t["photo"], (W, PHOTO_H), warm_tint=0.15)
    img.paste(photo, (0, 0))

    # Gradient: photo fades to cream at bottom
    apply_bottom_gradient(img, PHOTO_H - 200, color=CREAM, max_alpha=255)

    # ── Logo top-left ──
    draw_logo(img, 28, 24, size=64)

    # ── Category eyebrow ──
    y = TEXT_TOP
    cat_id  = t["category"]["id"]
    cat_en  = t["category"]["en"]
    eyebrow = f"{cat_id.upper()}  ·  {cat_en.upper()}"
    draw.text((MARGIN, y), eyebrow, font=font_body_bold(18), fill=GOLD)
    y += 28

    # ── Treatment name (bilingual) ──
    name_id = t["name"]["id"]
    name_en = t["name"]["en"]
    y = draw_multiline_text(draw, name_id, font_display(46), MARGIN, y, CONTENT_W, INK, line_spacing=4)
    y += 4
    y = draw_multiline_text(draw, name_en, font_display_it(28), MARGIN, y, CONTENT_W, INK_SOFT, line_spacing=2)
    y += 18

    # ── Divider ──
    draw_divider(draw, MARGIN, y, 80, GOLD, thickness=3)
    y += 20

    # ── Description ──
    desc = t["desc"]["id"]
    y = draw_text_block(draw, desc, font_body(24), MARGIN, y, CONTENT_W, INK, line_spacing=5)
    y += 16

    # ── Prices ──
    for dur, price in t["prices"]:
        line = f"{dur}  ·  {price}"
        draw.text((MARGIN, y), line, font=font_body_bold(26), fill=INK)
        y += 36

    # ── Bottom strip ──
    draw_bottom_strip(img, strip_h=100)

    return _save(img, f"treatment-{t['slug']}.jpg")


# ── Testimonial ───────────────────────────────────────────────────────────────

def render_testimonial(review: dict, photo: str, index: int) -> Path:
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    photo_img = load_photo(photo, (W, PHOTO_H - 60), warm_tint=0.22)
    img.paste(photo_img, (0, 0))
    apply_bottom_gradient(img, PHOTO_H - 260, color=CREAM, max_alpha=255)
    draw_logo(img, 28, 24, size=64)

    y = PHOTO_H - 20

    # Rating stars
    y = draw_stars(draw, MARGIN, y, review["rating"], size=32)

    # Source label
    source_line = f"{review['source']} Review"
    draw.text((MARGIN, y), source_line, font=font_body_bold(18), fill=GOLD)
    y += 30

    # Quote
    quote_id = f'"{review["text"]["id"]}"'
    quote_en = f'"{review["text"]["en"]}"'
    y = draw_text_block(draw, quote_id, font_display_reg(30), MARGIN, y, CONTENT_W, INK, line_spacing=6)
    y += 6
    y = draw_text_block(draw, quote_en, font_display_it(24), MARGIN, y, CONTENT_W, INK_SOFT, line_spacing=4)
    y += 16

    # Attribution
    name_line = f"— {review['name']}"
    draw.text((MARGIN, y), name_line, font=font_body_bold(24), fill=INK)
    y += 40

    # Rating badges
    badge = f"Google 4.9★  ·  Tripadvisor 5.0★"
    draw.text((MARGIN, y), badge, font=font_body(20), fill=INK_SOFT)

    draw_bottom_strip(img, strip_h=100)
    return _save(img, f"testimonial-{index+1}.jpg")


# ── Promo ─────────────────────────────────────────────────────────────────────

def render_promo() -> Path:
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    photo = load_photo("hero.jpg", (W, PHOTO_H), warm_tint=0.10)
    img.paste(photo, (0, 0))
    apply_bottom_gradient(img, PHOTO_H - 260, color=CREAM, max_alpha=255)
    draw_logo(img, 28, 24, size=64)

    y = TEXT_TOP - 10

    # Eyebrow
    draw.text((MARGIN, y), "PROMO SPESIAL  ·  SPECIAL PROMO", font=font_body_bold(18), fill=GOLD)
    y += 32

    # Headline — big
    label_id = C.PROMO["label"]["id"]
    label_en = C.PROMO["label"]["en"]
    draw.text((MARGIN, y), label_id, font=font_display(54), fill=INK)
    y += 68
    draw.text((MARGIN, y), label_en, font=font_display_it(34), fill=INK_SOFT)
    y += 52

    draw_divider(draw, MARGIN, y, 80, GOLD, thickness=3)
    y += 22

    # Terms bilingual
    terms_id = C.PROMO["terms"]["id"]
    terms_en = C.PROMO["terms"]["en"]
    draw.text((MARGIN, y), terms_id, font=font_body(26), fill=INK)
    y += 36
    draw.text((MARGIN, y), terms_en, font=font_body(22), fill=INK_SOFT)
    y += 46

    # CTA
    cta = "Chat us on WhatsApp  ·  Hubungi via WhatsApp"
    draw.text((MARGIN, y), cta, font=font_body_bold(22), fill=GOLD)

    draw_bottom_strip(img, strip_h=100)
    return _save(img, "promo-30off.jpg")


# ── Location ──────────────────────────────────────────────────────────────────

def render_location() -> Path:
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    photo = load_photo("about.jpg", (W, PHOTO_H), warm_tint=0.12)
    img.paste(photo, (0, 0))
    apply_bottom_gradient(img, PHOTO_H - 240, color=CREAM, max_alpha=255)
    draw_logo(img, 28, 24, size=64)

    y = TEXT_TOP

    # Eyebrow
    draw.text((MARGIN, y), "LOKASI  ·  LOCATION", font=font_body_bold(18), fill=GOLD)
    y += 32

    # Heading
    draw.text((MARGIN, y), "Kunjungi Kami di Batam", font=font_display(48), fill=INK)
    y += 60
    draw.text((MARGIN, y), "Visit Us in Batam", font=font_display_it(30), fill=INK_SOFT)
    y += 46

    draw_divider(draw, MARGIN, y, 80, GOLD, thickness=3)
    y += 22

    # Address block
    address_lines = [
        "Jl. Komp. Penuin Centre No. 14, Blok A",
        "Batu Selicin, Kec. Lubuk Baja",
        "Kota Batam, Kepulauan Riau 29411",
    ]
    for line in address_lines:
        draw.text((MARGIN, y), line, font=font_body(24), fill=INK)
        y += 34

    y += 10
    landmark_id = C.BUSINESS["landmark"]["id"]
    landmark_en = C.BUSINESS["landmark"]["en"]
    draw.text((MARGIN, y), landmark_id, font=font_body_bold(24), fill=GOLD)
    y += 34
    draw.text((MARGIN, y), landmark_en, font=font_body(22), fill=INK_SOFT)
    y += 40

    hours_id = C.BUSINESS["hours"]["id"]
    hours_en = C.BUSINESS["hours"]["en"]
    draw.text((MARGIN, y), hours_id, font=font_body_bold(26), fill=INK)
    y += 36
    draw.text((MARGIN, y), hours_en, font=font_body(22), fill=INK_SOFT)

    draw_bottom_strip(img, strip_h=100)
    return _save(img, "location.jpg")


# ── Ambiance / Gallery ────────────────────────────────────────────────────────

def render_ambiance(photo_file: str, index: int) -> Path:
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    photo = load_photo(photo_file, (W, H - 140), warm_tint=0.10)
    img.paste(photo, (0, 0))

    # Dark gradient at bottom for text
    apply_bottom_gradient(img, H - 380, color=(30, 18, 8), max_alpha=210)

    draw_logo(img, 28, 24, size=64)

    y = H - 340
    tagline_id = "Ketenangan yang berakar pada tradisi."
    tagline_en = "Calm, rooted in tradition."

    draw.text((MARGIN, y), tagline_id, font=font_display(42), fill=WHITE)
    y += 54
    draw.text((MARGIN, y), tagline_en, font=font_display_it(28), fill=(220, 200, 170))
    y += 50

    desc = "Djaya Massage & Reflexology — premium spa di Penuin Centre, Batam.\nOpen daily 10 AM – 10 PM"
    y = draw_text_block(draw, desc, font_body(22), MARGIN, y, CONTENT_W, (200, 180, 150), line_spacing=5)

    draw_bottom_strip(img, strip_h=100, on_photo=True)
    return _save(img, f"ambiance-{index+1}.jpg")


# ── Booking reminder ──────────────────────────────────────────────────────────

def render_booking_reminder() -> Path:
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    photo = load_photo("Hero.jpeg", (W, PHOTO_H), warm_tint=0.08)
    img.paste(photo, (0, 0))
    apply_bottom_gradient(img, PHOTO_H - 240, color=CREAM, max_alpha=255)
    draw_logo(img, 28, 24, size=64)

    y = TEXT_TOP

    draw.text((MARGIN, y), "RESERVASI  ·  BOOK NOW", font=font_body_bold(18), fill=GOLD)
    y += 32

    draw.text((MARGIN, y), "Siap untuk Beristirahat?", font=font_display(50), fill=INK)
    y += 62
    draw.text((MARGIN, y), "Ready to Unwind?", font=font_display_it(32), fill=INK_SOFT)
    y += 50

    draw_divider(draw, MARGIN, y, 80, GOLD, thickness=3)
    y += 22

    body_id = "Booking langsung lewat WhatsApp. Tim kami siap membantu memilih waktu dan perawatan terbaik untuk Anda."
    body_en = "Book directly via WhatsApp. Our team will help you choose the best time and treatment."
    y = draw_text_block(draw, body_id, font_body(24), MARGIN, y, CONTENT_W, INK, line_spacing=5)
    y += 8
    y = draw_text_block(draw, body_en, font_body(22), MARGIN, y, CONTENT_W, INK_SOFT, line_spacing=4)
    y += 30

    hours_id = C.BUSINESS["hours"]["id"]
    hours_en = C.BUSINESS["hours"]["en"]
    draw.text((MARGIN, y), hours_id, font=font_body_bold(26), fill=INK)
    y += 36
    draw.text((MARGIN, y), hours_en, font=font_body(22), fill=INK_SOFT)

    draw_bottom_strip(img, strip_h=100)
    return _save(img, "booking-reminder.jpg")


# ── Signature ─────────────────────────────────────────────────────────────────

def render_signature() -> Path:
    t = C.TREATMENTS["signature"][0]
    img = Image.new("RGB", SIZE, CREAM)
    draw = ImageDraw.Draw(img)

    photo = load_photo(t["photo"], (W, PHOTO_H + 40), warm_tint=0.12)
    img.paste(photo, (0, 0))
    apply_bottom_gradient(img, PHOTO_H - 180, color=CREAM, max_alpha=255)
    draw_logo(img, 28, 24, size=64)

    y = PHOTO_H + 20

    draw.text((MARGIN, y), "DJAYA SIGNATURE", font=font_body_bold(18), fill=GOLD)
    y += 30

    draw.text((MARGIN, y), "3-in-1 Healing Ritual", font=font_display(52), fill=INK)
    y += 66

    draw_divider(draw, MARGIN, y, 80, GOLD, thickness=3)
    y += 22

    desc_id = t["desc"]["id"]
    desc_en = t["desc"]["en"]
    y = draw_text_block(draw, desc_id, font_body(23), MARGIN, y, CONTENT_W, INK, line_spacing=5)
    y += 6
    y = draw_text_block(draw, desc_en, font_body(21), MARGIN, y, CONTENT_W, INK_SOFT, line_spacing=4)
    y += 18

    draw.text((MARGIN, y), "150 min  ·  Rp 420.000", font=font_body_bold(28), fill=INK)

    draw_bottom_strip(img, strip_h=100)
    return _save(img, "signature-3in1.jpg")
