#!/usr/bin/env python3
import pathlib,json,hashlib,argparse
import numpy as np
from PIL import Image
p=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--records',default='TRANSITION-CAPTURE-RECORDS.json');parser.add_argument('--output',default='TRANSITION-CAPTURE-VERIFICATION.json');args=parser.parse_args()
report=json.loads((p/args.records).read_text());checks=[]
for row in report['records']:
 mpath=p/row['source_manifest'].replace('res://','');m=json.loads(mpath.read_text());f=m['frames'][row['source_frame']];source=mpath.parent/f['file'];assert hashlib.sha256(source.read_bytes()).hexdigest()==f['sha256']
 s=int(row['scale']);rgba=np.array(Image.open(source).convert('RGBA'));expanded=np.repeat(np.repeat(rgba,s,axis=0),s,axis=1);yy,xx=np.nonzero(expanded[:,:,3]==255)
 x,y=map(int,row['draw_origin']);im=np.array(Image.open(p/row['file'].replace('res://','')).convert('RGBA'));wx,wy=xx+x,yy+y;inside=(wx>=0)&(wy>=0)&(wx<im.shape[1])&(wy<im.shape[0])
 ok=bool(inside.all()) and np.array_equal(im[wy,wx,:3],expanded[yy,xx,:3]);checks.append({'sample':row['sample'],'group':row['group'],'source_frame':row['source_frame'],'opaque_source_rgb_exact':ok})
result={'passed':all(c['opaque_source_rgb_exact'] for c in checks),'checks':checks,'scope':'Actual GPU whole-actor opaque source RGB at recorded final draw origin. Proves source pixel presentation, not anatomical contact or art quality. Input capture record specifies live-clock or fixed-state sampling.','input_records':args.records}
(p/args.output).write_text(json.dumps(result,indent=2));print('exact transition captures',sum(c['opaque_source_rgb_exact'] for c in checks),'/',len(checks));assert result['passed']
