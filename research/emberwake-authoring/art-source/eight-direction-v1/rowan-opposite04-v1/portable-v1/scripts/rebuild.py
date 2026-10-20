"""Fresh-output exact raw construction, actual editor journal replay, and authored-guide replay."""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_dilation
from sprite_lab import History,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def rgba(n):return np.array(Image.open(R/n).convert('RGBA'))
def mask(n):return np.array(Image.open(R/n))>0
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output required';out.mkdir(parents=True)
 for n in ['constructed','journal-replay']:(out/n).mkdir()
 raw=rgba('generation/raw.png');assert raw.shape==(1254,1254,4)
 cc,n=label(raw[...,3]>16,np.ones((3,3)));ct=np.bincount(cc.ravel());ct[0]=0;keep=binary_dilation(cc==int(ct.argmax()),iterations=1)&(raw[...,3]>0)
 assert np.array_equal(keep,mask('masks/raw-mainbody-owner.png'));filtered=raw.copy();filtered[~keep]=0;g=np.array(Image.fromarray(filtered).resize((128,128),Image.Resampling.NEAREST))
 base=rgba('inputs/authority/04.png');owner=mask('inputs/guide/04-new-lower-owner.png');stable=mask('inputs/guide/04-stable-upper-hem-owner.png');arm=mask('inputs/guide/04-complete-old-arm-erase-owner.png');opaque=mask('inputs/guide/04-opaque-glove-foreground-owner.png');negative=arm&~opaque
 assert np.array_equal(owner,mask('masks/04-lower-owner.png'));assert np.array_equal(stable,mask('masks/04-stable-upper-hem-owner.png'))
 body=mask('masks/04-literal-painted-thigh-volume.png');behind=owner&negative&body&(g[...,3]>0);assert np.array_equal(behind,mask('masks/04-generated-body-behind-arm.png'))
 constructed=base.copy();constructed[owner]=0;constructed[owner]=g[owner];constructed[owner&negative]=0;constructed[behind]=g[behind];constructed[opaque]=base[opaque];constructed[stable]=base[stable]
 assert np.array_equal(constructed[~owner],base[~owner]);assert np.array_equal(constructed[stable],base[stable]);assert np.array_equal(constructed[opaque],base[opaque])
 z=np.load(R/'maps/04-raw-source.npz')
 for y,x in np.argwhere(z['generated_visible']):
  rx,ry=z['raw_source_xy'][y,x];assert np.array_equal(constructed[y,x],raw[ry,rx])
 initial=json.loads((R/'projects/initial.json').read_text());journal=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(json.loads((R/'projects/final.json').read_text()))
 rows=[]
 for i in range(8):
  expected=rgba(f'candidate/{i:02}.png');rebuilt=constructed if i==4 else rgba(f'inputs/authority/{i:02}.png');j=render_cel(h.project,f'rowan-se-{i:02}')
  assert np.array_equal(rebuilt,expected);assert j.tobytes()==expected.tobytes()
  if i==4:Image.fromarray(rebuilt).save(out/'constructed'/f'{i:02}.png')
  else:shutil.copy2(R/'inputs/authority'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
  j.save(out/'journal-replay'/f'{i:02}.png')
  rows.append({'phase':i,'raw_RGBA_exact':True,'editor_journal_RGBA_exact':True,'raw_PNG_bytes_exact':sha(out/'constructed'/f'{i:02}.png')==sha(R/'candidate'/f'{i:02}.png'),'editor_PNG_bytes_exact':sha(out/'journal-replay'/f'{i:02}.png')==sha(R/'candidate'/f'{i:02}.png'),'sha256':sha(R/'candidate'/f'{i:02}.png'),'hold':[9,160]})
 final_hash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final_hash
 # Independent authored-guide construction: literal before/after palette strokes, then complete rigid boots.
 guide=base.copy();guide[owner]=0;strokes=json.loads((R/'inputs/guide/AUTHORED-PAINT-JOURNAL.json').read_text())
 for op in strokes['strokes']:
  x,y=op['target'];assert guide[y,x].tolist()==op['before'];donor=rgba(f"inputs/authority/{op['palette_sample']['phase']:02}.png");sx,sy=op['palette_sample']['xy'];assert donor[sy,sx].tolist()==op['after'];guide[y,x]=op['after']
 cfg=json.loads((R/'inputs/guide/CONSTRUCTION.json').read_text())
 for boot in cfg['boot_placements']:
  donor=rgba(f"inputs/authority/{boot['source_phase']:02}.png");m=mask('inputs/donor-masks/'+boot['source_mask']);dx,dy=boot['translation']
  for y,x in np.argwhere(m&(donor[...,3]>0)):guide[y+dy,x+dx]=donor[y,x]
 guide[stable]=base[stable];source2=rgba('inputs/upper/source02.png');guide[opaque]=source2[opaque]
 assert np.array_equal(guide,rgba('inputs/guide/04.png'));gm=np.load(R/'inputs/guide/04-construction-map.npz');assert int(gm['authored_visible'].sum())==276
 Image.fromarray(guide).save(out/'guide04-journal-replay.png')
 receipt={'fresh_output':str(out),'external_artifact_dependencies':[],'model_calls_during_replay':0,'raw_constructed_frames':8,'independent_editor_journal_frames':8,'actual_guarded_editor_transactions':1,'actual_undo_redo':True,'rows':rows,'guide_literal_strokes':len(strokes['strokes']),'guide_RGBA_exact':True,'guide_newly_authored_visible_pants_pixels':276,'new04_generated_composite_authored_pixels':0,'calls_this04_trial':1,'cycle':[9,20]}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
