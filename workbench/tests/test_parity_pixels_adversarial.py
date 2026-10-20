"""Independent marker oracles for bounded execution of original Godot pixel methods.

Host capture/undo are fixtures. These tests do not exercise private PixelLab
servers or establish broader application/model parity.
"""
from io import BytesIO
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import ValidationError, UnsupportedCapability


def _conditioning_oracle(source):
    """First 4096 distinct visible RGBA values, x-major in and x-major out."""
    seen = set()
    ordered = []
    height, width = source.shape[:2]
    for x in range(width):
        for y in range(height):
            color = tuple(int(v) for v in source[y, x])
            if color[3] and color not in seen:
                seen.add(color)
                ordered.append(color)
    result = np.zeros((64, 64, 4), dtype=np.uint8)
    for index, color in enumerate(ordered[:4096]):
        x, y = divmod(index, 64)
        result[y, x] = color
    return result


def _png(source):
    stream = BytesIO()
    Image.fromarray(source).save(stream, format='PNG')
    return stream.getvalue()


def _blit_oracle(destination, source, *, origin=(0, 0), rect_size=None, mask=None):
    """Full RGBA replacement with clipping and a separate source-alpha mask."""
    result = destination.copy()
    width, height = rect_size or (source.shape[1], source.shape[0])
    for y in range(height):
        for x in range(width):
            dx, dy = x + origin[0], y + origin[1]
            if (x >= source.shape[1] or y >= source.shape[0] or
                    dx < 0 or dy < 0 or dx >= result.shape[1] or dy >= result.shape[0]):
                continue
            if mask is None or mask[y, x, 3] != 0:
                result[dy, dx] = source[y, x]
    return result

@pytest.fixture
def store(tmp_path):
    from sprite_workbench.core import Store
    return Store(tmp_path / 'store')


@pytest.fixture
def api():
    from sprite_workbench import parity_pixels
    return parity_pixels


def _run(api, store, operation, **kwargs):
    arrays = {key: value.copy() for key, value in kwargs.items() if isinstance(value, np.ndarray)}
    request = {key: store.put_raster(value) if isinstance(value, np.ndarray) else value
               for key, value in kwargs.items()}
    receipt = api.execute(store, operation, **request)
    assert receipt['execution']['input_unchanged'] is True
    assert len(receipt['execution']['method_sha256']) == 6
    for key, value in arrays.items():
        np.testing.assert_array_equal(kwargs[key], value)
        np.testing.assert_array_equal(store.get_raster(request[key]), value)
    output = store.get_raster(receipt['output_raster']) if 'output_raster' in receipt else None
    return receipt, output


def test_serialization_normalizes_only_zero_alpha_without_mutating_input(api, store):
    source = np.array([[[91, 72, 53, 0], [12, 34, 56, 1], [3, 4, 5, 127]],
                       [[9, 8, 7, 254], [100, 110, 120, 255], [5, 6, 7, 0]]], dtype=np.uint8)
    expected = source.copy()
    expected[expected[..., 3] == 0] = 0
    receipt, output = _run(api, store, 'serialize', raster=source)
    np.testing.assert_array_equal(output, expected)
    assert store.get_bytes(receipt['raw_rgba']) == expected.tobytes()
    assert receipt['encoding'] == 'raw-rgba; not PNG'


@pytest.mark.parametrize('alphas,expected', [([1, 127, 254, 255], False),
                                            ([1, 127, 0, 255], True), ([0, 0, 0, 0], True)])
def test_transparency_means_exact_zero_not_partial(api, store, alphas, expected):
    source = np.full((1, 4, 4), 93, dtype=np.uint8)
    source[0, :, 3] = alphas
    result, _ = _run(api, store, 'transparency', raster=source)
    assert result['has_exact_zero_alpha'] is expected


