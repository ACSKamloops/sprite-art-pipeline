#!/usr/bin/env python3
"""One follow-up: whether invisible black background consumes a palette entry.

Offline only. Reuses unchanged, already frozen generic palette hypothesis.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
import prepare_palette_predictions as hypothesis


def prepare(root):
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'inputs'
    inputs.mkdir()
    colors = [[0, 0, 0], [195, 142, 48], [211, 166, 72], [228, 186, 99], [242, 205, 124],
              [28, 134, 75], [38, 146, 81], [48, 156, 89], [59, 169, 96]]
    a = hypothesis.frame(colors, [512, 160, 80, 48, 32, 96, 48, 32, 16])
    b = hypothesis.frame(colors, [512, 32, 48, 80, 160, 16, 32, 48, 96])
    for name, image in [('A', a), ('B', b)]:
        image[..., 3][np.all(image[..., :3] == 0, axis=2)] = 0
        Image.fromarray(image).save(inputs / (name + '.png'))
    run = root / 'hidden-black-3'
    run.mkdir()
    payload = {'images': [hypothesis.descriptor(inputs / (n + '.png')) for n in ['A', 'B']],
               'num_colors': 3, 'dithering': 'none', 'dithering_strength': 5.0}
    hypothesis.write(run / 'request.json', payload)
    predictions = []
    for policy in ['ignore', 'exclude-zero', 'alpha-weight']:
        palette, receipt = hypothesis.predict([a, b], 3, policy)
        dest = run / ('prediction-' + policy)
        dest.mkdir()
        Image.fromarray(palette[None]).save(dest / 'palette.png')
        outputs = []
        for i, source in enumerate([a, b]):
            result = hypothesis.remap_rgba(source, palette)
            path = dest / f'output-{i:02}.png'
            Image.fromarray(result).save(path)
            outputs.append({'path': str(path.relative_to(root)), 'png_sha256': hypothesis.sha(path.read_bytes()),
                            'rgba_sha256': hypothesis.sha(result.tobytes())})
        receipt.update({'palette_rgba': palette.tolist(), 'palette_png_sha256': hypothesis.sha((dest / 'palette.png').read_bytes()),
                        'outputs': outputs, 'rounding': 'numpy.rint, nearest even',
                        'palette_order_is_untested_hypothesis': True})
        hypothesis.write(dest / 'PREDICTION.json', receipt)
        predictions.append({'policy': policy, 'path': str((dest / 'PREDICTION.json').relative_to(root)),
                            'sha256': hypothesis.sha((dest / 'PREDICTION.json').read_bytes())})
    row = {'variant': 'hidden-black-3', 'request_sha256': hypothesis.sha((run / 'request.json').read_bytes()),
           'wire_sha256': hypothesis.sha(json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()),
           'predictions': predictions}
    hypothesis.write(root / 'PLAN.json', {'version': 1, 'endpoint': 'https://api.pixellab.ai/v2/reduce-colors',
        'max_posts': 1, 'automatic_retries': 0, 'requests': [row],
        'prediction_source_sha256': hypothesis.sha(Path(hypothesis.__file__).read_bytes()),
        'preparer_source_sha256': hypothesis.sha(Path(__file__).read_bytes()),
        'mapper_source_sha256': hypothesis.sha(Path(hypothesis.__file__).with_name('replay_pixellab_fixed_palette.py').read_bytes()),
        'scope': 'Adaptive follow-up to first four predictions; frozen before its own call. Reuses old warm/green RGBs with a new invisible-only black family; not an independent new-color heldout.',
        'inputs': [{'path': str(p.relative_to(root)), 'sha256': hypothesis.sha(p.read_bytes())} for p in sorted(inputs.iterdir())],
        'binary_alpha_competitors_equivalent': 'exclude-zero and alpha-weight are identical on this binary-alpha source',
        'predeclared_comparison': 'If allRGB participates, invisible black occupies one of three palette entries, reducing this fixture to two visible output colors; predicted exact palette and output RGBA are frozen.'})
    return {'root': str(root), 'plan_sha256': hypothesis.sha((root / 'PLAN.json').read_bytes()), 'posts': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root)))
