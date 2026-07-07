# reel_templates.py — 5 animated reel template builders
# Each build_rN() returns a moviepy VideoClip (1080x1920, with audio if available).
from __future__ import annotations
import math
from pathlib import Path
from datetime import date, datetime
from typing import Optional

import numpy as np
from moviepy import VideoClip, AudioFileClip

from anim_effects import (
    REEL_SIZE, CREAM, INK, GOLD, GOLD_LIGHT, WHITE, TEAL, BLACK, AMBER_TINT,
    PHOTOS_DIR,
    ease_out_cubic, ease_in_out_sine, ease_out_back, linear, fade_alpha,
    ken_burns_frame, warm_tint, dark_gradient, top_vignette,
    render_text_block, render_stars, render_price_ticker,
    composite, draw_logo, end_card_frame, bottom_strip,
    _load_src, load_audio,
)

W, H = REEL_SIZE
MARGIN = 64


def _photo_paths(photos: list[str]) -> list[Path]:
    """Resolve photo filenames to full paths, filter to existing files."""
    paths = []
    for p in photos:
        full = PHOTOS_DIR / p
        if full.exists():
            paths.append(full)
    return paths


def _pick(paths: list[Path], index: int) -> Optional[Path]:
    if not paths:
        return None
    return paths[index % len(paths)]


def _solid(color: tuple, size=REEL_SIZE) -> np.ndarray:
    return np.full((*size[::-1], 3), color, dtype=np.uint8)


def _make_clip(make_frame, duration: float, mood: str) -> VideoClip:
    clip = VideoClip(make_frame, duration=duration)
    audio = load_audio(mood, duration)
    if audio:
        clip = clip.with_audio(audio)
    return clip


# ─────────────────────────────────────────────────────────────────────────────
# R1 — Treatment Showcase "Sole Story"  (22s, conversion)
# ─────────────────────────────────────────────────────────────────────────────

