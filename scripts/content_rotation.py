# content_rotation.py — rotation index management + weekday→post-type map
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROTATION_PATH = str(REPO_ROOT / "data" / "rotation.json")

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
    return _load(rotation_path)["menu_index"]


def get_testimonial_index(rotation_path: str = DEFAULT_ROTATION_PATH) -> int:
    return _load(rotation_path)["testimonial_index"]


def increment_rotation(
    rotation_path: str,
    menu_count: int = 0,
    testimonial_count: int = 0,
    menu: bool = False,
    testimonial: bool = False,
) -> None:
    data = _load(rotation_path)
    if menu and menu_count > 0:
        data["menu_index"] = (data["menu_index"] + 1) % menu_count
    if testimonial and testimonial_count > 0:
        data["testimonial_index"] = (data["testimonial_index"] + 1) % testimonial_count
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
