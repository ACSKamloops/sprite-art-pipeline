#!/usr/bin/env python3
"""Move one exact source-owned head in one bridge; record guarded neck paint."""
import argparse
import copy
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
sys.path.insert(0,str(TOOLKIT))
from sprite_lab import History, canonical_json, candidate_transaction, export_aseprite, project_hash, render_cel
from sprite_lab.core import render_frames


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


delivery=module('head_delivery',REPO/'skills/sprite-animation-pipeline/scripts/project_delivery.py')
apng=module('head_apng',REPO/'skills/sprite-animation-pipeline/scripts/exact_apng.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n')


def export(project,folder,name):
    folder.mkdir()
    path=folder/'editable-project.json'
    path.write_text(canonical_json(project)+'\n')
    delivery.export(path,folder/'delivery','walk',TOOLKIT,actor=name)
    apng.convert(folder/'delivery/manifest.json',folder/'delivery/apng')
    export_aseprite(project,folder/'hero.aseprite','walk')


def sheet(path,rows,scale=2,crop=None):
    width,height=(80,80) if crop is None else (crop[2]-crop[0],crop[3]-crop[1])
    count=len(rows[0][1])
    result=Image.new('RGB',(width*scale*count,(height*scale+22)*len(rows)),(49,57,77))
    draw=ImageDraw.Draw(result)
    for r,(label,images) in enumerate(rows):
        draw.text((4,r*(height*scale+22)+3),label,fill='white')
        for i,image in enumerate(images):
            if crop is not None:
                image=image.crop(crop)
            image=image.resize((width*scale,height*scale),Image.Resampling.NEAREST)
            result.paste(image,(i*width*scale,r*(height*scale+22)+20),image)
    result.save(path)


