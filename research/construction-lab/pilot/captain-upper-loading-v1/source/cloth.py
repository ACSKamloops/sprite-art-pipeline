"""Source-owned cloth lag in a cyclic authored pose packet. No gait/art approval."""
import math
import numpy as np
from PIL import Image


def sample_parent(packet,phase,cfg,parent):
    """Interpolate world parent through wrap; preserves cycle translation."""
    count=len(packet['frames']);whole=math.floor(phase);u=(phase-whole)*count;i=math.floor(u);t=u-i
    a=packet['frames'][i%count];b=packet['frames'][(i+1)%count]
    stride=np.array(packet['camera']['matrix_2x3'])@np.array(packet['dimensions']['stride_world'])
    pa=np.array(a['upper_pixels'][parent])+whole*stride
    pb=np.array(b['upper_pixels'][parent])+(whole+(i+1==count))*stride
    offset=np.zeros(2)
    if parent=='chest':
        bind=packet['neutral_bind']['upper_pixels']
        offset=np.array(cfg['chest_hinge'])-cfg['pelvis_rest']-(np.array(bind['chest'])-bind['pelvis'])
    return (1-t)*pa+t*pb+offset,(1-t)*a['chest_counterrotation_degrees']+t*b['chest_counterrotation_degrees']


def render(source,packet,index,cfg,parent='chest',hinge_y=103,lag_cycles=.10):
    """Inverse NEAREST row warp; top fixed to current parent, hem trails world parent.

    Fixed per-source y profile, same lag for the entire sequence. No per-frame
    landmark fitting, new colours, palette mixing or frame-specific redraw.
    """
    f=packet['frames'][index];phase=f['phase'];root=np.array(f['physical_root_pixels'])
    now,angle=sample_parent(packet,phase,cfg,parent)
    pivot=np.array(cfg['chest_hinge'] if parent=='chest' else cfg['pelvis_rest'])
    if parent=='pelvis':angle=0
    rad=math.radians(angle);rot=np.array([[math.cos(rad),-math.sin(rad)],[math.sin(rad),math.cos(rad)]])
    src=np.array(source.convert('RGBA'));box=source.getbbox();bottom=box[3]-1
    rows=[]
    for y in range(256):
        w=np.clip((y-hinge_y)/max(1,bottom-hinge_y),0,1);w=w*w*(3-2*w)
        past,_=sample_parent(packet,phase-lag_cycles*w,cfg,parent)
        rows.append(past-now)
    rows=np.asarray(rows)
    yy,xx=np.mgrid[:256,:256];dst=np.stack([xx,yy],axis=-1).astype(float)
    # Fixed-point inverse: lag is selected by source row; bounded displacement.
    uv=(dst-(now-root))@rot+pivot
    for _ in range(4):
        shift=rows[np.clip(np.rint(uv[:,:,1]),0,255).astype(int)]
        uv=(dst-(now-root)-shift)@rot+pivot
    inds=np.rint(uv).astype(int);valid=(inds[:,:,0]>=0)&(inds[:,:,0]<256)&(inds[:,:,1]>=0)&(inds[:,:,1]<256)
    out=np.zeros_like(src);out[valid]=src[inds[:,:,1][valid],inds[:,:,0][valid]]
    return Image.fromarray(out),{'parent':parent,'hinge_y':hinge_y,'lag_cycles':lag_cycles,'max_world_hem_offset':float(np.linalg.norm(rows,axis=1).max()),'new_colors':False,'loop_policy':'previous world parent with canonical stride through wrap'}
