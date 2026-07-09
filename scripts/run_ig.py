#!/usr/bin/env python3
"""
run_ig.py — Instagram publish pipeline entry point.

Env vars:
  POST_TYPE         Override weekday schedule (e.g. service_spotlight)
  DRY_RUN           true = render only, skip commit + publish
  CAPTION_LANG      id (default) or en
  IG_USER_ID        Instagram Business Account numeric ID
  META_ACCESS_TOKEN Long-lived Page access token
  GITHUB_REPOSITORY Set automatically by GitHub Actions runner
  GITHUB_REF_NAME   Set automatically by GitHub Actions runner

Usage:
  python scripts/run_ig.py
  DRY_RUN=true POST_TYPE=promo python scripts/run_ig.py
"""
from __future__ import annotations
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import captions as C
import content as DATA
import content_rotation as ROT
import generate_post as GP
import post as META

REPO_ROOT = Path(__file__).resolve().parent.parent
ROTATION_PATH = str(REPO_ROOT / "data" / "rotation.json")

CDN_BASE = (
    "https://raw.githubusercontent.com"
    f"/{os.environ.get('GITHUB_REPOSITORY', '')}"
    f"/{os.environ.get('GITHUB_REF_NAME', 'main')}"
)

IG_USER_ID       = os.environ.get("IG_USER_ID", "")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
DRY_RUN          = os.environ.get("DRY_RUN", "false").lower() == "true"
LANG             = os.environ.get("CAPTION_LANG", "id")

_VALID_TYPES = set(ROT.WEEKDAY_TO_POST_TYPE.values())


def resolve_post_type() -> str:
    override = os.environ.get("POST_TYPE", "").strip()
    if override and override in _VALID_TYPES:
        return override
    entry = ROT.get_schedule_entry(ROTATION_PATH)
    return entry["template"]


def _all_treatments() -> list:
    return list(DATA.all_treatments())


def _commit_and_push_image(img_path: str) -> str:
    rel = Path(img_path).relative_to(REPO_ROOT)
    rel_posix = str(rel).replace(os.sep, "/")
    subprocess.run(
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "add", str(rel)], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: add post image {Path(img_path).name} [skip ci]"],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)
    cdn_url = f"{CDN_BASE}/{rel_posix}"
    print(f"Image pushed. CDN URL: {cdn_url}")
    return cdn_url


def _wait_for_cdn(cdn_url: str, timeout: int = 60) -> None:
    import requests as _req
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = _req.head(cdn_url, timeout=5)
            if r.status_code == 200:
                print(f"CDN ready: {cdn_url}")
                return
        except Exception:
            pass
        time.sleep(5)
    raise TimeoutError(f"CDN URL not reachable after {timeout}s: {cdn_url}")


def run() -> None:
    post_type = resolve_post_type()
    print(f"[djaya-ig] post_type={post_type}  dry_run={DRY_RUN}  lang={LANG}")

    treatments = _all_treatments()
    menu_idx   = ROT.get_menu_index(ROTATION_PATH)
    test_idx   = ROT.get_testimonial_index(ROTATION_PATH)

    advance_menu = False
    advance_testimonial = False

    if post_type == "service_spotlight":
        t = treatments[menu_idx % len(treatments)]
        img_path = GP.render_treatment(t)
        caption  = C.service_spotlight(t, lang=LANG)
        advance_menu = True

    elif post_type == "signature":
        t = DATA.TREATMENTS["signature"][0]
        img_path = GP.render_signature()
        caption  = C.signature(t, lang=LANG)

    elif post_type == "testimonial":
        review   = DATA.REVIEWS[test_idx % len(DATA.REVIEWS)]
        img_path = GP.render_testimonial(review, DATA.GALLERY_PHOTOS[test_idx % len(DATA.GALLERY_PHOTOS)], test_idx)
        caption  = C.testimonial(review, lang=LANG)
        advance_testimonial = True

    elif post_type == "promo":
        img_path = GP.render_promo()
        caption  = C.promo(DATA.PROMO, lang=LANG)

    elif post_type == "ambiance":
        photo = DATA.GALLERY_PHOTOS[menu_idx % len(DATA.GALLERY_PHOTOS)]
        img_path = GP.render_ambiance(photo, menu_idx % len(DATA.GALLERY_PHOTOS))
        caption  = C.ambiance(lang=LANG)

    elif post_type == "location":
        img_path = GP.render_location()
        caption  = C.location(DATA.BUSINESS, lang=LANG)

    elif post_type == "booking_reminder":
        img_path = GP.render_booking_reminder()
        caption  = C.booking_reminder(DATA.BUSINESS, lang=LANG)

    else:
        raise ValueError(f"Unknown post_type: {post_type!r}")

    print(f"[djaya-ig] rendered:        {img_path}")
    preview = caption[:140].encode("ascii", errors="replace").decode("ascii")
    print(f"[djaya-ig] caption preview: {preview}...")

    if DRY_RUN:
        print("[djaya-ig] DRY_RUN=true — skipping commit and publish.")
        return

    cdn_url = _commit_and_push_image(img_path)

    ROT.increment_rotation(
        ROTATION_PATH,
        menu_count=len(treatments),
        testimonial_count=len(DATA.REVIEWS),
        menu=advance_menu,
        testimonial=advance_testimonial,
    )
    ROT.commit_rotation(ROTATION_PATH)

    _wait_for_cdn(cdn_url)

    media_id = META.publish_image(cdn_url, caption, IG_USER_ID, META_ACCESS_TOKEN)
    print(f"[djaya-ig] published!  media_id={media_id}")


if __name__ == "__main__":
    run()
