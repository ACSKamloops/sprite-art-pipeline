from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
BASE=Path('/home/astra/artifacts/emberwake-rowan-contact-transition-review-v1')
OUT=BASE/'review'
DATA=json.loads((BASE/'input/INPUTS.json').read_text())
FONT=ImageFont.load_default()
BGS={'light':(238,237,233,255),'dark':(31,34,43,255),'ground':(101,111,85,255)}
def cel(path,bg,sz):
 im=Image.open(BASE/'input'/path).convert('RGBA')
 layer=Image.new('RGBA',(128,128),BGS[bg]);d=ImageDraw.Draw(layer)
 if bg=='ground':
  for x in range(0,129,16): d.line((x,0,x,127),fill=(110,120,94,255))
  for y in range(0,129,16): d.line((0,y,127,y),fill=(110,120,94,255))
  d.line((0,112,127,112),fill=(179,186,163,255))
  d.line((64,108,64,116),fill=(179,186,163,255))
 layer.alpha_composite(im)
 return layer.convert('RGB').resize((sz,sz),Image.Resampling.NEAREST)
for direction in ('southeast','southwest'):
 for tag,sz in [('native',128),('nearest2x',256),('proxy84',84)]:
  gap=4; left=64; head=28; rh=sz+24
  sheet=Image.new('RGB',(left+8*(sz+gap),head+6*rh),(215,216,218));d=ImageDraw.Draw(sheet)
  d.text((8,6),f'{direction} {tag}: equal 9/160 s holds; columns 00..07, then 07 -> 00',fill=(0,0,0),font=FONT)
  for r,(bg,variant) in enumerate((b,v) for b in BGS for v in ('A','B')):
   y=head+r*rh;d.text((4,y+8),f'{variant}\n{bg}',fill=(0,0,0),font=FONT)
   for i,item in enumerate(DATA['variants'][variant][direction]):
    x=left+i*(sz+gap);sheet.paste(cel(item['path'],bg,sz),(x,y+18));d.text((x,y+2),f'{i:02}',fill=(0,0,0),font=FONT)
  sheet.save(OUT/f'{direction}-{tag}.png')
 # Every cyclic pair in both variants, lower-body only, nearest x3.
 sz=192;rh=166;gap=8;sheet=Image.new('RGB',(48+8*(sz+gap),30+4*rh),(215,216,218));d=ImageDraw.Draw(sheet)
 d.text((5,7),f'{direction}: all cyclic lower-body pairs, x3, fixed stage; 00-03 top, 04-07 below',fill=(0,0,0),font=FONT)
 for vindex,variant in enumerate(('A','B')):
  seq=DATA['variants'][variant][direction]
  for i in range(8):
   row=vindex*2+i//4;col=i%4;y=30+row*rh;x=48+col*(2*sz+2*gap)
   if col==0:d.text((3,y+22),variant,fill=(0,0,0),font=FONT)
   d.text((x,y+2),f'{i:02} -> {(i+1)%8:02}',fill=(0,0,0),font=FONT)
   for j,k in enumerate((i,(i+1)%8)):
    pic=cel(seq[k]['path'],'ground',128).crop((32,77,96,125)).resize((192,144),Image.Resampling.NEAREST)
    sheet.paste(pic,(x+j*(sz+gap),y+18))
 sheet.save(OUT/f'{direction}-all-cyclic-pairs.png')
# Cardinal context, including every nominated cel, is context only.
for direction in ('east','south','west'):
 items=[x for x in DATA['context'] if x['path'].startswith('context/'+direction+'-')]
 sz=168;gap=4;sheet=Image.new('RGB',(10*(sz+gap),2*(sz+24)+28),(215,216,218));d=ImageDraw.Draw(sheet)
 d.text((4,6),f'{direction}: idle 00,01 then walk 00..07; identity/turn context only',fill=(0,0,0),font=FONT)
 for row,bg in enumerate(('light','dark')):
  for i,item in enumerate(items):
   x=i*(sz+gap);y=28+row*(sz+24);d.text((x,y),item['path'].split('/')[-1],fill=(0,0,0),font=FONT);sheet.paste(cel(item['path'],bg,sz),(x,y+16))
 sheet.save(OUT/f'context-{direction}.png')
# Exact changed-pixel diagnostic is descriptive, never a score.
changes=[]
for direction in ('southeast','southwest'):
 for i in range(8):
  pa=DATA['variants']['A'][direction][i]['path'];pb=DATA['variants']['B'][direction][i]['path']
  a=Image.open(BASE/'input'/pa).convert('RGBA');b=Image.open(BASE/'input'/pb).convert('RGBA')
  count=sum(p!=q for p,q in zip(a.getdata(),b.getdata()))
  box=ImageChops.difference(a,b).getbbox(alpha_only=False)
  changes.append({'direction':direction,'cel':f'{i:02}','changed_pixels':count,'changed_bbox':box})
(OUT/'descriptive-changes.json').write_text(json.dumps(changes,indent=2)+'\n')
print(json.dumps({'diagnostic_pngs':11,'changes':[x for x in changes if x['changed_pixels']]}))
