import json
import pytest
import content_rotation as ROT


def _write_rotation(tmp_path, menu_index=0, testimonial_index=0) -> str:
    path = tmp_path / "rotation.json"
    path.write_text(json.dumps({"menu_index": menu_index, "testimonial_index": testimonial_index}))
    return str(path)


# --- weekday map ---

def test_weekday_map_covers_all_seven_days():
    assert set(ROT.WEEKDAY_TO_POST_TYPE.keys()) == set(range(7))


def test_weekday_map_values_are_known_post_types():
    valid = {
        "service_spotlight", "signature", "testimonial",
        "promo", "ambiance", "location", "booking_reminder",
    }
    assert set(ROT.WEEKDAY_TO_POST_TYPE.values()) == valid


# --- get_menu_index / get_testimonial_index ---

def test_get_menu_index_reads_value(tmp_path):
    p = _write_rotation(tmp_path, menu_index=3)
    assert ROT.get_menu_index(p) == 3


def test_get_testimonial_index_reads_value(tmp_path):
    p = _write_rotation(tmp_path, testimonial_index=2)
    assert ROT.get_testimonial_index(p) == 2


# --- increment_rotation ---

def test_increment_rotation_advances_menu(tmp_path):
    p = _write_rotation(tmp_path, menu_index=0)
    ROT.increment_rotation(p, menu_count=5, menu=True)
    assert json.loads(open(p).read())["menu_index"] == 1


def test_increment_rotation_wraps_menu_at_end(tmp_path):
    p = _write_rotation(tmp_path, menu_index=4)
    ROT.increment_rotation(p, menu_count=5, menu=True)
    assert json.loads(open(p).read())["menu_index"] == 0


def test_increment_rotation_advances_testimonial(tmp_path):
    p = _write_rotation(tmp_path, testimonial_index=1)
    ROT.increment_rotation(p, testimonial_count=3, testimonial=True)
    assert json.loads(open(p).read())["testimonial_index"] == 2


def test_increment_rotation_wraps_testimonial_at_end(tmp_path):
    p = _write_rotation(tmp_path, testimonial_index=2)
    ROT.increment_rotation(p, testimonial_count=3, testimonial=True)
    assert json.loads(open(p).read())["testimonial_index"] == 0


def test_increment_rotation_neither_flag_is_noop(tmp_path):
    p = _write_rotation(tmp_path, menu_index=1, testimonial_index=1)
    ROT.increment_rotation(p, menu_count=5, testimonial_count=3)
    data = json.loads(open(p).read())
    assert data["menu_index"] == 1
    assert data["testimonial_index"] == 1


def test_increment_rotation_does_not_touch_menu_when_only_testimonial(tmp_path):
    p = _write_rotation(tmp_path, menu_index=2, testimonial_index=0)
    ROT.increment_rotation(p, menu_count=5, testimonial_count=3, testimonial=True)
    data = json.loads(open(p).read())
    assert data["menu_index"] == 2
    assert data["testimonial_index"] == 1
