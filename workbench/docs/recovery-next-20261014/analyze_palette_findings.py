#!/usr/bin/env python3
"""Bounded offline analysis; supplied diagnostics, no provider/credential code."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
import PIL
from PIL import Image


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def decode(value):
    raw = base64.b64decode(value['base64'].split(',')[-1], validate=True)
    with Image.open(BytesIO(raw)) as image:
        return raw, np.array(image.convert('RGBA'))


def linear(rgb):
    value = rgb / 255
    return np.where(value <= .04045, value / 12.92, ((value + .055) / 1.055) ** 2.4)


def encode(value):
    value = np.maximum(value, 0)
    return np.where(value <= .0031308, value * 12.92, 1.055 * value ** (1 / 2.4) - .055) * 255


def require(condition, message):
    if not condition:
        raise ValueError(message)


def analyze(root, output, mapper_path):
    output.mkdir(parents=True, exist_ok=False)
    mapper_bytes = mapper_path.read_bytes()
    require(sha(mapper_bytes) == '6272a72903dd4a7d330e7eeb5c8e7df321cbc84c6ba9f9485404a640857ba742', 'Inferred mapper source drift')
    snapshot = output / 'inferred-fixed-palette-mapper.source.py'
    snapshot.write_bytes(mapper_bytes)
    spec = importlib.util.spec_from_file_location('frozen_mapper', snapshot)
    mapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mapper)
    manifest = read(root / 'PREPARATION-MANIFEST.json')
    for row in manifest['prepared_files']:
        require(sha((root / row['file']).read_bytes()) == row['sha256'], 'Frozen prepared artifact changed')
    plan = read(root / 'PLAN.json')
    original = {c['variant']: c for c in read(root / 'ORIGINAL-HELPER-REPLAY.json')['results']}
    variation_path = output / 'INFERRED-WEIGHTED-HELPER-VARIANT.json'
    subprocess.run(['node', str(Path(__file__).with_name('replay_palette_weighted_variant.cjs')),
                    str(root), str(variation_path)], check=True)
    variation = read(variation_path)
    rows = []
    for case in plan['requests']:
        run = root / case['variant']
        request_bytes = (run / 'request.json').read_bytes()
        require(sha(request_bytes) == case['request_sha256'], 'Request changed')
        payload = read(run / 'request.json')
        wire = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
        require(sha(wire) == case['compact_http_body_sha256'], 'Wire changed')
        har_bytes = (run / 'network.har').read_bytes()
        entries = read(run / 'network.har')['log']['entries']
        require(len(entries) == 1, 'Exactly one producer record required')
        entry = entries[0]
        require(entry['request']['method'] == 'POST' and entry['request']['url'] == plan['endpoint'], 'Endpoint binding')
        require(entry['request']['postData']['text'].encode() == wire, 'Actual wire binding')
        require(entry['_request_body_sha256'] == sha(wire), 'Actual request SHA')
        require(entry['response']['status'] == 200 and entry['_response_body_sha256_scope'] == 'full', 'Complete HTTP200 required')
        text = entry['response']['content']['text']
        require(entry['response']['content']['text_redacted'] is False, 'Exact response bytes required for this check')
        require(sha(text.encode()) == entry['_response_body_sha256_before_scrub'], 'Full original response SHA')
        response = read(run / 'response.json')
        require(json.loads(text) == response, 'Response JSON binding')
        state = read(run / 'state.json')
        require(state['status'] == 'completed' and state['plan_sha256'] == sha((root / 'PLAN.json').read_bytes()), 'Completed frozen state')
        rea = read(run / 'REA-EVIDENCE.json')
        require(rea['subject']['digest']['sha256'] == sha(har_bytes), 'REA HAR SHA')
        require(rea['normalized_result']['total_records'] == 1, 'REA complete record count')
        require(rea['normalized_result']['records'][0]['reported'] == entry, 'REA exact producer record')
        palette_raw, palette_image = decode(response['palette'])
        require(palette_raw == (run / 'palette.png').read_bytes(), 'Palette PNG binding')
        palette = palette_image.reshape(-1, 4)
        palette_rgb = [tuple(map(int, c[:3])) for c in palette]
        source, actual, frame_stats = [], [], []
        require(len(payload['images']) == len(response['images']) == 2, 'Two frames required')
        for index, (a, b) in enumerate(zip(payload['images'], response['images'])):
            source_raw, src = decode(a)
            actual_raw, result = decode(b)
            require(actual_raw == (run / f'output-{index:02}.png').read_bytes(), 'Output PNG binding')
            require(src.shape == result.shape == (64, 64, 4), 'Diagnostic dimensions')
            replay = mapper.remap_rgba(src, palette)
            delta = mapper.oklab(src[..., :3])[:, :, None, :] - mapper.oklab(palette[:, :3])[None, None, :, :]
            unweighted = palette[np.argmin(np.sum(delta ** 2, axis=-1), axis=-1), :3]
            distance = np.sum(delta ** 2 * np.array([.25, 1, 1]), axis=-1)
            lowest = np.sort(distance, axis=-1)[..., :2]
            source.append(src)
            actual.append(result)
            frame_stats.append({'index': index, 'pixels': 4096, 'source_png_sha256': sha(source_raw),
                'output_png_sha256': sha(actual_raw), 'weighted_oklab_rgba_mismatches': int(np.count_nonzero(np.any(replay != result, axis=-1))),
                'unweighted_oklab_rgb_mismatches': int(np.count_nonzero(np.any(unweighted != result[..., :3], axis=-1))),
                'exact_distance_ties': int(np.count_nonzero(lowest[..., 0] == lowest[..., 1])),
                'alpha_exact': bool(np.array_equal(src[..., 3], result[..., 3]))})
        combined = np.concatenate(source, axis=0)
        combined_actual = np.concatenate(actual, axis=0)
        candidates = []
        for method in [Image.Quantize.MEDIANCUT, Image.Quantize.MAXCOVERAGE, Image.Quantize.FASTOCTREE]:
            q = Image.fromarray(combined[..., :3]).quantize(colors=case['num_colors'], method=method,
                dither=Image.Dither.NONE, kmeans=0)
            indices = sorted(set(q.get_flattened_data() if hasattr(q, 'get_flattened_data') else q.getdata()))
            p = q.getpalette()
            colors = [tuple(p[i * 3:i * 3 + 3]) for i in indices]
            candidates.append({'method': method.name, 'settings': {'colors': case['num_colors'], 'dither': 'NONE', 'kmeans': 0},
                'palette_rgb': colors, 'palette_rgb_multiset_equal': Counter(colors) == Counter(palette_rgb),
                'palette_rgb_set_intersection': len(set(colors) & set(palette_rgb)),
                'candidate_rgb_output_mismatches': int(np.count_nonzero(np.any(np.array(q.convert('RGB')) != combined_actual[..., :3], axis=-1)))})
        flat_source, flat_actual = combined.reshape(-1, 4), combined_actual.reshape(-1, 4)
        centroid_rows = []
        for color in palette_rgb:
            assigned = flat_source[np.all(flat_actual[:, :3] == color, axis=-1), :3].astype(float)
            row = {'palette_rgb': color, 'assigned_pixels': len(assigned), 'models': []}
            for unique in [False, True]:
                values = np.unique(assigned, axis=0) if unique else assigned
                if not len(values):
                    continue
                for space in ['srgb', 'linearRGB', 'Oklab']:
                    mean = np.mean(values if space == 'srgb' else linear(values) if space == 'linearRGB' else mapper.oklab(values), axis=0)
                    if space == 'linearRGB':
                        mean = encode(mean)
                    elif space == 'Oklab':
                        mean = encode((mean @ np.linalg.inv(mapper.M2).T) ** 3 @ np.linalg.inv(mapper.M1).T)
                    for rounding in ['floor', 'rint']:
                        predicted = np.clip(np.floor(mean) if rounding == 'floor' else np.rint(mean), 0, 255).astype(int)
                        row['models'].append({'weighting': 'unique-RGB' if unique else 'pixel-frequency',
                            'space': space, 'rounding': rounding, 'centroid_srgb_float': mean.tolist(),
                            'predicted_rgb': predicted.tolist(), 'exact': bool(np.array_equal(predicted, color))})
            centroid_rows.append(row)
        summary = {}
        for center in centroid_rows:
            for model in center['models']:
                key = '/'.join(model[k] for k in ['weighting', 'space', 'rounding'])
                summary[key] = summary.get(key, 0) + int(model['exact'])
        source_rgb = set(map(tuple, flat_source[:, :3]))
        original_colors = set(map(tuple, original[case['variant']]['palette_rgb']))
        rows.append({'variant': case['variant'], 'usage': response['usage'], 'rea_evidence_id': rea['evidence_id'],
            'rea_authority': rea['authority'], 'har_sha256': sha(har_bytes), 'rea_sha256': sha((run / 'REA-EVIDENCE.json').read_bytes()),
            'response_file_sha256': sha((run / 'response.json').read_bytes()),
            'palette_png_sha256': sha(palette_raw), 'palette_rgb': palette_rgb,
            'palette_entries_present_in_source': len(set(palette_rgb) & source_rgb),
            'original_helper_palette_set_intersection': len(set(palette_rgb) & original_colors),
            'original_helper_same_requested_target_size': case['num_colors'] == 32,
            'weighted_helper_variation_intersection': len(set(palette_rgb) & set(map(tuple, variation['palette_rgb']))) if case['num_colors'] == 32 else None,
            'frames': frame_stats, 'standard_candidates': candidates,
            'centroid_match_counts': summary, 'centroid_denominator': len(palette), 'centroids': centroid_rows})
    report = {'schema': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'label': 'supplied diagnostic, no generated art',
        'versions': {'Pillow': PIL.__version__, 'numpy': np.__version__}, 'mapper_snapshot_sha256': sha(mapper_bytes),
        'mapper_policy': mapper.POLICY, 'plan_sha256': sha((root / 'PLAN.json').read_bytes()),
        'source_preparation_manifest_sha256': sha((root / 'PREPARATION-MANIFEST.json').read_bytes()),
        'analysis_script_sha256': sha(Path(__file__).read_bytes()), 'cases': rows,
        'totals': {'posts_observed': len(rows), 'reported_generations': sum(c['usage']['generations'] for c in rows),
            'rgba_entries_compared': 32768, 'weighted_rgba_mismatches': sum(f['weighted_oklab_rgba_mismatches'] for c in rows for f in c['frames'])},
        'centroid_method': 'Clusters are observed returned output-RGB assignments; compare pixel-frequency versus unique-input-RGB means in sRGB/linearRGB/Oklab, inverse transfer, clip0..255, then floor or numpy.rint(ties-to-even). Fixed candidate list, no fit.',
        'scope': 'Finite constructed-palette/opaque-input observation and post-hoc candidate rejection; no private algorithm/source/checkpoint/animation pipeline identity'}
    target = output / 'PALETTE-FINDINGS.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['totals']))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--mapper', required=True, type=Path)
    args = parser.parse_args()
    analyze(args.root, args.output_dir, args.mapper)
