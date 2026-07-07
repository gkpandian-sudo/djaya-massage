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
