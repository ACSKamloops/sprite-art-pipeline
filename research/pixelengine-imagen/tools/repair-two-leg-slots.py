#!/usr/bin/env python3
"""Source-bound two-slot leg repair: clearance, measured rotation, pixel clusters."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image

REPO=Path(__file__).resolve().parents[3]
TOOLKIT=REPO/'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0,str(TOOLKIT))
from sprite_lab import History,canonical_json,candidate_transaction,project_hash,render_cel
from sprite_lab.core import render_frames


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


helper=module('leg_repair_helpers',Path(__file__).with_name('probe-component-head-bridge.py'))
warp=module('leg_repair_warp',REPO/'skills/sprite-construction-editing/scripts/warp_part.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n')


def frame(project,name):
    return next(f for f in project['frames'] if f['id']==name)


def apply(history,ops,reason):
    history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),'reason':reason,'operations':ops})


def run(args):
    out=args.output.absolute()
    if out.exists() or out.is_symlink():raise ValueError('Fresh output required')
    recipe=json.loads(args.recipe.read_text())
    source_path=args.pilot/'candidate-two-bridges/editable-project.json'
    if sha(source_path)!=recipe['baseline_sha256'] or sha(args.rich_source)!=recipe['rich_source_sha256']:
        raise ValueError('Frozen source mismatch')
    baseline=json.loads(source_path.read_text());rich=json.loads(args.rich_source.read_text())
    original=render_frames(rich,rich['animations'][0]['frames'])
    order=baseline['animations'][0]['frames'];before=render_frames(baseline,order)
    out.mkdir(parents=True);shutil.copy2(__file__,out/'runner.py');shutil.copy2(args.recipe,out/'recipe.json')
    shutil.copy2(source_path,out/'baseline-project.json')
    maps={}
    for bridge in ['bridge-2-3','bridge-3-4']:
        maps[bridge]={p:np.load(args.pilot/f'{bridge}-{p}/source-xy.npy',allow_pickle=False).copy() for p in ['far-trouser','far-distal','near-trouser','near-distal']}
        for part in maps[bridge]:
            Image.fromarray(np.array(render_cel(baseline,frame(baseline,bridge)['cels'][part]))).save(out/f'{bridge}-{part}-baseline.png')
    history=History(baseline)
    # First interval: clearance before knee lift. Complete visible distal piece
    # remains rigid; the following literal trouser edit coordinates its cuff.
    bridge='bridge-2-3';part='near-distal';dx,dy=recipe['first_distal_translation']
    cid=frame(history.project,bridge)['cels'][part]
    apply(history,[{'op':'translate','cel_id':cid,'dx':dx,'dy':dy,'allow_clip':False}],
          'Give near boot lateral clearance from support toe; original source-owned distal volume retained')
    moved=np.full_like(maps[bridge][part],-1)
    for y,x in np.argwhere(maps[bridge][part][:,:,0]>=0):moved[y+dy,x+dx]=maps[bridge][part][y,x]
    maps[bridge][part]=moved
    # Second interval: derive the modest angle from explicit visible source-foot
    # silhouette probes. These are projected proxies, not recovered bone joints.
    rotation=recipe['second_distal_rotation'];angles=[]
    for proxy in rotation['visible_pose_proxies']:
        a,b=np.array(proxy['ankle']),np.array(proxy['toe'])
        assert original[proxy['source_key']].getpixel(tuple(a))[3]>0 and original[proxy['source_key']].getpixel(tuple(b))[3]>0
        assert int(b[0])==max(x for x in range(40,80) if original[proxy['source_key']].getpixel((x,int(b[1])))[3]>0)
        vector=b-a;angles.append(math.degrees(math.atan2(vector[1],vector[0])))
    midpoint_delta=(angles[1]-angles[0])/2
    assert abs(midpoint_delta-rotation['degrees'])<1
    source_vertices=np.array([[37,56],[53,56],[53,71],[37,71]],dtype=float)
    pivot=np.array(rotation['source_cuff_proxy'],dtype=float)
    target_pivot=pivot+np.array(rotation['target_translation'],dtype=float)
    angle=math.radians(rotation['degrees']);matrix=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    target_vertices=(source_vertices-pivot)@matrix.T+target_pivot
    request={'schema':'nearest-part-warp/v1','canvas':[80,80],
             'donor':{'path':str((args.pilot/'assets/donor-key3.png').resolve()),'sha256':sha(args.pilot/'assets/donor-key3.png')},
             'owner_mask':{'path':str((args.pilot/'assets/owner-near-distal.png').resolve()),'sha256':sha(args.pilot/'assets/owner-near-distal.png')},
             'source_vertices':source_vertices.tolist(),'target_vertices':target_vertices.tolist(),
             'triangles':[[0,1,2],[0,2,3]],'alpha_mode':'nonzero-only'}
    write(out/'second-distal-request.json',request);warp.run(out/'second-distal-request.json',out/'second-distal-rotation')
    bridge='bridge-3-4';part='near-distal';cid=frame(history.project,bridge)['cels'][part]
    layer=Image.open(out/'second-distal-rotation/layer.png').convert('RGBA');old=np.array(render_cel(history.project,cid));new=np.array(layer)
    mask=[[int(x),int(y)] for y,x in np.argwhere((old[:,:,3]>0)|(new[:,:,3]>0))]
    tx=candidate_transaction(history.project,cid,layer,mask);tx['reason']='Rotate complete visible cuff/shin/boot by measured projected half-angle; no whole body flow or new paint'
    history.apply(tx);maps[bridge][part]=np.load(out/'second-distal-rotation/source-xy.npy',allow_pickle=False)
    articulated=copy.deepcopy(history.project)
    write(out/'articulated-controls-journal.json',history.journal())
    # Actual pencil/eraser cluster repair: a short articulated trouser section
    # connects the held hip to the advanced near cuff, with explicit material
    # samples. New covered pixels are authored visible paint, not hidden anatomy.
    manual=recipe['first_near_trouser_clusters'];bridge='bridge-2-3';part='near-trouser'
    cid=frame(history.project,bridge)['cels'][part];old=np.array(render_cel(history.project,cid))
    erase=[[int(x),int(y)] for y,x in np.argwhere(old[:,:,3]>0)]
    points=[];witness=[];part_map=np.full((80,80,2),-1,dtype=np.int64)
    palette=history.project['palette']
    for row in manual['rows']:
        for i,symbol in enumerate(row['pattern']):
            x,y=row['x']+i,row['y'];sx,sy=manual['source_color_samples'][symbol]
            color=original[3].getpixel((sx,sy));assert color[3]==255
            points.append([x,y,palette.index(list(color))]);part_map[y,x]=[sx,sy]
            witness.append({'destination':[x,y],'source_frame':3,'source_xy':[sx,sy],'rgba':list(color)})
    allowed=sorted({tuple(p) for p in erase}|{tuple(p[:2])for p in points},key=lambda p:(p[1],p[0]))
    allowed=[list(p)for p in allowed]
    apply(history,[{'op':'erase','cel_id':cid,'points':erase,'mask':allowed},
                   {'op':'paint','cel_id':cid,'points':points,'mask':allowed}],
          'Literal source-colored trouser clusters coordinate held hip and advanced cuff; preserve hanging glove and all upper paint')
    maps[bridge][part]=part_map
    Image.fromarray(np.array(render_cel(history.project,cid))).save(out/'first-near-trouser-manual.png')
    mask_image=np.zeros((80,80),dtype=np.uint8)
    for x,y in allowed:mask_image[y,x]=255
    Image.fromarray(mask_image).save(out/'first-near-trouser-edit-mask.png')
    write(out/'manual-cluster-witness.json',{'pixels':witness,'erase':erase,'allowed_mask':allowed,
                                          'underpaint':'Only the declared visible trouser cluster is authored; no concealed limb/body completion. Every new material sample comes from richer source key3.'})
    final=history.project
    (out/'initial-project.json').write_text(canonical_json(baseline)+'\n');write(out/'journal.json',history.journal())
    replay=History.replay(baseline,history.journal());assert project_hash(replay.project)==project_hash(final)
    after=render_frames(final,order);stage=render_frames(articulated,order)
    target_ids=['bridge-2-3','bridge-3-4']
    for i,(a,b) in enumerate(zip(before,after)):
        if order[i]not in target_ids:assert a.tobytes()==b.tobytes()
        else:
            aa,bb=np.array(a),np.array(b);assert np.array_equal(aa[:54],bb[:54])
    assert baseline['animations']==final['animations'] and baseline['canvas']==final['canvas']
    for i in range(8):assert after[order.index(f'key-{i}')].tobytes()==original[i].tobytes()
    # Composite frozen source-frame/XY maps from the actual per-layer owners.
    # Rebuild pixels from these maps independently; no inverse geometry rerun.
    for bridge,held_key in [('bridge-2-3',2),('bridge-3-4',3)]:
        image=np.zeros((80,80,4),dtype=np.uint8);source_map=np.full((80,80,3),-1,dtype=np.int64)
        current=frame(final,bridge)
        upper=np.array(render_cel(final,current['cels']['held-upper']));image[:]=upper
        for y,x in np.argwhere(upper[:,:,3]>0):source_map[y,x]=[held_key,x,y]
        for part in ['far-trouser','far-distal','near-trouser','near-distal']:
            pixels=np.array(render_cel(final,current['cels'][part]));owned=pixels[:,:,3]>0;xy=maps[bridge][part]
            assert all(np.array_equal(pixels[y,x],np.array(original[3])[xy[y,x,1],xy[y,x,0]]) for y,x in np.argwhere(owned))
            image[owned]=pixels[owned]
            for y,x in np.argwhere(owned):source_map[y,x]=[3,int(xy[y,x,0]),int(xy[y,x,1])]
            np.save(out/f'{bridge}-{part}-source-xy.npy',xy,allow_pickle=False)
        assert np.array_equal(image,np.array(after[order.index(bridge)]))
        np.save(out/f'{bridge}-source-frame-xy.npy',source_map,allow_pickle=False)
        Image.fromarray(image).save(out/f'{bridge}-repaired.png')
    for name,project in [('baseline',baseline),('articulated-controls',articulated),('cluster-repair',final)]:helper.export(project,out/name,name)
    choices=[('Frozen leg-only baseline',before),('Clearance plus measured distal rotation',stage),('Manual trouser cluster repair',after)]
    for scale in [1,2,4]:helper.sheet(out/f'affected-chronology-{scale}x.png',[(label,[images[i]for i in [2,3,4,5,6]])for label,images in choices],scale)
    helper.sheet(out/'lower-clusters-8x.png',[(label,[images[3],images[5]])for label,images in choices],8,(27,52,57,73))
    helper.sheet(out/'all-pairs-2x.png',[('Final pairs9->0,0->1,...8->9',[im for i in range(10)for im in[after[(i-1)%10],after[i]]])],2)
    rotated_xy=maps['bridge-3-4']['near-distal']
    rotated_owned=new[:,:,3]>0
    distinct_source=len(set(map(tuple,rotated_xy[rotated_owned].tolist())))
    counts={'second_distal_source_pixels':int(np.array(Image.open(args.pilot/'assets/owner-near-distal.png')).astype(bool).sum()),
            'second_distal_rotated_pixels':int(rotated_owned.sum()),'second_distal_distinct_source_texels':distinct_source,
            'second_distal_repeated_source_samples':int(rotated_owned.sum())-distinct_source,'manual_trouser_pixels':len(points)}
    write(out/'RESULTS.json',{'schema':'two-existing-leg-slot-repair/v1','baseline_sha256':sha(source_path),'rich_source_sha256':sha(args.rich_source),
                            'all8original_keys_and_onsets_unchanged':True,'all_upper_head_scarf_glove_pixels_unchanged':True,
                            'changed_frames':target_ids,'period':[1,1],'new_frames_added':0,'journal_replay_exact':True,
                            'all_final_composite_visible_pixels_source_witnessed':True,'visible_source_pose_angles_degrees':angles,
                            'source_half_angle_delta_degrees':midpoint_delta,'applied_rotation_degrees':rotation['degrees'],
                            'source_pose_proxies':'Visible projected ankle/toe silhouette points; not recovered joints or hidden anatomy',
                            'counts':counts,'coordination_limit':'Upper body/pelvis remains held. These masked edits cannot establish whole-pose coordination or continuous-playback improvement.',
                            'art_acceptance':'pending root review','runner_sha256':sha(__file__),'recipe_sha256':sha(args.recipe)})
    assert sha(source_path)==recipe['baseline_sha256'] and sha(args.rich_source)==recipe['rich_source_sha256']
    write(out/'SHA256.json',{str(p.relative_to(out)):sha(p)for p in sorted(out.rglob('*'))if p.is_file()})
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',required=True,type=Path);parser.add_argument('--rich-source',required=True,type=Path)
    parser.add_argument('--recipe',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    run(parser.parse_args())
