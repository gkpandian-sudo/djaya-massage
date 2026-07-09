# content_rotation.py — 4-week content rotation system
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROTATION_PATH = str(REPO_ROOT / "data" / "rotation.json")

# ── 4-week calendar ───────────────────────────────────────────────────────────
# Each entry: (content_type, template_or_post_type, lang, photo_hint)
# content_type: "image" | "reel"
# template:     r1..r5 for reels; post_type string for images
# lang:         "id" | "en"
# photo_hint:   primary photo filename

ROTATION_CALENDAR = [
    # Week 0 — "Fundamentals"
    [  # Mon Tue Wed Thu Fri Sat Sun
        ("image", "service_spotlight", "id", "treatment-10.jpg"),
        ("reel",  "r2",               "id", "gallery-2.jpg"),
        ("image", "ambiance",          "id", "gallery-4.jpg"),
        ("reel",  "r1",               "en", "treatment-11.jpeg"),
        ("image", "location",          "en", "Hero.jpeg"),
        ("image", "booking_reminder",  "en", "gallery-3.jpg"),
        ("reel",  "r5",               "id", "gallery-6.jpg"),
    ],
    # Week 1 — "Proof & Promo"
    [
        ("image", "service_spotlight", "id", "treatment-12.jpeg"),
        ("reel",  "r3",               "id", "gallery-1.jpg"),
        ("image", "testimonial",       "id", "gallery-5.jpg"),
        ("reel",  "r1",               "en", "treatment-10.jpg"),
        ("image", "signature",         "en", "signature.jpg"),
        ("image", "ambiance",          "en", "Hero.jpeg"),
        ("reel",  "r4",               "id", "gallery-3.jpg"),
    ],
    # Week 2 — "Premium"
    [
        ("image", "service_spotlight", "id", "treatment-14.jpeg"),
        ("reel",  "r2",               "en", "gallery-6.jpg"),
        ("image", "promo",             "id", "treatment-15.jpeg"),
        ("reel",  "r1",               "en", "treatment-15.jpeg"),
        ("image", "location",          "en", "about.jpg"),
        ("image", "booking_reminder",  "en", "gallery-2.jpg"),
        ("reel",  "r5",               "en", "gallery-5.jpg"),
    ],
    # Week 3 — "Signature & Reset"
    [
        ("reel",  "r1",               "id", "signature.jpg"),
        ("image", "testimonial",       "id", "gallery-1.jpg"),
        ("image", "service_spotlight", "id", "treatment-11.jpeg"),
        ("image", "signature",         "en", "gallery-4.jpg"),
        ("reel",  "r4",               "en", "treatment-10.jpg"),
        ("image", "ambiance",          "en", "gallery-5.jpg"),
        ("reel",  "r3",               "id", "gallery-6.jpg"),
    ],
]

# Kept for backward compatibility with image pipeline
WEEKDAY_TO_POST_TYPE = {
    0: "service_spotlight",
    1: "signature",
    2: "testimonial",
    3: "promo",
    4: "ambiance",
    5: "location",
    6: "booking_reminder",
}


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def get_menu_index(rotation_path: str = DEFAULT_ROTATION_PATH) -> int:
    return _load(rotation_path).get("menu_index", 0)


def get_testimonial_index(rotation_path: str = DEFAULT_ROTATION_PATH) -> int:
    return _load(rotation_path).get("testimonial_index", 0)


def get_week_index(rotation_path: str = DEFAULT_ROTATION_PATH) -> int:
    return _load(rotation_path).get("week_index", 0)


def get_schedule_entry(rotation_path: str = DEFAULT_ROTATION_PATH, weekday: int = None) -> dict:
    """Return today's schedule entry from the 4-week calendar."""
    if weekday is None:
        weekday = datetime.now(timezone.utc).weekday()
    week = get_week_index(rotation_path) % 4
    ct, tpl, lang, photo = ROTATION_CALENDAR[week][weekday]
    return {"content_type": ct, "template": tpl, "lang": lang, "photo_hint": photo}


def increment_rotation(
    rotation_path: str,
    menu_count: int = 0,
    testimonial_count: int = 0,
    menu: bool = False,
    testimonial: bool = False,
) -> None:
    data = _load(rotation_path)
    if menu and menu_count > 0:
        data["menu_index"] = (data.get("menu_index", 0) + 1) % menu_count
    if testimonial and testimonial_count > 0:
        data["testimonial_index"] = (data.get("testimonial_index", 0) + 1) % testimonial_count
    _save(rotation_path, data)


def increment_week(rotation_path: str = DEFAULT_ROTATION_PATH) -> None:
    """Call once every Sunday after posting to advance to the next week."""
    data = _load(rotation_path)
    data["week_index"] = (data.get("week_index", 0) + 1) % 4
    _save(rotation_path, data)


def commit_rotation(rotation_path: str) -> None:
    subprocess.run(
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "add", rotation_path], check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode == 0:
        print("No rotation change to commit.")
        return
    subprocess.run(
        ["git", "commit", "-m", "chore: rotate content index [skip ci]"],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)
