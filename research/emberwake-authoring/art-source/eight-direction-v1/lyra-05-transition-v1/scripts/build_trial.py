from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];Y,X=np.indices((128,128))
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def m(n):return np.array(Image.open(P/n).convert('L'))>0
def save(ar,n):Image.fromarray(ar).save(P/n)
def shift(ar,dx,dy):
 out=np.zeros_like(ar);ys,xs=np.where(ar);xx=xs+dx;yy=ys+dy;ok=(xx>=0)&(xx<128)&(yy>=0)&(yy<128);out[yy[ok],xx[ok]]=ar[ys[ok],xs[ok]];return out

def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0

def over(body,part):
 owned=part[...,3]>0;partial=owned&(part[...,3]<255)&(body[...,3]>0);d=body.astype('int64');s=part.astype('int64');sa=s[...,3];da=d[...,3];n=sa*255+da*(255-sa);out=body.copy();out[owned&~partial]=part[owned&~partial]
 for k in range(3):out[...,k][partial]=(s[...,k][partial]*sa[partial]*255+d[...,k][partial]*da[partial]*(255-sa[partial])+n[partial]//2)//n[partial]
 out[...,3][partial]=(n[partial]+127)//255
 return out,[[int(x),int(y)]for y,x in np.argwhere(partial)]
source={i:a(f'inputs/cycle/{i:02}.png')for i in [2,6]};base=a('inputs/cycle/05.png');up=np.load(P/'inputs/05-upstream-visible-source-map.npz')
# Final visible torso/hem/socket ownership plus entire posed arms, rather than
# preserving old crossed trouser pixels merely because they overlap a body ROI.
visible_upper=np.isin(up['layer_id'],[0,4,5,6])
arm=shift(m('inputs/ownership/left-arm-owner.png'),1,1)|shift(m('inputs/ownership/right-arm-owner.png'),-1,1)
protected=visible_upper|arm|(Y<=76)
repair=poly([(30,77),(95,77),(95,124),(30,124)])&~protected
save(protected.astype('uint8')*255,'masks/05-upper-hem-full-gloves-protected.png');save(arm.astype('uint8')*255,'masks/05-full-arm-owner.png');save(repair.astype('uint8')*255,'masks/05-repair-owner.png')
# The whole visible source6 partitions are frozen in the inspected03/04 package.
# Their hidden anatomy is unknown; this is a new authored layout of visible paint.
parts=[{'id':'right-rear','source_phase':6,'owner':'06-right-source-leg-owner.png','xs':[59,65,71,77,84,91],'ys':[72,78,84,90,96,108],'row_displacements':{72:[0,0],78:[0,0],84:[-1,0],90:[-1,1],96:[-1,1],108:[-1,1]},'role':'P rear/swing; pass behind left/front support, distinct rounded source06 bent boot','cuff':[77,87],'heel':[76,102],'toe':[84,104]},
 {'id':'left-front','source_phase':6,'owner':'06-left-source-leg-owner.png','xs':[37,44,51,58,65,69],'ys':[79,83,88,94,100,115],'row_displacements':{79:[0,0],83:[0,0],88:[1,1],94:[2,2],100:[2,2],115:[2,2]},'role':'Q front/support; keep continuous projected left lane from new04 toward actual06','cuff':[54,96],'heel':[48,110],'toe':[61,111]}]
body=base.copy();body[repair]=0;save(body,'layers/05-cleared-body.png')
hip=m('inputs/ownership/hip-underlay.png')&repair&(source[2][...,3]>0);under=np.zeros_like(base);under[hip]=source[2][hip];body,hipblends=over(body,under);save(under,'layers/05-actual02-hip-underpaint.png');save(hip.astype('uint8')*255,'masks/05-actual02-hip-underpaint.png')
recipe=[];blend=[]
for b in parts:
 donor=source[b['source_phase']];owner=m('inputs/source-parts/'+b['owner']);src=np.array([[x,y]for y in b['ys']for x in b['xs']],float);dst=np.array([[x+b['row_displacements'][int(y)][0],y+b['row_displacements'][int(y)][1]]for x,y in src],float);cols=len(b['xs']);rows=len(b['ys']);tris=np.array([[r*cols+c,(r+1)*cols+c,r*cols+c+1]for r in range(rows-1)for c in range(cols-1)]+[[r*cols+c+1,(r+1)*cols+c,(r+1)*cols+c+1]for r in range(rows-1)for c in range(cols-1)])
 mapping=np.full((128,128,2),-1,np.int16);paint=np.zeros_like(base);owned=np.zeros((128,128),bool)
 for tri in tris:
  st,tt=src[tri],dst[tri];det=lambda q:np.linalg.det(np.stack([q[1]-q[0],q[2]-q[0]],axis=1));assert det(st)*det(tt)>0
  inv=np.linalg.inv(np.vstack([tt.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(tt[:,1].min()))),min(127,int(np.ceil(tt[:,1].max())))+1):
   for x in range(max(0,int(np.floor(tt[:,0].min()))),min(127,int(np.ceil(tt[:,0].max())))+1):
    bary=inv@np.array([x,y,1])
    if bary.min()<-1e-8:continue
    sx,sy=np.floor(bary@st+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and owner[sy,sx]and repair[y,x]:paint[y,x]=donor[sy,sx];mapping[y,x]=[sx,sy];owned[y,x]=True
 body,partial=over(body,paint);blend.append({'part':b['id'],'source_over_coordinates':partial});save(paint,f'layers/05-{b["id"]}.png');np.savez_compressed(P/f'maps/05-{b["id"]}.npz',source_xy=mapping,owner=owned,source_phase=np.array(b['source_phase']))
 recipe.append({**b,'source_points':src.tolist(),'target_points':dst.tolist(),'triangles':tris.tolist(),'source_visible_positive_pixels':int(owner.sum()),'placed_positive_pixels':int(owned.sum()),'toe_reflection':False,'limitation':'Only actual visible source texels; connected authored projection is not recovered hidden anatomy.'})
body[protected]=base[protected];body[body[...,3]==0]=0
assert np.array_equal(body[protected],base[protected]);assert np.array_equal(body[~repair],base[~repair])
save(body,'candidate/05.png');save(np.any(body!=base,axis=2).astype('uint8')*255,'masks/05-actual-change.png')
for i in range(8):
 if i!=5:shutil.copy2(P/'inputs/cycle'/f'{i:02}.png',P/'candidate'/f'{i:02}.png')
receipt={'status':'ONE meaningful no-generation05 lower candidate; preview pending; no score or selection','actor':'Lyra','view':'southeast','model_calls':0,'source_package':'emberwake-lyra-se-contact-repair-v1','authoring':'Explicit new05 layout of actual visible source06 two distinct legs and bounded actual02 hip underpaint; not recovered hidden anatomy','stage':[128,128],'pivot':[64,112],'clock':{'holds':[[9,160]]*8,'loop':[9,20]},'roles':{'P':'new04 right/rear bent boot →05 rear/swing(-1,+1 distal) →06 actual right/rear bent boot','Q':'new04 left/front(+4,+4 distal) →05 left/front(+2,+2) →06 actual left/front(0,0)'},'clearing':'Old lower cleared first; actual02 hip underpaint behind positive source6 paint; transparent donor never punches valid underpaint','protected':'Actual final upstream visible torso/hem/socket layers0/4/5/6 plus complete posed arm masks(left+1,+1;right-1,+1) and full rows<=76. Final RGBA copied from actual05; crossed knee/boot owners7/8 are repairable.','hip_underpaint_pixels':int(hip.sum()),'hip_alpha_blends':hipblends,'part_alpha_blends':blend,'parts':recipe,'candidate05_sha256':hashlib.sha256((P/'candidate/05.png').read_bytes()).hexdigest(),'actual_changed_pixels':int(np.any(body!=base,axis=2).sum()),'actual_upper_hem_full_gloves_RGBA_exact':True,'other7_PNG_bytes_exact':all((P/'candidate'/f'{i:02}.png').read_bytes()==(P/'inputs/cycle'/f'{i:02}.png').read_bytes()for i in range(8)if i!=5),'wholepose_fit_or_recentering':False,'limited_new_join_pencil_pixels':0}
(P/'RECIPE.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k]for k in ['candidate05_sha256','actual_changed_pixels','hip_underpaint_pixels','actual_upper_hem_full_gloves_RGBA_exact','other7_PNG_bytes_exact']}))
