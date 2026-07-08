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
    render_text_block, render_text_shadowed, render_stars, render_price_ticker,
    composite, draw_logo, end_card_frame, bottom_strip,
    paint_scrim, _load_src, load_audio,
    line_wipe, slide_in_x, scale_overlay, count_up_price,
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

    # Pre-render text overlays — shadowed for readability on any photo
    eyebrow_arr  = render_text_shadowed(cat,  "segoeuib.ttf", 28, (230,190,80),  max_width=900,  shadow_blur=3)
    name_arr     = render_text_shadowed(name, "georgiab.ttf", 72, WHITE,          max_width=952,  shadow_blur=4)
    desc_arr     = render_text_shadowed(desc, "segoeui.ttf",  34, (222,200,168),  max_width=952,  line_spacing=12, shadow_blur=3)
    price_arr    = (render_price_ticker(prices, 44, WHITE)
                    if prices else
                    render_text_shadowed(price_lbl, "segoeuib.ttf", 44, WHITE, max_width=952, shadow_blur=3))
    end_frame    = end_card_frame()

    # Phase timings
    P1_END, P2_END, P3_END, P4_END = 7.0, 12.0, 17.0, 22.0
    _last_p3_frame: list = [None]   # mutable container — captures last Phase 3 frame

    def make_frame(t: float) -> np.ndarray:
        # ── Phase 1 (0–7s): foot/treatment photo, title fades in ──
        if t < P1_END:
            base = (ken_burns_frame(src0, t, P1_END, 1.0, 1.07, drift=(0, -25))
                    if src0 is not None else _solid(CREAM))
            base = warm_tint(base, 0.18)
            base = dark_gradient(base, int(H * 0.38), BLACK, 0.88)  # stronger, starts higher
            base = top_vignette(base, 220, 0.50)
            text_y = int(H * 0.53)
            scrim_h = eyebrow_arr.shape[0] + name_arr.shape[0] + 60
            base = paint_scrim(base, text_y - 20, scrim_h, alpha=0.48, feather=30)
            logo_a = fade_alpha(0.3, 0.6, t)
            base = draw_logo(base, 36, 44, size=80, alpha=logo_a)

            # Gold line wipe below eyebrow — starts at t=0.4, completes by t=0.85
            wipe_progress = (t - 0.4) / 0.45 if t > 0.4 else 0.0
            base = line_wipe(base, x=MARGIN, y=text_y - 10, h=6, w_final=140, progress=wipe_progress)

            # Eyebrow: slide in from x=28 → x=MARGIN while fading in
            ey_a = fade_alpha(0.5, 0.5, t)
            ey_x = slide_in_x(eyebrow_arr, x_from=28, x_to=MARGIN, progress=(t - 0.5) / 0.5 if t > 0.5 else 0.0)
            nm_a = fade_alpha(0.9, 0.7, t)

            base = composite(base, eyebrow_arr, ey_x, text_y, ey_a)
            base = composite(base, name_arr,    MARGIN, text_y + 38, nm_a)
            return base

        # ── Phase 2 (7–12s): room photo, description fades in ──
        elif t < P2_END:
            pt   = t - P1_END
            pdur = P2_END - P1_END
            base = (ken_burns_frame(src1, pt, pdur, 1.08, 1.0, drift=(0, 12))
                    if src1 is not None else _solid((40, 30, 20)))
            base = warm_tint(base, 0.20)
            base = dark_gradient(base, int(H * 0.35), BLACK, 0.90)
            base = top_vignette(base, 200, 0.42)
            text_y = int(H * 0.50)
            scrim_h = name_arr.shape[0] + desc_arr.shape[0] + 60
            base = paint_scrim(base, text_y - 16, scrim_h, alpha=0.50, feather=28)
            nm_a   = fade_alpha(0.0, 0.4, pt)
            desc_a = fade_alpha(0.5, 0.7, pt)
            base = draw_logo(base, 36, 44, size=80)
            base = composite(base, name_arr, MARGIN, text_y, nm_a)
            base = composite(base, desc_arr, MARGIN, text_y + name_arr.shape[0] + 16, desc_a)
            return base

        # ── Phase 3 (12–17s): detail photo + price reveal ──
        elif t < P3_END:
            pt   = t - P2_END
            pdur = P3_END - P2_END
            base = (ken_burns_frame(src2, pt, pdur, 1.0, 1.08, drift=(15, -12))
                    if src2 is not None else _solid((35, 22, 10)))
            base = warm_tint(base, 0.22)
            base = dark_gradient(base, int(H * 0.40), BLACK, 0.92)
            p_a    = fade_alpha(0.3, 0.6, pt)
            base   = draw_logo(base, 36, 44, size=80)
            card_y = int(H * 0.70)

            # Gold accent bar wipe (animated, not static)
            wipe_p = (pt - 0.2) / 0.45 if pt > 0.2 else 0.0
            base = line_wipe(base, x=MARGIN, y=card_y - 8, h=6, w_final=140, progress=wipe_p)
            base = paint_scrim(base, card_y - 12, price_arr.shape[0] + 48, alpha=0.55, feather=20)

            # Animated price count-up (only when prices list is available)
            if prices and pt > 0.3:
                try:
                    first_rp = int(prices[0][1].replace("Rp ", "").replace(".", "").replace(",", ""))
                    count_progress = min((pt - 0.3) / 0.8, 1.0)
                    dyn_price_arr = count_up_price(first_rp, count_progress, font_size=44)
                    base = composite(base, dyn_price_arr, MARGIN, card_y + 8, p_a)
                except (ValueError, IndexError):
                    base = composite(base, price_arr, MARGIN, card_y + 8, p_a)
            else:
                base = composite(base, price_arr, MARGIN, card_y + 8, p_a)

            # bottom_strip fade-in (was instant pop-in, now fades over 0.6s)
            strip_a = fade_alpha(float(P2_END) + 1.0, 0.6, t)
            if strip_a > 0.01:
                base_with_strip = bottom_strip(base)
                base = np.clip(
                    base.astype(np.float32) * (1 - strip_a) + base_with_strip.astype(np.float32) * strip_a,
                    0, 255,
                ).astype(np.uint8)
            # strip stays invisible until fade_alpha blend takes over at t=13.0
            _last_p3_frame[0] = base
            return base

        # ── Phase 4 (17–22s): cream end card ──
        else:
            pt   = t - P3_END
            prev = _last_p3_frame[0] if _last_p3_frame[0] is not None else _solid(BLACK)
            a    = ease_out_cubic(min(pt / 0.6, 1.0))
            return np.clip(prev.astype(np.float32) * (1 - a) + end_frame.astype(np.float32) * a, 0, 255).astype(np.uint8)

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
    star_single = render_text_block("★", "segoeuib.ttf", 72, (230,190,80), max_width=100)
    sw = star_single.shape[1]

    source_arr = render_text_shadowed(f"{source} Review", "segoeuib.ttf", 30, (193,152,28),  max_width=800, shadow_blur=3)
    quote_arr  = render_text_shadowed(quote,               "georgiai.ttf", 44, WHITE,         max_width=920, line_spacing=16, shadow_blur=3)
    name_arr   = render_text_shadowed(f"— {name}",         "segoeuib.ttf", 34, (210,185,148), max_width=800, shadow_blur=3)
    badge_arr  = render_text_shadowed("Google 4.9 ★  ·  Tripadvisor 5.0 ★", "segoeui.ttf", 28, (205,183,140), max_width=820, shadow_blur=3)
    cta_arr    = render_text_shadowed("wa.me/6285278355590", "segoeuib.ttf", 38, (230,190,80), max_width=800, shadow_blur=3)
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

    # Pre-compute scrim heights (quote block height may vary by review length)
    quote_block_h = source_arr.shape[0] + 52 + quote_arr.shape[0] + 30 + name_arr.shape[0] + 40

    def make_frame(t: float) -> np.ndarray:
        if t < duration - 4.0:
            base = bg_arr.copy()
            base = dark_gradient(base, int(H * 0.08), BLACK, 0.72)
            base = top_vignette(base, 180, 0.40)

            star_y = int(H * 0.18)
            base = paint_scrim(base, star_y - 24, 80 + quote_block_h, alpha=0.52, feather=32)

            # Stars drop one-by-one with ease_out_back — composite() now clamps alpha safely
            for i in range(rating):
                drop_start = i * 0.28
                a = fade_alpha(drop_start, 0.35, t, ease_out_back)
                drop_offset = int((1 - ease_out_back(min(max((t - drop_start) / 0.35, 0.0), 1.0))) * 80) if t > drop_start else 80
                base = composite(base, star_single, MARGIN + i * (sw + 4), star_y - drop_offset, a)

            # Star shimmer sweep at t=2.2 — semi-transparent white band crosses the star row
            if 2.2 < t < 2.6:
                sweep_p = (t - 2.2) / 0.4
                sweep_x = int(MARGIN + (rating * (sw + 4) + 60) * sweep_p)
                shimmer = np.zeros((80, 60, 4), dtype=np.uint8)
                shimmer[:, :, :3] = 255
                shimmer[:, :, 3] = 64   # α=25%
                base = composite(base, shimmer, sweep_x - 30, star_y - 20, 1.0)

            src_a   = fade_alpha(1.6, 0.5, t)
            quote_a = fade_alpha(2.4, 1.0, t)
            name_a  = fade_alpha(10.5, 0.7, t)
            badge_a = fade_alpha(11.5, 0.6, t)
            cta_a   = fade_alpha(12.5, 0.7, t)

            qy = star_y + 96
            base = composite(base, source_arr, MARGIN, qy, src_a)
            base = composite(base, quote_arr,  MARGIN, qy + source_arr.shape[0] + 12, quote_a)
            base = composite(base, name_arr,   MARGIN, qy + source_arr.shape[0] + 12 + quote_arr.shape[0] + 24, name_a)

            base = paint_scrim(base, H - 310, 260, alpha=0.55, feather=28)
            base = composite(base, badge_arr, MARGIN, H - 292, badge_a)

            # CTA slide-up: y offset 24→0 while fading in
            if cta_a > 0.0:
                cta_y_offset = int(24 * (1.0 - ease_out_cubic(min((t - 12.5) / 0.7, 1.0))))
                base = composite(base, cta_arr, MARGIN, H - 232 + cta_y_offset, cta_a)

            base = draw_logo(base, 36, 44, size=80, alpha=fade_alpha(0.5, 0.5, t))
            return base

        # End card (last 4s)
        pt = t - (duration - 4.0)
        a  = ease_out_cubic(min(pt / 0.8, 1.0))
        return np.clip(bg_arr.astype(np.float32) * (1 - a) + end_frame.astype(np.float32) * a, 0, 255).astype(np.uint8)

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

    shot_dur = max(0.5, (duration - 3.0) / len(shots))  # ~5.5s each, last 3s = end card
    prerendered = [(
        render_text_shadowed(h, "segoeuib.ttf", 30, (230,190,80), max_width=900, shadow_blur=3),
        render_text_shadowed(b, "georgiai.ttf", 48, WHITE,         max_width=952, line_spacing=14, shadow_blur=3) if b else None,
    ) for h, b in shots]
    cta_arr   = render_text_shadowed(cta_txt, "segoeuib.ttf", 32, (215,190,152), max_width=900, shadow_blur=3)
    end_frame = end_card_frame()

    # Ken Burns params per shot — varied direction/speed for visual rhythm
    KB_PARAMS = [
        (1.00, 1.07, (6,  -10)),   # shot 0: push in + drift up
        (1.07, 1.00, (-8,  0)),    # shot 1: pull out + drift left
        (1.00, 1.06, (0,  -14)),   # shot 2: vertical drift only
        (1.00, 1.09, (0,  -20)),   # shot 3: hardest push for the "for you" reveal
    ]
    DISSOLVE = 0.35   # seconds of cross-dissolve at each shot boundary

    def make_frame(t: float) -> np.ndarray:
        shot_idx = max(0, min(int(t / shot_dur), len(shots) - 1))
        shot_t   = t - shot_idx * shot_dur
        next_idx = min(shot_idx + 1, len(shots) - 1)

        def render_shot(idx: int, local_t: float) -> np.ndarray:
            zs, ze, drift = KB_PARAMS[idx % len(KB_PARAMS)]
            p = _pick(paths, idx)
            if p:
                src  = _load_src(str(p), REEL_SIZE)
                base = ken_burns_frame(src, local_t, shot_dur, zs, ze, drift=drift)
                base = warm_tint(base, 0.14)
                base = dark_gradient(base, int(H * 0.40), BLACK, 0.88)
            else:
                base = _solid((30, 20, 12))
            return base

        base = render_shot(shot_idx, shot_t)

        # Cross-dissolve in the last DISSOLVE seconds of each shot (except the final shot)
        if shot_t > (shot_dur - DISSOLVE) and shot_idx < len(shots) - 1:
            blend = ease_in_out_sine(min((shot_t - (shot_dur - DISSOLVE)) / DISSOLVE, 1.0))
            next_frame = render_shot(next_idx, 0.0)
            base = np.clip(
                base.astype(np.float32) * (1 - blend) + next_frame.astype(np.float32) * blend,
                0, 255,
            ).astype(np.uint8)

        base = top_vignette(base, 200, 0.48)
        base = draw_logo(base, 36, 44, size=80, alpha=0.85)

        header_arr, body_arr = prerendered[shot_idx]
        h_a    = fade_alpha(0.3, 0.5, shot_t)
        b_a    = fade_alpha(0.7, 0.6, shot_t) if body_arr is not None else 0.0
        text_y = int(H * 0.56)
        scrim_h = header_arr.shape[0] + (body_arr.shape[0] + 18 if body_arr is not None else 0) + 48
        base = paint_scrim(base, text_y - 20, scrim_h, alpha=0.54, feather=28)

        # Header slides in from left
        h_x = slide_in_x(header_arr, x_from=28, x_to=MARGIN, progress=(shot_t - 0.3) / 0.5 if shot_t > 0.3 else 0.0)
        base = composite(base, header_arr, h_x, text_y, h_a)
        if body_arr is not None:
            base = composite(base, body_arr, MARGIN, text_y + header_arr.shape[0] + 14, b_a)

        # CTA in final 7s
        if t > duration - 7.0:
            cta_a = fade_alpha(duration - 7.0, 1.0, t)
            base  = paint_scrim(base, H - 290, 260, alpha=0.52, feather=24)
            base  = composite(base, cta_arr, MARGIN, H - 268, cta_a)

        # End card
        if t > duration - 3.0:
            pt = t - (duration - 3.0)
            a  = ease_out_cubic(min(pt / 0.8, 1.0))
            base = np.clip(
                base.astype(np.float32) * (1 - a) + end_frame.astype(np.float32) * a,
                0, 255,
            ).astype(np.uint8)

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

    badge_arr = render_text_shadowed("30%",    "georgiab.ttf", 196, WHITE,         max_width=620, shadow_blur=10)
    off_arr   = render_text_shadowed("OFF" if lang == "en" else "DISKON",
                                      "segoeuib.ttf", 62, (230,190,80),  max_width=520, shadow_blur=4)
    h_arr     = render_text_shadowed(headline, "georgiab.ttf",  58, WHITE,         max_width=952, line_spacing=12, shadow_blur=4)
    s1_arr    = render_text_shadowed(sub1,     "georgiai.ttf",  42, (228,208,170), max_width=900, line_spacing=12, shadow_blur=3)
    s2_arr    = render_text_shadowed(sub2,     "segoeui.ttf",   34, (205,185,145), max_width=900, shadow_blur=3) if sub2 else None
    terms_arr = render_text_shadowed(terms_txt,"segoeuib.ttf",  36, (230,190,80),  max_width=900, shadow_blur=3)
    days_arr  = render_text_shadowed(days_left,"segoeuib.ttf",  32, WHITE,         max_width=600, shadow_blur=3) if days_left else None
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

    # Pre-load photo sources for optional ken-burns on background
    bg_src_arr = _load_src(str(paths[0]), REEL_SIZE) if paths else None

    def make_frame(t: float) -> np.ndarray:
        if t < 10.0:
            if bg_src_arr is not None:
                # Photo bg with teal color overlay for brand identity
                base = ken_burns_frame(bg_src_arr, t, 10.0, 1.0, 1.05, drift=(0, -8))
                base = np.clip(
                    base.astype(np.float32) * 0.38 + np.array(TEAL, dtype=np.float32) * 0.62,
                    0, 255
                ).astype(np.uint8)
            else:
                base = bg_base.copy()

            base = draw_logo(base, 36, 44, size=80, alpha=0.9)
            badge_y = int(H * 0.22) if t >= 3.0 else int(H * 0.28)

            # Phase A (0–3s): badge fades in
            if t < 3.0:
                alpha_a = ease_out_cubic(min(t / 0.65, 1.0))
                bx = int(W / 2 - badge_arr.shape[1] // 2)
                base = paint_scrim(base, badge_y - 20, badge_arr.shape[0] + off_arr.shape[0] + 40, alpha=0.30)
                base = composite(base, badge_arr, bx, badge_y, alpha_a)
                base = composite(base, off_arr,   int(W / 2 - off_arr.shape[1] // 2), badge_y + badge_arr.shape[0], alpha_a)

            # Phase B (3–7s): headline + terms slide in
            elif t < 7.0:
                pt  = t - 3.0
                bx  = int(W / 2 - badge_arr.shape[1] // 2)
                base = paint_scrim(base, badge_y - 16, badge_arr.shape[0] + off_arr.shape[0] + 32, alpha=0.32)
                base = composite(base, badge_arr, bx, badge_y, 1.0)
                base = composite(base, off_arr,   int(W / 2 - off_arr.shape[1] // 2), badge_y + badge_arr.shape[0], 1.0)
                h_a  = fade_alpha(0.2, 0.6, pt)
                s1_a = fade_alpha(0.7, 0.6, pt)
                s2_a = fade_alpha(1.3, 0.6, pt) if s2_arr is not None else 0.0
                ty   = int(H * 0.60)
                scrim_h = h_arr.shape[0] + s1_arr.shape[0] + (s2_arr.shape[0] + 16 if s2_arr is not None else 0) + 48
                base = paint_scrim(base, ty - 16, scrim_h, alpha=0.52, feather=24)
                base = composite(base, h_arr,  MARGIN, ty, h_a)
                base = composite(base, s1_arr, MARGIN, ty + h_arr.shape[0] + 12, s1_a)
                if s2_arr is not None:
                    base = composite(base, s2_arr, MARGIN, ty + h_arr.shape[0] + s1_arr.shape[0] + 20, s2_a)

            # Phase C (7–10s): countdown bar + CTA
            else:
                pt  = t - 7.0
                bx  = int(W / 2 - badge_arr.shape[1] // 2)
                base = paint_scrim(base, badge_y - 16, badge_arr.shape[0] + off_arr.shape[0] + 32, alpha=0.32)
                base = composite(base, badge_arr, bx, badge_y, 1.0)
                base = composite(base, off_arr,   int(W / 2 - off_arr.shape[1] // 2), badge_y + badge_arr.shape[0], 1.0)
                bar_w = W - MARGIN * 2
                bar_y = int(H * 0.65)
                fill  = max(0, int(bar_w * (1.0 - pt / 3.0)))
                base = paint_scrim(base, bar_y - 16, terms_arr.shape[0] + 100, alpha=0.54, feather=20)
                base[bar_y : bar_y + 12, MARGIN : MARGIN + bar_w] = np.array(GOLD)
                base[bar_y : bar_y + 12, MARGIN : MARGIN + fill]  = np.array(WHITE)
                t_a    = fade_alpha(0.3, 0.5, pt)
                days_a = fade_alpha(0.6, 0.5, pt) if days_arr is not None else 0.0
                base = composite(base, terms_arr, MARGIN, bar_y + 22, t_a)
                if days_arr is not None:
                    base = composite(base, days_arr, MARGIN, bar_y + 72, days_a)

            return base

        # End card (10–12s)
        pt = t - 10.0
        a  = ease_out_cubic(min(pt / 0.8, 1.0))
        return np.clip(bg_base.astype(np.float32) * (1 - a) + end_frame.astype(np.float32) * a, 0, 255).astype(np.uint8)

    return _make_clip(make_frame, duration, "r4")


# ─────────────────────────────────────────────────────────────────────────────
# R5 — Ambiance / Brand "The Exhale"  (15s, reach & saves)
# ─────────────────────────────────────────────────────────────────────────────

def build_r5(content: dict, lang: str = "id", photos: list = None, duration: float = 15.0) -> VideoClip:
    photos = photos or []
    paths  = _photo_paths(photos)

    if lang == "id":
        line1, line2 = "Tarik napas.", "Hembuskan."
        line3 = "Djaya Massage  ·  Penuin Centre, Batam"
        line4 = "Buka 10.00 – 22.00  ·  wa.me/6285278355590"
    else:
        line1, line2 = "Breathe in.", "Let go."
        line3 = "Djaya Massage  ·  Penuin Centre, Batam"
        line4 = "Open 10 AM – 10 PM  ·  wa.me/6285278355590"

    l1_arr = render_text_shadowed(line1, "georgiai.ttf", 84, WHITE,          max_width=952, shadow_blur=5)
    l2_arr = render_text_shadowed(line2, "georgiai.ttf", 84, (232,210,170),  max_width=952, shadow_blur=5)
    # End-card text on CREAM background — use INK/brown, NO shadow (looks dirty on cream)
    l3_arr = render_text_block(line3, "segoeuib.ttf", 30, (52,38,24),   max_width=952)
    l4_arr = render_text_block(line4, "segoeui.ttf",  28, (120,96,68),  max_width=952)
    end_frame = end_card_frame()

    LB_H = 100  # cinematic letterbox height each side

    def make_frame(t: float) -> np.ndarray:
        if t < 13.0:
            p0 = _pick(paths, 0)
            p1 = _pick(paths, 1) or p0
            p2 = _pick(paths, 2) or p0

            if p0:
                s0 = _load_src(str(p0), REEL_SIZE)
                f0 = ken_burns_frame(s0, t, 6.5, 1.0, 1.06, drift=(0, -18))
                f0 = warm_tint(f0, 0.14)
            else:
                f0 = _solid((20, 14, 8))

            # Cross-dissolve to photo 2 at 6s
            if t > 5.5 and p1 and str(p1) != str(p0):
                s1    = _load_src(str(p1), REEL_SIZE)
                blend = ease_in_out_sine(min((t - 5.5) / 1.2, 1.0))
                f1    = ken_burns_frame(s1, t - 5.5, 6.5, 1.06, 1.0, drift=(10, 0))
                f1    = warm_tint(f1, 0.16)
                base  = np.clip(f0.astype(np.float32) * (1 - blend) + f1.astype(np.float32) * blend, 0, 255).astype(np.uint8)
            else:
                base = f0

            # Cinematic tint — dark but not crushing
            base = dark_gradient(base, 0, BLACK, 0.50)
            base = top_vignette(base, 240, 0.42)

            # Letterbox
            base[:LB_H]  = np.array(BLACK)
            base[-LB_H:] = np.array(BLACK)

            # Centre text with scrim
            cy = H // 2 - 80
            l1_a = fade_alpha(4.5, 1.0, t) * (1 - fade_alpha(8.0, 0.8, t))
            l2_a = fade_alpha(8.0, 1.0, t) * (1 - fade_alpha(11.5, 0.8, t))
            if l1_a > 0.01 or l2_a > 0.01:
                base = paint_scrim(base, cy - 20, 90 + max(l1_arr.shape[0], l2_arr.shape[0]) + 40, alpha=0.42, feather=36)
            base = composite(base, l1_arr, MARGIN, cy, l1_a)
            base = composite(base, l2_arr, MARGIN, cy + 90, l2_a)
            base = draw_logo(base, 36, LB_H + 12, size=80, alpha=fade_alpha(0.5, 0.8, t))
            return base

        # End card (13–15s) with CTA lines
        pt    = t - 13.0
        a     = ease_out_cubic(min(pt / 0.8, 1.0))
        frame = np.clip(
            _solid(BLACK).astype(np.float32) * (1 - a) + end_frame.astype(np.float32) * a,
            0, 255,
        ).astype(np.uint8)
        l3_a = fade_alpha(13.4, 0.6, t)
        l4_a = fade_alpha(13.7, 0.6, t)
        frame = composite(frame, l3_arr, MARGIN, int(H * 0.52) + 50, l3_a)
        frame = composite(frame, l4_arr, MARGIN, int(H * 0.52) + 50 + l3_arr.shape[0] + 16, l4_a)
        return frame

    return _make_clip(make_frame, duration, "r5")