def build_r1(content: dict, lang: str = "id", photos: list = None, duration: float = 22.0) -> VideoClip:
    photos = photos or []
    paths  = _photo_paths(photos) or [None]

    # Load sources (None → solid cream fallback)
    def src(idx):
        p = _pick(paths, idx)
        return _load_src(str(p), REEL_SIZE) if p else None

    src0 = src(0)  # foot/treatment close-up
    src1 = src(1)  # treatment room
    src2 = src(2)  # therapist hands

    # Content
    t_data   = content.get("treatment", {})
    name     = t_data.get("name", {}).get(lang, "Djaya Massage")
    cat      = t_data.get("category", {}).get(lang, "").upper()
    desc     = t_data.get("desc", {}).get(lang, "")
    prices   = t_data.get("prices", [])
    price_lbl = t_data.get("price_label", "")

    # Pre-render text overlays (cached)
    eyebrow_arr  = render_text_block(cat, "segoeuib.ttf", 26, GOLD, max_width=900)
    name_arr     = render_text_block(name, "georgiab.ttf", 70, WHITE, max_width=952)
    desc_arr     = render_text_block(desc, "segoeui.ttf",  30, (215,190,155), max_width=952)
    price_arr    = render_price_ticker(prices, 40, WHITE) if prices else render_text_block(price_lbl, "segoeuib.ttf", 40, WHITE, max_width=952)
    end_frame    = end_card_frame()

    # Phase timings
    P1_END, P2_END, P3_END, P4_END = 7.0, 12.0, 17.0, 22.0

    def make_frame(t: float) -> np.ndarray:
        # ── Phase 1 (0–7s): foot photo, title fades in ──
        if t < P1_END:
            base = ken_burns_frame(src0 if src0 is not None else _solid(CREAM), t, P1_END,
                                   zoom_start=1.0, zoom_end=1.06, drift=(0, -20)) if src0 is not None else _solid(CREAM)
            base = warm_tint(base, 0.15)
            base = dark_gradient(base, int(H * 0.50), BLACK, 0.78)
            base = top_vignette(base, 180, 0.45)
            base = draw_logo(base, 36, 44, size=80, alpha=fade_alpha(0.3, 0.6, t))
            ey_a  = fade_alpha(0.5, 0.5, t)
            nm_a  = fade_alpha(0.9, 0.7, t)
            text_y = int(H * 0.55)
            base = composite(base, eyebrow_arr, MARGIN, text_y, ey_a)
            base = composite(base, name_arr,    MARGIN, text_y + 38, nm_a)
            return base

        # ── Phase 2 (7–12s): room photo, desc fades in ──
        elif t < P2_END:
            pt = t - P1_END
            pdur = P2_END - P1_END
            base = ken_burns_frame(src1 if src1 is not None else _solid((40,30,20)), pt, pdur,
                                   zoom_start=1.08, zoom_end=1.0, drift=(0, 10)) if src1 is not None else _solid((40,30,20))
            base = warm_tint(base, 0.18)
            base = dark_gradient(base, int(H * 0.45), BLACK, 0.82)
            nm_a   = fade_alpha(0.0, 0.4, pt)
            desc_a = fade_alpha(0.5, 0.7, pt)
            base = draw_logo(base, 36, 44, size=80)
            text_y = int(H * 0.52)
            base = composite(base, name_arr, MARGIN, text_y, nm_a)
            base = composite(base, desc_arr, MARGIN, text_y + name_arr.shape[0] + 16, desc_a)
            return base

        # ── Phase 3 (12–17s): hands photo + price reveal ──
        elif t < P3_END:
            pt = t - P2_END
            pdur = P3_END - P2_END
            base = ken_burns_frame(src2 if src2 is not None else _solid((35,22,10)), pt, pdur,
                                   zoom_start=1.0, zoom_end=1.07, drift=(15, -10)) if src2 is not None else _solid((35,22,10))
            base = warm_tint(base, 0.20)
            base = dark_gradient(base, int(H * 0.48), BLACK, 0.88)
            p_a  = fade_alpha(0.3, 0.6, pt)
            base = draw_logo(base, 36, 44, size=80)
            # Price card
            card_y = int(H * 0.72)
            # Gold divider
            base[card_y - 6 : card_y, MARGIN : MARGIN + 120] = np.array(GOLD)
            base = composite(base, price_arr, MARGIN, card_y + 8, p_a)
            base = bottom_strip(base)
            return base

        # ── Phase 4 (17–22s): cream end card ──
        else:
            pt   = t - P3_END
            pdur = P4_END - P3_END
            a    = ease_out_cubic(min(pt / 0.6, 1.0))
            # Blend from last frame dark bg to cream end card
            dark = _solid(BLACK)
            frame = (dark.astype(np.float32) * (1 - a) + end_frame.astype(np.float32) * a)
            return np.clip(frame, 0, 255).astype(np.uint8)

    return _make_clip(make_frame, duration, "r1")


# ─────────────────────────────────────────────────────────────────────────────
# R2 — Testimonial "Five Stars Drop"  (18s, trust)
# ─────────────────────────────────────────────────────────────────────────────

