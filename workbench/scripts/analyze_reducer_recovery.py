#!/usr/bin/env python3
"""Offline byte binding and candidate replay for retained reducer probes."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image

from replay_pixellab_fixed_palette import remap_rgba, oklab, POLICY


def image(value):
    raw = base64.b64decode(value['base64'].split(',')[-1], validate=True)
    return raw, np.array(Image.open(BytesIO(raw)).convert('RGBA'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def analyze(base):
    paths = [(base, 'fixed-none'), (base, 'fixed-repeat'), (base, 'fixed-2x2'),
             (Path(str(base) + '-phase2'), 'six-color-none'),
             (Path(str(base) + '-phase2'), 'bw-2x2-zero'),
             (Path(str(base) + '-phase2'), 'bw-2x2-ten'),
             (Path(str(base) + '-holdout'), 'weighted-holdout')]
    records, failures = [], []
    for root, name in paths:
        try:
            run = root / name
            load = lambda p: json.loads(p.read_bytes())
            request_bytes = (run / 'request.json').read_bytes()
            request = json.loads(request_bytes)
            plan = load(root / 'PLAN.json')
            require(next(r['request_sha256'] for r in plan['requests'] if r['variant'] == name) == digest(request_bytes), 'Frozen request hash')
            har_bytes = (run / 'network.har').read_bytes()
            har = json.loads(har_bytes)['log']['entries']
            rea = load(run / 'REA.json')
            require(len(har) == 1 and rea['normalized_result']['total_records'] == 1, 'Capture count')
            require(rea['subject']['digest']['sha256'] == digest(har_bytes), 'REA subject binding')
            require(rea['normalized_result']['records'][0]['reported'] == har[0], 'REA record binding')
            require(har[0]['request']['method'] == 'POST' and har[0]['request']['url'] == 'https://api.pixellab.ai/v2/reduce-colors', 'Captured endpoint')
            require(json.loads(har[0]['request']['postData']['text']) == request, 'Submitted body binding')
            response = load(run / 'response.json')
            require(json.loads(har[0]['response']['content']['text']) == response and har[0]['response']['status'] == 200, 'Returned body binding')
            require(len(request['images']) == len(response['images']) == 2, 'Frame count')
            _, palette = image(request['palette_image'])
            palette = palette.reshape(-1, 4)
            nondithered = request['dithering'] == 'none' or request['dithering_strength'] == 0
            frame_stats = []
            for i, (src, value) in enumerate(zip(request['images'], response['images'])):
                source_png, source = image(src)
                returned_png, actual = image(value)
                require(returned_png == (run / f'output-{i:02}.png').read_bytes(), 'Returned/extracted PNG binding')
                require(source.shape == actual.shape, 'Canvas')
                replay = remap_rgba(source, palette)
                delta = oklab(source[..., :3])[:, :, None, :] - oklab(palette[:, :3])[None, None, :, :]
                unweighted = palette[np.argmin(np.sum(delta**2, axis=-1), axis=-1), :3]
                srgb = palette[np.argmin(np.sum((source[:, :, None, :3].astype(float) - palette[None, None, :, :3])**2, axis=-1), axis=-1), :3]
                frame_stats.append({'index': i, 'pixels': int(source.shape[0] * source.shape[1]),
                                    'source_png_sha256': digest(source_png), 'returned_png_sha256': digest(returned_png),
                                    'alpha_exact': bool(np.array_equal(source[..., 3], actual[..., 3])),
                                    'weighted_oklab_rgba_mismatches': int(np.count_nonzero(np.any(replay != actual, axis=2))),
                                    'unweighted_oklab_rgb_mismatches': int(np.count_nonzero(np.any(unweighted != actual[..., :3], axis=2))),
                                    'srgb_rgb_mismatches': int(np.count_nonzero(np.any(srgb != actual[..., :3], axis=2)))})
            records.append({'case': name, 'root': str(root), 'rea_evidence_id': rea['evidence_id'],
                            'rea_har_sha256': digest(har_bytes), 'rea_authority': rea['authority'],
                            'nondithered_or_zero_strength': nondithered, 'usage': response.get('usage'), 'frames': frame_stats})
        except (OSError, ValueError, KeyError, StopIteration) as error:
            failures.append({'case': name, 'error': str(error)})
    repeat_exact = all((base / 'fixed-none' / f'output-{i:02}.png').read_bytes() ==
                       (base / 'fixed-repeat' / f'output-{i:02}.png').read_bytes() for i in range(2))
    zero_exact = all((base / 'fixed-none' / f'output-{i:02}.png').read_bytes() ==
                     (Path(str(base) + '-phase2') / 'bw-2x2-zero' / f'output-{i:02}.png').read_bytes() for i in range(2))
    nondithered = [c for c in records if c['nondithered_or_zero_strength']]
    holdout_request = json.loads((Path(str(base) + '-holdout') / 'weighted-holdout/request.json').read_bytes())
    _, holdout_source = image(holdout_request['images'][0])
    distinct = {tuple(color) for color in holdout_source[..., :3].reshape(-1, 3)}
    calibration_request = json.loads((base / 'fixed-none/request.json').read_bytes())
    _, calibration_source = image(calibration_request['images'][0])
    calibration = {tuple(color) for color in calibration_source[..., :3].reshape(-1, 3)}
    return {'version': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'cases': records,
            'failures': failures, 'policy': POLICY, 'repeat_png_bytes_exact': repeat_exact,
            'zero_strength_png_bytes_exact_to_none': zero_exact,
            'nondithered_rgba_entries_verified': sum(f['pixels'] for c in nondithered for f in c['frames']),
            'nondithered_rgba_mismatches': sum(f['weighted_oklab_rgba_mismatches'] for c in nondithered for f in c['frames']),
            'heldout_rgb_samples_tested': int(holdout_source.shape[0] * holdout_source.shape[1]),
            'heldout_distinct_rgb_colors_tested': len(distinct),
            'heldout_distinct_previously_unseen_rgb_colors_tested': len(distinct - calibration),
            'heldout_rgba_entries_tested': 8192,
            'total_paid_posts': len(records), 'generation_usage': round(sum(c['usage']['generations'] for c in records), 4),
            'private_source_recovered': False, 'pixminimax_uses_this_reducer_known': False,
            'scope': 'Observed fixed opaque-palette behavior, exact input/result/capture binding and offline candidate replay; calibration/repeat pixels are not independent samples. No automatic palette clustering, source weights, animation cutout or temporal de-flicker recovery.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.base)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['total_paid_posts', 'generation_usage', 'nondithered_rgba_entries_verified',
                                           'nondithered_rgba_mismatches', 'repeat_png_bytes_exact', 'zero_strength_png_bytes_exact_to_none', 'failures']}))
    raise SystemExit(bool(result['failures'] or result['nondithered_rgba_mismatches']))
