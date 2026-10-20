"""Fresh-output replay of retained source construction, raw registration and guarded editor journal.
No generation call, credential, canonical checkout or outside artwork is used.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_dilation
from sprite_lab import History,project_hash,render_cel,load_json
ROOT=Path(__file__).resolve().parents[1]
def arr(n):return np.array(Image.open(ROOT/n).convert('RGBA'))
def mask(n):return np.array(Image.open(ROOT/n).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def same(a,b,msg):assert np.array_equal(a,b),msg
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output path required';out.mkdir(parents=True)
 for n in ['constructed','journal-replay','source-guide']:(out/n).mkdir()
 intake=load_json((ROOT/'INTAKE.json').read_text())
 for row in intake['inputs']:
  path=ROOT/row['file'];assert sha(path)==row['sha256'],f'Changed input {row["file"]}'
 rawreceipt=load_json((ROOT/'generation/RAW-RECEIPT.json').read_text());assert sha(ROOT/'generation/raw.png')==rawreceipt['raw_sha256']
 base=arr('inputs/A/07.png');donor=arr('inputs/A/06.png');repair=mask('masks/07-lower-repair-owner.png');torso=mask('masks/07-stable-upper-hem-owner.png');arm=mask('masks/07-complete-old-part-arm-owner.png');opaque=mask('masks/07-opaque-gloves-protected.png');negative=arm&~opaque
 # Replay the saved integer source map, independently of triangulation versions or the authored recipe.
 frozen=np.load(ROOT/'guide/source06-lower-map.npz',allow_pickle=False);guide=base.copy();guide[repair]=0;source_count={}
 for sid,source in [(1,donor),(2,donor),(3,base)]:
  owned=frozen['source_id']==sid;source_count[str(sid)]=int(owned.sum())
  for y,x in np.argwhere(owned):
   sx,sy=map(int,frozen['source_xy'][y,x]);assert 0<=sx<128 and 0<=sy<128;guide[y,x]=source[sy,sx]
 guide[torso|opaque]=base[torso|opaque];same(guide,arr('guide/proposed07.png'),'Source-part guide replay');Image.fromarray(guide).save(out/'source-guide/proposed07.png')
 # Recompute the declared raw alpha owner, then apply exactly one full-stage nearest transform.
 raw=arr('generation/raw.png');assert list(Image.fromarray(raw).size)==rawreceipt['actual_raw_dimensions'];labels,n=label(raw[...,3]>16,np.ones((3,3)));counts=np.bincount(labels.ravel());counts[0]=0;keep=binary_dilation(labels==int(counts.argmax()),iterations=1)&(raw[...,3]>0);same(keep,mask('masks/raw-actor-owner.png'),'Raw owner changed')
 clean=raw.copy();clean[~keep]=0;g=np.array(Image.fromarray(clean).resize((128,128),Image.Resampling.NEAREST));g[g[...,3]==0]=0;same(g,arr('generation/registered07.png'),'Single raw registration')
 Y,X=np.indices((128,128));rf,gf,bf=[g[...,k].astype(float) for k in range(3)];cream=(g[...,3]>0)&(rf>70)&(gf>.70*rf)&(bf>.63*gf);behind=negative&repair&cream&(Y>=80)&(X>=47)&(X<=84);same(behind,mask('masks/07-generated-body-behind-glove.png'),'Behind-glove underpaint owner changed')
 rebuilt=base.copy();rebuilt[repair]=0;rebuilt[repair]=g[repair];rebuilt[negative&repair]=0;rebuilt[behind]=g[behind];rebuilt[opaque]=base[opaque];rebuilt[torso]=base[torso];rebuilt[rebuilt[...,3]==0]=0
 same(rebuilt[~repair],base[~repair],'Outside lower repair');same(rebuilt[torso],base[torso],'Stable upper/hem');same(rebuilt[opaque],base[opaque],'Whole original visible gloves')
 rawmap=np.load(ROOT/'maps/07-raw-source.npz',allow_pickle=False);coord=np.floor((np.arange(128)+.5)*raw.shape[0]/128).astype(int)
 for y,x in np.argwhere(rawmap['generated_owner']):
  sx,sy=map(int,rawmap['raw_source_xy'][y,x]);assert [sx,sy]==[int(coord[x]),int(coord[y])];same(rebuilt[y,x],g[y,x],'Raw-source coordinate witness')
 initial=load_json((ROOT/'projects/initial.json').read_text());journal=load_json((ROOT/'projects/journal.json').read_text());h=History.replay(initial,journal);final=load_json((ROOT/'projects/final.json').read_text());assert project_hash(h.project)==project_hash(final)
 rows=[]
 for i in range(8):
  expected=arr(f'trial/{i:02}.png');constructed=rebuilt if i==7 else arr(f'inputs/A/{i:02}.png');journal_pixels=np.array(render_cel(h.project,f'rowan-se-{i:02}'));same(constructed,expected,f'Raw construction phase{i}');same(journal_pixels,expected,f'Journal phase{i}')
  if i==7:Image.fromarray(constructed).save(out/'constructed'/f'{i:02}.png')
  else:shutil.copy2(ROOT/'inputs/A'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
  Image.fromarray(journal_pixels).save(out/'journal-replay'/f'{i:02}.png')
  rows.append({'phase':i,'raw_construction_RGBA_exact':True,'journal_RGBA_exact':True,'raw_construction_PNG_bytes_exact':sha(out/'constructed'/f'{i:02}.png')==sha(ROOT/'trial'/f'{i:02}.png'),'journal_PNG_bytes_exact':sha(out/'journal-replay'/f'{i:02}.png')==sha(ROOT/'trial'/f'{i:02}.png'),'trial_sha256':sha(ROOT/'trial'/f'{i:02}.png'),'hold':[9,160]})
 finalhash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
 receipt={'status':'PASS retained-input source construction, raw construction and guarded journal replay','external_artwork_dependencies':[],'generation_calls_during_replay':0,'actual_guarded_transactions':len(journal['receipts']),'actual_undo_redo':True,'source_part_guide_RGBA_exact':True,'source_part_pixels_by_map_id':source_count,'registered_raw_RGBA_exact':True,'all8_raw_construction_RGBA_exact':True,'all8_journal_RGBA_exact':True,'frames':rows,'stage':[128,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'external_editor_GUI_tested':False,'game_runtime_tested':False,'art_quality_approval':'separate parent review'}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
