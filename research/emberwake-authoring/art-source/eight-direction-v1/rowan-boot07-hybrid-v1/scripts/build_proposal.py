from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def mask(n):return np.array(Image.open(P/n).convert('L'))>0
def save(im,n):Image.fromarray(im).save(P/n)
def poly(pts):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
src=a('inputs/A/07.png');base=a('inputs/generated07.png');Y,X=np.indices((128,128));gloves=mask('inputs/masks/07-opaque-gloves-protected.png');upper=mask('inputs/masks/07-stable-upper-hem-owner.png')
def cream(im):
 r,g,b=[im[...,k].astype(float) for k in range(3)];return (im[...,3]>0)&(r>70)&(g>.70*r)&(b>.63*g)
sourcecream=cream(src);newcream=cream(base)
left=poly([(38,85),(49,85),(61,90),(62,94),(58,103),(38,103)])&(src[...,3]>0)&~sourcecream&~gloves
right=poly([(63,90),(83,90),(91,100),(92,114),(63,114)])&(src[...,3]>0)&~sourcecream&~gloves
left&=~right
repair=(poly([(40,85),(64,85),(66,106),(39,106)])|poly([(64,87),(91,87),(93,113),(63,113)]))&~newcream&~upper&~gloves
out=base.copy();out[repair]=0;sid=np.full((128,128),-1,np.int8);xy=np.full((128,128,2),-1,np.int16);placed={};claims=[]
for ident,name,owner,dx,dy in [(1,'screen-left-old07-boot',left,2,2),(2,'screen-right-old07-boot',right,0,-2)]:
 covered=0;occluded=0;canvas=np.zeros_like(base);placedowner=np.zeros((128,128),bool)
 for sy,sx in np.argwhere(owner):
  tx,ty=sx+dx,sy+dy
  if 0<=tx<128 and 0<=ty<128:
   canvas[ty,tx]=src[sy,sx];placedowner[ty,tx]=True
   if repair[ty,tx]:out[ty,tx]=src[sy,sx];sid[ty,tx]=ident;xy[ty,tx]=[sx,sy];covered+=1
   elif newcream[ty,tx]:occluded+=1
   else:raise AssertionError(('Boot owner outside repair',name,sx,sy,tx,ty))
 save(owner.astype('uint8')*255,f'proposal/{name}-source-owner.png');save(canvas,f'proposal/{name}-translated-paint.png');placed[name]={'rigid_native_translation':[dx,dy],'source_visible_boot_pixels':int(owner.sum()),'retained_visible_pixels':covered,'occluded_by_exact_new_knee':occluded}
 claims.append((ident,owner,dx,dy))
save(out,'proposal/07-before-cuff.png')
# Bounded source-colored cuff connector fills only newly exposed alpha0 gaps; whole boot texels stay untouched.
cuff=[]
for ty,x0,x1,sy,sx0 in [(89,51,61,92,43),(90,50,60,92,43),(91,49,59,93,43),(92,48,57,94,43),(93,47,56,95,43)]:
 for tx in range(x0,x1+1):
  sx=sx0+tx-x0
  if out[ty,tx,3]==0 and repair[ty,tx] and not newcream[ty,tx]:
   assert src[sy,sx,3]>0 and not sourcecream[sy,sx]
   out[ty,tx]=src[sy,sx];sid[ty,tx]=3;xy[ty,tx]=[sx,sy];cuff.append({'at':[tx,ty],'source_at':[sx,sy]})
(P/'proposal/cuff-source-edits.json').write_text(json.dumps({'reason':'Join the retained generated left knee to the complete translated old07 boot, filling alpha0 cuff gaps only','source':'inputs/A/07.png','actual_edits':cuff},indent=2)+'\n')
assert np.array_equal(out[newcream],base[newcream]);assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[gloves],base[gloves]);assert np.array_equal(out[~repair],base[~repair])
save(out,'proposal/07.png');save(repair.astype('uint8')*255,'proposal/07-boot-repair-owner.png');save(newcream.astype('uint8')*255,'proposal/07-generated-knee-protected.png');save(np.any(out!=base,axis=2).astype('uint8')*255,'proposal/07-actual-change.png');np.savez_compressed(P/'maps/07-boot-source.npz',source_id=sid,source_xy=xy)
can=Image.new('RGBA',(384,146),(29,34,43,255));d=ImageDraw.Draw(can)
for j,(name,im) in enumerate([('old07',src),('new07',base),('boot hybrid',out)]):can.alpha_composite(Image.fromarray(im),(128*j,18));d.text((128*j+3,2),name,fill='white')
can.save(P/'proof/old-new-hybrid-native.png');can.resize((1536,584),Image.Resampling.NEAREST).save(P/'proof/old-new-hybrid-4x.png')
receipt={'status':'UNSELECTED no-generation source-boot proposal; joins await inspection','generation_calls':0,'boot_part_placement':placed,'exact_generated_cream_knee_RGBA':True,'exact_upper_hem_RGBA':True,'exact_full_original_visible_gloves_RGBA':True,'changed_pixels':int(np.any(out!=base,axis=2).sum()),'proposal07_sha256':hashlib.sha256((P/'proposal/07.png').read_bytes()).hexdigest(),'rigid_boot_rotation_reflection_scaling_narrowing':False,'bounded_cuff_authored_pixels':len(cuff),'cuff_rule':'Only alpha0 gaps in rows89..93; source-colored boot texels; no whole-boot texel overwritten'}
(P/'PROPOSAL-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
