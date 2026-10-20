from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parents[1]
def load(n):return np.array(Image.open(P/n).convert('RGBA'))
def save(a,n):Image.fromarray(a).save(P/n)
def poly(pts):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
base=load('inputs/A/05.png');donor=load('inputs/A/06.png');source=load('inputs/upper/source02.png')
arms=[np.array(Image.open(P/'inputs/upper'/f'{n}-arm-owner.png'))>0 for n in ['left','right']]
def arm_owner(phase):
 sw=[0,-1,-2,-1,0,1,2,1][phase];bob=[0,1,1,0,0,1,1,0][phase];own=np.zeros((128,128),bool);paint=np.zeros_like(base)
 for k,dx in [(0,sw),(1,-sw)]:
  for y,x in np.argwhere(arms[k]):
   tx,ty=x+dx,y+bob
   if 0<=tx<128 and 0<=ty<128:own[ty,tx]=1;paint[ty,tx]=source[y,x]
 return own,paint
oldarm,oldpaint=arm_owner(6);newarm,newpaint=arm_owner(5)
oldarm_visible=oldarm & (oldpaint[...,3]>0) & np.all(oldpaint==donor,axis=2)
newarm_opaque=newarm & (newpaint[...,3]>0)
ma=poly([(42,81),(62,81),(65,88),(64,102),(65,109),(59,112),(40,112),(39,101),(40,88)]) & ~oldarm_visible
mb=poly([(63,82),(68,79),(73,74),(83,73),(89,78),(89,88),(86,91),(86,102),(82,105),(63,105),(61,96)]) & ~oldarm_visible
# Isolated visible source pixels only; all source boot and knee pixels stay rigid, same orientation.
# Source A (screen-left leg) supporting foot shifts +2,+2; source B swing knee/boot shifts -3,+5.
ma &= (donor[...,3]>0);mb &= (donor[...,3]>0);ma &= ~mb
# Complete lower ownership clears old05 feet and old high knee; complete gloves restored afterwards.
repair=poly([(32,80),(49,80),(49,77),(83,77),(83,72),(94,72),(94,126),(32,126)])
out=base.copy();out[repair]=0
sid=np.full((128,128),-1,np.int8);xy=np.full((128,128,2),-1,np.int16);layer=np.zeros((128,128),np.int8)
for k,(mask,dx,dy) in enumerate([(ma,2,2),(mb,-3,5)],1):
 for y,x in np.argwhere(mask):
  tx,ty=x+dx,y+dy
  if 0<=tx<128 and 0<=ty<128 and repair[ty,tx]:out[ty,tx]=donor[y,x];sid[ty,tx]=6;xy[ty,tx]=[x,y];layer[ty,tx]=k
# Keep the literal stable hem/waist from A05 (thin source-derived hip cap), not invented hidden anatomy.
hip=poly([(48,78),(79,77),(82,82),(76,84),(68,83),(62,85),(49,84)])
hip &= repair & (base[...,3]>0) & ((out[...,3]==0) | (np.indices((128,128))[0]<80))
out[hip]=base[hip];sid[hip]=5;layer[hip]=3
for y,x in np.argwhere(hip):xy[y,x]=[x,y]
# Protect full 2D arm ownership. Preserve original05 RGBA in its complete arm owner.
out[newarm_opaque]=newpaint[newarm_opaque];sid[newarm_opaque]=-1;xy[newarm_opaque]=-1;layer[newarm_opaque]=0
# Outside lower owner and complete arms must remain exact original05.
assert np.array_equal(out[~(repair|newarm)],base[~(repair|newarm)])
save(out,'source-part-proposal/05.png')
for mask,n in [(ma,'donor06-support-owner'),(mb,'donor06-swing-owner'),(repair,'05-lower-repair-owner'),(newarm,'05-complete-arm-owner'),(hip,'05-source-hip-cap')]:save(mask.astype('uint8')*255,f'source-part-proposal/{n}.png')
np.savez_compressed(P/'source-part-proposal/05-source-map.npz',source_id=sid,source_xy=xy,layer_id=layer)
receipt={'status':'unselected source-part proposal; new05 only','donor':'A06 complete visible legs, source alpha only; no recovered hidden anatomy','leg_A_screen_left_source_shift':[2,2],'leg_B_screen_right_source_shift':[-3,5],'rigid_all_visible_knee_boot_pixels':True,'source05_hip_cap_pixels':int(hip.sum()),'authored_underpaint':0,'glove_transparency_handling':'full old-part clear before leg composition; only visible opaque original05 gloves over leg paint; negative arm-owner pixels may now contain body behind glove','layer_order':['A05 outside repair','erased old05 lower','source06 support','source06 swing','literal source05 hem/hip cap','complete source02 arms at phase05 offsets'],'source_pixels':{'support':int(ma.sum()),'swing':int(mb.sum())},'note':'Any missing proximal donor coverage stays transparent; guide only until visual inspection.'}
(P/'source-part-proposal/RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
rows=[('A04',load('inputs/A/04.png')),('A05 control',base),('proposed05',out),('A06',donor)]
canvas=Image.new('RGBA',(512,146),(29,34,43,255));d=ImageDraw.Draw(canvas)
for j,(label,a) in enumerate(rows):canvas.alpha_composite(Image.fromarray(a),(j*128,18));d.text((j*128+4,2),label,fill='white')
canvas.save(P/'source-part-proposal/comparison-native.png');canvas.resize((2048,584),Image.Resampling.NEAREST).save(P/'source-part-proposal/comparison-4x.png')
print(json.dumps(receipt))
