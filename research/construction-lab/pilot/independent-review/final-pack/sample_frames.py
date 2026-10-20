from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
B=Path('/home/astra/artifacts/copper-scout-bake-private/full-grounded-final-v1/first');O=Path(__file__).resolve().parent
m=json.loads((B/'manifest.json').read_text());timings={}
for key,c in m['clips'].items():
 name,view=key.split('/');samples=[round(i*(len(c['frames'])-1)/7)for i in range(8)];scale=1;sheet=Image.new('RGBA',(768,424),(32,38,46,255));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(samples):
  f=c['frames'][i];im=Image.open(B/f['png']).convert('RGBA');x=j%4*192;y=j//4*212;sheet.alpha_composite(im,(x,y));d.text((x+5,y+192),f'{key} f{i}',fill='white')
 sheet.save(O/(name+'-'+view+'-eight-native.png'))
 if view=='right':
  ids=[0,len(c['frames'])//3,2*len(c['frames'])//3,len(c['frames'])-1];s=Image.new('RGBA',(768,808),(32,38,46,255));d=ImageDraw.Draw(s)
  for j,i in enumerate(ids):
   im=Image.open(B/c['frames'][i]['png']).convert('RGBA').resize((384,384),Image.Resampling.NEAREST);x=j%2*384;y=j//2*404;s.alpha_composite(im,(x,y));d.text((x+5,y+384),f'{key} f{i} exact2x',fill='white')
  s.save(O/(name+'-right-2x.png'))
 p=B/'review'/(name+'-'+view+'-1x.gif');g=Image.open(p);holds=[]
 for i in range(g.n_frames):g.seek(i);holds.append(g.info.get('duration',0))
 timings[key]={'actual_gif_duration_ms':sum(holds),'gif_unique_frames':g.n_frames,'gif_holds_ms':holds,'source_duration_ticks':c['duration_ticks'],'source_fps':m['fps'],'sampled_frames':samples,'last_phase':c['frames'][-1]['pose']['phase'],'last_endpoint':c['frames'][-1]['pose']['endpoint'],'loop':c['loop']}
(O/'timing.json').write_text(json.dumps(timings,indent=2)+'\n')
(O/'sampling-input.json').write_text(json.dumps({'manifest_sha256':hashlib.sha256((B/'manifest.json').read_bytes()).hexdigest(),'source_bindings':m['source_bindings']},indent=2)+'\n')
