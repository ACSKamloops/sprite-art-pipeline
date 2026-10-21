#!/usr/bin/env python3
"""One authored source-colored support-boot shape between turning keys.

Bounded to the frozen phase3.5 owner; not recovered anatomy or ground contact.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import History, candidate_transaction, canonical_json, load_project, project_hash, render_cel, render_frame


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


def run(args):
    pin = sha(args.project)
    project = load_project(args.project.read_text())
    out = args.output.absolute()
    if out.exists():
        raise ValueError('Fresh output required')
    target = next(f for f in project['frames'] if f['id'] == 'bridge-3-4')
    cid = target['cels']['far-distal']
    source = render_cel(project, cid)
    if project['canvas']['width'] != 80 or project['canvas']['height'] != 80:
        raise ValueError('Native80px case only')
    # Sole span must bind the observed owner, rather than apply to a changed rig.
    assert [x for x in range(80) if source.getpixel((x, 70))[3]] == list(range(27, 38))
    candidate = Image.new('RGBA', (80, 80))
    witnesses = []
    for y in range(80):
        if y < 58:
            scale, shift = 1., 0.
        elif y <= 65:
            scale, shift = 1., -(y - 58) / 7
        elif y < 70:
            scale, shift = 1. - .2 * (y - 65) / 5, -1. + (y - 65) / 5
        else:
            scale, shift = .8, 0.
        for x in range(80):
            sx = round((x - (32.5 + shift)) / scale + 32.5)
            if 0 <= sx < 80 and source.getpixel((sx, y))[3]:
                candidate.putpixel((x, y), source.getpixel((sx, y)))
                witnesses.append([x, y, sx, y])
    mask = [[x, y] for y in range(80) for x in range(80)
            if source.getpixel((x, y))[3] or candidate.getpixel((x, y))[3]]
    history = History(project)
    tx = candidate_transaction(project, cid, candidate, mask)
    tx['reason'] = 'Authored phase3.5 foot foreshortening: keep heel near midpoint, shorten toe reach, shift leather shaft1px. Source-colored nearest map, no anatomical inference.'
    receipt = history.apply(tx)
    result = history.project
    journal = history.journal()
    assert project_hash(History.replay(project, journal).project) == project_hash(result)
    expected = project_hash(result)
    history.undo()
    assert project_hash(history.project) == project_hash(project)
    history.redo()
    assert project_hash(history.project) == expected
    assert all(render_frame(project, f['id']).tobytes() == render_frame(result, f['id']).tobytes()
               for f in project['frames'] if f['id'] != target['id'])
    assert project['animations'] == result['animations'] and project['canvas'] == result['canvas']
    actual = render_frame(result, target['id'])
    before = render_frame(project, target['id'])
    changed = [[x, y] for y in range(80) for x in range(80) if before.getpixel((x, y)) != actual.getpixel((x, y))]
    out.mkdir(parents=True)
    source.save(out / 'source-owner.png')
    candidate.save(out / 'candidate-owner.png')
    (out / 'project.json').write_text(canonical_json(result) + '\n')
    write(out / 'journal.json', journal)
    write(out / 'receipt.json', receipt)
    write(out / 'frozen-source-map.json', {'source_project_sha256': pin, 'source_cel': cid,
          'source_cel_rgba_sha256': hashlib.sha256(source.tobytes()).hexdigest(), 'source_xy': witnesses,
          'sampling': 'Python nearest integer, frozen source map is exact replay authority',
          'rows': [{'y': 58, 'scale_x': 1, 'shift_x': 0}, {'y': 65, 'scale_x': 1, 'shift_x': -1},
                   {'y': 70, 'scale_x': .8, 'shift_x': 0}], 'horizontal_pivot': 32.5})
    replay = Image.new('RGBA', (80, 80))
    for x, y, sx, sy in witnesses:
        replay.putpixel((x, y), source.getpixel((sx, sy)))
    assert replay.tobytes() == candidate.tobytes()
    exporter = module('roll_exporter', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
    exporter.export(out / 'project.json', out / 'delivery', 'walk', TOOLKIT, 8, 'hero')
    apng = module('roll_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')
    apng.convert(out / 'delivery/manifest.json', out / 'delivery/apng')
    cells = [('Key3', render_frame(project, 'key-3')), ('Before3.5', before),
             ('Authored3.5', actual), ('Key4', render_frame(project, 'key-4'))]
    montage = Image.new('RGB', (4 * 320, 350), (125, 125, 125))
    draw = ImageDraw.Draw(montage)
    for i, (label, image) in enumerate(cells):
        draw.text((i * 320 + 4, 4), label, fill='white')
        image = image.resize((320, 320), Image.Resampling.NEAREST)
        montage.paste(image, (i * 320, 25), image)
    montage.save(out / 'neighbors-4x.png')
    assert sha(args.project) == pin
    write(out / 'RESULTS.json', {'source_project_sha256': pin, 'recipe_sha256': sha(__file__),
          'changed_pixels': changed, 'only_phase3_5_changed': True, 'all_other_frames_and_clocks_exact': True,
          'journal_undo_redo_replay_and_frozen_map_exact': True,
          'visible_component_sole_span_row70': [x for x in range(80) if candidate.getpixel((x, 70))[3]],
          'source_pixels': sum(p[3] > 0 for p in source.get_flattened_data()),
          'output_pixels': len(witnesses), 'distinct_source_samples': len({(x[2], x[3]) for x in witnesses}),
          'approval': 'Unreviewed authored projected shape. No physical contact, rigid-volume or art-score claim.'})
    print(json.dumps({'output': str(out), 'changed_pixels': len(changed),
                      'owner_sole_span_row70': [x for x in range(80) if candidate.getpixel((x, 70))[3]]}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    run(p.parse_args())
