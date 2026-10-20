"""Boundary tests for unchanged Godot methods, using explicit supplied fixtures."""
from io import BytesIO
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
import pytest

from sprite_workbench import parity_pixels as p
from sprite_workbench.core import Store, ValidationError, UnsupportedCapability


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path)


def rgba(store, pixels):
    return store.put_raster(np.array(pixels, dtype=np.uint8))


def test_exact_serialization_and_transparency_do_not_discard_partial_or_mutate(store):
    raster = rgba(store, [[[90, 80, 70, 0], [10, 20, 30, 1], [5, 6, 7, 128]]])
    result = p.execute(store, 'serialize', raster=raster)
    assert store.get_raster(result['output_raster']).tolist() == [[[0, 0, 0, 0], [10, 20, 30, 1], [5, 6, 7, 128]]]
    assert store.get_bytes(result['raw_rgba']) == bytes([0, 0, 0, 0, 10, 20, 30, 1, 5, 6, 7, 128])
    assert store.get_raster(raster)[0, 0].tolist() == [90, 80, 70, 0]
    assert result['execution']['input_unchanged'] is True
    assert p.execute(store, 'transparency', raster=raster)['has_exact_zero_alpha'] is True
    partial = rgba(store, [[[1, 2, 3, 128]]])
    assert p.execute(store, 'transparency', raster=partial)['has_exact_zero_alpha'] is False


def test_reference_palette_is_unique_rgba_x_major_not_frequency_or_quantizer(store):
    raster = rgba(store, [[[5, 6, 7, 128], [5, 6, 7, 255]], [[5, 6, 7, 128], [99, 88, 77, 0]]])
    result = p.execute(store, 'reference_palette', raster=raster)
    output = store.get_raster(result['output_raster'])
    assert result['palette_entries'] == 2 and output.shape == (64, 64, 4)
    assert output[0, 0].tolist() == [5, 6, 7, 128]
    assert output[1, 0].tolist() == [5, 6, 7, 255]
    assert np.count_nonzero(output[..., 3]) == 2


def test_mask_distinguishes_positive_and_zero_alpha_from_preserve_alpha_convention(store):
    mask = rgba(store, [[[90, 80, 70, 0], [1, 2, 3, 1], [3, 4, 5, 128]]])
    art = rgba(store, [[[9, 8, 7, 255], [9, 8, 7, 0], [9, 8, 7, 1]]])
    result = p.execute(store, 'mask', mask=mask, art=art)
    assert store.get_raster(result['output_raster']).tolist() == [[[0, 0, 0, 255], [255, 255, 255, 255], [255, 255, 255, 255]]]
    blank = rgba(store, [[[1, 2, 3, 0], [4, 5, 6, 0], [7, 8, 9, 0]]])
    filled = p.execute(store, 'mask', mask=blank, art=art, fill_background=True)
    assert store.get_raster(filled['output_raster'])[0, :, 0].tolist() == [0, 255, 0]
    empty = p.execute(store, 'mask', mask=blank, art=blank, inpaint_empty_image=True)
    assert np.all(store.get_raster(empty['output_raster']) == 255)
    assert 'consume RGB' in result['mask_encoding']


def test_png_decode_uses_actual_dimensions_raw_decode_uses_declaration(store):
    array = np.array([[[9, 8, 7, 0], [1, 2, 3, 128]]], dtype=np.uint8)
    buffer = BytesIO(); Image.fromarray(array).save(buffer, format='PNG')
    result = p.execute(store, 'decode', media=store.put_bytes(buffer.getvalue()), width=99, height=98)
    assert result['width'] == 2 and result['height'] == 1
    assert np.array_equal(store.get_raster(result['output_raster']), array)
    raw = p.execute(store, 'decode', media=store.put_bytes(array.tobytes()), width=2, height=1)
    assert np.array_equal(store.get_raster(raw['output_raster']), array)


def test_placement_erases_zero_alpha_and_clips_without_mutating_destination(store):
    source = rgba(store, [[[9, 8, 7, 0], [1, 2, 3, 128]]])
    destination = rgba(store, [[[255, 0, 0, 255]] * 3, [[255, 0, 0, 255]] * 3])
    result = p.execute(store, 'place', source=source, destination=destination, origin=[1, 1])
    assert store.get_raster(result['output_raster'])[1].tolist() == [[255, 0, 0, 255], [9, 8, 7, 0], [1, 2, 3, 128]]
    assert np.all(store.get_raster(destination)[..., 3] == 255)
    preserve = rgba(store, [[[0, 0, 0, 255], [255, 255, 255, 0]]])
    masked = p.execute(store, 'place', source=source, destination=destination, origin=[1, 1], preserve_mask=preserve)
    assert store.get_raster(masked['output_raster'])[1].tolist() == [[255, 0, 0, 255], [9, 8, 7, 0], [255, 0, 0, 255]]
    clipped = p.execute(store, 'place', source=source, destination=destination, origin=[-1, 0])
    assert store.get_raster(clipped['output_raster'])[0, 0].tolist() == [1, 2, 3, 128]


@pytest.mark.parametrize('operation,payload', [
    ('unknown', {}), ('serialize', {}), ('serialize', {'raster': 'x', 'extra': 1}),
    ('decode', {'media': 'x', 'width': True, 'height': 1}),
    ('decode', {'media': 'x', 'width': 513, 'height': 1}),
])
def test_invalid_requests_never_launch_host(store, monkeypatch, operation, payload):
    monkeypatch.setattr(p, '_engine', lambda *_: pytest.fail('invalid request reached host'))
    with pytest.raises(ValidationError):
        p.execute(store, operation, **payload)


def test_malformed_and_oversized_png_rejected_as_explicit_local_admission_rule(store, monkeypatch):
    monkeypatch.setattr(p, '_engine', lambda *_: pytest.fail('invalid media reached host'))
    for raw in (b'\x89PNG\r\n\x1a\n', b'bad'):
        with pytest.raises(ValidationError):
            p.execute(store, 'decode', media=store.put_bytes(raw), width=1, height=1)
    buffer = BytesIO(); Image.new('RGBA', (513, 1)).save(buffer, format='PNG')
    with pytest.raises(ValidationError):
        p.execute(store, 'decode', media=store.put_bytes(buffer.getvalue()), width=1, height=1)


def test_resource_failure_is_structured_and_does_not_create_outputs(store, monkeypatch):
    raster = rgba(store, [[[1, 2, 3, 255]]])
    before = sorted((store.path / 'blobs').iterdir())
    def timeout(command, **kwargs):
        assert '--as=4294967296' in command and 'preexec_fn' not in kwargs
        assert kwargs['timeout'] == 30
        raise subprocess.TimeoutExpired(command, 30)
    monkeypatch.setattr(p.subprocess, 'run', timeout)
    with pytest.raises(UnsupportedCapability, match='timed out'):
        p.execute(store, 'serialize', raster=raster)
    assert sorted((store.path / 'blobs').iterdir()) == before


def test_missing_host_and_altered_source_fail_closed(store, monkeypatch, tmp_path):
    raster = rgba(store, [[[1, 2, 3, 255]]])
    monkeypatch.setattr(p.shutil, 'which', lambda _: None)
    with pytest.raises(UnsupportedCapability, match='Godot4'):
        p.execute(store, 'serialize', raster=raster)
    vendor = tmp_path / 'vendor'; vendor.mkdir()
    (vendor / 'manifest.json').write_text('{}')
    monkeypatch.setattr(p, '_VENDOR', vendor)
    with pytest.raises(ValidationError, match='manifest integrity'):
        p.describe()
