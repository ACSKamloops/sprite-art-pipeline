"""Actual rendered boot byte/palette tests; not fullactor/gait or art acceptance."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import Delaunay
import build as b
P=b.P;out=P/'artifacts/surface-v2';packet=json.loads((P/'source/poses.json').read_text());texture=np.array(Image.open(P/'source/leg-master-128.png').convert('RGBA'));cam=np.array(packet['camera']['matrix_2x3']);groups={};bounds={};features={}
for f in packet['frames']:
 for n,surface in b.BIND.items():
  tris=Delaunay(np.array([v[0]for v in surface])).simplices.tolist()
  im,world,xy=b.render(surface,tris,texture,f['legs'][n],cam,np.array([0,0]));key=f"{n}/episode{f['legs'][n]['foot']['episode']}"
  if f['legs'][n]['foot']['role']=='flat':groups.setdefault(key,[]).append(hashlib.sha256(im.tobytes()).hexdigest())
  bbox=im.getbbox();assert bbox and bbox[0]>=0 and bbox[1]>=0 and bbox[2]<=256 and bbox[3]<=256
  bounds.setdefault(n,[]).append([bbox[2]-bbox[0],bbox[3]-bbox[1]])
  # Source-owned corner vertices have declared source-alpha validity, no invented marker dots.
  features[n]=[{'uv':v[0],'source_RGBA':texture[int(v[0][1]),int(v[0][0])].tolist(),'local_world':v[1]}for v in surface[-4:]]
report={'scope':'direct actual UV-mesh raster at fixed worldcamera; not heldbaked Sprite2D/rootround proof or art acceptance','flat_world_RGBA_unique_counts':{k:len(set(v))for k,v in groups.items()},'rendered_dimensions':{k:{'min_width':min(x[0]for x in v),'max_width':max(x[0]for x in v),'min_height':min(x[1]for x in v),'max_height':max(x[1]for x in v)}for k,v in bounds.items()},'source_sole_vertices':features,'bindings':{'renderer':b.sha(P/'build.py'),'binding':b.sha(P/'binding.json'),'source':b.sha(P/'source/leg-master-128.png'),'pose_packet':b.sha(P/'source/poses.json')}}
(out/'rendered-material-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
