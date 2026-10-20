"""Portable frozen-control construction, source-map and guarded editor replay."""
from pathlib import Path
import argparse,json,hashlib,shutil,os
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def a(p):return np.array(Image.open(R/p).convert('RGBA'))
def mask(p):return np.array(Image.open(R/p))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output required';out.mkdir(parents=True)
 if hasattr(os,'sched_setaffinity'):os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
 for d in ['constructed','source-map-replay','editor-replay']:(out/d).mkdir()
 sources={4:a('inputs/control/04.png'),5:a('inputs/control/05.png')};base=sources[4];lower=mask('masks/lower-repair-owner.png');protected=mask('masks/source-upper-hem-complete-gloves.png');cfg=json.loads((R/'CONSTRUCTION.json').read_text());built=base.copy();built[lower]=0
 sp=np.full((128,128),4,np.int16);y,x=np.indices((128,128));xy=np.stack([x,y],axis=-1).astype(np.int16);sp[lower]=-1;xy[lower]=-1
 own_paths={'rear-surface':'masks/source-rear-whole-surface.png','front-pants':'masks/source-front-pants.png','front-boot':'masks/source-front-whole-boot.png'}
 for c in cfg['parts']:
  source=sources[c['source_phase']];owner=mask(own_paths[c['name']]);src=np.array(c['source_vertices'],float);dst=np.array(c['target_vertices'],float)
  for t in c['triangles']:
   s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
   for yy in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
    for xx in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
     bary=inv@np.array([xx,yy,1.])
     if bary.min()<-1e-8:continue
     sx,sy=np.floor(bary@s+.5).astype(int)
     if 0<=sx<128 and 0<=sy<128 and owner[sy,sx] and source[sy,sx,3]>0 and lower[yy,xx]:built[yy,xx]=source[sy,sx];sp[yy,xx]=c['source_phase'];xy[yy,xx]=[sx,sy]
 expected=a('candidate/04.5.png');assert np.array_equal(built,expected);assert np.array_equal(built[protected],base[protected]);assert np.array_equal(built[~lower],base[~lower])
 saved=np.load(R/'maps/04.5-sources.npz');assert np.array_equal(sp,saved['source_phase']);assert np.array_equal(xy,saved['source_xy']);mapped=np.zeros_like(base)
 for sid,source in sources.items():
  yy,xx=np.where(saved['source_phase']==sid);pos=saved['source_xy'][yy,xx];mapped[yy,xx]=source[pos[:,1],pos[:,0]]
 assert np.array_equal(mapped,expected)
 initial=json.loads((R/'projects/initial.json').read_text());journal=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,journal);final=json.loads((R/'projects/final.json').read_text());assert project_hash(h.project)==project_hash(final);finalhash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
 timing=json.loads((R/'TIMING.json').read_text());order=timing['candidate_order'];holds=timing['candidate_holds'];clock=0;starts={};rows=[]
 for n,hold in zip(order,holds):
  starts[n]=clock;clock+=hold;expected=a(f'candidate/{n}.png');edited=render_cel(h.project,f'rowan-se-{n}');assert edited.tobytes()==expected.tobytes()
  if n=='04.5':Image.fromarray(built).save(out/'constructed'/f'{n}.png');Image.fromarray(mapped).save(out/'source-map-replay'/f'{n}.png')
  else:
   assert (R/f'candidate/{n}.png').read_bytes()==(R/f'inputs/control/{n}.png').read_bytes()
   shutil.copy2(R/f'inputs/control/{n}.png',out/'constructed'/f'{n}.png');shutil.copy2(R/f'inputs/control/{n}.png',out/'source-map-replay'/f'{n}.png')
  edited.save(out/'editor-replay'/f'{n}.png')
  for folder in ['constructed','source-map-replay','editor-replay']:assert sha(out/folder/f'{n}.png')==sha(R/f'candidate/{n}.png')
  rows.append({'exposure':n,'duration_ticks320':hold,'construction_RGBA_PNG_exact':True,'source_map_RGBA_PNG_exact':True,'editor_RGBA_PNG_exact':True,'sha256':sha(R/f'candidate/{n}.png')})
 assert clock==144;assert all(starts[f'{i:02}']==18*i for i in range(8));assert starts['04.5']==81
 assert h.project['animations'][0]['fps']==320;assert [f['duration_ticks'] for f in h.project['frames']]==holds
 receipt={'status':'Reconstruction evidence only; one-midpoint trial has no inherited whole-cycle acceptance.','external_artifact_dependencies':[],'model_calls':0,'new_authored_pixel_colors':0,'all9_control_construction_and_inverse_source_map_and_editor_RGBA_PNG_exact':True,'all_original8_PNG_bytes_exact':True,'actual_guarded_editor_transactions':len(journal['receipts']),'actual_undo_redo':True,'protected_actual04_upper_hem_full2Dgloves_RGBA_exact':True,'outside_lower_owner_RGBA_exact':True,'frozen_source_xy_map_exact':True,'candidate_start_ticks320':starts,'total_ticks320':clock,'cycle_seconds':clock/320,'original8_starts_exact':True,'04_only_hold_split':[9,9],'other_original_holds_ticks320':18,'rows':rows,'midpoint_sha256':sha(R/'candidate/04.5.png')}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
