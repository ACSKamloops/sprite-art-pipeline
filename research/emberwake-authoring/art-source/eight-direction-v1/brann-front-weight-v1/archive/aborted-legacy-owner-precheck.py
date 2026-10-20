"""ONE authored body-weight XY curve after fixed registration. No pose fitting.
Literal current-source cloth owners; complete retained lower layers stay fixed.
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];L=Path('/home/astra/artifacts/emberwake-brann-full-lower-paint-v1/manual-pilot-v2');T=R/'single-curve-v1'
for n in ['frames','layers','maps','masks','proof','inputs/provenance']:(T/n).mkdir(parents=True,exist_ok=True)
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def png(p,a):Image.fromarray(a.astype('uint8')).save(p)
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
# Literal rows inspected against the actual current colour/cuff grid. These
# are deliberately not a runtime RGB classifier. Warm seam lips and ambiguous
# small side tabs remain in fixedlower, rather than guessed as mutable cloth.
ROWS=[
 {84:[[47,63],[74,79]],85:[[48,63],[74,79]],86:[[48,63],[74,79]],87:[[48,79]],88:[[49,79]],89:[[50,79]],90:[[51,59],[61,79]],91:[[54,58],[61,79]],92:[[63,71]],93:[[63,69]],94:[[64,67]]},
 {85:[[49,64],[74,79]],86:[[49,67],[74,79]],87:[[49,67],[74,79]],88:[[56,81]],89:[[57,81]],90:[[64,81]],91:[[64,80]],92:[[64,74]],93:[[66,72]]},
 {85:[[53,64],[74,79]],86:[[56,58],[62,67],[74,79]],87:[[62,67],[74,79]],88:[[60,80]],89:[[60,79]],90:[[61,77]],91:[[61,64],[68,75]],92:[[63,64]]},
 {84:[[49,64],[74,79]],85:[[49,67],[74,79]],86:[[49,68],[74,78]],87:[[48,76]],88:[[48,64],[67,74]],89:[[48,64]],90:[[49,64]],91:[[49,64]],92:[[50,53],[57,60]],93:[[50,53]],94:[[51,52]],95:[[52,52]],96:[[53,53]]},
 {84:[[49,53],[56,64],[74,79]],85:[[49,53],[56,67],[74,79]],86:[[49,68],[74,74]],87:[[49,68],[70,73]],88:[[49,67],[70,74]],89:[[49,65],[71,74]],90:[[49,64],[71,75]],91:[[49,64],[72,75]],92:[[48,61],[74,76]],93:[[48,59]],94:[[48,57]]},
 {85:[[49,64],[74,79]],86:[[49,63],[74,79]],87:[[49,65],[74,79]],88:[[49,65],[71,79]],89:[[48,66],[72,79]],90:[[48,66],[72,79]],91:[[48,49],[52,67],[74,79]],92:[[49,49],[52,66]],93:[[54,64]]},
 {85:[[51,64],[74,79]],86:[[51,67],[74,79]],87:[[52,67],[74,79]],88:[[52,68],[71,79]],89:[[52,68],[71,79]],90:[[53,68],[72,79]],91:[[53,67],[74,79]],92:[[55,65]]},
 {84:[[52,53],[64,64],[74,79]],85:[[52,54],[64,67],[74,79]],86:[[52,69],[77,79]],87:[[52,79]],88:[[53,79]],89:[[55,79]],90:[[56,79]],91:[[58,63],[65,71]],92:[[64,64],[66,69]]}
]
Y=[1,0,-1,0,1,0,-1,0];X=[1,1,0,-1,-1,-1,0,1];OLD=[0,1,1,0,0,1,1,0];dycurve=[a-b for a,b in zip(Y,OLD)];yy,xx=np.mgrid[:128,:128];records=[]
for i in range(8):
 src=arr(R/'inputs/control'/f'{i:02}.png');legacy=np.load(L/'maps'/f'se-{i:02}.npz');ids=legacy['source_id'];oldpilot=arr(L/'se-pilot'/f'{i:02}.png');bodyowner=(ids==8)|(ids==9)
 # Validate the CURRENT full upper against the original exact source assembly;
 # sampling is always from this phase's current native PNG, never repeated02.
 assert np.array_equal(src[bodyowner],oldpilot[bodyowner]),f'Current upper differs from assembly witness at{i}'
 shutil.copy2(L/'maps'/f'se-{i:02}.npz',T/'inputs/provenance'/f'upper-assembly-{i:02}.npz')
 clothowner=np.zeros((128,128),bool)
 for y,spans in ROWS[i].items():
  for lo,hi in spans:clothowner[y,lo:hi+1]=True
 clothowner&=~bodyowner&(src[:,:,3]>0)
 body=np.zeros_like(src);body[bodyowner]=src[bodyowner];fixed=src.copy();fixed[bodyowner|clothowner]=0;cloth=np.zeros_like(src);cloth[clothowner]=src[clothowner]
 # Positive monotone per-column endpoint field. Last literal charcoal row is
 # fixed at its actual painted lip; one-row columns remain exact endpoint pins.
 columns={};moving=[];pins=[]
 for x in range(128):
  ys=np.where(clothowner[:,x])[0]
  if len(ys)==0:continue
  h,e=int(ys.min()),int(ys.max());columns[x]=(h,e)
  if h==e or e-h-dycurve[i]<=0:pins.append(x)
  else:moving.append(x)
 mapped=np.zeros_like(src);sourcexy=np.full((128,128,2),-1,dtype='int16');errors=np.full((128,128),99.0);dx,dy=X[i],dycurve[i]
 for ty in range(77,100):
  for tx in range(43,86):
   options=[]
   for sx in range(max(0,tx-2),min(128,tx+3)):
    if sx not in columns:continue
    h,e=columns[sx]
    if sx in pins:
     if tx==sx and clothowner[ty,sx]:options.append((0.0,sx,ty))
     continue
    ht=h+dy
    if ty<ht or ty>e:continue
    syf=h+(ty-ht)*(e-h)/(e-h-dy);w=(e-syf)/(e-h);predx=sx+dx*w;err=abs(predx-tx);sy=int(np.floor(syf+.5))
    if err<=.500000001 and 0<=sy<128 and clothowner[sy,sx]:options.append((err,sx,sy))
   if options:
    err,sx,sy=min(options);mapped[ty,tx]=src[sy,sx];sourcexy[ty,tx]=[sx,sy];errors[ty,tx]=err
 moved=np.zeros_like(src);bodyxy=np.full((128,128,2),-1,dtype='int16');newbodyowner=np.zeros((128,128),bool)
 for sy,sx in np.argwhere(bodyowner):
  tx,ty=int(sx)+dx,int(sy)+dy
  if not(0<=tx<128 and 0<=ty<128):
   assert src[sy,sx,3]==0;continue
  moved[ty,tx]=src[sy,sx];bodyxy[ty,tx]=[sx,sy];newbodyowner[ty,tx]=True
 # Known retained lower/boots are foreground to the cloth field; whole upper
 # and its attached hem/tab then compose in foreground with natural occlusion.
 lower=over(fixed,mapped);out=over(moved,lower);out[out[:,:,3]==0]=0
 # An identity reconstruction must exactly reproduce the original RGBA.
 assert np.array_equal(over(body,over(fixed,cloth)),src)
 # Potential missing-undercoat exposures only: current torso/hem-owned paint
 # vacated near the waist, not old arm/glove or inter-leg background channels.
 waist=(yy>=80)&(yy<=89)&(xx>=48)&(xx<=80)&(ids==8)&(src[:,:,3]>0)
 exposed=waist&(moved[:,:,3]==0)&(lower[:,:,3]==0)
 oldclothloss=clothowner&(src[:,:,3]>=128)&(out[:,:,3]==0)
 bootocclusion=(fixed[:,:,3]>0)&(moved[:,:,3]>0)
 png(T/'frames'/f'{i:02}.png',out)
 for n,a in [('body-source',body),('body-moved',moved),('fixed-lower-before',fixed),('fixed-lower-after',fixed),('cloth-source',cloth),('cloth-mapped',mapped),('lower-before-body',lower)]:png(T/'layers'/f'{i:02}-{n}.png',a)
 for n,m in [('current-upper-owner',bodyowner),('literal-cloth-owner',clothowner),('moved-upper-owner',newbodyowner),('coat-only-exposure-candidates',exposed),('old-cloth-lost-alpha-candidates',oldclothloss),('new-body-over-fixedlower',bootocclusion)]:png(T/'masks'/f'{i:02}-{n}.png',m.astype('uint8')*255)
 np.savez_compressed(T/'maps'/f'{i:02}.npz',cloth_source_xy=sourcexy,body_source_xy=bodyxy)
 records.append({'phase':i,'current_upper_RGBA_exact_to_original_phase_assembly':True,'authored_body_translation_after_fixed_registration':[dx,dy],'absolute_body_xy':[X[i],Y[i]],'body_source_pixels':int((body[:,:,3]>0).sum()),'literal_cloth_pixels':int(clothowner.sum()),'fixed_lower_layer_RGBA_exact':True,'cloth_column_endpoints':{str(x):{'first_mutable_y':h,'fixed_terminal_y':e,'one_row_pin':x in pins}for x,(h,e)in columns.items()},'coat_only_exposure_candidates':[[int(x),int(y)]for y,x in np.argwhere(exposed)],'old_cloth_lost_alpha_candidates':[[int(x),int(y)]for y,x in np.argwhere(oldclothloss)],'new_body_over_fixedlower_pixels':[[int(x),int(y)]for y,x in np.argwhere(bootocclusion)],'frame_sha256':sha(T/'frames'/f'{i:02}.png')})
save(T/'LITERAL-OWNERS-AND-FIELD.json',{'status':'single-curve construction before any necessary coat completion; no art score','literal_cloth_rows':ROWS,'absolute_body_y':Y,'absolute_body_x':X,'old_body_y':OLD,'source_correction_y':dycurve,'source_correction_x':X,'registration':'All offsets are authored body motion after fixed128stage registration; no fitting.','source_sampling':'Each CURRENT phase native supplies its full upper/costume/arms/gloves; original assembly only verifies source ownership.','material_claim':'Complete visible leather/cuffs/sole and other retained lower/outline paint stay at identity in fixed layer. Ambiguous gray side tabs outside literal owners remain fixed and qualified. No complete hidden boot masters or anatomical hip recovered.','depth':['mapped proximal charcoal','retained fixed lower including whole visible boots','rigid current upper incl full gloves, hem, orange tab'],'records':records,'model_calls':0})
# Native and84 complete chronology on3grounds. Nearest84 is deliberately
# declared; these are static cel/pair proofs, not playback perception evidence.
forest=Image.open('/home/astra/artifacts/emberwake-brann-ne06-recovery-v1/inputs/forest-ground-crop.png').convert('RGBA');forest.save(T/'inputs/provenance/forest-ground-crop.png')
for size in [128,84]:
 h=size+20
 for label,color in [('light',(232,231,218,255)),('dark',(24,27,25,255)),('forest',None)]:
  can=Image.new('RGB',(8*size,2*h),(232,231,218));d=ImageDraw.Draw(can)
  for row,folder in enumerate([R/'inputs/control',T/'frames']):
   for i in range(8):
    z=forest.copy()if color is None else Image.new('RGBA',(128,128),color);z.alpha_composite(Image.open(folder/f'{i:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST);can.paste(z.convert('RGB'),(i*size,row*h+20));d.text((i*size+2,row*h+3),f'{"old"if row==0 else"trial"}{i:02}',fill='black')
  can.save(T/'proof'/f'full8-{size}-{label}.png')
# Source material overlays and lower joint crops for all8, no painted labels.
can=Image.new('RGB',(4*384,2*315),(232,231,218));d=ImageDraw.Draw(can)
for i in range(8):
 src=arr(R/'inputs/control'/f'{i:02}.png');b=np.array(Image.open(T/'masks'/f'{i:02}-current-upper-owner.png').convert('L'))>0;c=np.array(Image.open(T/'masks'/f'{i:02}-literal-cloth-owner.png').convert('L'))>0;bg=Image.new('RGBA',(128,128),(232,231,218,255));bg.alpha_composite(Image.fromarray(src));ov=np.zeros_like(src);ov[b]=[40,100,230,90];ov[c]=[40,210,70,125];bg.alpha_composite(Image.fromarray(ov));crop=bg.crop((40,74,88,111)).resize((384,296),Image.Resampling.NEAREST).convert('RGB');ox=i%4*384;oy=i//4*315;can.paste(crop,(ox,oy+19));d.text((ox+3,oy+2),f'{i:02} blue=current upper;green=literalcloth;bootretained',fill='black')
can.save(T/'proof/material-owners-lower-8x.png')
print(json.dumps({'body_curve_y':Y,'body_curve_x':X,'coat_exposures':[len(v['coat_only_exposure_candidates'])for v in records],'old_cloth_losses':[len(v['old_cloth_lost_alpha_candidates'])for v in records],'fixed_lower_exact_all8':True},indent=2))
