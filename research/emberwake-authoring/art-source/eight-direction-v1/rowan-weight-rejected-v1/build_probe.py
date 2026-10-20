from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw
Q=Path(__file__).resolve().parent
spec=json.loads((Q/'LITERAL-CLOTH-ROWS.json').read_text());adds=json.loads((Q/'body_additions.json').read_text());D=[1,-1,-2,0]*2
out=Q/'sourcefield-probe-v1';out.mkdir(exist_ok=False)
for n in ['frames','maps','layers','masks','proof']:(out/n).mkdir()
def a(path):return np.array(Image.open(path).convert('RGBA'))
def m(path):return np.array(Image.open(path).convert('L'))>0
def save(p,v):Image.fromarray(v).save(out/p)
records=[]
for i,dy in enumerate(D):
 src=a(Q/f'inputs/current/{i:02}.png');body=m(Q/f'masks/{i:02}-body-source-owner.png')
 for y,runs in adds[str(i)].items():
  for x0,x1 in runs:body[int(y),x0:x1+1]=src[int(y),x0:x1+1,3]>0
 rigid=np.zeros_like(src);bxy=np.full((128,128,2),-1,np.int16)
 for y,x in np.argwhere(body):rigid[y+dy,x]=src[y,x];bxy[y+dy,x]=[x,y]
 cloths=[];mutable=np.zeros((128,128),bool);colrecords=[]
 for name in ['left','right']:
  core=m(Q/f'masks/{i:02}-{name}-literal-cloth.png')&~body
  layer=np.zeros_like(src);xy=np.full((128,128,2),-1,np.int16);owner=np.zeros((128,128),bool)
  for x in range(128):
   ys=np.where(core[:,x])[0]
   if len(ys)<3:continue
   first=int(ys.min());end=int(ys[-2]);last=int(ys[-1]);sourceSpan=end-first
   if sourceSpan<=0 or sourceSpan-dy<=0:continue
   # Complete source cloth top follows current rigid coat; last two real
   # source cloth samples are the fixed per-column terminal plateau.
   mutable[:,x]|=core[:,x]&(np.arange(128)<end)
   for y in range(max(0,first+dy),end):
    sy=int(math.floor(first+(y-first-dy)*sourceSpan/(sourceSpan-dy)+.5))
    if 0<=sy<128 and core[sy,x]:layer[y,x]=src[sy,x];xy[y,x]=[x,sy];owner[y,x]=1
   colrecords.append({'part':name,'x':x,'first_source_cloth_y':first,'fixed_plateau_start_y':end,'last_source_cloth_y':last,'slope':(sourceSpan-dy)/sourceSpan})
  cloths.append(layer);save(f'layers/{i:02}-{name}-mapped-cloth.png',layer);save(f'masks/{i:02}-{name}-literal-cloth.png',core.astype('uint8')*255);np.savez_compressed(out/f'maps/{i:02}-{name}-cloth.npz',source_xy=xy,owner=owner)
 fixed=src.copy();fixed[body|mutable]=0;composed=fixed.copy()
 for layer in cloths+[rigid]:
  use=layer[...,3]>0;composed[use]=layer[use]
 save(f'frames/{i:02}.png',composed);save(f'layers/{i:02}-fixed-lower.png',fixed);save(f'layers/{i:02}-body-rigid.png',rigid);save(f'masks/{i:02}-body-source-owner.png',body.astype('uint8')*255);save(f'masks/{i:02}-mutable-cloth.png',mutable.astype('uint8')*255);np.savez_compressed(out/f'maps/{i:02}-body.npz',source_xy=bxy,owner=rigid[...,3]>0)
 holes=[{'at':[int(x),int(y)],'before_rgba':src[y,x].tolist(),'old_owner':'body'if body[y,x]else'cloth'}for y,x in np.argwhere((src[...,3]>0)&(composed[...,3]==0)&(np.indices((128,128))[0]>=76))]
 overlap=[{'at':[int(x),int(y)],'foreground_source_at':bxy[y,x].tolist(),'foreground_rgba':rigid[y,x].tolist(),'fixed_rgba':fixed[y,x].tolist()}for y,x in np.argwhere((fixed[...,3]>0)&(rigid[...,3]>0)&np.any(src!=composed,axis=2))]
 records.append({'phase':i,'dy':dy,'columns':colrecords,'new_clear_y76plus':holes,'body_over_fixed':overlap,'changed_pixels':int(np.any(src!=composed,axis=2).sum()),'rigid_body_source_RGBA_exact':True,'fixed_layer_preserves_all_original_its_owned_pixels':True})
for size,tag in [(128,'native'),(256,'2x'),(84,'84')]:
 for bg,label in [('#e9e4d7','light'),('#1d222b','dark'),('#344c32','forest')]:
  board=Image.new('RGBA',(8*size,2*(size+20)),bg);dr=ImageDraw.Draw(board)
  for row,bank in enumerate([Q/'inputs/current',out/'frames']):
   for i in range(8):
    board.alpha_composite(Image.open(bank/f'{i:02}.png').resize((size,size),Image.Resampling.NEAREST),(size*i,row*(size+20)+20));dr.text((size*i+2,row*(size+20)+2),f'{"current"if row==0 else"PROBE"} {i:02}',fill='white'if label!='light'else'black')
  board.convert('RGB').save(out/f'proof/full8-{tag}-{label}.png')
(out/'CONSTRUCTION-RECEIPT.json').write_text(json.dumps({'status':'unreviewed single source-field construction probe; never selected','curve':[1,0,-1,0]*2,'corrections':D,'clock':{'hold':[9,160],'cycle':[9,20]},'phases':records,'newpaint':0},indent=2)+'\n')
print([(v['phase'],len(v['new_clear_y76plus']),len(v['body_over_fixed']),v['changed_pixels'])for v in records])
