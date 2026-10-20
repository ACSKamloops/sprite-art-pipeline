"""One optional, fixed-anchor carried torso parent. No art acceptance implied."""
import math,copy
import numpy as np
from PIL import Image

CARRIED=('chest','shield','backpack_halo','sword_upper_arm','sword_forearm')
HEAD_NECK=np.array([133.,72.])  # Authored bottom-of-head connection in the owned256 source.

def transform(packet,index,cfg):
 f=packet['frames'][index];phase=f['phase'];angle=-3*math.sin(2*math.pi*phase)
 # Bounded settling of carried upper relative to waist, not extra whole-actor bob.
 load=sum(.5*(1+math.cos(math.pi*abs((phase-c+.5)%1-.5)/.16)) if abs((phase-c+.5)%1-.5)<.16 else 0 for c in [.10,.60])
 settle=np.array([0.,2.25*load]);a=math.radians(angle);rot=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
 pelvis=np.array(f['upper_pixels']['pelvis'])-f['physical_root_pixels'];pivot=np.array(cfg['pelvis_rest']);target=pelvis+settle
 return rot,pivot,target,{'phase':phase,'angle_degrees':angle,'settle_y_px':float(settle[1]),'pelvis':pelvis.tolist(),'source_pivot':pivot.tolist(),'target_pivot':target.tolist(),'head_neck_source':HEAD_NECK.tolist(),'head_neck_target':(target+rot@(HEAD_NECK-pivot)).tolist()}

def warp(source,rotation,anchor,target):
 inv=rotation.T;offset=np.array(anchor)-inv@target
 return source.transform((256,256),Image.Transform.AFFINE,(inv[0,0],inv[0,1],offset[0],inv[1,0],inv[1,1],offset[1]),Image.Resampling.NEAREST)

def cloth_packet(packet,cfg):
 result=copy.deepcopy(packet);bind=packet['neutral_bind']['upper_pixels'];offset=np.array(cfg['chest_hinge'])-cfg['pelvis_rest']-(np.array(bind['chest'])-bind['pelvis'])
 for i,f in enumerate(result['frames']):
  rot,pivot,target,data=transform(packet,i,cfg);chest=target+rot@(np.array(cfg['chest_hinge'])-pivot)
  f['upper_pixels']['chest']=(chest+f['physical_root_pixels']-offset).tolist();f['chest_counterrotation_degrees']=data['angle_degrees']
 return result

def render(sources,packet,index,cfg,cloth_module,adapted):
 rot,pivot,target,meta=transform(packet,index,cfg);layers={n:warp(sources[n],rot,pivot,target)for n in CARRIED}
 neck=np.array(meta['head_neck_target']);layers['head']=warp(sources['head'],np.eye(2),HEAD_NECK,neck)
 layers['cape'],detail=cloth_module.render(sources['cape'],adapted,index,cfg,'chest',103,.10)
 meta['cape']=detail;meta['head_gaze_rotation_degrees']=0
 return layers,meta
