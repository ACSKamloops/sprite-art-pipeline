from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
p=Path(__file__).resolve().parent;b=p/'output/playwright';runs={}
for key in ['native','uncompensated','twice']:
 text=(b/f'capture-{key}-cli.txt').read_text();r=json.loads(text.split('### Result\n')[1].split('\n')[0]);runs[key]=r
 sc=2 if key=='twice' else 1;size=256*sc;columns=1 if sc==2 else 2
 for start in range(0,len(r['records']),columns):
  out=Image.new('RGB',(size*2*columns,size+24),(33,40,46));d=ImageDraw.Draw(out)
  for i,rec in enumerate(r['records'][start:start+columns]):
   im=Image.open(b/rec['file']);rec['sha256']=hashlib.sha256((b/rec['file']).read_bytes()).hexdigest();x=i*size*2
   out.paste(im.crop((0,49,size,49+size)),(x,24));wx=430 if sc==1 else 686;out.paste(im.crop((wx,104,wx+size,104+size)),(x+size,24))
   d.text((x+3,3),f"{key} {start+i} frames{rec['before']['frame']}..{rec['after']['frame']} t{rec['before']['clock_ms']:.0f}..{rec['after']['clock_ms']:.0f}ms",fill='white')
  out.save(p/f'{key}-strip-{start:02d}.png')
(p/'browser-capture.json').write_text(json.dumps({'runs':runs,'crop_contract':'Exactcurrentframe canvas x0,y49,width256/512; world fixedscreenROI x430/686,y104,width256/512,height256/512. Camera follows active; no perpose crop adjustment. Full .views screenshots retained. Clockbefore/afterranges maycrosspose.'},indent=2)+'\n')
print([(k,len(v['records']),round(v['stopped']['clock_ms'],1)) for k,v in runs.items()])
