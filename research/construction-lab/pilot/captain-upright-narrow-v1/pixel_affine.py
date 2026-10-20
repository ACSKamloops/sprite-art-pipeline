"""Fixed-canvas pixel affine experiment, not a full RotSprite implementation.

Scale2x rule reference: https://www.scale2x.it/algorithm
Only existing RGBA tuples are selected. No palette interpolation or fitting.
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image


def scale2x(im):
    e=np.array(im.convert('RGBA')); padded=np.pad(e,((1,1),(1,1),(0,0)),mode='edge')
    b=padded[:-2,1:-1];d=padded[1:-1,:-2];f=padded[1:-1,2:];h=padded[2:,1:-1]
    equal=lambda a,b:np.all(a==b,axis=2)
    active=~equal(b,h)&~equal(d,f)
    out=np.empty((e.shape[0]*2,e.shape[1]*2,4),dtype=np.uint8)
    for oy,ox,a,c in [(0,0,d,b),(0,1,b,f),(1,0,d,h),(1,1,h,f)]:
        out[oy::2,ox::2]=np.where((active&equal(a,c))[...,None],a,e)
    return Image.fromarray(out)


@lru_cache(maxsize=32)
def expanded(size,rgba):
    im=Image.frombytes('RGBA',size,rgba)
    for _ in range(3):im=scale2x(im)
    return im


def affine(im,origin,target,angle,shear=0):
    """Clockwise rigid carry after source-space cloth shear about origin."""
    factor=8;hi=expanded(im.size,im.tobytes())
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    ox,oy=(v*factor for v in origin);tx,ty=(v*factor for v in target)
    # Inverse R then inverse source shear y'=y+shear*(x-ox).
    matrix=(c,s,ox-c*tx-s*ty,
            -s-shear*c,c-shear*s,oy+(s+shear*c)*tx-(c-shear*s)*ty)
    return hi.transform(hi.size,Image.Transform.AFFINE,matrix,
        resample=Image.Resampling.NEAREST,fillcolor=(0,0,0,0)).resize(im.size,Image.Resampling.NEAREST)
