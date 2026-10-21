#!/usr/bin/env python3
"""Run the actual offline PixelEngine on pinned raw cells, without resizing."""
import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from math import lcm
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image

REPO = Path(__file__).resolve().parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


recipe = module('native_grid_exports', Path(__file__).with_name('author-pixel-candidates.py'))
sha, write, require = recipe.sha, recipe.write, recipe.require


def rgba_hash(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def run(args):
    plan_path, out = args.plan.resolve(), args.output.absolute()
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    plan = json.loads(plan_path.read_text())
    require(plan['schema'] == 'native-grid-production/v1', 'Unknown production plan')
    require(re.fullmatch('[A-Za-z0-9_-]+', plan['clip_id']) is not None, 'Filename-safe clip ID required')
    require(not args.verify_replay or args.reference_eight is not None, 'Exact replay requires the prior reference directory')
    pins, sheets = {}, {}
    for name, entry in plan['sheets'].items():
        require(re.fullmatch('[A-Za-z0-9_-]+', name) is not None, 'Filename-safe sheet ID required')
        path = Path(entry['file']).resolve()
        require(sha(path) == entry['sha256'], 'Stale source sheet pin: ' + name)
        image = Image.open(path).convert('RGBA')
        edge = entry['cell_edge']
        require(type(edge) is int and edge > 0 and image.size == (edge*3, edge*3), 'Require an explicit3x3 cell sheet')
        sheets[name] = image
        pins[name] = {'file': str(path), 'sha256': sha(path), 'cell_edge': edge}
    palette_path = Path(plan['palette_results']['file']).resolve()
    require(sha(palette_path) == plan['palette_results']['sha256'], 'Stale palette results pin')
    palette = json.loads(palette_path.read_text())['palette_rgba']
    require(len(palette) == 52 and all(len(p) == 4 and p[3] == 255 for p in palette), 'Require the explicit52-color opaque union palette')
    holds = [Fraction(*entry['hold']) for entry in plan['frames']]
    require(all(hold > 0 for hold in holds) and sum(holds, Fraction()) == 1, 'Positive exact holds must total1second')
    out.mkdir(parents=True)
    for folder in ['source', 'raw-crops', 'inputs', 'projects', 'clips']:
        (out / folder).mkdir()
    shutil.copy2(plan_path, out / 'plan.json')
    shutil.copy2(palette_path, out / 'source/palette-results.json')
    for name, entry in pins.items():
        shutil.copy2(entry['file'], out / 'source' / (name + '.png'))
    records = []
    for i, entry in enumerate(plan['frames']):
        sheet = sheets[entry['sheet']]
        edge = pins[entry['sheet']]['cell_edge']
        cell = entry['cell']
        require(type(cell) is int and 0 <= cell < 9, 'Invalid raw cell index')
        box = [(cell%3)*edge, (cell//3)*edge, (cell%3+1)*edge, (cell//3+1)*edge]
        crop = sheet.crop(box)
        raw = Image.frombytes('RGBA', crop.size, crop.tobytes())
        raw.save(out / f'raw-crops/{i:02d}.png')
        pixels = list(raw.get_flattened_data())
        prepared = Image.new('RGBA', raw.size)
        prepared.putdata([(0,0,0,0) if p[3] < 8 else p for p in pixels])
        prepared.save(out / f'inputs/{i:02d}.png')
        require(all(before == after for before, after in zip(pixels, prepared.get_flattened_data()) if before[3] >= 8), 'Alpha>=8RGBA changed')
        records.append({'position': i, 'id': entry['id'], 'sheet': entry['sheet'], 'cell': cell, 'source_sheet_sha256': pins[entry['sheet']]['sha256'],
                        'crop_box': box, 'raw_png_sha256': sha(out/f'raw-crops/{i:02d}.png'), 'raw_rgba_sha256': rgba_hash(raw),
                        'prepared_png_sha256': sha(out/f'inputs/{i:02d}.png'),
                        'positive_alpha1to7_removed': sum(0 < p[3] < 8 for p in pixels),
                        'alpha0_hidden_rgb_zeroed': sum(p[3] == 0 and any(p[:3]) for p in pixels), 'alpha_at_least8_rgba_exact': True})
    write(out / 'INPUTS.json', {'sheets': pins, 'palette_results_sha256': sha(palette_path), 'palette_rgba': palette, 'ordered_crops': records,
                              'alpha_policy': 'Set alpha1-7RGBA to transparent black; separately canonicalize hiddenRGB at alpha0. AllRGBA at alpha>=8 unchanged. No binary128 or resizing.'})
    timing = {'holds': [entry['hold'] for entry in plan['frames']], 'duration': [1,1], 'loop': True}
    (out/'timing.json').write_text(json.dumps(timing)+'\n')
    colors = ['#' + ''.join(f'{c:02x}' for c in p[:3]) for p in palette]
    command = ['node', str(REPO/'research/pixelengine-imagen/tools/offline-pixelengine.cjs'), 'process-frames',
               '--wrapper', str(args.wrapper.resolve()), '--wasm', str(args.wasm.resolve())]
    for i in range(len(records)):
        command += ['--input', str(out/f'inputs/{i:02d}.png')]
    command += ['--palette', json.dumps(colors), '--timing-sidecar', str(out/'timing.json'), '--output-dir', str(out/'wasm')]
    process = subprocess.run(command, capture_output=True, text=True)
    write(out/'INVOCATION.json', {'argv': command, 'returncode': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr})
    require(process.returncode == 0, 'Actual processor failed; retained invocation/receipt are authority')
    receipt = json.loads((out/'wasm/receipt.json').read_text())
    metadata = json.loads((out/'wasm/metadata.json').read_text())
    frames = [Image.open(out/f'wasm/frame-{i:06d}.png').convert('RGBA') for i in range(len(records))]
    sizes = {image.size for image in frames}
    require(len(sizes) == 1, 'Actual processor returned mixed grids; no scale invented')
    width, height = frames[0].size
    require(metadata['output_size'] == [width,height] and metadata['frame_count'] == len(records), 'Runtime metadata differs from actual native rasters')
    boxes = [image.getchannel('A').getbbox() for image in frames]
    if width > 80 or height > 80 or any(box is None for box in boxes):
        write(out/'INVALID_GRID.json', {'actual_grid': [width,height], 'boxes': boxes, 'reason': 'Grid exceeds80 or has empty actor; no scaling/fitting/export performed'})
        raise ValueError('Invalid actual native grid; retained before any invented scale')
    dx, dy = 40-width//2, 72-max(box[3] for box in boxes)
    if any(box[0]+dx < 0 or box[1]+dy < 0 or box[2]+dx > 80 or box[3]+dy > 80 for box in boxes):
        write(out/'INVALID_GRID.json', {'actual_grid': [width,height], 'offset': [dx,dy], 'boxes': boxes, 'reason': 'One global integer staging offset clips visible paint; no scaling/fitting performed'})
        raise ValueError('Global integer staging would clip visible paint')
    fps = lcm(*(hold.denominator for hold in holds))
    project_dir = out/'projects'/plan['clip_id']
    project_dir.mkdir()
    frame_specs = []
    staged = []
    for i, (entry, image, hold) in enumerate(zip(plan['frames'], frames, holds)):
        art = Image.new('RGBA', (80,80))
        art.paste(image, (dx,dy))
        art.save(project_dir/f'{i:02d}.png')
        staged.append(art)
        frame_specs.append({'id': entry['id'], 'duration_ticks': int(hold*fps), 'landmarks': {},
                            'cels': {'whole-body': {'image': f'{i:02d}.png', 'at': [0,0]}}})
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': {'width':80,'height':80,'render_pivot':[40,72],'ground_pivot':[40,72]},
            'layers': [{'id':'whole-body','name':'Actual PixelEngine whole-body raster; not an anatomical rig','locked':False}],
            'frames': frame_specs, 'animations': [{'id':'walk','frames':[f['id'] for f in frame_specs],'fps':fps,'loop':True,'events':[]}],
            'provenance': {'operation':'Actual pinned wrapper/WASM shared-grid conversion then one whole-clip integer placement; no resampling or per-frame fitting',
                           'actual_grid':[width,height], 'offset':[dx,dy], 'plan_sha256':sha(plan_path), 'adapter_receipt_sha256':sha(out/'wasm/receipt.json'),
                           'batch_warning':'Shared-grid/palette inference can change every key when sources are added; no eight-key exactness assumed for a new batch.'}}
    write(project_dir/'spec.json', spec)
    project = recipe.constructor.construct(project_dir/'spec.json')
    (project_dir/'project.json').write_text(recipe.canonical_json(project)+'\n')
    output = recipe.package(project, out/'clips'/plan['clip_id'], 'walk', args.native_editor)
    comparison = []
    if args.reference_eight:
        prior = args.reference_eight.resolve()
        old_staging = json.loads((prior/'STAGING.json').read_text())
        old_receipt = json.loads((prior/'wasm/receipt.json').read_text())
        for i, entry in enumerate(plan['frames']):
            if entry['sheet'] != 'keys':
                continue
            key = entry['cell']
            old_raw = prior/f'wasm/frame-{key:06d}.png'
            old_stage = prior/f'clips/native-grid/frames/{key:04d}.png'
            original = Image.open(old_stage).convert('RGBA')
            comparison.append({'position':i,'source_key':key,
                'prepared_input_png_exact':sha(out/f'inputs/{i:02d}.png') == sha(prior/f'inputs/{key:02d}.png'),
                'native_png_bytes_exact':sha(out/f'wasm/frame-{i:06d}.png') == sha(old_raw),
                'native_rgba_exact':frames[i].size == Image.open(old_raw).size and frames[i].tobytes() == Image.open(old_raw).convert('RGBA').tobytes(),
                'staged_png_bytes_exact':sha(out/f'clips/{plan["clip_id"]}/frames/{i:04d}.png') == sha(old_stage),
                'staged_rgba_exact':staged[i].tobytes() == original.tobytes(),
                'staged_changed_pixels':len(recipe.changed(original,staged[i]))})
        if args.verify_replay:
            require(len(records) == 8 and len(comparison) == 8 and all(all(row[k] for k in ['prepared_input_png_exact','native_png_bytes_exact','native_rgba_exact','staged_png_bytes_exact','staged_rgba_exact']) for row in comparison), 'Eight-only replay differs from prior exact bytes/pixels')
            require([width,height] == old_staging['actual_shared_grid'] and [dx,dy] == old_staging['offset'] and [list(b) for b in boxes] == old_staging['boxes'], 'Prior eight-only grid/staging differs')
            require(sha(out/'wasm/metadata.json') == sha(prior/'wasm/metadata.json') and sha(out/'timing.json') == sha(prior/'timing.json'), 'Prior runtime metadata/timing differs')
            require(receipt['requested_options'] == old_receipt['requested_options'] and receipt['wrapper']['sha256'] == old_receipt['wrapper']['sha256'] and receipt['wasm']['sha256'] == old_receipt['wasm']['sha256'], 'Processor binding/options differ')
            require(output['atlas_sha256'] == sha(prior/'clips/native-grid/atlas.png') and output['apng_sha256'] == sha(prior/'clips/native-grid/apng/animation.apng.png'), 'Prior atlas/APNG bytes differ')
    require(all(sha(Path(plan['sheets'][name]['file'])) == entry['sha256'] for name,entry in pins.items()) and sha(palette_path) == plan['palette_results']['sha256'], 'Immutable input changed')
    staging = {'actual_shared_grid':[width,height],'offset':[dx,dy],'grid_integer_center_anchor':[width//2, max(box[3] for box in boxes)],
               'stage_anchor':[40,72],'boxes':[list(b) for b in boxes],'per_frame_fitting':False,'spatial_resampling':False,
               'metadata':metadata,'actual_global_palette_count':len(metadata['palette']), 'adapter_receipt_sha256':sha(out/'wasm/receipt.json'),
               'exact_period':[1,1],'prior_eight_comparison':comparison,'eight_only_replay_verified':args.verify_replay,'output':output,
               'source_unchanged':True,'limits':'Actual local artifact and literal staging; no hosted equality, anatomy recovery, eight-key preservation for a changed batch, art score or timed playback acceptance.'}
    write(out/'STAGING.json', staging)
    print(json.dumps({'output':str(out),'grid':[width,height],'offset':[dx,dy],'replay_verified':args.verify_replay,'prior_key_changed_pixels':[c['staged_changed_pixels'] for c in comparison],'exports':output}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--wrapper',type=Path,required=True)
    parser.add_argument('--wasm',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference-eight',type=Path)
    parser.add_argument('--verify-replay',action='store_true')
    parser.add_argument('--native-editor')
    run(parser.parse_args())
