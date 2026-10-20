"""Independent bytes/clock/source checks for the equipped candidate, no art approval."""
from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'candidate-walk-bow160-game-light-v11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'manifest.json').read_text());checks=[]
checks.append({'label':'Native source24fps/30frame cycle1.25sec','passed':m['source_fps']==24 and m['source_action_frames']==[0,30] and m['cycle_seconds']==1.25})
checks.append({'label':'Renderer frozen before invocation','passed':sha(ROOT/'render_walk_game_light.py')==sha(ROOT/'source/renderers/render_walk_game_light-v11.py')==m['render_script_sha256']})
for p,digest in m['source_sha256'].items():checks.append({'label':'Source '+p,'passed':sha(ROOT/p)==digest})
for view,entries in m['views'].items():
 checks.append({'label':view+' twelve unique keys','passed':len(entries)==12})
 for i,e in enumerate(entries):
  path=OUT/e['png'];im=Image.open(path).convert('RGBA');box=im.getchannel('A').getbbox()
  checks.append({'label':view+' '+str(i)+' hash/clock/canvas/unclipped','passed':sha(path)==e['sha256'] and e['source_frame']==i*2.5 and e['seconds']==i*2.5/24 and im.size==(160,160) and box is not None and box[0]>0 and box[1]>0 and box[2]<160 and box[3]<160})
 expected=Image.open(OUT/view/'00.png').convert('RGBA').tobytes()
 for frame in [0,30]:checks.append({'label':view+' actualpackedscene reopenRGBA frame'+str(frame),'passed':Image.open(OUT/'reopen'/f'{view}-frame{frame}.png').convert('RGBA').tobytes()==expected})
 with Image.open(OUT/f'walk-{view}-1x.gif')as gif:
  durations=[]
  for i in range(gif.n_frames):gif.seek(i);durations.append(gif.info['duration'])
  checks.append({'label':view+' actualGIF1.25sec twelveorderedkeys','passed':gif.n_frames==12 and sum(durations)==1250,'durations_ms':durations})
original=ROOT/'candidate-walk-polished160-final24-v9';before=json.loads((original/'landmarks.json').read_text());after=json.loads((OUT/'landmarks.json').read_text())
for view,entries in before['views'].items():
 for a,b in zip(entries,after['views'][view]):checks.append({'label':view+' evaluated sourcepose preserved '+str(a['source_frame']),'passed':a['root_world']==b['root_world'] and all(b['landmarks'][k]==v for k,v in a['landmarks'].items())})
transforms=m['view_transforms'];base=transforms['front']['lights_camera_space_matrices']
for view,t in transforms.items():
 for lamp,matrix in t['lights_camera_space_matrices'].items():
  residual=max(abs(a-b)for row0,row1 in zip(matrix,base[lamp])for a,b in zip(row0,row1));checks.append({'label':view+' '+lamp+' fixed camera-space lighting','passed':residual<=1e-5,'maximum_matrix_residual':residual,'tolerance':1e-5})
r={'schema':'equipped-source-walk-byte-audit/v1','passed':all(c['passed']for c in checks),'checks':checks,'manifest_sha256':sha(OUT/'manifest.json'),'packed_scene_sha256':sha(OUT/'ranger-walk-render.blend'),'scope':'Actual source/frame hashes, sourceclock/GIFduration, PNGcanvas/clipbounds, eightactualnative-Blender reopened/loop RGBA byte matches, and unchanged evaluated bodylandmarks. Does not establish art quality, sourceauthor exclusive intent, or worldcontact.'}
report=OUT/'byte-validation.json'
if report.exists():raise ValueError('Refuse overwrite prior audit')
report.write_text(json.dumps(r,indent=2)+'\n');print('passed',r['passed'],'checks',len(checks))
if not r['passed']:raise SystemExit(2)
