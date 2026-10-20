"""Portable conditional contact calculation; no engine or source mutations.

All coordinates below are literal native texel centers. The labels describe
painted landmarks, not recovered skeleton joints or proven ground contacts.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
G = R / 'inputs/guides'
SCALE, SPEED, HOLD = 0.66, 158.0, 9 / 160
COLORS = {'heel': '#ff2f8a', 'forefoot': '#00a9c0', 'ankle': '#eca900', 'sole': '#b65bff'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rgba(p):
    return np.array(Image.open(p).convert('RGBA'))

def image_for(bank, phase):
    return R / 'inputs' / bank / f'{phase:02}.png'

def mapped(mapname, key, source):
    xy = np.load(G / mapname)[key]
    points = np.argwhere(np.all(xy == source, axis=2))
    assert len(points) == 1, (mapname, source, points.tolist())
    return points[0, ::-1].tolist()

def witness(bank, phase, label, target, sourcefile, source, mapname=None, mapkey=None):
    actual = rgba(image_for(bank, phase))[target[1], target[0]].tolist()
    source_rgba = rgba(G / sourcefile)[source[1], source[0]].tolist()
    assert actual[3] > 0
    if mapname:
        xy = np.load(G / mapname)[mapkey]
        assert xy[target[1], target[0]].tolist() == source
    return {'phase': phase, 'label': label, 'target_xy': target, 'target_RGBA': actual,
            'source_file': 'inputs/guides/' + sourcefile, 'source_xy': source,
            'source_RGBA': source_rgba, 'direct_RGBA_equal': actual == source_rgba,
            'map': 'inputs/guides/' + mapname if mapname else None, 'map_key': mapkey}

def build_runs():
    runs = []
    w = []
    for label, source in [('heel', [49, 109]), ('forefoot', [57, 110]), ('ankle', [51, 101])]:
        for phase in [4, 5, 6]:
            mp = f'lyra-{phase:02}-map.npz' if phase != 6 else None
            target = mapped(mp, 'source_xy', source) if mp else source
            w.append(witness('lyra-southeast', phase, label, target, 'lyra-06-source.png', source, mp, 'source_xy'))
    runs.append({'id': 'lyra-SE-Q04-06', 'bank': 'lyra-southeast', 'phases': [4, 5, 6],
                 'class': 'plausible_support_hypothesis', 'fit': True, 'same_material': True,
                 'rationale': 'Same visible06 foreground boot sole and ankle, whole distal shape retained in04/05 maps. Broad sole faces down, alternate boot remains visibly tucked. This supports a stance hypothesis, not ground proof.',
                 'witnesses': w})
    w = []
    for label, source in [('heel', [58, 109]), ('forefoot', [69, 109]), ('ankle', [61, 101])]:
        for phase in [5, 6]:
            mp = 'brann-se-selected05-map.npz' if phase == 5 else None
            target = mapped(mp, 'source_xy', source) if mp else source
            w.append(witness('brann-southeast', phase, label, target, 'brann-se-selected06-source.png', source, mp, 'source_xy'))
    runs.append({'id': 'brann-SE-Q05-06', 'bank': 'brann-southeast', 'phases': [5, 6],
                 'class': 'load_return_hypothesis_contact_uncertain', 'fit': True, 'same_material': True,
                 'rationale': 'Actual selected05 uses the06 foreground boot at[-1,+1], then06 retains it at[0,0]. Sole and ankle material correspond exactly through the map. Broad lowered sole suggests a possible load/return interval, but the producer names05 forward recovery; it may already be releasing. This is a conditional test, not an asserted planted run. Older full-lower04/05 maps do not reproduce selected art and are rejected.',
                 'witnesses': w})
    w = []
    points = {4: {'heel': [52, 113], 'forefoot': [64, 111], 'ankle': [53, 103], 'sole': [58, 115]},
              5: {'heel': [54, 111], 'forefoot': [63, 112], 'ankle': [54, 102], 'sole': [59, 112]},
              6: {'heel': [49, 105], 'forefoot': [56, 106], 'ankle': [49, 98], 'sole': [53, 107]}}
    for phase, labels in points.items():
        for label, target in labels.items():
            if phase == 4:
                source = [target[0] + 18, target[1] - 4]
                v = witness('rowan-southeast', phase, label, target, 'rowan-04-source00.png', source)
                v['literal_translation'] = [-18, 4]
            elif phase == 5:
                sx, sy = np.load(G / 'rowan-05-map.npz')['source_xy'][target[1], target[0]].tolist()
                raw = np.load(G / 'rowan-05-raw-map.npz')['raw_source_xy'][sy, sx].tolist()
                v = witness('rowan-southeast', phase, label, target, 'rowan-05-raw.png', raw)
                v['intermediate_control_xy'] = [sx, sy]
                v['map_chain'] = ['rowan-05-map.npz:source_xy', 'rowan-05-raw-map.npz:raw_source_xy']
                assert rgba(G / 'rowan-05-control.png')[sy, sx].tolist() == v['target_RGBA']
            else:
                actual = rgba(image_for('rowan-southeast', phase))[target[1], target[0]].tolist()
                v = {'phase': phase, 'label': label, 'target_xy': target, 'target_RGBA': actual,
                     'source_file': f'inputs/rowan-southeast/{phase:02}.png', 'source_xy': target,
                     'source_RGBA': actual, 'direct_RGBA_equal': True, 'map': None,
                     'scope': 'Literal existing06 paint; no cross-drawing material correspondence claimed.'}
            assert v['target_RGBA'][3] > 0
            w.append(v)
    runs.append({'id': 'rowan-SE-Q04-06', 'bank': 'rowan-southeast', 'phases': [4, 5, 6],
                 'class': 'conditional_geometric_comparison_only', 'fit': True, 'same_material': False,
                 'rationale': 'Loaded-looking foreground sequence with literal heel/forefoot/ankle and sole-edge witnesses.04 is a whole00 boot donor;05 is distinct generated paint then bounded path projection;06 is another existing drawing. Points are homologous visual hypotheses, not the same material texel. This cannot certify a planted run.',
                 'witnesses': w})
    w = []
    for label, source in [('heel', [75, 102]), ('forefoot', [84, 96]), ('ankle', [75, 93])]:
        for phase in [5, 6, 7]:
            mp, key = ('brann-ne-05-map.npz', 'new_Q_source_xy') if phase == 5 else ('brann-ne-06-map.npz', 'boot_source_xy')
            target = mapped(mp, key, source) if phase != 7 else source
            w.append(witness('brann-northeast', phase, label, target, 'brann-ne-source07.png', source, mp if phase != 7 else None, key))
    runs.append({'id': 'brann-NE-Q05-07-excluded', 'bank': 'brann-northeast', 'phases': [5, 6, 7],
                 'class': 'recovery_control_excluded_from_support', 'fit': False, 'same_material': True,
                 'rationale': 'The complete07 donor moves[-7,0] then[-4,-1] then[0,0]. It travels forward along NE and exposes a bent/tilted boot rather than an established planted sole. Screen y and anatomical depth are not ground height. The other boot uses different source poses; no well-supported rear multi-pose stance interval is asserted.',
                 'witnesses': w})
    source = [76, 110]
    target = mapped('brann-se-07-map.npz', 'source_xy', source)
    w = [witness('brann-southeast', 7, 'sole', target, 'brann-se-07-source00.png', source, 'brann-se-07-map.npz', 'source_xy'),
         witness('brann-southeast', 0, 'sole', source, 'brann-se-07-source00.png', source)]
    runs.append({'id': 'brann-SE-P07-00-excluded', 'bank': 'brann-southeast', 'phases': [7, 0],
                 'class': 'return_control_excluded_from_support', 'fit': False, 'same_material': True,
                 'rationale': '07 P is the explicit shortened return from00 P paint. Its forward relative motion at wrap is consistent with recovery, not a stance fit.06 tucked P and07 bent Q cannot be treated as the same grounded silhouette.',
                 'witnesses': w})
    return runs

def measure(runs):
    rows = []
    for run in runs:
        direction = np.array([1, -1 if run['bank'].endswith('northeast') else 1]) / math.sqrt(2)
        transverse = np.array([-direction[1], direction[0]])
        labels = sorted(set(v['label'] for v in run['witnesses']))
        for label in labels:
            ws = {v['phase']: v for v in run['witnesses'] if v['label'] == label}
            pairs = list(zip(run['phases'][:-1], run['phases'][1:]))
            if len(run['phases']) > 2:
                pairs.append((run['phases'][0], run['phases'][-1]))
            for a, b in pairs:
                intervals = (b - a) % 8
                dt = intervals * HOLD
                delta = SCALE * (np.array(ws[b]['target_xy']) - ws[a]['target_xy'])
                root = SPEED * dt * direction
                residual = root + delta
                backward = -float(delta @ direction)
                rows.append({'run': run['id'], 'class': run['class'], 'same_material': run['same_material'],
                             'label': label, 'start_phase': a, 'end_phase': b, 'seconds': dt,
                             'relative_dx_world': float(delta[0]), 'relative_dy_world': float(delta[1]),
                             'root_travel_world': SPEED * dt, 'backward_travel_world': backward,
                             'cancellation_fraction': backward / (SPEED * dt),
                             'residual_along_world': float(residual @ direction),
                             'residual_transverse_world': float(residual @ transverse),
                             'residual_norm_world': float(np.linalg.norm(residual)),
                             'conditional_speed_fit': backward / dt if run['fit'] and backward > 0 else None,
                             'conditional_phase_seconds_at158': backward / SPEED if run['fit'] and backward > 0 else None,
                             'fit_is_recommendation': False})
    return rows

def sheets(runs, out):
    by_bank = {}
    for run in runs:
        for w in run['witnesses']:
            by_bank.setdefault(run['bank'], {}).setdefault(w['phase'], []).append(w)
    for size in [128, 84]:
        for bg, name, ink in [('#e7e3d6', 'light', 'black'), ('#22252b', 'dark', 'white')]:
            board = Image.new('RGB', (8 * size, 4 * (size + 36) + 44), bg)
            d = ImageDraw.Draw(board)
            d.text((4, 4), 'Literal painted anchors; circles are hypotheses, never ground proof. Magenta heel / cyan forefoot / amber ankle / violet sole.', fill=ink)
            d.text((4, 19), f'{size}px stage preview; numeric draw scale=.66. Cross=pivot(64,112), not ground. SE movement down-right; NE up-right.', fill=ink)
            for row, bank in enumerate(by_bank):
                for phase in range(8):
                    x, y = phase * size, 44 + row * (size + 36)
                    im = Image.open(image_for(bank, phase)).convert('RGBA').resize((size, size), Image.Resampling.NEAREST)
                    board.paste(im, (x, y + 30), im)
                    d.text((x + 2, y + 2), bank.replace('southeast', 'SE').replace('northeast', 'NE'), fill=ink)
                    d.text((x + 2, y + 15), f'{phase:02}', fill=ink)
                    px, py = x + 64 * size / 128, y + 30 + 112 * size / 128
                    d.line((px - 2, py, px + 2, py), fill='#777777')
                    d.line((px, py - 2, px, py + 2), fill='#777777')
                    for w in by_bank[bank].get(phase, []):
                        px, py = w['target_xy']
                        cx, cy = x + (px + .5) * size / 128, y + 30 + (py + .5) * size / 128
                        d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), outline=COLORS[w['label']], width=1)
            board.save(out / f'contact-full8-{size}-{name}.png')
    for run in runs:
        board = Image.new('RGB', (len(run['phases']) * 400, 390), '#e7e3d6')
        d = ImageDraw.Draw(board)
        for j, phase in enumerate(run['phases']):
            box = (35, 78, 95, 122)
            im = Image.open(image_for(run['bank'], phase)).convert('RGBA').crop(box).resize((360, 264), Image.Resampling.NEAREST)
            board.paste(im, (j * 400 + 10, 42), im)
            d.text((j * 400 + 10, 4), run['id'] + f' phase{phase:02}', fill='black')
            lines = []
            for w in run['witnesses']:
                if w['phase'] != phase:
                    continue
                x, y = w['target_xy']
                cx, cy = j * 400 + 10 + (x - 35 + .5) * 6, 42 + (y - 78 + .5) * 6
                d.rectangle((cx - 3, cy - 3, cx + 3, cy + 3), outline=COLORS[w['label']], width=2)
                lines.append(f"{w['label']}: target{x,y} source{tuple(w['source_xy'])}")
            d.multiline_text((j * 400 + 10, 314), '\n'.join(lines), fill='black', spacing=3)
        board.save(out / (run['id'] + '-6x.png'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Fresh output directory required'
    args.output.mkdir(parents=True)
    ledger = json.loads((R / 'INPUTS.json').read_text())
    guides = json.loads((R / 'GUIDE-INPUTS.json').read_text())
    for entry in ledger['canonical'] + [v for bank in ledger['banks'].values() for v in bank] + guides:
        assert sha(R / entry['retained']) == entry['sha256']
    hero = (R / 'inputs/canonical/scripts/hero.gd').read_text()
    assert re.search(r'MOVE_SPEED: float = 158\.0', hero)
    for name in ['hero', 'characters/lyra', 'characters/brann']:
        manifest = json.loads((R / f'inputs/canonical/assets/{name}/animations.json').read_text())
        assert manifest['draw_scale'] == SCALE and manifest['pivot'] == [64, 112]
        for view in ['southeast', 'northeast']:
            assert manifest['animations'][view + '_walk']['holds'] == [HOLD] * 8
    runs = build_runs()
    rows = measure(runs)
    (args.output / 'ANCHORS.json').write_text(json.dumps(runs, indent=2) + '\n')
    with (args.output / 'CALCULATIONS.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    receipt = {'scope': 'Static selected-v9 art + frozen code calculation; no engine/GPU/input/contact test.',
               'speed': SPEED, 'scale': SCALE, 'hold': HOLD, 'cycle': HOLD * 8,
               'root_travel_per_hold': SPEED * HOLD, 'root_travel_per_cycle': SPEED * HOLD * 8,
               'required_native_backward_per_hold': SPEED * HOLD / SCALE,
               'diagonal_component_native_per_hold': SPEED * HOLD / SCALE / math.sqrt(2),
               'source_hash_validation': True, 'source_correspondence_checks': len([w for run in runs for w in run['witnesses']]),
               'direct_RGBA_unequal_samples': [w for run in runs for w in run['witnesses'] if not w['direct_RGBA_equal']],
               'within_hold_steady_root_drift_world': SPEED * HOLD,
               'half_hold_drift_world': SPEED * HOLD / 2,
               'render_rounding_not_measured': True, 'canonical_changes': 0, 'model_calls': 0,
               'calculation_only_variants': 'Each positive backward run gets one speed fit and one phase-duration-at158 calculation. They are conditional fits, not changes or recommendations.'}
    (args.output / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    variant = {
        'status': 'Calculations only; not game settings or recommendations.',
        'lyra_uniform_speed_matching04_06_boundary_travel': SCALE * 4 * math.sqrt(2) / (2 * HOLD),
        'lyra_uniform_cycle_at158_matching_same_boundary_travel': (SCALE * 4 * math.sqrt(2) / SPEED) * 4,
        'lyra_phase_linked_04_05_and05_06_root_distance_each': SCALE * 2 * math.sqrt(2),
        'lyra_phase_linked_other_six_distances_if_preserving71_1_stride': (SPEED * HOLD * 8 - SCALE * 4 * math.sqrt(2)) / 6,
        'lyra_boundary_whole_actor_correction_excursion04_06': SPEED * HOLD * 2 - SCALE * 4 * math.sqrt(2),
        'brann05_06_root_step_needed_to_cancel_along_component': 0,
        'brann05_06_remaining_transverse_travel_even_if_zero_speed': SCALE * math.sqrt(2),
        'limits': [
            'A phase-linked physical root would change gameplay velocity; no change is proposed.',
            'A uniform speed or cycle fit cannot remove within-hold drift or transverse motion.',
            'These windows do not establish the contact schedule or required stride of a full cycle.',
            'No fitted whole-actor visual correction is rendered or recommended.',
        ],
    }
    (args.output / 'CALCULATION-ONLY-VARIANTS.json').write_text(json.dumps(variant, indent=2) + '\n')
    traces = []
    lyra = runs[0]
    points = {v['phase']: np.array(v['target_xy']) for v in lyra['witnesses'] if v['label'] == 'heel'}
    direction = np.array([1, 1]) / math.sqrt(2)
    for phase in [4, 5, 6]:
        for fraction in [0, .25, .5, .75, .999999]:
            time = (phase - 4 + fraction) * HOLD
            relative = float(SCALE * (points[phase] - points[4]) @ direction)
            traces.append({'phase': phase, 'fraction_in_hold': fraction, 'seconds_since04_start': time,
                           'root_along_world': SPEED * time, 'relative_paint_along_world': relative,
                           'conditional_world_sole_displacement': SPEED * time + relative,
                           'contact_at_sample_is_proven': False})
    with (args.output / 'HELD-POSE-TRACE.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(traces[0]))
        writer.writeheader()
        writer.writerows(traces)
    sheets(runs, args.output)
    for row in rows:
        if row['label'] in ['sole', 'heel']:
            print(row['run'], row['label'], row['start_phase'], row['end_phase'], 'back', round(row['backward_travel_world'], 4), 'residual', round(row['residual_along_world'], 4), 'side', round(row['residual_transverse_world'], 4), 'fit', row['conditional_speed_fit'])
    print('Unequal direct RGBA samples:', len(receipt['direct_RGBA_unequal_samples']))

if __name__ == '__main__':
    main()
