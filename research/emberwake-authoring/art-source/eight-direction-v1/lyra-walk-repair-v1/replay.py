#!/usr/bin/env python3
"""Replay frozen painted-leg maps and the actual guarded editing journal.

No model call. Source-map replay is distinct from fresh geometry solving and
from art acceptance. Needs this folder and its sibling editor-toolkit-v1.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import sys

import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent
TOOL = BASE.parent / 'editor-toolkit-v1'
sys.path.insert(0, str(TOOL))
from sprite_lab import History, canonical_json, project_hash, render_frame

loader = importlib.util.spec_from_file_location('construction', TOOL / 'scripts/sprite_construct.py')
construction = importlib.util.module_from_spec(loader)
loader.loader.exec_module(construction)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('Output must be a fresh directory.')
    inputs = json.loads((BASE / 'INPUT-HASHES.json').read_text())
    for name, expected in inputs.items():
        assert sha(BASE / name) == expected, ('changed input', name)
    args.out.mkdir(parents=True)
    shutil.copyfile(BASE / 'construction-spec.json', args.out / 'construction-spec.json')
    count = 0
    for view in ('southeast', 'northeast'):
        source = BASE / 'frozen-geometry' / view
        receipt = json.loads((source / 'receipt.json').read_text())
        keys = {i: np.array(Image.open(source / 'keys' / f'{i:02}.png').convert('RGBA'))
                for i in (0, 2, 4, 6)}
        for frame in receipt['frames']:
            i = frame['frame']
            if i % 2 == 0:
                rgba = keys[i].copy()
            else:
                data = np.load(source / f'{i:02}-map.npz')
                owner, xy = data['owner'], data['source_xy']
                rgba = keys[frame['body_key']].copy()
                rgba[owner == 3] = 0
                for leg in (0, 1):
                    donor = keys[frame['controls'][leg]['source_key']]
                    mask = owner == leg + 1
                    rgba[mask] = donor[xy[:, :, 1][mask], xy[:, :, 0][mask]]
            expected = np.array(Image.open(BASE / f'{view}-{i:02}-source.png').convert('RGBA'))
            np.testing.assert_array_equal(rgba, expected)
            Image.fromarray(rgba).save(args.out / f'{view}-{i:02}-source.png')
            count += 1
    source_project = construction.construct(args.out / 'construction-spec.json')
    expected_source = json.loads((BASE / 'source-project.json').read_text())
    assert project_hash(source_project) == project_hash(expected_source)
    journal = json.loads((BASE / 'journal.json').read_text())
    history = History.replay(source_project, journal)
    edited = json.loads((BASE / 'edited-project.json').read_text())
    assert project_hash(history.project) == project_hash(edited)
    assert project_hash(history.undo()) == project_hash(source_project)
    assert project_hash(history.redo()) == project_hash(edited)
    for view in ('southeast', 'northeast'):
        (args.out / view).mkdir()
        for i in range(8):
            image = render_frame(history.project, f'{view}-{i:02}')
            np.testing.assert_array_equal(np.array(image), np.array(Image.open(BASE / view / f'{i:02}.png')))
            image.save(args.out / view / f'{i:02}.png')
    result = {'schema': 'emberwake-walk-edit-replay/v1', 'inputs_verified': len(inputs),
              'source_map_frames_exact': count, 'edited_frames_exact': 16,
              'guarded_journal_replay': True, 'undo_exact': True, 'redo_exact': True,
              'quality': 'Unselected candidate. Mechanical replay supplies no art score.'}
    (args.out / 'REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
