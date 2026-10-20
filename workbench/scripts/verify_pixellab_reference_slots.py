#!/usr/bin/env python3
"""Compare original serialization to three retained actual PixelLab slot0 PNGs.

No network, model inference or provider credentials. Keep generated slots
separate: this verifies reference transport only.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from sprite_workbench.core import Store, digest
from sprite_workbench.parity_pixels import execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True, help='Retained pixellab-h3-rpg-pilot artifact root')
    parser.add_argument('--output', type=Path, required=True, help='New external evidence directory')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Preserve earlier evidence; choose a new output directory')
    args.output.mkdir(parents=True)
    store = Store(args.output / 'store')
    checks = []
    for case in ('pixellab-walk-v1', 'pixellab-slash-v1', 'pixellab-slash-margin-v2'):
        first = args.inputs / case / 'source.png'
        returned = args.inputs / case / 'extracted/frame-000.png'
        with Image.open(first) as image:
            a = np.array(image.convert('RGBA'))
        with Image.open(returned) as image:
            b = np.array(image.convert('RGBA'))
        source = store.put_raster(a)
        result = execute(store, 'serialize', raster=source)
        normalized = store.get_raster(result['output_raster'])
        checks.append({'case': case, 'source_png': str(first.resolve()), 'source_png_sha256': digest(first.read_bytes()),
            'reference_png': str(returned.resolve()), 'reference_png_sha256': digest(returned.read_bytes()),
            'raw_different_pixels': int(np.count_nonzero(np.any(a != b, axis=2))),
            'original_serializer_matches_returned_reference_rgba': bool(np.array_equal(normalized, b)),
            'receipt': result['receipt'], 'output_rgba_sha256': result['output_rgba_sha256']})
    report = {'kind': 'retained-pixellab-reference-slot-parity', 'checks': checks,
              'passed': all(c['original_serializer_matches_returned_reference_rgba'] for c in checks),
              'recipe_sha256': digest(Path(__file__).read_bytes()),
              'boundary': 'Actual shipped serialization reproduces these three retained reference pixels. No generated-frame, server model or animation conversion parity.'}
    (args.output / 'MATCHED-REFERENCE-PARITY.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'checks': len(checks)}))
    return 0 if report['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
