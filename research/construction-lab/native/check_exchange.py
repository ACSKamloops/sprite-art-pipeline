#!/usr/bin/env python3
"""Independently reopen ORA layer stack and compare to raw native oracle."""
import io,json,zipfile,xml.etree.ElementTree as ET,sys
from pathlib import Path
from PIL import Image
from audit import scalar
BASE=Path(__file__).resolve().parent;issues=[];checks=0;frames=0;layers=0
for d in sorted((BASE/'fixtures').iterdir()):
 b=json.loads((d/'bindings.json').read_text())
 for f in b['frames']:
  expected=scalar(d/f['raw']);filename=d/'exports'/(f['frame_id']+'.ora')
  with zipfile.ZipFile(filename)as z:
   assert z.read('mimetype')==b'image/openraster';root=ET.fromstring(z.read('stack.xml'));actual=Image.new('RGBA',(int(root.get('w')),int(root.get('h'))));stack=list(root.find('stack'))
   for layer in reversed(stack):
    im=Image.open(io.BytesIO(z.read(layer.get('src')))).convert('RGBA');actual.alpha_composite(im,(int(layer.get('x')),int(layer.get('y'))));layers+=1
   merged=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA')
   for kind,image in [('reopened_ORA_stack',actual),('ORA_merged',merged),('exported_PNG',Image.open(d/'exports'/(f['frame_id']+'.png')).convert('RGBA'))]:
    checks+=1
    if image.tobytes()!=expected.tobytes():issues.append({'frame':f['frame_id'],'kind':kind})
   frames+=1
report={'passed':not issues,'checks':checks,'frames':frames,'actual_reopened_layers':layers,'issues':issues,'limits':'OpenRaster layered file bytes reopened and composited independently; no GUI editor launch claimed.'};(BASE/'exchange-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));sys.exit(0 if report['passed']else 1)
