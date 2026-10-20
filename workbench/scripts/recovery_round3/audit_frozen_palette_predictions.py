#!/usr/bin/env python3
"""Read-only audit/replay of locally frozen predictions; no network/provider code."""
import argparse
import base64
from datetime import datetime
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image

PHASE_SHA = '612055f7f53bf6eadeb71b24f9d4573f8d1bccf9707f2027d1dd293c16cddcaf'
COMMIT = '7f17ca694c659ef0aa69e64ae9dec0ac4b2b7e13'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def require(value, message):
    if not value:
        raise ValueError(message)


def decode(raw):
    with Image.open(BytesIO(raw)) as image:
        image.load()
        return np.array(image.convert('RGBA'))


def descriptor(value):
    return base64.b64decode(value['base64'].split(',')[-1], validate=True)


def audit(base, repository, output):
    phase_file = base / 'PHASE-PLAN.json'
    require(sha(phase_file.read_bytes()) == PHASE_SHA, 'Phase drift')
    phase = read(phase_file)
    require(phase['source_commit'] == COMMIT, 'Frozen source commit changed')
    group, = phase['plans']
    plan_path = Path(group['path'])
    require(sha(plan_path.read_bytes()) == group['sha256'], 'Subplan drift')
    root, plan = plan_path.parent, read(plan_path)
    source_dir = output / 'source'
    source_dir.mkdir(exist_ok=False)
    source_pins = []
    for filename, expected in [('prepare_palette_predictions.py', plan['prediction_source_sha256']),
                               ('replay_pixellab_fixed_palette.py', plan['mapper_source_sha256'])]:
        archived = subprocess.check_output(['git', '-C', str(repository), 'show', f'{COMMIT}:scripts/{filename}'])
        require(sha(archived) == expected, 'Archived source hash differs from frozen plan')
        require(archived == (repository / 'scripts' / filename).read_bytes(), 'Current source differs from pre-response commit')
        (source_dir / filename).write_bytes(archived)
        source_pins.append({'file': filename, 'sha256': expected})
    sys.path.insert(0, str(source_dir))
    spec = importlib.util.spec_from_file_location('frozen_predictor', source_dir / 'prepare_palette_predictions.py')
    predictor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predictor)
    for entry in plan['inputs']:
        require(sha((root / entry['path']).read_bytes()) == entry['sha256'], 'Frozen input drift')
    phase_predictions = {Path(p['path']).resolve(): p['sha256'] for p in phase['predictions']}
    binding_path = output / 'BINDINGS.json'
    bindings = read(binding_path)
    require(bindings['phase_sha256'] == PHASE_SHA and bindings['cases_checked'] == 4
            and bindings['pngs_bound'] == 12 and bindings['failures'] == [], 'Expected independent verifier receipt')
    rows, timestamps = [], []
    for case in plan['requests']:
        run = root / case['variant']
        require(sha((run / 'request.json').read_bytes()) == case['request_sha256'], 'Request drift')
        request = read(run / 'request.json')
        wire = json.dumps(request, separators=(',', ':'), ensure_ascii=False).encode()
        require(sha(wire) == case['wire_sha256'], 'Wire drift')
        entry, = read(run / 'network.har')['log']['entries']
        timestamps.append(entry['startedDateTime'])
        require(datetime.fromisoformat(phase['prepared_utc']) <= datetime.fromisoformat(entry['startedDateTime']), 'Local timestamp order inconsistent')
        require(entry['request']['postData']['text'].encode() == wire, 'Producer wire mismatch')
        result = read(run / 'response.json')
        images = [decode(descriptor(v)) for v in request['images']]
        actual = []
        for i, value in enumerate(result['images']):
            raw = descriptor(value)
            require(raw == (run / f'output-{i:02}.png').read_bytes(), 'Returned frame byte mismatch')
            actual.append(decode(raw))
        actual_palette = decode(descriptor(result['palette']))
        require(descriptor(result['palette']) == (run / 'palette.png').read_bytes(), 'Returned palette byte mismatch')
        predictions = []
        for frozen in case['predictions']:
            receipt_path = root / frozen['path']
            require(sha(receipt_path.read_bytes()) == frozen['sha256'] == phase_predictions[receipt_path.resolve()], 'Prediction receipt drift')
            receipt = read(receipt_path)
            palette, metadata = predictor.predict(images, request['num_colors'], frozen['policy'])
            require(palette.tolist() == receipt['palette_rgba'], 'Archived predictor does not replay frozen palette')
            require(np.allclose(metadata['float_centers_oklab'], receipt['float_centers_oklab'], rtol=0, atol=1e-14), 'Float-center replay differs')
            palette_file = receipt_path.parent / 'palette.png'
            require(sha(palette_file.read_bytes()) == receipt['palette_png_sha256'], 'Frozen palette PNG drift')
            require(np.array_equal(decode(palette_file.read_bytes()), palette[None]), 'Frozen palette RGBA drift')
            frames = []
            for i, frame in enumerate(receipt['outputs']):
                predicted_file = root / frame['path']
                predicted_raw = predicted_file.read_bytes()
                predicted_rgba = decode(predicted_raw)
                require(sha(predicted_raw) == frame['png_sha256'] and sha(predicted_rgba.tobytes()) == frame['rgba_sha256'], 'Frozen predicted output drift')
                replay = predictor.remap_rgba(images[i], palette)
                require(np.array_equal(replay, predicted_rgba), 'Archived mapper does not replay frozen predicted output')
                mismatch = np.any(predicted_rgba != actual[i], axis=-1)
                hidden = images[i][..., 3] == 0
                frames.append({'index': i, 'pixels': int(mismatch.size), 'rgba_mismatches': int(mismatch.sum()),
                    'alpha_mismatches': int(np.count_nonzero(images[i][..., 3] != actual[i][..., 3])),
                    'hidden_source_pixels': int(hidden.sum()),
                    'hidden_rgb_changed': int(np.count_nonzero(np.any(images[i][..., :3] != actual[i][..., :3], axis=-1) & hidden)),
                    'frozen_prediction_png_bytes_equal_actual': predicted_raw == (run / f'output-{i:02}.png').read_bytes()})
            predictions.append({'policy': frozen['policy'], 'frozen_receipt_sha256': frozen['sha256'],
                'palette_rgba_order_exact': np.array_equal(palette[None], actual_palette),
                'frozen_palette_png_bytes_equal_actual': palette_file.read_bytes() == (run / 'palette.png').read_bytes(),
                'replayed_source_and_frozen_rgba_equal': True, 'frames': frames})
        rea = read(run / 'REA-EVIDENCE.json')
        rows.append({'variant': case['variant'], 'num_colors': request['num_colors'],
            'actual_palette_rgba': actual_palette.reshape(-1, 4).tolist(), 'rea_evidence_id': rea['evidence_id'],
            'har_sha256': sha((run / 'network.har').read_bytes()), 'predictions': predictions})
    ab, ba = root / 'two-opaque-ab', root / 'two-opaque-ba'
    symmetry = {'palette_png_bytes_equal': (ab / 'palette.png').read_bytes() == (ba / 'palette.png').read_bytes(),
        'A_output_png_equal_after_permutation': (ab / 'output-00.png').read_bytes() == (ba / 'output-01.png').read_bytes(),
        'B_output_png_equal_after_permutation': (ab / 'output-01.png').read_bytes() == (ba / 'output-00.png').read_bytes()}
    ignored = [p for c in rows for p in c['predictions'] if p['policy'] == 'ignore']
    report = {'classification': 'independent offline audit of locally frozen predictions; not server-source attestation',
        'source_commit': COMMIT, 'phase_sha256': PHASE_SHA, 'plan_sha256': group['sha256'],
        'source_pins': source_pins, 'verifier_receipt_sha256': sha(binding_path.read_bytes()),
        'local_phase_prepared_utc': phase['prepared_utc'], 'producer_started_utc': timestamps,
        'cases': rows, 'AB_BA_symmetry': symmetry,
        'totals': {'captured_calls': 4, 'returned_pngs_bound': 12, 'reported_generations': bindings['reported_generations'],
            'ignore_policy_exact_palette_orders': sum(p['palette_rgba_order_exact'] for p in ignored),
            'ignore_policy_rgba_entries': sum(f['pixels'] for p in ignored for f in p['frames']),
            'ignore_policy_rgba_mismatches': sum(f['rgba_mismatches'] for p in ignored for f in p['frames'])},
        'limits': ['Source/plan pins and producer timestamps are local records, not third-party notarization.',
            'Deliberately separated lowK clusters constrain centroid/alpha/presentation behavior, not initialization identity or general clustering.',
            'AB/BA have the same pooled histogram; opaque/alpha cases share RGB; repeated pixel counts are not independent samples.',
            'Three frozen alpha policies are competing alternatives, not three independent validations.',
            'Older32-color case remains inexact; no private-source, dithering, automatic-size or animation-internal claim.']}
    with (output / 'FRESH-PREDICTION-AUDIT.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report['totals']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit(args.base, args.repository, args.output)
