#!/usr/bin/env python3
"""Reconstruct the16 actual authority cels from retained generated raw/baseline."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('output');args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);results=[]
for actor in ('lyra','rowan'):
 for view in ('southeast','northeast'):
  dst=out/actor/view;dst.mkdir(parents=True);n=2 if view=='southeast' else 3
  raw=Image.open(ROOT/'generation'/actor/view/'raw.png').convert('RGBA').resize((128*n,128),Image.Resampling.NEAREST);a=np.array(raw);a[a[:,:,3]<24]=0;a[:,:,3][a[:,:,3]>245]=255;a[a[:,:,3]==0,:3]=0
  for phase in (0,2,4,6):
   if phase==0:im=Image.open(ROOT/'baseline'/actor/view/'00.png')
   elif phase==6 and view=='southeast':im=Image.open(ROOT/'baseline'/actor/view/'02.png')
   else:im=Image.fromarray(a[:,128*({2:0,4:1,6:2}[phase]):128*({2:0,4:1,6:2}[phase]+1)])
   p=dst/f'{phase:02d}.png';im.save(p);expected=ROOT/'authorities'/actor/view/f'{phase:02d}.png';assert np.array_equal(np.array(Image.open(p).convert('RGBA')),np.array(Image.open(expected).convert('RGBA'))),(actor,view,phase)
   results.append({'actor':actor,'view':view,'phase':phase,'same_rgba':True,'same_png_bytes':p.read_bytes()==expected.read_bytes()})
print(json.dumps({'raw_derived_authorities':len(results),'all_rgba_equal':True,'all_png_bytes_equal':all(r['same_png_bytes'] for r in results)}))
