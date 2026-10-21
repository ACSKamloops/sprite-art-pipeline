#!/usr/bin/env python3
"""Pinned rational-grid sprite import and portable RPG delivery. No model calls."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import struct
import sys
from fractions import Fraction as F
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import canonical_json, export_aseprite, import_aseprite, project_hash, read_aseprite


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


constructor = module('rpg_constructor', TOOLKIT / 'scripts/sprite_construct.py')
delivery = module('rpg_delivery', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
apng = module('rpg_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rgba_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def rational(value):
    require(isinstance(value, list) and len(value) == 2 and all(type(v) is int for v in value) and value[1] > 0,
            'Expected rational [integer numerator, positive denominator]')
    return F(*value)


def rat(value):
    value = F(value)
    return [value.numerator, value.denominator]


def fresh(path):
    require(not path.exists() and not path.is_symlink(), 'Fresh output required: ' + str(path))
    path.mkdir(parents=True)


def contract_at(path):
    c = read(path)
    require(c['schema'] == 'hero-rpg-expansion/v1' and c['canvas'] == [80, 80] and c['pivot'] == [40, 72], 'Require fixed80 stage/pivot40,72 contract')
    require(c['layout']['columns'] == 4 and c['layout']['rows'] == 6, 'Require explicit4x6 bank')
    require(sorted(i for cells in c['layout']['cells'].values() for i in cells) == list(range(24)), 'Cells must cover0..23 once')
    for action, cells in c['layout']['cells'].items():
        data = c['actions'][action]
        holds = [rational(h) for h in data['holds']]
        require(len(holds) == len(cells) and all(h > 0 for h in holds), 'Positive hold per cell required')
        for event in data.get('events', []):
            require(0 <= rational(event['time']) < sum(holds, F()), 'Event outside clip')
    return c


def prepare(image, recipe):
    alpha, palette = recipe['alpha'], recipe['palette']
    require(set(alpha) <= {'mode', 'threshold', 'remove_below', 'canonicalize_transparent_rgb', 'chroma_key'}, 'Unknown alpha operation')
    mode = alpha.get('mode', 'preserve')
    require(mode in ['preserve', 'binary'], 'Unknown alpha mode')
    threshold = alpha['threshold'] if mode == 'binary' else alpha['remove_below']
    require(type(threshold) is int and 0 <= threshold <= 255, 'Invalid alpha threshold')
    require(alpha['canonicalize_transparent_rgb'] is True, 'Explicit alpha0RGB canonicalization required by editable toolkit')
    key = alpha.get('chroma_key')
    if key:
        require(len(key['rgb']) == 3 and all(type(c) is int and 0 <= c <= 255 for c in key['rgb']), 'Invalid key color')
        require(type(key['max_channel_distance']) is int and 0 <= key['max_channel_distance'] <= 255, 'Invalid key tolerance')
    require(palette['mode'] in ['preserve', 'exact-rgba-map', 'fixed'], 'No implicit palette fitting')
    table = {}
    fixed = palette.get('palette_rgba', [])
    if palette['mode'] == 'fixed':
        require(bool(fixed) and all(len(c) == 4 and c[3] == 255 and all(type(v) is int and 0 <= v <= 255 for v in c) for c in fixed), 'Fixed palette requires explicit opaqueRGBA colors')
    if palette['mode'] == 'exact-rgba-map':
        for entry in palette['entries']:
            for color in [entry['from'], entry['to']]:
                require(len(color) == 4 and all(type(c) is int and 0 <= c <= 255 for c in color), 'Invalid RGBA mapping')
            require(tuple(entry['from']) not in table, 'Duplicate palette source')
            table[tuple(entry['from'])] = tuple(entry['to'])
    counts = dict(positive_alpha_removed=0, alpha_promoted_to_255=0, chroma_key_removed=0, alpha0_hidden_rgb_zeroed=0, palette_changed=0)
    nearest = {}
    pixels = []
    for p in image.get_flattened_data():
        if 0 < p[3] < threshold:
            counts['positive_alpha_removed'] += 1
            p = (0, 0, 0, 0)
        elif mode == 'binary' and p[3]:
            counts['alpha_promoted_to_255'] += p[3] != 255
            p = (*p[:3], 255)
        if key and p[3] and max(abs(p[c] - key['rgb'][c]) for c in range(3)) <= key['max_channel_distance']:
            counts['chroma_key_removed'] += 1
            p = (0, 0, 0, 0)
        if palette['mode'] == 'fixed' and p[3]:
            if p[:3] not in nearest:
                nearest[p[:3]] = min(fixed, key=lambda c: sum((p[i]-c[i])**2 for i in range(3)))[:3]
            mapped = (*nearest[p[:3]], p[3])
        else:
            mapped = table.get(p, p)
        counts['palette_changed'] += mapped != p
        p = mapped
        if p[3] == 0 and any(p[:3]):
            counts['alpha0_hidden_rgb_zeroed'] += 1
            p = (0, 0, 0, 0)
        pixels.append(p)
    result = Image.new('RGBA', image.size)
    result.putdata(pixels)
    return result, counts


def export_action(out, action, direction, images, data, provenance, cells):
    project_dir = out / 'construction' / action
    project_dir.mkdir(parents=True)
    holds = [rational(h) for h in data['holds']]
    tick_rate = math.lcm(*(h.denominator for h in holds), *(rational(e['time']).denominator for e in data.get('events', [])))
    frames = []
    for i, (image, hold, cell) in enumerate(zip(images, holds, cells)):
        image.save(project_dir / f'{i:04d}.png')
        frames.append({'id': f'cell-{cell:02d}', 'duration_ticks': int(hold*tick_rate), 'landmarks': {},
                       'cels': {'body': {'image': f'{i:04d}.png', 'at': [0, 0]}}})
    events = [{'at_tick': int(rational(e['time'])*tick_rate), 'name': e['name']} for e in data.get('events', [])]
    spec = {'schema': 'sprite-construction-spec/v1',
            'canvas': {'width': 80, 'height': 80, 'render_pivot': [40, 72], 'ground_pivot': [40, 72]},
            'layers': [{'id': 'body', 'name': 'Whole-body paint; no anatomical rig', 'locked': False}],
            'frames': frames, 'animations': [{'id': f'{action}_{direction}', 'frames': [f['id'] for f in frames], 'fps': tick_rate, 'loop': data['loop'], 'events': events}], 'provenance': provenance}
    write(project_dir / 'spec.json', spec)
    project = constructor.construct(project_dir / 'spec.json')
    (project_dir / 'project.json').write_text(canonical_json(project) + '\n')
    clip = out / 'actions' / action
    receipt = delivery.export(project_dir / 'project.json', clip, toolkit=TOOLKIT, columns=4, actor='hero')
    manifest = read(clip / 'manifest.json')
    manifest.update({'action': action, 'direction': direction, 'events': data.get('events', []), 'anchors': {'hand': 'pending measurement', 'grip': 'pending measurement', 'release': 'pending measurement'},
                     'event_scope': 'Authored data only; no gameplay/contact/damage-window proof'})
    write(clip / 'manifest.json', manifest)
    engine = read(clip / 'clips.json')
    engine['clips'][0].update({'action': action, 'direction': direction, 'pivot_pixels': [40, 72], 'ground_pivot_pixels': [40, 72], 'authored_events': data.get('events', [])})
    write(clip / 'clips.json', engine)
    receipt.update({'manifest_sha256': sha(clip / 'manifest.json'), 'clips_sha256': sha(clip / 'clips.json'), 'rpg_extension': 'Direction/pivots/authored event data added; receipt rebound'})
    write(clip / 'DELIVERY-RECEIPT.json', receipt)
    export_aseprite(project, clip / 'editable.aseprite')
    require(project_hash(import_aseprite(clip / 'editable.aseprite')) == project_hash(project), 'ASE import project mismatch')
    decoded = read_aseprite(clip / 'editable.aseprite')
    for i, expected in enumerate(images):
        require(decoded['frames'][i]['cels'][0].tobytes() == expected.tobytes(), 'ASE decoded RGBA mismatch')
        require(Image.open(clip / f'frames/{i:04d}.png').convert('RGBA').tobytes() == expected.tobytes(), 'Constructor altered RGBA')
    receipt = apng.convert(clip / 'manifest.json', clip / 'apng')
    return {'action': action, 'direction': direction, 'manifest': f'actions/{action}/manifest.json', 'manifest_sha256': sha(clip / 'manifest.json'),
            'project': f'actions/{action}/project.json', 'aseprite': f'actions/{action}/editable.aseprite', 'atlas': f'actions/{action}/atlas.png',
            'apng': f'actions/{action}/apng/animation.apng.png', 'apng_sha256': receipt['output_sha256'], 'frame_count': len(images), 'duration': manifest['duration'],
            'mechanics': {'ase_decoded_rgba_exact': True, 'ase_project_roundtrip_exact': True, 'apng_decoded_rgba_and_holds_exact': True}}


def import_sheet(args):
    c, recipe = contract_at(args.contract), read(args.recipe)
    require(recipe['schema'] == 'rpg-bank-import/v1', 'Unknown import recipe')
    direction = recipe['direction']
    require(direction in c['directions'], 'Unknown direction')
    require(recipe.get('review_status', 'unreviewed') in ['unreviewed', 'rejected'], 'Importer cannot grant art approval')
    if recipe.get('review_status') == 'rejected':
        require(bool(recipe.get('review_reason')), 'Rejected bank needs reason')
    source = (args.recipe.resolve().parent / recipe['source']['file']).resolve()
    require(sha(source) == recipe['source']['sha256'], 'Stale source PNG pin')
    palette_source = recipe['palette'].get('source')
    if palette_source:
        palette_path = (args.recipe.resolve().parent/palette_source['file']).resolve()
        require(sha(palette_path) == palette_source['sha256'], 'Stale palette source pin')
    with Image.open(source) as opened:
        require(opened.format == 'PNG' and getattr(opened, 'n_frames', 1) == 1, 'Static PNG source required')
        raw = opened.convert('RGBA')
    require(list(raw.size) == recipe['source']['size'], 'Actual dimensions differ from recipe')
    transform = recipe['transform']
    scale = rational(transform['scale'])
    require(scale > 0 and transform['stage_anchor'] == [40, 72], 'Positive uniform scale/fixed stage anchor required')
    anchor = [rational(v) for v in transform['source_anchor']]
    offsets = {}
    for entry in transform.get('row_offsets', []):
        row = entry['row']
        require(type(row) is int and 0 <= row < 6 and row not in offsets and bool(entry['reason']), 'Unique justified row offset required')
        offsets[row] = [rational(v) for v in entry['delta_source']]
    prepared, counts = prepare(raw, recipe)
    out = args.output.absolute()
    fresh(out)
    for folder in ['source', 'raw-crops', 'source-maps', 'staged', 'construction', 'actions']:
        (out / folder).mkdir()
    shutil.copy2(source, out / 'source/raw.png')
    shutil.copy2(args.recipe, out / 'recipe.json')
    shutil.copy2(args.contract, out / 'contract.json')
    if palette_source:
        shutil.copy2(palette_path, out/'source/palette-source.json')
    # Original recipe bytes remain authority; this equivalent recipe resolves only bundled inputs.
    replay_recipe = json.loads(json.dumps(recipe))
    replay_recipe['source']['file'] = 'source/raw.png'
    if palette_source:
        replay_recipe['palette']['source']['file'] = 'source/palette-source.json'
    write(out/'replay-recipe.json', replay_recipe)
    prepared.save(out / 'source/prepared.png')
    pixels, records, images = prepared.load(), [], []
    width, height = raw.size
    grid = recipe.get('source_grid')
    x_boundaries = [F(i*width,4) for i in range(5)]
    y_boundaries = [F(i*height,6) for i in range(7)]
    if grid:
        require(bool(grid['reason']), 'Measured partition needs justification')
        x_boundaries = [rational(v) for v in grid.get('x_boundaries', [rat(v) for v in x_boundaries])]
        y_boundaries = [rational(v) for v in grid.get('y_boundaries', [rat(v) for v in y_boundaries])]
        require(len(x_boundaries) == 5 and len(y_boundaries) == 7 and x_boundaries[0] == y_boundaries[0] == 0 and x_boundaries[-1] == width and y_boundaries[-1] == height,
                'Explicit partitions must span whole actual source')
        require(all(a < b for values in [x_boundaries,y_boundaries] for a,b in zip(values,values[1:])), 'Partitions must increase strictly')
    boundary_checks = []
    alpha = prepared.getchannel('A')
    for axis, values in [('x',x_boundaries),('y',y_boundaries)]:
        for value in values[1:-1]:
            if value.denominator == 1:
                coordinate = int(value)
                pairs = [(alpha.getpixel((coordinate-1,t)),alpha.getpixel((coordinate,t))) for t in range(height)] if axis == 'x' else [(alpha.getpixel((t,coordinate-1)),alpha.getpixel((t,coordinate))) for t in range(width)]
                boundary_checks.append({'axis':axis,'boundary':int(value),'adjacent_alpha_positive_pairs':sum(a > 0 and b > 0 for a,b in pairs),
                                        'adjacent_opaque_subject_pairs':sum(a >= 128 and b >= 128 for a,b in pairs), 'opaque_pixels_either_side':sum(a >= 128 or b >= 128 for a,b in pairs)})
    for cell in range(24):
        col, row = cell % 4, cell // 4
        bounds = [x_boundaries[col],y_boundaries[row],x_boundaries[col+1],y_boundaries[row+1]]
        box = [math.floor(bounds[0]), math.floor(bounds[1]), math.ceil(bounds[2]), math.ceil(bounds[3])]
        raw.crop(box).save(out / f'raw-crops/{cell:02d}.png')
        offset = offsets.get(row, [F(), F()])
        # Pixel-boundary coordinates: map destination centers, then floor.
        xs = [bounds[0]+anchor[0]+offset[0]+(F(2*x+1, 2)-40)/scale for x in range(80)]
        ys = [bounds[1]+anchor[1]+offset[1]+(F(2*y+1, 2)-72)/scale for y in range(80)]
        image, samples, mapping = Image.new('RGBA', (80, 80)), [], bytearray()
        for sy in ys:
            for sx in xs:
                valid = bounds[0] <= sx < bounds[2] and bounds[1] <= sy < bounds[3]
                ix, iy = (math.floor(sx), math.floor(sy)) if valid else (-1, -1)
                samples.append(pixels[ix, iy] if valid else (0, 0, 0, 0))
                mapping += struct.pack('<ii', ix, iy)
        image.putdata(samples)
        image.save(out / f'staged/{cell:02d}.png')
        map_path = out / f'source-maps/{cell:02d}.i32le'
        map_path.write_bytes(mapping)
        bbox = image.getchannel('A').getbbox()
        source_bbox = prepared.crop(box).getchannel('A').getbbox()
        source_edge = bool(source_bbox and (source_bbox[0] == 0 or source_bbox[1] == 0 or source_bbox[2] == box[2]-box[0] or source_bbox[3] == box[3]-box[1]))
        mapped_bbox = None
        if source_bbox:
            mapped_bbox = [(F(box[axis % 2]+source_bbox[axis])-bounds[axis % 2]-anchor[axis % 2]-offset[axis % 2])*scale+[40,72][axis % 2] for axis in range(4)]
        clipped = bool(mapped_bbox and (mapped_bbox[0] < 0 or mapped_bbox[1] < 0 or mapped_bbox[2] > 80 or mapped_bbox[3] > 80))
        record = {'cell': cell, 'row': row, 'column': col, 'logical_bounds_rational': [rat(v) for v in bounds], 'raw_enclosing_crop': box,
                  'raw_crop_sha256': sha(out / f'raw-crops/{cell:02d}.png'), 'source_map': f'source-maps/{cell:02d}.i32le', 'source_map_sha256': sha(map_path),
                  'staged': f'staged/{cell:02d}.png', 'staged_sha256': sha(out / f'staged/{cell:02d}.png'), 'staged_rgba_sha256': rgba_sha(image),
                  'alpha_bounds': bbox, 'empty': bbox is None, 'edge_contact': bool(bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == 80 or bbox[3] == 80))}
        record.update({'prepared_source_alpha_bounds_in_enclosing_crop': source_bbox, 'source_cell_boundary_contact': source_edge,
                       'transformed_source_alpha_bounds_rational': [rat(v) for v in mapped_bbox] if mapped_bbox else None, 'stage_clipping': clipped})
        if 'expected_staged_rgba_sha256' in recipe:
            require(rgba_sha(image) == recipe['expected_staged_rgba_sha256'][cell], 'Frozen stage hash mismatch')
        records.append(record)
        images.append(image)
    warnings = [{'cell': r['cell'], 'empty': r['empty'], 'source_cell_boundary_contact': r['source_cell_boundary_contact'], 'stage_clipping': r['stage_clipping']} for r in records if r['empty'] or r['source_cell_boundary_contact'] or r['stage_clipping']]
    clipping = recipe.get('clipping', {'mode': 'reject'})
    require(clipping['mode'] in ['reject', 'record'], 'Unknown clipping policy')
    require(clipping['mode'] != 'record' or bool(clipping.get('reason')), 'Recording clipping requires explicit reason')
    write(out/'REGISTRATION.json', {'cells': records, 'warnings': warnings, 'clipping_policy': clipping, 'source_grid':grid,
                                   'integer_partition_alpha_checks':boundary_checks,
                                   'scope': 'Prepared alpha bounds expose stage clipping/cell-edge contact; source/crops retained. Cell-edge contact flags possible cross-cell spill; ownership is not inferred.'})
    require(not warnings or clipping['mode'] == 'record', 'Empty/cell-edge/clipping warning; retained REGISTRATION.json. Repair registration or explicitly record justified candidate limits')
    provenance = {'source_png_sha256': sha(source), 'recipe_sha256': sha(args.recipe), 'contract_sha256': sha(args.contract), 'registration': transform,
                  'operation': 'One whole-sheet rational registration; explicit nearest sampling/alpha/palette', 'source_grid':grid, 'alpha': recipe['alpha'], 'palette': recipe['palette'], 'art_status': 'unreviewed'}
    actions = [export_action(out, action, direction, [images[i] for i in cells], c['actions'][action], provenance, cells) for action, cells in c['layout']['cells'].items()]
    result = {'schema': 'rpg-bank-delivery/v1', 'direction': direction, 'source': {'file': 'source/raw.png', 'sha256': sha(source), 'size': list(raw.size)},
              'recipe_sha256': sha(args.recipe), 'contract_sha256': sha(args.contract), 'importer_sha256': sha(__file__), 'prepared_rgba_sha256': rgba_sha(prepared),
              'alpha_palette_counts': counts, 'registration': transform, 'source_map_format': '80x80 row-major little-endian int32 globalSourceX,Y pairs; -1,-1 transparent. Replay against prepared source.',
              'source_grid':grid, 'integer_partition_alpha_checks':boundary_checks,
              'fixed_palette_rule': 'Minimum squaredRGB distance to explicit ordered palette; ties choose first. Prepared alpha preserved; same palette across whole sheet.' if recipe['palette']['mode'] == 'fixed' else None,
              'registration_warnings': warnings,
              'grid_boundary_rule': 'Exact rational equal cells or explicitly measured common partitions; integer enclosing raw crops. Source sample uses partition origin+declared anchor+row offset; no normalization by cell size or individual fitting',
              'review_status': recipe.get('review_status', 'unreviewed'), 'review_reason': recipe.get('review_reason'), 'actions': actions, 'cells': records,
              'limits': ['No art acceptance', 'No external editor GUI save/reopen', 'No engine playback/contact test', 'Bounds diagnostic only; no automatic clipping repair'],
              'source_unchanged': sha(source) == recipe['source']['sha256']}
    require(result['source_unchanged'], 'Source changed during import')
    write(out / 'BANK.json', result)
    return {'output': str(out), 'direction': direction, 'actions': len(actions), 'frames': 24, 'empty_cells': sum(r['empty'] for r in records), 'edge_contact_cells': sum(r['edge_contact'] for r in records)}


def portable_copy(source, destination):
    require(source.is_dir() and not source.is_symlink(), 'Expected actual directory')
    pins = {}
    for path in sorted(source.rglob('*')):
        require(not path.is_symlink(), 'Symlinks are not portable: ' + str(path))
        if path.is_file():
            pins[str(path.relative_to(source))] = sha(path)
    shutil.copytree(source, destination)
    require(all(sha(destination/name) == digest and sha(source/name) == digest for name, digest in pins.items()), 'Source/copy changed')
    return pins


def verify_bank(args):
    """Replay saved integer maps, independently of rational coordinate rebuilding."""
    bank, recipe = read(args.bank/'BANK.json'), read(args.bank/'recipe.json')
    require(sha(args.bank/'recipe.json') == bank['recipe_sha256'], 'Stale recipe copy')
    require(sha(args.bank/'source/raw.png') == bank['source']['sha256'], 'Stale raw source')
    raw = Image.open(args.bank/'source/raw.png').convert('RGBA')
    prepared, _ = prepare(raw, recipe)
    require(rgba_sha(prepared) == bank['prepared_rgba_sha256'], 'Prepared source changed')
    require(Image.open(args.bank/'source/prepared.png').convert('RGBA').tobytes() == prepared.tobytes(), 'Prepared PNG mismatch')
    source_pixels, staged = prepared.load(), []
    for record in bank['cells']:
        map_path = args.bank/record['source_map']
        require(sha(map_path) == record['source_map_sha256'], 'Stale source map')
        mapping = map_path.read_bytes()
        require(len(mapping) == 80*80*8, 'Source map dimensions changed')
        samples = []
        for x,y in struct.iter_unpack('<ii', mapping):
            require((x,y) == (-1,-1) or (0 <= x < prepared.width and 0 <= y < prepared.height), 'Out-of-range map coordinate')
            samples.append((0,0,0,0) if x == -1 else source_pixels[x,y])
        replay = Image.new('RGBA',(80,80))
        replay.putdata(samples)
        require(rgba_sha(replay) == record['staged_rgba_sha256'], 'Frozen-map replay mismatch')
        require(sha(args.bank/record['staged']) == record['staged_sha256'], 'Stale staged PNG')
        require(Image.open(args.bank/record['staged']).convert('RGBA').tobytes() == replay.tobytes(), 'Staged/map RGBA mismatch')
        require(sha(args.bank/f'raw-crops/{record["cell"]:02d}.png') == record['raw_crop_sha256'], 'Stale raw crop')
        staged.append(replay)
    for action in bank['actions']:
        path = args.bank/action['manifest']
        require(sha(path) == action['manifest_sha256'], 'Stale action manifest')
        manifest = read(path)
        expected = [staged[int(frame['source_frame_id'].split('-')[-1])] for frame in manifest['frames']]
        ase = read_aseprite(path.parent/'editable.aseprite')
        for i, (frame, image) in enumerate(zip(manifest['frames'], expected)):
            require(sha(path.parent/frame['file']) == frame['sha256'], 'Stale exported frame')
            require(Image.open(path.parent/frame['file']).convert('RGBA').tobytes() == image.tobytes(), 'Exported PNG/map mismatch')
            require(ase['frames'][i]['cels'][0].tobytes() == image.tobytes(), 'ASE/map mismatch')
        apng.verify((path.parent/'apng/animation.apng.png').read_bytes(), expected, [rational(f['hold']) for f in manifest['frames']], 0 if manifest['loop'] else 1)
    result = {'schema':'rpg-bank-verification/v1', 'bank_sha256':sha(args.bank/'BANK.json'), 'frames':len(staged), 'actions':len(bank['actions']),
              'integer_map_replay_exact':True, 'exported_png_ase_apng_exact':True, 'scope':'Frozen integer-map replay and export pixels/clocks; no art or gameplay approval'}
    if args.report:
        require(not args.report.exists(), 'Fresh report required')
        write(args.report,result)
    return result


def review_clip(root, path, role, status, action, direction, variant):
    manifest = read(path)
    require(manifest['canvas'] == [80, 80], 'Review clips require80px stage')
    frames = []
    for frame in manifest['frames']:
        rel = Path(frame['file'])
        require(not rel.is_absolute() and '..' not in rel.parts, 'Escaping frame path')
        image = path.parent / rel
        require(sha(image) == frame['sha256'], 'Stale review frame')
        frames.append({**frame, 'file': str(image.relative_to(root))})
    return {'id': f'{action}_{direction}_{variant}', 'action': action, 'direction': direction, 'variant': variant, 'role': role, 'review_status': status,
            'loop': manifest['loop'], 'duration': manifest['duration'], 'frames': frames, 'manifest': str(path.relative_to(root)), 'manifest_sha256': sha(path), 'events': manifest.get('events', [])}


def assemble(args):
    c, banks, seen = contract_at(args.contract), [], set()
    for path in args.bank:
        bank = read(path / 'BANK.json')
        require(bank['contract_sha256'] == sha(args.contract) and bank['direction'] not in seen, 'Duplicate direction or other contract')
        seen.add(bank['direction'])
        for action in bank['actions']:
            require(sha(path / action['manifest']) == action['manifest_sha256'], 'Stale bank manifest')
        banks.append((path, bank))
    out = args.output.absolute()
    fresh(out)
    (out / 'banks').mkdir()
    shutil.copy2(args.contract, out / 'CONTRACT.json')
    baseline = Path(c['baseline']).resolve()
    pins = portable_copy(baseline, out / 'preferred-original-SE-walk')
    clips = [review_clip(out, out/'preferred-original-SE-walk/manifest.json', 'preferred', 'preferred', 'walk', 'SE', 'original')]
    for path, bank in banks:
        direction = bank['direction']
        portable_copy(path.resolve(), out / 'banks' / direction)
        for action in bank['actions']:
            experimental = direction == 'SE' and action['action'] == 'walk'
            clips.append(review_clip(out, out/'banks'/direction/action['manifest'], 'experimental' if experimental else 'candidate', bank['review_status'], action['action'], direction, 'generated'))
    selected, coverage = {}, []
    for direction in c['directions']:
        for action in c['actions']:
            options = [clip for clip in clips if clip['direction'] == direction and clip['action'] == action]
            pick = next((v for v in options if v['role'] == 'preferred'), None) or next((v for v in options if v['review_status'] != 'rejected' and v['role'] != 'experimental'), None)
            if pick:
                selected[f'{action}_{direction}'] = pick['id']
            coverage.append({'direction': direction, 'action': action, 'selected': pick['id'] if pick else None, 'status': pick['review_status'] if pick else 'missing',
                             'variants': [{'id': v['id'], 'role': v['role'], 'review_status': v['review_status']} for v in options]})
            if not pick and options and all(v['review_status'] == 'rejected' for v in options):
                coverage[-1]['status'] = 'rejected'
    write(out/'library.json', {'schema': 'rpg-review-library/v1', 'canvas': [80,80], 'pivot': [40,72], 'directions': c['directions'], 'actions': list(c['actions']), 'reference': clips[0]['id'], 'selected': selected, 'clips': clips,
                               'limits': 'Preferred is original SE walk/view only. New actions/views unreviewed. Events are authored metadata, not gameplay proof.'})
    write(out/'COVERAGE.json', {'schema': 'rpg-coverage/v1', 'entries': coverage, 'pending_additional_actions': c['pending_additional_actions'], 'runtime_verified': [], 'human_timed_review': [], 'preferred_scope': 'Original SE walk/view only'})
    engine = {'video_fps': 1, 'clips': [], 'scope': 'Resource bindings only; new art unreviewed; no gameplay verification'}
    by_id = {clip['id']: clip for clip in clips}
    for name, clip_id in selected.items():
        clip = by_id[clip_id]
        path = out / clip['manifest']
        record = read(path.parent/'clips.json')['clips'][0]
        tick_rate = math.lcm(*(rational(f['hold']).denominator for f in clip['frames']))
        record.update({'actor': 'hero', 'name': name, 'action': clip['action'], 'direction': clip['direction'], 'video_fps': tick_rate,
                       'sheet': str((path.parent/record['sheet']).relative_to(out)), 'pivot_pixels': [40,72], 'ground_pivot_pixels': [40,72],
                       'frames': [{'atlas_index': i, 'duration_video_frames': int(rational(f['hold'])*tick_rate)} for i,f in enumerate(clip['frames'])], 'authored_events': clip['events']})
        engine['clips'].append(record)
    write(out/'clips.json', engine)
    shutil.copy2(REPO/'skills/sprite-animation-pipeline/assets/build_godot.gd', out/'build_godot.gd')
    (out/'project.godot').write_text('config_version=5\n[application]\nconfig/name="RPG candidate resource check"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    shutil.copy2(Path(__file__).with_name('rpg-bank-review.html'), out/'index.html')
    write(out/'ASSEMBLY-RECEIPT.json', {'schema': 'rpg-assembly/v1', 'contract_sha256': sha(args.contract), 'baseline_source': str(baseline), 'baseline_file_sha256': pins,
                                       'baseline_copy_all_bytes_exact': True, 'preferred_binding': selected.get('walk_SE'), 'bank_directions': sorted(seen), 'engine_tested': False, 'native_editor_gui_tested': False})
    return {'output': str(out), 'clips': len(clips), 'selected_resource_bindings': len(selected), 'missing': sum(r['status'] == 'missing' for r in coverage), 'baseline_exact': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    importer = commands.add_parser('import-sheet')
    importer.add_argument('--recipe', type=Path, required=True)
    importer.add_argument('--contract', type=Path, required=True)
    importer.add_argument('--output', type=Path, required=True)
    assembler = commands.add_parser('assemble')
    assembler.add_argument('--contract', type=Path, required=True)
    assembler.add_argument('--bank', type=Path, action='append', default=[])
    assembler.add_argument('--output', type=Path, required=True)
    verifier = commands.add_parser('verify-bank')
    verifier.add_argument('--bank', type=Path, required=True)
    verifier.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = {'import-sheet':import_sheet, 'assemble':assemble, 'verify-bank':verify_bank}[args.command](args)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Error: {error}\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
