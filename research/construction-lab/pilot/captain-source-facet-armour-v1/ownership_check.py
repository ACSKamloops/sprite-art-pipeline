from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;a=P/'artifacts/collar-source-facets';b=P.parent/'captain-greave-hidden-material-v1/artifacts/shaded-long110';m=json.loads((a/'manifest.json').read_text());src=np.array(Image.open(P/'source/upper/source/native-256.png'));report={'art_approval':False,'partition':{},'unchanged_unrelated_layers':0,'same_packet_sha256':m['poses_sha256'],'geometry_scope':'Source armor relief/cap and declared collar change; boots/bones/upper/femur unchanged'}
for n in ['far','near']:
 parts=[np.array(Image.open(a/'parts'/f'{n}_{kind}-source.png')) for kind in ['thigh','shin','cap','boot','shin_ornament']];masks=[v[:,:,3]>0 for v in parts];overlap=sum(masks);assert (overlap<=1).all();old=np.array(Image.open(b/'upper-parts/source-owned'/f'{n}_leg.png'));combined=np.zeros_like(src)
 for v in parts:combined[v[:,:,3]>0]=v[v[:,:,3]>0]
 assert np.array_equal(combined,old)
 report['partition'][n]={'source_leg_RGBA_exact':True,'duplicate_ownership':0,'shaft_armor_pixels':int(masks[1].sum()),'separate_ornament_pixels':int(masks[4].sum())}
for f in (a/'layers').glob('*.png'):
 if not any(f.name.endswith('-'+kind+'.png') for kind in ['far_shin','near_shin','far_cap','near_cap']):assert f.read_bytes()==(b/'layers'/f.name).read_bytes();report['unchanged_unrelated_layers']+=1
assert json.loads((b/'manifest.json').read_text())['poses_sha256']==m['poses_sha256']
(a/'ownership-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
