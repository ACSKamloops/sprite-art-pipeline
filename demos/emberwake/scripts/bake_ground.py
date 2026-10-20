#!/usr/bin/env python3
"""Bake the authored layout and ImageGen tiles into one continuous ground layer.
Removes thousands of alternating texture draws and 12px alpha blocks. Static
contacts/quest rings/effects remain live Godot data. No new semantic image art.
"""
import ast
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/main.gd').read_text()
block=source.split('const ROUTES := ',1)[1].split('\n\nclass ',1)[0]
routes=ast.literal_eval(re.sub(r'Vector2\(([^)]+)\)',r'[\1]',block))
W,H=2304,1728
y,x=np.mgrid[:H,:W].astype(np.float32)
distance=np.full((H,W),1e5,np.float32)
for route in routes:
    for a,b in zip(route,route[1:]):
        ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay
        t=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1)
        d=np.sqrt((x-ax-t*dx)**2+(y-ay-t*dy)**2)
        np.minimum(distance,d,out=distance)
rng=np.random.default_rng(824017)
noise=Image.fromarray((rng.random((54,72))*255).astype(np.uint8)).resize((W,H),Image.Resampling.BICUBIC)
noise=(np.asarray(noise).astype(np.float32)/255-.5)*9
alpha=np.clip((73-distance+np.sin(x*.046)*5+np.cos(y*.051)*5+noise)/26,0,1)
village=np.clip((151-np.sqrt((x-390)**2+(y-1380)**2))/29,0,1)
np.maximum(alpha,village,out=alpha)
# A gently feathered rounded shrine clearing, rather than a tan rectangle.
shrine=np.clip((1-np.sqrt(((x-1900)/214)**2+((y-405)/223)**2))*13,0,1)
np.maximum(alpha,shrine,out=alpha)
alpha=gaussian_filter(alpha,.9)
def tiled(name):
    tile=np.asarray(Image.open(ROOT/f'assets/world/{name}.png').convert('RGB')).astype(np.float32)
    return np.tile(tile,(H//48,W//48,1))
grass=tiled('grass');path=tiled('path');water=tiled('water')
# Quiet foliage beneath character/art; slow coherent variation rather than48px checker shading.
shade=(.87+.06*np.sin(x/279)*np.cos(y/361))[:,:,None]
ground=(grass*(1-alpha[:,:,None])+path*alpha[:,:,None])*shade
for cx,cy,rx,ry in [(325,420,235,133),(1890,1480,228,125)]:
    elliptical=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)
    wet=np.clip((1.01-elliptical)*30,0,1)[:,:,None]
    bank=np.clip((1.08-elliptical)*14,0,1)[:,:,None]
    ground=ground*(1-bank*.30)
    ground=ground*(1-wet)+water*.84*wet
out=ROOT/'assets/world/ground.png'
Image.fromarray(np.clip(ground,0,255).astype(np.uint8)).save(out,optimize=True)
(ROOT/'art-source/GROUND-RECEIPT.json').write_text(json.dumps({'size':[W,H],'source_tiles':{n:hashlib.sha256((ROOT/f'assets/world/{n}.png').read_bytes()).hexdigest() for n in ['grass','path','water']},'routes':routes,'transform':'Continuous per-pixel segmentdistance; varying feathered pathcoverage, pondellipses, restrained coherent shade, no perframe generation.','ground_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'seed':824017},indent=2)+'\n')
print('Ground baked2304x1728 continuous raster from actual ImageGen tiles.')
