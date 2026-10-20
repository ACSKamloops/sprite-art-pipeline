"""Single genuine02.5 source-pixel GUIDE, not generated/accepted art or recovered anatomy."""
from pathlib import Path
import os,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def m(n):return np.array(Image.open(R/n))>0
def sm(o,n):Image.fromarray((o*255).astype(np.uint8)).save(R/n)
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=d.copy();use=sa>0
 for k in range(3):o[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 o[:,:,3][use]=(n[use]+127)//255
 return o.astype(np.uint8)
def grid(rows,cols,xt,yt):
 src=np.array([[x,y] for y in rows for x in cols],float);dst=np.array([[xt[j][i],yt[j][i] if isinstance(yt[j],list) else yt[j]] for j in range(len(rows)) for i in range(len(cols))],float);tri=[]
 for j in range(len(rows)-1):
  for i in range(len(cols)-1):
   k=j*len(cols)+i;tri.extend([[k,k+len(cols),k+1],[k+1,k+len(cols),k+len(cols)+1]])
 return src,dst,tri
def warp(source,owner,mesh):
 src,dst,tri=mesh;paint=np.zeros((128,128,4),np.uint8);xy=np.full((128,128,2),-1,np.int16);acc=np.zeros((128,128),bool);ti=np.full((128,128),-1,np.int16);dets=[]
 for ordinal,t in enumerate(tri):
  s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;dets.append([float(ds),float(dd)]);inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
   for x in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
    bary=inv@np.array([x,y,1.])
    if bary.min()<-1e-8:continue
    sx,sy=np.floor(bary@s+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and owner[sy,sx] and source[sy,sx,3]>0:paint[y,x]=source[sy,sx];xy[y,x]=[sx,sy];acc[y,x]=True;ti[y,x]=ordinal
 return paint,xy,acc,ti,dets
source={2:a('inputs/control/02.png'),3:a('inputs/control/03.png')};yy,xx=np.indices((128,128));upper=yy<=85
for layer in ['sleeve','far','near','fixed']:upper|=a(f'inputs/upper-layers/02-{layer}.png')[...,3]>0
sm(upper,'masks/02-exact-upper-armcuffs-gloves-owner.png')
# Actual03visible charcoal surface; no new polygon-colored paint. Polygon only defines pixel ownership.
clothpoly=[(49,85),(61,85),(66,88),(66,91),(63,94),(53,95),(49,92),(47,88)]
cloth=poly(clothpoly)&(source[3][...,3]>0)&(source[3][...,:3].max(axis=-1)<90)&((source[3][...,:3].max(axis=-1).astype(int)-source[3][...,:3].min(axis=-1))<=14)
qowner=m('inputs/source-owners/03-Q-whole-boot.png')&(source[3][...,3]>0)
powner=m('inputs/source-owners/02-P-whole-visible-leg.png')&(source[2][...,3]>0)
for n,o in [('03-Q-proximal-trousers-source',cloth),('03-Q-cuff-boot-source',qowner),('02-P-complete-leg-source',powner)]:sm(o,'masks/'+n+'.png')
# Qboot has separate cuff/calf/ankle/heel/toe bands, with modest distinct changes inwidth/lean/height.
qmesh=grid([90,94,98,102,106,110],[50,56,62,68,76],[[48,53,58,63,69],[48,52,57,62,69],[49,53,58,63,69],[49,54,59,64,69],[50,54,59,64,69],[50,55,60,64,69]],[89,92.5,95.5,98,101,105])
# Complete actual03trouser shading is projected only at the proximal join, with fixedtophip.
cmesh=grid([85,88,91,95],[47,53,59,66],[[47,53,59,66],[47,52.5,58,65],[47,52,57.5,64],[48,52.5,57,63]],[85,87.5,89.5,92])
pmesh=grid([86,94,102,115],[61,70,80,93],[[61,70,80,93]]*4,[85,93,101,114])
items=[('Q-proximal',3,cloth,cmesh),('P-retreating',2,powner,pmesh),('Q-cuff-heel-toe',3,qowner,qmesh)]
base=source[2];out=base.copy();out[~upper]=0;parts=[];controls=[]
for rid,(name,phase,owner,mesh) in enumerate(items,1):
 paint,xy,acc,ti,dets=warp(source[phase],owner,mesh);out=over(out,paint);Image.fromarray(paint).save(R/'layers'/f'{rid}-{name}.png');sm(acc,f'masks/{rid}-{name}-target.png');np.savez_compressed(R/'maps'/f'{rid}-{name}.npz',source_phase=np.array(phase,np.int8),source_xy=xy,owner=acc,triangle=ti)
 for y,x in np.argwhere(acc):sx,sy=xy[y,x];assert np.array_equal(paint[y,x],source[phase][sy,sx])
 src,dst,tri=mesh;controls.append({'id':rid,'name':name,'source_phase':phase,'source_vertices':src.tolist(),'target_vertices':dst.tolist(),'triangles':tri,'determinants':dets,'source_owned_pixels':int(owner.sum()),'target_paint_pixels':int(acc.sum())})
 parts.append(paint)
out[upper]=base[upper];assert np.array_equal(out[upper],base[upper]);Image.fromarray(out).save(R/'frames/02.5.png');sm(np.any(out!=base,axis=-1),'masks/02.5-change-vs02.png')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();same=[]
for i in range(8):assert (R/'frames'/f'{i:02}.png').read_bytes()==(R/'inputs/control'/f'{i:02}.png').read_bytes();same.append(i)
order=['00','01','02','02.5','03','04','05','06','07'];holds=[18,18,9,9,18,18,18,18,18];clock=0;starts={}
for n,h in zip(order,holds):starts[n]=clock;clock+=h
assert clock==144 and all(starts[f'{i:02}']==i*18 for i in range(8))
(R/'TIMING.json').write_text(json.dumps({'fps':320,'order':order,'hold_ticks':holds,'start_ticks':starts,'total_ticks':144,'cycle_seconds':[9,20],'all_original8_key_starts_fixed':True,'only02hold_split':[9,9]},indent=2)+'\n')
recipe={'status':'GUIDE ONLY, one02.5source-art hypothesis, parentpreviewbeforeanypaintcallorlargepackage','upper_authority':'Exactactual02head/torso/hem/armcuffs/gloves; completeupperownerrestoredRGBA','planned_roles':{'P':'02rightforeboot retracts slightly by02.5 then03rightretreating; exactactual02visiblepart shifts[0,-1]withupperprotected','Q':'02lefttucked boot unfolds into02.5intermediatecuff/heel/toe, thenactual03fullerleftQ. Usesonlyactual03visiblematerialsurfaces, separatedclothandbootbands.'},'source_cloth_owner_polygon':clothpoly,'material_ownership_note':'Darkneutralactual03RGBrestrictsclothsourcepolygon. Bootowneris literal03Qconstructionowner butsamplesactualcurrent03PNG,includingdeclaredprior2pxcuffrepair. No hiddenlimbanatomy recovered.','raster':'Integerpixelcentres, inversebarycentricnearestfloor(value+.5),sourceRGBAexact,integer source-over foroverlap','parts':controls,'layer_order':['exact02bodywithlowererased','Qactual03proximaltrousers','Pactual02retreating','Qactual03cuff/heel/toe','exact02upperrestore'],'new_authored_paint':0,'model_calls':0,'new_hidden_anatomy_or_contact_claim':False,'whole_body_fit_reflection_crossfade':False,'limitations':'Projectedvisibletexturemaylacknecessarynewcuff/kneepaint. Thisis a guide forinspection, not selectedart. No acceptance frommaps/timing.'}
(R/'RECIPE.json').write_text(json.dumps(recipe,indent=2)+'\n')
receipt={'new02_5_sha256':sha(R/'frames/02.5.png'),'all8_original_PNG_bytes_exact':same,'actual02upper_RGBA_exact':True,'all_original8_key_starts_fixed':True,'exposures':9,'total_seconds':.45,'sourceRGBA_part_witnesses_exact':True,'P_target_paint_pixels':int((parts[1][...,3]>0).sum()),'Q_boot_target_paint_pixels':int((parts[2][...,3]>0).sum()),'Q_cloth_target_paint_pixels':int((parts[0][...,3]>0).sum()),'new_authored_pixels':0,'model_calls':0,'guide_only':True};(R/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
