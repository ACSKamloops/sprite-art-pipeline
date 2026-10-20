#!/usr/bin/env python3
"""Check actual painted attachment adjacency, not just authored joint targets."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def neighbours(mask):
 h,w=mask.shape;p=np.pad(mask,1);out=np.zeros_like(mask)
 for dy in [-1,0,1]:
  for dx in [-1,0,1]:out|=p[1+dy:1+dy+h,1+dx:1+dx+w]
 return out
def main():
 src=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else src/'RASTER-JOINS.json';assert not out.exists();m=json.loads((src/'manifest.json').read_text());pr=json.loads((src/'MASTER-BAKE-PROOF.json').read_text());controls=json.loads((src/'CONTROLS.json').read_text());order=pr['draw_order'];rows=[];pins={};fail=[]
 for i,c in enumerate(controls):
  masks={};top=np.full((m['canvas'][1],m['canvas'][0]),-1,int)
  for j,k in enumerate(order):
   f=src/'layers'/f'{i:03d}'/f'{k}.png';pins[f'{i:03d}/{k}']=sha(f);masks[k]=np.array(Image.open(f).convert('RGBA'))[:,:,3]>0;top[masks[k]]=j
  for side in ['near','far']:
   a=side+'_forearm';b=side+'_hand'
   if b not in c.get('active_layers',order):continue
   raster_count=int(np.count_nonzero(masks[b]&neighbours(masks[a])));visible_count=int(np.count_nonzero((top==order.index(b))&neighbours(top==order.index(a))));row={'frame':i,'pair':[a,b],'layer_adjacent_hand_pixels':raster_count,'visible_adjacent_hand_pixels':visible_count};rows.append(row)
   if raster_count==0:fail.append(row)
 report={'checker_sha256':sha(__file__),'manifest_sha256':sha(src/'manifest.json'),'controls_sha256':sha(src/'CONTROLS.json'),'layer_PNGs':pins,'connections':rows,'connection_count':len(rows),'minimum_layer_contact':min(r['layer_adjacent_hand_pixels'] for r in rows),'minimum_visible_contact':min(r['visible_adjacent_hand_pixels'] for r in rows),'failures':fail,'scope':'Actual8-neighbour held-pose alpha contact, plus visible top-layer witnesses; no physical force, world-foot contact, or anatomical/art approval. Whole painted replacement poses are outside separate-part join checks.'};out.write_text(json.dumps(report,indent=2)+'\n');print('Raster joins:',len(rows),'minlayer',report['minimum_layer_contact'],'minvisible',report['minimum_visible_contact'],'failures',len(fail));sys.exit(1 if fail else 0)
if __name__=='__main__':main()
