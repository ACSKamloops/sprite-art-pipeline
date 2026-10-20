from pathlib import Path
import json,hashlib
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def load(n):return np.array(Image.open(P/n).convert('RGBA'))
def save(a,n):Image.fromarray(a).save(P/n)
def poly(pts):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
base=load('inputs/A/07.png');donor=load('inputs/A/06.png');source=load('inputs/upper/source02.png')
arms=[np.array(Image.open(P/'inputs/upper'/f'{n}-arm-owner.png').convert('L'))>0 for n in ['left','right']]
def arm_owner(phase):
 sw=[0,-1,-2,-1,0,1,2,1][phase];bob=[0,1,1,0,0,1,1,0][phase];own=np.zeros((128,128),bool);paint=np.zeros_like(base)
 for k,dx in [(0,sw),(1,-sw)]:
  for y,x in np.argwhere(arms[k]):
   tx,ty=x+dx,y+bob
   if 0<=tx<128 and 0<=ty<128:own[ty,tx]=1;paint[ty,tx]=source[y,x]
 return own,paint
oldarm,oldpaint=arm_owner(6);newarm,newpaint=arm_owner(7)
oldarm_visible=oldarm&(oldpaint[...,3]>0)&np.all(oldpaint==donor,axis=2)
newarm_opaque=newarm&(newpaint[...,3]>0)
# Original shared source02 torso/hem owner is shifted up one native pixel from phase05 (bob1) to phase07 (bob0).
torso05=np.array(Image.open(P/'inputs/masks/05-stable-torso-hem-owner.png').convert('L'))>0
torso=np.zeros((128,128),bool);torso[:-1]=torso05[1:];torso[0]=True
repair=poly([(32,76),(94,76),(94,126),(32,126)])&~torso
support=poly([(42,81),(62,81),(65,88),(64,102),(65,109),(59,112),(40,112),(39,101),(40,88)])&~oldarm_visible&(donor[...,3]>0)
swing=poly([(63,82),(68,79),(73,74),(83,73),(89,78),(89,88),(86,91),(86,102),(82,105),(63,105),(61,96)])&~oldarm_visible&(donor[...,3]>0)
Y,X=np.indices((128,128))
# Remove the donor's attached old blue/gold waist tab from the leg owner.
swing &= ~((X<=71)&(Y<=84))
support&=~swing
# Meshes move proximal source paint modestly while each COMPLETE source boot is a rigid translated plateau.
# Projected side names describe the image, not unverified anatomical left/right.
source_points={
 'screen-left-support':[[x,y] for y in [79,82,87,92,108,114] for x in [38,46,54,62,67]],
 'screen-right-swing':[[x,y] for y in [71,75,80,85,89,103,108] for x in [59,65,71,77,84,91]]}
transforms={
 'screen-left-support':{79:(0,0),82:(0,0),87:(0,-1),92:(0,-3),108:(0,-3),114:(0,-3)},
 'screen-right-swing':{71:(0,4),75:(0,4),80:(0,4),85:(1,5),89:(1,5),103:(1,5),108:(1,5)}}
