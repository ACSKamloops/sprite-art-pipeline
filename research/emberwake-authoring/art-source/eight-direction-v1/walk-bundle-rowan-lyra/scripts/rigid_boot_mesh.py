"""One visible same-view leg map with a complete rigid painted boot plateau."""
import numpy as np
from scipy.spatial import Delaunay
from scipy.ndimage import binary_erosion

def make_map(bootmask,sourcehip,targethip,delta,hip_x):
    points={}
    def put(x,y,tx,ty):
        key=(int(x),int(y));value=(float(tx),float(ty))
        if key in points and points[key]!=value:raise ValueError(('conflicting source control',key,points[key],value))
        points[key]=value
    for x,y in ((0,0),(127,0),(127,127),(0,127)):put(x,y,x,y)
    # Preserve body/hip boundary while allowing the visible attached pants to deform.
    for x in (hip_x,):
        y=int(sourcehip)
        if not bootmask[y,x]:put(x,y,x,targethip)
    for x in range(0,128,16):
        y=max(0,int(sourcehip)-6)
        if not bootmask[y,x]:put(x,y,x,y+targethip-sourcehip)
    # Actual boot-owned pixel boundary, not an axis-aligned rectangle that would
    # rigidify adjacent thigh paint. Every owned boot pixel is a rigid control.
    by,bx=np.where(bootmask)
    for x,y in zip(bx,by):put(x,y,x+delta[0],y+delta[1])
    src=np.array(list(points),float);dst=np.array(list(points.values()),float)
    triangles=Delaunay(src).simplices
    S=src[triangles];T=dst[triangles]
    areaS=np.cross(S[:,1]-S[:,0],S[:,2]-S[:,0]);areaT=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0])
    if np.any(areaS*areaT<=1e-8):
        bad=np.where(areaS*areaT<=1e-8)[0].tolist();raise ValueError(('folded boot mesh',bad[:10]))
    source_xy=np.full((128,128,2),-1,np.int16)
    for s,t in zip(S,T):
        x0=max(0,int(np.floor(t[:,0].min())));x1=min(127,int(np.ceil(t[:,0].max())));y0=max(0,int(np.floor(t[:,1].min())));y1=min(127,int(np.ceil(t[:,1].max())))
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];q=np.stack((xx,yy),axis=-1)
        inv=np.linalg.inv(np.column_stack((t[1]-t[0],t[2]-t[0])));v=(q-t[0])@inv.T;w=np.concatenate((1-v.sum(axis=-1,keepdims=True),v),axis=-1);inside=(w.min(axis=-1)>=-1e-8)&(w.max(axis=-1)<=1+1e-8)
        mapped=w@s;xy=np.floor(mapped+.5).astype(np.int16);region=source_xy[y0:y1+1,x0:x1+1];region[inside]=xy[inside]
    if np.any(source_xy<0):raise ValueError(('uncovered mesh pixels',int((source_xy[:,:,0]<0).sum())))
    source_xy=np.clip(source_xy,0,127)
    # All unoccluded output samples from the rigid boot must be exact translation.
    by,bx=np.where(bootmask);tx=bx+delta[0];ty=by+delta[1]
    valid=(tx>=0)&(tx<128)&(ty>=0)&(ty<128)
    if not np.array_equal(source_xy[ty[valid],tx[valid]],np.stack((bx[valid],by[valid]),axis=-1)):raise ValueError('nonrigid boot control output')
    return source_xy,{'source_points':src.tolist(),'target_points':dst.tolist(),'triangles':triangles.tolist(),'minimum_area_product':float((areaS*areaT).min()),'all_boot_pixels_are_rigid_controls':int(bootmask.sum()),'covered_pixels':128*128}
