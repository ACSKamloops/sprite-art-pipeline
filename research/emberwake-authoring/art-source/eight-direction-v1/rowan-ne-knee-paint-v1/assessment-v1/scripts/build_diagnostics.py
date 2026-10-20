from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path('/home/astra/artifacts/emberwake-rowan-ne-knee-paint-v1');A=P/'assessment-v1';A.mkdir()
(A/'raw-cells').mkdir();(A/'proof').mkdir();(A/'scripts').mkdir()
rawp=P/'generation/raw.png';raw=Image.open(rawp).convert('RGBA');assert raw.size==(1254,1254);assert hashlib.sha256(rawp.read_bytes()).hexdigest()=='3289cd552a813181c71e7921e4cc900eeccece070de6587dc60cc2917f9edc99'
small=raw.resize((256,256),Image.Resampling.NEAREST);small.save(A/'raw-grid-native.png');sa=np.array(small);ra=np.array(raw);coord=np.floor((np.arange(256)+.5)*1254/256).astype('int16');xx,yy=np.meshgrid(coord,coord);xy=np.stack([xx,yy],axis=-1);assert np.array_equal(ra[yy,xx],sa);np.savez_compressed(A/'whole-grid-source-xy.npz',source_xy=xy)
ids=[3,4,5,6]
for k,i in enumerate(ids):small.crop(((k%2)*128,(k//2)*128,(k%2+1)*128,(k//2+1)*128)).save(A/'raw-cells'/f'{i:02}.png')
source=[Image.open(P/f'inputs/source-frames/{i:02}.png').convert('RGBA')for i in ids];cells=[Image.open(A/f'raw-cells/{i:02}.png').convert('RGBA')for i in ids]
for size,name in [(128,'native'),(256,'2x'),(84,'game')]:
 can=Image.new('RGB',(4*size,6*(size+18)));d=ImageDraw.Draw(can)
 for bgrow,(bgname,bg)in enumerate([('light',(235,230,215)),('dark',(29,34,43)),('green',(64,111,80))]):
  for row,bank in enumerate([source,cells]):
   y=(bgrow*2+row)*(size+18);d.rectangle((0,y,can.width,y+size+18),fill=bg)
   for c,(i,im)in enumerate(zip(ids,bank)):
    im=im.resize((size,size),Image.Resampling.NEAREST);can.paste(im,(c*size,y+18),im);d.text((c*size+3,y+2),f'{"source"if row==0 else"RAW"} {i:02} {bgname}',fill='black'if bgrow==0 else'white')
 can.save(A/f'proof/source-vs-RAW-{name}.png')
# Same fixed diagnostic lower crop across all4cells, not a pose fit.
can=Image.new('RGBA',(4*344,2*274),(235,230,215,255));d=ImageDraw.Draw(can)
for row,bank in enumerate([source,cells]):
 for c,(i,im)in enumerate(zip(ids,bank)):
  im=im.crop((41,76,84,108)).resize((344,256),Image.Resampling.NEAREST);can.alpha_composite(im,(c*344,row*274+18));d.text((c*344+3,row*274+2),f'{"source"if row==0 else"RAW"} {i:02}',fill='black')
can.save(A/'proof/cuff-comparison-8x.png')
# Difference is raw-only; no imported candidates or restoration.
records=[]
for i,s,r in zip(ids,source,cells):
 s=np.array(s);r=np.array(r);row={'phase':i,'whole_cell_RGBA_equal_pixels':int(np.all(s==r,axis=2).sum()),'thresholds':[]}
 for threshold in [1,128,245]:
  item={'alpha_threshold':threshold}
  for name,box in [('full_actor',(0,0,128,128)),('all_boot_lower',(30,94,96,124)),('lowest_boot',(30,103,96,124))]:
   vals={}
   for key,a in [('source',s),('raw',r)]:
    x0,y0,x1,y1=box;ys,xs=np.where(a[y0:y1,x0:x1,3]>=threshold)
    if len(xs):
     ys+=y0;xs+=x0;lo=int(ys.max());vals[key]={'bounds_inclusive':[int(xs.min()),int(ys.min()),int(xs.max()),lo],'lowest_row':lo,'lowest_row_columns':xs[ys==lo].astype(int).tolist(),'positive_pixels':len(xs)}
    else:vals[key]=None
   if vals['source']and vals['raw']:vals['bounds_delta_raw_minus_source']=(np.array(vals['raw']['bounds_inclusive'])-np.array(vals['source']['bounds_inclusive'])).astype(int).tolist()
   item[name]=vals
  row['thresholds'].append(item)
 records.append(row)
(A/'NORMALIZATION.json').write_text(json.dumps({'raw_path':str(rawp),'raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'raw_dimensions':[1254,1254],'whole_grid_destination':[256,256],'transform':'One whole-grid nearest1254→256; no translation, crop fitting, cell refit, thresholding, alpha/color normalization or protected-owner restoration','scale':[128,627],'native_cells':[128,128],'fixed_cell_order':ids,'source_xy_center_rule':'floor((destination+0.5)*1254/256), exact equality to Pillow NEAREST verified','raw_only':True},indent=2)+'\n');(A/'SILHOUETTE-MEASUREMENTS.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps([{'phase':r['phase'],'a128':r['thresholds'][1]}for r in records]))
