from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
import build
P=Path(__file__).resolve().parent;out=P/'artifacts/calibrated-long110';m=json.loads((out/'manifest.json').read_text());packet=json.loads((P/'source/poses-long-110.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);bind=json.loads((P/'source/poses.json').read_text())['neutral_bind'];report={'state':'UNAPPROVED','source_profile_sha256':build.sha(P/'calibration.json'),'packet_sha256':build.sha(P/'source/poses-long-110.json'),'actual_joint_gap':{},'neutral_profile':{},'new_colors':0,'nonbinary_alpha':0,'clipped_layer_edge_pixels':0}
src=np.array(Image.open(P/'source/upper/source/native-256.png'));colors={tuple(x) for x in src.reshape(-1,4) if x[3]}
for n in ['far','near']:
 gaps=[]
 for rec in m['records']:
  a=np.array(Image.open(out/rec['integration_layers'][n+'_thigh']['file']))[:,:,3]>0;b=np.array(Image.open(out/rec['integration_layers'][n+'_shin']['file']))[:,:,3]>0
  gaps.append(float(distance_transform_edt(~a)[b].min()))
  for kind in ['shin','boot']:
   rgba=np.array(Image.open(out/rec['integration_layers'][n+'_'+kind]['file']));report['new_colors']+=sum(tuple(x) not in colors for x in rgba[rgba[:,:,3]>0]);report['nonbinary_alpha']+=int(((rgba[:,:,3]!=0)&(rgba[:,:,3]!=255)).sum());report['clipped_layer_edge_pixels']+=int((rgba[0,:,3]>0).sum()+(rgba[-1,:,3]>0).sum()+(rgba[:,0,3]>0).sum()+(rgba[:,-1,3]>0).sum())
 report['actual_joint_gap'][n]={'max_nearest_alpha_gap':max(gaps),'frames':len(gaps)}
 leg=bind['legs'][n];w=leg['world'];axis,t,norm=build.basis(leg);fake={'foot':{'orientation_world':{'forward':norm,'transverse':t,'up':axis},'origin_world':w['knee']}};surf=m['surfaces'][n+'_shin'];tex=np.array(Image.open(out/'parts'/f'{n}_shin-extended-UV.png'));im,_,_=build.raster.render(surf['UV_local_vertices'],surf['triangles'],tex,fake,cam,np.array([0,0]));im.save(out/f'neutral-{n}-shaft.png')
 source=m['source_anchors'][n];M=build.core.bone_matrix(source['knee'],source['ankle'],np.array(w['knee']),np.array(w['ankle']),cam,np.array(packet['camera']['transverse']));target=build.core.warp(Image.open(out/'parts'/f'{n}_shin-source.png'),M,source['knee'],cam@np.array(w['knee'])+np.array(packet['camera']['screen_origin']));target.save(out/f'neutral-{n}-source-target.png')
 # Width normal to projected axis; material coverage, not anatomical acceptance.
 pa=cam@axis;pa/=np.linalg.norm(pa);perp=np.array([-pa[1],pa[0]]);rows={}
 for name,image in [('shell',im),('source',target)]:
  ys,xs=np.nonzero(np.array(image)[:,:,3]);pts=np.column_stack([xs,ys]);a=pts@pa;b=pts@perp;bins=[]
  for q in range(int(a.min()),int(a.max())+1):
   z=b[abs(a-q)<=1]
   if len(z)>2:bins.append(float(z.max()-z.min()+1))
  rows[name]={'median_width':float(np.median(bins)),'max_width':max(bins),'opaque_pixels':len(pts)}
 report['neutral_profile'][n]=rows
(out/'quality-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
