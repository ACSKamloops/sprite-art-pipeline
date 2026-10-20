from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];T=R/'prototype-donor07-v1'
for n in ['frames','maps','masks','proof','parts']:(T/n).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def png(p,a):Image.fromarray(a.astype('uint8')).save(p)
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def poly(pts):
 m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0
src=arr(R/'inputs/control/06.png');donor=arr(R/'inputs/control/07.png');yy,xx=np.mgrid[:128,:128]
# Persistent P: exact current visible left leg/boot, including fringe in this
# explicit2D owner. The fused diagonal boundary is declared, not recovered.
powner=poly([(49,80),(57,80),(59,85),(58,88),(61,92),(61,97),(64,101),(64,103),(60,107),(47,108),(45,102),(46,94),(48,88)])
sash=np.array(Image.open(R/'inputs/provenance/visible-sash06.png').convert('L'))>0
body=arr(R/'inputs/provenance/body06.png')[:,:,3]>0
protected=(yy<81)|body|sash|powner
# Whole visible07 cuff/boot contour, with transparent pixels around its toe,
# heel and sole. The top edge follows the visible boot/gray-cuff division,
# excluding the separate glove above it.
bootrows={86:[80,88],87:[75,89],88:[72,90],89:[69,91],90:[68,91],91:[67,91],92:[67,91],93:[68,91],94:[69,91],95:[69,90],96:[69,89],97:[69,88],98:[69,87],99:[70,86],100:[70,85],101:[71,84],102:[72,82],103:[73,81],104:[73,80]}
bootowner=np.zeros((128,128),bool)
for y,(lo,hi)in bootrows.items():bootowner[y,lo:hi+1]=True
# Remove only the old Q envelope. P is never removed. This is old-part erasure,
# not a mask inferred by brown color or by a row threshold.
oldq=poly([(56,82),(67,82),(73,84),(75,88),(73,91),(73,93),(73,99),(71,103),(65,104),(61,101),(59,94),(57,90),(55,87)])&~protected
out=src.copy();out[oldq]=0
source_id=np.full((128,128),6,dtype='int16');source_xy=np.stack([xx,yy],-1).astype('int16');source_id[oldq]=-1;source_xy[oldq]=-1
# A small projected proximal CLOTH patch, sampled only from visible07 gray
# trousers. These target control points author its new silhouette/coverage.
# It is source-colored projected underpaint, not recovered hidden anatomy.
sp=np.array([[69,83],[76,83],[77,86],[73,88],[69,87],[73,85]],float)
tp=np.array([[58,82],[73,82],[76,86],[70,92],[60,89],[67,86]],float)
tris=[[5,0,1],[5,1,2],[5,2,3],[5,3,4],[5,4,0]]
cloth=np.zeros_like(src);clothmap=np.full((128,128,2),-1,dtype='int16');clothowner=np.zeros((128,128),bool)
for tri in tris:
 s=sp[tri];t=tp[tri];M=np.vstack((t.T,np.ones(3)));inv=np.linalg.inv(M)
 for y in range(max(0,int(t[:,1].min())),min(127,int(t[:,1].max()))+1):
  for x in range(max(0,int(t[:,0].min())),min(127,int(t[:,0].max()))+1):
   w=inv@np.array([x,y,1]);
   if w.min()<-1e-8:continue
   sx,sy=np.floor(w@s+.5).astype(int)
   if not protected[y,x]:cloth[y,x]=donor[sy,sx];clothmap[y,x]=[sx,sy];clothowner[y,x]=True
# Literal gray attachment already present at06 is kept unless covered by the
# complete07 boot in foreground. New cloth lies behind this original volume.
for y,x in np.argwhere(clothowner):
 old=src[y,x];isgray=old[3]>0 and int(old[:3].max())-int(old[:3].min())<18
 if isgray and not oldq[y,x]:continue
 out[y,x]=cloth[y,x];source_id[y,x]=7;source_xy[y,x]=clothmap[y,x]
boot=np.zeros_like(src);bootmap=np.full((128,128,2),-1,dtype='int16');boot_towner=np.zeros((128,128),bool);dx,dy=-4,-1
for sy,sx in np.argwhere(bootowner):
 tx,ty=int(sx)+dx,int(sy)+dy
 boot[ty,tx]=donor[sy,sx];bootmap[ty,tx]=[sx,sy];boot_towner[ty,tx]=True
