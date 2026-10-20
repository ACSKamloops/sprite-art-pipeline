"""Authoritative animation time survives real encoded-image import."""
from fractions import Fraction
import struct

import numpy as np
import pytest

from sprite_workbench.acquisition import import_image
from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.export import apng_bytes


def test_apng_fractional_holds_survive_real_export_decode(tmp_path):
    arrays = [np.full((3, 4, 4), [30, 40, 50, 255], np.uint8),
              np.full((3, 4, 4), [40, 60, 80, 128], np.uint8)]
    path = tmp_path / 'exact.png'
    path.write_bytes(apng_bytes(arrays, [Fraction(1, 7), Fraction(2, 9)], 0))
    store = Store(tmp_path / 'store')
    result = import_image(store, path)
    doc, decoded = load_sequence(store, result['sequence'])
    assert [f['duration'] for f in doc['frames']] == [[1, 7], [2, 9]]
    assert doc['loop'] and doc['play_count'] == 0
    assert all(np.array_equal(a, b) for a, b in zip(arrays, decoded))
    assert doc['metadata']['duration_source'] == 'APNG fcTL exact rational'


def test_apng_control_crc_failure_is_not_silently_reinterpreted(tmp_path):
    array = np.full((2, 2, 4), 255, np.uint8)
    data = bytearray(apng_bytes([array, array.copy()], [Fraction(1, 7)] * 2, 1))
    marker = data.index(b'fcTL')
    data[marker + 4 + 20] ^= 1
    path = tmp_path / 'bad.png'
    path.write_bytes(data)
    with pytest.raises(ValidationError, match='CRC'):
        import_image(Store(tmp_path / 'store'), path)
