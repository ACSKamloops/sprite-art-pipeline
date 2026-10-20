#!/usr/bin/env python3
"""Replay frozen master pixels and affine controls without importing producers."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 src=Path(sys.argv[1]).resolve();dst=Path(sys.argv[2]).resolve();dst.mkdir()
 m=json.loads((src/'manifest.json').read_text());pr=json.loads((src/'MASTER-BAKE-PROOF.json').read_text());controls=json.loads((src/'CONTROLS.json').read_text());w,h=m['canvas'];order=pr['draw_order'];masters={}
 for key in order:
  f=src/'masters'/f'{key}.png';assert sha(f)==pr['masters'][key];masters[key]=np.array(Image.open(f).convert('RGBA'))
 rows=[];n=0
 # Scalar equation here is deliberately independent of the producer's vector
 # expression: inverse of destination=A*source+b, nearest floor(source+.5).
 for i,(frame,ctrl) in enumerate(zip(m['frames'],controls,strict=True)):
  composite=Image.new('RGBA',(w,h));ld=dst/f'{i:03d}';ld.mkdir()
  for key in order:
   tx=ctrl['layer_affines'][key];A=np.array(tx['A']);b=np.array(tx['b']);inv=np.linalg.inv(A);yy,xx=np.mgrid[:h,:w];dx=xx-b[0];dy=yy-b[1];sx=np.floor(inv[0,0]*dx+inv[0,1]*dy+.5).astype(int);sy=np.floor(inv[1,0]*dx+inv[1,1]*dy+.5).astype(int);valid=(sx>=0)&(sx<w)&(sy>=0)&(sy<h);a=np.zeros((h,w,4),np.uint8);a[valid]=masters[key][sy[valid],sx[valid]];im=Image.fromarray(a)
   if 'active_layers' in ctrl and key not in ctrl['active_layers']:a[:]=0;im=Image.fromarray(a)
   original=np.array(Image.open(src/'layers'/f'{i:03d}'/f'{key}.png').convert('RGBA'));assert np.array_equal(a,original),(i,key,int(np.any(a!=original,axis=2).sum()));im.save(ld/f'{key}.png');composite.alpha_composite(im);n+=1
  p=dst/f'{i:03d}.png';composite.save(p);assert sha(src/frame['file'])==frame['sha256'];original=Image.open(src/frame['file']).convert('RGBA');assert composite.tobytes()==original.tobytes();rows.append({'index':i,'RGBA_exact':True,'PNG_bytes_exact':sha(p)==frame['sha256']})
 report={'source_manifest_sha256':sha(src/'manifest.json'),'controls_sha256':sha(src/'CONTROLS.json'),'master_proof_sha256':sha(src/'MASTER-BAKE-PROOF.json'),'frames':len(rows),'layers':len(order),'layer_rasters_exact':n,'results':rows,'scope':'Frozen painted masters plus frozen authored transforms reproduce all layer and final RGBA. No producer imports. This does not regenerate stochastic art or certify anatomy/motion.'};(dst/'REPLAY.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Frozen replay: {n} layer rasters and {len(rows)} composites exact.')
if __name__=='__main__':main()
