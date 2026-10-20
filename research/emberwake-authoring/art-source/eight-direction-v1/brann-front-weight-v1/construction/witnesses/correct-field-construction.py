"""Single authorized construction correction; same authored curve, no model.
Correct current material owners, explicit inverse-field pins, bounded source-color
coat underlay. The uncorrected single-curve-v1 remains immutable.
"""
from pathlib import Path
import json,hashlib,shutil,ast
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];OLDTRIAL=R/'single-curve-v1';T=R/'corrected-field-v1'
for n in ['frames','layers','maps','masks','proof','inputs/control','inputs/provenance']:(T/n).mkdir(parents=True,exist_ok=True)
def a(p):return np.array(Image.open(p).convert('RGBA'))
def png(p,z):Image.fromarray(z.astype('uint8')).save(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
base=json.loads((OLDTRIAL/'LITERAL-OWNERS-AND-FIELD.json').read_text());OLD=base['old_body_y'];X=base['absolute_body_x'];Y=base['absolute_body_y'];DY=base['source_correction_y'];yy,xx=np.mgrid[:128,:128]
# Literal current tab outline; broad gray hip shadow is proximal cloth, not
# rigid torso. Phase05 visible brown cuff occludes tab; phase07 orange tip is
# actually displaced in the current source and is preserved, not normalized.
TAB=[{84:[[67,73]],85:[[68,73]],86:[[69,73]]},{85:[[67,73]],86:[[68,73]],87:[[69,73]]},{85:[[67,73]],86:[[68,73]],87:[[69,73]]},{84:[[67,73]],85:[[68,73]],86:[[69,73]]},{84:[[67,73]],85:[[68,73]],86:[[69,73]]},{85:[[67,73]],86:[[69,73]],87:[[72,73]]},{85:[[67,73]],86:[[68,73]],87:[[69,73]]},{84:[[67,73]],85:[[68,73]],86:[[71,76]]}]
# Explicit known current charcoal extensions freed from old tab rectangle.
GRAY=[{84:[[64,66]],85:[[64,67]],86:[[64,68]]},{85:[[64,66]],86:[[64,67]],87:[[64,68]]},{85:[[64,66]],86:[[64,67]],87:[[64,68]]},{84:[[64,66]],85:[[64,67]],86:[[64,68]]},{84:[[64,66]],85:[[64,67]],86:[[64,68]]},{85:[[64,66]],87:[[63,65]]},{85:[[64,66]],86:[[64,67]],87:[[64,68]]},{84:[[64,66]],85:[[64,67]],86:[[64,70]]}]
# Explicit source-map pins will be frozen after actual owners/field diagnosis.
PINFILE=R/'diagnosis/MAP-PINS.json';UNDERFILE=R/'diagnosis/COAT-UNDERLAY.json'
pindata=json.loads(PINFILE.read_text())if PINFILE.exists()else[];underdata=json.loads(UNDERFILE.read_text())if UNDERFILE.exists()else[]
records=[]
for i in range(8):
 src=a(R/'inputs/control'/f'{i:02}.png');oldbody=np.array(Image.open(OLDTRIAL/'masks'/f'{i:02}-current-upper-owner.png').convert('L'))>0;bodyowner=oldbody.copy()
 # Remove old tab rectangle, restore actual contour. Actual glove ownership
 # wins throughout and is sampled from CURRENT composed source.
 arm=np.zeros((128,128),bool)
 for role in ['near','far','sleeve']:
  p=OLDTRIAL/'inputs/provenance'/f'current-attachment-{i:02}-{role}.png';arm|=a(p)[:,:,3]>0;shutil.copy2(p,T/'inputs/provenance'/p.name)
 oldrect=(xx>=64)&(xx<=73)&(yy>=84+OLD[i])&(yy<=86+OLD[i]);bodyowner[oldrect&~arm]=False
 for y,spans in TAB[i].items():
  for lo,hi in spans:bodyowner[y,lo:hi+1]=True
 # Current06 outer charcoal projection begins above old generic y83 boundary;
 # two literal CURRENT gray texels stay with the fixed visible lower surface.
 if i==6:bodyowner[81:83,80]=False
 bodyowner|=arm
 clothowner=np.array(Image.open(OLDTRIAL/'masks'/f'{i:02}-literal-cloth-owner.png').convert('L'))>0
 for y,spans in GRAY[i].items():
  for lo,hi in spans:clothowner[y,lo:hi+1]=True
 clothowner&=~bodyowner&(src[:,:,3]>0)
 body=np.zeros_like(src);body[bodyowner]=src[bodyowner];cloth=np.zeros_like(src);cloth[clothowner]=src[clothowner];fixed=src.copy();fixed[bodyowner|clothowner]=0
 assert np.array_equal(over(body,over(fixed,cloth)),src)
 columns={};short=[]
 for sx in range(128):
  ys=np.where(clothowner[:,sx])[0]
  if len(ys):
   h,e=int(ys.min()),int(ys.max());columns[sx]=(h,e)
   if h==e or e-h-DY[i]<=0:short.append(sx)
 mapped=np.zeros_like(src);sm=np.full((128,128,2),-1,dtype='int16');dx,dy=X[i],DY[i]
 for ty in range(77,100):
  for tx in range(43,86):
   opts=[]
   for sx in range(max(0,tx-2),min(128,tx+3)):
    if sx not in columns:continue
    h,e=columns[sx]
    if sx in short:
     if tx==sx and clothowner[ty,sx]:opts.append((0.0,sx,ty))
     continue
    ht=h+dy
    if ty<ht or ty>e:continue
    syf=h+(ty-ht)*(e-h)/(e-h-dy);w=(e-syf)/(e-h);err=abs(sx+dx*w-tx);sy=int(np.floor(syf+.5))
    if err<=.500000001 and 0<=sy<128 and clothowner[sy,sx]:opts.append((err,sx,sy))
   if opts:
    _,sx,sy=min(opts);mapped[ty,tx]=src[sy,sx];sm[ty,tx]=[sx,sy]
 beforepins=sm.copy();pinreceipts=[]
 for p in pindata:
  if p['phase']!=i:continue
  tx,ty=p['target'];sx,sy=p['source'];assert clothowner[sy,sx],(i,p);assert src[sy,sx,3]>=128;old=sm[ty,tx].tolist();mapped[ty,tx]=src[sy,sx];sm[ty,tx]=[sx,sy]
  pinreceipts.append(p|{'old_map':old,'source_RGBA':src[sy,sx].tolist()})
 moved=np.zeros_like(src);bm=np.full((128,128,2),-1,dtype='int16');newowner=np.zeros((128,128),bool)
 for sy,sx in np.argwhere(bodyowner):
  tx,ty=int(sx)+dx,int(sy)+dy
  if 0<=tx<128 and 0<=ty<128:moved[ty,tx]=src[sy,sx];bm[ty,tx]=[sx,sy];newowner[ty,tx]=True
  else:assert src[sy,sx,3]==0
 under=np.zeros_like(src);um=np.full((128,128,3),-1,dtype='int16');underreceipts=[]
 for p in underdata:
  if p['phase']!=i:continue
  tx,ty=p['target'];di=p.get('donor_phase',i);sx,sy=p['donor'];don=a(R/'inputs/control'/f'{di:02}.png');assert don[sy,sx,3]>=128
  # Underpaint is intentionally authored source-colour coverage, not recovered
  # hidden texels. Every sample must be one exact literal donor witness.
  under[ty,tx]=don[sy,sx];um[ty,tx]=[di,sx,sy];underreceipts.append(p|{'donor_RGBA':don[sy,sx].tolist()})
 lower=over(fixed,over(mapped,under));out=over(moved,lower);out[out[:,:,3]==0]=0
 oldlower=a(OLDTRIAL/'layers'/f'{i:02}-fixed-lower-before.png');oldmap=np.load(OLDTRIAL/'maps'/f'{i:02}.npz')['cloth_source_xy'];mapdelta=np.any(oldmap!=sm,axis=2)
 loss=clothowner&(src[:,:,3]>=128)&(out[:,:,3]==0);waist=(yy>=80)&(yy<=89)&(xx>=48)&(xx<=80)&bodyowner&~arm&(src[:,:,3]>0);exposed=waist&(moved[:,:,3]==0)&(lower[:,:,3]==0)
 png(T/'frames'/f'{i:02}.png',out);shutil.copy2(R/'inputs/control'/f'{i:02}.png',T/'inputs/control'/f'{i:02}.png')
 for n,z in [('body-source',body),('body-moved',moved),('fixed-lower',fixed),('cloth-source',cloth),('cloth-mapped',mapped),('authored-undercoat',under),('lower-before-body',lower)]:png(T/'layers'/f'{i:02}-{n}.png',z)
 for n,z in [('current-upper-owner',bodyowner),('literal-cloth-owner',clothowner),('owner-changed-vs-initial',bodyowner!=oldbody),('map-changed-vs-initial',mapdelta),('remaining-old-cloth-loss',loss),('remaining-coat-exposure',exposed)]:png(T/'masks'/f'{i:02}-{n}.png',z.astype('uint8')*255)
 np.savez_compressed(T/'maps'/f'{i:02}.npz',cloth_source_xy=sm,body_source_xy=bm,authored_undercoat_source_phase_xy=um)
 delta=[]
 for ty,tx in np.argwhere(mapdelta):
  sx,sy=sm[ty,tx];delta.append({'target':[int(tx),int(ty)],'old_source':oldmap[ty,tx].tolist(),'new_source':sm[ty,tx].tolist(),'source_RGBA':src[sy,sx].tolist()if sx>=0 else None,'material':'visible current charcoal trouser; source coordinate pin/field, not filler'})
 records.append({'phase':i,'body_xy':[dx,dy],'original_source_png_sha256':sha(R/'inputs/control'/f'{i:02}.png'),'frame_png_sha256':sha(T/'frames'/f'{i:02}.png'),'owner_changes':[{'xy':[int(x),int(y)],'was_upper':bool(oldbody[y,x]),'now_upper':bool(bodyowner[y,x]),'now_mutable_charcoal':bool(clothowner[y,x]),'source_RGBA':src[y,x].tolist()}for y,x in np.argwhere(bodyowner!=oldbody)],'fixed_lower_delta_vs_bad_initial_partition':[{'xy':[int(x),int(y)],'old':oldlower[y,x].tolist(),'corrected':fixed[y,x].tolist()}for y,x in np.argwhere(np.any(fixed!=oldlower,axis=2))],'columns':{str(x):[h,e]for x,(h,e)in columns.items()},'map_deltas':delta,'explicit_pins':pinreceipts,'authored_undercoat':underreceipts,'remaining_positive_cloth_losses':[[int(x),int(y)]for y,x in np.argwhere(loss)],'remaining_old_coat_exposures':[[int(x),int(y)]for y,x in np.argwhere(exposed)],'new_upper_over_fixedlower':[[int(x),int(y)]for y,x in np.argwhere((fixed[:,:,3]>0)&(moved[:,:,3]>0))]})
save(T/'CONSTRUCTION.json',{'status':'ONE authorized corrected construction; no score/acceptance','original_failed_trial':'../single-curve-v1 (unchanged)','original_absolute_body_x':X,'original_absolute_body_y':Y,'actual_source_correction_y':DY,'clock':{'holds':[[9,160]]*8,'total':[9,20]},'registration':'128 stage; authored XY motion, no fit','tab_literal_rows':TAB,'newly_mutable_current_gray_rows':GRAY,'depth':['bounded explicitly authored source-shaded undercoat','mapped current visible proximal charcoal','fixed actual lower incl complete visible boot/cuffs and residual outline','rigid current upper/attached tab/full gloves'],'material_limits':'No inferred hidden anatomy. Side gray/outline ambiguous pixels fixed. Phase05 actual cuff occludes tab; source current07 displaced orange tip preserved. Coverage/edge classifications are explicit, not automatic alpha hole-fill.','records':records,'model_calls':0})
print(json.dumps({'frames':str(T/'frames'),'remaining_cloth_losses':[r['remaining_positive_cloth_losses']for r in records],'coat_exposures':[r['remaining_old_coat_exposures']for r in records],'map_delta_counts':[len(r['map_deltas'])for r in records]},indent=2))
