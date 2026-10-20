"""Actual knee-region alpha underlap + scoped continuous normal sign audit."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
import build as b
P=b.P;report={};view=np.array([0,math.cos(math.radians(18)),math.sin(math.radians(18))])
for name,pack,posefile,modeldir in [('canonical','original-underlap-v1','poses.json','gait-canonical'),('amplitude','amplitude-underlap-v1','poses-amplitude-70.json','gait-amplitude')]:
 out=P/'artifacts'/pack;d=json.loads((out/'manifest.json').read_text());packet=json.loads((P/'source'/posefile).read_text());assert d['poses_sha256']==b.sha(P/'source'/posefile)
 rows=[]
 for f,r in zip(packet['frames'],d['records']):
  rr={'index':f['index'],'feet':{}}
  for n in ['far','near']:
   t=np.array(Image.open(out/r['integration_layers'][n+'_thigh']['file']))[:,:,3]>0;s=np.array(Image.open(out/r['integration_layers'][n+'_shin']['file']))[:,:,3]>0;k=np.array(f['legs'][n]['pixels']['knee'])-f['physical_root_pixels'];yy,xx=np.mgrid[:256,:256];area=(xx-k[0])**2+(yy-k[1])**2<=24**2
   assert (s&area).any() and (t&area).any();global_gap=float(distance_transform_edt(~t)[s].min());joint_gap=float(distance_transform_edt(~(t&area))[s&area].min());assert joint_gap<=1
   rr['feet'][n]={'global_min_thigh_to_shin_distance':global_gap,'knee_neighborhood_min_distance':joint_gap,'joint_region_radius_pixels':24}
  rows.append(rr)
 geom=b.load('geometry_'+name,P/'source'/modeldir/'build.py');dots=[];stable=[];flips=0;matched=0;max_packet_delta=0
 for frame in packet['frames']:
  generated=geom.pose(frame['phase'])
  for nn in ['far','near']:
   for point in ['hip','knee','ankle']:
    max_packet_delta=max(max_packet_delta,float(np.linalg.norm(np.array(generated['legs'][nn]['world'][point])-frame['legs'][nn]['world'][point])))
 assert max_packet_delta<1e-10
 reference={}
 for n in ['far','near']:
  for cap in [False,True]:
   leg=geom.pose(0)['legs'][n];axis=b.core.unit(np.array(leg['world']['ankle'])-leg['world']['knee'])
   if cap:axis=b.core.unit(axis+b.core.unit(np.array(leg['world']['knee'])-leg['world']['hip']))
   t=np.array([-.8,-.6,0]);t=b.core.unit(t-axis*np.dot(t,axis));reference[(n,cap)]=b.core.unit(np.cross(axis,t))
 for i in range(1441):
  f=geom.pose(i/1440)
  for n in ['far','near']:
   for cap in [False,True]:
    leg=f['legs'][n];axis=b.core.unit(np.array(leg['world']['ankle'])-leg['world']['knee'])
    if cap:axis=b.core.unit(axis+b.core.unit(np.array(leg['world']['knee'])-leg['world']['hip']))
    t=np.array([-.8,-.6,0]);t=b.core.unit(t-axis*np.dot(t,axis));normal=b.core.unit(np.cross(axis,t));dv=float(normal@view);dots.append(dv);stable.append(float(normal@reference[(n,cap)]));flips+=dv<0
 assert flips==0
 report[name]={'pose_sha256':d['poses_sha256'],'maximum_global_alpha_gap':max(x['feet'][n]['global_min_thigh_to_shin_distance']for x in rows for n in ['far','near']),'maximum_knee_region_alpha_gap':max(x['feet'][n]['knee_neighborhood_min_distance']for x in rows for n in ['far','near']),'actual_rendered_joint_rows':rows,'basis_audit':{'uniform_continuous_phase_samples':1441,'normal_camera_sign_flips':int(flips),'minimum_raw_normal_dot_camera':min(dots),'minimum_raw_normal_dot_neutral_reference':min(stable),'model_builder_sha256':b.sha(P/'source'/modeldir/'build.py'),'packet_declared_builder_sha256':packet['builder_sha256'],'copied_model_matches_all72_bone_positions_max_error':max_packet_delta,'model_design_sha256':b.sha(P/'source'/modeldir/'design.json'),'scope':'sampled current forward gait only, not arbitrary future clips; material-front selector never activated in these samples'}}
(P/'joint-basis-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:{'max_knee_gap':v['maximum_knee_region_alpha_gap'],'basis':v['basis_audit']}for k,v in report.items()}))
