from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
im=Image.new('RGBA',(768,1024),(31,34,41,255));d=ImageDraw.Draw(im)
for n,k in enumerate([0,7,18,24,36,54]):
 x=n%3*256;y=n//3*512
 for j,path in enumerate([R.parent/'foreground-shin-v22/frames'/f'{k:02}.png',R/'frames'/f'{k:02}.png']):
  im.alpha_composite(Image.open(path).convert('RGBA'),(x,y+j*256));d.text((x+4,y+j*256+4),f'{k:02} '+('v22control'if j==0 else'cap/shellprobe'),fill='white')
im.save(R/'comparison-native.png');im.resize((1536,2048),Image.Resampling.NEAREST).save(R/'comparison-fixed-origin-2x.png')
