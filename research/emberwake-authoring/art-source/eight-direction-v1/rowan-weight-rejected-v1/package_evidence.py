from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
Q=Path(__file__).resolve().parent;R=Q/'sourcefield-probe-v1';G=Q/'generation-guide-v1';G.mkdir(exist_ok=False)
for n in ['inputs','masks','proof']:(G/n).mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def a(p):return np.array(Image.open(p).convert('RGBA'))
receipt=json.loads((R/'CONSTRUCTION-RECEIPT.json').read_text())
confirmed={2:[[65,76],[67,76],[53,80],[54,80]]+[[x,81]for x in range(55,61)],6:[[65,76],[66,76],[67,76],[64,77],[64,78],[68,78],[63,79],[68,79],[63,80],[69,80]]+[[x,81]for x in range(54,63)]+[[69,81],[70,82]]}
roles=[];maskrows=[]
for i in [2,6]:
 src=a(Q/f'inputs/current/{i:02}.png');tgt=a(R/f'frames/{i:02}.png');holes=receipt['phases'][i]['new_clear_y76plus'];green=np.zeros((128,128),bool);yellow=green.copy();blue=green.copy()
 for x,y in confirmed[i]:assert src[y,x,3]>0 and tgt[y,x,3]==0;green[y,x]=1
 for hole in holes:
  x,y=hole['at']
  if green[y,x]:continue
  if 48<=x<=81 and 76<=y<=88:yellow[y,x]=1
  else:blue[y,x]=1
 for n,mask in [('demonstrated-interior-coverage-loss',green),('uncertain-waist-or-ownership',yellow),('vacated-outer-silhouette-not-paint-request',blue)]:
  p=G/f'masks/{i:02}-{n}.png';Image.fromarray(mask.astype('uint8')*255).save(p)
  maskrows.append({'phase':i,'role':n,'file':p.relative_to(G).as_posix(),'sha256':sha(p),'coordinates':[[int(x),int(y)]for y,x in np.argwhere(mask)]})
 for kind,p in [('selected-source',Q/f'inputs/current/{i:02}.png'),('rejected-curve-target',R/f'frames/{i:02}.png')]:
  dest=G/f'inputs/{i:02}-{kind}.png';shutil.copyfile(p,dest);roles.append({'phase':i,'role':kind,'file':dest.relative_to(G).as_posix(),'sha256':sha(dest),'meaning':'Authoritative selected existing paint, identity, costume and original pose'if kind=='selected-source'else'Actual failed source-field target; guide to rigid upper height only, not an approved drawing/anatomical target'})
 ov=tgt.copy();ov[green]=[20,220,90,255];ov[yellow]=[255,180,20,255];ov[blue]=[50,130,255,255];Image.fromarray(ov).save(G/f'proof/{i:02}-coverage-classes.png')
for size,tag in [(128,'native'),(256,'2x')]:
 board=Image.new('RGBA',(3*size,2*(size+24)+30),'#e9e4d7');dr=ImageDraw.Draw(board)
 for row,i in enumerate([2,6]):
  for col,(label,path)in enumerate([('selected source',G/f'inputs/{i:02}-selected-source.png'),('REJECTED height target',G/f'inputs/{i:02}-rejected-curve-target.png'),('coverage guide',G/f'proof/{i:02}-coverage-classes.png')]):
   y=row*(size+24);dr.text((col*size+2,y+3),f'{i:02} {label}',fill='black');board.alpha_composite(Image.open(path).resize((size,size),Image.Resampling.NEAREST),(col*size,y+24))
 dr.text((3,2*(size+24)+3),'green: interior gap; amber: uncertain; blue: outer clearance',fill='black')
 board.convert('RGB').save(G/f'proof/source-vs-failed-target-02-06-{tag}.png')
