from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path('/home/astra/artifacts/emberwake-rowan-ne03-whole-walk-v1/packet/input')
out=Path('/home/astra/artifacts/emberwake-rowan-ne03-cycle-critic-v1')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
backgrounds={'light':(231,227,214),'dark':(34,37,43),'ground':(39,57,47)}
for direction in ('northeast','northwest'):
 for name,bg in backgrounds.items():
  sheet=Image.new('RGB',(9*264+16,1128),(42,42,42)); d=ImageDraw.Draw(sheet)
  y=6
  for variant in ('A','B'):
   for size in (128,256,84):
    d.text((10,y),f'{variant} {direction}  {size}x{size}  {name}; repeat 00 after 07 for wrap',font=font,fill='white'); y+=21
    for col,n in enumerate([0,1,2,3,4,5,6,7,0]):
     x=8+col*264
     cel=Image.open(root/variant/direction/f'{n:02d}.png')
     if size!=128:cel=cel.resize((size,size),Image.Resampling.NEAREST)
     tile=Image.new('RGB',(size,size),bg); tile.paste(cel,mask=cel.getchannel('A'))
     sheet.paste(tile,(x,y))
     d.text((x+size+2,y+2),f'{n:02d}',font=font,fill='white')
    y+=size+8
   y+=3
  sheet.save(out/f'{direction}-{name}-cycles.png')
# Identity context, only for identity and turn context.
ims=[]
for direction in ('west','north','east'):
 for kind,n in [('idle',0),('walk',0),('walk',3),('walk',7)]:
  ims.append((f'{direction}-{kind}-{n:02d}',Image.open(root/'context'/f'{direction}-{kind}-{n:02d}.png')))
context=Image.new('RGB',(4*272,3*300),(221,216,200));d=ImageDraw.Draw(context)
for i,(label,im) in enumerate(ims):
 x=(i%4)*272;y=(i//4)*300
 d.text((x+4,y+2),label,font=font,fill='black')
 im=im.resize((256,256),Image.Resampling.NEAREST);context.paste(im,(x+4,y+26),im)
context.save(out/'identity-context.png')
# Explicit cyclic pair ledger: each row is predecessor/current, without altered registration.
for variant in ('A','B'):
 for direction in ('northeast','northwest'):
  pairs=Image.new('RGB',(1008,8*286),(42,42,42));d=ImageDraw.Draw(pairs)
  for n in range(8):
   nxt=(n+1)%8;y=n*286
   d.text((8,y+2),f'{variant} {direction} {n:02d} -> {nxt:02d}; 128 / 256 / 84; ground #27392f',font=font,fill='white')
   x=8
   for size in (128,256,84):
    for k in (n,nxt):
     cel=Image.open(root/variant/direction/f'{k:02d}.png').resize((size,size),Image.Resampling.NEAREST)
     tile=Image.new('RGB',(size,size),(39,57,47));tile.paste(cel,mask=cel.getchannel('A'))
     pairs.paste(tile,(x,y+24));x+=size
    x+=18
  pairs.save(out/f'{variant}-{direction}-pairs-ground.png')
