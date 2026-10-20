"""One-time observed source cross-sections; no posewise shape fitting."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image
import build
P=Path(__file__).resolve().parent
base=P/'source/profile-reference'
packet=json.loads((P/'source/poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);old=json.loads((base/'manifest.json').read_text())
report={'schema':'captain.source_profile_calibration.v1','source_sha256':build.sha(P/'source/upper/source/native-256.png'),'fixed_bind_sha256':build.sha(P/'source/poses.json'),'method':'Source alpha cross-section along source bone; median span within longitudinal +/-2 pixels. Transport source span through neutral bone map; fixed elliptical ring depth/radius=.55. Proximal missing shaft extrapolates earliest observed shaft. No per-pose fitting.','legs':{}}
for n in ['far','near']:
 mask=np.array(Image.open(base/'parts'/f'{n}_shin-source.png'))[:,:,3]>0
 mask[:181]=False
 yy,xx=np.nonzero(mask);points=np.column_stack([xx,yy]);c=old['source_anchors'][n];k=np.array(c['knee']);ank=np.array(c['ankle']);axis=(ank-k)/np.linalg.norm(ank-k);perp=np.array([-axis[1],axis[0]]);long=(points-k)@axis;trans=(points-k)@perp
 leg=packet['neutral_bind']['legs'][n];M=build.core.bone_matrix(k,ank,np.array(leg['world']['knee']),np.array(leg['world']['ankle']),cam,np.array(packet['camera']['transverse']));pa,t,norm=build.basis(leg);projaxis=cam@pa;projperp=np.array([-projaxis[1],projaxis[0]]);projperp/=np.linalg.norm(projperp);transport=abs(float(projperp@(M@perp)));denom=2*math.sqrt(float(projperp@(cam@t))**2+(.55*float(projperp@(cam@norm)))**2)
 samples=[]
 for s in np.arange(math.floor(long.min())+2,math.ceil(long.max())-1,1):
  ts=trans[abs(long-s)<=2]
  if len(ts)>4:samples.append({'source_longitudinal':float(s),'source_width':float(ts.max()-ts.min()+1)})
 rings=[]
 for v in [0,12,20,28,40,48]:
  source_s=v*np.linalg.norm(ank-k)/48
  nearby=sorted(samples,key=lambda q:abs(q['source_longitudinal']-source_s))[:3]
  width=float(np.median([q['source_width'] for q in nearby]));radius=width*transport/denom
  radius*=json.loads((P/'source/neutral-fit.json').read_text())['fixed_radial_scale'][n]
  rings.append([v,radius,.55*radius])
 report['legs'][n]={'samples':samples,'rings':rings,'projected_source_width_scale':transport,'radius_diameter_projection_factor':denom,'observed_source_mask':str(base/'parts'/f'{n}_shin-source.png'),'cap':'unchanged source registered ellipsoid; widening shaft restores cap/shaft ratio without enlarging cap','boot':'unchanged original source-painted proxy; this trial isolates shaft mass, not boot mass repair'}
(P/'calibration.json').write_text(json.dumps(report,indent=2)+'\n')
print({n:report['legs'][n]['rings'] for n in report['legs']})
