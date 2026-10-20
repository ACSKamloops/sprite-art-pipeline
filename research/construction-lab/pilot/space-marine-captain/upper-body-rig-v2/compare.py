from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
CONTROL=Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assembled-v18')
OUT=ROOT/'artifacts/loaded-v1'
keys=[0,4,7,10,18,24,36,40,43,46,54,60]
im=Image.new('RGB',(6*256,4*280),(45,48,53));d=ImageDraw.Draw(im)
for j,k in enumerate(keys):
 for candidate,path in enumerate([CONTROL,OUT/'weighted']):
  xy=((j%6)*256,(j//6*2+candidate)*280)
  frame=Image.open(path/'frames'/f'{k:02}.png').convert('RGBA');im.paste(frame,xy,frame)
  d.text((xy[0]+4,xy[1]+258),f'{"v18 control" if candidate==0 else "loaded upper v2"} / {k}',fill='white')
im.save(OUT/'comparison-native.png');im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST).save(OUT/'comparison-2x.png')
