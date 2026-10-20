from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path(__file__).resolve().parents[1];src=Image.open(R/'inputs/base128.png').convert('RGBA');raw=Image.open(R/'raw/whole-canvas-native128-BOX.png').convert('RGBA');S=np.array(src);G=np.array(raw)
for size in[128,256,84]:
 for name,col in [('light',(231,227,214,255)),('dark',(34,37,43,255)),('game',(39,57,47,255))]:
  board=Image.new('RGB',(size*2,size+24),col[:3]);d=ImageDraw.Draw(board)
  for j,(title,im)in enumerate([('sole painted input',src),('RAW generated; no restore',raw)]):
   bg=Image.new('RGBA',(128,128),col);bg.alpha_composite(im);board.paste(bg.resize((size,size),Image.Resampling.NEAREST).convert('RGB'),(size*j,24));d.text((size*j+2,3),title,fill='black'if name=='light'else'white')
  board.save(R/'proof'/f'input-vs-raw-{size}-{name}.png')
box=(32,76,68,108);scale=12;board=Image.new('RGB',(2*36*scale,32*scale+24),(231,227,214));d=ImageDraw.Draw(board)
for j,(title,im)in enumerate([('PAINTED INPUT',src),('RAW GENERATED: unprotected',raw)]):
 bg=Image.new('RGBA',(128,128),(231,227,214,255));bg.alpha_composite(im);board.paste(bg.crop(box).resize((36*scale,32*scale),Image.Resampling.NEAREST).convert('RGB'),(j*36*scale,24));d.text((j*36*scale+3,3),title,fill='black')
board.save(R/'proof/raw-leg-comparison-12x.png')
# Fixed whole-stage windows report actual raster boundaries, not fitted anatomy.
windows={'head-hair-upper':[35,8,93,44],'left-glove-region':[37,65,52,84],'foreground-lower-region':[33,90,62,109],'otherleg-lower-region':[64,84,82,109]};rec={}
for name,(x0,y0,x1,y1)in windows.items():
 rr={}
 for title,z in [('input',S),('raw',G)]:
  ys,xs=np.where(z[y0:y1,x0:x1,3]>=128);rr[title+'_alpha128_bbox_exclusive']=[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0+1),int(ys.max()+y0+1)]
 rec[name]=rr|{'same_fixed_stage_window':[x0,y0,x1,y1],'semantic_limit':'literal foreground raster within fixed window; not whole anatomy, fitted registration, or physical contact measurement'}
(R/'raw/REGISTRATION-WINDOW-MEASUREMENTS.json').write_text(json.dumps({'whole_canvas_mapping_only':True,'windows':rec,'no_protection_restoration':True,'raw_character_source_pose_correspondence':'manual anatomy/geometry assessment separate; raw image remains sole generated output'},indent=2)+'\n')
print(json.dumps(rec,indent=2))
