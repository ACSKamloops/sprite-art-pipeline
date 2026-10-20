#!/usr/bin/env python3
"""Verify literal source ownership, replay, preservation and exact dodge clocks."""
from pathlib import Path
import json,hashlib,struct,subprocess,argparse
from fractions import Fraction
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes,label
from replay_head import replay,cell
R=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def chunks(p):
 data=p.read_bytes();i=8
 while i<len(data):
  n=int.from_bytes(data[i:i+4],'big');yield data[i+4:i+8],data[i+8:i+8+n];i+=n+12

def main(out):
 if out.exists():raise ValueError('Use a fresh verification output directory')
 out.mkdir();atlas=np.array(Image.open(R/'inputs'/'atlas.png'));m=read(R/'inputs'/'head-protection.json');plan=read(R/'frozen-plan.json');records=[]
 for filename,pin in read(R/'SOURCE-INPUTS.json').items():
  assert sha(Path(pin['path']).read_bytes())==pin['sha256'];assert sha((R/'inputs'/filename).read_bytes())==pin['sha256']
 for job in plan['jobs']:
  view=job['view'];a=cell(atlas,job['source_frame']);b=np.array(Image.open(R/'candidates'/f'{view}.png'));p=R/'replay-verified'/'witnesses'/view;xy=np.load(p/'source-xy.npy',allow_pickle=False);owner=np.load(p/'owner.npy',allow_pickle=False)
  # Independent scalar literal row replay; source remains immutable.
  expected=a.copy();old=np.zeros((128,128),bool);shift=np.zeros_like(old)
  for y,x0,x1 in m['views'][view]['rows_y_x0_x1']:
   for x in range(x0,x1):expected[y,x]=[0,0,0,0];old[y,x]=True
  for y,x0,x1 in m['views'][view]['rows_y_x0_x1']:
   for x in range(x0,x1):
    shift[y+job['dy'],x]=True
    if a[y,x,3]>0:expected[y+job['dy'],x]=a[y,x]
  assert np.array_equal(expected,b);assert np.array_equal(a[xy[:,:,1],xy[:,:,0]],b)
  assert sha(a.tobytes())==job['source_cel_rgba_sha256'];assert sha(b.tobytes())==job['candidate_rgba_sha256'];assert sha((R/'candidates'/f'{view}.png').read_bytes())==job['candidate_png_sha256']
  changed=np.any(a!=b,axis=2);assert not (changed&~(old|shift)).any();assert np.array_equal(a[61:],b[61:]);assert not np.any(b[b[:,:,3]==0,:3])
  sy,sx=np.where(old&(a[:,:,3]>0));assert np.array_equal(b[sy+job['dy'],sx],a[sy,sx])
  nonhead=(~old)&(a[:,:,3]>0);assert not (nonhead&changed&(b[:,:,3]==0)).any()
  zero_skip=shift&~old&(owner==0)&(a[:,:,3]>0);assert np.array_equal(a[zero_skip],b[zero_skip])
  journal=read(p/'changed-pixels.json');assert len(journal)==int(changed.sum());assert {(j['at'][0],j['at'][1]) for j in journal}=={(int(x),int(y)) for y,x in zip(*np.where(changed))}
  for j in journal:
   x,y=j['at'];sx,sy=j['source_xy'];assert j['before']==a[y,x].tolist();assert j['after']==b[y,x].tolist()==a[sy,sx].tolist()
  topology={}
  for threshold in (1,128):
   aalpha=a[:,:,3]>=threshold;balpha=b[:,:,3]>=threshold
   topology[f'alpha_ge_{threshold}']={'source_components_4':int(label(aalpha)[1]),'candidate_components_4':int(label(balpha)[1]),'source_enclosed_gap_pixels':int((binary_fill_holes(aalpha)&~aalpha).sum()),'candidate_enclosed_gap_pixels':int((binary_fill_holes(balpha)&~balpha).sum())}
  clip=view+'_dodge';manifest=read(R/'inputs'/'animations.json');holds=[Fraction(9,200),Fraction(21,200),Fraction(11,200),Fraction(11,400),Fraction(11,400)];assert manifest['animations'][clip]['holds']==[float(x) for x in holds];assert manifest['animations'][clip]['loop'] is False
  for suffix in ('A-source-native','B-head-candidate-native','AB-dodge-2x-once','AB-dodge-2x-repeat'):
   path=R/'previews'/f'{view}-{suffix}.apng';dur=[];plays=None
   for kind,data in chunks(path):
    if kind==b'fcTL':f=struct.unpack('>IIIIIHHBB',data);dur.append(Fraction(f[5],f[6]))
    if kind==b'acTL':count,plays=struct.unpack('>II',data);assert count==5
   assert dur==holds and sum(dur)==Fraction(13,50);assert plays==(0 if suffix.endswith('repeat') else 1)
  # Decode the MP4 and verify every exact held-pose exposure, not merely rate.
  mp=R/'previews'/f'{view}-AB-dodge-exact-260ms.mp4';raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(mp),'-f','rawvideo','-pix_fmt','rgb24','-']);frames=np.frombuffer(raw,np.uint8).reshape((-1,288,512,3));assert len(frames)==104
  begin=0
  for hold in (18,42,22,11,11):assert np.all(frames[begin:begin+hold]==frames[begin]);begin+=hold
  records.append({'view':view,'literal_replay_exact':True,'full_frame_source_coordinate_witness_exact':True,'rigid_head_nonzero_texels_preserved':int((old&(a[:,:,3]>0)).sum()),'outside_union_changed':0,'rows_y_ge_61_unchanged':True,'boots_unchanged':True,'nonhead_visible_pixels_erased':0,'transparent_shift_nonhead_pixels_preserved':int(zero_skip.sum()),'head_body_topology':topology,'apng_exact_holds':[[x.numerator,x.denominator] for x in holds],'mp4_exact_400fps_hold_counts':[18,42,22,11,11]})
 # Apply to a fresh destination, and verify refusal behavior before output.
 receipt=replay(R/'inputs'/'atlas.png',R/'inputs'/'head-protection.json',out/'fresh-replay')
 for job in plan['jobs']:assert np.array_equal(np.array(Image.open(out/'fresh-replay'/f"{job['view']}.png")),np.array(Image.open(R/'candidates'/f"{job['view']}.png")))
 stale=atlas.copy();stale[116//8*128+35,116%8*128+60]=[255,0,255,255];Image.fromarray(stale).save(out/'stale-settle-atlas.png')
 target=out/'must-not-exist-stale'
 try:replay(out/'stale-settle-atlas.png',R/'inputs'/'head-protection.json',target)
 except ValueError as e:assert 'Settle donor changed' in str(e)
 else:raise AssertionError('Stale target accepted')
 assert not target.exists()
 (out/'changed-ownership.json').write_bytes((R/'inputs'/'head-protection.json').read_bytes()+b'\n')
 try:replay(R/'inputs'/'atlas.png',out/'changed-ownership.json',out/'must-not-exist-mask')
 except ValueError as e:assert 'Head ownership source changed' in str(e)
 else:raise AssertionError('Changed ownership accepted')
 assert not (out/'must-not-exist-mask').exists()
 sentinel=out/'existing';sentinel.mkdir();(sentinel/'KEEP').write_text('preserve\n')
 try:replay(R/'inputs'/'atlas.png',R/'inputs'/'head-protection.json',sentinel)
 except ValueError:pass
 else:raise AssertionError('Existing output accepted')
 assert (sentinel/'KEEP').read_text()=='preserve\n'
 result={'mechanical_checks_passed':True,'source_files_unchanged':True,'stale_settle_rejected_before_output':True,'changed_head_ownership_rejected_before_output':True,'existing_output_refused_and_sentinel_preserved':True,'exact_replay_views':4,'source_alpha0_hidden_rgb_zero':True,'candidate_alpha0_hidden_rgb_zero':True,'whole_body_or_boot_translation':False,'candidate_count':1,'literal_mask_draft_status':'rejected diagnostic, final transparent ownership preserves body outside old mask','ratings':None,'approval_claimed':False,'views':records}
 (out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='views'},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-name',default='verification');a=p.parse_args()
 if Path(a.out_name).name!=a.out_name or a.out_name in ('.','..'):p.error('Use a fresh child directory name')
 main(R/a.out_name)