# Target boot owner includes transparent erasure. It may not touch actual P,
# upper or sash. A handful of owner-rectangle empty pixels can intersect P;
# they are excluded, while every nonzero boot sample must remain complete.
conflict=boot_towner&protected&(boot[:,:,3]>0)
assert not conflict.any(),np.argwhere(conflict).tolist()
active=boot_towner&~protected
# Source-over actual partial-alpha07 boot over the cloth/base underpaint.
base_before_boot=out.copy();O=Image.fromarray(out);O.alpha_composite(Image.fromarray(boot));composited=np.array(O)
changed_by_boot=active&(boot[:,:,3]>0);out[changed_by_boot]=composited[changed_by_boot]
source_id[changed_by_boot]=17;source_xy[changed_by_boot]=bootmap[changed_by_boot]
# Preserve complete P/source upper/sash byte-for-byte in final RGBA.
out[protected]=src[protected];source_id[protected]=6;source_xy[protected]=np.stack([xx,yy],-1)[protected]
out[out[:,:,3]==0]=0
for i in range(8):
 p=T/'frames'/f'{i:02}.png'
 if i==6:png(p,out)
 else:shutil.copy2(R/'inputs/control'/f'{i:02}.png',p)
for n,m in [('P-protected-owner',powner),('source07-complete-visible-boot-owner',bootowner),('target07-boot-owner',boot_towner),('old06-Q-erasure',oldq),('projected-cloth-owner',clothowner),('upper-sash-P-protected',protected),('actual-RGBA-change',np.any(out!=src,axis=2))]:png(T/'masks'/f'{n}.png',m.astype('uint8')*255)
for n,a in [('07-visible-boot',np.where(bootowner[:,:,None],donor,0)),('07-boot-translated-minus4-minus1',boot),('07-projected-gray-cloth',cloth),('06-after-old-Q-erasure',np.where(oldq[:,:,None],0,src)),('06-before-boot-over',base_before_boot)]:png(T/'parts'/f'{n}.png',a)
np.savez_compressed(T/'maps/source-map.npz',source_id=source_id,source_xy=source_xy,boot_source_xy=bootmap,cloth_source_xy=clothmap)
# Keep literal per-target witnesses for both projected cloth and translated boot,
# including underneath occluded/partial-alpha samples.
texels=[]
for role,m,mp in [('projected-cloth',clothowner,clothmap),('translated-complete-boot',boot_towner,bootmap)]:
 for y,x in np.argwhere(m):
  sx,sy=map(int,mp[y,x]);texels.append({'role':role,'target':[int(x),int(y)],'source':'inputs/control/07.png','source_xy':[sx,sy],'source_rgba':donor[sy,sx].tolist(),'protected_at_target':bool(protected[y,x]),'under_rgba_before_boot':base_before_boot[y,x].tolist()if role.startswith('translated')else None,'final_rgba':out[y,x].tolist()})
