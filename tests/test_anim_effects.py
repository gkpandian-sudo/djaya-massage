"""Tests for anim_effects.py — easing math, ken_burns geometry, compositing."""
import math
import numpy as np
import pytest
import anim_effects as A


# ── Easing ────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("fn", [A.ease_out_cubic, A.ease_in_out_sine, A.linear])
def test_easing_boundary_zero(fn):
    assert fn(0.0) == pytest.approx(0.0, abs=1e-6)

@pytest.mark.parametrize("fn", [A.ease_out_cubic, A.ease_in_out_sine, A.linear])
def test_easing_boundary_one(fn):
    assert fn(1.0) == pytest.approx(1.0, abs=1e-6)

@pytest.mark.parametrize("fn", [A.ease_out_cubic, A.ease_in_out_sine, A.linear])
def test_easing_monotonic(fn):
    vals = [fn(t/10) for t in range(11)]
    for a, b in zip(vals, vals[1:]):
        assert b >= a - 1e-9

@pytest.mark.parametrize("fn", [A.ease_out_cubic, A.ease_in_out_sine, A.ease_out_back, A.linear])
def test_easing_clamps_below_zero(fn):
    assert fn(-0.5) >= 0.0

@pytest.mark.parametrize("fn", [A.ease_out_cubic, A.ease_in_out_sine, A.linear])
def test_easing_clamps_above_one(fn):
    assert fn(1.5) <= 1.0 + 1e-6


# ── fade_alpha ────────────────────────────────────────────────────────────────

def test_fade_alpha_zero_before_start():
    assert A.fade_alpha(2.0, 1.0, 1.0) == pytest.approx(0.0)

def test_fade_alpha_one_after_dur():
    assert A.fade_alpha(2.0, 1.0, 5.0) == pytest.approx(1.0, abs=1e-6)

def test_fade_alpha_partial():
    v = A.fade_alpha(0.0, 2.0, 1.0)
    assert 0.0 < v < 1.0


# ── Ken Burns ─────────────────────────────────────────────────────────────────

@pytest.fixture
def fake_src():
    """180×320 source image (small but covers 1080×1920 after _load_src resize)."""
    return np.random.randint(0, 255, (400, 230, 3), dtype=np.uint8)

def test_ken_burns_frame_output_shape(fake_src):
    frame = A.ken_burns_frame(fake_src, t=0.0, duration=8.0, size=(108, 192))
    assert frame.shape == (192, 108, 3)

def test_ken_burns_frame_dtype(fake_src):
    frame = A.ken_burns_frame(fake_src, t=0.0, duration=8.0, size=(108, 192))
    assert frame.dtype == np.uint8

def test_ken_burns_frame_valid_at_start(fake_src):
    frame = A.ken_burns_frame(fake_src, t=0.0, duration=8.0, size=(108, 192))
    assert frame.min() >= 0 and frame.max() <= 255

def test_ken_burns_frame_valid_at_end(fake_src):
    frame = A.ken_burns_frame(fake_src, t=8.0, duration=8.0, size=(108, 192))
    assert frame.min() >= 0 and frame.max() <= 255

def test_ken_burns_stays_in_source_bounds(fake_src):
    for t in [0.0, 2.0, 4.0, 8.0]:
        frame = A.ken_burns_frame(fake_src, t=t, duration=8.0, zoom_start=1.0, zoom_end=1.08, size=(108, 192))
        assert frame.shape == (192, 108, 3)


# ── Compositing ───────────────────────────────────────────────────────────────

def test_composite_full_alpha_overwrites():
    base = np.zeros((10, 10, 3), dtype=np.uint8)
    # RGBA: RGB=200, A=255 → fully opaque overlay
    overlay = np.ones((4, 4, 4), dtype=np.uint8) * 255
    overlay[:,:,:3] = 200
    result = A.composite(base, overlay, 0, 0, alpha=1.0)
    assert result[1, 1, 0] == pytest.approx(200, abs=2)

def test_composite_zero_alpha_leaves_base():
    base = np.full((10, 10, 3), 100, dtype=np.uint8)
    overlay = np.full((4, 4, 4), 255, dtype=np.uint8)
    result = A.composite(base, overlay, 0, 0, alpha=0.0)
    assert result[1, 1, 0] == 100

