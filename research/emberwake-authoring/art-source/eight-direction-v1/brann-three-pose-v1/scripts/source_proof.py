from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
recipe=json.loads((ROOT/'RECIPE.json').read_text());guide=json.loads((ROOT/'inputs/guide04-recipe.json').read_text());parts=[]
for i in [3,4,5]:
 boots=guide['boot_sources']if i==4 else recipe['frames'][f'{i:02}']['parts_in_back_to_front_order']
 for b,layer in zip(boots,['rear','front']):
  src=arr(ROOT/'inputs/v5-frames'/f'{b["source_phase"]:02}.png');cut=np.zeros_like(src);own=poly(b['polygon']);cut[own]=src[own];data=np.load(ROOT/'maps'/f'{i:02}-{b["id"]}.npz');xy=data['source_xy'];valid=xy[:,:,0]>=0;ys,xs=np.where(valid);placed=np.zeros_like(src);placed[ys,xs]=src[xy[ys,xs,1],xy[ys,xs,0]];final=arr(ROOT/'layers'/f'editor-{i:02}-{layer}.png');contributes=np.array(Image.open(ROOT/'masks'/f'{i:02}-{b["id"]}-target-visible.png'))>0;final[~contributes]=0;parts.append((i,b,src,cut,placed,final))
for label,s in [('native',128),('066',84)]:
 sh=Image.new('RGBA',(4*s,len(parts)*(s+26)),(233,233,222,255));d=ImageDraw.Draw(sh)
 for row,(i,b,*ims)in enumerate(parts):
  for col,im in enumerate(ims):sh.alpha_composite(Image.fromarray(im).resize((s,s),Image.Resampling.NEAREST),(col*s,row*(s+26)+26))
  d.text((2,row*(s+26)+1),f'{i:02} {b["id"]}; source{b["source_phase"]:02} {b.get("source_position",b.get("source_screen_position"))}',fill='black');d.text((2,row*(s+26)+13),'source / scoped source / full-stage placed / contributing source',fill='black')
 sh.save(ROOT/'proof'/f'actual-source-cutouts-and-placement-{label}.png')
origin=Path('/home/astra/artifacts/emberwake-brann-full-lower-paint-v1/se-near-attachment-v5');rows=[]
for folder,glob in [('v5-frames','*.png'),('v5-layers','*.png')]:
 for p in sorted((ROOT/'inputs'/folder).glob(glob)):
  source=origin/('frames'if folder=='v5-frames'else'layers')/p.name;assert sha(p)==sha(source);rows.append({'source':str(source),'copy':str(p.relative_to(ROOT)),'sha256':sha(p),'source_current_at_freeze_matches':True})
for source,dest in [(Path('/home/astra/artifacts/emberwake-brann-se04-source-part-guide-v1/frames/04.png'),ROOT/'inputs/guide04.png'),(Path('/home/astra/artifacts/emberwake-brann-se04-source-part-guide-v1/GUIDE.json'),ROOT/'inputs/guide04-recipe.json')]:
 assert sha(source)==sha(dest);rows.append({'source':str(source),'copy':str(dest.relative_to(ROOT)),'sha256':sha(dest),'source_current_at_freeze_matches':True})
(ROOT/'INPUTS.json').write_text(json.dumps({'status':'actual source copies hash-checked against read-only source authority at freeze','source_files':rows,'manual_only_model_calls':0},indent=2)+'\n')
print('Actual source/cutout/placed/contribution native/.66 proof and current source authority hashes checked.')
