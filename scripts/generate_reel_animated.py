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


def _photo_list(template: str, post_type: str) -> list[str]:
    """Choose the best photos for a given template."""
    gallery = DATA.GALLERY_PHOTOS
    if template == "r1":
        return gallery[:3]
    elif template == "r2":
        return gallery[:2]
    elif template == "r3":
        return gallery  # cycle through all
    elif template == "r4":
        return [DATA.HERO_PHOTO]
    elif template == "r5":
        return gallery[:2]
    return gallery[:2]


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

    cfg      = TEMPLATE_DEFAULTS[template]
    duration = cfg["duration"] * duration_scale
    content  = _build_content_dict(template, lang)
    photos   = _photo_list(template, post_type)

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
