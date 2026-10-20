#!/usr/bin/env python3
"""Freeze painted parts once; articulate the same pixels through a walk."""
import math,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
SPECS=[('head',(28,25)),('torso',(21,34)),('scarf',(24,9)),('pelvis',(18,12)),
 ('near_upper_arm',(10,24)),('near_forearm',(9,23)),('far_upper_arm',(10,24)),('far_forearm',(9,23)),
 ('near_thigh',(12,29)),('near_shin',(10,29)),('near_boot',(19,20)),('far_thigh',(12,29)),
 ('far_shin',(10,29)),('far_boot',(19,20)),('armor',(10,10)),('pouch',(9,10))]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def freeze():
 im=Image.open(ROOT/'parts-master.png').convert('RGBA');parts={};notes=[]
 (ROOT/'parts').mkdir(exist_ok=True)
 for i,(name,size) in enumerate(SPECS):
  x=i%4;y=i//4;box=(round(x*im.width/4),round(y*im.height/4),round((x+1)*im.width/4),round((y+1)*im.height/4))
  c=im.crop(box);alpha=c.getchannel('A');bounds=alpha.point(lambda v:255 if v>=128 else 0).getbbox()
  if not bounds:raise ValueError('Missing painted part '+name)
  c=c.crop(bounds).resize(size,Image.Resampling.NEAREST)
  c.putalpha(c.getchannel('A').point(lambda v:255 if v>=160 else 0))
  c.save(ROOT/'parts'/f'{name}.png');parts[name]=c
  notes.append({'name':name,'source_cell':box,'solid_bounds':bounds,'authored_size':size,'pixel_sha256':sha(c.tobytes())})
 (ROOT/'parts-receipt.json').write_text(json.dumps({'master_sha256':sha((ROOT/'parts-master.png').read_bytes()),'policy':'One fixed part extraction/size/alpha normalization before animation. No per-frame redrawing, fitting or anatomy change.','parts':notes},indent=2)+'\n')
 return parts
def ik(a,c,l1,l2,bend):
 dx=c[0]-a[0];dy=c[1]-a[1];d=math.hypot(dx,dy)
 if not abs(l1-l2)<d<=l1+l2:raise ValueError('Unreachable target')
 along=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-along*along))
 return(a[0]+dx/d*along-dy/d*height*bend,a[1]+dy/d*along+dx/d*height*bend)
def put(canvas,image,pivot,target,angle=0):
 co=math.cos(angle);si=math.sin(angle);ox,oy=target;px,py=pivot
 # Inverse mapping; no whole-actor translation or independent recentering.
 layer=image.transform(canvas.size,Image.Transform.AFFINE,(co,si,px-co*ox-si*oy,-si,co,py+si*ox-co*oy),Image.Resampling.NEAREST)
 canvas.alpha_composite(layer)
def bone(canvas,image,a,b):
 theta=math.atan2(b[1]-a[1],b[0]-a[0])-math.pi/2
 put(canvas,image,(image.width/2,3),a,theta)
def pose(p):
 py=84+2*math.sin(4*math.pi*p);pelvis=(70,py);data={'phase':p,'pelvis':pelvis,'feet':{},'joints':{},'contacts':{}}
 for side,offset in [('near',0),('far',.5)]:
  t=(p+offset)%1;stance=.6
  if t<stance:x=70+15-30*t/stance;lift=0
  else:
   q=(t-stance)/(1-stance);x=70-15+30*q*q*(3-2*q);lift=9*math.sin(math.pi*q)
  foot=(x,127-lift);hip=(70+(1 if side=='near' else -1),py+(0 if side=='near' else 1))
  knee=ik(hip,foot,23,23,-1)
  shoulder=(70+(-2 if side=='near' else 1),py-27)
  hand=(70-12*math.cos(2*math.pi*t),py+4-1.5*math.sin(2*math.pi*t))
  elbow=ik(shoulder,hand,18,17,1)
  data['feet'][side]=foot;data['contacts'][side]=t<stance
  data['joints'][side]={'hip':hip,'knee':knee,'ankle':foot,'shoulder':shoulder,'elbow':elbow,'hand':hand}
 return data
def render(parts,p):
 state=pose(p);canvas=Image.new('RGBA',(128,160));py=state['pelvis'][1]
 def leg(side):
  j=state['joints'][side];bone(canvas,parts[side+'_thigh'],j['hip'],j['knee']);bone(canvas,parts[side+'_shin'],j['knee'],j['ankle'])
  put(canvas,parts[side+'_boot'],(6,16),j['ankle'])
 def arm(side):
  j=state['joints'][side];bone(canvas,parts[side+'_upper_arm'],j['shoulder'],j['elbow']);bone(canvas,parts[side+'_forearm'],j['elbow'],j['hand'])
 leg('far');arm('far');put(canvas,parts['armor'],(5,3),state['joints']['far']['shoulder'])
 put(canvas,parts['pelvis'],(9,6),(70,py));leg('near')
 put(canvas,parts['torso'],(11,30),(70,py+3))
 put(canvas,parts['scarf'],(23,4),(67,py-26),.06*math.sin(2*math.pi*p-.8))
 put(canvas,parts['head'],(16,23),(72,py-28))
 arm('near');put(canvas,parts['pouch'],(5,3),(59,py-3))
 return canvas,state
def build():
 for tick in range(48):pose(tick/48)
 parts=freeze();dest=ROOT/'candidate-v4'
 if dest.exists():raise ValueError('Preserve previous animation candidates')
 dest.mkdir();images=[];frames=[]
 for tick in range(48):
  im,state=render(parts,tick/48);im.save(dest/f'{tick:02}.png');images.append(im);frames.append({'tick':tick,'png':f'{tick:02}.png','duration_ticks':1,'pixel_sha256':sha(im.tobytes()),'pose':state})
 images[0].save(dest/'preview.gif',save_all=True,append_images=[images[i] for i in range(2,48,2)],duration=[30,40]*12,loop=0,disposal=2)
 sheet=Image.new('RGB',(1024,688),'#273541');d=ImageDraw.Draw(sheet)
 for i,tick in enumerate(range(0,48,6)):
  x=i%4*256;y=i//4*344;im=images[tick].resize((256,320),Image.Resampling.NEAREST);d.text((x+4,y+3),f'{tick} '+['CONTACT','DOWN','PASSING','UP'][i%4],fill='white');sheet.paste(im,(x,y+24),im)
 sheet.save(dest/'keys-2x.png')
 (dest/'manifest.json').write_text(json.dumps({'schema':'painted-cutout-walk/v1','decision':'unapproved_candidate','canvas':[128,160],'fps':60,'duration_ticks':48,'loop':True,'view':'right','source_parts_sha256':sha((ROOT/'parts-receipt.json').read_bytes()),'builder_sha256':sha(Path(__file__).read_bytes()),'frames':frames,'limits':['Single authored side view only.','No source pixel changes across frames; textures rotate rigidly.','Joint seams, anatomy and motion require actual visual review.','World contact not certified.']},indent=2)+'\n')
 print(json.dumps({'frames':48,'parts':16,'output':str(dest),'art_approved':False}))
if __name__=='__main__':build()