def test_reference_conditioning_order_rgba_keys_and_frequency(api, store):
    # Column-major first occurrence: A,C,B,D,E. A frequency does not duplicate it.
    a, b, c, d, e = ([11, 22, 33, 255], [44, 55, 66, 1],
                     [11, 22, 33, 127], [0, 0, 0, 255], [77, 88, 99, 254])
    source = np.array([[a, b], [c, d], [a, e], [[99, 88, 77, 0], a]], dtype=np.uint8)
    receipt, output = _run(api, store, 'reference_palette', raster=source)
    np.testing.assert_array_equal(output, _conditioning_oracle(source))
    assert receipt['palette_entries'] == 5
    assert np.all(output[:, 1:] == 0)
    assert np.all(output[5:, 0] == 0)


def test_reference_conditioning_caps_unique_colors_without_resampling(api, store):
    source = np.empty((65, 65, 4), dtype=np.uint8)
    for x in range(65):
        for y in range(65):
            index = x * 65 + y
            source[y, x] = [index % 256, index // 256, 73, 255]
    receipt, output = _run(api, store, 'reference_palette', raster=source)
    assert receipt['palette_entries'] == 4096
    np.testing.assert_array_equal(output, _conditioning_oracle(source))
    assert output[63, 63].tolist() == [255, 15, 73, 255]


def test_invisible_reference_omits_hidden_rgb(api, store):
    source = np.full((2, 3, 4), [31, 47, 59, 0], dtype=np.uint8)
    receipt, output = _run(api, store, 'reference_palette', raster=source)
    assert receipt['palette_entries'] == 0
    assert np.all(output == 0)


@pytest.mark.parametrize('fill,empty', [(False, False), (True, False), (False, True), (True, True)])
def test_mask_is_opaque_bw_and_fill_tests_exact_zero(api, store, fill, empty):
    mask = np.full((1, 4, 4), 91, dtype=np.uint8)
    mask[0, :, 3] = [0, 1, 127, 255]
    art = np.full((1, 4, 4), 41, dtype=np.uint8)
    art[0, :, 3] = [255, 1, 0, 0]
    expected = np.full_like(mask, 255)
    white = mask[..., 3] > 0
    if fill:
        white |= art[..., 3] == 0
    expected[..., :3] = white[..., None] * 255
    _, output = _run(api, store, 'mask', mask=mask, art=art,
                     fill_background=fill, inpaint_empty_image=empty)
    np.testing.assert_array_equal(output, expected)


@pytest.mark.parametrize('mask_empty,art_empty,inpaint,expected_white', [
    (True, True, False, False), (True, True, True, True),
    (True, False, True, False), (False, True, True, True)])
def test_empty_image_inpaint_requires_both_captures_invisible(api, store, mask_empty, art_empty,
                                                            inpaint, expected_white):
    mask = np.full((2, 2, 4), [9, 8, 7, 0 if mask_empty else 1], dtype=np.uint8)
    art = np.full((2, 2, 4), [3, 4, 5, 0 if art_empty else 1], dtype=np.uint8)
    _, output = _run(api, store, 'mask', mask=mask, art=art, inpaint_empty_image=inpaint)
    assert np.all(output[..., :3] == (255 if expected_white else 0))
    assert np.all(output[..., 3] == 255)


@pytest.mark.parametrize('encoding', ['raw', 'png'])
def test_decode_preserves_full_rgba_and_png_actual_dimensions(api, store, encoding):
    source = np.array([[[91, 22, 33, 0], [44, 55, 66, 127]],
                       [[7, 8, 9, 1], [10, 11, 12, 255]],
                       [[13, 14, 15, 254], [16, 17, 18, 255]]], dtype=np.uint8)
    media = store.put_bytes(source.tobytes() if encoding == 'raw' else _png(source))
    receipt, output = _run(api, store, 'decode', media=media,
                           width=2 if encoding == 'raw' else 1,
                           height=3 if encoding == 'raw' else 1)
    np.testing.assert_array_equal(output, source)
    assert (receipt['width'], receipt['height']) == (2, 3)


@pytest.mark.parametrize('origin,extent', [([0, 0], [3, 2]), ([-1, -1], [3, 2]),
                                          ([3, 2], [3, 2]), ([1, 1], [1, 1]),
                                          ([0, 0], [4, 3])])
def test_placement_replaces_including_alpha_zero_and_clips(api, store, origin, extent):
    destination = np.full((3, 4, 4), [73, 61, 49, 255], dtype=np.uint8)
    source = np.array([[[11, 22, 33, 0], [44, 55, 66, 127], [7, 8, 9, 255]],
                       [[2, 3, 4, 1], [6, 7, 8, 254], [15, 16, 17, 255]]], dtype=np.uint8)
    expected = _blit_oracle(destination, source, origin=origin, rect_size=extent)
    _, output = _run(api, store, 'place', source=source, destination=destination,
                     origin=origin, extent=extent)
    np.testing.assert_array_equal(output, expected)


def test_preserve_mask_consumes_alpha_not_rgb_and_does_not_blend(api, store):
    destination = np.full((1, 4, 4), [73, 61, 49, 255], dtype=np.uint8)
    source = np.array([[[11, 22, 33, 0], [44, 55, 66, 127], [7, 8, 9, 255], [1, 2, 3, 1]]], dtype=np.uint8)
    mask = np.array([[[0, 0, 0, 255], [255, 255, 255, 0],
                      [0, 0, 0, 1], [255, 255, 255, 127]]], dtype=np.uint8)
    _, output = _run(api, store, 'place', source=source, destination=destination, preserve_mask=mask)
    np.testing.assert_array_equal(output, _blit_oracle(destination, source, mask=mask))
    assert output[0, 0].tolist() == [11, 22, 33, 0]
    assert output[0, 1].tolist() == destination[0, 1].tolist()


def _blobs(store):
    return {p.name for p in (store.path / 'blobs').iterdir()}


@pytest.mark.parametrize('payload,width,height', [
    (b'', 1, 1), (b'123', 1, 1), (b'12345', 1, 1),
    (b'\x89PNG\r\n\x1a\n', 1, 2), (b'1234', 0, 1),
    (b'1234', True, 1), (b'1234', 513, 1), (b'1234', 1.0, 1)])
def test_bad_encoded_admission_creates_no_accepted_artifacts(api, store, payload, width, height):
    media = store.put_bytes(payload)
    before = _blobs(store)
    with pytest.raises(ValidationError):
        api.execute(store, 'decode', media=media, width=width, height=height)
    assert _blobs(store) == before


@pytest.mark.parametrize('kind', ['mask_shape', 'placement_mask_shape', 'origin_bool', 'extent_zero',
                                  'mask_flag_int', 'unknown_field', 'unknown_operation', 'raster_too_wide'])
def test_invalid_controls_fail_without_publication(api, store, kind):
    a = store.put_raster(np.full((2, 3, 4), 255, dtype=np.uint8))
    b = store.put_raster(np.full((1, 3, 4), 255, dtype=np.uint8))
    operation, request = 'place', {'source': a, 'destination': a}
    if kind == 'mask_shape':
        operation, request = 'mask', {'mask': a, 'art': b}
    elif kind == 'placement_mask_shape': request['preserve_mask'] = b
    elif kind == 'origin_bool': request['origin'] = [True, 0]
    elif kind == 'extent_zero': request['extent'] = [0, 1]
    elif kind == 'mask_flag_int': operation, request = 'mask', {'mask': a, 'art': a, 'fill_background': 1}
    elif kind == 'unknown_field': request['surprise'] = a
    elif kind == 'unknown_operation': operation = 'server_cutout'
    else:
        request = {'raster': store.put_raster(np.full((1, 513, 4), 255, dtype=np.uint8))}
        operation = 'serialize'
    before = _blobs(store)
    with pytest.raises(ValidationError): api.execute(store, operation, **request)
    assert _blobs(store) == before


@pytest.mark.parametrize('failure', ['missing_runtime', 'timeout', 'nonzero_exit', 'missing_result',
                                    'malformed_result', 'wrong_output_size', 'changed_input'])
def test_resource_and_result_failures_do_not_publish(api, store, monkeypatch, failure):
    raster = store.put_raster(np.full((1, 1, 4), 255, dtype=np.uint8))
    before = _blobs(store)
    if failure == 'missing_runtime':
        monkeypatch.setattr(api.shutil, 'which', lambda _: None)
    else:
        def fake_run(command, **kwargs):
            if failure == 'timeout': raise subprocess.TimeoutExpired(command, 30)
            kwargs['stdout'].write(b'Godot Engine fixture\nPIXELS_OK\n')
            root = Path(command[command.index('--path') + 1])
            if failure not in ('nonzero_exit', 'missing_result'):
                if failure == 'malformed_result': (root / 'result.json').write_text('{')
                else:
                    import json
                    (root / 'result.json').write_text(json.dumps({'width': 1, 'height': 1,
                        'raw_size': 4, 'input_unchanged': failure != 'changed_input'}))
                    (root / 'output.rgba').write_bytes(b'123' if failure == 'wrong_output_size' else b'1234')
            return subprocess.CompletedProcess(command, 1 if failure == 'nonzero_exit' else 0)
        monkeypatch.setattr(api.subprocess, 'run', fake_run)
    with pytest.raises((ValidationError, UnsupportedCapability)):
        api.execute(store, 'serialize', raster=raster)
    assert _blobs(store) == before


def test_corrupted_source_bundle_is_rejected_before_engine(api, store, monkeypatch, tmp_path):
    import shutil
    vendor = tmp_path / 'vendor'
    shutil.copytree(api._VENDOR, vendor)
    original = vendor / 'get_image.gd'
    if not original.exists():
        candidates = [p for p in vendor.iterdir() if p.suffix == '.gd' and p.name != 'runner.gd']
        original = candidates[0]
    original.write_bytes(original.read_bytes() + b'\n# altered source\n')
    monkeypatch.setattr(api, '_VENDOR', vendor)
    raster = store.put_raster(np.full((1, 1, 4), 255, dtype=np.uint8))
    before = _blobs(store)
    with pytest.raises(ValidationError, match='integrity'):
        api.execute(store, 'serialize', raster=raster)
    assert _blobs(store) == before


@pytest.mark.parametrize('kind', ['png_too_wide', 'animated_png', 'encoded_byte_budget', 'corrupt_media'])
def test_container_and_store_failure_boundaries(api, store, kind):
    width, height = 1, 1
    if kind == 'png_too_wide':
        raw = _png(np.full((1, 513, 4), 255, dtype=np.uint8))
    elif kind == 'animated_png':
        first = Image.fromarray(np.full((1, 1, 4), [1, 2, 3, 255], dtype=np.uint8))
        second = Image.fromarray(np.full((1, 1, 4), [4, 5, 6, 255], dtype=np.uint8))
        stream = BytesIO()
        first.save(stream, format='PNG', save_all=True, append_images=[second], duration=100, loop=0)
        raw = stream.getvalue()
    elif kind == 'encoded_byte_budget':
        raw = b'0' * (api.MAX_ENCODED_BYTES + 1)
    else:
        raw = b'1234'
    media = store.put_bytes(raw)
    if kind == 'corrupt_media':
        (store.path / 'blobs' / media).write_bytes(b'4321')
    before = _blobs(store)
    with pytest.raises(ValidationError):
        api.execute(store, 'decode', media=media, width=width, height=height)
    assert _blobs(store) == before


def test_corrupted_manifest_is_rejected_before_engine(api, store, monkeypatch, tmp_path):
    import shutil
    vendor = tmp_path / 'vendor'
    shutil.copytree(api._VENDOR, vendor)
    (vendor / 'manifest.json').write_text('{}')
    monkeypatch.setattr(api, '_VENDOR', vendor)
    raster = store.put_raster(np.full((1, 1, 4), 255, dtype=np.uint8))
    before = _blobs(store)
    with pytest.raises(ValidationError, match='integrity'):
        api.execute(store, 'serialize', raster=raster)
    assert _blobs(store) == before
