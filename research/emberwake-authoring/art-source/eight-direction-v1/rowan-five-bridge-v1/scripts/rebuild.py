"""Deterministic fresh-output single-raw construction and independent toolkit journal replay."""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_dilation
from sprite_lab import History,project_hash,render_cel
ROOT=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(ROOT/n).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output path required';out.mkdir(parents=True)
 for n in ['constructed','journal-replay','source-part-replays']:(out/n).mkdir()
 raw_image=Image.open(ROOT/'generation/raw.png').convert('RGBA');raw=np.array(raw_image);assert raw_image.size==(1254,1254)
 cc,n=label(raw[...,3]>16,np.ones((3,3)));counts=np.bincount(cc.ravel());counts[0]=0;keep=binary_dilation(cc==int(counts.argmax()),iterations=1)&(raw[...,3]>0)
 assert np.array_equal(keep,np.array(Image.open(ROOT/'masks/raw-mainbody-owner.png'))>0)
 raw[~keep]=0;g=np.array(Image.fromarray(raw).resize((128,128),Image.Resampling.NEAREST))
 base=a('inputs/A/05.png');oldrepair=np.array(Image.open(ROOT/'inputs/ownership/05-waist-lower-owner.png'))>0
 arm=np.array(Image.open(ROOT/'inputs/ownership/05-complete-gloves-owner.png'))>0
 conf=json.loads((ROOT/'scripts/torso-contour.json').read_text());torso=np.zeros((128,128),bool);torso[:conf['all_stage_rows_through']+1]=True
 for x,y in conf['additional_column_last_protected_y'].items():torso[:int(y)+1,int(x)]=True
 repair=oldrepair&~torso;assert np.array_equal(repair,np.array(Image.open(ROOT/'masks/05-lower-repair-owner.png'))>0)
 assert np.array_equal(torso,np.array(Image.open(ROOT/'masks/05-stable-torso-hem-owner.png'))>0)
 opaque=arm&(base[...,3]>0);negative=arm&~opaque
 # New body paint would be allowed behind an opaque foreground glove only through this literal material mask.
 Y,X=np.indices((128,128));rf,gf,bf=[g[...,k].astype(float) for k in range(3)]
 cream=(g[...,3]>0)&(rf>70)&(gf>0.70*rf)&(bf>0.63*gf)
 behind=negative&repair&cream&(Y>=80)&(X>=47)&(X<=84)
 assert np.array_equal(behind,np.array(Image.open(ROOT/'masks/05-generated-body-behind-glove.png'))>0)
 rebuilt=base.copy();rebuilt[repair]=g[repair];rebuilt[negative&repair]=0;rebuilt[behind]=g[behind];rebuilt[opaque]=base[opaque]
 assert np.array_equal(rebuilt[~repair],base[~repair]);assert np.array_equal(rebuilt[torso],base[torso]);assert np.array_equal(rebuilt[opaque],base[opaque])
 z=np.load(ROOT/'maps/05-raw-source.npz');raw_original=np.array(raw_image)
 for y,x in np.argwhere(z['generated_visible']):
  rx,ry=z['raw_source_xy'][y,x];assert np.array_equal(rebuilt[y,x],raw_original[ry,rx])
 initial=json.loads((ROOT/'projects/initial.json').read_text());journal=json.loads((ROOT/'projects/journal.json').read_text());h=History.replay(initial,journal);expected_project=json.loads((ROOT/'projects/final.json').read_text());assert project_hash(h.project)==project_hash(expected_project)
 rows=[]
 for i in range(8):
  expected=a(f'selected/{i:02}.png');constructed=rebuilt if i==5 else a(f'inputs/A/{i:02}.png');replayed=render_cel(h.project,f'rowan-se-{i:02}')
  assert np.array_equal(constructed,expected),f'raw construction phase{i}';assert replayed.tobytes()==expected.tobytes(),f'journal phase{i}'
  if i==5:Image.fromarray(constructed).save(out/'constructed'/f'{i:02}.png')
  else:shutil.copy2(ROOT/'inputs/A'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
  replayed.save(out/'journal-replay'/f'{i:02}.png')
  rows.append({'phase':i,'raw_construction_RGBA_exact':True,'journal_RGBA_exact':True,'raw_construction_PNG_bytes_exact':sha(out/'constructed'/f'{i:02}.png')==sha(ROOT/'selected'/f'{i:02}.png'),'journal_PNG_bytes_exact':sha(out/'journal-replay'/f'{i:02}.png')==sha(ROOT/'selected'/f'{i:02}.png'),'sha256':sha(ROOT/'selected'/f'{i:02}.png'),'hold':[9,160]})
 final_hash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final_hash
 # Independent frozen-map replay of both preserved source06-part experiments.
 source2=a('inputs/upper/source02.png');arm_masks=[np.array(Image.open(ROOT/'inputs/upper'/f'{n}-arm-owner.png'))>0 for n in ['left','right']];own=np.zeros((128,128),bool);paint=np.zeros_like(base)
 for k,dx in [(0,1),(1,-1)]:
  for y,x in np.argwhere(arm_masks[k]):
   xx,yy=x+dx,y+1
   if 0<=xx<128 and yy<128:own[yy,xx]=1;paint[yy,xx]=source2[y,x]
 experiments=[]
 for name,transparent_restore in [('rejected-transparent-arm-proposal',True),('source-part-placement-guide',False)]:
  folder=ROOT/'experiments'/name;mask=np.array(Image.open(folder/'05-lower-repair-owner.png'))>0;maps=np.load(folder/'05-source-map.npz');im=base.copy();im[mask]=0
  for y,x in np.argwhere(maps['source_id']>=0):
   sid=int(maps['source_id'][y,x]);sx,sy=maps['source_xy'][y,x];im[y,x]=a(f'inputs/A/{sid:02}.png')[sy,sx]
  arm_restore=own if transparent_restore else own&(paint[...,3]>0);im[arm_restore]=paint[arm_restore]
  assert np.array_equal(im,np.array(Image.open(folder/'05.png').convert('RGBA'))),name
  Image.fromarray(im).save(out/'source-part-replays'/f'{name}.png');experiments.append({'name':name,'frozen_map_RGBA_exact':True})
 receipt={'fresh_output':str(out),'retained_inputs_only':True,'external_artifact_dependencies':[],'built_in_calls_during_replay':0,'raw_construction_frames':8,'independent_journal_frames':8,'actual_guarded_transactions':1,'actual_undo_redo':True,'frames':rows,'source_part_experiments':experiments,'cycle':[9,20],'new_generation_calls_total':1}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