def build_r2(content: dict, lang: str = "id", photos: list = None, duration: float = 18.0) -> VideoClip:
    photos = photos or []
    paths  = _photo_paths(photos)

    review  = content.get("review", {})
    rating  = review.get("rating", 5)
    source  = review.get("source", "Google")
    name    = review.get("name", "")
    text    = review.get("text", {}).get(lang, "")
    quote   = f'"{text}"'

    # One star RGBA for animation (we composite N of them with stagger)
    star_single = render_text_block("★", "segoeuib.ttf", 64, GOLD_LIGHT, max_width=80)
    sw = star_single.shape[1]

    source_arr = render_text_block(f"{source} Review", "segoeuib.ttf", 28, GOLD,    max_width=800)
    quote_arr  = render_text_block(quote,               "georgiai.ttf", 38, WHITE,   max_width=952, line_spacing=12)
    name_arr   = render_text_block(f"— {name}",         "segoeuib.ttf", 32, (200,175,140), max_width=800)
    badge_arr  = render_text_block("Google 4.9★  ·  Tripadvisor 5.0★", "segoeui.ttf", 26, (170,150,115), max_width=800)
    cta_arr    = render_text_block("wa.me/6285278355590", "segoeuib.ttf", 36, GOLD, max_width=800)
    end_frame  = end_card_frame()

    # Background: blurred photo or solid teal
    if paths:
        bg_img = _load_src(str(paths[0]), REEL_SIZE)
        bg_arr = dark_gradient(warm_tint(bg_img, 0.25), int(H * 0.15), BLACK, 0.88)
        # _load_src adds margin for ken_burns room; crop back to canvas size
        bh, bw = bg_arr.shape[:2]
        bg_arr = bg_arr[(bh - H) // 2 : (bh - H) // 2 + H, (bw - W) // 2 : (bw - W) // 2 + W]
    else:
        bg_arr = _solid(TEAL)

    def make_frame(t: float) -> np.ndarray:
        if t < 14.0:
            base = bg_arr.copy()

            # Stars drop in one-by-one with 0.25s stagger (t=0..2.5s)
            star_y = int(H * 0.20)
            for i in range(rating):
                drop_start = i * 0.25
                a = fade_alpha(drop_start, 0.3, t, ease_out_back)
                drop_offset = int((1 - ease_out_back(min((t - drop_start) / 0.3, 1.0))) * 60) if t > drop_start else 60
                base = composite(base, star_single, MARGIN + i * (sw + 8), star_y - drop_offset, a)

            src_a   = fade_alpha(1.5, 0.5, t)
            quote_a = fade_alpha(2.5, 1.2, t)
            name_a  = fade_alpha(11.0, 0.6, t)
            badge_a = fade_alpha(11.8, 0.5, t)
            cta_a   = fade_alpha(13.0, 0.6, t)

            qy = star_y + 90
            base = composite(base, source_arr, MARGIN, qy, src_a)
            base = composite(base, quote_arr,  MARGIN, qy + 44, quote_a)
            base = composite(base, name_arr,   MARGIN, qy + 44 + quote_arr.shape[0] + 20, name_a)
            base = composite(base, badge_arr,  MARGIN, H - 280, badge_a)
            base = composite(base, cta_arr,    MARGIN, H - 220, cta_a)
            base = draw_logo(base, 36, 44, size=80, alpha=fade_alpha(0.5, 0.5, t))
            return base

        # End card (14–18s)
        pt  = t - 14.0
        a   = ease_out_cubic(min(pt / 0.8, 1.0))
        return np.clip(bg_arr.astype(np.float32) * (1-a) + end_frame.astype(np.float32) * a, 0, 255).astype(np.uint8)

    return _make_clip(make_frame, duration, "r2")


# ─────────────────────────────────────────────────────────────────────────────
# R3 — Behind the Scenes "Before You Arrive"  (25s, humanizing)
# ─────────────────────────────────────────────────────────────────────────────

def build_r3(content: dict, lang: str = "id", photos: list = None, duration: float = 25.0) -> VideoClip:
    photos = photos or []
    paths  = _photo_paths(photos)

    shots = [
        ("09.40 — 20 menit sebelum buka" if lang == "id" else "09:40 — 20 min before opening",
         "Kain hangat disiapkan." if lang == "id" else "Fresh towels, ready."),
        ("Minyak hangat disiapkan" if lang == "id" else "Warm oil, prepared",
         ""),
        ("Lilin dinyalakan." if lang == "id" else "Candles lit.",
         ""),
        ("Semua ini… untuk satu orang: kamu." if lang == "id" else "All of this… for one person: you.",
         ""),
    ]

    cta_txt = ("Djaya buka 10.00. Pesan tempatmu → wa.me/6285278355590"
               if lang == "id" else
               "Djaya opens at 10:00. Book your spot → wa.me/6285278355590")

    shot_dur = (duration - 3.0) / len(shots)   # ~5.5s each, last 3s = end card
    prerendered = [(
        render_text_block(h, "segoeuib.ttf", 28, GOLD, max_width=900),
        render_text_block(b, "georgiai.ttf", 42, WHITE, max_width=952) if b else None,
    ) for h, b in shots]
    cta_arr  = render_text_block(cta_txt, "segoeui.ttf", 28, (200,175,140), max_width=900)
    end_frame = end_card_frame()

    def make_frame(t: float) -> np.ndarray:
        shot_idx = min(int(t / shot_dur), len(shots) - 1)
        shot_t   = t - shot_idx * shot_dur

        p = _pick(paths, shot_idx)
        if p:
            src = _load_src(str(p), REEL_SIZE)
            base = ken_burns_frame(src, shot_t, shot_dur, 1.0, 1.06, drift=(5, -8))
            base = warm_tint(base, 0.12)
            base = dark_gradient(base, int(H * 0.50), BLACK, 0.80)
        else:
            base = _solid((30, 20, 12))

        base = top_vignette(base, 160, 0.4)
        base = draw_logo(base, 36, 44, size=80, alpha=0.85)

        header_arr, body_arr = prerendered[shot_idx]
        h_a = fade_alpha(0.3, 0.5, shot_t)
        b_a = fade_alpha(0.8, 0.6, shot_t) if body_arr is not None else 0.0
        text_y = int(H * 0.58)
        base = composite(base, header_arr, MARGIN, text_y, h_a)
        if body_arr is not None:
            base = composite(base, body_arr, MARGIN, text_y + 42, b_a)

        # CTA in final 4s
        if t > duration - 7.0:
            cta_a = fade_alpha(duration - 7.0, 1.0, t)
            base  = composite(base, cta_arr, MARGIN, H - 250, cta_a)

        # End card
        if t > duration - 3.0:
            pt = t - (duration - 3.0)
            a  = ease_out_cubic(min(pt / 0.8, 1.0))
            base = np.clip(base.astype(np.float32)*(1-a) + end_frame.astype(np.float32)*a, 0, 255).astype(np.uint8)

        return base

    return _make_clip(make_frame, duration, "r3")


# ─────────────────────────────────────────────────────────────────────────────
# R4 — Promo Countdown "30% Klaxon"  (12s, urgency)
# ─────────────────────────────────────────────────────────────────────────────

def build_r4(content: dict, lang: str = "id", photos: list = None,
             duration: float = 12.0, promo_end: date = None) -> VideoClip:
    photos = photos or []
    promo = content.get("promo", {})

    if lang == "en":
        headline  = "S$17 for 90 minutes."
        sub1      = "Yes, really."
        sub2      = "10 min from Harbour Bay ferry terminal."
        terms_txt = "Book your slot via WhatsApp before you board the ferry."
    else:
        headline  = promo.get("label", {}).get("id", "Diskon 30%")
        sub1      = promo.get("terms", {}).get("id", "Tunjukkan KTP Kepri.")
        sub2      = ""
        terms_txt = "Reservasi: wa.me/6285278355590"

    days_left = ""
    if promo_end:
        delta = (promo_end - date.today()).days
        days_left = f"Sisa {max(0, delta)} hari" if lang == "id" else f"{max(0, delta)} days left"

    badge_arr = render_text_block("30%", "georgiab.ttf", 180, WHITE, max_width=600)
    off_arr   = render_text_block("OFF" if lang == "en" else "DISKON", "segoeuib.ttf", 56, GOLD_LIGHT, max_width=500)
    h_arr     = render_text_block(headline, "georgiab.ttf",  52, WHITE, max_width=952)
    s1_arr    = render_text_block(sub1,     "georgiai.ttf",  40, (215,195,155), max_width=900)
    s2_arr    = render_text_block(sub2,     "segoeui.ttf",   32, (190,170,130), max_width=900) if sub2 else None
    terms_arr = render_text_block(terms_txt,"segoeuib.ttf",  34, GOLD,          max_width=900)
    days_arr  = render_text_block(days_left,"segoeuib.ttf",  30, (200,175,140), max_width=600) if days_left else None
    end_frame = end_card_frame()

    # Background: teal + optional photo overlay
    paths = _photo_paths(photos)
    if paths:
        bg_src = _load_src(str(paths[0]), REEL_SIZE)
        bg_base = dark_gradient(warm_tint(bg_src, 0.08), 0, TEAL, 0.82)
        # _load_src adds margin; crop back to canvas size
        bh, bw = bg_base.shape[:2]
        bg_base = bg_base[(bh - H) // 2 : (bh - H) // 2 + H, (bw - W) // 2 : (bw - W) // 2 + W]
    else:
        bg_base = _solid(TEAL)

    def make_frame(t: float) -> np.ndarray:
        if t < 10.0:
            base = bg_base.copy()
            base = draw_logo(base, 36, 44, size=80, alpha=0.9)

            # Phase A (0–3s): badge scales in
            if t < 3.0:
                s = ease_out_back(min(t / 0.7, 1.0))
                # Render badge at scale
                badge_y = int(H * 0.28)
                base = composite(base, badge_arr, int(W/2 - badge_arr.shape[1]//2), badge_y, s)
                base = composite(base, off_arr,   int(W/2 - off_arr.shape[1]//2), badge_y + badge_arr.shape[0], s)

            # Phase B (3–7s): terms slide in
            elif t < 7.0:
                pt  = t - 3.0
                badge_y = int(H * 0.22)
                base = composite(base, badge_arr, int(W/2 - badge_arr.shape[1]//2), badge_y, 1.0)
                base = composite(base, off_arr,   int(W/2 - off_arr.shape[1]//2), badge_y + badge_arr.shape[0], 1.0)
                h_a  = fade_alpha(0.2, 0.6, pt)
                s1_a = fade_alpha(0.8, 0.6, pt)
                s2_a = fade_alpha(1.4, 0.6, pt) if s2_arr is not None else 0.0
                ty   = int(H * 0.60)
                base = composite(base, h_arr,  MARGIN, ty, h_a)
                base = composite(base, s1_arr, MARGIN, ty + h_arr.shape[0] + 12, s1_a)
                if s2_arr is not None:
                    base = composite(base, s2_arr, MARGIN, ty + h_arr.shape[0] + s1_arr.shape[0] + 20, s2_a)

            # Phase C (7–10s): countdown + CTA
            else:
                pt   = t - 7.0
                badge_y = int(H * 0.22)
                base = composite(base, badge_arr, int(W/2 - badge_arr.shape[1]//2), badge_y, 1.0)
                base = composite(base, off_arr,   int(W/2 - off_arr.shape[1]//2), badge_y + badge_arr.shape[0], 1.0)

                # Timer bar: drains left to right
                bar_w = W - MARGIN * 2
                bar_y = int(H * 0.65)
                base[bar_y : bar_y+10, MARGIN : MARGIN + bar_w] = np.array(GOLD)  # bg
                fill = int(bar_w * (1.0 - pt / 3.0))
                base[bar_y : bar_y+10, MARGIN : MARGIN + fill] = np.array(WHITE)

                t_a    = fade_alpha(0.3, 0.5, pt)
                days_a = fade_alpha(0.6, 0.5, pt) if days_arr is not None else 0.0
                cta_pulse = 1.0  # could pulse: 0.85 + 0.15*math.sin(t*6)
                base = composite(base, terms_arr, MARGIN, bar_y + 24, t_a * cta_pulse)
                if days_arr is not None:
                    base = composite(base, days_arr, MARGIN, bar_y + 80, days_a)

            return base

        # End card (10–12s)
        pt = t - 10.0
        a  = ease_out_cubic(min(pt / 0.8, 1.0))
        return np.clip(bg_base.astype(np.float32)*(1-a) + end_frame.astype(np.float32)*a, 0, 255).astype(np.uint8)

    return _make_clip(make_frame, duration, "r4")


# ─────────────────────────────────────────────────────────────────────────────
# R5 — Ambiance / Brand "The Exhale"  (15s, reach & saves)
# ─────────────────────────────────────────────────────────────────────────────

def build_r5(content: dict, lang: str = "id", photos: list = None, duration: float = 15.0) -> VideoClip:
    photos = photos or []
    paths  = _photo_paths(photos)

    line1 = "Tarik napas."        if lang == "id" else "Breathe in."
    line2 = "Hembuskan."          if lang == "id" else "Let go."
    line3 = "Djaya — calm rooted in tradition · Batam"

    l1_arr = render_text_block(line1, "georgiai.ttf", 72, WHITE,         max_width=952)
    l2_arr = render_text_block(line2, "georgiai.ttf", 72, (220,195,155), max_width=952)
    l3_arr = render_text_block(line3, "segoeuib.ttf", 28, GOLD,          max_width=952)
    end_frame = end_card_frame()

    # Letterbox bars
    LB_H = 80  # px each side

    def make_frame(t: float) -> np.ndarray:
        if t < 13.0:
            # Two-photo Ken Burns: first 7s photo A, then cross-dissolve to B
            p0 = _pick(paths, 0)
            p1 = _pick(paths, 1) or p0

            if p0:
                s0 = _load_src(str(p0), REEL_SIZE)
                f0 = ken_burns_frame(s0, t, 13.0, 1.0, 1.05, drift=(0, -15))
                f0 = warm_tint(f0, 0.12)
            else:
                f0 = _solid((20, 14, 8))

            if t > 6.0 and p1 and str(p1) != str(p0):
                s1    = _load_src(str(p1), REEL_SIZE)
                blend = ease_in_out_sine(min((t - 6.0) / 1.5, 1.0))
                f1    = ken_burns_frame(s1, t - 6.0, 7.0, 1.05, 1.0, drift=(0, 10))
                f1    = warm_tint(f1, 0.14)
                base  = np.clip(f0.astype(np.float32)*(1-blend) + f1.astype(np.float32)*blend, 0, 255).astype(np.uint8)
            else:
                base = f0

            # Subtle dark overall tint for cinema mood
            base = dark_gradient(base, 0, BLACK, 0.45)

            # Letterbox bars
            base[:LB_H]  = np.array(BLACK)
            base[-LB_H:] = np.array(BLACK)

            # Top vignette
            base = top_vignette(base, 200, 0.35)

            # Text timings
            l1_a = fade_alpha(5.0, 1.2, t) * (1 - fade_alpha(8.5, 0.8, t))  # fades out
            l2_a = fade_alpha(8.5, 1.0, t) * (1 - fade_alpha(11.5, 0.8, t))

            cy  = H // 2 - 60
            base = composite(base, l1_arr, MARGIN, cy, l1_a)
            base = composite(base, l2_arr, MARGIN, cy + 80, l2_a)
            base = draw_logo(base, 36, LB_H + 12, size=80, alpha=fade_alpha(0.5, 0.8, t))
            return base

        # End card (13–15s) with tagline
        pt    = t - 13.0
        a     = ease_out_cubic(min(pt / 0.8, 1.0))
        frame = np.clip(
            _solid(BLACK).astype(np.float32)*(1-a) + end_frame.astype(np.float32)*a,
            0, 255
        ).astype(np.uint8)
        l3_a  = fade_alpha(13.4, 0.6, t)
        frame = composite(frame, l3_arr, MARGIN, int(H*0.52) + 60, l3_a)
        return frame

    return _make_clip(make_frame, duration, "r5")
