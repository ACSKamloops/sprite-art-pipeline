from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
P=Path('/home/astra/artifacts/emberwake-rowan-ne-knee-paint-v1');A=P/'assessment-v1';D=P/'composite-diagnostic-v1';D.mkdir()
for n in ['frames','proposed','maps','masks','proof','rejected']:(D/n).mkdir()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,indent=2)+'\n')
rawxy=np.load(A/'whole-grid-source-xy.npz')['source_xy'];records=[]
for i in range(8):
 src=P/f'inputs/source-frames/{i:02}.png'
 if i not in [3,4,6]:shutil.copy2(src,D/'frames'/f'{i:02}.png');continue
 k=[3,4,5,6].index(i);base=arr(src);raw=arr(A/f'raw-cells/{i:02}.png');allowed=m(P/f'owners/{i:02}-allowed-trouser-knee-cuff.png');upper=m(P/f'owners/{i:02}-upper-hem-gloves.png');boot=m(P/f'owners/{i:02}-complete-boot-protected-region.png');out=base.copy();out[allowed]=raw[allowed]
 assert np.array_equal(out[~allowed],base[~allowed]);assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[boot],base[boot])
 Image.fromarray(out).save(D/'proposed'/f'{i:02}.png');Image.fromarray(out).save(D/'frames'/f'{i:02}.png');changed=np.any(out!=base,axis=2);Image.fromarray(changed.astype('uint8')*255).save(D/f'masks/{i:02}-actual-change.png');Image.fromarray(allowed.astype('uint8')*255).save(D/f'masks/{i:02}-frozen-cloth-owner.png')
 mapping=rawxy[(k//2)*128:(k//2+1)*128,(k%2)*128:(k%2+1)*128].copy();mapping[~allowed]=-1;np.savez_compressed(D/f'maps/{i:02}-raw-source-map.npz',raw_source_xy=mapping,allowed=allowed)
 alpha_zero_loss=(base[...,3]>0)&(out[...,3]==0)&allowed;core_loss=(base[...,3]>=128)&(out[...,3]<128)&allowed;core_gain=(base[...,3]<128)&(out[...,3]>=128)&allowed
 records.append({'phase':i,'source_PNG_sha256':sha(src),'proposed_PNG_sha256':sha(D/f'proposed/{i:02}.png'),'frozen_owner_sha256':sha(P/f'owners/{i:02}-allowed-trouser-knee-cuff.png'),'changed_RGBA_pixels':int(changed.sum()),'changed_coordinates':[[int(x),int(y)]for y,x in np.argwhere(changed)],'protected_outside_owner_RGBA_exact':True,'upper_hem_complete_gloves_RGBA_exact':True,'whole_boot_region_RGBA_exact':True,'positive_source_to_alpha0':[[int(x),int(y)]for y,x in np.argwhere(alpha_zero_loss)],'source_alpha128_to_below128':[[int(x),int(y)]for y,x in np.argwhere(core_loss)],'alpha128_new_coverage':[[int(x),int(y)]for y,x in np.argwhere(core_gain)],'alpha_normalization':False,'body_or_boot_restore_afterfit':False,'normalization':'same fixed whole1254→256nearest as raw assessment; no additional transform'})
shutil.copy2(A/'raw-cells/05.png',D/'rejected/05-raw-unimported.png');save('rejected/05-STATUS.json',{'status':'not imported; source05 remains exact','reason':'Raw x66 crossing cuff extends cream/shade into original leather rows88–89, strong leather begins90 vs88source','raw_source':'../assessment-v1/raw-cells/05.png','source05_PNG_sha256':sha(P/'inputs/source-frames/05.png'),'candidate05_PNG_sha256':sha(D/'frames/05.png')})
for size,name in [(128,'native'),(256,'2x'),(84,'game')]:
 for ids,prefix in [([2,3,4,5,6],'02-03-04-05-06'),(list(range(8)),'full8')]:
  can=Image.new('RGB',(len(ids)*size,6*(size+18)));d=ImageDraw.Draw(can)
  for bgr,(bgname,bg)in enumerate([('light',(235,230,215)),('dark',(29,34,43)),('green',(64,111,80))]):
   for row,bank in enumerate([P/'inputs/source-frames',D/'frames']):
    y=(bgr*2+row)*(size+18);d.rectangle((0,y,can.width,y+size+18),fill=bg)
    for col,i in enumerate(ids):
     im=Image.open(bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*size,y+18),im);d.text((col*size+2,y+2),f'{"source"if row==0 else"diag"} {i:02} {bgname}',fill='black'if bgr==0 else'white')
  can.save(D/f'proof/{prefix}-{name}.png')
can=Image.new('RGBA',(4*344,2*274),(235,230,215,255));d=ImageDraw.Draw(can)
for row,bank in enumerate([P/'inputs/source-frames',D/'frames']):
 for col,i in enumerate([3,4,5,6]):
  im=Image.open(bank/f'{i:02}.png').convert('RGBA').crop((41,76,84,108)).resize((344,256),Image.Resampling.NEAREST);can.alpha_composite(im,(col*344,row*274+18));d.text((col*344+3,row*274+2),f'{"source"if row==0 else"DIAG"} {i:02}',fill='black')
can.save(D/'proof/joint-boundary-8x.png')
save('DIAGNOSTIC-RECEIPT.json',{'status':'Unselected composite diagnostic; self-inspection pending; no editor package','changed_phases':[3,4,6],'05_fully_original':True,'other5_original_PNG_bytes_exact':all((P/f'inputs/source-frames/{i:02}.png').read_bytes()==(D/f'frames/{i:02}.png').read_bytes()for i in [0,1,2,5,7]),'records':records,'no_fit_or_recenter':True,'raw_alpha_preserved_inside_frozen_owner':True,'model_calls_in_this_lane':0,'inherited_score':None})
print(json.dumps([{'phase':r['phase'],'changed':r['changed_RGBA_pixels'],'alpha0_losses':r['positive_source_to_alpha0'],'core_losses':r['source_alpha128_to_below128'],'core_gains':r['alpha128_new_coverage']}for r in records]))
