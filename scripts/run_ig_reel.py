#!/usr/bin/env python3
"""
run_ig_reel.py — Animated reel publish pipeline.

Env vars:
  REEL_TEMPLATE      Override template (r1..r5). Default: auto from weekday.
  DRY_RUN            true = render only, skip commit and publish.
  CAPTION_LANG       id (default) or en.
  IG_USER_ID         Instagram Business Account numeric ID.
  META_ACCESS_TOKEN  Long-lived Page access token.
  GITHUB_REPOSITORY  Set automatically by GitHub Actions runner.
  GITHUB_REF_NAME    Set automatically by GitHub Actions runner.

Weekday → template schedule:
  Tue (1) → r2 Testimonial
  Thu (3) → r1 Treatment Showcase
  Sun (6) → r5 Ambiance

Usage:
  python scripts/run_ig_reel.py
  DRY_RUN=true REEL_TEMPLATE=r2 python scripts/run_ig_reel.py
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
import generate_reel_animated as GRA
import post as META

REPO_ROOT = Path(__file__).resolve().parent.parent
ROTATION_PATH = str(REPO_ROOT / "data" / "rotation.json")

CDN_BASE = (
    "https://raw.githubusercontent.com"
    f"/{os.environ.get('GITHUB_REPOSITORY', '')}"
    f"/{os.environ.get('GITHUB_REF_NAME', 'main')}"
)

IG_USER_ID        = os.environ.get("IG_USER_ID", "")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
DRY_RUN           = os.environ.get("DRY_RUN", "false").lower() == "true"
LANG              = os.environ.get("CAPTION_LANG", "id")

# Tue/Thu/Sun reel schedule
WEEKDAY_TO_TEMPLATE = {
    1: "r2",   # Tuesday  → Testimonial
    3: "r1",   # Thursday → Treatment Showcase
    6: "r5",   # Sunday   → Ambiance
}

# Caption generator per template/post-type
TEMPLATE_TO_POST_TYPE = {
    "r1": "service_spotlight",
    "r2": "testimonial",
    "r3": "ambiance",
    "r4": "promo",
    "r5": "ambiance",
}


def resolve_template() -> str:
    override = os.environ.get("REEL_TEMPLATE", "").strip()
    if override and override in GRA.TEMPLATE_DEFAULTS:
        return override
    entry = ROT.get_schedule_entry(ROTATION_PATH)
    return entry.get("template", "r5")


def _build_caption(template: str) -> str:
    post_type = TEMPLATE_TO_POST_TYPE.get(template, "ambiance")
    menu_idx  = ROT.get_menu_index(ROTATION_PATH)
    test_idx  = ROT.get_testimonial_index(ROTATION_PATH)
    treatments = list(DATA.all_treatments())

    if post_type == "service_spotlight":
        t = treatments[menu_idx % len(treatments)]
        return C.service_spotlight(t, lang=LANG)
    elif post_type == "testimonial":
        review = DATA.REVIEWS[test_idx % len(DATA.REVIEWS)]
        return C.testimonial(review, lang=LANG)
    elif post_type == "promo":
        return C.promo(DATA.PROMO, lang=LANG)
    else:
        return C.ambiance(lang=LANG)


def _commit_and_push_reel(reel_path: str) -> str:
    rel = Path(reel_path).relative_to(REPO_ROOT)
    rel_posix = str(rel).replace(os.sep, "/")
    subprocess.run(
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "add", str(rel)], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: add reel {Path(reel_path).name} [skip ci]"],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)
    cdn_url = f"{CDN_BASE}/{rel_posix}"
    print(f"Reel pushed. CDN URL: {cdn_url}")
    return cdn_url


def _wait_for_cdn(cdn_url: str, timeout: int = 120) -> None:
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
    template  = resolve_template()
    post_type = TEMPLATE_TO_POST_TYPE.get(template, "ambiance")
    print(f"[djaya-reel] template={template} post_type={post_type} dry_run={DRY_RUN} lang={LANG}")

    reel_path = GRA.render(
        template=template,
        lang=LANG,
        post_type=post_type,
    )
    caption = _build_caption(template)

    preview = caption[:140].encode("ascii", errors="replace").decode("ascii")
    print(f"[djaya-reel] rendered:        {reel_path}")
    print(f"[djaya-reel] caption preview: {preview}...")

    if DRY_RUN:
        print("[djaya-reel] DRY_RUN=true — skipping commit and publish.")
        return

    cdn_url = _commit_and_push_reel(reel_path)

    # Advance rotation indices same as image pipeline
    treatments = list(DATA.all_treatments())
    ROT.increment_rotation(
        ROTATION_PATH,
        menu_count=len(treatments),
        testimonial_count=len(DATA.REVIEWS),
        menu=(template == "r1"),
        testimonial=(template == "r2"),
    )
    ROT.commit_rotation(ROTATION_PATH)

    # Advance week index every Sunday
    if datetime.now(timezone.utc).weekday() == 6:
        ROT.increment_week(ROTATION_PATH)
        ROT.commit_rotation(ROTATION_PATH)

    _wait_for_cdn(cdn_url, timeout=120)

    media_id = META.publish_reel(cdn_url, caption, IG_USER_ID, META_ACCESS_TOKEN)
    print(f"[djaya-reel] published!  media_id={media_id}")


if __name__ == "__main__":
    run()
