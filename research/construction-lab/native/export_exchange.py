#!/usr/bin/env python3
"""Lossless PNG/ORA exchange of captured full-canvas layered projects."""
import io,json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent));from audit import render
BASE=Path(__file__).resolve().parent
for directory in sorted((BASE/'fixtures').iterdir()):
 p=json.loads((directory/'project.json').read_text());out=directory/'exports';out.mkdir(exist_ok=True)
 frames=[]
 for f in p['frames']:
  im=render(p,f);im.save(out/(f['id']+'.png'));frames.append(im)
 # A real ORA for each presented frame, not a renamed flat file.
 for f,merged in zip(p['frames'],frames):
  tree=ET.Element('image',{'w':'256','h':'224','name':f['id'],'version':'0.0.3'});stack=ET.SubElement(tree,'stack');buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED)as z:
   def write(name,data,compress=zipfile.ZIP_DEFLATED):
    info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=compress;z.writestr(info,data)
   write('mimetype','image/openraster',zipfile.ZIP_STORED)
   for layer in reversed(p['layers']):
    cid=f['cels'].get(layer['id'])
    if cid is None:continue
    im=Image.new('RGBA',(256,224));im.putdata([tuple(p['palette'][v])for v in p['cels'][cid]['pixels']]);b=io.BytesIO();im.save(b,format='PNG');name='data/'+layer['id']+'.png';write(name,b.getvalue());ET.SubElement(stack,'layer',{'name':layer['id'],'src':name,'x':'0','y':'0','opacity':'1.0','visibility':'visible','composite-op':'svg:src-over'})
   b=io.BytesIO();merged.save(b,format='PNG');write('mergedimage.png',b.getvalue());write('stack.xml',ET.tostring(tree))
  (out/(f['id']+'.ora')).write_bytes(buf.getvalue())
 # Fixed screen crop, never alpha-centered. White ground reference is metadata anchor.
 picks=[0,5,10,15,20,25]if'walk'in directory.name else list(range(0,len(frames),5))
 contact=Image.new('RGBA',(len(picks)*288,210),(38,43,52,255));draw=ImageDraw.Draw(contact)
 for j,i in enumerate(picks):
  image=frames[i].crop((24,118,120,182)).resize((288,192),Image.Resampling.NEAREST);contact.alpha_composite(image,(j*288,18));draw.text((j*288+4,3),p['frames'][i]['id'],fill='white');y=(p['frames'][i]['landmarks']['native_actor_world_anchor'][1]-118)*3+18
  if 18<=y<210:draw.line((j*288,y,(j+1)*288-1,y),fill=(100,210,250,255))
 contact.save(out/'fixed-screen-contact.png')
print('PNG and genuine layered ORA frames exported')
