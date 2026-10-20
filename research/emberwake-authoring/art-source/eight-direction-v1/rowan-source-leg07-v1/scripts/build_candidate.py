from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def m(n):return np.array(Image.open(P/n).convert('L'))>0
def save(ar,n):Image.fromarray(ar).save(P/n)
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
src=a('inputs/source06.png');old=a('inputs/original07.png');base=a('inputs/cycle/07.png');Y,X=np.indices((128,128));upper=m('inputs/masks/07-stable-upper-hem-owner.png');gloves=m('inputs/masks/07-opaque-gloves-protected.png')
repair=poly([(32,76),(94,76),(94,126),(32,126)])&~upper
left_owner=m('inputs/masks/screen-left-support-source-owner.png');right_owner=m('inputs/masks/screen-right-swing-source-owner.png')
# The two proximal leg surfaces are the actual06 bent trousers/cuffs, not generated07 shorts.
left_pants=left_owner&(Y<=92);right_pants=right_owner&(Y<=90)
meshes={};layers=[];witness=[]
configs=[('left-proximal06',left_pants,[38,46,54,62,67],[79,82,87,92,96]),('right-bent06-unbending',right_pants,[59,65,71,77,84,91],[71,75,80,85,89,92])]
for name,owner,xs,ys in configs:
 source=np.array([[x,y] for y in ys for x in xs],float);target=[]
 for x,y in source:
  if name=='left-proximal06':dx=0;dy={79:0,82:0,87:-1,92:-3,96:-3}[int(y)]
  else:
   # Fix the projected inner hip, lower the rounded lifted knee, then start straightening the cuff toward00.
   dyrow={71:4,75:4,80:4,85:3,89:2,92:1}[int(y)];weight=np.clip((x-65)/12,0,1);dx=-weight;dy=dyrow*weight
  target.append([x+dx,y+dy])
 target=np.array(target,float);cols=len(xs);rows=len(ys)
 tris=np.array([[r*cols+c,(r+1)*cols+c,r*cols+c+1] for r in range(rows-1) for c in range(cols-1)]+[[r*cols+c+1,(r+1)*cols+c,(r+1)*cols+c+1] for r in range(rows-1) for c in range(cols-1)])
 layer=np.zeros_like(base);xy=np.full((128,128,2),-1,np.int16);owner_out=np.zeros((128,128),bool)
 for tri in tris:
  st,tt=source[tri],target[tri];det=lambda q:np.linalg.det(np.stack([q[1]-q[0],q[2]-q[0]],axis=1));assert det(st)*det(tt)>0
  inv=np.linalg.inv(np.vstack([tt.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(tt[:,1].min()))),min(127,int(np.ceil(tt[:,1].max())))+1):
   for x in range(max(0,int(np.floor(tt[:,0].min()))),min(127,int(np.ceil(tt[:,0].max())))+1):
    bary=inv@np.array([x,y,1])
    if bary.min()<-1e-8:continue
    sx,sy=np.floor(bary@st+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and owner[sy,sx] and repair[y,x]:layer[y,x]=src[sy,sx];xy[y,x]=[sx,sy];owner_out[y,x]=True
 layers.append((name,layer,6));witness.append((name,xy,owner_out));meshes[name]={'source_points':source.tolist(),'target_points':target.tolist(),'triangles':tris.tolist(),'source':'inputs/source06.png','source_owner_rows_through':92 if name=='left-proximal06' else 90}
 save(owner.astype('uint8')*255,f'source-parts/{name}-source-owner.png');save(layer,f'source-parts/{name}.png');np.savez_compressed(P/f'maps/{name}.npz',source_xy=xy,owner=owner_out)
# Complete rounded same-view boot paint:06 support boot retains its longer shaft; old07 forward boot retains full toe/heel volume.
def cream(im):
 r,g,b=[im[...,i].astype(float) for i in range(3)];return (im[...,3]>0)&(r>70)&(g>.70*r)&(b>.63*g)
boot_left=left_owner&(Y>=88)&~cream(src)
boot_right=m('inputs/masks/screen-right-old07-boot-source-owner.png')
bootlayers=[];bootinfo={}
for name,source,source_id,owner,dx,dy in [('left-complete06-boot',src,6,boot_left,0,-6),('right-complete07-boot',old,7,boot_right,0,-2)]:
 layer=np.zeros_like(base);xy=np.full((128,128,2),-1,np.int16);output_owner=np.zeros((128,128),bool)
 for sy,sx in np.argwhere(owner):
  tx,ty=sx+dx,sy+dy
  if 0<=tx<128 and 0<=ty<128 and repair[ty,tx]:layer[ty,tx]=source[sy,sx];xy[ty,tx]=[sx,sy];output_owner[ty,tx]=True
 bootlayers.append((name,layer,source_id));witness.append((name,xy,output_owner));save(owner.astype('uint8')*255,f'source-parts/{name}-source-owner.png');save(layer,f'source-parts/{name}.png');np.savez_compressed(P/f'maps/{name}.npz',source_xy=xy,owner=output_owner)
 bootinfo[name]={'source':'inputs/source06.png' if source_id==6 else 'inputs/original07.png','native_translation':[dx,dy],'complete_visible_source_owner_pixels':int(owner.sum()),'mapped_pixels_before_trouser_occlusion':int(output_owner.sum())}
hip=m('inputs/masks/07-original-trouser-hip-cap.png')&(Y<=84)&repair&(old[...,3]>0);hiplayer=np.zeros_like(base);hiplayer[hip]=old[hip];save(hiplayer,'source-parts/actual07-hipcap.png');save(hip.astype('uint8')*255,'masks/07-actual-hipcap-owner.png')
# Explicit integer source-over retains body underpaint beneath partial-alpha foreground contours.
def over(dst,foreground):
 d=dst.astype(np.int64);s=foreground.astype(np.int64);sa=s[...,3];da=d[...,3];N=sa*255+da*(255-sa);o=np.zeros_like(s)
 o[...,3]=(N+127)//255
 for k in range(3):o[...,k]=np.where(N>0,(s[...,k]*sa*255+d[...,k]*da*(255-sa)+N//2)//np.maximum(N,1),0)
 return o.astype('uint8')
low=np.zeros_like(base)
for name,layer,sid in bootlayers:low=over(low,layer)
low=over(low,hiplayer)
blend=0
for name,layer,sid in layers:blend+=int(((layer[...,3]>0)&(layer[...,3]<255)&(low[...,3]>0)).sum());low=over(low,layer)
out=base.copy();out[repair]=0;out[repair]=low[repair];out[upper]=base[upper];out[gloves]=base[gloves];out[out[...,3]==0]=0
assert np.array_equal(out[~repair],base[~repair]);assert np.array_equal(out[upper|gloves],base[upper|gloves])
for i in range(8):
 if i==7:Image.fromarray(out).save(P/'candidate/07.png')
 else:shutil.copy2(P/'inputs/cycle'/f'{i:02}.png',P/'candidate'/f'{i:02}.png')
save(repair.astype('uint8')*255,'masks/07-lower-repair-owner.png');save(np.any(out!=base,axis=2).astype('uint8')*255,'masks/07-actual-change.png');(P/'maps/proximal-mesh.json').write_text(json.dumps(meshes,indent=2)+'\n')
recipe={'layer_order':['left-complete06-boot','right-complete07-boot','actual07-hipcap','left-proximal06','right-bent06-unbending'],'source_ids':{'6':'inputs/source06.png','7':'inputs/original07.png'},'compositing':'integer source-over; N=sa*255+da*(255-sa); alpha=(N+127)//255; channels=(src*sa*255+dst*da*(255-sa)+N//2)//N','preserve_on_top':['inputs/masks/07-stable-upper-hem-owner.png','inputs/masks/07-opaque-gloves-protected.png'],'proximal_partial_alpha_pixels_with_underpaint':blend,'no_generated07_lower_source':True}
(P/'maps/COMPOSITION.json').write_text(json.dumps(recipe,indent=2)+'\n')
# Preview before packaging, in the actual selected combined cycle context.
def sheet(ids,size,prefix):
 can=Image.new('RGBA',(len(ids)*size,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,bank in enumerate(['inputs/cycle','candidate']):
  for k,i in enumerate(ids):
   im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.alpha_composite(im,(k*size,row*(size+18)+18));d.text((k*size+3,row*(size+18)+2),f'{"current" if row==0 else "source07"} {i:02}',fill='white')
 can.save(P/f'proof/{prefix}.png');return can
for ids,prefix in [(list(range(8)),'full8'),([6,7,0],'06-07-00')]:
 im=sheet(ids,128,prefix+'-native');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(P/f'proof/{prefix}-3x.png');sheet(ids,84,prefix+'-game')
receipt={'status':'ONE no-generation07 source-leg candidate; preview before packaging','generation_calls':0,'candidate07_sha256':hashlib.sha256((P/'candidate/07.png').read_bytes()).hexdigest(),'source06_proximal_trousers':True,'generated07_shorts_preserved':False,'explicit_fixed_inner_hip_and_lowered_rounded_knee':True,'complete_boot_sources':bootinfo,'bounded_actual07_hipcap_pixels':int(hip.sum()),'source_over_partial_alpha_underpaint_pixels':blend,'stable07_upper_hem_whole_visible_gloves_RGBA_exact':True,'other7_PNG_bytes_exact':all((P/'candidate'/f'{i:02}.png').read_bytes()==(P/'inputs/cycle'/f'{i:02}.png').read_bytes() for i in range(7)),'hold':[9,160],'cycle':[9,20],'art_selection':'unselected pending fresh comparison'}
(P/'CANDIDATE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
