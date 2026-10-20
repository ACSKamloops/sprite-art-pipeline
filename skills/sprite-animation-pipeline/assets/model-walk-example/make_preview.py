"""Mechanical native-canvas previews and coverage/bounds; no per-frame art edits."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
p=Path(sys.argv[1]);m=json.loads((p/'manifest.json').read_text());size=m['canvas'][0];sheet=Image.new('RGBA',(size*12,(size+20)*4),(27,33,39,255));d=ImageDraw.Draw(sheet);checks=[]
for row,(view,entries) in enumerate(m['views'].items()):
 frames=[]
 for col,e in enumerate(entries):
  im=Image.open(p/e['png']).convert('RGBA');box=im.getchannel('A').getbbox();checks.append({'view':view,'sample':col,'bounds':box,'size_correct':im.size==tuple(m['canvas']),'has_transparency':im.getchannel('A').getextrema()[0]==0,'unclipped':box is not None and box[0]>0 and box[1]>0 and box[2]<size and box[3]<size})
  sheet.alpha_composite(im,(col*size,row*(size+20)));d.text((col*size+3,row*(size+20)+size+3),f'{view} {col}',fill='white')
  bg=Image.new('RGBA',(size,size),(27,33,39,255));bg.alpha_composite(im);frames.append(bg.convert('RGB'))
 durations=[round((i+1)*m['cycle_seconds']*1000/12/10)*10-round(i*m['cycle_seconds']*1000/12/10)*10 for i in range(12)]
 for scale in [1,2,3]:
  enlarged=[f.resize((size*scale,size*scale),Image.Resampling.NEAREST)for f in frames];enlarged[0].save(p/f'walk-{view}-{scale}x.gif',save_all=True,append_images=enlarged[1:],duration=durations,loop=0,disposal=2)
sheet.save(p/'contact-all.png');sheet.resize((sheet.width*2,sheet.height*2),Image.Resampling.NEAREST).save(p/'contact-all-2x.png')
report={'schema':'model-sprite-render-coverage/v1','passed':len(checks)==48 and all(x['size_correct']and x['has_transparency']and x['unclipped']for x in checks),'checks':checks,'manifest_sha256':hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest(),'scope':'Actual image coverage, canvas, alpha and clipping only. Not artistic acceptance, world contact or dense temporal validation.'};(p/'coverage.json').write_text(json.dumps(report,indent=2)+'\n');print(report['passed'])
