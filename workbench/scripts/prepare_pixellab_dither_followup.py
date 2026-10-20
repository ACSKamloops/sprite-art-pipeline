#!/usr/bin/env python3
"""Freeze three discriminating public-reducer probes; offline preparation only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

import pixellab_h3_comparison as capture


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(path):
    return {'type': 'base64', 'format': 'png',
            'base64': 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()}


def prepare(root):
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'inputs'
    inputs.mkdir()
    # Pin previous exact inputs rather than silently substituting a new encoding.
    prior = Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014/inputs')
    pins = {'rgb-cube-gray.png': '02a8c2ed81763a07eb7ac03d74526c24c59bdff4d905431cedec499ea8d042f6',
            'rgba-stripes.png': 'c098f95d8636ffccfbb3efb221ae1796ea5f8d960c730791fa5272a56f3d80f9',
            'black-white-palette.png': 'f0891e063e294b42af8ecf4a1168aaace411da9908d324fb88bde8f88b500fa8'}
    for name, expected in pins.items():
        raw = (prior / name).read_bytes()
        if sha(raw) != expected:
            raise ValueError('Prior input changed: ' + name)
        (inputs / name).write_bytes(raw)
    gray = np.zeros((32, 256, 4), dtype=np.uint8)
    gray[..., :3] = np.arange(256, dtype=np.uint8)[None, :, None]
    gray[..., 3] = 255
    Image.fromarray(gray).save(inputs / 'gray-only.png')
    gray_alpha = gray.copy()
    gray_alpha[..., 3] = np.tile(np.repeat([0, 64, 128, 255], 64), (32, 1))
    Image.fromarray(gray_alpha).save(inputs / 'gray-alpha.png')
    rows = []
    for variant, names, matrix, strength in [
        ('gray-context-2x2', ['gray-only.png', 'gray-alpha.png'], '2x2', 5.0),
        ('epsilon-2x2', ['rgb-cube-gray.png', 'rgba-stripes.png'], '2x2', 0.000001),
        ('cube-4x4', ['rgb-cube-gray.png', 'rgba-stripes.png'], '4x4', 5.0),
    ]:
        run = root / variant
        run.mkdir()
        payload = {'images': [descriptor(inputs / name) for name in names],
                   'palette_image': descriptor(inputs / 'black-white-palette.png'),
                   'dithering': matrix, 'dithering_strength': strength}
        capture.write_json(run / 'request.json', payload)
        wire = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
        rows.append({'variant': variant, 'request_sha256': sha((run / 'request.json').read_bytes()),
                     'wire_sha256': sha(wire), 'dithering': matrix, 'strength': strength})
    capture.write_json(root / 'PLAN.json', {
        'version': 1, 'prepared_utc': capture.now(), 'endpoint': 'https://api.pixellab.ai/v2/reduce-colors',
        'max_posts': 3, 'automatic_retries': 0, 'requests': rows,
        'hypotheses': [
            'Gray-only compared with cube-tail gray at identical phase discriminates context-dependent mapping or cache behavior.',
            'A tiny positive strength tests whether ordered mapping approaches the nondithered Oklab limit continuously.',
            '4x4 exposes phase thresholds beyond 2x2; compare conventional Bayer ordering without fitting an arbitrary lookup.'
        ],
        'source_script_sha256': sha(Path(__file__).read_bytes()),
        'inputs': [{'path': str(p.relative_to(root)), 'sha256': sha(p.read_bytes())} for p in sorted(inputs.iterdir())],
        'scope': 'Public reducer characterization only; no private source or internal animation pipeline claim.'})
    return {'root': str(root), 'posts': 0, 'plan_sha256': sha((root / 'PLAN.json').read_bytes()),
            'variants': [row['variant'] for row in rows]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root)))
