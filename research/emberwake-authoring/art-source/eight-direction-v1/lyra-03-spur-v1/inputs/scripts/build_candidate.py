from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
Y,X=np.indices((128,128))
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def m(n):return np.array(Image.open(P/n).convert('L'))>0
def save(ar,n):Image.fromarray(ar).save(P/n)
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
sources={i:a(f'inputs/A/{i:02}.png') for i in [0,2,6]}
# Visible source ownership stays separate from an anatomical completeness claim.
polys={(2,'left'):[(45,81),(64,81),(65,94),(65,105),(43,105),(42,91)],(2,'right'):[(63,81),(81,81),(88,95),(91,117),(63,117),(62,95)],(6,'left'):[(43,80),(65,80),(65,96),(66,114),(38,114),(38,94),(42,86)],(6,'right'):[(64,74),(84,74),(90,82),(89,95),(87,107),(63,107),(61,90)]}
sourceowners={}
for (phase,side),points in polys.items():
 src=sources[phase];lower=m(f'inputs/ownership/{phase:02}-lower-owner.png');fore=m(f'inputs/ownership/{phase:02}-foreground-knee.png');boot=m(f'inputs/ownership/{phase:02}-complete-boot.png');owner=poly(points)&(lower|fore|boot)&(src[...,3]>0)
 rgb=src[...,:3].astype(int);neutral=(rgb.max(axis=2)-rgb.min(axis=2)<28)&(rgb[...,0]<135)
 # Above the known leather cuff, use only actual charcoal trouser texture. This excludes fixed gloves/coat.
 cutoff=85 if side=='right' and phase==6 else 87
 owner &= (Y>=cutoff)|neutral
 owner &= ~((rgb[...,1]-rgb[...,0]>8)&(rgb[...,1]>=rgb[...,2]-2))
 sourceowners[(phase,side)]=owner;save(owner.astype('uint8')*255,f'source-parts/{phase:02}-{side}-source-leg-owner.png')
# Disjoint source leg claims at the crotch; projected sides are not verified anatomical identities.
for phase in [2,6]:
 sourceowners[(phase,'left')] &= ~sourceowners[(phase,'right')]
 save(sourceowners[(phase,'left')].astype('uint8')*255,f'source-parts/{phase:02}-left-source-leg-owner.png')

def controls(phase,side,xs,ys):
 src=np.array([[x,y] for y in ys for x in xs],float);dst=[]
 for x,y in src:
  if phase==4 and side=='left':
   dx,dy={79:(0,0),83:(1,0),88:(3,1),94:(4,4),100:(4,4),115:(4,4)}[int(y)]
  elif phase==4:
   dx,dy=(-3,2)
  elif side=='left':
   dx,dy={79:(0,0),83:(0,0),87:(1,2),90:(3,6),94:(3,6),98:(3,6),107:(3,6)}[int(y)]
   if y>=94:dx+=max(0,(y-94)/7)*np.clip((x-50)/14,0,1)
  else:dx,dy={79:(0,0),83:(0,0),88:(-1,-1),94:(-2,-5),100:(-2,-5),118:(-2,-5)}[int(y)]
  dst.append([x+dx,y+dy])
 return src,np.array(dst,float)