save(T/'maps/source-RGBA-witnesses.json',texels)
save(T/'recipe.json',{'status':'one unselected projected-donor06 prototype','sources':{'06':{'file':'../inputs/control/06.png','sha256':sha(R/'inputs/control/06.png')},'07':{'file':'../inputs/control/07.png','sha256':sha(R/'inputs/control/07.png')}},'boot_source_owner_rows':bootrows,'boot_complete_visible_translation':[-4,-1],'boot_scaling_or_reflection':False,'cloth_source_control_points':sp.tolist(),'cloth_target_control_points':tp.tolist(),'cloth_triangle_indices':tris,'cloth_new_coverage':'new explicit projected proximal cloth coverage from visible07 source texels; not hidden-anatomy recovery','source_map_ids':{'6':'unchanged06','7':'07 projected gray cloth source copy','17':'07 boot source-over onto retained/projected underpaint','-1':'old-Q erasure'},'protected_mask':'masks/upper-sash-P-protected.png','P_visible_role':'upright screen-left06 boot and associated visible cloth. Fused seam ownership is a declared editing interpretation.','gray_projection':'Original intended cloth retained outside exact old-Q owner; foreground donor boot may occlude it. No blanket gray erasure.','upper_and_sash_and_P_exact':bool(np.array_equal(src[protected],out[protected])),'unchanged_other7_PNG_bytes':all(sha(T/'frames'/f'{i:02}.png')==sha(R/'inputs/control'/f'{i:02}.png')for i in range(8)if i!=6),'actual_changed_RGBA_pixels':int(np.any(out!=src,axis=2).sum()),'raw_input06_boot_count':int((src[:,:,3]>0).sum()),'complete_visible07_boot_samples':int((bootowner&(donor[:,:,3]>0)).sum()),'nonzero_boot_samples_blocked_by_protected_mask':int(conflict.sum()),'new06_sha256':sha(T/'frames/06.png'),'timing':'8 unchanged9/160 holds,9/20 total','model_calls':0,'limits':['No anatomy/contact or normal-speed quality claim.','Visible07 donor is fused paint, no complete hidden leg.','Cloth controls are newly authored projected coverage; its underpaint is honest source-colored construction.','No editor package before parent visual inspection.']})
# Proof rows:05 /old06 /new06 /07, each on light,dark,actualforest.
ground=Image.open(R/'inputs/forest-ground-crop.png').convert('RGBA')
for size in [128,256,84]:
 rh=size+20;outproof=Image.new('RGB',(4*size,3*rh),(232,231,218))
 for ri,bg in enumerate([(232,231,218,255),(24,27,25,255),'forest']):
  for ci,(label,p)in enumerate([('05 exact',R/'inputs/control/05.png'),('06 old',R/'inputs/control/06.png'),('06 donor07 trial',T/'frames/06.png'),('07 exact',R/'inputs/control/07.png')]):
   z=ground.copy()if bg=='forest'else Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(p).convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST if size>=128 else Image.Resampling.LANCZOS);outproof.paste(z.convert('RGB'),(ci*size,ri*rh+20));ImageDraw.Draw(outproof).text((ci*size+2,ri*rh+3),label,fill='black')
 outproof.save(T/'proof'/f'05-old06-new06-07-{size}.png')
# Fullsource/candidate8chronology atnative/2x/84, exactlysamebackdrop.
for size in [128,256,84]:
 outproof=Image.new('RGB',(8*size,2*(size+20)),(232,231,218));d=ImageDraw.Draw(outproof)
 for row,fold in enumerate([R/'inputs/control',T/'frames']):
  for i in range(8):
   z=ground.copy();z.alpha_composite(Image.open(fold/f'{i:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST if size>=128 else Image.Resampling.LANCZOS);outproof.paste(z.convert('RGB'),(i*size,row*(size+20)+20));d.text((i*size+2,row*(size+20)+3),f'{"old" if row==0 else "trial"} NE{i:02}',fill='black')
 outproof.save(T/'proof'/f'full8-before-after-{size}.png')
# Lower detail usesactualsourcepixels only; checker behind alpha.
box=(43,77,89,110);sz=8;can=Image.new('RGB',(4*(box[2]-box[0])*sz,((box[3]-box[1])*sz)+24),(232,231,218));d=ImageDraw.Draw(can)
for j,(label,p)in enumerate([('05 exact',R/'inputs/control/05.png'),('old06',R/'inputs/control/06.png'),('new06 donor07',T/'frames/06.png'),('07 exact',R/'inputs/control/07.png')]):
 z=Image.new('RGBA',(128,128),(232,231,218,255));z.alpha_composite(Image.open(p).convert('RGBA'));can.paste(z.crop(box).resize(((box[2]-box[0])*sz,(box[3]-box[1])*sz),Image.Resampling.NEAREST).convert('RGB'),(j*(box[2]-box[0])*sz,24));d.text((j*(box[2]-box[0])*sz+4,4),label,fill='black')
can.save(T/'proof/lower-before-after-8x.png')
print(json.dumps({'sha256':sha(T/'frames/06.png'),'changed_pixels':int(np.any(out!=src,axis=2).sum()),'source_boot_samples':int((bootowner&(donor[:,:,3]>0)).sum()),'P_upper_sash_exact':True,'other7_PNG_exact':True},indent=2))
