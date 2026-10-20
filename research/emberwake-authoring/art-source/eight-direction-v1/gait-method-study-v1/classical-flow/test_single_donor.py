#!/usr/bin/env python3
"""Follow-up excludes union-of-silhouettes fill; keeps first failure frozen."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import build as b

r=b.ROOT/'single-donor-v2';r.mkdir(exist_ok=True)
inputs=[np.array(Image.open(b.ROOT/'inputs'/f'{i:02}.png').convert('RGBA')) for i in range(8)]
lanes=[('control',[Image.fromarray(a) for a in inputs])]
records=[]
for method in ('dis','farneback'):
    out=r/method;out.mkdir(exist_ok=True)
    mids=[]
    for i in range(8):
        f=np.load(b.ROOT/'flows'/f'{method}-{i:02}.npz')
        for sub in range(4):
            arr=inputs[i] if sub==0 else b.interpolate(inputs[i],inputs[(i+1)%8],f['ab'],f['ba'],sub/4,'single')
            Image.fromarray(arr).save(out/f'{i*4+sub:02}.png')
            if sub==2:mids.append(Image.fromarray(arr))
    lanes.append((method,mids))
    records.append({'method':method,'source':'existing frozen bidirectional flow fields','mode':'one nearest sampled donor only; no hole fill or alpha blending','frame_count':32,'hold':[9,640]})
for size in (84,128,256):
    for label,bg in [('light',(238,236,226)),('dark',(28,32,40)),('game',(38,62,50))]:
        b.sheet(lanes,size,bg,r/f'midpoints-{size}-{label}.png')
# Meaningful coordinate-convention control: an independent integer-translated
# opaque rectangle with declared constant bidirectional flow has an exact
# half-time displacement. This does not validate estimated flow on anatomy.
a=np.zeros((128,128,4),dtype=np.uint8);a[40:60,30:50]=[190,80,30,255]
bb=np.zeros_like(a);bb[42:62,34:54]=[190,80,30,255]
ab=np.zeros((128,128,2),dtype=np.float32);ab[:]=[4,2]
ba=-ab
expected=np.zeros_like(a);expected[41:61,32:52]=[190,80,30,255]
checks={mode:bool(np.array_equal(b.interpolate(a,bb,ab,ba,.5,mode),expected)) for mode in ('source','single','blend')}
assert all(checks.values()),checks
b.save_json(r/'METHOD.json',{'lanes':records,'inverse_coordinate_control':checks,'qualification':'Known constant flow only validates inverse-map sign and premultiplied combination on matching translated paint, not dense field correctness, foot roles, occlusion or quality.'})
print(json.dumps({'directory':str(r),'inverse_coordinate_control':checks}))
