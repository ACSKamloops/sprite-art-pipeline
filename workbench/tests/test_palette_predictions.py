"""Offline checks for a labeled palette hypothesis, never service-parity tests."""
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest


@pytest.fixture
def module(monkeypatch):
    scripts = Path(__file__).parents[1] / 'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location('palette_prediction', scripts / 'prepare_palette_predictions.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standard_transform_roundtrips_rgb_bytes(module):
    values = np.array([[0, 0, 0], [255, 255, 255], [255, 0, 0], [0, 255, 0],
                       [0, 0, 255], [22, 39, 64], [242, 205, 124]], dtype=np.uint8)
    assert np.array_equal(np.rint(module.inverse_lab(module.oklab(values))).astype(np.uint8), values)


def test_two_exact_colors_preserved_with_frequency_order(module):
    source = np.array([[[10, 20, 30, 255], [220, 210, 200, 255], [10, 20, 30, 255]]], dtype=np.uint8)
    palette, receipt = module.predict([source], 2)
    assert palette.tolist() == [[10, 20, 30, 255], [220, 210, 200, 255]]
    assert receipt['cluster_included_mass'] == [2, 1]
    assert np.array_equal(module.remap_rgba(source, palette), source)


def test_excluded_all_transparent_fails_explicitly(module):
    source = np.array([[[10, 20, 30, 0], [220, 210, 200, 0]]], dtype=np.uint8)
    with pytest.raises(ValueError, match='Not enough'):
        module.predict([source], 2, 'exclude-zero')


def test_prepared_alphas_are_discriminating_and_frozen(module, tmp_path):
    root = tmp_path / 'prepared'
    module.prepare(root)
    plan = json.loads((root / 'PLAN.json').read_text())
    case = next(row for row in plan['requests'] if row['variant'] == 'two-alpha-ab')
    palettes = []
    for row in case['predictions']:
        raw = (root / row['path']).read_bytes()
        assert module.sha(raw) == row['sha256']
        palette = json.loads(raw)['palette_rgba']
        palettes.append(tuple(sorted(tuple(c) for c in palette)))
    assert len(set(palettes)) == 3
    for item in plan['inputs']:
        assert module.sha((root / item['path']).read_bytes()) == item['sha256']
    assert not list(root.rglob('response.json'))


def test_ab_ba_predictions_are_order_invariant(module, tmp_path):
    root = tmp_path / 'prepared'
    module.prepare(root)
    a = root / 'two-opaque-ab/prediction-ignore'
    b = root / 'two-opaque-ba/prediction-ignore'
    assert (a / 'palette.png').read_bytes() == (b / 'palette.png').read_bytes()
    assert (a / 'output-00.png').read_bytes() == (b / 'output-01.png').read_bytes()
    assert (a / 'output-01.png').read_bytes() == (b / 'output-00.png').read_bytes()


def test_opaque_cluster_centers_use_frequency(module):
    # Two red shades form one separated cluster; blue is the other. Frequency
    # weighting must move the red center toward the more common shade.
    source = np.array([[[100, 10, 10, 255]] * 20 + [[160, 10, 10, 255]] * 2 + [[10, 10, 180, 255]] * 4], dtype=np.uint8)
    palette, _ = module.predict([source], 2)
    red = palette[np.argmax(palette[:, 0]), 0]
    assert 100 < red < 120


def test_hidden_only_color_fixture_separates_alpha_inclusion(module, tmp_path):
    import prepare_hidden_palette_prediction as hidden
    root = tmp_path / 'hidden'
    hidden.prepare(root)
    run = root / 'hidden-black-3'
    receipts = {policy: json.loads((run / ('prediction-' + policy) / 'PREDICTION.json').read_text())
                for policy in ['ignore', 'exclude-zero', 'alpha-weight']}
    assert receipts['ignore']['palette_rgba'][0] == [0, 0, 0, 255]
    assert receipts['exclude-zero']['palette_rgba'] == receipts['alpha-weight']['palette_rgba']
    assert sorted(receipts['ignore']['palette_rgba']) != sorted(receipts['exclude-zero']['palette_rgba'])
    for name in ['A', 'B']:
        array = np.array(Image.open(root / 'inputs' / (name + '.png')))
        assert np.count_nonzero(array[..., 3] == 0) == 512
        assert np.all(array[array[..., 3] == 0, :3] == 0)
