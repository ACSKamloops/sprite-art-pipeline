from pathlib import Path
from PIL import Image,ImageDraw
import json
OUT=Path(__file__).resolve().parent
exec((OUT/'build_review.py').read_text().split("ledger={'input_hashes'")[0])
e=json.loads((OUT/'EVIDENCE.json').read_text())
for n in ['lyra','brann']:
 out=OUT/n;f=cells(ROOT/'bake-v6'/n/'atlas.png');m=json.loads((ROOT/'bake-v6'/n/'animations.json').read_text())
 js=[(f[j['frame']],f[j['idle']],f"{j['clip']} f{j['frame']}>idle{j['idle']}") for j in e['joins'][n] if not j['pixels_unchanged_v5']]
 pairs(out/'changed-idle-endpoints-2x.png',js,2,2)
 ids=[120,121]+m['animations']['south_walk']['frames'][3:4]+[122,123]+m['animations']['south_walk']['frames'][7:8]+[124,125]+m['animations']['north_walk']['frames'][3:4]+[126,127]+m['animations']['north_walk']['frames'][7:8]
 o=Image.new('RGBA',(6*224,2*190),LIGHT);d=ImageDraw.Draw(o)
 for k,x in enumerate(ids):
  im=f[x].crop((36,78,92,116)).resize((224,152),Image.Resampling.NEAREST);xx=k%6*224;yy=k//6*190;d.text((xx+3,yy+3),f'{n} f{x}',font=FONT,fill='black');o.alpha_composite(comp(im,bg=LIGHT),(xx,yy+25))
 o.convert('RGB').save(out/'lower-negative-spaces-light-4x.png')
 if n=='lyra':
  o=Image.new('RGBA',(4*288,3*244),LIGHT);d=ImageDraw.Draw(o)
  for j,di in enumerate(DIRS):
   ids=m['animations'][di+'_dodge']['frames'][-3:]
   for k,x in enumerate(ids):
    im=f[x].crop((28,12,100,66)).resize((288,216),Image.Resampling.NEAREST);xx=j*288;yy=k*244;d.text((xx+2,yy+2),f'{di} f{x}',font=FONT,fill='black');o.alpha_composite(comp(im,bg=LIGHT),(xx,yy+24))
  o.convert('RGB').save(out/'head-neck-joins-light-4x.png')
print('detail sheets created')
