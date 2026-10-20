#!/usr/bin/env python3
"""Bind frozen pre-response palette predictions to captured results, offline."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image

import verify_pixellab_probe_phase as binding


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rgba(path):
    with Image.open(path) as image:
        return np.array(image.convert('RGBA'))


def within(root, path):
    require(path.resolve().is_relative_to(root.resolve()), 'Prediction path escaped root')
    return path


def analyze(phase_path, phase_sha, output):
    verified = binding.verify(phase_path, phase_sha)
    phase = binding.read(phase_path)
    require(len(phase['plans']) == 1, 'Expected one prepared palette plan')
    root = Path(phase['plans'][0]['path']).parent
    plan = binding.read(root / 'PLAN.json')
    source_path = Path(__file__).with_name('prepare_palette_predictions.py')
    require(binding.sha(source_path) == plan['prediction_source_sha256'], 'Prediction source changed')
    committed = subprocess.check_output(['git', 'show', phase['source_commit'] + ':scripts/prepare_palette_predictions.py'],
                                        cwd=Path(__file__).parents[1])
    require(hashlib.sha256(committed).hexdigest() == plan['prediction_source_sha256'], 'Committed prediction source differs')
    for item in plan['inputs']:
        require(binding.sha(within(root, root / item['path'])) == item['sha256'], 'Input fixture changed')
    before = {(p['path'], p['sha256']) for p in phase['predictions']}
    current = {(str(root / p['path']), p['sha256']) for case in plan['requests'] for p in case['predictions']}
    require(before == current, 'Phase/plan prediction pins differ')
    rows = []
    for case in plan['requests']:
        run = root / case['variant']
        request = binding.read(run / 'request.json')
        actual_palette = rgba(run / 'palette.png').reshape(-1, 4)
        actual = [rgba(run / f'output-{i:02}.png') for i in range(len(request['images']))]
        predictions = []
        for item in case['predictions']:
            path = within(root, root / item['path'])
            require(binding.sha(path) == item['sha256'], 'Frozen prediction receipt changed')
            receipt = binding.read(path)
            palette_path = path.parent / 'palette.png'
            require(binding.sha(palette_path) == receipt['palette_png_sha256'], 'Frozen palette PNG changed')
            expected_palette = rgba(palette_path).reshape(-1, 4)
            require(expected_palette.tolist() == receipt['palette_rgba'], 'Palette descriptor differs')
            frame_rows = []
            for index, entry in enumerate(receipt['outputs']):
                target = within(root, root / entry['path'])
                predicted = rgba(target)
                require(binding.sha(target) == entry['png_sha256'], 'Predicted PNG changed')
                require(hashlib.sha256(predicted.tobytes()).hexdigest() == entry['rgba_sha256'], 'Predicted pixels changed')
                require(predicted.shape == actual[index].shape, 'Frame size mismatch')
                frame_rows.append({'index': index, 'pixels': int(np.prod(predicted.shape[:2])),
                    'full_rgba_mismatches': int(np.count_nonzero(np.any(predicted != actual[index], axis=2))),
                    'alpha_mismatches': int(np.count_nonzero(predicted[..., 3] != actual[index][..., 3])),
                    'predicted_png_sha256': binding.sha(target), 'actual_png_sha256': binding.sha(run / f'output-{index:02}.png')})
            predictions.append({'policy': item['policy'], 'receipt_sha256': item['sha256'],
                'predicted_palette_rgba': expected_palette.tolist(),
                'palette_order_exact': bool(np.array_equal(expected_palette, actual_palette)),
                'palette_multiset_exact': sorted(map(tuple, expected_palette)) == sorted(map(tuple, actual_palette)),
                'frames': frame_rows})
            if 'competing_visible_only_palette_rgba' in receipt:
                visible = receipt['competing_visible_only_palette_rgba']
                predictions[-1]['frozen_adaptive_visible_only_palette_rgba'] = visible
                predictions[-1]['frozen_adaptive_visible_only_order_exact'] = visible == actual_palette.tolist()
        rows.append({'variant': case['variant'], 'requested_colors': request['num_colors'],
                     'actual_palette_rgba': actual_palette.tolist(), 'predictions': predictions})
    ignore = [p for case in rows for p in case['predictions'] if p['policy'] == 'ignore']
    result = {'created_utc': datetime.now(timezone.utc).isoformat(), 'classification': 'frozen-prediction-validation-not-server-source-recovery',
        'phase_sha256': phase_sha, 'prediction_source_commit': phase['source_commit'],
        'prediction_source_sha256': plan['prediction_source_sha256'], 'analyzer_source_sha256': binding.sha(Path(__file__)),
        'bindings': verified, 'cases': rows, 'summary': {'calls': len(rows),
        'ignore_policy_exact_palette_orders': sum(p['palette_order_exact'] for p in ignore),
        'ignore_policy_rgba_entries': sum(f['pixels'] for p in ignore for f in p['frames']),
        'ignore_policy_rgba_mismatches': sum(f['full_rgba_mismatches'] for p in ignore for f in p['frames'])},
        'limits': ['Fresh deliberately separated low-K color clusters, not a general quantizer validation.',
                   'AB/BA share the same pooled histogram and repeated RGB; counts are not independent color samples.',
                   'Three alpha-construction policies were frozen competitors; a match does not identify implementation uniquely.',
                   'Local pre-response source/plan pins and producer timestamps are not third-party notarization.',
                   'REA decodes retained producer HAR; no independent network-origin or vendor-internals attestation.']}
    with output.open('x') as file:
        file.write(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase_path', type=Path)
    parser.add_argument('--phase-sha', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.phase_path, args.phase_sha, args.output)
    print(json.dumps(result['summary']))
