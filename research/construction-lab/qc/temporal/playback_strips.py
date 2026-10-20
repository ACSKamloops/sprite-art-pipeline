#!/usr/bin/env python3
"""Chronological actual browser captures, native CSS size, no image alignment."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('receipt',type=Path);a=p.parse_args();d=json.loads(a.receipt.read_text());out=a.receipt.parent;rows=d['routes'];sheets=[]
for offset in range(0,len(rows),4):
 sheet=Image.new('RGB',(1552,888),(32,47,57));draw=ImageDraw.Draw(sheet);group=rows[offset:offset+4]
 for r,row in enumerate(group):
  for c,capture in enumerate(row['captures']):
   path=Path(capture['file']);img=Image.open(path).convert('RGB')
   if img.size!=(194,195):raise SystemExit('Native CSS capture size differs; no automatic rescale')
   if hashlib.sha256(path.read_bytes()).hexdigest()!=capture['sha256']:raise SystemExit('Stale capture')
   sheet.paste(img,(c*194,r*222));draw.text((c*194,r*222+196),f"{row['binding']} tick{capture['held']} t{(capture['wallTime']-row['start'])/1000:.2f}s",fill='white')
 file=out/('chronological-%02d.png'%(offset//4));sheet.save(file);sheets.append({'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bindings':[r['binding']for r in group],'display':'Actual194x195native-size browser canvas screenshot including CSSborder, no recenter/rescale.'})
(out/'chronological-index.json').write_text(json.dumps({'receipt_sha256':hashlib.sha256(a.receipt.read_bytes()).hexdigest(),'sheets':sheets,'art_approval':False},indent=2)+'\n')
