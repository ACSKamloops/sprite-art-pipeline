#!/usr/bin/env python3
"""One adaptive discriminator: K2 with unchanged invisible-only black inputs.

Old plans/predictions remain untouched. All new predictions precede this call.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
import prepare_palette_predictions as hypothesis


def prepare(root, previous):
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'inputs'
    inputs.mkdir()
    old = json.loads((previous / 'PLAN.json').read_bytes())
    arrays = []
    for name in ['A', 'B']:
        src = previous / 'inputs' / (name + '.png')
        pin = next(i for i in old['inputs'] if i['path'] == 'inputs/' + src.name)
        if hypothesis.sha(src.read_bytes()) != pin['sha256']:
            raise ValueError('Previous source changed')
        (inputs / src.name).write_bytes(src.read_bytes())
        arrays.append(np.array(Image.open(src).convert('RGBA')))
    run = root / 'hidden-black-2'
    run.mkdir()
    payload = {'images': [hypothesis.descriptor(inputs / (n + '.png')) for n in ['A', 'B']],
               'num_colors': 2, 'dithering': 'none', 'dithering_strength': 5.0}
    hypothesis.write(run / 'request.json', payload)
    predictions = []
    for policy in ['ignore', 'exclude-zero', 'alpha-weight']:
        palette, receipt = hypothesis.predict(arrays, 2, policy)
        dest = run / ('prediction-' + policy)
        dest.mkdir()
        Image.fromarray(palette[None]).save(dest / 'palette.png')
        outputs, visible = [], set()
        for i, source in enumerate(arrays):
            result = hypothesis.remap_rgba(source, palette)
            path = dest / f'output-{i:02}.png'
            Image.fromarray(result).save(path)
            visible.update(map(tuple, result[result[..., 3] > 0, :3]))
            outputs.append({'path': str(path.relative_to(root)), 'png_sha256': hypothesis.sha(path.read_bytes()),
                            'rgba_sha256': hypothesis.sha(result.tobytes())})
        filtered = [c.tolist() for c in palette if tuple(c[:3]) in visible]
        receipt.update({'palette_rgba': palette.tolist(), 'palette_png_sha256': hypothesis.sha((dest / 'palette.png').read_bytes()),
                        'outputs': outputs, 'rounding': 'numpy.rint, nearest even',
                        'palette_order_is_untested_hypothesis': True,
                        'competing_visible_only_palette_rgba': filtered,
                        'visible_palette_is_adaptive_hypothesis_not_recovered_code': True})
        hypothesis.write(dest / 'PREDICTION.json', receipt)
        predictions.append({'policy': policy, 'path': str((dest / 'PREDICTION.json').relative_to(root)),
                            'sha256': hypothesis.sha((dest / 'PREDICTION.json').read_bytes())})
    row = {'variant': 'hidden-black-2', 'request_sha256': hypothesis.sha((run / 'request.json').read_bytes()),
           'wire_sha256': hypothesis.sha(json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()),
           'predictions': predictions}
    hypothesis.write(root / 'PLAN.json', {'version': 1, 'endpoint': 'https://api.pixellab.ai/v2/reduce-colors',
        'max_posts': 1, 'automatic_retries': 0, 'requests': [row],
        'prediction_source_sha256': hypothesis.sha(Path(hypothesis.__file__).read_bytes()),
        'preparer_source_sha256': hypothesis.sha(Path(__file__).read_bytes()),
        'previous_plan_sha256': hypothesis.sha((previous / 'PLAN.json').read_bytes()),
        'scope': 'Adaptive K2 follow-up after K3 stripped invisible-only black from returned palette. Reuses exact source PNGs; not an independent new-color heldout.',
        'inputs': [{'path': str(p.relative_to(root)), 'sha256': hypothesis.sha(p.read_bytes())} for p in sorted(inputs.iterdir())],
        'predeclared_comparison': 'AllRGB construction predicts invisible black plus one merged visible center. Ignoring alpha in construction but returning visible-only palette predicts one-entry strip; alpha-excluding construction predicts two separated visible colors.'})
    return {'root': str(root), 'plan_sha256': hypothesis.sha((root / 'PLAN.json').read_bytes()), 'posts': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--previous', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.previous)))
