from pathlib import Path
import json,sys,argparse,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import History,render_frame,project_hash

def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p))>0
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype('uint8')
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
if a.output:
 assert a.output.is_absolute()and not a.output.exists(),'output must be fresh absolute path';a.output.mkdir(parents=True)
recipe=json.loads((ROOT/'RECIPE.json').read_text());guide=json.loads((ROOT/'inputs/guide04-recipe.json').read_text());initial=json.loads((ROOT/'initial-project.json').read_text());target=json.loads((ROOT/'project.json').read_text());journal=json.loads((ROOT/'journal.json').read_text());history=History.replay(initial,journal);assert project_hash(history.project)==project_hash(target)
source=[arr(ROOT/'inputs/v5-frames'/f'{i:02}.png')for i in range(8)];yy,xx=np.mgrid[:128,:128];results=[]
for i in range(8):
 assert sha(ROOT/'inputs/v5-frames'/f'{i:02}.png')==recipe['source_hashes'][f'{i:02}']
 layers={n:np.zeros_like(source[i])for n in ['base','cloth','rear','proximal','front']};layers['base']=source[i].copy()
 if i in [3,4,5]:
  upper=yy<=85
  for n in ['sleeve','far','near','fixed']:upper|=arr(ROOT/'inputs/v5-layers'/f'{i:02}-{n}.png')[:,:,3]>0
  upper|=poly([(69,84),(74,84),(74,86),(69,86)])&(source[i][:,:,3]>0)
  assert np.array_equal(upper,mask(ROOT/'masks'/f'{i:02}-whole-upper.png'));layers['base'][~upper]=0
  r=guide if i==4 else recipe['frames'][f'{i:02}'];witnesses=r['literal_trouser_source_witnesses']if i==4 else r['literal_cloth_witnesses'];boots=r['boot_sources']if i==4 else r['parts_in_back_to_front_order']
  for w in witnesses:
   x,y=w['destination'];sx,sy=w['source'];sp=w.get('source_phase',0);c=source[sp][sy,sx];assert c.tolist()==w['RGBA'];name='proximal'if w['role'].startswith('literal rounded rear-thigh')else'cloth';layers[name][y,x]=c;assert not upper[y,x]
  for b,name in zip(boots,['rear','front']):
   path=ROOT/'maps'/f'{i:02}-{b["id"]}.npz';data=np.load(path);xy=data['source_xy'];own=xy[:,:,0]>=0;sp=b['source_phase'];raw=np.zeros_like(source[i]);ys,xs=np.where(own);raw[ys,xs]=source[sp][xy[ys,xs,1],xy[ys,xs,0]]
   # Recompute complete inverse transform from declared one-part parameters;
   # equality prevents a fitted XY map from masquerading as the recipe.
   if 'translation'in b:sxmap=xx-b['translation'][0];symap=yy-b['translation'][1]
   else:
    pr=b['projection'];num,den=pr['y_scale'];sxmap=xx-pr['x_translation'];symap=np.floor((yy-pr['target_y_anchor'])*den/num+pr['source_y_anchor']+.5).astype('int16')
   valid=(sxmap>=0)&(sxmap<128)&(symap>=0)&(symap<128);source_owner=poly(b['polygon']);valid&=source_owner[np.clip(symap,0,127),np.clip(sxmap,0,127)]
   assert np.array_equal(valid,own);assert np.array_equal(xy[own],np.stack([sxmap,symap],axis=-1)[own])
   raw[upper]=0;layers[name]=raw
 expected=np.zeros_like(source[i])
 for n,part in layers.items():
  assert np.array_equal(part,arr(ROOT/'layers'/f'editor-{i:02}-{n}.png'));expected=over(expected,part)
 actual=arr(ROOT/'frames'/f'{i:02}.png');assert np.array_equal(expected,actual);assert render_frame(history.project,f'f{i}').tobytes()==Image.fromarray(expected).tobytes();assert render_frame(initial,f'f{i}').tobytes()==Image.fromarray(source[i]).tobytes()
 if i in [3,4,5]:assert np.array_equal(actual[upper],source[i][upper])
 else:assert sha(ROOT/'frames'/f'{i:02}.png')==sha(ROOT/'inputs/v5-frames'/f'{i:02}.png')
 assert target['frames'][i]['duration_ticks']==9
 if a.output:Image.fromarray(expected).save(a.output/f'{i:02}.png');assert sha(a.output/f'{i:02}.png')==sha(ROOT/'frames'/f'{i:02}.png')
 results.append({'phase':i,'PNG_sha256':sha(ROOT/'frames'/f'{i:02}.png'),'raw_source_map_literal_join_recipe_exact':True,'full_v5_upper_and_arms_exact':True,'changed_RGBA_pixels':int(np.any(actual!=source[i],axis=2).sum())})
final=project_hash(history.project)
for _ in range(len(history.records)):history.undo()
assert project_hash(history.project)==project_hash(initial)
for _ in range(len(history.records)):history.redo()
assert project_hash(history.project)==final;assert target['animations'][0]['fps']==160
receipt={'project_sha256':final,'frames':results,'editor_transactions':len(history.records),'source_layer_PNG_and_guarded_editor_replay_exact':True,'undo_redo_exact':True,'clock':'8x9/160 seconds=.45 second loop','03_projection_vertical':[5,6],'03_unscaled_source_perfect':False,'status':'unselected candidate; no physical contact claim or acceptance'}
if a.output:(a.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS8/8 raw source maps, declared transforms, literal joins, layer/PNG/editor RGBA, endpoints/upper, clock, guarded replay and undo/redo.')