configs={4:[('right',6,[59,65,71,77,84,91],[72,78,84,90,96,108]),('left',6,[37,44,51,58,65,69],[79,83,88,94,100,115])],3:[('right',2,[59,65,71,78,85,92],[79,83,88,94,100,118]),('left',2,[41,47,53,59,65,69],[79,83,87,90,94,98,107])]}
receipts=[];allmeshes={}
for phase in [4,3]:
 base=a(f'inputs/A/{phase:02}.png');upper=m(f'masks/{phase:02}-stable-upper-hem-owner.png');gloves=m(f'masks/{phase:02}-full-visible-gloves-owner.png');repair=(~upper)&poly([(30,77),(95,77),(95,124),(30,124)])
 out=base.copy();out[repair]=0;sid=np.full((128,128),-1,np.int16);xy=np.full((128,128,2),-1,np.int16);layerid=np.full((128,128),-1,np.int8)
 # Literal actual02 charcoal hip underpaint; new source ownership does not imply recovered hidden thighs.
 hip=m('inputs/ownership/hip-underlay.png')&repair&(sources[2][...,3]>0);out[hip]=sources[2][hip];sid[hip]=2;layerid[hip]=0
 for y,x in np.argwhere(hip):xy[y,x]=[x,y]
 details=[];blend_points=[]
 for layer,(side,donorphase,xs,ys) in enumerate(configs[phase],1):
  donor=sources[donorphase];owner=sourceowners[(donorphase,side)];src,dst=controls(phase,side,xs,ys);cols=len(xs);rows=len(ys);tris=np.array([[r*cols+c,(r+1)*cols+c,r*cols+c+1] for r in range(rows-1) for c in range(cols-1)]+[[r*cols+c+1,(r+1)*cols+c,(r+1)*cols+c+1] for r in range(rows-1) for c in range(cols-1)])
  painted=np.zeros_like(base);mapping=np.full((128,128,2),-1,np.int16);owned=np.zeros((128,128),bool)
  for tri in tris:
   st,tt=src[tri],dst[tri];det=lambda q:np.linalg.det(np.stack([q[1]-q[0],q[2]-q[0]],axis=1));assert det(st)*det(tt)>0
   inv=np.linalg.inv(np.vstack([tt.T,np.ones(3)]))
   for y in range(max(0,int(np.floor(tt[:,1].min()))),min(127,int(np.ceil(tt[:,1].max())))+1):
    for x in range(max(0,int(np.floor(tt[:,0].min()))),min(127,int(np.ceil(tt[:,0].max())))+1):
     bary=inv@np.array([x,y,1])
     if bary.min()<-1e-8:continue
     sx,sy=np.floor(bary@st+.5).astype(int)
     if 0<=sx<128 and 0<=sy<128 and owner[sy,sx] and repair[y,x]:painted[y,x]=donor[sy,sx];mapping[y,x]=[sx,sy];owned[y,x]=True
  # Positive source paint only; no transparent donor owner punches new body underpaint.
  partial=owned&(painted[...,3]<255)&(out[...,3]>0)
  for yy,xx in np.argwhere(partial):
   sr,sg,sb,sa=map(int,painted[yy,xx]);dr,dg,db,da=map(int,out[yy,xx]);N=sa*255+da*(255-sa);out[yy,xx]=[(c*sa*255+d*da*(255-sa)+N//2)//N for c,d in [(sr,dr),(sg,dg),(sb,db)]]+[(N+127)//255];blend_points.append([int(xx),int(yy)])
  out[owned&~partial]=painted[owned&~partial];sid[owned]=donorphase;xy[owned]=mapping[owned];layerid[owned]=layer
  save(painted,f'source-parts/{phase:02}-{side}-mapped-leg.png');np.savez_compressed(P/f'maps/{phase:02}-{side}-leg.npz',source_xy=mapping,owner=owned,source_phase=np.array(donorphase));allmeshes[f'{phase:02}-{side}']={'source_phase':donorphase,'source_points':src.tolist(),'target_points':dst.tolist(),'triangles':tris.tolist(),'boot_projection':'04 complete06 boots rigid native placement;03 left forefoot opens by bounded native shear,03 right boot rigidly retreats','toe_reflection':False};details.append({'projected_side':side,'source_phase':donorphase,'mapped_pixels':int(owned.sum()),'source_leg_pixels':int(owner.sum())})
 out[upper]=base[upper];out[gloves]=base[gloves];sid[upper|gloves]=-1;xy[upper|gloves]=-1;layerid[upper|gloves]=-1;out[out[...,3]==0]=0
 assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[gloves],base[gloves]);assert np.array_equal(out[~repair],base[~repair])
 save(out,f'candidate/{phase:02}.png');save(repair.astype('uint8')*255,f'masks/{phase:02}-repair-owner.png');save(hip.astype('uint8')*255,f'masks/{phase:02}-actual02-hip-underpaint.png');save(np.any(out!=base,axis=2).astype('uint8')*255,f'masks/{phase:02}-actual-change.png');np.savez_compressed(P/f'maps/{phase:02}-composition.npz',source_id=sid,source_xy=xy,layer_id=layerid)
 receipts.append({'phase':phase,'original_full_upper_hem_RGBA_exact':True,'original_full_visible_gloves_RGBA_exact':True,'other_RGBA_outside_lower_owner_exact':True,'actual02_hip_underpaint_pixels':int(hip.sum()),'source_over_partial_alpha_underpaint_pixels':len(blend_points),'source_over_coordinates':blend_points,'parts':details,'candidate_sha256':hashlib.sha256((P/f'candidate/{phase:02}.png').read_bytes()).hexdigest(),'changed_pixels':int(np.any(out!=base,axis=2).sum())})
for i in range(8):
 if i not in [3,4]:shutil.copy2(P/'inputs/A'/f'{i:02}.png',P/'candidate'/f'{i:02}.png')
for key,v in allmeshes.items():
 if key=='04-left':v['boot_projection']='Whole06 support boot visible paint; distal rows>=94 translate(+4,+4), proximal cuff shares continuous authored leg mesh'
 elif key=='04-right':v['boot_projection']='Whole06 bent/rear visible boot translates(-3,+2), same toe orientation'
 elif key=='03-left':v['boot_projection']='Whole02 visible boot descends(+3,+6); bounded forefoot shear opens toe by at most2 native pixels, no reflection'
 else:v['boot_projection']='Whole02 visible boot distal rows>=94 translate(-2,-5), with connected proximal trouser map'
(P/'maps/control-meshes.json').write_text(json.dumps(allmeshes,indent=2)+'\n')
(P/'maps/COMPOSITION.json').write_text(json.dumps({'layer_order':['actual02 hip underpaint','right/rear mapped leg','left/front mapped leg','exact original full upper/hem/visible gloves'],'partial_alpha_rule':'Integer source-over when existing body underpaint is present; sourcealpha0 never erases valid body','single_map_semantics':'Primary foreground source coordinates; final overlapping contour RGBA may blend it with the earlier mapped layer','replay_authority':'Per-leg integer maps plus hip mask and stated layer order'},indent=2)+'\n')
def sheet(ids,size,prefix):
 can=Image.new('RGBA',(len(ids)*size,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,bank in enumerate(['inputs/A','candidate']):
  for k,i in enumerate(ids):can.alpha_composite(Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST),(k*size,row*(size+18)+18));d.text((k*size+3,row*(size+18)+2),f'{"current" if row==0 else "source"} {i:02}',fill='white')
 can.save(P/f'proof/{prefix}.png');return can
for ids,prefix in [(list(range(8)),'full8'),([2,3,4,5,6],'02-03-04-05-06')]:
 im=sheet(ids,128,prefix+'-native');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(P/f'proof/{prefix}-3x.png');sheet(ids,84,prefix+'-game')
report={'status':'ONE bounded03/04 source-pixel candidate; inspect before editor packaging','actor':'Lyra','view':'southeast','generation_calls':0,'role_intent':{'screen-left':'02 swinging/tucked →03 descending →04 low/forward support sourced from06 →05/06 opposite support','screen-right':'02 low first support →03 retreating →04 higher rear/bent whole06 boot; retain projection, no mirrored toe'},'new_authored_layout_not_recovered_hidden_anatomy':True,'full_boot_geometry_not_shared_identical_front_boot':True,'fixed_wholepose_fit_or_recenter':False,'phases':receipts,'unchanged_other6_PNG_bytes_exact':all((P/'candidate'/f'{i:02}.png').read_bytes()==(P/'inputs/A'/f'{i:02}.png').read_bytes() for i in range(8) if i not in [3,4]),'holds':[[9,160]]*8,'cycle':[9,20],'inherited_quality_score':None}
(P/'CANDIDATE-RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
