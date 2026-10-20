#!/usr/bin/env python3
"""Inspect an existing bounded candidate; no new fitting/search or API access."""
import argparse
import base64
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image


def read(path):
    return json.loads(path.read_bytes())


def analyze(root, experiment, mapper_path):
    spec = importlib.util.spec_from_file_location('round3_methods', Path(__file__).with_name('infer_palette_construction.py'))
    methods = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(methods)
    spec = importlib.util.spec_from_file_location('mapper', mapper_path)
    mapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mapper)
    results_path = experiment / 'RESULTS.json'
    results = read(results_path)
    case = next(c for c in results['cases'] if c['variant'] == 'joint-ab-32')
    candidate = next(c for c in case['independent_candidates'] if c['initializer'] == 'lightness-weighted-farthest' and c['mean_space'] == 'Oklab')
    prior_path = root / 'analysis-20261014/PALETTE-FINDINGS.json'
    require = methods.require
    require(methods.sha(prior_path.read_bytes()) == results['prior_bound_receipt_sha256'], 'Prior receipt changed')
    prior = next(c for c in read(prior_path)['cases'] if c['variant'] == 'joint-ab-32')
    old_failures = []
    for center in prior['centroids']:
        model = next(m for m in center['models'] if m['weighting'] == 'pixel-frequency' and m['space'] == 'Oklab' and m['rounding'] == 'rint')
        if not model['exact']:
            old_failures.append((center, model))
    payload = read(root / 'joint-ab-32/request.json')
    pixels = []
    for value in payload['images']:
        raw = base64.b64decode(value['base64'].split(',')[-1], validate=True)
        pixels.append(np.array(Image.open(BytesIO(raw)).convert('RGBA')).reshape(-1, 4)[:, :3])
    rgb, counts = np.unique(np.concatenate(pixels), axis=0, return_counts=True)
    lab = mapper.oklab(rgb)
    centers = np.array(candidate['final_centers_oklab'])
    rounded = np.array(candidate['final_palette_rgb'])
    target = np.array(case['service_palette_rgb'])
    float_assignment, _ = methods.nearest(lab, centers)
    rounded_assignment, _ = methods.nearest(lab, mapper.oklab(rounded))
    service_assignment, _ = methods.nearest(lab, mapper.oklab(target))
    center_reports = []
    for center, old in old_failures:
        target_color = np.array(center['palette_rgb'])
        indices = np.flatnonzero(np.all(rounded == target_color, axis=1))
        require(len(indices) == 1, 'Previously failed color not uniquely present in candidate')
        index = int(indices[0])
        target_index = int(np.flatnonzero(np.all(target == target_color, axis=1))[0])
        latent_mask, observed_mask = float_assignment == index, service_assignment == target_index
        mean = np.average(lab[latent_mask], weights=counts[latent_mask], axis=0)
        require(np.allclose(mean, centers[index], atol=1e-14, rtol=0), 'Candidate not a weighted Lloyd fixed point')
        mean_rgb = methods.rgb_from_lab(mean, mapper)
        rounded_mean = np.clip(np.rint(mean_rgb), 0, 255).astype(np.uint8)
        require(np.array_equal(rounded_mean, target_color), 'Latent mean does not round to service color')
        center_reports.append({'service_rgb': target_color.tolist(),
            'rounded_assignment_mean_srgb': old['centroid_srgb_float'],
            'rounded_assignment_mean_presented_rgb': old['predicted_rgb'],
            'latent_float_assignment_mean_srgb': mean_rgb.tolist(),
            'latent_float_assignment_mean_presented_rgb': rounded_mean.tolist(),
            'observed_cluster_pixels': int(np.sum(counts[observed_mask])),
            'latent_cluster_pixels': int(np.sum(counts[latent_mask])),
            'gained_pixels': int(np.sum(counts[latent_mask & ~observed_mask])),
            'lost_pixels': int(np.sum(counts[observed_mask & ~latent_mask]))})
    unmatched = [list(map(int, color)) for color in sorted(set(map(tuple, target)) - set(map(tuple, rounded)))]
    report = {'classification': 'post-hoc explanation using one already tested authored candidate; not an independent exact palette prediction',
        'candidate': 'lightness-weighted-farthest/Oklab, fixed prior run; no new candidates or fitted parameters',
        'results_sha256': methods.sha(results_path.read_bytes()),
        'candidate_palette_exact_centers': 29, 'candidate_palette_missing_service_centers': unmatched,
        'eight_previously_failed_means_reproduced_by_latent_assignments': len(center_reports),
        'center_details': center_reports,
        'float_vs_rounded_candidate_assignment_changed_pixels': int(np.sum(counts[float_assignment != rounded_assignment])),
        'unresolved': 'Three pale-family service centers differ; candidate final palette mapper still misses768/8192 pixels. No hybrid/per-center splice or extra search was performed.'}
    path = experiment / 'FLOAT-ASSIGNMENT-EXPLANATION.json'
    text = json.dumps(report, indent=2) + '\n'
    with path.open('x') as stream:
        stream.write(text)
    print(json.dumps({k: v for k, v in report.items() if k != 'center_details'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--mapper', type=Path, required=True)
    args = parser.parse_args()
    analyze(args.root, args.experiment, args.mapper)
