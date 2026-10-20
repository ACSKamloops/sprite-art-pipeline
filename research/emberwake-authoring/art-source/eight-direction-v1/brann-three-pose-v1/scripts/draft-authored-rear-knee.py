from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def png(p,a):Image.fromarray(a.astype('uint8')).save(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype('uint8')
yy,xx=np.mgrid[:128,:128]
sources=[arr(ROOT/'inputs/v5-frames'/f'{i:02}.png')for i in range(8)]
# Whole visible source surfaces. Target screen roles are projected, not anatomical limb claims.
parts={
3:[{'id':'right-retreating','source_phase':2,'source_position':'screen-right','translation':[-1,-3],'polygon':[(62,86),(80,86),(84,92),(90,102),(92,115),(65,115),(64,101),(64,95)]},
   {'id':'left-passing-pitched','source_phase':7,'source_position':'screen-right','polygon':[(70,97),(76,96),(80,94),(83,93),(86,92),(89,94),(92,98),(94,117),(73,118),(69,101)],'projection':{'x_translation':-17,'source_y_anchor':93,'target_y_anchor':91,'y_scale':[5,6]}}],
5:[{'id':'right-tucked-recovery','source_phase':7,'source_position':'screen-left','translation':[19,-3],'polygon':[(46,88),(49,86),(63,91),(65,94),(61,98),(65,102),(65,110),(44,110),(44,91)]},
   {'id':'left-forward-recovery','source_phase':6,'source_position':'screen-left-foreground','translation':[-1,1],'polygon':[(51,86),(66,86),(68,91),(68,96),(69,100),(76,104),(77,118),(48,118),(48,91)]}]
}
cloth_polys={
3:[('rear',[(62,85),(74,85),(78,88),(77,94),(70,95),(66,92)]),('front',[(49,85),(61,85),(66,87),(71,90),(70,93),(65,96),(54,97),(50,93),(48,88)]),('crotch',[(59,85),(67,85),(69,88),(65,92),(61,93),(59,90)])],
5:[('rear',[(64,85),(73,85),(78,88),(78,93),(72,95),(67,91)]),('front',[(49,85),(64,85),(67,88),(67,93),(61,96),(51,95),(48,91)]),('crotch',[(60,85),(68,85),(69,89),(65,92),(61,93),(59,90)])]
}
receipt={'status':'unselected three-pose source-pixel hypothesis, preview before editor packaging','model_calls':0,'clock':{'exposures':8,'seconds_each':[9,160],'loop_seconds':[9,20]},'roles':{'A':'02 screen-right extended ->03 right retreating ->04 tucked/right ->05 tucked/right ->06 source-occluded rear','B':'02 left tucked ->03 left pitched passing ->04 left forward ->05 left forward recovery ->06 source left foreground'},'physical_contact_claim':False,'frames':{},'source_hashes':{f'{i:02}':sha(ROOT/'inputs/v5-frames'/f'{i:02}.png')for i in range(8)}}
for i in range(8):
 if i not in [3,4,5]:
  shutil.copy2(ROOT/'inputs/v5-frames'/f'{i:02}.png',ROOT/'frames'/f'{i:02}.png');continue
 base=sources[i]
 if i==4:
  shutil.copy2(ROOT/'inputs/guide04.png',ROOT/'frames/04.png');receipt['frames']['04']={'method':'earlier unselected source-part guide exact PNG','recipe':'inputs/guide04-recipe.json','sha256':sha(ROOT/'frames/04.png')};continue
 upper=yy<=85
 for layer in ['sleeve','far','near','fixed']:upper|=arr(ROOT/'inputs/v5-layers'/f'{i:02}-{layer}.png')[:,:,3]>0
 upper|=poly([(69,84),(74,84),(74,86),(69,86)])&(base[:,:,3]>0)
 erase=(yy>=86)&~upper;body=base.copy();body[erase]=0
 png(ROOT/'layers'/f'{i:02}-after-erasure.png',body);Image.fromarray((upper*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-whole-upper.png');Image.fromarray((erase*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-old-lower-erasure.png')
 pants=np.zeros_like(base);witness=[];donor=sources[0];overlap_cloth=np.zeros_like(base)
 available=[]
 for sy in range(85,94):
  for sx in range(48,79):
   c=donor[sy,sx]
   if c[3]>=240 and max(map(int,c[:3]))<=85 and max(map(int,c[:3]))-min(map(int,c[:3]))<=12:available.append((sx,sy))
 dark=min(available,key=lambda p:sum(map(int,donor[p[1],p[0],:3])))
 for role,points in cloth_polys[i]:
  owner=poly(points)&~upper;edge=owner&(~np.roll(owner,1,0)|~np.roll(owner,-1,0)|~np.roll(owner,1,1)|~np.roll(owner,-1,1))
  for y,x in np.argwhere(owner):
   if edge[y,x]or role=='crotch':sx,sy=dark
   else:sx,sy=min(available,key=lambda p:(p[0]-x)**2+(p[1]-(85+(y-86)*.65))**2)
   pants[y,x]=donor[sy,sx];witness.append({'destination':[int(x),int(y)],'source_phase':0,'source':[sx,sy],'RGBA':donor[sy,sx].tolist(),'role':role+' authored charcoal-trouser join'})
 png(ROOT/'layers'/f'{i:02}-authored-trousers.png',pants);body=over(body,pants)
 descriptions=[]
 for item in parts[i]:
  source=sources[item['source_phase']];owner=poly(item['polygon']);cut=np.zeros_like(source);cut[owner]=source[owner];part=np.zeros_like(source);mp=np.full((128,128,2),-1,dtype='int16')
  if 'translation'in item:
   dx,dy=item['translation'];sxmap=xx-dx;symap=yy-dy
  else:
   pr=item['projection'];sxmap=xx-pr['x_translation'];num,den=pr['y_scale'];symap=np.floor((yy-pr['target_y_anchor'])*den/num+pr['source_y_anchor']+.5).astype('int16')
  valid=(sxmap>=0)&(sxmap<128)&(symap>=0)&(symap<128);syc=np.clip(symap,0,127);sxc=np.clip(sxmap,0,127);valid&=owner[syc,sxc];part[valid]=source[syc[valid],sxc[valid]];mp[valid,0]=sxc[valid];mp[valid,1]=syc[valid]
  png(ROOT/'layers'/f'{i:02}-{item["id"]}-source.png',cut);png(ROOT/'layers'/f'{i:02}-{item["id"]}-placed.png',part);Image.fromarray((owner*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-{item["id"]}-source.png');np.savez_compressed(ROOT/'maps'/f'{i:02}-{item["id"]}.npz',source_xy=mp,source_rgba=source,source_owner=owner)
  before=body.copy();body=over(body,part);visibility=(part[:,:,3]>0)&~upper;Image.fromarray((visibility*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-{item["id"]}-target-visible.png')
  if i==5 and item['id']=='right-tucked-recovery':
   # Rounded charcoal rear proximal chain occludes the top of its actual boot.
   # This is authored cloth ownership in front of the bent cuff, before the
   # complete foreground recovery leg. No distal boot pixels are stretched.
   points=[(65,85),(73,85),(78,86),(81,88),(81,90),(77,92),(72,93),(68,90)]
   own=poly(points)&~upper;edge=own&(~np.roll(own,1,0)|~np.roll(own,-1,0)|~np.roll(own,1,1)|~np.roll(own,-1,1))
   for y,x in np.argwhere(own):
    if edge[y,x]:sx,sy=dark
    else:sx,sy=min(available,key=lambda p:(p[0]-(x-10))**2+(p[1]-(85+(y-86)*.6))**2)
    overlap_cloth[y,x]=donor[sy,sx];witness.append({'destination':[int(x),int(y)],'source_phase':0,'source':[sx,sy],'RGBA':donor[sy,sx].tolist(),'role':'rounded rear proximal trousers in front of bent cuff'})
   png(ROOT/'layers'/'05-rear-proximal-occlusion.png',overlap_cloth);body=over(body,overlap_cloth);Image.fromarray((own*255).astype('uint8')).save(ROOT/'masks'/'05-rear-proximal-occlusion.png')
  item=dict(item);item['literal_source_positive_pixels']=int((owner&(source[:,:,3]>0)).sum());item['placed_positive_pixels']=int((part[:,:,3]>0).sum());item['limitation']='Visible source surface only; hidden anatomy not recovered. Foreground overlap and exact body upper occlude placed surface.';descriptions.append(item)
 body[upper]=base[upper];png(ROOT/'frames'/f'{i:02}.png',body)
 assert np.array_equal(body[upper],base[upper]);assert np.array_equal(body[:86],base[:86])
 receipt['frames'][f'{i:02}']={'parts_in_back_to_front_order':descriptions,'authored_cloth_polygons':cloth_polys[i],'literal_cloth_witnesses':witness,'upper_and_arms_RGBA_exact':True,'changed_pixel_count':int(np.any(body!=base,axis=2).sum()),'sha256':sha(ROOT/'frames'/f'{i:02}.png')}
for i in [0,1,2,6,7]:assert sha(ROOT/'frames'/f'{i:02}.png')==sha(ROOT/'inputs/v5-frames'/f'{i:02}.png')
receipt['five_endpoint_PNG_bytes_exact']=True;save(ROOT/'RECIPE.json',receipt)
BG=(233,233,222,255)
for name,s in [('native',128),('066',84),('2x',256)]:
 for label,phases in [('02-03-04-05-06',[2,3,4,5,6]),('full8',list(range(8)))]:
  sh=Image.new('RGBA',(len(phases)*s,2*(s+18)),BG);d=ImageDraw.Draw(sh)
  for row,folder in enumerate(['inputs/v5-frames','frames']):
   for col,i in enumerate(phases):
    im=Image.open(ROOT/folder/f'{i:02}.png').convert('RGBA').resize((s,s),Image.Resampling.NEAREST);sh.alpha_composite(im,(col*s,row*(s+18)+18));d.text((col*s+2,row*(s+18)+1),f'{"v5"if row==0 else"trial"} {i:02}',fill='black')
  sh.save(ROOT/'proof'/f'{label}-{name}.png')
 for label,phases in [('trial-full8',list(range(8)))]:
  sh=Image.new('RGBA',(len(phases)*s,s+18),BG);d=ImageDraw.Draw(sh)
  for col,i in enumerate(phases):sh.alpha_composite(Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA').resize((s,s),Image.Resampling.NEAREST),(col*s,18));d.text((col*s+2,1),f'{i:02}',fill='black')
  sh.save(ROOT/'proof'/f'{label}-{name}.png')
#Actual fixed-size lower crops on light; no per-cell fitting.
sh=Image.new('RGBA',(8*310,350),BG);d=ImageDraw.Draw(sh)
for i in range(8):
 im=Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA').crop((35,80,97,119)).resize((248,156),Image.Resampling.NEAREST);sh.alpha_composite(im,(i*310,22));d.text((i*310+2,3),f'trial {i:02}; x35 y80 4x',fill='black')
sh.save(ROOT/'proof/lower-full8-4x.png')
print('Manual three-pose preview produced; exact v5 endpoints00/01/02/06/07 and upper ownership retained.')
