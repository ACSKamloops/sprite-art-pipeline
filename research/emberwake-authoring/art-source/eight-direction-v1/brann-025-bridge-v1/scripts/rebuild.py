"""Portable fresh-output controls/maps/RGBA/editor replay for exactfrozen02.5candidate."""
from pathlib import Path
from fractions import Fraction
import argparse,json,hashlib,shutil,os
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,candidate_transaction
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def mask(n):return np.array(Image.open(R/n))>0
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=d.copy();use=sa>0
 for k in range(3):o[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 o[:,:,3][use]=(n[use]+127)//255
 return o.astype(np.uint8)
def from_controls(source,owner,c):
 src=np.array(c['source_vertices'],float);dst=np.array(c['target_vertices'],float);paint=np.zeros((128,128,4),np.uint8);xy=np.full((128,128,2),-1,np.int16);acc=np.zeros((128,128),bool)
 for t in c['triangles']:
  s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
   for x in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
    b=inv@np.array([x,y,1.])
    if b.min()<-1e-8:continue
    sx,sy=np.floor(b@s+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and owner[sy,sx] and source[sy,sx,3]>0:paint[y,x]=source[sy,sx];xy[y,x]=[sx,sy];acc[y,x]=True
 return paint,xy,acc
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output required';out.mkdir(parents=True)
 if hasattr(os,'sched_setaffinity'):os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
 for d in ['controls','source-map','editor']:(out/d).mkdir()
 source={i:a(f'inputs/control/{i:02}.png') for i in [2,3]};upper=mask('masks/02-exact-upper-armcuffs-gloves-owner.png');body=source[2].copy();body[~upper]=0;mapped=body.copy();recipe=json.loads((R/'RECIPE.json').read_text());paths={'Q-proximal':'masks/03-Q-proximal-trousers-source.png','P-retreating':'masks/02-P-complete-leg-source.png','Q-cuff-heel-toe':'masks/03-Q-cuff-boot-source.png'}
 for c in recipe['parts']:
  n=f'{c["id"]}-{c["name"]}';src=source[c['source_phase']];z=np.load(R/'maps'/f'{n}.npz');part=np.zeros_like(body);assert int(z['source_phase'])==c['source_phase']
  for y,x in np.argwhere(z['owner']):sx,sy=z['source_xy'][y,x];part[y,x]=src[sy,sx]
  drawn,xy,owner=from_controls(src,mask(paths[c['name']]),c);assert np.array_equal(part,drawn);assert np.array_equal(xy,z['source_xy']);assert np.array_equal(owner,z['owner']);assert np.array_equal(part,a(f'layers/{n}.png'));body=over(body,drawn);mapped=over(mapped,part)
 body[upper]=source[2][upper];mapped[upper]=source[2][upper];expected=a('candidate/02.5.png');assert np.array_equal(body,expected) and np.array_equal(mapped,expected);assert np.array_equal(expected[upper],source[2][upper])
 initial=json.loads((R/'projects/initial.json').read_text());j=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,j);final=json.loads((R/'projects/final.json').read_text());assert len(j['receipts'])==1;finalhash=project_hash(h.project);assert finalhash==project_hash(final);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
 coords=[[int(x),int(y)] for y,x in np.argwhere(np.any(expected!=source[2],axis=-1))];tx=candidate_transaction(initial,'brann-se-02.5',Image.fromarray(expected),coords,reason='staleguardprobe');stale_rejected=False
 try:h.apply(tx)
 except Exception:stale_rejected=True
 assert stale_rejected and project_hash(h.project)==finalhash
 bad=Image.fromarray(expected);bad.putpixel((0,0),(1,1,1,255));outside_rejected=False
 try:candidate_transaction(h.project,'brann-se-02.5',bad,coords,reason='outsideownerprobe')
 except Exception:outside_rejected=True
 assert outside_rejected and project_hash(h.project)==finalhash
 t=json.loads((R/'TIMING.json').read_text());spec=json.loads((R/'ROOT-REVIEW-SPEC.json').read_text());assert len(spec['frames'])==9;assert sum(Fraction(*f['hold']) for f in spec['frames'])==Fraction(9,20);clock=0;starts={};rows=[]
 for n,hold,f in zip(t['order'],t['hold_ticks'],spec['frames']):
  assert f=={'file':f'candidate/{n}.png','hold':[hold,320]};starts[n]=clock;clock+=hold;wanted=a(f'candidate/{n}.png');edited=render_cel(h.project,f'brann-se-{n}');assert edited.tobytes()==wanted.tobytes()
  if n=='02.5':Image.fromarray(body).save(out/'controls'/f'{n}.png');Image.fromarray(mapped).save(out/'source-map'/f'{n}.png')
  else:
   assert (R/'candidate'/f'{n}.png').read_bytes()==(R/'inputs/control'/f'{n}.png').read_bytes();shutil.copy2(R/'inputs/control'/f'{n}.png',out/'controls'/f'{n}.png');shutil.copy2(R/'inputs/control'/f'{n}.png',out/'source-map'/f'{n}.png')
  edited.save(out/'editor'/f'{n}.png')
  for folder in ['controls','source-map','editor']:assert sha(out/folder/f'{n}.png')==sha(R/'candidate'/f'{n}.png')
  rows.append({'drawing':n,'hold_ticks320':hold,'controls_RGBA_PNG_exact':True,'inverse_source_map_RGBA_PNG_exact':True,'editor_RGBA_PNG_exact':True,'sha256':sha(R/'candidate'/f'{n}.png')})
 assert clock==144 and starts['02.5']==45;assert all(starts[f'{i:02}']==18*i for i in range(8));assert [f['duration_ticks'] for f in h.project['frames']]==t['hold_ticks'];assert h.project['animations'][0]['fps']==320
 receipt={'status':'Frozen one02.5candidate, whole-loopfollowup pending;mechanics notartacceptance','all9_controls_inverse_maps_sourceRGBA_and_editor_RGBA_PNG_exact':True,'original8_PNG_bytes_exact':True,'actual02_upper_armcuffs_gloves_RGBA_exact':True,'all_original8_start_times_exact':True,'02_only_hold_split_ticks320':[9,9],'cycle_ticks320':144,'cycle_seconds':[9,20],'actual_guarded_import_transactions':1,'actual_undo_redo':True,'stale_project_guard_rejected_atomically':True,'outside_midpoint_owner_guard_rejected_atomically':True,'original8_unique_cels_unchanged':True,'midpoint_separate_cel':True,'new_pixels_after_parent_inspection':0,'model_calls':0,'external_artifact_dependencies':[],'ROOT_REVIEW_SPEC_relative_paths_valid':True,'rows':rows};(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
