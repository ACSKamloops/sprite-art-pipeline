from pathlib import Path
from PIL import Image,ImageDraw
import json
out=Path(__file__).parent;rows=json.load(open(out/'named-feature-rays.json'));regions=[(1490,210,1600,340),(1860,380,2020,530),(0,1760,140,1950)];im=Image.open(out/'packed-source-texture.png');safe=Image.open(out/'proposed-head-owned-edit-footprint.png');canvas=Image.new('RGB',(1050,640),(35,40,45));d=ImageDraw.Draw(canvas)
for j,roi in enumerate(regions):
 a=im.crop(roi).convert('RGB').resize(((roi[2]-roi[0])*2,(roi[3]-roi[1])*2),Image.Resampling.NEAREST);canvas.paste(a,(j*350,0));
 for i,r in enumerate(rows,1):
  x,y=r['texture_xy_top_origin']
  if roi[0]<=x<roi[2] and roi[1]<=y<roi[3]:
   xx=j*350+(x-roi[0])*2;yy=(y-roi[1])*2;d.ellipse((xx-3,yy-3,xx+3,yy+3),outline='cyan',width=1);d.text((xx+4,yy),str(i),fill='cyan')
 d.text((j*350,395),f'UV rectangle {roi} nearest2x',fill='white')
for i,r in enumerate(rows,1):d.text(((i-1)//5*350,425+(i-1)%5*38),f'{i}: source{r["source_frame"]} {r["feature_label_visual_proposal"]}\nUV texel {r["texture_xy_top_origin"]}',fill='white')
canvas.save(out/'annotated-UV-feature-crops.png')
c=Image.new('RGB',(1200,440),(35,40,45));d=ImageDraw.Draw(c)
for j,f in enumerate([1,33,103]):
 a=Image.open(out/f'source-{f:03}.png').convert('RGBA').crop((168,76,212,124)).resize((352,384),Image.Resampling.NEAREST);b=Image.new('RGBA',a.size,(35,40,45,255));b.alpha_composite(a);c.paste(b.convert('RGB'),(j*400,0));
 for i,r in enumerate(rows,1):
  if r['source_frame']!=f:continue
  x,y=r['pixel_xy'];xx=j*400+(x-168+.5)*8;yy=(y-76+.5)*8;d.ellipse((xx-3,yy-3,xx+3,yy+3),outline='cyan');d.text((xx+5,yy),str(i),fill='cyan')
 d.text((j*400,394),f'source{f}: geometric primary-ray markers',fill='white')
c.save(out/'annotated-source-head-crops.png')
