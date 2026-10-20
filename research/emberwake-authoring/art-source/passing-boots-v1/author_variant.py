"""Author a single source-toe/heel variant; freeze literal masks in PLAN.json.
This script is the recorded authoring operation, not a generic ownership finder.
Every listed view/role coordinate was inspected in its native source pair.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
BASE=Path(__file__).resolve().parent
# target, preceding donor, far dx/dy+distal band, support dx/dy+literal row regions.
SPEC={
 'lyra':[
  (112,121,(3,2,(54,96,62,102)),(1,0,[(101,104,62,75),(104,110,60,75)])),
  (113,123,(1,4,(68,97,75,102)),(2,-1,[(101,104,54,68),(104,110,54,69)])),
  (114,125,(3,4,(54,99,63,104)),(2,-2,[(101,104,62,76),(104,110,61,76)])),
  (115,127,(0,3,(67,99,75,104)),(-1,-2,[(101,104,53,67),(104,110,52,69)])),
 ],
 'brann':[
  (112,121,(4,3,(50,102,64,108)),(0,-1,[(101,111,63,81)])),
  (113,123,(0,2,(69,101,79,108)),(0,0,[(101,105,51,69),(105,111,50,70)])),
  (114,125,(3,8,(53,102,65,107)),(3,-3,[(101,109,64,82)])),
  (115,127,(3,2,(69,101,80,108)),(1,-2,[(101,105,50,68),(105,109,50,69)])),
 ]}
def sha(data):return hashlib.sha256(data).hexdigest()
def cel(a,f):return a.crop((f%8*128,f//8*128,f%8*128+128,f//8*128+128))
entries=[]
for char,specs in SPEC.items():
 atlas=Image.open(BASE/'inputs'/char/'atlas.png').convert('RGBA')
 for target,source,far,support in specs:
  before=cel(atlas,target);donor=cel(atlas,source)
  entry={'character':char,'target':target,'source':source,'view':'south' if target<114 else 'north','target_rgba_sha256':sha(before.tobytes()),'source_rgba_sha256':sha(donor.tobytes()),'operations':[]}
  dx,dy,(x0,y0,x1,y1)=far
  points=[]
  for ty in range(y0,y1):
   for tx in range(x0,x1):
    sx,sy=tx-dx,ty-dy
    # Authoring constraint only: lifted outer alpha/cuff stays exact. The
    # frozen literal point list, not this condition, is used in replay.
    if before.getpixel((tx,ty))[3]==255 and donor.getpixel((sx,sy))[3]==255:
     points.append([tx,ty,sx,sy])
  entry['operations'].append({'owner':'visible lifted distal leather; current cuff/outer alpha retained','offset':[dx,dy],'points_tx_ty_sx_sy':points})
  dx,dy,regions=support;points=[]
  for y0,y1,x0,x1 in regions:
   for ty in range(y0,y1):
    for tx in range(x0,x1):points.append([tx,ty,tx-dx,ty-dy])
  entry['operations'].append({'owner':'foreground support toe/heel and immediate ankle seam','offset':[dx,dy],'literal_y0_y1_x0_x1_regions':regions,'points_tx_ty_sx_sy':points})
  entries.append(entry)
plan={'schema':'emberwake-passing-boot-variant/v1','status':'Single toe/heel source-pixel candidate; no rating or approval','cell':[128,128],'columns':8,'preserve_final_sole_row':True,'targets':[112,113,114,115],'entries':entries,'source_contract':'Same character and view, predecessor source as stated. Exact RGBA from named visible distal boot donors; no invented anatomy, scale, warp, palette remap or body fit. Final original sole row and upper cuff stay untouched.'}
(BASE/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print('Authored literal plan for',len(entries),'cels')
