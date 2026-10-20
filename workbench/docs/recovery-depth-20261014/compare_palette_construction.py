#!/usr/bin/env python3
"""Offline comparison of supplied diagnostic results; never sends a request."""
import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path

from PIL import Image


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decoded(raw):
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        return image.convert('RGBA')


def pixels(image):
    return list(image.get_flattened_data() if hasattr(image, 'get_flattened_data') else image.getdata())


def compare(root):
    plan = json.loads((root / 'PLAN.json').read_text())
    oracle = json.loads((root / 'ORIGINAL-HELPER-REPLAY.json').read_text())
    original = {r['variant']: r for r in oracle['results']}
    rows, mappings = [], {}
    for case in plan['requests']:
        run = root / case['variant']
        request_bytes = (run / 'request.json').read_bytes()
        if sha(request_bytes) != case['request_sha256']:
            raise ValueError('Frozen request changed')
        request = json.loads(request_bytes)
        compact = json.dumps(request, separators=(',', ':'), ensure_ascii=False).encode()
        if sha(compact) != case['compact_http_body_sha256']:
            raise ValueError('Frozen compact HTTP body changed')
        response_bytes = (run / 'response.json').read_bytes()
        response = json.loads(response_bytes)
        if len(response['images']) != 2:
            raise ValueError('Expected both output frames')
        palette_raw = base64.b64decode(response['palette']['base64'].split(',')[-1], validate=True)
        palette = decoded(palette_raw)
        if palette.height != 1:
            raise ValueError('Palette must be a1px strip per public contract')
        colors = [tuple(c[:3]) for c in pixels(palette)]
        frame_rows, variant_mapping = [], []
        for index, (source, value) in enumerate(zip(request['images'], response['images'])):
            source_raw = base64.b64decode(source['base64'].split(',')[-1], validate=True)
            output_raw = base64.b64decode(value['base64'].split(',')[-1], validate=True)
            before, after = decoded(source_raw), decoded(output_raw)
            if before.size != after.size:
                raise ValueError('Output size changed')
            saved = run / f'output-{index:02}.png'
            if saved.exists() and saved.read_bytes() != output_raw:
                raise ValueError('Saved output differs from response')
            relation = defaultdict(set)
            before_pixels, after_pixels = pixels(before), pixels(after)
            for a, b in zip(before_pixels, after_pixels):
                relation[a[:3]].add(b[:3])
            relation = {key: tuple(sorted(values)) for key, values in relation.items()}
            variant_mapping.append(relation)
            frame_rows.append({'index': index, 'input_png_sha256': sha(source_raw),
                'output_png_sha256': sha(output_raw), 'output_rgba_sha256': sha(after.tobytes()),
                'output_rgb_count': len(set(p[:3] for p in after_pixels)),
                'same_source_rgb_maps_to_multiple_outputs': sum(len(v) != 1 for v in relation.values()),
                'exact_alpha_preserved': all(a[3] == b[3] for a, b in zip(before_pixels, after_pixels))})
        mappings[case['variant']] = variant_mapping
        candidate = [tuple(c) for c in original[case['variant']]['palette_rgb']]
        rows.append({'variant': case['variant'], 'response_file_sha256': sha(response_bytes),
            'palette_png_sha256': sha(palette_raw), 'palette_rgb_in_api_order': colors,
            'reported_n_colors': response['n_colors'], 'palette_strip_width': palette.width,
            'original_helper_palette_size': len(candidate),
            'original_helper_palette_set_equal': set(candidate) == set(colors),
            'original_helper_palette_set_intersection': len(set(candidate) & set(colors)),
            'same_target_size_for_original_comparison': case['num_colors'] == 32, 'frames': frame_rows})
    comparisons = {
        'AB4_vs_CC4_first_frame_source_rgb_relations_equal': mappings['joint-ab-4'][0] == mappings['histogram-cc-4'][0],
        'AB4_A_vs_AA4_A_source_rgb_relations_equal': mappings['joint-ab-4'][0] == mappings['weighted-aa-4'][0],
        'AA4_repeated_frame_source_rgb_relations_equal': mappings['weighted-aa-4'][0] == mappings['weighted-aa-4'][1]}
    palettes = {r['variant']: Counter(r['palette_rgb_in_api_order']) for r in rows}
    comparisons['AB4_vs_CC4_palette_rgb_multiset_equal'] = palettes['joint-ab-4'] == palettes['histogram-cc-4']
    return {'schema': 1, 'label': 'offline comparison of supplied diagnostic responses',
        'no_provider_calls': True, 'cases': rows, 'comparisons': comparisons,
        'limits': ['No internal clustering/checkpoint/animation inference',
            'Matching palettes on one fixture do not identify a unique algorithm',
            'AB/CC differences can arise from insertion order or ties despite equal histograms',
            'Original client helper hardcodes32 and sorts by lightness; API palette order is documented as frequency']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Exclusive output prevents replacing an earlier comparison receipt.
    report = compare(args.root)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report['comparisons']))
