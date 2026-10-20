#!/usr/bin/env python3
"""Hash-bound, reversible edits to authoritative rig shapes and pose tracks."""
import argparse
import copy
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def vector(value):
    return isinstance(value, list) and len(value) == 2 and all(finite(x) for x in value)


def validate(document):
    if document.get('schema') == 'copper-scout-design/v1':
        require(document['canvas'] == [192, 192], 'Canvas contract changed')
        require(0 < document['ground_y'] < 192, 'Invalid ground')
        require(all(isinstance(v, str) and re.fullmatch('[0-9A-Fa-f]{6}', v)
                    for v in document['palette'].values()), 'Invalid palette color')
        require(all(vector(v) for v in document['anchors'].values()), 'Invalid anchor')
        for name, values in document['polygons'].items():
            require(len(values) >= 3 and all(vector(v) for v in values), f'Invalid polygon {name}')
        for name, value in document['dimensions'].items():
            if name in ('leg_widths', 'arm_widths'):
                require(isinstance(value, list) and len(value) == 3, 'Limb widths need three values')
                require(all(finite(v) and 0 < v <= 192 for v in value), 'Invalid limb widths')
            else:
                require(finite(value) and 0 < value <= 192, 'Limb length/radius must be a positive scalar')
    elif document.get('schema') == 'copper-scout-clips/v1':
        require(document['fps'] == 60, 'Authored clock contract changed')
        for name, clip in document['clips'].items():
            require(type(clip['duration_ticks']) is int and 2 <= clip['duration_ticks'] <= 441,
                    f'Invalid duration {name}')
            require(type(clip['loop']) is bool, 'Invalid loop flag')
            require(clip['equipment'] in ('none', 'sword', 'blaster'), 'Unknown equipment')
            vector_tracks = ('pelvis', 'front_foot', 'rear_foot', 'front_hand', 'rear_hand')
            require(all(vector(v) if key in vector_tracks else finite(v) for key, v in clip['defaults'].items()), 'Invalid default pose type')
            if 'gait' in clip:
                require(all(finite(v) and v >= 0 for v in clip['gait'].values()), 'Invalid gait parameter')
                require(0 < clip['gait']['stance_fraction'] < 1, 'Invalid stance fraction')
            for event in clip['events']:
                require(type(event['tick']) is int and 0 <= event['tick'] < clip['duration_ticks'],
                        f'Event outside timeline {name}')
                require(isinstance(event['type'], str) and bool(event['type']), 'Invalid event type')
            for track, keys in clip['tracks'].items():
                require(isinstance(keys, list) and len(keys) >= 2, f'Missing track endpoints {track}')
                require(all(isinstance(k, list) and len(k) == 2 and finite(k[0])
                            and 0 <= k[0] <= 1 and (finite(k[1]) or vector(k[1])) for k in keys),
                        f'Invalid track {track}')
                require(keys[0][0] == 0 and keys[-1][0] == 1, f'Missing endpoint {track}')
                require(all(a[0] < b[0] for a, b in zip(keys, keys[1:])), f'Unordered track {track}')
                require(all(vector(k[1]) if track in vector_tracks else finite(k[1]) for k in keys), f'Wrong pose track type {track}')
    else:
        raise ValueError('Unsupported source schema')


def editable(document, path):
    if document['schema'] == 'copper-scout-design/v1':
        return len(path) >= 2 and path[0] in ('palette', 'anchors', 'polygons', 'dimensions')
    return (len(path) >= 3 and path[0] == 'clips'
            and path[2] in ('tracks', 'defaults', 'gait', 'duration_ticks', 'events', 'equipment'))


def parent_at(document, path):
    require(isinstance(path, list) and path, 'Path must be a nonempty JSON array')
    node = document
    for key in path[:-1]:
        if isinstance(node, list):
            require(type(key) is int and 0 <= key < len(node), 'Invalid array index')
        else:
            require(isinstance(node, dict) and isinstance(key, str) and key in node, 'Unknown path')
        node = node[key]
    key = path[-1]
    if isinstance(node, list):
        require(type(key) is int and 0 <= key < len(node), 'Invalid array index')
    else:
        require(isinstance(node, dict) and isinstance(key, str) and key in node, 'Unknown path')
    return node, key


def apply(source_bytes, edit):
    require(edit.get('schema') == 'rig-source-edit/v1', 'Unsupported edit schema')
    require(edit.get('expected_sha256') == sha(source_bytes), 'Stale source; rebase and review the edit')
    require(isinstance(edit.get('reason'), str) and edit['reason'].strip(), 'An edit needs a reason')
    document = json.loads(source_bytes)
    validate(document)
    operations = edit.get('operations')
    require(isinstance(operations, list) and 0 < len(operations) <= 256, 'Invalid operation count')
    result = copy.deepcopy(document)
    for op in operations:
        require(set(op) == {'op', 'path', 'before', 'value'} and op['op'] == 'set', 'Invalid operation')
        require(editable(document, op['path']), 'Path is not an editable art or motion parameter')
        parent, key = parent_at(result, op['path'])
        require(parent[key] == op['before'], 'Parameter changed since the edit was authored')
        parent[key] = copy.deepcopy(op['value'])
    validate(result)
    output = (json.dumps(result, indent=2, allow_nan=False) + '\n').encode()
    receipt = {'schema': 'rig-source-receipt/v1', 'before_sha256': sha(source_bytes),
               'after_sha256': sha(output), 'before_utf8': source_bytes.decode(), 'edit': edit,
               'downstream_status': 'stale: rebake, rebuild editable cels, invalidate old pixel journals and re-review'}
    return output, receipt


def undo(current_bytes, receipt):
    require(receipt.get('schema') == 'rig-source-receipt/v1', 'Unsupported receipt')
    require(sha(current_bytes) == receipt['after_sha256'], 'Cannot undo over a newer source edit')
    original = receipt['before_utf8'].encode()
    require(sha(original) == receipt['before_sha256'], 'Receipt original bytes are corrupt')
    validate(json.loads(original))
    replayed, _ = apply(original, receipt['edit'])
    require(replayed == current_bytes, 'Receipt edit does not reproduce the current source')
    return original


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    change = commands.add_parser('apply')
    change.add_argument('source', type=Path)
    change.add_argument('edit', type=Path)
    change.add_argument('--output', type=Path, required=True)
    change.add_argument('--receipt', type=Path, required=True)
    restore = commands.add_parser('undo')
    restore.add_argument('source', type=Path)
    restore.add_argument('receipt', type=Path)
    restore.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'apply':
        require(args.output.resolve() != args.receipt.resolve(), 'Output and receipt need distinct paths')
        require(args.receipt.resolve() != args.source.resolve(), 'Receipt would overwrite the source')
        output, receipt = apply(args.source.read_bytes(), json.loads(args.edit.read_bytes()))
        # Persist the complete rollback record before promoting source bytes.
        atomic_write(args.receipt, (json.dumps(receipt, indent=2) + '\n').encode())
        atomic_write(args.output, output)
    else:
        output = undo(args.source.read_bytes(), json.loads(args.receipt.read_bytes()))
        atomic_write(args.output, output)
    print(json.dumps({'source_sha256': sha(output), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