def test_composite_out_of_bounds_safe():
    base = np.zeros((10, 10, 3), dtype=np.uint8)
    overlay = np.ones((4, 4, 4), dtype=np.uint8) * 200
    result = A.composite(base, overlay, 8, 8, alpha=1.0)  # mostly out of bounds
    assert result.shape == (10, 10, 3)


# ── Text rendering ────────────────────────────────────────────────────────────

def test_render_text_block_returns_rgba():
    arr = A.render_text_block("Hello", "segoeui.ttf", 24, A.WHITE, max_width=300)
    assert arr.ndim == 3
    assert arr.shape[2] == 4

def test_render_text_block_has_nonzero_alpha():
    arr = A.render_text_block("Hello", "segoeui.ttf", 24, A.WHITE, max_width=300)
    assert arr[:,:,3].max() > 0

def test_render_stars_count_five():
    arr = A.render_stars(5, size=40)
    assert arr.ndim == 3 and arr.shape[2] == 4


def test_composite_alpha_gt1_clamped():
    """ease_out_back can return >1.0; composite must not go negative."""
    base = np.full((10, 10, 3), 100, dtype=np.uint8)
    overlay = np.full((4, 4, 4), 255, dtype=np.uint8)
    overlay[:, :, :3] = 200
    result = A.composite(base, overlay, 0, 0, alpha=1.15)
    assert result.min() >= 0, "composite should not produce negative values with alpha>1"
    assert result[1, 1, 0] == 200, "composite with alpha>1 should still yield full overlay"

def test_composite_alpha_negative_safe():
    base = np.full((10, 10, 3), 100, dtype=np.uint8)
    overlay = np.full((4, 4, 4), 255, dtype=np.uint8)
    result = A.composite(base, overlay, 0, 0, alpha=-0.1)
    assert (result == 100).all(), "negative alpha should preserve base"


# ── New primitives (Task 2) ───────────────────────────────────────────────────

def test_line_wipe_output_shape():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = A.line_wipe(frame, x=10, y=50, h=6, w_final=80, progress=0.5)
    assert result.shape == (100, 100, 3)

def test_line_wipe_partial_draws_gold():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = A.line_wipe(frame, x=10, y=50, h=6, w_final=80, progress=0.5)
    assert result[50, 10, 0] == 193  # GOLD red channel

def test_line_wipe_progress_zero_draws_nothing():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = A.line_wipe(frame, x=10, y=50, h=6, w_final=80, progress=0.0)
    assert result[50, 10, 0] == 0   # no bar drawn

def test_slide_in_x_returns_int():
    arr = np.ones((20, 60, 4), dtype=np.uint8) * 200
    result = A.slide_in_x(arr, x_from=20, x_to=0, progress=0.5)
    assert isinstance(result, int)

def test_slide_in_x_at_zero_progress():
    arr = np.ones((20, 60, 4), dtype=np.uint8) * 200
    result = A.slide_in_x(arr, x_from=50, x_to=10, progress=0.0)
    assert result == 50

def test_slide_in_x_at_full_progress():
    arr = np.ones((20, 60, 4), dtype=np.uint8) * 200
    result = A.slide_in_x(arr, x_from=50, x_to=10, progress=1.0)
    assert result == 10

def test_scale_overlay_shrinks():
    arr = np.ones((100, 80, 4), dtype=np.uint8) * 255
    out = A.scale_overlay(arr, s=0.5)
    assert out.shape[0] == 50 and out.shape[1] == 40

def test_scale_overlay_grows():
    arr = np.ones((50, 40, 4), dtype=np.uint8) * 255
    out = A.scale_overlay(arr, s=2.0)
    assert out.shape[0] == 100 and out.shape[1] == 80

def test_count_up_price_returns_rgba():
    frame = A.count_up_price(220000, progress=0.0)
    assert frame.ndim == 3 and frame.shape[2] == 4

def test_count_up_price_full_returns_rgba():
    frame = A.count_up_price(220000, progress=1.0)
    assert frame.ndim == 3 and frame.shape[2] == 4
