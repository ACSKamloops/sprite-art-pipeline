"""One source-owned foreleg path correction, not a repaint or recovered rig."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
BASE=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 d=ROOT/'inputs'
 if not d.exists():
  (d/'control').mkdir(parents=True)
  for i in range(8):shutil.copyfile(BASE/'rowan-source-legs-v2/frames'/f'{i:02}.png',d/'control'/f'{i:02}.png')
  for n in ['05-stable-torso-hem-owner.png','05-opaque-gloves-protected.png','05-complete-old-part-arm-owner.png']:
   shutil.copyfile(BASE/'rowan-five-bridge-v1/masks'/n,d/n)
  (d/'HASHES.json').write_text(json.dumps({f.relative_to(d).as_posix():sha(f)for f in sorted(d.rglob('*.png'))},indent=2)+'\n')
 o=a.output;o.mkdir();(o/'frames').mkdir();(o/'proof').mkdir();(o/'maps').mkdir()
 src=np.array(Image.open(d/'control/05.png').convert('RGBA'));Y,X=np.indices((128,128))
 protected=np.zeros((128,128),bool)
 for n in ['05-stable-torso-hem-owner.png','05-opaque-gloves-protected.png','05-complete-old-part-arm-owner.png']:
  protected|=np.array(Image.open(d/n))>0
 # Explicit visible foreground trouser/cuff/boot surface. The boundary follows
 # the separated inner pant/cuff edge; rear05 paint stays an independent owner.
 poly=Image.new('L',(128,128));ImageDraw.Draw(poly).polygon([(47,80),(66,80),(68,86),(66,92),(65,96),(69,103),(74,111),(71,116),(53,116),(46,106),(46,94)],fill=255)
 owner=(np.array(poly)>0)&(src[...,3]>0)&~protected
 # Anchored hip, bounded proximal lean, rigid complete distal boot plateau.
 # No width scaling, reflection, per-pose fit or new source color.
 shifts=np.floor(-3*np.clip((np.arange(128)-82)/16,0,1)+.5).astype(int)
 placed=np.zeros_like(src);xy=np.full((128,128,2),-1,np.int16)
 for y,x in np.argwhere(owner):
  tx=x+shifts[y];placed[y,tx]=src[y,x];xy[y,tx]=[x,y]
 out=src.copy();out[owner]=0;use=(placed[...,3]>0)&~protected;out[use]=placed[use];xy[~use]=-1
 # Restore the complete protected owner, including transparent erasure space.
 out[protected]=src[protected]
 assert np.array_equal(out[protected],src[protected]);assert np.array_equal(out[:80],src[:80])
 Image.fromarray(owner.astype('uint8')*255).save(o/'maps/source-foreleg-owner.png')
 Image.fromarray(protected.astype('uint8')*255).save(o/'maps/protected-upper.png')
 np.savez_compressed(o/'maps/05-projection.npz',source_xy=xy,row_dx=shifts,placed=use)
 Image.fromarray(placed).save(o/'maps/05-placed-foreleg.png')
 for i in range(8):
  dest=o/'frames'/f'{i:02}.png'
  if i==5:Image.fromarray(out).save(dest)
  else:shutil.copyfile(d/'control'/f'{i:02}.png',dest)
 for scale,name in [(128,'native'),(256,'2x'),(84,'game')]:
  for ground,label in [('#e7e3d6','light'),('#22252b','dark')]:
   board=Image.new('RGB',(3*scale,2*(scale+22)),ground);dr=ImageDraw.Draw(board)
   for r,which in enumerate(['control','trial']):
    for j,i in enumerate([4,5,6]):
     im=Image.open((d/'control'if r==0 else o/'frames')/f'{i:02}.png').resize((scale,scale),Image.Resampling.NEAREST)
     board.paste(im,(j*scale,r*(scale+22)+22),im);dr.text((j*scale+3,r*(scale+22)+3),f'{which} {i:02}',fill='black'if label=='light'else'white')
   board.save(o/'proof'/f'04-05-06-{name}-{label}.png')
 board=Image.new('RGB',(8*128,2*150),'#e7e3d6');dr=ImageDraw.Draw(board)
 for r,bank in enumerate([d/'control',o/'frames']):
  for i in range(8):
   im=Image.open(bank/f'{i:02}.png');board.paste(im,(i*128,r*150+22),im);dr.text((i*128+3,r*150+3),f'{"control"if r==0 else"trial"} {i:02}',fill='black')
 board.save(o/'proof/full8-native.png')
 receipt={'status':'preview; source-owned foreleg path hypothesis, no art approval','model_calls':0,'only_changed_frame':5,'sha256':sha(o/'frames/05.png'),'changed_RGBA_pixels':int(np.any(out!=src,axis=2).sum()),'original_upper_hem_complete_gloves_exact':True,'other7_PNG_bytes_exact':True,'source_part_pixels':int(owner.sum()),'distal_rows98_plus_dx':-3,'sourceRGBA_samples_only':True,'clock':{'hold':[9,160],'cycle':[9,20]},'limitation':'Visible source05surface only. Declared projection continuous in x; no recovered hidden limb or measured physical contact. Inspect outer contour and protected-glove occlusion.'}
 (o/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
