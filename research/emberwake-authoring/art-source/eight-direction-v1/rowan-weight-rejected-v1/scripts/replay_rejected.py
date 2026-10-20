"""Reproduce the frozen REJECTED curve from local maps into a fresh folder."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parents[1];R=Q/'sourcefield-probe-v1'
def a(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args();out=args.output.resolve();assert not out.exists(),'Fresh output required'
inputs=json.loads((Q/'INPUTS.json').read_text())
for v in inputs:assert sha(Q/v['local'])==v['sha256']
frames=[]
for i in range(8):
 src=a(Q/f'inputs/current/{i:02}.png');body=np.array(Image.open(R/f'masks/{i:02}-body-source-owner.png'))>0;mutable=np.array(Image.open(R/f'masks/{i:02}-mutable-cloth.png'))>0
 composed=src.copy();composed[body|mutable]=0
 assert np.array_equal(composed,a(R/f'layers/{i:02}-fixed-lower.png'))
 for name in ['left-cloth','right-cloth','body']:
  data=np.load(R/f'maps/{i:02}-{name}.npz');layer=np.zeros_like(src)
  for y,x in np.argwhere(data['owner']):sx,sy=data['source_xy'][y,x];layer[y,x]=src[sy,sx]
  layerpath=R/f'layers/{i:02}-{name.replace("-cloth","-mapped-cloth") if name!="body" else "body-rigid"}.png';assert np.array_equal(layer,a(layerpath))
  use=layer[...,3]>0;composed[use]=layer[use]
 assert np.array_equal(composed,a(R/f'frames/{i:02}.png'));frames.append(composed)
out.mkdir(parents=True)
rows=[]
for i,frame in enumerate(frames):
 path=out/f'{i:02}.png';Image.fromarray(frame).save(path);assert sha(path)==sha(R/f'frames/{i:02}.png');rows.append({'phase':i,'sha256':sha(path),'RGBA_and_PNG_bytes_exact':True})
(out/'REPLAY-RECEIPT.json').write_text(json.dumps({'status':'PASS exact rejected construction replay; no art approval','canonical_dependencies':[],'rows':rows},indent=2)+'\n')
print('8/8 rejected sourcefield PNGs exact')
