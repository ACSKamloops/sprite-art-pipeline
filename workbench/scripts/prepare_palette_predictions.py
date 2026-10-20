#!/usr/bin/env python3
"""Authored hypothesis and preregistered fixtures, NOT recovered PixelLab code.

Predicts shared palette by frequency-weighted Oklab Lloyd iterations, fixed .25
lightness distance and deterministic farthest-point seeds. No provider imports.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from replay_pixellab_fixed_palette import M1, M2, oklab, remap_rgba


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    with path.open('x') as file:
        file.write(json.dumps(value, indent=2) + '\n')


def inverse_lab(lab):
    linear = (np.asarray(lab) @ np.linalg.inv(M2).T) ** 3 @ np.linalg.inv(M1).T
    linear = np.maximum(linear, 0)
    srgb = np.where(linear <= .0031308, linear * 12.92,
                    1.055 * linear ** (1 / 2.4) - .055)
    return np.clip(srgb * 255, 0, 255)


def predict(images, count, alpha_policy='ignore'):
    if alpha_policy not in {'ignore', 'exclude-zero', 'alpha-weight'}:
        raise ValueError('Unknown alpha policy')
    if type(count) is not int or not 2 <= count <= 32:
        raise ValueError('Expected 2..32 colors for bounded hypothesis')
    for image in images:
        if image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 4:
            raise ValueError('Expected uint8 RGBA images')
    pixels = np.concatenate([image.reshape(-1, 4) for image in images])
    if len(pixels) > 262144:
        raise ValueError('Bounded total image area exceeded')
    colors, indices = np.unique(pixels[:, :3], axis=0, return_inverse=True)
    pixel_weights = (np.ones(len(pixels)) if alpha_policy == 'ignore' else
                     (pixels[:, 3] > 0).astype(float) if alpha_policy == 'exclude-zero' else
                     pixels[:, 3].astype(float) / 255)
    weights = np.bincount(indices, weights=pixel_weights, minlength=len(colors))
    colors, weights = colors[weights > 0], weights[weights > 0]
    if len(colors) < count:
        raise ValueError('Not enough included distinct colors')
    lab = oklab(colors)
    metric = np.array([.25, 1, 1])
    centers = [lab[int(np.argmax(weights))].copy()]
    while len(centers) < count:
        distance = np.min(np.sum((lab[:, None] - np.array(centers)[None]) ** 2 * metric, axis=2), axis=1)
        centers.append(lab[int(np.argmax(distance))].copy())
    centers = np.array(centers)
    previous = None
    for iteration in range(1, 33):
        labels = np.argmin(np.sum((lab[:, None] - centers[None]) ** 2 * metric, axis=2), axis=1)
        if any(not np.any(labels == c) for c in range(count)):
            raise ValueError('Empty cluster; no unverified reseeding')
        updated = np.stack([np.average(lab[labels == c], weights=weights[labels == c], axis=0)
                            for c in range(count)])
        stable = previous is not None and np.array_equal(labels, previous)
        centers, previous = updated, labels.copy()
        if stable:
            break
    else:
        raise ValueError('No convergence within 32 iterations')
    rgb = np.rint(inverse_lab(centers)).astype(np.uint8)
    mass = np.array([weights[labels == c].sum() for c in range(count)])
    # Presentation hypothesis: greatest included mass first, RGB lexicographic ties.
    order = sorted(range(count), key=lambda c: (-float(mass[c]), *map(int, rgb[c])))
    palette = np.column_stack([rgb[order], np.full(count, 255, dtype=np.uint8)])
    if len(np.unique(palette[:, :3], axis=0)) != count:
        raise ValueError('Rounded palette collapsed')
    return palette, {'alpha_policy': alpha_policy, 'iterations': iteration,
                     'float_centers_oklab': centers[order].tolist(),
                     'cluster_included_mass': mass[order].tolist(),
                     'independent_prediction_not_recovered_source': True}


def frame(colors, weights):
    pixels = np.concatenate([np.repeat(np.array([*color, 255], dtype=np.uint8)[None], n, axis=0)
                             for color, n in zip(colors, weights)])
    if len(pixels) != 1024:
        raise ValueError('Fixture must contain 1024 pixels')
    return pixels[(np.arange(1024) * 517) % 1024].reshape(32, 32, 4)


def descriptor(path):
    return {'type': 'base64', 'format': 'png',
            'base64': 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()}


def prepare(root):
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'inputs'
    inputs.mkdir()
    colors = [[22, 39, 64], [28, 50, 76], [35, 55, 82], [42, 64, 88],
              [195, 142, 48], [211, 166, 72], [228, 186, 99], [242, 205, 124]]
    a = frame(colors, [400, 200, 120, 80, 20, 40, 64, 100])
    b = frame(colors, [100, 100, 100, 100, 200, 200, 200, 24])
    alpha_a, alpha_b = a.copy(), b.copy()
    for i, color in enumerate(colors):
        for array in (alpha_a, alpha_b):
            array[..., 3][np.all(array[..., :3] == color, axis=2)] = [0, 64, 128, 255][i % 4]
    greens = [[28, 134, 75], [38, 146, 81], [48, 156, 89], [59, 169, 96]]
    c = frame(colors + greens, [200, 100, 60, 40, 10, 20, 32, 50, 200, 150, 100, 62])
    d = frame(colors + greens, [40, 30, 20, 10, 100, 100, 100, 12, 250, 170, 100, 92])
    frames = {'A': a, 'B': b, 'A-alpha': alpha_a, 'B-alpha': alpha_b, 'C': c, 'D': d}
    for name, array in frames.items():
        Image.fromarray(array).save(inputs / (name + '.png'))
    rows = []
    for name, names, count in [('two-opaque-ab', ['A', 'B'], 2),
                               ('two-alpha-ab', ['A-alpha', 'B-alpha'], 2),
                               ('three-opaque-cd', ['C', 'D'], 3),
                               ('two-opaque-ba', ['B', 'A'], 2)]:
        run = root / name
        run.mkdir()
        payload = {'images': [descriptor(inputs / (n + '.png')) for n in names],
                   'num_colors': count, 'dithering': 'none', 'dithering_strength': 5.0}
        write(run / 'request.json', payload)
        predictions = []
        policies = ['ignore', 'exclude-zero', 'alpha-weight'] if name == 'two-alpha-ab' else ['ignore']
        for policy in policies:
            palette, receipt = predict([frames[n] for n in names], count, policy)
            dest = run / ('prediction-' + policy)
            dest.mkdir()
            Image.fromarray(palette[None]).save(dest / 'palette.png')
            outputs = []
            for index, n in enumerate(names):
                result = remap_rgba(frames[n], palette)
                path = dest / f'output-{index:02}.png'
                Image.fromarray(result).save(path)
                outputs.append({'path': str(path.relative_to(root)), 'png_sha256': sha(path.read_bytes()),
                                'rgba_sha256': sha(result.tobytes())})
            receipt.update({'palette_rgba': palette.tolist(), 'palette_png_sha256': sha((dest / 'palette.png').read_bytes()),
                            'outputs': outputs, 'rounding': 'numpy.rint, nearest even',
                            'palette_order_is_untested_hypothesis': True})
            write(dest / 'PREDICTION.json', receipt)
            predictions.append({'policy': policy, 'path': str((dest / 'PREDICTION.json').relative_to(root)),
                                'sha256': sha((dest / 'PREDICTION.json').read_bytes())})
        rows.append({'variant': name, 'request_sha256': sha((run / 'request.json').read_bytes()),
                     'wire_sha256': sha(json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()),
                     'predictions': predictions})
    write(root / 'PLAN.json', {'version': 1, 'endpoint': 'https://api.pixellab.ai/v2/reduce-colors',
        'max_posts': 4, 'automatic_retries': 0, 'requests': rows,
        'prediction_source_sha256': sha(Path(__file__).read_bytes()),
        'mapper_source_sha256': sha(Path(__file__).with_name('replay_pixellab_fixed_palette.py').read_bytes()),
        'scope': 'Pre-submission palette prediction on fresh deliberately separated clusters; no algorithm uniqueness or animation claim.',
        'comparisons': ['Opaque K2/K3 exact RGB multiset and output RGBA predictions, with no returned palette supplied.',
                        'Three explicitly frozen alpha-construction hypotheses; not three independent held-out predictions.',
                        'AB/BA palette order/membership/output-frame symmetry.'],
        'inputs': [{'path': str(p.relative_to(root)), 'sha256': sha(p.read_bytes())} for p in sorted(inputs.iterdir())]})
    return {'root': str(root), 'plan_sha256': sha((root / 'PLAN.json').read_bytes()), 'posts': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root)))
