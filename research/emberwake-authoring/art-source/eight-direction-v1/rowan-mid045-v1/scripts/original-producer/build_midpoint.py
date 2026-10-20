"""One authored midpoint from material-owned endpoint surfaces; exact source samples."""
from pathlib import Path
import os,json,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
def art(i):return np.array(Image.open(P/'inputs/control'/f'{i:02}.png').convert('RGBA'))
def mask(n):return np.array(Image.open(P/n))>0
def smask(m,n):Image.fromarray((m*255).astype(np.uint8)).save(P/n)
a4,a5=art(4),art(5);Y,X=np.indices((128,128))
stable=mask('inputs/owners/04-stable-upper-hem.png');glove=mask('inputs/owners/04-gloves.png');arms=mask('inputs/owners/04-complete-arm-owner.png');protected=stable|glove|arms
frontpants=(mask('inputs/owners/04-front-pants.png')|mask('inputs/owners/04-cuff-connection.png'))&~protected
frontboot=mask('inputs/owners/04-front-whole-boot.png')&~protected
frontpants&=~frontboot
# An explicitly owned actual05 rear surface, including complete visible knee/cuff/heel/toe.
r=Image.new('L',(128,128));d=ImageDraw.Draw(r);d.polygon([(69,79),(84,79),(86,88),(84,97),(83,105),(77,108),(69,107),(65,99),(66,92),(68,86)],fill=255)
rear=(np.array(r)>0)&(a5[...,3]>0)&~protected
for n,m in [('front-pants',frontpants),('front-whole-boot',frontboot),('rear-whole-surface',rear),('upper-hem-complete-gloves',protected)]:smask(m,'masks/source-'+n+'.png')
def grid(rows,cols,target):
 src=np.array([[x,y] for y in rows for x in cols],float);dst=np.array([target(x,y,ri,ci) for ri,y in enumerate(rows) for ci,x in enumerate(cols)],float);tri=[]
 for j in range(len(rows)-1):
  for i in range(len(cols)-1):
   k=j*len(cols)+i;tri.extend([[k,k+len(cols),k+1],[k+1,k+len(cols),k+len(cols)+1]])
 return src,dst,tri
# Cloth has separate hip, knee, cuff controls. Hip stays fixed; round source shading survives.
pan=grid([79,84,89,94,97],[46,53,60,68],lambda x,y,j,i:[x+[0,.3,.7,1,1][j],[79,84,89,94.5,97][j]])
# Cuff, calf, ankle and heel/toe rows deform separately; no whole-leg/whole-body affine.
def front_target(x,y,j,i):
 dx=[1,1,1,1.5*(70-x)/24,2*(70-x)/24][j];dy=[0,0,-.5,-1,-2][j]
 return [x+dx,y+dy]
