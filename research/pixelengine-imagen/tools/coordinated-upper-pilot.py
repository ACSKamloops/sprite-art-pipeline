#!/usr/bin/env python3
"""One source-owned coordinated upper pose, preserving frozen keys and legs."""
import argparse,copy,hashlib,importlib.util,json,sys
from pathlib import Path
import numpy as np
from PIL import Image

REPO=Path(__file__).resolve().parents[3]
TOOLKIT=REPO/'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0,str(TOOLKIT))
from sprite_lab import History,canonical_json,candidate_transaction,project_hash,render_cel
from sprite_lab.core import render_frames


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


helper=module('coordinated_helpers',Path(__file__).with_name('probe-component-head-bridge.py'))
warp=module('coordinated_warp',REPO/'skills/sprite-construction-editing/scripts/warp_part.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def frame(project,name):return next(f for f in project['frames']if f['id']==name)


def spans_mask(image,spans):
    a=np.array(image);mask=np.zeros((80,80),dtype=bool)
    for y,left,right in spans:mask[y,left:right+1]=a[y,left:right+1,3]>0
    return mask


def run(args):
    out=args.output.absolute()
    if out.exists()or out.is_symlink():raise ValueError('Fresh output required')
    recipe=json.loads(args.plan.read_text())
    if sha(args.baseline)!=recipe['baseline_sha256']or sha(args.source)!=recipe['source_sha256']:raise ValueError('Frozen input mismatch')
    baseline=json.loads(args.baseline.read_text());source=json.loads(args.source.read_text());order=baseline['animations'][0]['frames']
    keys=render_frames(source,source['animations'][0]['frames']);arrays=[np.array(i)for i in keys]
    body2=np.array(render_cel(source,frame(source,'pose-02')['cels']['body']))
    head2=np.array(render_cel(source,frame(source,'pose-02')['cels']['owner']))
    masks2={};masks2['bib']=spans_mask(keys[2],recipe['source2_bib_spans'])&(body2[:,:,3]>0)
    old_arm=spans_mask(keys[2],recipe['source2_old_near_arm_spans'])&(body2[:,:,3]>0)&~masks2['bib']
    # Below sleeve, never assign teal body material to the old leather/skin arm.
    for y,x in np.argwhere(old_arm):
        if y>=38 and body2[y,x,1]>body2[y,x,0]:old_arm[y,x]=False
    masks2['old-near-arm']=old_arm
    far=np.zeros((80,80),dtype=bool);far[37:53,47:54]=body2[37:53,47:54,3]>0
    masks2['far-upper-arm']=far.copy();masks2['far-upper-arm'][48:]=False
    masks2['far-hand']=far.copy();masks2['far-hand'][:48]=False
    assigned=masks2['bib']|old_arm|far
    masks2['pelvis']=(body2[:,:,3]>0)&~assigned
    masks2['pelvis'][:47]=False;masks2['pelvis'][54:]=False
    assigned|=masks2['pelvis']
    masks2['torso']=(body2[:,:,3]>0)&~assigned;masks2['torso'][54:]=False
    masks2['head']=head2[:,:,3]>0
    lower=body2[:,:,3]>0;lower[:54]=False
    assert np.array_equal(sum(m.astype(int)for m in masks2.values())+lower.astype(int),((body2[:,:,3]>0)|(head2[:,:,3]>0)).astype(int))
    masks3={part:spans_mask(keys[3],spans)for part,spans in recipe['source3_near_arm_spans'].items()}
    assert (sum(m.astype(int)for m in masks3.values())<=1).all()
    out.mkdir(parents=True);(out/'assets').mkdir()
    keys[2].save(out/'assets/key2.png');keys[3].save(out/'assets/key3.png')
    write(out/'plan.json',recipe);(out/'runner.py').write_text(Path(__file__).read_text())
    for label,masks in [('key2',masks2),('key3',masks3)]:
        colors=[(220,60,60,255),(60,160,240,255),(240,170,40,255),(180,60,220,255),(60,220,160,255),(200,200,80,255),(240,140,160,255),(120,160,200,255)]
        view=np.zeros((80,80,4),dtype=np.uint8)
        for (part,mask),color in zip(masks.items(),colors):
            Image.fromarray(mask.astype(np.uint8)*255).save(out/f'assets/{label}-{part}-owner.png');view[mask]=color
        Image.fromarray(view).save(out/f'{label}-ownership.png')
    before=render_frames(baseline,order);target_index=order.index('bridge-2-3')
    initial=copy.deepcopy(baseline);f=frame(initial,'bridge-2-3');old_upper=f['cels'].pop('held-upper')
    initial['layers'].append({'id':'coordinated-old-upper','name':'Old upper removal through exact source mask','locked':False})
    initial['cels']['coordinated-old-upper']={'layer_id':'coordinated-old-upper','pixels':list(initial['cels'][old_upper]['pixels'])};f['cels']['coordinated-old-upper']='coordinated-old-upper'
    for part in recipe['layer_order']:
        initial['layers'].append({'id':'coord-'+part,'name':'Source-owned '+part+' only at phase2.5','locked':False})
        initial['cels']['coord-'+part]={'layer_id':'coord-'+part,'pixels':[0]*6400};f['cels']['coord-'+part]='coord-'+part
    initial['layers'].append({'id':'coord-seam-underpaint','name':'Explicit one-pixel newly exposed shoulder cloth seam','locked':False})
    initial['cels']['coord-seam-underpaint']={'layer_id':'coord-seam-underpaint','pixels':[0]*6400};f['cels']['coord-seam-underpaint']='coord-seam-underpaint'
    initial['provenance']['coordinated_upper_plan_sha256']=sha(args.plan)
    assert all(a.tobytes()==b.tobytes()for a,b in zip(before,render_frames(initial,order)))
    history=History(initial);old_pixels=np.array(render_cel(initial,'coordinated-old-upper'))
    points=[[int(x),int(y)]for y,x in np.argwhere(old_pixels[:,:,3]>0)]
    history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),
                   'reason':'Remove exact held upper owner only in new coordinated bridge; original eight keys and lower owners remain untouched',
                   'operations':[{'op':'erase','cel_id':'coordinated-old-upper','points':points,'mask':points}]})
    part_records=[];composite=np.zeros((80,80,4),dtype=np.uint8);full_map=np.full((80,80,3),-1,dtype=np.int64)
    for part in recipe['layer_order']:
        spec=recipe['parts'][part];key=spec['source_key'];mask=(masks2 if key==2 else masks3)[spec.get('owner',part)]
        mask_path=out/f'assets/key{key}-{spec.get("owner",part)}-owner.png'
        request={'schema':'nearest-part-warp/v1','canvas':[80,80],
                 'donor':{'path':str((out/f'assets/key{key}.png').resolve()),'sha256':sha(out/f'assets/key{key}.png')},
                 'owner_mask':{'path':str(mask_path.resolve()),'sha256':sha(mask_path)},
                 'source_vertices':spec['source_vertices'],'target_vertices':spec['target_vertices'],
                 'triangles':[[0,1,2],[0,2,3]],'alpha_mode':'nonzero-only'}
        write(out/f'{part}-request.json',request);warp.run(out/f'{part}-request.json',out/part)
        layer=Image.open(out/part/'layer.png').convert('RGBA');a=np.array(layer);owned=a[:,:,3]>0
        assert not owned[54:].any()
        xy=np.load(out/part/'source-xy.npy',allow_pickle=False)
        assert all(tuple(a[y,x])==keys[key].getpixel(tuple(map(int,xy[y,x])))for y,x in np.argwhere(owned))
        tx=candidate_transaction(history.project,'coord-'+part,layer,[[int(x),int(y)]for y,x in np.argwhere(owned)])
        tx['reason']='Import explicit source-owned '+part+' with frozen nearest source map and stated projected attachment controls'
        history.apply(tx);composite[owned]=a[owned]
        for y,x in np.argwhere(owned):full_map[y,x]=[key,int(xy[y,x,0]),int(xy[y,x,1])]
        part_records.append({'part':part,'source_key':key,'source_owned_pixels':int(mask.sum()),'target_owned_pixels':int(owned.sum()),'distinct_source_texels':len(set(map(tuple,xy[owned].tolist())))})
    raw=copy.deepcopy(history.project)
    if recipe.get('seam_repairs'):
        repairs=recipe['seam_repairs'];x,y=repairs['isolated_rim_erase']
        assert composite[y,x,3]>0
        history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),
                       'reason':'Erase one isolated source rim pixel produced at the far-shoulder ownership boundary; retain raw checkpoint',
                       'operations':[{'op':'erase','cel_id':'coord-far-upper-arm','points':[[x,y]],'mask':[[x,y]]}]})
        composite[y,x]=0;full_map[y,x]=[-1,-1,-1]
        sample=repairs['cloth_fill'];x,y=sample['destination'];key,sx,sy=sample['source']
        color=keys[key].getpixel((sx,sy));assert list(color)==sample['expected_rgba']and composite[y,x,3]==0
        index=history.project['palette'].index(list(color))
        history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),
                       'reason':'Author one source-colored shoulder-cloth seam pixel in explicit newly exposed tunic ownership; no hidden anatomy recovered',
                       'operations':[{'op':'paint','cel_id':'coord-seam-underpaint','points':[[x,y,index]],'mask':[[x,y]]}]})
        composite[y,x]=color;full_map[y,x]=[key,sx,sy]
        write(out/'SEAM-REPAIRS.json',repairs)
    upper_preview=Image.fromarray(composite);upper_preview.save(out/'coordinated-upper-only.png')
    final=history.project;after=render_frames(final,order)
    # Add the unchanged lower owners to the full witness map, preserving their
    # actual occlusion. Their source map was frozen by the support-midpoint trial.
    lower_map=np.load(args.baseline.parent.parent/'phase2_5-source-frame-xy.npy',allow_pickle=False)
    final_pixels=np.array(after[target_index])
    for y,x in np.argwhere((final_pixels[:,:,3]>0)&(full_map[:,:,0]<0)):
        assert y>=54;full_map[y,x]=lower_map[y,x]
    reconstructed=np.zeros((80,80,4),dtype=np.uint8)
    for y,x in np.argwhere(full_map[:,:,0]>=0):
        key,sx,sy=map(int,full_map[y,x]);reconstructed[y,x]=arrays[key][sy,sx]
    assert np.array_equal(reconstructed,final_pixels)
    for i,(a,b)in enumerate(zip(before,after)):
        if i!=target_index:assert a.tobytes()==b.tobytes()
        else:assert np.array_equal(np.array(a)[54:],np.array(b)[54:])
    for i in range(8):assert after[order.index(f'key-{i}')].tobytes()==keys[i].tobytes()
    assert baseline['animations']==final['animations']and baseline['canvas']==final['canvas']
    for part in ['far-trouser','far-distal','near-trouser','near-distal']:
        assert {k:v for k,v in baseline['cels'].items()if v['layer_id']==part}=={k:v for k,v in final['cels'].items()if v['layer_id']==part}
    (out/'initial-project.json').write_text(canonical_json(initial)+'\n');write(out/'journal.json',history.journal())
    assert project_hash(History.replay(initial,history.journal()).project)==project_hash(final)
    np.save(out/'phase2_5-source-frame-xy.npy',full_map,allow_pickle=False)
    for record in part_records:
        record['post_seam_edit_pixels']=int((np.array(render_cel(final,'coord-'+record['part']))[:,:,3]>0).sum())
    for name,project in [('support-midpoint-baseline',baseline),('raw-source-parts',raw),('coordinated-upper',final)]:helper.export(project,out/name,name)
    # Rebase the previously requested head-only control on the identical lower
    # pose so comparisons do not accidentally compare different leg repairs.
    control_recipe=json.loads(Path(__file__).with_name('a15-rich-head-bridge-recipe.json').read_text())
    control_recipe['candidate_project_sha256']=sha(args.baseline)
    control_recipe['head_source_project_sha256']=sha(args.source)
    write(out/'head-only-control-plan.json',control_recipe)
    helper.run(argparse.Namespace(candidate=args.baseline,head_source=args.source,
                                  recipe=out/'head-only-control-plan.json',output=out/'head-only-control'))
    control=json.loads((out/'head-only-control/head-neck-cap/editable-project.json').read_text())
    control_frames=render_frames(control,order)
    raw_frames=render_frames(raw,order)
    choices=[('Measured support-midpoint baseline',before),('Head-only rise with neck-cap CONTROL',control_frames),('Raw source-parts: one gap and isolated rim',raw_frames),('Source-owned coordinated upper with explicit seam repair',after)]
    for scale in [1,2,4]:helper.sheet(out/f'neighbors-{scale}x.png',[(label,[images[i]for i in [2,3,4]])for label,images in choices],scale)
    helper.sheet(out/'joints-8x.png',[(label,[images[i]for i in [2,3,4]])for label,images in choices],8,(26,23,54,54))
    helper.sheet(out/'all-pairs-2x.png',[('Coordinated all pairs9->0,0->1,...8->9',[im for i in range(10)for im in[after[(i-1)%10],after[i]]])],2)
    controls=[]
    for name,control in recipe['projected_proxies'].items():
        item=copy.deepcopy(control);item['name']=name
        item['key2_rgba']=list(keys[2].getpixel(tuple(item['key2'])));item['key3_rgba']=list(keys[3].getpixel(tuple(item['key3'])))
        item['target_actual_rgba']=list(after[target_index].getpixel(tuple(item['target'])))
        controls.append(item)
    write(out/'MEASURED-CONTROLS.json',controls)
    write(out/'RESULTS.json',{'schema':'one-coordinated-upper-pose/v1','source_sha256':sha(args.source),'baseline_sha256':sha(args.baseline),
                            'only_phase2_5_changes':True,'other9frames_and8keys_exact':True,'support_and_passing_legs_exact':True,
                            'clock_onsets_canvas_pivots_exact':True,'parts':part_records,'underpaint_pixels':1 if recipe.get('seam_repairs')else 0,
                            'jaw_neck_cap':'none; source2 head and collar translate together',
                            'head_only_control':'Old1pxhead-rise+9pxneckcap recipe rebased on identical support/passing legs and exact clock; separate comparison only',
                            'all_composite_pixels_have_frozen_source_witness':True,'journal_replay_exact':True,
                            'missing_surfaces':'One source-colored cloth seam pixel explicitly authored at(35,36); one isolated rim pixel erased at(48,36). Raw assembly retained. No concealed anatomy reconstructed.',
                            'art_acceptance':'pending; single pose hypothesis only','runner_sha256':sha(__file__),'plan_sha256':sha(args.plan)})
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--baseline',required=True,type=Path);parser.add_argument('--plan',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    run(parser.parse_args())