meshes={};layers=[];witness=[]
for name,mask in [('screen-left-support',support),('screen-right-swing',swing)]:
 src=np.array(source_points[name],dtype=float)
 dst=np.array([[x+transforms[name][int(y)][0],y+transforms[name][int(y)][1]] for x,y in src],dtype=float)
 cols=5 if name=='screen-left-support' else 6;rows=len(src)//cols
 tris=np.array([[r*cols+c,(r+1)*cols+c,r*cols+c+1] for r in range(rows-1) for c in range(cols-1)]+[[r*cols+c+1,(r+1)*cols+c,(r+1)*cols+c+1] for r in range(rows-1) for c in range(cols-1)])
 out=np.zeros_like(donor);xy=np.full((128,128,2),-1,np.int16);owner=np.zeros((128,128),bool)
 for tri in tris:
  st,tt=src[tri],dst[tri]
  assert np.linalg.det(np.stack([st[1]-st[0],st[2]-st[0]],axis=1))*np.linalg.det(np.stack([tt[1]-tt[0],tt[2]-tt[0]],axis=1))>0
  mat=np.linalg.inv(np.vstack([tt.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(tt[:,1].min()))),min(127,int(np.ceil(tt[:,1].max())))+1):
   for x in range(max(0,int(np.floor(tt[:,0].min()))),min(127,int(np.ceil(tt[:,0].max())))+1):
    b=mat@np.array([x,y,1]);
    if np.min(b)<-1e-8:continue
    sx,sy=np.floor(b@st+0.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and mask[sy,sx]:out[y,x]=donor[sy,sx];xy[y,x]=[sx,sy];owner[y,x]=1
 layers.append(out);witness.append((owner,xy))
 meshes[name]={'source_points':src.astype(int).tolist(),'target_points':dst.astype(int).tolist(),'triangles':tris.tolist()}
 save(mask.astype('uint8')*255,f'guide/{name}-source-owner.png');save(out,f'guide/{name}-paint.png')
# Clear all obsolete lower paint first, then place complete source-derived lower parts.
out=base.copy();out[repair]=0;sid=np.full((128,128),-1,np.int8);xy=np.full((128,128,2),-1,np.int16)
# The literal source07 trouser hip cap completes proximal coverage under the new legs.
hip=poly([(54,78),(66,77),(72,79),(77,85),(73,89),(65,88),(58,86),(53,83)])&repair&(base[...,3]>0)
out[hip]=base[hip];sid[hip]=3
for yy,xx in np.argwhere(hip):xy[yy,xx]=[xx,yy]
save(hip.astype('uint8')*255,'guide/07-original-trouser-hip-cap.png')
for i,(paint,(own,mapping)) in enumerate(zip(layers,witness),1):
 m=own&repair;out[m]=paint[m];sid[m]=i;xy[m]=mapping[m]
# Stable upper, blue/gold hem, and whole original07 visible gloves retain their exact source RGBA.
out[torso]=base[torso];out[newarm_opaque]=base[newarm_opaque];sid[torso|newarm_opaque]=-1;xy[torso|newarm_opaque]=-1
# Transparent donor owner is deliberately not copied over valid body underpaint.
assert np.array_equal(out[torso],base[torso]);assert np.array_equal(out[newarm_opaque],base[newarm_opaque])
assert np.array_equal(out[~repair],base[~repair])
save(out,'guide/proposed07.png')
for m,n in [(repair,'07-lower-repair-owner'),(torso,'07-stable-upper-hem-owner'),(newarm,'07-complete-arm-owner'),(newarm_opaque,'07-opaque-gloves-protected'),(np.any(out!=base,axis=2),'07-actual-change')]:save(m.astype('uint8')*255,f'guide/{n}.png')
np.savez_compressed(P/'guide/source06-lower-map.npz',source_id=sid,source_xy=xy)
(P/'guide/mesh.json').write_text(json.dumps(meshes,indent=2)+'\n')
rows=[('source06',load('inputs/A/06.png')),('proposed07',out),('source00',load('inputs/A/00.png'))]
for size,label in [(128,'native'),(84,'game')]:
 can=Image.new('RGBA',(3*size,size+18),(29,34,43,255));d=ImageDraw.Draw(can)
 for j,(name,a) in enumerate(rows):can.alpha_composite(Image.fromarray(a).resize((size,size),Image.Resampling.NEAREST),(j*size,18));d.text((j*size+3,2),name,fill='white')
 can.save(P/f'guide/06-guide07-00-{label}.png')
 if size==128:can.resize((can.width*4,can.height*4),Image.Resampling.NEAREST).save(P/'guide/06-guide07-00-4x.png')
receipt={'status':'COMPLETE PAINTED GUIDE FOR PARENT REVIEW; no ImageGen call yet','guide':'guide/proposed07.png','source':'inputs/A/06.png','target':'inputs/A/07.png','direction':'SE','stage':[128,128],'pivot':[64,112],'source_pixel_part_construction':True,'authored_hidden_anatomy':False,'literal_source07_hip_cap_pixels':int(hip.sum()),'boot_motion':{'screen-left-support':[0,-3],'screen-right-swing':[1,5]},'whole_original07_visible_gloves_exact':True,'stable_upper_blue_gold_hem_exact':True,'outside_repair_exact':True,'old_lower_cleared_before_parts':True,'transparent_arm_owner_does_not_erase_valid_body':True,'complete_visible_source_leg_pixels':[int(support.sum()),int(swing.sum())],'changed07_pixels':int(np.any(out!=base,axis=2).sum()),'guide_sha256':hashlib.sha256((P/'guide/proposed07.png').read_bytes()).hexdigest()}
(P/'guide/RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
