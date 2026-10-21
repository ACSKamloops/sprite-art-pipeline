#!/usr/bin/env python3
"""Two source-colored articulated bridge probes; preserves eight frozen keys.

This source-bound experiment is deliberately limited to two intervals. Rigid
distal pieces plus short projected trouser warps do not recover hidden anatomy.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import History, canonical_json, candidate_transaction, export_aseprite, project_hash
from sprite_lab.core import render_frames


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


warp = module('bridge_warp', REPO / 'skills/sprite-construction-editing/scripts/warp_part.py')
constructor = module('bridge_constructor', TOOLKIT / 'scripts/sprite_construct.py')
delivery = module('bridge_delivery', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
apng = module('bridge_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + '\n')


def export(project, folder, name):
    folder.mkdir()
    source = folder / 'editable-project.json'
    source.write_text(canonical_json(project) + '\n')
    delivery.export(source, folder / 'delivery', 'walk', TOOLKIT, actor=name)
    apng.convert(folder / 'delivery/manifest.json', folder / 'delivery/apng')
    export_aseprite(project, folder / 'hero.aseprite', 'walk')


def run(args):
    src, out = args.source.resolve(), args.output.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError('Fresh output required')
    recipe = json.loads(args.recipe.read_text())
    if recipe.get('schema') != 'source-lowerbody-bridge-recipe/v1' or [b['after_key'] for b in recipe['bridges']] != [2,3]:
        raise ValueError('This bounded probe requires exactly the 2->3 and 3->4 bridges')
    if sha(src / 'project.json') != recipe['project_sha256']:
        raise ValueError('Frozen ImageGen source project changed')
    source = json.loads((src / 'project.json').read_text())
    original = render_frames(source, source['animations'][0]['frames'])
    assert len(original) == 8 and all(i.size == (80,80) for i in original)
    assert source['animations'][0]['fps'] == 8 and all(f['duration_ticks'] == 1 for f in source['frames'])
    source_hashes = {f'frames/{i:04d}.png': sha(src / f'frames/{i:04d}.png') for i in range(8)}
    assert all(Image.open(src / f'frames/{i:04d}.png').convert('RGBA').tobytes() == image.tobytes() for i, image in enumerate(original))
    out.mkdir(parents=True)
    shutil.copy2(__file__, out / 'runner.py')
    shutil.copy2(args.recipe, out / 'recipe.json')
    assets = out / 'assets'
    assets.mkdir()
    for i, image in enumerate(original):
        image.save(assets / f'key-{i}.png')
    donor = original[3]
    donor.save(assets / 'donor-key3.png')
    donor_array = np.array(donor)
    masks = {k: np.zeros((80,80), dtype=bool) for k in ['far-trouser','far-distal','near-trouser','near-distal']}
    lower = np.zeros((80,80), dtype=bool)
    lower[recipe['lower_start_y']:, :] = True
    for y,x in np.argwhere(lower & (donor_array[:,:,3] > 0)):
        split = recipe['near_start_x_by_y'].get(str(y), 41)
        side = 'near' if x >= split else 'far'
        distal = y >= recipe['distal_start_y'][side]
        masks[side + ('-distal' if distal else '-trouser')][y,x] = True
    assert np.array_equal(sum(m.astype(int) for m in masks.values()), (lower & (donor_array[:,:,3]>0)).astype(int))
    owner_view = np.zeros((80,80,4), dtype=np.uint8)
    colors = [(80,180,240,255),(40,80,210,255),(240,180,80,255),(210,80,40,255)]
    for (part, mask), color in zip(masks.items(), colors):
        Image.fromarray(mask.astype(np.uint8)*255).save(assets / f'owner-{part}.png')
        owner_view[mask] = color
    Image.fromarray(owner_view).save(out / 'source-ownership.png')
    # Explicit empty underpaint: no invented concealed limb/body pixels.
    Image.new('RGBA',(80,80)).save(assets / 'underpaint-empty.png')
    write(out / 'UNDERPAINT.json', {'policy':'No hidden paint. Base is held source key above y54 and transparent below. All lower coverage comes from visible key3 owned pixels; gaps stay visible until an explicit source-colored seam transaction.',
                                  'layer_order':['held-upper','far-trouser','far-distal','near-trouser','near-distal'],
                                  'limb_names':'Screen-relative projected ownership in key3; no recovered skeleton or compulsory symmetric limb claim.'})
    layers = [{'id':'key','name':'Frozen source keys','locked':True},
              {'id':'held-upper','name':'Unmodified held head torso arms scarf','locked':True}]
    layers += [{'id':p,'name':p + ' visible source-owned paint','locked':False} for p in masks]
    initial_frames, final_images, warp_records = [], {}, []
    for bridge in recipe['bridges']:
        name, base = bridge['id'], bridge['after_key']
        upper = original[base].copy()
        upper.paste((0,0,0,0),(0,recipe['lower_start_y'],80,80))
        upper.save(assets / f'{name}-upper.png')
        bridge_cels = {'held-upper':{'image':f'{name}-upper.png'}}
        composition = np.array(upper)
        source_map = np.full((80,80,3),-1,dtype=np.int64)
        for y,x in np.argwhere(np.array(upper)[:,:,3]>0):
            source_map[y,x] = [base,x,y]
        for part in masks:
            folder = out / f'{name}-{part}'
            request = {'schema':'nearest-part-warp/v1','canvas':[80,80],
                       'donor':{'path':str(assets/'donor-key3.png'),'sha256':sha(assets/'donor-key3.png')},
                       'owner_mask':{'path':str(assets/f'owner-{part}.png'),'sha256':sha(assets/f'owner-{part}.png')},
                       'source_vertices':recipe['source_vertices'][part],
                       'target_vertices':bridge['target_vertices'][part],
                       'triangles':[[0,1,2],[0,2,3]],'alpha_mode':'nonzero-only'}
            request_path = out / f'{name}-{part}-request.json'
            write(request_path,request)
            warp.run(request_path,folder)
            layer = np.array(Image.open(folder/'layer.png'))
            owned = layer[:,:,3]>0
            assert not owned[:recipe['lower_start_y']].any()
            xy = np.load(folder/'source-xy.npy',allow_pickle=False)
            assert all(np.array_equal(layer[y,x],donor_array[xy[y,x,1],xy[y,x,0]]) for y,x in np.argwhere(owned))
            if part.endswith('distal'):
                # Distal target quads must be one exact integer translation.
                delta = np.array(request['target_vertices']) - np.array(request['source_vertices'])
                assert (delta == delta[0]).all() and np.equal(delta,np.floor(delta)).all()
                assert int(owned.sum()) == int(masks[part].sum())
            composition[owned] = layer[owned]
            for y,x in np.argwhere(owned):
                source_map[y,x] = [3,int(xy[y,x,0]),int(xy[y,x,1])]
            Image.new('RGBA',(80,80)).save(assets / f'{name}-{part}-initial.png')
            bridge_cels[part] = {'image':f'{name}-{part}-initial.png'}
            warp_records.append({'bridge':name,'part':part,'directory':str(folder.relative_to(out)),
                                 'rigid_distal':part.endswith('distal'),'source_rgba_exact':True,'owned_pixels':int(owned.sum())})
        image = Image.fromarray(composition)
        assert image.crop((0,0,80,recipe['lower_start_y'])).tobytes() == original[base].crop((0,0,80,recipe['lower_start_y'])).tobytes()
        image.save(out / f'{name}.png')
        np.save(out/f'{name}-source-frame-xy.npy',source_map,allow_pickle=False)
        assert all(tuple(composition[y,x]) == original[f].getpixel((sx,sy)) for y,x in np.argwhere(composition[:,:,3]>0) for f,sx,sy in [source_map[y,x]])
        final_images[name] = image
        initial_frames.append({'id':name,'duration_ticks':1,'landmarks':bridge['projected_controls'],'cels':bridge_cels})
    frames = [{'id':f'key-{i}','duration_ticks':1 if i in [b['after_key'] for b in recipe['bridges']] else 2,
               'landmarks':{},'cels':{'key':{'image':f'key-{i}.png'}}} for i in range(8)] + initial_frames
    ordered = []
    for i in range(8):
        ordered.append(f'key-{i}')
        ordered += [b['id'] for b in recipe['bridges'] if b['after_key']==i]
    spec = {'schema':'sprite-construction-spec/v1','canvas':source['canvas'],'layers':layers,'frames':frames,
            'animations':[{'id':'walk','frames':ordered,'fps':16,'loop':True,'events':[]}],
            'provenance':{'source_project_sha256':sha(src/'project.json'),'recipe_sha256':sha(args.recipe),
                          'clock':'Eight keys keep original onset times; only holds after keys2/3 subdivide 1/8 into two 1/16 slots. Total16ticks/16Hz=1second.',
                          'boundary':'Two new visible-paint bridge cels. No recovered hidden anatomy, blend, optical flow, generation or per-pose fit.'}}
    write(assets/'spec.json',spec)
    initial = constructor.construct(assets/'spec.json')
    history = History(initial)
    for row in warp_records:
        bridge, part = row['bridge'], row['part']
        frame = next(f for f in history.project['frames'] if f['id']==bridge)
        cel = frame['cels'][part]
        image = Image.open(out/row['directory']/'layer.png').convert('RGBA')
        mask = [[int(x),int(y)] for y,x in np.argwhere(np.array(image)[:,:,3]>0)]
        tx = candidate_transaction(history.project,cel,image,mask)
        tx['reason'] = 'Import source-owned nearest part with frozen sourceXY witness; complete distal parts translate rigidly'
        history.apply(tx)
    (out/'initial-project.json').write_text(canonical_json(initial)+'\n')
    write(out/'journal.json',history.journal())
    replay = History.replay(initial,history.journal())
    assert project_hash(replay.project)==project_hash(history.project)
    onset, actual_onsets = Fraction(0), {}
    by_id = {f['id']:f for f in history.project['frames']}
    for frame_id in ordered:
        actual_onsets[frame_id] = [onset.numerator,onset.denominator]
        onset += Fraction(by_id[frame_id]['duration_ticks'],16)
    assert onset == 1
    assert all(Fraction(*actual_onsets[f'key-{i}'])==Fraction(i,8) for i in range(8))
    assert Fraction(*actual_onsets['bridge-2-3'])==Fraction(5,16)
    assert Fraction(*actual_onsets['bridge-3-4'])==Fraction(7,16)
    exported = render_frames(history.project,ordered)
    assert all(exported[ordered.index(f'key-{i}')].tobytes()==original[i].tobytes() for i in range(8))
    assert all(exported[ordered.index(k)].tobytes()==v.tobytes() for k,v in final_images.items())
    export(history.project,out/'candidate-two-bridges','candidate-two-bridges')
    export(source,out/'original-eight-keys','original-eight-keys')
    control = copy.deepcopy(source)
    for f in control['frames']:
        f['duration_ticks'] = 1 if int(f['id'][-2:]) in [2,3] else 2
    control_order = []
    for i in range(8):
        key = f'pose-{i:02d}'
        control_order += [key,key] if i in [2,3] else [key]
    control['animations'][0]['frames']=control_order
    control['animations'][0]['fps']=16
    export(control,out/'timing-only-control','timing-only-control')
    # Full chronology and every adjacency, including wrap.
    for label,images in [('candidate',exported),('original',original)]:
        for kind in ['ordered','pairs']:
            count = len(images)
            panel=Image.new('RGB',(count*160*(2 if kind=='pairs' else 1),182),(49,57,77))
            d=ImageDraw.Draw(panel)
            for i,image in enumerate(images):
                chosen = [images[(i-1)%count],image] if kind=='pairs' else [image]
                d.text((i*160*len(chosen)+3,2),f'{(i-1)%count}->{i}' if kind=='pairs' else str(i),fill='white')
                for p,im in enumerate(chosen):
                    bg=Image.new('RGBA',(160,160),(49,57,77,255));bg.alpha_composite(im.resize((160,160),Image.Resampling.NEAREST));panel.paste(bg,(i*160*len(chosen)+p*160,20))
            panel.save(out/f'{label}-{kind}-2x.png')
    assert all(sha(src/name)==value for name,value in source_hashes.items())
    assert sha(src/'project.json') == recipe['project_sha256']
    write(out/'RESULTS.json',{'schema':'source-lowerbody-bridge-probe/v1','source_project_sha256':sha(src/'project.json'),
                             'all_eight_keys_rgba_unchanged':True,'upper_head_torso_arms_scarf_unchanged_from_held_key':True,
                             'canvas':[80,80],'period':[1,1],'new_bridge_count':2,'total_cels':10,
                             'key_onsets_seconds':[[i,8] for i in range(8)],'bridge_onsets_seconds':[[5,16],[7,16]],
                             'actual_reduced_rational_onsets':actual_onsets,
                             'rigid_distal_pieces_preserve_owned_pixel_counts':True,'all_composite_visible_pixels_have_exact_source_witness':True,
                             'warp_parts':warp_records,'journal_replay_exact':True,'source_immutable':True,
                             'art_acceptance':'pending','full_16_frame_bank':'not built; decision requires actual motion review',
                             'runner_sha256':sha(__file__),'recipe_sha256':sha(args.recipe)})
    shutil.copy2(Path(__file__).with_name('review-bridge-probe.html'),out/'index.html')
    write(out/'SHA256.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--recipe',required=True,type=Path)
    run(parser.parse_args())
