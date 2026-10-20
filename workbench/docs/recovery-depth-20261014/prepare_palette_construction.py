#!/usr/bin/env python3
"""Prepare only: deterministic diagnostics and four frozen reducer requests. No HTTP/auth."""
import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def png(rgba, width=64, height=64):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    scanlines = b''.join(b'\x00' + rgba[y * width * 4:(y + 1) * width * 4] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(scanlines, 9)) + chunk(b'IEND', b''))


def prepare(root, asset, schema):
    root.mkdir(parents=True, exist_ok=False)
    (root / 'inputs').mkdir()
    assert sha(schema.read_bytes()) == '8cb24ecdd26e9fe48639dc789e44f32b3c78c29e8da8c3121f23ab360ade5dad'
    api = json.loads(schema.read_text())
    write_json(root / 'PUBLIC-CONTRACT.json', {'source_sha256': sha(schema.read_bytes()),
        'route': api['paths']['/reduce-colors'], 'schemas': {k: api['components']['schemas'][k]
        for k in ['ReduceColorsRequest', 'ReduceColorsResponse', 'Base64Image']}})
    bases = [(24, 24, 32), (224, 216, 192), (188, 44, 52), (40, 152, 76),
             (44, 76, 192), (212, 132, 40), (136, 64, 160), (40, 164, 172)]
    weights = {'A': [16, 8, 12, 8, 8, 4, 4, 4], 'B': [4, 4, 4, 4, 8, 12, 12, 16]}
    weights['C'] = [(a + b) // 2 for a, b in zip(weights['A'], weights['B'])]
    fixture_rows, histograms = [], {}
    for name, counts in weights.items():
        pixels = []
        for base, count in zip(bases, counts):
            for r in [-7, -3, 1, 5]:
                for g in [-7, -3, 1, 5]:
                    for b in [-7, -3, 1, 5]:
                        pixels += [(base[0] + r, base[1] + g, base[2] + b, 255)] * count
        assert len(pixels) == 4096
        # Odd modular stride is a permutation; histogram remains exact.
        pixels = [pixels[(i * 2053) % 4096] for i in range(4096)]
        histograms[name] = Counter(pixels)
        assert len(histograms[name]) == 512
        rgba = bytes(channel for pixel in pixels for channel in pixel)
        raw_png = png(rgba)
        (root / 'inputs' / (name + '.rgba')).write_bytes(rgba)
        (root / 'inputs' / (name + '.png')).write_bytes(raw_png)
        fixture_rows.append({'name': name, 'width': 64, 'height': 64, 'unique_colors': 512,
            'all_alpha': 255, 'rgba_file': 'inputs/' + name + '.rgba', 'rgba_sha256': sha(rgba),
            'png_file': 'inputs/' + name + '.png', 'png_sha256': sha(raw_png), 'family_weights_per_color': counts})
    assert histograms['A'] + histograms['B'] == histograms['C'] + histograms['C']
    write_json(root / 'FIXTURES.json', {'label': 'supplied synthetic diagnostics; no generated art',
        'family_bases_rgb': bases, 'channel_offsets': [-7, -3, 1, 5],
        'spatial_permutation': 'output[i] = original[(i*2053)%4096]',
        'histogram_identity': 'hist(A)+hist(B) == 2*hist(C), exact RGBA counts', 'fixtures': fixture_rows})
    cases = [('joint-ab-4', ['A', 'B'], 4), ('histogram-cc-4', ['C', 'C'], 4),
             ('weighted-aa-4', ['A', 'A'], 4), ('joint-ab-32', ['A', 'B'], 32)]
    frozen = []
    for variant, frames, count in cases:
        run = root / variant
        run.mkdir()
        images = []
        for frame in frames:
            raw = (root / 'inputs' / (frame + '.png')).read_bytes()
            images.append({'type': 'base64', 'base64': 'data:image/png;base64,' + base64.b64encode(raw).decode(), 'format': 'png'})
        payload = {'images': images, 'num_colors': count, 'dithering': 'none', 'dithering_strength': 5.0}
        write_json(run / 'request.json', payload)
        frozen.append({'variant': variant, 'frames': frames, 'num_colors': count,
            'request_sha256': sha((run / 'request.json').read_bytes()),
            'compact_http_body_sha256': sha(json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode())})
    write_json(root / 'PLAN.json', {'version': 1, 'phase': 'palette-construction',
        'endpoint': 'https://api.pixellab.ai/v2/reduce-colors', 'max_posts': 4, 'automatic_retries': 0,
        'requests': frozen, 'credential_access': False, 'posts_performed': 0,
        'predeclared_comparisons': ['AB4 versus CC4 palette RGB multiset and per-source-color mappings: identical total histogram, different frame partition',
            'AB4 first A versus AA4 first A: shared-frame influence; report any palette/mapping changes',
            'AB32 versus unchanged original palette-image helper32 RGB set: exact equality or disagreement, no parameter fitting'],
        'scope': 'Public reducer palette construction only; no model identity, H3 conversion or private-source equivalence claim'})
    helper = Path(__file__).with_name('replay_palette_helper.cjs')
    subprocess.run(['node', str(helper), str(asset), str(root)], check=True)
    return {'prepared': str(root), 'posts': 0, 'cases': [c[0] for c in cases]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--asset', type=Path, required=True)
    parser.add_argument('--schema', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.asset, args.schema)))
