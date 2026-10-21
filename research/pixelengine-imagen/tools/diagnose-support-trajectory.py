#!/usr/bin/env python3
"""Visible support-boot trajectory diagnostic and one bounded midpoint trial."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
import sys,shutil
import numpy as np
from PIL import Image

REPO=Path(__file__).resolve().parents[3]
TOOLKIT=REPO/'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0,str(TOOLKIT))
from sprite_lab import History,canonical_json,candidate_transaction,project_hash,render_cel
from sprite_lab.core import render_frames


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


helper=module('support_helpers',Path(__file__).with_name('probe-component-head-bridge.py'))
warp=module('support_warp',REPO/'skills/sprite-construction-editing/scripts/warp_part.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def getframe(project,name):return next(f for f in project['frames']if f['id']==name)


def measure(image,roi,source_frame,source_xy=None,visibility=None):
    a=np.array(image);left,right=roi
    row70=[x for x in range(left,right+1)if a[70,x,3]>0]
    toe69=max(x for x in range(left,right+1)if a[69,x,3]>0)
    bright=(128,71,42,255)
    shaft=max(x for x in range(left,right+1)if tuple(a[65,x])==bright)
    points={'toe_outline_row69':[toe69,69],'sole_back_row70':[min(row70),70],
            'sole_front_row70':[max(row70),70],'ankle_height_bright_leather_edge':[shaft,65]}
    result={}
    for key,(x,y)in points.items():
        sx,sy=(x,y)if source_xy is None else map(int,source_xy[y,x])
        result[key]={'xy':[x,y],'rgba':list(map(int,a[y,x])),'source_frame':source_frame,
                     'source_xy':[sx,sy],'visible_in_composite':True if visibility is None else bool(visibility[y,x])}
    return result


def layer_visibility(project,frame_id,layer_id):
    frame=getframe(project,frame_id);above=False;hidden=np.zeros((80,80),dtype=bool)
    for layer in project['layers']:
        if layer['id']==layer_id:above=True;continue
        if above and layer['id']in frame['cels']:
            hidden|=np.array(render_cel(project,frame['cels'][layer['id']]))[:,:,3]>0
    return ~hidden


def run(args):
    out=args.output.absolute()
    if out.exists()or out.is_symlink():raise ValueError('Fresh output required')
    recipe=json.loads(args.recipe.read_text());repair_path=args.repair/'cluster-repair/editable-project.json'
    original_path=args.pilot/'candidate-two-bridges/editable-project.json'
    for p,h in [(args.rich_source,recipe['rich_source_sha256']),(repair_path,recipe['repair02_sha256']),(original_path,recipe['original_two_bridge_sha256'])]:
        if sha(p)!=h:raise ValueError('Frozen source mismatch')
    rich=json.loads(args.rich_source.read_text());repair=json.loads(repair_path.read_text());original=json.loads(original_path.read_text())
    keys=render_frames(rich,rich['animations'][0]['frames']);order=repair['animations'][0]['frames']
    before=render_frames(repair,order);initial=copy.deepcopy(repair)
    endpoint={str(i):measure(keys[i],recipe['endpoint_x_windows'][str(i)],i)for i in [2,3,4]}
    observed={};maps={}
    for bridge in ['bridge-2-3','bridge-3-4']:
        maps[bridge]={p:np.load(args.repair/f'{bridge}-{p}-source-xy.npy',allow_pickle=False)for p in ['far-trouser','far-distal','near-trouser','near-distal']}
        image=render_cel(repair,getframe(repair,bridge)['cels']['far-distal'])
        observed[bridge]=measure(image,[20,50],3,maps[bridge]['far-distal'],layer_visibility(repair,bridge,'far-distal'))
    # Material edges, not alpha centroids or nominal control names.
    assert endpoint['2']['sole_back_row70']['xy'][0]==35 and endpoint['2']['sole_front_row70']['xy'][0]==45
    assert endpoint['3']['sole_back_row70']['xy'][0]==29 and endpoint['3']['sole_front_row70']['xy'][0]==39
    assert observed['bridge-2-3']['sole_back_row70']['xy'][0]==30 and observed['bridge-2-3']['sole_front_row70']['xy'][0]==40
    out.mkdir(parents=True);shutil.copy2(__file__,out/'runner.py');shutil.copy2(args.recipe,out/'recipe.json')
    write(out/'MEASURED-PROXIES.json',{'source_endpoints':endpoint,'existing_slots':observed,
                                    'clock_ms':{'key2':250,'phase2.5':312.5,'key3':375,'phase3.5':437.5,'key4':500},
                                    'role_correspondence':'Plausible support-role trace from key1 broad right boot through key2 broad central boot to key3 left boot. Key2 opposite foot/cuffs overlap; physical limb side is not established.',
                                    'proxy_limits':'Toe/sole contour and bright-leather material edges can redraw across keys; the ankle joint is not visible. These are actual pixel probes, not recovered bones/contact.',
                                    'hypothesis':'Linear midpoint of corresponding visible material/silhouette features at half-phase; gait acceleration or ground contact is not established.'})
    # The two visible sole edges agree for2.5. They disagree for3.5 because the
    # endpoint boot turns/narrows; leave that whole slot unchanged.
    history=History(initial);bridge='bridge-2-3';shift=recipe['phase2_5_support_shift']
    cid=getframe(history.project,bridge)['cels']['far-distal']
    history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),
                   'reason':'Correct support-boot horizontal midpoint using BOTH visible sole edges; retain complete rigid boot and permit passing occlusion',
                   'operations':[{'op':'translate','cel_id':cid,'dx':shift,'dy':0,'allow_clip':False}]})
    old_map=maps[bridge]['far-distal'];new_map=np.full_like(old_map,-1)
    for y,x in np.argwhere(old_map[:,:,0]>=0):new_map[y,x+shift]=old_map[y,x]
    maps[bridge]['far-distal']=new_map
    request=json.loads((args.pilot/f'{bridge}-far-trouser/request.json').read_text())
    request['target_vertices'][2][0]+=shift;request['target_vertices'][3][0]+=shift
    write(out/'support-trouser-request.json',request);warp.run(out/'support-trouser-request.json',out/'support-trouser')
    cid=getframe(history.project,bridge)['cels']['far-trouser'];old=np.array(render_cel(history.project,cid));replacement=Image.open(out/'support-trouser/layer.png').convert('RGBA');new=np.array(replacement)
    mask=[[int(x),int(y)]for y,x in np.argwhere((old[:,:,3]>0)|(new[:,:,3]>0))]
    tx=candidate_transaction(history.project,cid,replacement,mask);tx['reason']='Adjust only owned support trouser source paint to meet the rigid boot midpoint; pelvis and passing leg remain protected'
    history.apply(tx);maps[bridge]['far-trouser']=np.load(out/'support-trouser/source-xy.npy',allow_pickle=False)
    final=history.project;after=render_frames(final,order)
    assert repair['animations']==final['animations']and repair['canvas']==final['canvas']
    for i,(a,b)in enumerate(zip(before,after)):
        if order[i]!=bridge:assert a.tobytes()==b.tobytes()
        else:assert np.array_equal(np.array(a)[:54],np.array(b)[:54])
    for i in range(8):assert after[order.index(f'key-{i}')].tobytes()==keys[i].tobytes()
    # No further separation optimization: all near/passing-leg cels stay exact.
    for layer in ['near-trouser','near-distal']:
        assert {k:v for k,v in repair['cels'].items()if v['layer_id']==layer}=={k:v for k,v in final['cels'].items()if v['layer_id']==layer}
    current=getframe(final,bridge);support=render_cel(final,current['cels']['far-distal'])
    trial_measured=measure(support,[20,50],3,maps[bridge]['far-distal'],layer_visibility(final,bridge,'far-distal'))
    assert trial_measured['sole_back_row70']['xy']==[32,70]and trial_measured['sole_front_row70']['xy']==[42,70]
    assert trial_measured['sole_back_row70']['visible_in_composite']and trial_measured['sole_front_row70']['visible_in_composite']
    assert trial_measured['ankle_height_bright_leather_edge']['xy']==[37,65]
    write(out/'TRIAL-MEASURED-PIXELS.json',trial_measured)
    # Full frozen map replay, including actual topmost passing-leg occlusion.
    source_map=np.full((80,80,3),-1,dtype=np.int64);composite=np.array(render_cel(final,current['cels']['held-upper']))
    for y,x in np.argwhere(composite[:,:,3]>0):source_map[y,x]=[2,x,y]
    for part in ['far-trouser','far-distal','near-trouser','near-distal']:
        pixels=np.array(render_cel(final,current['cels'][part]));owned=pixels[:,:,3]>0;xy=maps[bridge][part]
        for y,x in np.argwhere(owned):
            sx,sy=map(int,xy[y,x]);assert tuple(pixels[y,x])==keys[3].getpixel((sx,sy));source_map[y,x]=[3,sx,sy]
        composite[owned]=pixels[owned];np.save(out/f'{part}-source-xy.npy',xy,allow_pickle=False)
    assert np.array_equal(composite,np.array(after[order.index(bridge)]));np.save(out/'phase2_5-source-frame-xy.npy',source_map,allow_pickle=False)
    (out/'initial-project.json').write_text(canonical_json(initial)+'\n');write(out/'journal.json',history.journal())
    assert project_hash(History.replay(initial,history.journal()).project)==project_hash(final)
    for name,project in [('original-two-bridge',original),('repair02',repair),('support-midpoint-trial',final)]:helper.export(project,out/name,name)
    old_images=render_frames(original,order)
    choices=[('Original two-bridge',old_images),('Repair02 before support correction',before),('Only2.5 support midpoint corrected',after)]
    for scale in [1,2,4]:helper.sheet(out/f'affected-chronology-{scale}x.png',[(label,[images[i]for i in [2,3,4,5,6]])for label,images in choices],scale)
    helper.sheet(out/'support-features-8x.png',[(label,[images[3],images[5]])for label,images in choices],8,(27,53,53,73))
    helper.sheet(out/'all-pairs-2x.png',[('Trial all pairs9->0,0->1,...8->9',[im for i in range(10)for im in[after[(i-1)%10],after[i]]])],2)
    write(out/'RESULTS.json',{'schema':'visible-support-trajectory-trial/v1','all8keys_onsets_upper_clocks_unchanged':True,
                            'changed_slot':'phase2.5 only','phase3_5':'unchanged; one translation cannot match its heel,toe and shaft endpoint midpoints',
                            'rigid_support_shift':[shift,0],'trial_visible_sole_row70':[32,42],
                            'trial_shaft_edge_x65':37,'trial_upper_toe_row69_occluded':not trial_measured['toe_outline_row69']['visible_in_composite'],
                            'passing_leg_cels_unchanged':True,'journal_replay_exact':True,'frozen_source_map_replay_exact':True,
                            'assumptions':recipe['assumptions'],'art_acceptance':'pending root review; no score or ground-contact proof',
                            'runner_sha256':sha(__file__),'recipe_sha256':sha(args.recipe)})
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pilot',required=True,type=Path)
    parser.add_argument('--repair',required=True,type=Path);parser.add_argument('--rich-source',required=True,type=Path)
    parser.add_argument('--recipe',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    run(parser.parse_args())
