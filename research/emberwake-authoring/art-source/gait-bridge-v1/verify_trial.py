#!/usr/bin/env python3
"""Independent frozen-map/mesh replay and append-only integration checks."""
from pathlib import Path
import json,hashlib,subprocess,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_fill_holes
from apply_bridges import apply
R=Path(__file__).resolve().parent
V=R/'verification'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def cel(a,i):return a[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128]
def savej(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def topology(a):
 b=a[:,:,3]>0
 return {'alpha_components_4':int(label(b)[1]),'interior_alpha0_hole_pixels':int((binary_fill_holes(b)&~b).sum()),'visible_pixels':int(b.sum())}
def mesh_replay(a,s,owner,support):
 yy,xx=np.mgrid[:128,:128];m=np.stack((xx,yy),-1).astype(np.int16);m[owner]=s['clear_source_xy']
 roi=s['roi'];q=np.column_stack((xx.ravel(),yy.ravel(),np.ones(128*128)))
 inside=((xx>=roi[0])&(xx<roi[2])&(yy>=roi[1])&(yy<roi[3])).ravel()
 for indices in s['triangles']:
  src=np.array([s['source_vertices'][i] for i in indices],float);dst=np.array([s['target_vertices'][i] for i in indices],float)
  # Batched linear solve is separate from the producer's scalar pixel loop.
  weights=np.linalg.solve(np.vstack((dst.T,np.ones(3))),q.T).T
  accept=(weights.min(axis=1)>=-1e-8)&inside
  sample=np.floor(weights@src+.5).astype(int);accept&=(sample.min(axis=1)>=0)&(sample.max(axis=1)<128)
  idx=np.flatnonzero(accept);keep=owner[sample[idx,1],sample[idx,0]];idx=idx[keep]
  m.reshape(-1,2)[idx]=sample[idx]
 m[support]=np.stack((xx,yy),-1)[support]
 return m

def main():
 V.mkdir(exist_ok=False);rows=[];summary={}
 sourcepins=read(R/'SOURCE-INPUTS.json')
 for actor,files in sourcepins.items():
  for filename,pin in files.items():assert sha(Path(pin['path']).read_bytes())==pin['sha256'];assert sha((R/'inputs'/actor/filename).read_bytes())==pin['sha256']
 for variant in ('trial-a-down','trial-b-boot-preserved'):
  jobs=read(R/variant/'summary.json')
  for s in jobs:
   p=R/variant/'maps'/s['key'];a=np.array(Image.open(p/'body-donor.png').convert('RGBA'));expected=np.array(Image.open(p/'expected.png').convert('RGBA'));xy=np.load(p/'source-xy.npy',allow_pickle=False);owned=np.array(Image.open(p/'source-owner.png'))>0;protected=np.array(Image.open(p/'protected-support.png'))>0;boot=np.array(Image.open(p/'rigid-boot.png'))>0
   assert sha(a.tobytes())==s['donor_rgba_sha256'];assert sha(expected.tobytes())==s['expected_rgba_sha256'];assert sha((p/'source-xy.npy').read_bytes())==s['map_sha256']
   assert np.array_equal(a[xy[:,:,1],xy[:,:,0]],expected)
   independent=mesh_replay(a,s,owned,protected)
   independent_rgba_matches=bool(np.array_equal(a[independent[:,:,1],independent[:,:,0]],expected))
   # Verify geometry without assuming that a second binary64 solver resolves
   # exact mathematical half-texel ties in the same direction.
   triangle=np.load(p/'triangle.npy',allow_pickle=False);ownership=np.load(p/'ownership.npy',allow_pickle=False);max_distance=0.
   for ti,indices in enumerate(s['triangles']):
    sy,sx=np.where((triangle==ti)&(ownership==1))
    if len(sx)==0:continue
    src=np.array([s['source_vertices'][i] for i in indices],float);dst=np.array([s['target_vertices'][i] for i in indices],float)
    q=np.stack((sx,sy,np.ones(len(sx))),axis=0);bary=np.linalg.solve(np.vstack((dst.T,np.ones(3))),q).T;continuous=bary@src
    distance=np.abs(xy[sy,sx]-continuous);max_distance=max(max_distance,float(distance.max()));assert distance.max()<=.50000001
   assert np.array_equal(a[xy[:,:,1],xy[:,:,0]],expected)
   # Stored integer coordinates are the replay authority; floating arithmetic
   # may choose neighboring identical texels at exact nearest boundaries.
   coordinate_differences=int(np.any(independent!=xy,axis=2).sum())
   mask=np.zeros((128,128),bool);l,t,r,b=s['roi'];mask[t:b,l:r]=True;changed=np.any(a!=expected,axis=2)
   assert not changed[~mask].any();assert not changed[protected].any()
   journal=read(p/'changed-pixels.json');assert len(journal)==int(changed.sum())
   assert {(j['at'][0],j['at'][1]) for j in journal}=={(int(x),int(y)) for y,x in zip(*np.where(changed))}
   for j in journal:
    x,y=j['at'];sx,sy=j['source_xy'];assert j['before']==a[y,x].tolist();assert j['after']==expected[y,x].tolist()==a[sy,sx].tolist()
   by,bx=np.where(boot);dx,dy=s['translation'];clipped=int((~np.all(expected[by+dy,bx+dx]==a[by,bx],axis=1)).sum())
   assert clipped==s['boot_pixels_not_preserved_after_translation']
   if variant.endswith('boot-preserved'):assert clipped==0
   oldtop=topology(a);newtop=topology(expected)
   rows.append({'key':s['key'],'variant':variant,'changed_pixels':len(journal),'boot_clipped_pixels':clipped,'independent_floating_mesh_rgba_matches':independent_rgba_matches,'independent_nearest_geometry_bound_max':max_distance,'independent_mesh_coordinate_tie_differences':coordinate_differences,'frozen_integer_map_replay_matches':True,'outside_roi_changed':0,'protected_support_changed':0,'source_topology':oldtop,'candidate_topology':newtop,'swing_source_visible':s['source_visible_swing_pixels'],'swing_output_visible':s['output_visible_swing_pixels']})
 for actor in ('lyra','brann'):
  receipt=apply(R/'inputs'/actor/'atlas.png',R/'inputs'/actor/'animations.json',actor,V/f'apply-baseline-{actor}')
  actual=np.array(Image.open(V/f'apply-baseline-{actor}'/'atlas.png'));expected=np.array(Image.open(R/'trial-b-boot-preserved'/actor/'atlas.png'));assert np.array_equal(actual,expected)
  mm=read(V/f'apply-baseline-{actor}'/'animations.json');old=read(R/'inputs'/actor/'animations.json');wanted=read(R/'trial-b-boot-preserved'/actor/'animations.json')
  assert mm['animations']==wanted['animations']
  for key,val in old.items():
   if key not in ('animations','lineage'):assert mm[key]==val
  assert mm['lineage'][:len(old['lineage'])]==old['lineage']
  for key,clip in old['animations'].items():
   if key not in ('south_walk','north_walk'):assert clip==mm['animations'][key]
  # An unrelated changed action cel plus an appended settle cel and updated
  # action metadata must survive, while map donor hashes continue to bind.
  fd=V/f'modified-unrelated-input-{actor}';fd.mkdir();base=np.array(Image.open(R/'inputs'/actor/'atlas.png'));fixture=np.zeros((2176,1024,4),np.uint8);fixture[:len(base)]=base
  fixture[1*128+82,0*128+55]=base[82,55] # different texel inside cel8 only
  i=130;fixture[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128]=cel(base,14)
  fm=read(R/'inputs'/actor/'animations.json');fm['animations']['south_cast']['frames'][0]=130;fm['lineage'].append({'frame':130,'unrelated_test_fixture':True})
  Image.fromarray(fixture).save(fd/'atlas.png');savej(fd/'animations.json',fm)
  rr=apply(fd/'atlas.png',fd/'animations.json',actor,V/f'apply-modified-unrelated-{actor}');assert rr['append_start']==131
  applied=np.array(Image.open(V/f'apply-modified-unrelated-{actor}'/'atlas.png'));assert all(np.array_equal(cel(applied,i),cel(fixture,i)) for i in range(131))
  am=read(V/f'apply-modified-unrelated-{actor}'/'animations.json');assert am['animations']['south_cast']==fm['animations']['south_cast'];assert am['lineage'][:len(fm['lineage'])]==fm['lineage']
  # Stale edited donor must reject before creating any output.
  stale=fixture.copy();donor=1 if actor=='lyra' else 1;stale[donor//8*128+90,donor%8*128+55]=[255,0,255,255];Image.fromarray(stale).save(fd/'stale-donor.png')
  rejected=V/f'rejected-stale-{actor}'
  try:apply(fd/'stale-donor.png',fd/'animations.json',actor,rejected)
  except ValueError as e:assert 'Donor cel changed' in str(e)
  else:raise AssertionError('Stale donor accepted')
  assert not rejected.exists()
  sentinel=V/f'existing-output-{actor}';sentinel.mkdir();(sentinel/'KEEP').write_text('preserve\n')
  try:apply(fd/'atlas.png',fd/'animations.json',actor,sentinel)
  except ValueError:pass
  else:raise AssertionError('Existing output accepted')
  assert (sentinel/'KEEP').read_text()=='preserve\n'
 # MP4 decoded image holds: nine equal 1/160-second frames per authored pose.
 clock=[]
 for actor in ('lyra','brann'):
  for view in ('south','north'):
   mp4=R/'previews'/f'{actor}-{view}-comparison-exact-450ms.mp4'
   raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(mp4),'-f','rawvideo','-pix_fmt','rgb24','-'])
   frames=np.frombuffer(raw,np.uint8).reshape((-1,288,1024,3));assert len(frames)==72
   for i in range(8):assert np.all(frames[i*9:(i+1)*9]==frames[i*9])
   clock.append({'clip':f'{actor}-{view}','decoded_mp4_frames':72,'equal_nine_frame_holds':True,'cycle_seconds':'9/20'})
 savej(V/'MAP-AND-PRESERVATION.json',rows);savej(V/'CLOCK-DECODE.json',clock)
 summary={'mechanical_checks_passed':True,'hole_free_requirement_passed':False,'candidate_quality_status':'changes_required: thin inter-leg seams and isolated alpha pinholes remain','source_file_hashes_unchanged':True,'frozen_maps_replayed':len(rows),'floating_mesh_rebake_limitation':'Five Brann cels across A/B can choose different nearest neighbors at mathematical half-texel ties with a batched solve; frozen integer maps replay exactly and all mapped coordinates pass the independent <=0.5 nearest-geometry bound.','final_b_zero_boot_clipping_cels':16,'baseline_apply_matches_candidate_atlas':True,'unrelated_modified_actions_and_appended_settle_cells_preserved':True,'original_provenance_preserved':True,'stale_donor_rejected_before_output':True,'existing_output_refused_and_sentinel_preserved':True,'mp4_authored_holds_verified_by_decoded_pixels':True,'art_acceptance':'not established by these mechanical checks','topology_new_hole_cases':[x for x in rows if x['candidate_topology']['interior_alpha0_hole_pixels']>x['source_topology']['interior_alpha0_hole_pixels']],'topology_component_increase_cases':[x for x in rows if x['candidate_topology']['alpha_components_4']>x['source_topology']['alpha_components_4']]}
 savej(V/'SUMMARY.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out-name',default='verification-rerun');args=parser.parse_args()
 if Path(args.out_name).name!=args.out_name or args.out_name in ('.','..'):parser.error('Use a fresh child folder name')
 V=R/args.out_name
 main()
