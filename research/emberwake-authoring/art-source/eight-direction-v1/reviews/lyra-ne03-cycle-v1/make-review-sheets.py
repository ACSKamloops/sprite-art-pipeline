from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
ROOT=Path('/home/astra/artifacts/emberwake-lyra-ne03-transition-v1/review-packet/input')
OUT=Path('/home/astra/artifacts/emberwake-lyra-ne03-cycle-critic-v1/sheets')
GROUNDS={'light':'#e6e0d5','dark':'#171b24','game':'#35452e'}
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
coverage=[]
def cel(path,size,bg):
 im=Image.open(ROOT/path).convert('RGBA')
 assert im.size==(128,128)
 im=im.resize((size,size),Image.Resampling.NEAREST)
 base=Image.new('RGBA',(size,size),bg)
 base.alpha_composite(im)
 return base.convert('RGB')
for direction in ('northeast','northwest'):
 for size in (256,128,84):
  for ground,bg in GROUNDS.items():
   gap=10; pairw=2*size+gap; rowh=size+28
   sheet=Image.new('RGB',(4*pairw+5*gap,4*rowh+70),'#fafafa')
   draw=ImageDraw.Draw(sheet)
   draw.text((10,8),f'{direction} | stage {size}px | {ground} {bg} | NEAREST | no crop, fit, cleanup, translation',font=FONT,fill='black')
   draw.text((10,29),'Every hold = 9/160 s (56.25 ms); 00..07 = 9/20 s; explicit 07 > 00 wrap. Left = predecessor; right = current.',font=SMALL,fill='black')
   for vi,v in enumerate(('A','B')):
    for i in range(8):
     j=(i+1)%8; row=vi*2+i//4; col=i%4
     x=gap+col*(pairw+gap); y=65+row*rowh
     draw.text((x,y),f'{v} {i:02} > {j:02}'+(' WRAP' if i==7 else ''),font=FONT,fill='black')
     for fi,frame in enumerate((i,j)):
      path=f'{v}/{direction}/{frame:02}.png'
      sheet.paste(cel(path,size,bg),(x+fi*(size+gap),y+23))
   name=f'pairs-{direction}-{size}-{ground}.png';sheet.save(OUT/name)
   coverage.append({'sheet':name,'direction':direction,'variants':['A','B'],'pairs':[[i,(i+1)%8] for i in range(8)],'scale_px':size,'background':ground,'background_rgb':bg,'full_stage':True,'nearest':True})
for size in (256,128,84):
 for ground,bg in GROUNDS.items():
  gap=10; rowh=size+28; cols=5
  sheet=Image.new('RGB',(cols*(size+gap)+gap,6*rowh+60),'#fafafa'); draw=ImageDraw.Draw(sheet)
  draw.text((10,8),f'Identity context only | {size}px full stage | {ground} {bg} | NEAREST',font=FONT,fill='black')
  for di,d in enumerate(('east','north','west')):
   paths=[f'context/{d}-idle-{i:02}.png' for i in range(2)]+[f'context/{d}-walk-{i:02}.png' for i in range(8)]
   for k,path in enumerate(paths):
    x=gap+(k%cols)*(size+gap);y=45+(di*2+k//cols)*rowh
    draw.text((x,y),Path(path).stem,font=SMALL,fill='black');sheet.paste(cel(path,size,bg),(x,y+22))
  sheet.save(OUT/f'context-{size}-{ground}.png')
Path(OUT.parent/'sheet-coverage-plan.json').write_text(json.dumps(coverage,indent=2)+'\n')
print('Created 18 complete cyclic-pair sheets and 9 full context sheets; no source PNG was changed.')
