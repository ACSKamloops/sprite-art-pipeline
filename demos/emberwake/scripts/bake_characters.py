#!/usr/bin/env python3
"""Rebuild selected character banks from retained ImageGen sheets; never resubmit models."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import tempfile
import numpy as np
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art-source/characters-v2'
DIRECTIONS = ['south', 'east', 'north', 'west']
ACTIONS = {
    'idle': ([14, 15], [.58, .58], True),
    'walk': (list(range(8)), [.05625] * 8, True),
    'attack': (list(range(8, 14)), [.06, .07, .055, .055, .065, .105], False),
    'cast': (list(range(16, 22)), [.06, .08, .10, .08, .08, .10], False),
    'hurt': ([22, 23, 14], [.09, .10, .10], False),
    'dodge': ([24, 25, 26, 27], [.045, .105, .055, .055], False),
}
# Authored shared-sheet/row origins, not independent silhouette fitting.
# New paint stages differ between returned sheets. Measured neutral head/hip
# and foot baselines define each view; walk stride and pose deformation remain.
SETTINGS = {
    'lyra': {
        'south': {'anchor': [128, 228], 'scale': .49, 'row_y': [-3, 0, 0, 0]},
        'east': {'anchor': [126, 246], 'scale': .45},
        'north': {'anchor': [134, 229], 'scale': .47, 'row_y': [-4, 0, 0, 0]},
        'west': {'anchor': [139, 236], 'scale': .46},
    },
    'brann': {
        'south': {'anchor': [132, 228], 'scale': .49, 'row_y': [-4, 0, 0, 0]},
        'east': {'anchor': [138, 247], 'scale': .46, 'row_x': [-3, 0, 0, 0], 'row_y': [0, 0, 0, 3]},
        'north': {'anchor': [132, 230], 'scale': .49, 'row_y': [-4, 0, 0, 2]},
        'west': {'mirror': 'east'},
    },
}
# Coordinates measured on final native release cels; all gameplay remains on
# the foot plane. The visual projectile uses the hand-to-pivot projection.
HANDS = {
    'lyra': {'south': [99, 72], 'east': [95, 58], 'north': [94, 57], 'west': [34, 58]},
    'brann': {'south': [101, 72], 'east': [96, 52], 'north': [96, 40], 'west': [32, 52]},
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def shifted(im, x, y):
    result = Image.new('RGBA', im.size)
    result.alpha_composite(im, (x, y))
    return result

def build_base(character, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for request in sorted((SOURCE/character).glob('*request.json')):
        recorded = json.loads(request.read_text())
        raw = SOURCE/character/Path(recorded['raw']).name
        assert sha(raw) == recorded['raw_sha256'], f'Raw paint changed: {raw}'
        assert sha(request.parent/recorded['prompt']) == recorded['prompt_sha256'], f'Prompt changed: {request}'
        for reference in recorded['inputs']:
            path = ROOT/reference['project_path']
            assert sha(path) == reference['sha256'], f'Reference changed: {path}'
    frames, lineage, animations = [], [], {}
    for direction in DIRECTIONS:
        settings = SETTINGS[character][direction]
        source_direction = settings.get('mirror', direction)
        source = SOURCE / character / f'{source_direction}-raw.png'
        raw = Image.open(source).convert('RGBA')
        sheet = raw.resize((2048, 1024), Image.Resampling.NEAREST)
        if source_direction != direction:
            bank = [shifted(ImageOps.mirror(f), 1, 0) for f in frames[28:56]]
        else:
            bank = []
            for i in range(28):
                x, y = i % 8 * 256, i // 8 * 256
                cell = sheet.crop((x, y, x+256, y+256))
                sx, sy = settings['anchor']
                scale = settings['scale']
                cel = cell.transform((128, 128), Image.Transform.AFFINE,
                    (1/scale, 0, sx-64/scale, 0, 1/scale, sy-112/scale), Image.Resampling.NEAREST)
                pixels = np.array(cel)
                a = pixels[:, :, 3]
                a[a < 24] = 0
                a[a > 245] = 255
                pixels[a == 0] = 0
                cel = Image.fromarray(pixels)
                row = i // 8
                cel = shifted(cel, settings.get('row_x', [0]*4)[row], settings.get('row_y', [0]*4)[row])
                bank.append(cel)
        first = len(frames)
        for i, cel in enumerate(bank):
            assert cel.getbbox(), (character, direction, i)
            # No part crosses the fixed native canvas. Do not silently crop limbs.
            bbox = cel.getchannel('A').point(lambda a: 255 if a > 64 else 0).getbbox()
            assert bbox[0] > 0 and bbox[1] > 0 and bbox[2] < 128 and bbox[3] < 128, (character, direction, i, bbox)
            frames.append(cel)
            lineage.append({'frame': first+i, 'source': str(source.relative_to(ROOT)),
                'source_sha256': sha(source), 'source_cell': i, 'raw_size': list(raw.size),
                'whole_sheet_nearest_size': [2048, 1024], 'transform': settings,
                'mirror_offset_x': 1 if source_direction != direction else 0,
                'rgba_sha256': hashlib.sha256(cel.tobytes()).hexdigest()})
        for action, (indices, holds, loop) in ACTIONS.items():
            animations[f'{direction}_{action}'] = {'frames': [first+i for i in indices], 'holds': holds, 'loop': loop}
    # Focused ImageGen leg paint, with exact protected existing upper bodies.
    # The request target used phases2/6; the compositor deliberately rebases
    # only compatible leg paint onto phases3/7 at the half-cycle boundaries.
    passing_source = SOURCE / character / 'passing-raw.png'
    passing = Image.open(passing_source).convert('RGBA').resize((256, 256), Image.Resampling.NEAREST)
    selected = [(0, True), (0, False), (2, False), (2, True)] if character == 'lyra' else [(1, False), (0, False), (3, False), (2, False)]
    for n, (view, base_index) in enumerate([('south', 3), ('south', 7), ('north', 59), ('north', 63)]):
        source_index, mirror = selected[n]
        donor = passing.crop((source_index%2*128, source_index//2*128, source_index%2*128+128, source_index//2*128+128))
        if mirror:
            donor = shifted(ImageOps.mirror(donor), 1, 0)
        base = np.array(frames[base_index])
        paint = np.array(donor)
        mask = np.zeros((128, 128), bool)
        mask[83:123, 42:91] = True
        composed = base.copy()
        composed[mask] = paint[mask]
        composed[mask & (composed[:, :, 3] < 24)] = 0
        assert np.array_equal(base[~mask], composed[~mask]), 'protected body differs'
        frames.append(Image.fromarray(composed))
        lineage.append({'frame': len(frames)-1, 'source': str(passing_source.relative_to(ROOT)),
            'source_sha256': sha(passing_source), 'source_cell': source_index,
            'whole_sheet_nearest_size': [256, 256], 'mirror_x': mirror,
            'mirror_offset_x': 1 if mirror else 0, 'protected_body_frame': base_index,
            'protected_body_rgba_sha256': hashlib.sha256(base.tobytes()).hexdigest(),
            'allowed_roi': [42, 83, 91, 123], 'outside_roi_changed_pixels': 0,
            'rgba_sha256': hashlib.sha256(composed.tobytes()).hexdigest()})
    animations['south_walk']['frames'] = [0, 1, 2, 112, 4, 5, 6, 113] if character == 'lyra' else [0, 1, 2, 112, 5, 6, 7, 113]
    animations['north_walk']['frames'] = [56, 57, 58, 114, 61, 62, 63, 115] if character == 'lyra' else [56, 56, 58, 114, 61, 62, 63, 115]
    for view in DIRECTIONS:
        source = ROOT/'art-source/attack-settle-v1/selected-candidate'/character/f'{view}.png'
        cel = Image.open(source).convert('RGBA')
        assert cel.size == (128, 128)
        index = len(frames)
        frames.append(cel)
        lineage.append({'frame': index, 'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
            'source_cell': 0, 'operation': 'generated settle with existing same-view idle-head ownership',
            'replay': 'art-source/attack-settle-v1/register_settles.py',
            'rgba_sha256': hashlib.sha256(cel.tobytes()).hexdigest()})
        attack = animations[f'{view}_attack']
        attack['frames'] += [index, animations[f'{view}_idle']['frames'][0]]
        attack['holds'] = attack['holds'][:5] + [.035, .035, .035]
        dodge = animations[f'{view}_dodge']
        dodge['frames'] = dodge['frames'][:3] + [index, dodge['frames'][-1]]
        dodge['holds'] = [.045, .105, .055, .0275, .0275]
    atlas = Image.new('RGBA', (1024, 128*((len(frames)+7)//8)))
    for i, cel in enumerate(frames):
        atlas.alpha_composite(cel, (i % 8 * 128, i // 8 * 128))
    if character == 'brann':
        repair_dir = ROOT / 'art-source/tab-repair-v1'
        spec = importlib.util.spec_from_file_location('emberwake_tab_repair', repair_dir/'repair_tabs.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        atlas, tab_receipt = module.apply_tab_repairs(atlas, json.loads((repair_dir/'repair-plan.json').read_text()))
        (destination/'TAB-REPAIR-RECEIPT.json').write_text(json.dumps(tab_receipt, indent=2)+'\n')
        for item in tab_receipt['journal']:
            index = item['frame']
            lineage[index]['post_edit'] = {'plan': 'art-source/tab-repair-v1/repair-plan.json', 'plan_sha256': sha(repair_dir/'repair-plan.json'), 'donor': item['donor'], 'offset': item['offset'], 'outside_mask_unchanged': True}
            frames[index] = atlas.crop((index%8*128, index//8*128, index%8*128+128, index//8*128+128))
            lineage[index]['rgba_sha256'] = hashlib.sha256(frames[index].tobytes()).hexdigest()
        dodge_dir = ROOT/'art-source/tab-repair-v2'
        spec = importlib.util.spec_from_file_location('emberwake_dodge_tab_repair', dodge_dir/'repair_dodge_tabs.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        atlas, dodge_receipt = module.apply_dodge_repairs(atlas, json.loads((dodge_dir/'repair-plan.json').read_text()))
        (destination/'DODGE-TAB-REPAIR-RECEIPT.json').write_text(json.dumps(dodge_receipt, indent=2)+'\n')
        for item in dodge_receipt['journal']:
            index = item['frame']
            lineage[index]['post_edit'] = {'plan': 'art-source/tab-repair-v2/repair-plan.json', 'plan_sha256': sha(dodge_dir/'repair-plan.json'), 'donor': item['donor'], 'offset': item['offset'], 'outside_mask_unchanged': True}
            frames[index] = atlas.crop((index%8*128, index//8*128, index%8*128+128, index//8*128+128))
            lineage[index]['rgba_sha256'] = hashlib.sha256(frames[index].tobytes()).hexdigest()
    atlas.save(destination / 'atlas.png')
    manifest = {'schema': 'emberwake-animation/v1', 'character_id': character,
        'cell': [128, 128], 'columns': 8, 'pivot': [64, 112], 'draw_scale': .66,
        'cast_hand': HANDS[character], 'cast_release_index': 3,
        'animations': animations, 'lineage': lineage,
        'limitations': ['Brann west bank mirrors east, with +1 native x translation; symmetric unarmed design.' if character == 'brann' else 'Four separately painted cardinal banks; no diagonal artwork.',
            'No jump, modular weapon or separate collapse artwork; body/effect clocks are independent.']}
    (destination / 'animations.json').write_text(json.dumps(manifest, indent=2)+'\n')
    portrait = frames[14]
    portrait.save(destination / 'portrait.png')
    proof = Image.new('RGBA', (1024, 24*144), '#173033')
    draw = ImageDraw.Draw(proof)
    for row, (name, clip) in enumerate(animations.items()):
        draw.text((5, row*144+1), name, fill='#ddc696')
        for n, index in enumerate(clip['frames']):
            proof.alpha_composite(frames[index], (n*128, row*144+15))
    proof.save(destination / 'selected-contact-sheet.png')
    receipt = {'character': character, 'stored_nonempty_cells': len(frames),
        'clips': len(animations), 'source_files': {str(p.relative_to(ROOT)): sha(p) for p in sorted((SOURCE/character).glob('*-raw.png'))},
        'selected_bank_sha256': sha(destination/'atlas.png'), 'manifest_sha256': sha(destination/'animations.json'),
        'rejected': (['brann/west-raw.png: nonuniform rows cross cell boundaries; not selected.'] if character == 'brann' else []) + [f'{character}/walk-south-north-raw.png: extended-contact repetition remains; full-walk redraw not selected.'],
        'art_quality': 'Needs independent temporal and runtime review; hash checks are not a rating.'}
    (destination/'BAKE-RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(character, len(frames), 'cells;', len(animations), 'clips;', sha(destination/'atlas.png'))

def apply_selected_refinements(atlas, manifest, character):
    selection = json.loads((SOURCE/'selected-refinements.json').read_text())
    records = []
    images = []
    next_index = max(entry['frame'] for entry in manifest['lineage'])+1
    for item in selection['characters'][character]:
        for dependency in item.get('proof_inputs', []):
            assert sha(ROOT/dependency['path']) == dependency['sha256'], 'Refinement replay/proof changed'
        old = item['source_frame']
        current = atlas.crop((old%8*128, old//8*128, old%8*128+128, old//8*128+128))
        assert hashlib.sha256(current.tobytes()).hexdigest() == item['source_rgba_sha256'], 'Refinement source changed; rebase required'
        candidate_path = ROOT/item['candidate']
        assert sha(candidate_path) == item['candidate_sha256'], 'Selected refinement paint changed'
        cel = Image.open(candidate_path).convert('RGBA')
        assert cel.size == (128,128)
        index = next_index+len(images)
        images.append(cel)
        for clip_name in item['clips']:
            clip = manifest['animations'][clip_name]
            assert old in clip['frames'], f'Refinement no longer applies: {clip_name}/{old}'
            clip['frames'] = [index if frame == old else frame for frame in clip['frames']]
        entry = {'frame':index, 'source':item['candidate'], 'source_sha256':item['candidate_sha256'],
            'source_cell':0, 'rgba_sha256':hashlib.sha256(cel.tobytes()).hexdigest(),
            'refinement':{key:value for key,value in item.items() if key not in ['candidate','candidate_sha256']}}
        manifest['lineage'].append(entry)
        records.append(entry)
    result = Image.new('RGBA', (1024, 128*((next_index+len(images)+7)//8)))
    result.paste(atlas,(0,0))
    for offset,cel in enumerate(images):
        index=next_index+offset
        result.paste(cel,(index%8*128,index//8*128))
    assert np.array_equal(np.array(result)[:atlas.height], np.array(atlas)), 'Existing cels changed'
    return result, records

def build_refined(character, destination, use_selected=True):
    """Reapply frozen source maps; make receipts independent of scratch paths."""
    package = ROOT/'art-source/gait-bridge-v1'
    spec = importlib.util.spec_from_file_location('emberwake_gait_bridge', package/'apply_bridges.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='emberwake-character-bake-') as scratch:
        scratch = Path(scratch)
        base, refined = scratch/'base', scratch/'gait'
        build_base(character, base)
        # This retained intermediate is an inspectable source authority, not
        # the temporary path used by the frozen map applicator.
        authority = SOURCE/'bake-v4'/character
        for name in ('atlas.png', 'animations.json'):
            assert sha(base/name) == sha(authority/name), f'Base authority changed: {character}/{name}'
        receipt = module.apply(base/'atlas.png', base/'animations.json', character, refined, 'b')
        manifest = json.loads((refined/'animations.json').read_text())
        for entry in manifest['lineage']:
            bridge = entry.get('experimental_source_pixel_bridge')
            if bridge:
                entry['source'] = str((authority/'atlas.png').relative_to(ROOT))
                bridge['package'] = str(package.relative_to(ROOT))
        gait_manifest_sha = hashlib.sha256((json.dumps(manifest,indent=2)+'\n').encode()).hexdigest()
        final_atlas = Image.open(refined/'atlas.png').convert('RGBA')
        selected_records = []
        if use_selected:
            final_atlas, selected_records = apply_selected_refinements(final_atlas,manifest,character)
        destination.mkdir(parents=True, exist_ok=False)
        final_atlas.save(destination/'atlas.png')
        (destination/'animations.json').write_text(json.dumps(manifest, indent=2)+'\n')
        for name in ('portrait.png', 'TAB-REPAIR-RECEIPT.json', 'DODGE-TAB-REPAIR-RECEIPT.json'):
            if (base/name).exists():
                shutil.copyfile(base/name, destination/name)
        receipt['records'] = [entry for entry in manifest['lineage'] if 'experimental_source_pixel_bridge' in entry]
        receipt['output_manifest_sha256'] = gait_manifest_sha
        receipt['normalized_gait_manifest_sha256'] = gait_manifest_sha
        receipt['final_manifest_sha256'] = sha(destination/'animations.json')
        receipt['final_atlas_sha256'] = sha(destination/'atlas.png')
        receipt['selected_followup_records'] = selected_records
        receipt['path_normalization'] = 'Frozen helper scratch source/package fields rebound to hash-identical retained project-relative authorities.'
        (destination/'GAIT-REPAIR-RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
        atlas = Image.open(destination/'atlas.png').convert('RGBA')
        proof = Image.new('RGBA', (1024, 24*144), '#173033')
        draw = ImageDraw.Draw(proof)
        for row, (name, clip) in enumerate(manifest['animations'].items()):
            draw.text((5, row*144+1), name, fill='#ddc696')
            for n, index in enumerate(clip['frames']):
                cel = atlas.crop((index%8*128, index//8*128, index%8*128+128, index//8*128+128))
                proof.alpha_composite(cel, (n*128, row*144+15))
        proof.save(destination/'selected-contact-sheet.png')
        bake = json.loads((base/'BAKE-RECEIPT.json').read_text())
        bake.update({'stored_nonempty_cells':len(manifest['lineage']),
            'selected_bank_sha256':sha(destination/'atlas.png'),
            'manifest_sha256':sha(destination/'animations.json'),
            'refinement':'Frozen variant B source-pixel gait maps; final visual review remains separately scoped.'})
        (destination/'BAKE-RECEIPT.json').write_text(json.dumps(bake, indent=2)+'\n')
        print(character, 'refined;', sha(destination/'atlas.png'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='Fresh destination parent, never existing approved assets.')
    parser.add_argument('--stage', choices=['base', 'gait', 'refined'], default='refined', help='Base reproduces frozen v4; gait adds frozen B maps; refined applies selected follow-up paint.')
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Output must not exist: '+str(args.output))
    for character in SETTINGS:
        if args.stage == 'base':
            build_base(character, args.output/character)
        else:
            build_refined(character, args.output/character, use_selected=args.stage=='refined')

if __name__ == '__main__':
    main()
