"""Replay bounded measurements from retained GPU captures; never rerender art."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
SCALE = .66
PIVOT = np.array([64., 112.])
DIRECTION = np.array([1., 1.]) / math.sqrt(2)
GRID = np.array([399, 199])
ROI = (400, 164, 444, 202)
FEATURES = {'heel': [49, 109], 'forefoot': [57, 110], 'original_ankle': [51, 101], 'ankle_context': [49, 102]}
INKS = {'heel': '#ff3f9e', 'ankle_context': '#ffcc36'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def array(p):
    return np.array(Image.open(p).convert('RGBA'))

def write_json(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def write_csv(p, rows):
    with p.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def find_patch(frame, patch):
    found = []
    for y in range(ROI[1] + 1, ROI[3] - 1):
        for x in range(ROI[0] + 1, ROI[2] - 1):
            if np.array_equal(frame[y - 1:y + 2, x - 1:x + 2], patch):
                found.append([x, y])
    return found

def find_heel_context(frame, patch):
    found = []
    for y in range(ROI[1] + 1, ROI[3]):
        for x in range(ROI[0] + 1, ROI[2]):
            if np.array_equal(frame[y - 1:y + 1, x - 1:x + 1], patch):
                found.append([x, y])
    return found

def source_target(phase, source):
    if phase == 6:
        return source
    xy = np.load(R / f'inputs/source/{phase:02}-map.npz')['source_xy']
    points = np.argwhere(np.all(xy == source, axis=2))
    assert len(points) == 1
    return points[0, ::-1].tolist()

def inverse_sample(row, pixel):
    return np.floor((np.array(pixel) + .5 - row['world_root']) / SCALE + PIVOT).astype(int)

def proof_sheet(out, name, ticks, frames, rows, accepted):
    crop_box = (394, 160, 446, 206)
    factor = 6
    width, height = 312, 276
    board = Image.new('RGB', (len(ticks) * (width + 8), height + 102), '#e7e3d6')
    draw = ImageDraw.Draw(board)
    for j, tick in enumerate(ticks):
        image = Image.fromarray(frames[tick]).crop(crop_box).resize((width, height), Image.Resampling.NEAREST)
        left, top = j * (width + 8), 38
        board.paste(image, (left, top))
        draw.text((left + 4, 3), f"GPU tick{tick:03} / cel{rows[tick]['exposure']:02}", fill='black')
        draw.text((left + 4, 17), f"t={rows[tick]['time']:.7f}s", fill='black')
        gx, gy = left + (GRID[0] - crop_box[0] + .5) * factor, top + (GRID[1] - crop_box[1] + .5) * factor
        draw.line((gx - 7, gy, gx + 7, gy), fill='#61fcff', width=2)
        draw.line((gx, gy - 7, gx, gy + 7), fill='#61fcff', width=2)
        lines = ['cyan cross: fixed GPU grid(399,199)']
        for feature in ['heel', 'ankle_context']:
            record = accepted.get((tick, feature))
            if record is None:
                lines.append(feature + ': not identified')
                continue
            x, y = record['pixel_xy']
            cx, cy = left + (x - crop_box[0] + .5) * factor, top + (y - crop_box[1] + .5) * factor
            radius = 8 if feature == 'ankle_context' else 4
            draw.rectangle((cx - radius, cy - radius, cx + radius, cy + radius), outline=INKS[feature], width=2)
            lines.append(f'{feature}: GPU({x},{y})')
        draw.multiline_text((left + 4, top + height + 4), '\n'.join(lines), fill='black', spacing=3)
    board.save(out / name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Fresh output directory required'
    args.output.mkdir(parents=True)
    intake = json.loads((R / 'INPUTS.json').read_text())
    for item in intake['ledger']:
        assert sha(R / item['retained']) == item['sha256']
    receipt = json.loads((R / 'inputs/GPU-RECEIPT.json').read_text())
    clip = next(c for c in receipt['clips'] if c['actor'] == 'lyra' and c['view'] == 'southeast')
    rows = {v['tick']: v for v in clip['samples']}
    ticks = intake['selected_ticks']
    frames = {tick: array(R / f'inputs/gpu/{tick:04}.png') for tick in ticks}
    source = array(R / 'inputs/source/06.png')
    manifests = json.loads((R / 'inputs/animations.json').read_text())
    assert manifests['pivot'] == PIVOT.tolist() and manifests['draw_scale'] == SCALE
    assert manifests['animations']['southeast_walk']['holds'] == [9 / 160] * 8
    for phase in [4, 5, 6]:
        assert rows[phase * 18]['atlas_frame'] == manifests['animations']['southeast_walk']['frames'][phase]
    # Directly observed, unique 3x3 boot-shading context in GPU tick72.
    # Its center is the opaque source06[49,102], near the painted ankle.
    patch = frames[72][175:178, 412:415].copy()
    heel_patch = frames[72][180:182, 412:414].copy()
    assert np.all(patch[..., 3] == 255)
    write_json(args.output / 'ANKLE-PATCH.json', {'reference_tick': 72, 'reference_center': [413, 176],
               'source06_center': [49, 102], 'RGBA3x3': patch.tolist(),
               'scope': 'Observed GPU shading context, unique inside the literal foot search ROI; no anatomical joint claim.'})
    write_json(args.output / 'HEEL-PATCH.json', {'reference_tick': 72, 'reference_lower_right': [413, 181],
               'source06_lower_right': [49, 109], 'RGBA2x2': heel_patch.tolist(),
               'scope': 'Observed opaque2x2sole-shading context, unique inside GPU foot ROI. Heel RGB alone repeats at source06[47,97] and cannot establish identity.'})
    grid_patch = frames[72][198:201, 398:401]
    assert grid_patch[1, 1].tolist() == [48, 68, 56, 255]
    observations, accepted, context_witnesses = [], {}, []
    for tick in ticks:
        row, frame = rows[tick], frames[tick]
        assert frame.shape == (280, 640, 4)
        assert np.array_equal(frame[198:201, 398:401], grid_patch), 'Grid moved or was occluded'
        root = np.array(row['world_root'])
        assert np.max(np.abs(root - (np.array([395, 155]) + DIRECTION * 158 * row['time']))) < .00005
        for name, source_xy in FEATURES.items():
            target = source_target(row['exposure'], source_xy)
            native_rgba = source[source_xy[1], source_xy[0]]
            assert native_rgba[3] == 255
            selected = array(R / f"inputs/source/{row['exposure']:02}.png")
            assert np.array_equal(selected[target[1], target[0]], native_rgba)
            prediction = root + SCALE * (np.array(target) + .5 - PIVOT)
            if name == 'ankle_context':
                candidates = find_patch(frame, patch)
                source_repeats = None
            elif name == 'heel':
                candidates = find_heel_context(frame, heel_patch)
                source_repeats = int(np.all(source[94:111, 42:63] == native_rgba, axis=2).sum())
            else:
                matches = np.argwhere(np.all(frame[ROI[1]:ROI[3], ROI[0]:ROI[2]] == native_rgba, axis=2))
                candidates = (matches[:, ::-1] + [ROI[0], ROI[1]]).tolist()
                source_repeats = int(np.all(source[94:111, 42:63] == native_rgba, axis=2).sum())
            identified = False
            pixel = None
            source_index = None
            error = None
            reason = 'No exact feature in bounded GPU foot ROI; often nearest sampling omits the texel/context.'
            if len(candidates) == 1:
                candidate = candidates[0]
                source_index = inverse_sample(row, candidate).tolist()
                center_error = np.array(candidate) + .5 - prediction
                footprint_ok = float(np.max(np.abs(center_error))) <= SCALE / 2 + .0001
                actual_source_ok = source_index == target
                unique_identity = name in ['ankle_context', 'heel'] or source_repeats == 1
                identified = footprint_ok and actual_source_ok and unique_identity
                if identified:
                    pixel, error = candidate, center_error.tolist()
                    reason = 'Unique observed exact RGBA context and source-coverage check pass.'
                else:
                    reason = 'Observed color/context is not an unambiguous source feature; repeated color or native coverage differs.'
            elif len(candidates) > 1:
                reason = 'Multiple exact GPU colors/contexts in the bounded foot ROI; no unique feature asserted.'
            item = {'tick': tick, 'phase': row['exposure'], 'time': row['time'], 'feature': name,
                    'source06_xy': source_xy, 'selected_native_xy': target, 'source_RGBA': native_rgba.tolist(),
                    'ideal_native_center_to_screen': prediction.tolist(), 'GPU_exact_candidates': candidates,
                    'source_color_count_in_literal_boot_window': source_repeats, 'identified': identified,
                    'pixel_xy': pixel, 'raster_center_error': error, 'inverse_native_xy': source_index,
                    'reason': reason, 'world_root': row['world_root'], 'GPU_PNG_sha256': sha(R / f'inputs/gpu/{tick:04}.png')}
            observations.append(item)
            if identified:
                accepted[(tick, name)] = item
                if name in ['ankle_context', 'heel']:
                    x, y = pixel
                    offsets = [-1, 0, 1] if name == 'ankle_context' else [-1, 0]
                    for dy in offsets:
                        for dx in offsets:
                            gx, gy = x + dx, y + dy
                            nx, ny = inverse_sample(row, [gx, gy])
                            if row['exposure'] == 6:
                                sx, sy = nx, ny
                            else:
                                sx, sy = np.load(R / f"inputs/source/{row['exposure']:02}-map.npz")['source_xy'][ny, nx]
                            assert sx >= 0 and sy >= 0
                            color = frame[gy, gx].tolist()
                            assert source[sy, sx].tolist() == color
                            assert source[sy, sx, 3] == 255
                            context_witnesses.append({'tick': tick, 'feature': name, 'GPU_xy': [gx, gy], 'selected_native_xy': [int(nx), int(ny)],
                                                      'source06_xy': [int(sx), int(sy)], 'actual_GPU_RGBA': color,
                                                      'opaque_source_RGBA_exact': True})
    write_json(args.output / 'FEATURE-OBSERVATIONS.json', observations)
    write_json(args.output / 'OPAQUE-CONTEXT-WITNESSES.json', context_witnesses)
    measured = []
    for item in observations:
        if not item['identified']:
            continue
        x, y = item['pixel_xy']
        measured.append({'tick': item['tick'], 'phase': item['phase'], 'time': item['time'], 'feature': item['feature'],
                         'GPU_x': x, 'GPU_y': y, 'grid_x': int(GRID[0]), 'grid_y': int(GRID[1]),
                         'feature_minus_fixed_grid_x': x - int(GRID[0]), 'feature_minus_fixed_grid_y': y - int(GRID[1]),
                         'source06_x': item['source06_xy'][0], 'source06_y': item['source06_xy'][1],
                         'PNG_sha256': item['GPU_PNG_sha256']})
    write_csv(args.output / 'MEASURED-PIXELS.csv', measured)
    displacements = []
    for a, b in [(72, 75), (72, 78), (72, 89), (89, 90), (90, 107), (107, 108), (72, 108), (108, 125)]:
        for feature in ['heel', 'ankle_context']:
            if (a, feature) not in accepted or (b, feature) not in accepted:
                continue
            start, end = accepted[(a, feature)], accepted[(b, feature)]
            observed = np.array(end['pixel_xy']) - start['pixel_xy']
            delta_root = np.array(rows[b]['world_root']) - rows[a]['world_root']
            native = SCALE * (np.array(end['selected_native_xy']) - start['selected_native_xy'])
            predicted = delta_root + native
            displacements.append({'feature': feature, 'from_tick': a, 'to_tick': b,
                                  'from_phase': rows[a]['exposure'], 'to_phase': rows[b]['exposure'],
                                  'seconds': rows[b]['time'] - rows[a]['time'], 'observed_dx': int(observed[0]),
                                  'observed_dy': int(observed[1]), 'observed_along_SE': float(observed @ DIRECTION),
                                  'predicted_root_plus_source_along_SE': float(predicted @ DIRECTION),
                                  'observed_minus_prediction_along': float((observed - predicted) @ DIRECTION),
                                  'predicted_root_travel': float(delta_root @ DIRECTION),
                                  'same_cel': rows[a]['exposure'] == rows[b]['exposure'],
                                  'ground_grid_displacement': 0, 'contact_proven': False})
    write_csv(args.output / 'DISPLACEMENTS.csv', displacements)
    write_json(args.output / 'RESULTS.json', {'scope': 'Existing captured Godot GPU frames only, authored root fixture; not input/physics or plantar contact.',
               'capture_receipt_passed': receipt['passed'], 'engine': receipt['engine'], 'display': receipt['display'],
               'camera': 'No Camera2D in SubViewport; fixed640x280 screen/world mapping.',
               'sprite_registration': {'pivot': PIVOT.tolist(), 'offset': [0, -48], 'scale': SCALE, 'source_stage': [128, 128]},
               'selected_ticks': ticks, 'fixed_ground_grid_pixel': GRID.tolist(), 'fixed_grid_RGBA_exact_in_all_samples': True,
               'observations': len(observations), 'identified_features': len(accepted), 'opaque_context_pixel_checks': len(context_witnesses),
               'matching_ROI': list(ROI), 'matching_rule': 'Exact unique observed2x2GPU sole context or3x3GPU ankle context; require true source texel footprint and map identity. Original forefoot/ankle single-pixel colors remain ambiguous.',
               'source_texel_footprint_half_width_pixels': SCALE / 2,
               'numeric_tolerance_pixels': .0001, 'two_endpoint_along_raster_bound_pixels': SCALE * math.sqrt(2),
               'source_heel06': [49, 109], 'source_original_ankle06': [51, 101], 'refined_context_center06': [49, 102],
               'alpha_rule': 'All accepted source texels/context pixels are alpha255 and exact RGB in final GPU PNG. Transparent/partial-alpha contour colors excluded; alpha255 PNG alone does not prove source opacity.',
               'source_study_frozen': True, 'new_engine_or_browser_runs': 0, 'canonical_writes': 0, 'new_art_or_settings': 0})
    proof_sheet(args.output, 'held04-72-78-89-6x.png', [72, 78, 89], frames, rows, accepted)
    proof_sheet(args.output, 'contact04-05-06-6x.png', [72, 90, 108], frames, rows, accepted)
    proof_sheet(args.output, 'nearest-sampling-72-80-89-6x.png', [72, 80, 89], frames, rows, accepted)
    Image.fromarray(frames[72]).crop((384, 100, 464, 216)).resize((320, 464), Image.Resampling.NEAREST).save(args.output / 'right-actor-context72-4x.png')
    print(json.dumps({'accepted': len(accepted), 'source_context_checks': len(context_witnesses), 'grid_fixed': True,
                      'measured_deltas': [r for r in displacements if (r['from_tick'], r['to_tick']) in [(72, 89), (72, 108)]]}))

if __name__ == '__main__':
    main()