boo=grid([94,99,104,109,116],[46,52,58,64,70],front_target)
rea=grid([79,84,89,94,99,106],[65,71,77,85],lambda x,y,j,i:[x+[0,-.5,-.5,-1,-.5,-.5][j],[79,83.5,87.5,91.5,97,104][j]])
requests=[('rear-surface',5,rear,rea),('front-pants',4,frontpants,pan),('front-boot',4,frontboot,boo)]
out=a4.copy();lower=(Y>=76)&(X>=45)&(X<=87)&~protected;out[lower]=0
sp=np.full((128,128),4,np.int16);xy=np.stack([X,Y],axis=-1).astype(np.int16);role=np.zeros((128,128),np.int8);sp[lower]=-1;xy[lower]=-1;controls=[]
for rid,(name,sid,own,mesh) in enumerate(requests,1):
 src,dst,tris=mesh;source=a4 if sid==4 else a5;paint=np.zeros((128,128,4),np.uint8);sxy=np.full((128,128,2),-1,np.int16);accepted=np.zeros((128,128),bool);ti=np.full((128,128),-1,np.int16);dets=[]
 for ordinal,t in enumerate(tris):
  s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;dets.append([float(ds),float(dd)]);inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
   for x in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
    bary=inv@np.array([x,y,1.])
    if bary.min()<-1e-8:continue
    sx,sy=np.floor(bary@s+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and own[sy,sx] and source[sy,sx,3]>0:
     paint[y,x]=source[sy,sx];sxy[y,x]=[sx,sy];accepted[y,x]=True;ti[y,x]=ordinal
 accepted&=lower
 out[accepted]=paint[accepted];sp[accepted]=sid;xy[accepted]=sxy[accepted];role[accepted]=rid
 Image.fromarray(paint).save(P/'layers'/f'{rid}-{name}.png');smask(accepted,f'masks/target-{name}.png');np.savez_compressed(P/'maps'/f'{name}.npz',source_xy=sxy,accepted=accepted,triangle=ti)
 controls.append({'name':name,'source_phase':sid,'source_vertices':src.tolist(),'target_vertices':dst.tolist(),'triangles':tris,'determinants':dets,'source_owned_paint_pixels':int(own.sum()),'target_preocclusion_pixels':int(accepted.sum())})
# Source04whole upper/full2Dglove ownership stays byte-identical, including transparent pixels.
assert np.array_equal(out[protected],a4[protected]);assert np.array_equal(out[~lower],a4[~lower])
Image.fromarray(out).save(P/'candidate/04.5.png');np.savez_compressed(P/'maps/04.5-sources.npz',source_phase=sp,source_xy=xy,role=role)
# Saved inverse map is an independent source-coordinate construction witness for every outputRGBA.
replayed=np.zeros_like(out)
for sid,source in [(4,a4),(5,a5)]:
 ys,xs=np.where(sp==sid);pos=xy[ys,xs];replayed[ys,xs]=source[pos[:,1],pos[:,0]]
assert np.array_equal(out,replayed)
(P/'SURFACE-CONTROLS.json').write_text(json.dumps({'pixel_convention':'Integer pixelcentres, inverse barycentric nearest floor(value+0.5), no channel interpolation. Last valid triangle sample wins.','order':['rear05surface','front04pants','front04boot'],'anatomy':'Stylized projected intermediate from visible material surfaces; not recovered anatomy.','parts':controls,'landmarks':{'front04':{'hip':[57,81],'knee':[58,88],'cuff':[55,96],'ankle':[55,104],'heel':[48,110],'toe':[67,111],'sole_inclusive':115},'front_mid_authored':{'hip':[57,81],'knee':[58.6,88],'cuff':[56,96],'ankle':[56,103.5],'heel':[49.4,109],'toe':[67.2,110],'sole_approx':113},'rear05':{'hip':[74,81],'knee':[76,87],'cuff':[75,93],'heel':[72,102],'toe':[79,103],'sole_inclusive':105},'rear_mid_authored':{'hip':[74,81],'knee':[75.5,86],'cuff':[74.1,90.6],'heel':[71.5,100],'toe':[78.5,101],'sole_approx':103}}},indent=2)+'\n')
# Exact endpoints and key-start clock. Midpoint splits04hold; original key starts do not move.
order=['00','01','02','03','04','04.5','05','06','07'];holds=[18,18,18,18,9,9,18,18,18];assert sum(holds)==144
(P/'TIMING.json').write_text(json.dumps({'fps':320,'control_order':[f'{i:02}' for i in range(8)],'control_holds':[18]*8,'candidate_order':order,'candidate_holds':holds,'total_seconds':.45,'original_key_start_ticks320':{f'{i:02}':i*18 for i in range(8)},'midpoint_start_tick320':81,'midpoint_start_seconds':81/320},indent=2)+'\n')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
checks=[]
for i in range(8):
 cp=P/'candidate'/f'{i:02}.png';bp=P/'inputs/control'/f'{i:02}.png';assert cp.read_bytes()==bp.read_bytes();checks.append({'frame':f'{i:02}','sha256':sha(cp),'endpoint_exact_bytes':True})
(P/'TRIAL-RECEIPT.json').write_text(json.dumps({'status':'Unselected one-midpoint projected-surface trial; visual inspection pending.','model_calls':0,'CPU_affinity':sorted(os.sched_getaffinity(0)),'midpoint_sha256':sha(P/'candidate/04.5.png'),'endpoints':checks,'protected_RGBA_exact':True,'outside_lower_RGBA_exact':True,'inverse_source_map_RGBA_exact':True,'new_authored_join_pixels':0,'source_material':'Actual04front rounded pants/complete leather boot, actual05rear rounded knee/cuff/complete leather boot. Projection is authored; no hidden surface recovered.','lower_owner_bbox':[45,76,87,127],'new_midpoint_actual_changed_pixels_vs04':int(np.any(out!=a4,axis=-1).sum()),'clock':'04hold split9/320+9/320; other original starts and .45total unchanged'},indent=2)+'\n')
print('midpoint',sha(P/'candidate/04.5.png'),'source-map exact; endpoints8 unchanged')