(G/'INPUT-ROLES.json').write_text(json.dumps({'status':'Guide only for root decision; no new generation/repaint authorized by this artifact','stage':[128,128],'registration':{'pivot':[64,112],'pose_fitting':'none'},'clock':{'hold':[9,160],'cycle':[9,20]},'sources':roles,'masks':maskrows,'qualifications':['Masks record observed raster loss in this rejected construction, not proven material/anatomy ownership.','Green is a conservative minimum of visually interior holes requiring continuity if this target is pursued.','Amber can mix missing underpaint, incorrect owner/map decisions and normal silhouette clearance. Root must resolve anatomy before editing.','Blue records other vacated outer pixels and is not a request to fill them.','Existing rigid body/arms/gloves and fixed lower components are separately retained; full anatomical hidden boot masters are not claimed.','No generator input was sent. No human motion review, game or world contact test.']},indent=2)+'\n')
# All cyclic adjacent pairs, source and rejected construction, same clock.
for size,tag in [(128,'native'),(256,'2x'),(84,'84')]:
 for bg,label in [('#e9e4d7','light'),('#1d222b','dark'),('#344c32','forest')]:
  board=Image.new('RGBA',(8*size,4*(size+20)),bg);dr=ImageDraw.Draw(board)
  for bankrow,bank in enumerate([Q/'inputs/current',R/'frames']):
   for i in range(8):
    col=i%4;row=i//4+2*bankrow;j=(i+1)%8;x=col*2*size;y=row*(size+20)
    dr.text((x+2,y+2),f'{"source"if bankrow==0 else"REJECTED"} {i:02}>{j:02}',fill='black'if label=='light'else'white')
    for off,k in enumerate([i,j]):board.alpha_composite(Image.open(bank/f'{k:02}.png').resize((size,size),Image.Resampling.NEAREST),(x+off*size,y+20))
  board.convert('RGB').save(R/f'proof/cyclic-pairs-{tag}-{label}.png')
# Independent map-only replay (does not import producer).
V=Q/'verification';V.mkdir(exist_ok=False);(V/'replayed-rejected').mkdir();vr=[]
for i in range(8):
 src=a(Q/f'inputs/current/{i:02}.png');fixed=a(R/f'layers/{i:02}-fixed-lower.png');use=fixed[...,3]>0;assert np.array_equal(fixed[use],src[use])
 z=np.load(R/f'maps/{i:02}-body.npz');body=np.zeros_like(src)
 for y,x in np.argwhere(z['owner']):sx,sy=z['source_xy'][y,x];body[y,x]=src[sy,sx]
 assert np.array_equal(body,a(R/f'layers/{i:02}-body-rigid.png'))
 out=fixed.copy()
 for name in ['left','right']:
  z=np.load(R/f'maps/{i:02}-{name}-cloth.npz');layer=np.zeros_like(src)
  for y,x in np.argwhere(z['owner']):sx,sy=z['source_xy'][y,x];layer[y,x]=src[sy,sx]
  assert np.array_equal(layer,a(R/f'layers/{i:02}-{name}-mapped-cloth.png'));use=layer[...,3]>0;out[use]=layer[use]
 use=body[...,3]>0;out[use]=body[use]
 expected=R/f'frames/{i:02}.png';assert np.array_equal(out,a(expected));p=V/f'replayed-rejected/{i:02}.png';Image.fromarray(out).save(p);assert sha(p)==sha(expected)
 assert np.array_equal(out[99:],src[99:])
 vr.append({'phase':i,'RGBA_and_PNG_bytes_exact':True,'rows99plus_RGBA_exact':True,'sha256':sha(p)})
(V/'SOURCE-MAP-REPLAY.json').write_text(json.dumps({'status':'PASS exact reproduction of rejected sourcefield; not an art/material gate','frames':vr,'map_compositor':'literal sample replacement for positive alpha; matches producer; no new colors or authored underpaint','complete_boot_preservation':'Not certified: rejected owner partition never received a semantic full-boot acceptance. Rows99+ are verified exactly only.'},indent=2)+'\n')
# Source and failed-probe rational manifests; PNGs stay authoritative.
for base,rel in [(Q/'inputs/current','source'),(R/'frames','rejected')]:
 manifest={'canvas':[128,128],'loop':True,'duration':[9,20],'frames':[{'file':f'{i:02}.png','sha256':sha(base/f'{i:02}.png'),'hold':[9,160]}for i in range(8)]}
 (base/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Original input byte guard.
inputs=json.loads((Q/'INPUTS.json').read_text());guard=[]
for item in inputs:
 actual=sha(Path(item['source']));local=sha(Q/item['local']);assert actual==local==item['sha256'];guard.append({**item,'original_and_local_unchanged':True})
(V/'INPUT-HASH-CHECK.json').write_text(json.dumps(guard,indent=2)+'\n')
print(json.dumps({'guide':str(G/'proof/source-vs-failed-target-02-06-2x.png'),'green_counts':[len(confirmed[i])for i in [2,6]],'replay_exact_frames':8,'source_guards':8},indent=2))
