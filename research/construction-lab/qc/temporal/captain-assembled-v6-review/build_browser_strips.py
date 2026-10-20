from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
p=Path(__file__).resolve().parent;b=p/'output/playwright';runs={}
for key in ['native','uncompensated','twice']:
 text=(b/f'capture-{key}-cli.txt').read_text();r=json.loads(text.split('### Result\n')[1].split('\n')[0]);runs[key]=r
 for start in range(0,len(r['records']),2):
  sc=2 if key=='twice' else 1;w=256*sc+288;h=256*sc+24;out=Image.new('RGB',(w*2,h),(33,40,46));d=ImageDraw.Draw(out)
  for i,rec in enumerate(r['records'][start:start+2]):
   im=Image.open(b/rec['file']);rec['sha256']=hashlib.sha256((b/rec['file']).read_bytes()).hexdigest();x=i*w
   out.paste(im.crop((0,49,256*sc,49+256*sc)),(x,24));wx=416 if sc==1 else 672;out.paste(im.crop((wx,96,wx+288,352)),(x+256*sc,24))
   d.text((x+3,3),f"{key} {start+i} frames{rec['before']['frame']}..{rec['after']['frame']} t{rec['before']['clock_ms']:.0f}..{rec['after']['clock_ms']:.0f}ms",fill='white')
  out.save(p/f'{key}-strip-{start:02d}.png')
(p/'browser-capture.json').write_text(json.dumps({'runs':runs,'crop_contract':'Exactcurrentframe canvas x0,y49,width256/512; world fixedscreenROI x416/672,y96,width288,height256. Camera follows active; no perpose crop adjustment. Full .views screenshots retained. Clockbefore/afterranges maycrosspose.'},indent=2)+'\n')
print([(k,len(v['records']),round(v['stopped']['clock_ms'],1)) for k,v in runs.items()])
