"""Validate actual proxy rasters/material colors; no artistic acceptance."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import build as b,proxy
P=b.P;out=P/'artifacts/proxy-v2';d=json.loads((out/'manifest.json').read_text());packet=json.loads((P/'source/poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);palette={tuple(c)for c in np.array(Image.open(P/'source/leg-master-128.png')).reshape(-1,4) if c[3]};groups={};newcolors=0;alphas=set();dims={};world_contact={}
for f,r in zip(packet['frames'],d['records']):
 for n in ['far','near']:
  texture=np.array(Image.open(out/f'{n}-edge-extended-UV.png'));surface,tris=proxy.surface(n);im,world,xy=b.render(surface,tris,texture,f['legs'][n],cam,np.zeros(2));arr=np.array(im);alphas.update(arr[:,:,3].reshape(-1).tolist());newcolors+=sum(tuple(c)not in palette for c in arr.reshape(-1,4) if c[3]);bbox=im.getbbox();assert bbox;dims.setdefault(n,[]).append([bbox[2]-bbox[0],bbox[3]-bbox[1]])
  if f['legs'][n]['foot']['role']=='flat':groups.setdefault(n,[]).append(hashlib.sha256(im.tobytes()).hexdigest())
assert newcolors==0 and alphas=={0,255}
assert all(len(set(v))==1 for v in groups.values())
report={'scope':'actual direct 3D proxy raster at one fixed worldcamera; does not validate independently held Sprite2D frames, fullactor contact or game art','flat_RGBA_unique_counts':{k:len(set(v))for k,v in groups.items()},'new_opaque_RGBA_colors':newcolors,'alpha_values':sorted(alphas),'dimensions':{n:{'min':[min(x[k]for x in v)for k in [0,1]],'max':[max(x[k]for x in v)for k in [0,1]]}for n,v in dims.items()},'inputs':{str(p.relative_to(P)):b.sha(p)for p in [P/'build.py',P/'proxy.py',P/'binding.json',P/'source/leg-master-128.png',P/'source/poses.json']}}
(out/'rendered-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
