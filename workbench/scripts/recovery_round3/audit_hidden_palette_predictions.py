#!/usr/bin/env python3
"""Offline audit of one separately frozen adaptive hidden-color experiment."""
import argparse
from datetime import datetime
import importlib.util
from pathlib import Path
import json
import subprocess
import sys

import numpy as np
from audit_frozen_palette_predictions import sha, read, require, decode, descriptor


def audit(phase_path, expected, repository, preparer, output, bindings_path, previous_root=None):
    require(sha(phase_path.read_bytes()) == expected, 'Phase drift')
    phase = read(phase_path)
    group, = phase['plans']
    plan_path = Path(group['path'])
    require(sha(plan_path.read_bytes()) == group['sha256'], 'Subplan drift')
    plan, root = read(plan_path), plan_path.parent
    previous_plan = None
    if 'previous_plan_sha256' in plan:
        require(previous_root is not None and sha((previous_root / 'PLAN.json').read_bytes()) == plan['previous_plan_sha256'], 'Previous frozen plan mismatch')
        previous_plan = read(previous_root / 'PLAN.json')
    commit = phase['source_commit']
    output.mkdir(exist_ok=False)
    source = output / 'source'
    source.mkdir()
    pins = []
    for name, key in [('prepare_palette_predictions.py', 'prediction_source_sha256'),
                      ('replay_pixellab_fixed_palette.py', 'mapper_source_sha256'),
                      (preparer, 'preparer_source_sha256')]:
        raw = subprocess.check_output(['git', '-C', str(repository), 'show', f'{commit}:scripts/{name}'])
        expected_source = plan.get(key)
        if expected_source is None:
            require(key == 'mapper_source_sha256' and previous_plan is not None, 'Missing frozen source pin')
            expected_source = previous_plan[key]
        require(sha(raw) == expected_source, 'Archived source does not match frozen plan')
        (source / name).write_bytes(raw)
        pins.append({'filename': name, 'sha256': sha(raw), 'pin_inherited_from_previous_plan': key not in plan})
    sys.path.insert(0, str(source))
    spec = importlib.util.spec_from_file_location('hidden_frozen_predictor', source / 'prepare_palette_predictions.py')
    predictor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predictor)
    for f in plan['inputs']:
        require(sha((root / f['path']).read_bytes()) == f['sha256'], 'Input drift')
        if previous_root is not None:
            require((root / f['path']).read_bytes() == (previous_root / f['path']).read_bytes(), 'Reused input is not byte-identical')
    case, = plan['requests']
    run = root / case['variant']
    require(sha((run / 'request.json').read_bytes()) == case['request_sha256'], 'Request drift')
    request = read(run / 'request.json')
    require(sha(json.dumps(request, separators=(',', ':'), ensure_ascii=False).encode()) == case['wire_sha256'], 'Wire drift')
    bindings = read(bindings_path)
    require(bindings['phase_sha256'] == expected and bindings['cases_checked'] == 1 and bindings['failures'] == [], 'Binding receipt mismatch')
    images = [decode(descriptor(v)) for v in request['images']]
    response = read(run / 'response.json')
    actual_raw = [descriptor(v) for v in response['images']]
    actual = [decode(raw) for raw in actual_raw]
    require(len(actual) == len(images) == 2, 'Two frames required')
    for i, raw in enumerate(actual_raw):
        require(raw == (run / f'output-{i:02}.png').read_bytes(), 'Output file mismatch')
    palette_raw = descriptor(response['palette'])
    require(palette_raw == (run / 'palette.png').read_bytes(), 'Palette file mismatch')
    actual_palette = decode(palette_raw).reshape(-1, 4)
    visible = set(tuple(map(int, pixel[:3])) for result in actual for pixel in result.reshape(-1, 4) if pixel[3] > 0)
    all_rgb = set(tuple(map(int, pixel[:3])) for result in actual for pixel in result.reshape(-1, 4))
    frozen_pins = {Path(p['path']).resolve(): p['sha256'] for p in phase['predictions']}
    policies = []
    for entry in case['predictions']:
        receipt_path = root / entry['path']
        require(sha(receipt_path.read_bytes()) == entry['sha256'] == frozen_pins[receipt_path.resolve()], 'Frozen prediction changed')
        receipt = read(receipt_path)
        predicted_palette, metadata = predictor.predict(images, request['num_colors'], entry['policy'])
        require(predicted_palette.tolist() == receipt['palette_rgba'], 'Archived predictor palette replay mismatch')
        require(np.allclose(metadata['float_centers_oklab'], receipt['float_centers_oklab'], rtol=0, atol=1e-14), 'Float-center replay mismatch')
        require(sha((receipt_path.parent / 'palette.png').read_bytes()) == receipt['palette_png_sha256'], 'Prediction palette PNG drift')
        frames = []
        predicted_visible = set()
        for i, frozen in enumerate(receipt['outputs']):
            raw = (root / frozen['path']).read_bytes()
            rgba = decode(raw)
            require(sha(raw) == frozen['png_sha256'] and sha(rgba.tobytes()) == frozen['rgba_sha256'], 'Frozen output drift')
            require(np.array_equal(predictor.remap_rgba(images[i], predicted_palette), rgba), 'Archived mapper replay mismatch')
            predicted_visible.update(tuple(map(int, p[:3])) for p in rgba.reshape(-1, 4) if p[3] > 0)
            mask = np.any(rgba != actual[i], axis=-1)
            frames.append({'index': i, 'rgba_mismatches': int(mask.sum()),
                'visible_rgba_mismatches': int(np.count_nonzero(mask & (images[i][..., 3] > 0))),
                'hidden_rgba_mismatches': int(np.count_nonzero(mask & (images[i][..., 3] == 0))),
                'predicted_png_bytes_equal_actual': raw == actual_raw[i]})
        filtered = [p for p in predicted_palette.tolist() if tuple(p[:3]) in visible]
        frozen_visible = receipt.get('competing_visible_only_palette_rgba')
        if frozen_visible is not None:
            locally_filtered = [p for p in predicted_palette.tolist() if tuple(p[:3]) in predicted_visible]
            require(locally_filtered == frozen_visible, 'Frozen visible-only prediction does not replay from local outputs')
        policies.append({'policy': entry['policy'], 'prediction_receipt_sha256': entry['sha256'],
            'predicted_palette_rgba': predicted_palette.tolist(), 'palette_order_exact': np.array_equal(predicted_palette, actual_palette),
            'posthoc_actual_visible_union_filtered_prediction_order_equal': filtered == actual_palette.tolist(),
            'visible_only_palette_prediction_frozen': frozen_visible is not None,
            'frozen_visible_only_palette_prediction': frozen_visible,
            'frozen_visible_only_palette_order_exact': frozen_visible == actual_palette.tolist() if frozen_visible is not None else None,
            'frames': frames})
    strip_mapping = []
    for i, image in enumerate(images):
        reconstructed = predictor.remap_rgba(image, actual_palette)
        mismatch = np.any(reconstructed != actual[i], axis=-1)
        strip_mapping.append({'index': i, 'full_rgba_mismatches': int(mismatch.sum()),
            'visible_mismatches': int(np.count_nonzero(mismatch & (image[..., 3] > 0))),
            'hidden_mismatches': int(np.count_nonzero(mismatch & (image[..., 3] == 0))),
            'alpha_exact': bool(np.array_equal(image[..., 3], actual[i][..., 3]))})
    producer, = read(run / 'network.har')['log']['entries']
    require(datetime.fromisoformat(phase['prepared_utc']) <= datetime.fromisoformat(producer['startedDateTime']), 'Local timestamp order inconsistent')
    report = {'classification': 'separately frozen adaptive fixture audit; no private-stage identification',
        'source_commit': commit, 'phase_sha256': expected, 'plan_sha256': group['sha256'], 'source_pins': pins,
        'variant': case['variant'], 'requested_num_colors': request['num_colors'],
        'reported_n_colors': response['n_colors'], 'returned_palette_rgba': actual_palette.tolist(),
        'visible_output_rgb_union': sorted(visible), 'all_output_rgb_union': sorted(all_rgb),
        'returned_strip_equals_visible_union_set': set(map(tuple, actual_palette[:, :3])) == visible,
        'policies': policies, 'quarter_L_remap_using_returned_strip': strip_mapping,
        'binding_receipt_sha256': sha(bindings_path.read_bytes()),
        'rea_evidence_id': read(run / 'REA-EVIDENCE.json')['evidence_id'],
        'phase_prepared_utc': phase['prepared_utc'], 'producer_started_utc': producer['startedDateTime'],
        'limits': ['Adaptive follow-up frozen before its own response; reuses earlier visible RGBs, not a new-color holdout.',
            'Binary alpha makes exclude-zero and alpha-weight equivalent competing policies.',
            'Visible-union filtering is a post-hoc descriptive relationship, not a recovered internal stage.',
            'Local pins/timestamps and REA/producer binding are not external network attestation.']}
    (output / 'AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'variant': report['variant'], 'requested': request['num_colors'],
        'reported': response['n_colors'], 'policy_frame_misses': [(p['policy'], [f['rgba_mismatches'] for f in p['frames']]) for p in policies],
        'returned_strip_remap': strip_mapping}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase_path', type=Path)
    parser.add_argument('--phase-sha', required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--preparer', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--bindings', type=Path, required=True)
    parser.add_argument('--previous-root', type=Path)
    args = parser.parse_args()
    audit(args.phase_path, args.phase_sha, args.repository, args.preparer, args.output, args.bindings, args.previous_root)
