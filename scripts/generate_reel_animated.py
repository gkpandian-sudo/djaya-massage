#!/usr/bin/env python3
"""
generate_reel_animated.py — render animated Instagram reels (1080×1920 MP4).

Usage:
  python scripts/generate_reel_animated.py --template r2 --lang id
  python scripts/generate_reel_animated.py --template r1 --lang en --duration-scale 0.2 --fps 6  # fast preview
  python scripts/generate_reel_animated.py --template r5 --post-type ambiance

Post-type to template mapping:
  service_spotlight / signature → r1
  testimonial                   → r2
  ambiance (BTS)                → r3
  promo / booking_reminder      → r4
  location / brand              → r5
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import content as DATA
import content_rotation as ROT
from reel_templates import build_r1, build_r2, build_r3, build_r4, build_r5

_ALL = DATA.ALL_PHOTOS  # 15 real photos — rotated across templates

REPO_ROOT     = Path(__file__).resolve().parent.parent
OUTPUT_DIR    = REPO_ROOT / "output" / "reels-animated"
ROTATION_PATH = str(REPO_ROOT / "data" / "rotation.json")

POST_TYPE_TO_TEMPLATE = {
    "service_spotlight":  "r1",
    "signature":          "r1",
    "testimonial":        "r2",
    "ambiance":           "r3",
    "promo":              "r4",
    "booking_reminder":   "r4",
    "location":           "r5",
}

# Duration and audio mood per template (full quality)
TEMPLATE_DEFAULTS = {
    "r1": {"duration": 22.0, "mood": "r1"},
    "r2": {"duration": 18.0, "mood": "r2"},
    "r3": {"duration": 25.0, "mood": "r3"},
    "r4": {"duration": 12.0, "mood": "r4"},
    "r5": {"duration": 15.0, "mood": "r5"},
}


def _build_content_dict(template: str, lang: str) -> dict:
    """Build the content dict expected by each template builder."""
    treatments = list(DATA.all_treatments())
    menu_idx   = ROT.get_menu_index(ROTATION_PATH)
    test_idx   = ROT.get_testimonial_index(ROTATION_PATH)

    if template in ("r1",):
        t = treatments[menu_idx % len(treatments)]
        return {
            "treatment": {
                "name":     t["name"],
                "category": t["category"],
                "desc":     t["desc"],
                "prices":   t["prices"],
                "photo":    t.get("photo", ""),
            }
        }
    elif template == "r2":
        r = DATA.REVIEWS[test_idx % len(DATA.REVIEWS)]
        return {"review": r}
    elif template == "r3":
        return {}
    elif template == "r4":
        return {"promo": DATA.PROMO}
    elif template == "r5":
        return {
            "business": {
                "name":    DATA.BUSINESS["name"],
                "hours":   DATA.BUSINESS["hours"],
                "address": DATA.BUSINESS["address_short"],
            }
        }
    return {}


def _photo_list(template: str, post_type: str, menu_idx: int = 0, test_idx: int = 0) -> list[str]:
    """Rotate through ALL_PHOTOS so each day's reel shows different images."""
    N = len(_ALL)

    if template == "r1":
        # 3 photos: treatment-specific photo first, then 2 adjacent rotated shots
        t_data = _build_content_dict("r1", "id").get("treatment", {})
        t_photo = t_data.get("photo", "")  # e.g. "gallery-3.jpg"
        base = menu_idx % N
        pool = [t_photo] if t_photo else []
        for i in range(1, N):
            cand = _ALL[(base + i) % N]
            if cand not in pool:
                pool.append(cand)
            if len(pool) >= 3:
                break
        return pool

    elif template == "r2":
        # 2 photos rotating per testimonial index
        base = test_idx % N
        return [_ALL[base], _ALL[(base + 5) % N]]

    elif template == "r3":
        # 4–6 photos starting at a different offset each day
        base = (menu_idx * 3) % N
        return [_ALL[(base + i) % N] for i in range(6)]

    elif template == "r4":
        # Hero + 2 treatment photos for promo urgency
        return ["Hero.jpeg", "treatment-14.jpeg", "treatment-15.jpeg"]

    elif template == "r5":
        # 3 photos: hero + 2 rotating gallery shots for cinematic ambiance
        base = (menu_idx + 2) % N
        return ["Hero.jpeg", _ALL[base], _ALL[(base + 4) % N]]

    return [_ALL[menu_idx % N]]


def render(
    template: str,
    lang: str = "id",
    out_dir: Path = OUTPUT_DIR,
    date_str: str = None,
    duration_scale: float = 1.0,
    fps: int = 30,
    post_type: str = "",
) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str  = date_str or date.today().isoformat()
    label     = post_type or template
    out_path  = str(out_dir / f"{date_str}-{label}.mp4")

    cfg        = TEMPLATE_DEFAULTS[template]
    duration   = cfg["duration"] * duration_scale
    content    = _build_content_dict(template, lang)
    menu_idx   = ROT.get_menu_index(ROTATION_PATH)
    test_idx   = ROT.get_testimonial_index(ROTATION_PATH)
    photos     = _photo_list(template, post_type, menu_idx, test_idx)

    print(f"[djaya-animated] template={template} lang={lang} fps={fps} duration={duration:.1f}s -> {out_path}")

    builders = {"r1": build_r1, "r2": build_r2, "r3": build_r3, "r4": build_r4, "r5": build_r5}
    clip = builders[template](content, lang, photos, duration)

    clip.write_videofile(
        out_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="128k",
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        preset="medium",
        threads=2,
        logger=None,
    )
    print(f"[djaya-animated] saved: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template",       choices=["r1","r2","r3","r4","r5"], default=None)
    parser.add_argument("--post-type",      default="")
    parser.add_argument("--lang",           choices=["id","en"], default="id")
    parser.add_argument("--date",           default=None)
    parser.add_argument("--out-dir",        default=str(OUTPUT_DIR))
    parser.add_argument("--fps",            type=int,   default=30)
    parser.add_argument("--duration-scale", type=float, default=1.0,
                        help="Scale duration (0.1 = fast preview)")
    args = parser.parse_args()

    template = args.template
    if not template:
        if args.post_type and args.post_type in POST_TYPE_TO_TEMPLATE:
            template = POST_TYPE_TO_TEMPLATE[args.post_type]
        else:
            parser.error("Provide --template r1..r5 or a valid --post-type")

    render(
        template    = template,
        lang        = args.lang,
        out_dir     = Path(args.out_dir),
        date_str    = args.date,
        duration_scale = args.duration_scale,
        fps         = args.fps,
        post_type   = args.post_type or template,
    )


if __name__ == "__main__":
    main()