def run(args):
    out=args.output.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError('Fresh output required')
    recipe=json.loads(args.recipe.read_text())
    if recipe['schema']!='source-component-head-bridge/v1':
        raise ValueError('Unsupported recipe')
    if sha(args.candidate)!=recipe['candidate_project_sha256'] or sha(args.head_source)!=recipe['head_source_project_sha256']:
        raise ValueError('Frozen input mismatch')
    baseline=json.loads(args.candidate.read_text())
    head_source=json.loads(args.head_source.read_text())
    order=baseline['animations'][0]['frames']
    before=render_frames(baseline,order)
    target_index=order.index(recipe['target_frame'])
    target=next(f for f in baseline['frames'] if f['id']==recipe['target_frame'])
    donor_frame=next(f for f in head_source['frames'] if f['id']==recipe['head_source_frame'])
    owner_image=render_cel(head_source,donor_frame['cels'][recipe['head_source_layer']])
    owner=np.array(owner_image)
    owned=owner[:,:,3]>0
    assert np.array_equal(np.array(before[target_index])[owned],owner[owned])
    dx=recipe['target_anchor'][0]-recipe['source_anchor'][0]
    dy=recipe['target_anchor'][1]-recipe['source_anchor'][1]
    translated=np.zeros_like(owner)
    head_xy=np.full((80,80,2),-1,dtype=np.int64)
    for y,x in np.argwhere(owned):
        xx,yy=int(x+dx),int(y+dy)
        assert 0<=xx<80 and 0<=yy<80
        translated[yy,xx]=owner[y,x]
        head_xy[yy,xx]=[x,y]
    moved=translated[:,:,3]>0
    assert int(moved.sum())==int(owned.sum())
    out.mkdir(parents=True)
    shutil.copy2(__file__,out/'runner.py')
    shutil.copy2(args.recipe,out/'recipe.json')
    (out/'immutable-baseline').mkdir()
    shutil.copy2(args.candidate,out/'immutable-baseline/lower-bridge-project.json')
    shutil.copy2(args.head_source,out/'immutable-baseline/head-source-project.json')
    owner_image.save(out/'source-head-owned.png')
    Image.fromarray(owned.astype(np.uint8)*255).save(out/'source-head-mask.png')
    Image.fromarray(moved.astype(np.uint8)*255).save(out/'translated-head-mask.png')
    Image.fromarray(translated).save(out/'translated-head.png')
    np.save(out/'head-source-xy.npy',head_xy,allow_pickle=False)
    initial=copy.deepcopy(baseline)
    frame=next(f for f in initial['frames'] if f['id']==recipe['target_frame'])
    old_cel=frame['cels'].pop('held-upper')
    new_cel='head-bridge-upper-owned-edit'
    initial['layers'].insert(2,{'id':'head-bridge-upper','name':'Only original head ownership may be erased; other upper pixels receipt-protected','locked':False})
    initial['cels'][new_cel]={'layer_id':'head-bridge-upper','pixels':list(initial['cels'][old_cel]['pixels'])}
    frame['cels']['head-bridge-upper']=new_cel
    for layer in ['head-neck-cap','head-component']:
        initial['layers'].append({'id':layer,'name':layer+' only at phase2.5','locked':False})
        initial['cels'][layer]={'layer_id':layer,'pixels':[0]*6400}
        frame['cels'][layer]=layer
    initial['provenance']['head_bridge']={'source_project_sha256':sha(args.head_source),'source_frame':recipe['head_source_frame'],
                                         'source_layer':recipe['head_source_layer'],'source_anchor':recipe['source_anchor'],
                                         'target_anchor':recipe['target_anchor'],'recipe_sha256':sha(args.recipe),
                                         'scope':'Single component at phase2.5; all original keys/lower-body cels/clocks retained. Added source-colored neck cap is authored join paint.'}
    assert all(a.tobytes()==b.tobytes() for a,b in zip(before,render_frames(initial,order)))
    history=History(initial)
    points=[[int(x),int(y)] for y,x in np.argwhere(owned)]
    history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),
                   'reason':'Erase exactly the original head owner from held upper; no torso/glove/scarf or lower-body pixels',
                   'operations':[{'op':'erase','cel_id':new_cel,'points':points,'mask':points}]})
    cut_upper=np.array(render_cel(history.project,new_cel))
    assert not ((cut_upper[:,:,3]>0)&moved).any()
    tx=candidate_transaction(history.project,'head-component',Image.fromarray(translated),[[int(x),int(y)] for y,x in np.argwhere(moved)])
    tx['reason']='Translate complete exact source-owned key2 head by explicit delta; no averaging/resizing/recentering'
    history.apply(tx)
    raw=copy.deepcopy(history.project)
    write(out/'raw-journal.json',history.journal())
    neck=np.zeros_like(owner)
    neck_witness=[]
    for point in recipe['neck_cap_samples']:
        x,y,sx,sy=point
        assert owned[y,x] and not moved[y,x] and cut_upper[y,x,3]==0
        assert owner[sy,sx,3]==255
        neck[y,x]=owner[sy,sx]
        neck_witness.append({'destination':[x,y],'source_owner_xy':[sx,sy],'rgba':list(map(int,owner[sy,sx]))})
    neck_mask=neck[:,:,3]>0
    assert int(neck_mask.sum())==9
    Image.fromarray(neck).save(out/'neck-cap-source-colored.png')
    Image.fromarray(neck_mask.astype(np.uint8)*255).save(out/'neck-cap-mask.png')
    tx=candidate_transaction(history.project,'head-neck-cap',Image.fromarray(neck),[[int(x),int(y)] for y,x in np.argwhere(neck_mask)])
    tx['reason']='Close observed one-row neck/collar gap with explicit source-owner bottom-row neck-cap samples; no inferred hidden paint'
    history.apply(tx)
    final=history.project
    (out/'initial-project.json').write_text(canonical_json(initial)+'\n')
    write(out/'journal.json',history.journal())
    replay=History.replay(initial,history.journal())
    assert project_hash(replay.project)==project_hash(final)
    for _ in range(history.cursor):
        replay.undo()
    assert project_hash(replay.project)==project_hash(initial)
    while replay.cursor<history.cursor:
        replay.redo()
    assert project_hash(replay.project)==project_hash(final)
    after=render_frames(final,order)
    allowed=owned|moved|neck_mask
    assert all(a.tobytes()==b.tobytes() for i,(a,b) in enumerate(zip(before,after)) if i!=target_index)
    a,b=np.array(before[target_index]),np.array(after[target_index])
    assert np.array_equal(a[~allowed],b[~allowed]) and np.array_equal(a[54:],b[54:])
    assert baseline['animations']==final['animations'] and baseline['canvas']==final['canvas']
    for layer in ['far-trouser','far-distal','near-trouser','near-distal']:
        assert {k:v for k,v in baseline['cels'].items() if v['layer_id']==layer}=={k:v for k,v in final['cels'].items() if v['layer_id']==layer}
    for name,project in [('baseline-lower-bridges',baseline),('raw-head-translation',raw),('head-neck-cap',final)]:
        export(project,out/name,name)
    raw_images=render_frames(raw,order)
    choices=[('Original head in lower bridges',before),('Raw translation: rejected collar gap',raw_images),('Translated head with9px neck cap',after)]
    for scale in [1,2,4]:
        sheet(out/f'affected-chronology-{scale}x.png',[(label,[images[2],images[3],images[4]]) for label,images in choices],scale)
    sheet(out/'collar-seam-8x.png',[(label,[images[2],images[3],images[4]]) for label,images in choices],8,(29,22,49,33))
    for label,images in [('baseline',before),('head-midpoint',after)]:
        pair_images=[im for i in range(len(images)) for im in [images[(i-1)%len(images)],images[i]]]
        sheet(out/f'{label}-all-pairs-2x.png',[(label+' pairs:9->0,0->1,...8->9',pair_images)],2)
    write(out/'MASKS-AND-WITNESSES.json',{'head_source_project_sha256':sha(args.head_source),
                                        'source_frame':recipe['head_source_frame'],'source_owner_cel':donor_frame['cels'][recipe['head_source_layer']],
                                        'head_owned_pixels':int(owned.sum()),'head_translation':[dx,dy],
                                        'original_head_erase_mask':points,'translated_head_mask':[[int(x),int(y)] for y,x in np.argwhere(moved)],
                                        'neck_cap_samples':neck_witness,'head_pixel_count_preserved':True,
                                        'translated_head_overlaps_known_body':False,'outside_union_rgba_unchanged':True})
    write(out/'RESULTS.json',{'schema':'source-component-head-bridge-results/v1','baseline_project_sha256':sha(args.candidate),
                            'head_source_project_sha256':sha(args.head_source),'target_frame':recipe['target_frame'],
                            'source_anchor':recipe['source_anchor'],'target_anchor':recipe['target_anchor'],
                            'all8original_keys_unchanged':True,'other9candidate_frames_unchanged':True,
                            'both_lower_body_bridges_and_all_lower_cels_unchanged':True,'clock_canvas_pivots_unchanged':True,
                            'journal_replay_undo_redo_exact':True,'raw_translation':'Rejected: nine-pixel one-row gap above scarf',
                            'neck_cap':'Nine source-colored bottom-row samples; authored visible join, not recovered hidden anatomy',
                            'final_project_canonical_sha256':project_hash(final),'art_acceptance':'pending root review',
                            'runner_sha256':sha(__file__),'recipe_sha256':sha(args.recipe)})
    assert sha(args.candidate)==recipe['candidate_project_sha256'] and sha(args.head_source)==recipe['head_source_project_sha256']
    write(out/'SHA256.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',required=True,type=Path)
    parser.add_argument('--head-source',required=True,type=Path)
    parser.add_argument('--recipe',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    run(parser.parse_args())
