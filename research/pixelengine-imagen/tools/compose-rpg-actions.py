#!/usr/bin/env python3
"""Select pinned painted poses and explicit holds; never synthesize an intermediate."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def translate(image, offset):
    require(len(offset) == 2 and all(type(v) is int for v in offset), 'Integer offset required')
    box = image.getchannel('A').getbbox()
    require(box is not None, 'Empty selected drawing')
    dx, dy = offset
    require(box[0] + dx >= 0 and box[1] + dy >= 0 and box[2] + dx <= 80 and box[3] + dy <= 80, 'Translation clips visible source paint')
    result = Image.new('RGBA', (80, 80))
    result.paste(image, (dx, dy))
    return result


def run(args):
    plan, contract = read(args.plan), read(args.contract)
    require(plan['schema'] == 'rpg-action-selection/v1', 'Unknown selection schema')
    require(plan['direction'] in contract['directions'], 'Unknown direction')
    require(not args.output.exists(), 'Fresh output required')
    module_path = Path(__file__).with_name('build-rpg-bank.py')
    spec = importlib.util.spec_from_file_location('rpg_bank_export', module_path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    sources = {}
    for name, record in plan['sources'].items():
        path = Path(record['manifest']).resolve()
        require(sha(path) == record['sha256'], 'Stale manifest: ' + name)
        manifest = read(path)
        require(manifest['canvas'] == [80, 80], 'Unexpected source stage')
        sources[name] = (path, manifest, record.get('integer_offset', [0, 0]))
    args.output.mkdir(parents=True)
    (args.output / 'construction').mkdir()
    (args.output / 'actions').mkdir()
    write(args.output / 'selection-plan.json', plan)
    records, evidence = [], []
    for action, sequence in plan['actions'].items():
        require(action in contract['actions'], 'Action absent from coverage contract')
        images, holds, lineage = [], [], []
        for entry in sequence['poses']:
            path, manifest, offset = sources[entry['source']]
            require(type(entry['frame']) is int and 0 <= entry['frame'] < len(manifest['frames']), 'Invalid source frame index')
            frame = manifest['frames'][entry['frame']]
            rel = Path(frame['file'])
            require(not rel.is_absolute() and '..' not in rel.parts, 'Escaping frame path')
            image_path = path.parent / rel
            require(sha(image_path) == frame['sha256'], 'Stale source frame')
            image = Image.open(image_path).convert('RGBA')
            require(image.size == (80, 80), 'Wrong frame dimensions')
            original_rgba_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
            image = translate(image, offset)
            hold = Fraction(*entry['hold'])
            require(hold > 0, 'Nonpositive hold')
            images.append(image)
            holds.append(entry['hold'])
            lineage.append({'source': entry['source'], 'manifest_sha256': sha(path),
                            'frame_index': entry['frame'], 'frame_id': frame['source_frame_id'],
                            'file_sha256': sha(image_path), 'rgba_sha256': hashlib.sha256(image.tobytes()).hexdigest(),
                            'original_rgba_sha256': original_rgba_sha256, 'declared_integer_offset': offset,
                            'hold': entry['hold'], 'role': entry['role']})
        total = sum((Fraction(*h) for h in holds), Fraction())
        events = sequence.get('events', [])
        require(all(0 <= Fraction(*e['time']) < total for e in events), 'Event outside action')
        data = {'loop': sequence['loop'], 'holds': holds, 'events': events}
        provenance = {'operation': 'Explicit existing-pose selection and clock; no new paint or interpolation',
                      'selection_plan_sha256': sha(args.plan), 'source_lineage': lineage,
                      'art_status': 'Candidate; playback review required', 'notes': sequence['notes'],
                      'transform_scope': 'Only declared integer source-alias translations; no per-pose fitting, resampling or reshaping'}
        record = exporter.export_action(args.output, action, plan['direction'], images, data, provenance, list(range(len(images))))
        output_manifest = read(args.output / record['manifest'])
        for image, frame in zip(images, output_manifest['frames'], strict=True):
            actual = Image.open((args.output / record['manifest']).parent / frame['file']).convert('RGBA')
            require(actual.tobytes() == image.tobytes(), 'Selected output changed paint')
        if 'final_equals' in sequence:
            alias, index = sequence['final_equals']
            source_path, source_manifest, offset = sources[alias]
            final_source = Image.open(source_path.parent / source_manifest['frames'][index]['file']).convert('RGBA')
            final_source = translate(final_source, offset)
            require(images[-1].tobytes() == final_source.tobytes(), 'Final state binding mismatch')
        records.append(record)
        evidence.append({'action': action, 'exposures': len(images),
                         'unique_rasters': len({i.tobytes() for i in images}),
                         'duration': [total.numerator, total.denominator], 'lineage': lineage,
                         'all_selected_rgba_equal_declared_transform': True, 'notes': sequence['notes']})
    write(args.output / 'BANK.json', {'schema': 'rpg-authored-selection-bank/v1', 'direction': plan['direction'],
          'contract_sha256': sha(args.contract), 'review_status': 'repaired-playback-pending', 'actions': records,
          'boundary': 'Existing drawings and explicit state endpoints; no invented new intermediate or library acceptance'})
    write(args.output / 'SELECTION-VERIFICATION.json', {'actions': evidence, 'plan_sha256': sha(args.plan),
          'scope': 'Pixel selection/export/state binding only; not motion quality, anatomy or gameplay contact'})
    print(json.dumps({'direction': plan['direction'], 'actions': len(records), 'output': str(args.output)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
