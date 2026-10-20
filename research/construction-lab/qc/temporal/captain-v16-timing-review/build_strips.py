from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
p=Path(__file__).parent;src=p/'output/playwright';runs={}
for v in ['v15','v16']:
 for mode in ['native','twice']:
  k=v+'-'+mode;r=json.loads((src/f'capture-{k}-cli.txt').read_text().split('### Result\n')[1].split('\n')[0]);runs[k]=r;scale=2 if mode=='twice' else 1;size=256*scale;cols=2 if scale==1 else 1
  for start in range(0,len(r['records']),cols):
   out=Image.new('RGB',(size*2*cols,size+24),(33,40,46));d=ImageDraw.Draw(out)
   for i,rec in enumerate(r['records'][start:start+cols]):
    im=Image.open(src/rec['file']);rec['sha256']=hashlib.sha256((src/rec['file']).read_bytes()).hexdigest();x=i*size*2;out.paste(im.crop((0,49,size,49+size)),(x,24));wx=686 if scale==2 else 430;out.paste(im.crop((wx,104,wx+size,104+size)),(x+size,24));d.text((x+3,3),f"{k} {start+i} f{rec['before']['frame']}..{rec['after']['frame']} {rec['before']['clock_ms']:.0f}..{rec['after']['clock_ms']:.0f}ms",fill='white')
   out.save(p/f'{k}-strip-{start:02}.png')
(p/'browser-capture.json').write_text(json.dumps({'runs':runs,'crop_contract':'Fixedcurrentcanvas andfixedworldROI; fullrawscreensretained; labelsbefore/afterrangesnotexactpose.'},indent=2)+'\n');print([(k,len(v['records']),round(v['stopped']['clock_ms'],1)) for k,v in runs.items()])
