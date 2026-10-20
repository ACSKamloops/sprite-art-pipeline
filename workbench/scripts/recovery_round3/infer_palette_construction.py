#!/usr/bin/env python3
"""Bounded, authored palette hypotheses. Offline; not recovered PixelLab code."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image

PLAN = {
    'classification': 'post-hoc offline inference; never label original server/client code',
    'max_iterations': 20,
    'distance': '.25*dL^2+da^2+db^2 in Oklab',
    'mean_spaces': ['Oklab', 'sRGB'],
    'initializers': {
        'frequency-farthest': 'Most frequent RGB first (lexicographic tie), then maximum minimum squared weighted-Lab distance; no count score thereafter',
        'lightness-weighted-farthest': 'Minimum/maximum Oklab L first; then maximum minDistanceSquared*pixelCount',
        'histogram-topk': 'TopK pixel-frequency RGBs, ties lexicographic RGB'},
    'output_conditioned': 'Start at service rounded RGB palette converted to Oklab; infer latent float centers by the same bounded Lloyd updates. This is not independent prediction.',
    'empty_clusters': 'Keep previous center unchanged; no reseeding',
    'nearest_ties': 'First center index',
    'presentation': 'Inverse Oklab/sRGB transfer, clip0..255, numpy.rint ties-to-even',
    'termination': 'Stop on identical nearest assignment vector, or20 iterations; no random seeds/restarts/parameter search',
    'rgb_order': 'Lexicographic unique RGB; histogram counts retain exact source-pixel frequency',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def image(value):
    raw = base64.b64decode(value['base64'].split(',')[-1], validate=True)
    with Image.open(BytesIO(raw)) as decoded:
        return raw, np.array(decoded.convert('RGBA'))


def rgb_from_lab(lab, mapper):
    linear = (lab @ np.linalg.inv(mapper.M2).T) ** 3 @ np.linalg.inv(mapper.M1).T
    linear = np.maximum(linear, 0)
    rgb = np.where(linear <= .0031308, 12.92 * linear, 1.055 * linear ** (1 / 2.4) - .055) * 255
    return rgb


def nearest(lab, centers):
    d2 = np.sum((lab[:, None] - centers[None]) ** 2 * np.array([.25, 1, 1]), axis=-1)
    return np.argmin(d2, axis=1), np.min(d2, axis=1)


def initial(lab, counts, k, mode):
    if mode == 'histogram-topk':
        return lab[np.argsort(-counts, kind='stable')[:k]].copy()
    chosen = [int(np.argmax(counts))] if mode == 'frequency-farthest' else [int(np.argmin(lab[:, 0])), int(np.argmax(lab[:, 0]))]
    require(len(set(chosen)) == len(chosen), 'Distinct endpoints required')
    while len(chosen) < k:
        _, score = nearest(lab, lab[chosen])
        if mode == 'lightness-weighted-farthest':
            score = score * counts
        score[chosen] = -1
        chosen.append(int(np.argmax(score)))
    return lab[chosen].copy()


def refine(rgb, lab, counts, target, observed, centers, space, mapper):
    target_set = set(map(tuple, target))
    labels, _ = nearest(lab, centers)
    history = []
    for step in range(PLAN['max_iterations'] + 1):
        float_rgb = rgb_from_lab(centers, mapper)
        rounded = np.clip(np.rint(float_rgb), 0, 255).astype(np.uint8)
        rounded_labels, _ = nearest(lab, mapper.oklab(rounded))
        _, distance = nearest(lab, centers)
        empty = sum(not np.any(labels == i) for i in range(len(centers)))
        float_emission = rounded[labels]
        rounded_emission = rounded[rounded_labels]
        record = {'iteration': step, 'objective': float(np.dot(distance, counts)), 'empty_clusters': empty,
            'rounded_palette_intersection': len(set(map(tuple, rounded)) & target_set),
            'rounded_palette_set_equal': set(map(tuple, rounded)) == target_set and len(set(map(tuple, rounded))) == len(target),
            'float_assignment_emitted_rgb_mismatches': int(np.sum(counts[np.any(float_emission != observed, axis=1)])),
            'rounded_palette_mapper_rgb_mismatches': int(np.sum(counts[np.any(rounded_emission != observed, axis=1)])),
            'max_srgb_float_distance_to_rounded_service_same_index': float(np.max(np.abs(float_rgb - target))) if len(target) == len(centers) else None}
        history.append(record)
        if step == PLAN['max_iterations']:
            break
        updated = centers.copy()
        for i in range(len(centers)):
            mask = labels == i
            if not np.any(mask):
                continue
            updated[i] = (np.average(lab[mask], weights=counts[mask], axis=0) if space == 'Oklab'
                else mapper.oklab(np.average(rgb[mask], weights=counts[mask], axis=0)))
        next_labels, _ = nearest(lab, updated)
        record['next_assignment_changed_pixels'] = int(np.sum(counts[next_labels != labels]))
        record['next_max_weighted_lab_center_shift'] = float(np.sqrt(np.max(np.sum((updated - centers) ** 2 * [.25, 1, 1], axis=1))))
        converged = bool(np.array_equal(next_labels, labels))
        centers, labels = updated, next_labels
        if converged:
            # Record the actual updated fixed point, not its preceding centers.
            float_rgb = rgb_from_lab(centers, mapper)
            rounded = np.clip(np.rint(float_rgb), 0, 255).astype(np.uint8)
            rounded_labels, _ = nearest(lab, mapper.oklab(rounded))
            _, distance = nearest(lab, centers)
            history.append({'iteration': step + 1, 'objective': float(np.dot(distance, counts)),
                'empty_clusters': sum(not np.any(labels == i) for i in range(len(centers))),
                'rounded_palette_intersection': len(set(map(tuple, rounded)) & target_set),
                'rounded_palette_set_equal': set(map(tuple, rounded)) == target_set and len(set(map(tuple, rounded))) == len(target),
                'float_assignment_emitted_rgb_mismatches': int(np.sum(counts[np.any(rounded[labels] != observed, axis=1)])),
                'rounded_palette_mapper_rgb_mismatches': int(np.sum(counts[np.any(rounded[rounded_labels] != observed, axis=1)])),
                'converged_assignments': True})
            break
    return {'mean_space': space, 'history': history, 'converged': bool(history[-1].get('converged_assignments', False)),
        'final_palette_rgb': rounded.tolist(), 'final_centers_oklab': centers.tolist(),
        'final_centers_srgb_float': float_rgb.tolist(), 'final': history[-1]}


def analyze(root, output, mapper_path):
    output.mkdir(parents=True, exist_ok=False)
    # This plan is written before candidate execution; captured outputs are already known.
    (output / 'PLAN.json').write_text(json.dumps(PLAN, indent=2) + '\n')
    mapper_raw = mapper_path.read_bytes()
    require(sha(mapper_raw) == '6272a72903dd4a7d330e7eeb5c8e7df321cbc84c6ba9f9485404a640857ba742', 'Mapper snapshot drift')
    snapshot = output / 'inferred_mapper.source.py'
    snapshot.write_bytes(mapper_raw)
    spec = importlib.util.spec_from_file_location('inferred_mapper', snapshot)
    mapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mapper)
    prior_path = root / 'analysis-20261014/PALETTE-FINDINGS.json'
    require(sha(prior_path.read_bytes()) == 'ec5cb611f070081c975906870873e85796de0f3801bcb5bbb3ae98dd2ab46dba', 'Prior binding receipt drift')
    prior = {case['variant']: case for case in read(prior_path)['cases']}
    plan = read(root / 'PLAN.json')
    cases = []
    for case in plan['requests']:
        run = root / case['variant']
        require(sha((run / 'request.json').read_bytes()) == case['request_sha256'], 'Frozen request changed')
        require(sha((run / 'response.json').read_bytes()) == prior[case['variant']]['response_file_sha256'], 'Bound response changed')
        source, actual = [], []
        payload, response = read(run / 'request.json'), read(run / 'response.json')
        for i, (before, after) in enumerate(zip(payload['images'], response['images'])):
            a_raw, a = image(before)
            b_raw, b = image(after)
            require(sha(a_raw) == prior[case['variant']]['frames'][i]['source_png_sha256'], 'Source PNG changed')
            require(sha(b_raw) == prior[case['variant']]['frames'][i]['output_png_sha256'], 'Output PNG changed')
            source.append(a.reshape(-1, 4))
            actual.append(b.reshape(-1, 4))
        raw, palette = image(response['palette'])
        require(sha(raw) == prior[case['variant']]['palette_png_sha256'], 'Palette changed')
        target = palette.reshape(-1, 4)[:, :3]
        source, actual = np.concatenate(source), np.concatenate(actual)
        require(np.all(source[:, 3] == 255) and np.all(actual[:, 3] == 255), 'Opaque experiment only')
        rgb, inverse, counts = np.unique(source[:, :3], return_inverse=True, return_counts=True, axis=0)
        observed = np.zeros_like(rgb)
        for i in range(len(rgb)):
            values = np.unique(actual[inverse == i, :3], axis=0)
            require(len(values) == 1, 'Same RGB has conflicting observed mapping')
            observed[i] = values[0]
        lab = mapper.oklab(rgb)
        target_lab = mapper.oklab(target)
        conditional = [refine(rgb, lab, counts, target, observed, target_lab.copy(), space, mapper) for space in PLAN['mean_spaces']]
        independent = []
        for mode in PLAN['initializers']:
            for space in PLAN['mean_spaces']:
                result = refine(rgb, lab, counts, target, observed, initial(lab, counts, len(target), mode), space, mapper)
                independent.append({'initializer': mode, **result})
        cases.append({'variant': case['variant'], 'pixels': int(counts.sum()), 'unique_rgb': len(rgb),
            'service_palette_rgb': target.tolist(), 'output_conditioned_refinements': conditional, 'independent_candidates': independent})
    report = {'classification': 'bounded authored offline hypotheses; no source recovery or held-out validation',
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'script_sha256': sha(Path(__file__).read_bytes()),
        'plan_sha256': sha((output / 'PLAN.json').read_bytes()), 'mapper_sha256': sha(mapper_raw),
        'prior_bound_receipt_sha256': sha(prior_path.read_bytes()), 'cases': cases,
        'limits': ['Output-conditioned refinement uses returned palette and cannot independently predict it',
            'Independent seeds are fixed post-hoc candidates, not blind validation; AB4/CC4 have duplicate histograms',
            'No random grid, reinitialization, parameter fitting, provider/credential/network calls']}
    (output / 'RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
    for case in cases:
        print(json.dumps({'case': case['variant'],
            'conditional': [(r['mean_space'], r['final']['rounded_palette_intersection'], r['final']['rounded_palette_mapper_rgb_mismatches'], len(r['history']) - 1) for r in case['output_conditioned_refinements']],
            'independent': [(r['initializer'], r['mean_space'], r['final']['rounded_palette_intersection'], r['final']['rounded_palette_mapper_rgb_mismatches'], r['converged']) for r in case['independent_candidates']]}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--mapper', required=True, type=Path)
    args = parser.parse_args()
    analyze(args.root, args.output, args.mapper)
