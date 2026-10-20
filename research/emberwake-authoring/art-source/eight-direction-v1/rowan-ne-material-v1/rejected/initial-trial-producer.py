from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def m(n):return np.array(Image.open(P/n).convert('L'))>0
def save(ar,n):Image.fromarray(ar).save(P/n)
source=[a(f'inputs/frames/{i:02}.png')for i in range(8)];rows03=[(84,69,76,83,56),(85,68,76,84,55),(86,68,75,85,56),(87,68,74,86,57),(88,68,74,87,57),(89,68,73,88,58),(90,68,73,89,58),(91,69,72,90,59)]
operations={i:[]for i in [3,4,5,6]}
for y,x0,x1,sy,sx0 in rows03:
 for x in range(x0,x1+1):operations[3].append({'op':'copy','target':[x,y],'source_phase':0,'source':[sx0+x-x0,sy],'reason':'Rounded source00 cream knee light plane and short cuff turn, bounded inside existing03 visible cream cloth; retain boots'})
# Explicit small shade joins, not a global cloth or joint recolor.
for target,src in [([69,90],[62,89]),([70,90],[63,89]),([71,90],[64,89]),([70,91],[64,90]),([71,91],[65,89])]:operations[4].append({'op':'copy','target':target,'source_phase':0,'source':src,'reason':'Short source00 shaded cream cuff roll reduces pointed bright tongue while preserving actual boot outline'})
for target,src in [([60,84],[65,89]),([61,84],[63,90]),([62,84],[64,90])]:operations[6].append({'op':'copy','target':target,'source_phase':0,'source':src,'reason':'Bounded source00 cream-edge shade rounds the narrow under-hem cloth remnant'})
# The erasure owners are actual fixed source02 hip-underpaint only, in explicit
# per-pose fringe rectangles. No pose-owned leather or torso pixels are included.
for i,rect in [(4,[76,81,80,87]),(5,[72,82,80,88]),(6,[76,81,80,87])]:
 z=np.load(P/f'inputs/maps/{i:02}-source.npz');x0,y0,x1,y1=rect
 for y in range(y0,y1):
  for x in range(x0,x1):
   if z['layer_id'][y,x]==1 and source[i][y,x,3]>0:operations[i].append({'op':'erase','target':[x,y],'reason':'Remove visible unsupported fixed hip-underpaint fringe; source witness is layer1 of the retained upstream map'})
operations[6].append({'op':'erase','target':[61,85],'reason':'Trim one-pixel hanging cloth point below the small central under-hem cap; no boot surface'})
receipts=[]
for i in range(8):
 if i not in operations:shutil.copy2(P/f'inputs/frames/{i:02}.png',P/f'candidate/{i:02}.png');continue
 base=source[i];out=base.copy();z=np.load(P/f'inputs/maps/{i:02}-source.npz');upper=np.isin(z['layer_id'],[0,4,5,6]);boot=m(f'inputs/masks/{i:02}-complete-boot.png');changed=np.zeros((128,128),bool);sid=np.full((128,128),i,np.int16);xy=np.stack(np.meshgrid(np.arange(128),np.arange(128)),axis=-1).astype('int16');erased=np.zeros((128,128),bool);literal=[]
 for op in operations[i]:
  x,y=op['target'];assert not upper[y,x],(i,op,'upper');assert not boot[y,x],(i,op,'complete boot');before=base[y,x].tolist()
  if op['op']=='copy':
   sx,sy=op['source'];sp=op['source_phase'];c=source[sp][sy,sx];assert c[3]==255 and base[y,x,3]==255
   # The declared source patch is observed cream cloth, with its existing shaded edge.
   assert int(c[0])>120 and int(c[1])>90 and int(c[0])-int(c[1])<60
   out[y,x]=c;sid[y,x]=sp;xy[y,x]=[sx,sy];literal.append({**op,'source_RGBA':c.tolist(),'before_RGBA':before})
  else:out[y,x]=0;sid[y,x]=-2;xy[y,x]=[-1,-1];erased[y,x]=True;literal.append({**op,'before_RGBA':before,'upstream_source_phase':int(z['source_id'][y,x]),'upstream_source_xy':z['source_xy'][y,x].tolist(),'upstream_owner_layer':int(z['layer_id'][y,x])})
  changed[y,x]=True
 assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[boot],base[boot]);assert np.array_equal(out[~changed],base[~changed])
 save(out,f'candidate/{i:02}.png');save(changed.astype('uint8')*255,f'masks/{i:02}-literal-material-owner.png');save(upper.astype('uint8')*255,f'masks/{i:02}-protected-upper.png');save(boot.astype('uint8')*255,f'masks/{i:02}-exact-complete-boot.png');save(erased.astype('uint8')*255,f'masks/{i:02}-unsupported-fringe-erasure.png');np.savez_compressed(P/f'maps/{i:02}-literal-source-map.npz',source_phase=sid,source_xy=xy,erased=erased,allowed=changed)
 receipts.append({'phase':i,'operations':literal,'actual_changed_RGBA_pixels':int(np.any(base!=out,axis=2).sum()),'upper_head_torso_arms_gloves_RGBA_exact':True,'complete_boot_owner_RGBA_exact':True,'toe_placement_unchanged':True,'source0_material_copy_pixels':sum(op['op']=='copy'for op in literal),'authored_fringe_erasure_pixels':sum(op['op']=='erase'for op in literal),'candidate_PNG_sha256':hashlib.sha256((P/f'candidate/{i:02}.png').read_bytes()).hexdigest()})
recipe={'status':'ONE bounded material-only trial; preview pending, no selection or inherited score','actor':'Rowan','view':'northeast','generation_calls':0,'scope':'03 bounded rounded cream knee/cuff source00 patch;04 short cream cuff shade;04/05/06 fixed hip-underpaint fringe cleanup and06 small central cloth-tip shade.02 is retained exact after inspection, rather than recoloring every joint.','source_claim':'Actual visible same-view source00 cream material with literal per-pixel witnesses; layout and erasures are new authored repairs, not recovered hidden anatomy or rig','upper_protection':'All actual final upstream torso/arm/glove/socket owner pixels(layers0/4/5/6) exact; no blue tunic, gold rim or glove material edited','boot_protection':'Every original complete-boot owner RGBA exact; all new edits lie in literal existing cream cloth or unsupported hip-underpaint, no boot/toe displacement or whole-pose fitting','phase_repairs':receipts,'unchanged_PNG_byte_phases':[0,1,2,7],'clock':{'hold':[9,160],'cycle':[9,20]},'quality_approval':False}
(P/'RECIPE.json').write_text(json.dumps(recipe,indent=2)+'\n');print(json.dumps({'phases':[{k:r[k]for k in ['phase','actual_changed_RGBA_pixels','source0_material_copy_pixels','authored_fringe_erasure_pixels','candidate_PNG_sha256']}for r in receipts]}))
