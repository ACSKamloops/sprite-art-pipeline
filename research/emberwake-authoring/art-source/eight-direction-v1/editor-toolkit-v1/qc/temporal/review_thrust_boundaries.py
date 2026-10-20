#!/usr/bin/env python3
"""Fixed-canvas changed-action sheets including genuine ready gear endpoints."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
if (a.output/'index.json').exists():raise SystemExit('Fresh output required')
a.output.mkdir(parents=True,exist_ok=True);m=json.loads(a.manifest.read_text());rows=[]
for view in ['right','left','front','back']:
 c='thrust/'+view;ready='idle_sword/'+view;x=m['clips'][c]
 for i in range(len(x['frames'])-1):rows.append({'before_clip':c,'before_frame':i,'after_clip':c,'after_frame':i+1,'kind':'adjacent'})
 rows.extend([{'before_clip':ready,'before_frame':0,'after_clip':c,'after_frame':0,'kind':'ready_start'},{'before_clip':c,'before_frame':len(x['frames'])-1,'after_clip':ready,'after_frame':0,'kind':'ready_completion'},{'before_clip':c,'before_frame':len(x['frames'])-1,'after_clip':c,'after_frame':0,'kind':'deliberate_replay_reset'}])
for i,r in enumerate(rows):
 r['id']=i
 for side in ['before','after']:
  f=m['clips'][r[side+'_clip']]['frames'][r[side+'_frame']];png=a.manifest.parent/f['png'];rgba=Image.open(png).convert('RGBA')
  h=hashlib.sha256(rgba.tobytes()).hexdigest()
  if h!=f['pixel_sha256']:raise SystemExit('Stale pixels')
  r[side+'_pixel_sha256']=h
sheets=[]
for offset in range(0,len(rows),32):
 sheet=Image.new('RGBA',(1568,1712),(29,34,42,255));draw=ImageDraw.Draw(sheet);chunk=rows[offset:offset+32]
 for j,r in enumerate(chunk):
  x=j%4*392;y=j//4*214
  for side,dx in [('before',0),('after',196)]:
   f=m['clips'][r[side+'_clip']]['frames'][r[side+'_frame']];sheet.alpha_composite(Image.open(a.manifest.parent/f['png']).convert('RGBA'),(x+dx,y))
  draw.text((x+2,y+193),f"{r['id']} {r['before_clip']} {r['before_frame']} > {r['after_clip']} {r['after_frame']} {r['kind']}",fill='white')
 file=a.output/('pairs-%02d.png'%(offset//32));sheet.save(file);sheets.append({'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'ids':[r['id']for r in chunk]})
(a.output/'index.json').write_text(json.dumps({'manifest_sha256':hashlib.sha256(a.manifest.read_bytes()).hexdigest(),'rows':rows,'sheets':sheets,'quality_approved':False},indent=2)+'\n');print(len(rows))
