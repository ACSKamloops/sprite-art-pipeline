"""Captured boundary regressions and alpha scope; no provider calls."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location('fixed_palette', Path(__file__).parents[1] / 'scripts/replay_pixellab_fixed_palette.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def test_captured_gray_boundary_is_not_rgb_midpoint_and_alpha_is_exact():
    source = np.array([[[99, 99, 99, 0], [100, 100, 100, 64], [128, 128, 128, 128], [255, 255, 255, 255]]], dtype=np.uint8)
    palette = np.array([[0, 0, 0, 255], [255, 255, 255, 255]], dtype=np.uint8)
    result = replay.remap_rgba(source, palette)
    assert result[0, :, 0].tolist() == [0, 255, 255, 255]
    assert np.array_equal(result[..., 3], source[..., 3])
    assert source[0, 1, 0] == 100


def test_hidden_rgb_is_quantized_without_forcing_alpha_or_zeroing_hidden_pixels():
    source = np.array([[[240, 240, 240, 0]]], dtype=np.uint8)
    palette = np.array([[0, 0, 0, 255], [255, 255, 255, 255]], dtype=np.uint8)
    assert replay.remap_rgba(source, palette).tolist() == [[[255, 255, 255, 0]]]


def test_uncalibrated_palette_alpha_is_rejected():
    with pytest.raises(ValueError, match='opaque'):
        replay.remap_rgba(np.zeros((1, 1, 4), dtype=np.uint8), np.array([[0, 0, 0, 128]], dtype=np.uint8))
