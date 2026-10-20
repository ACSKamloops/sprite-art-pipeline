"""Direct03 guide replay from retained integer source maps; no generation or outside artwork."""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def arr(n):return np.array(Image.open(ROOT/n).convert('RGBA'))
def mask(n):return np.array(Image.open(ROOT/n).convert('L'))>0
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output path required';out.mkdir(parents=True)
 intake=json.loads((ROOT/'INTAKE.json').read_text())
 for item in intake['copied_files']:assert hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
 base=arr('inputs/03.png');donor=arr('inputs/02.png');repair=mask('masks/03-lower-repair-owner.png');upper=mask('masks/03-stable-upper-hem-owner.png');glove=mask('masks/03-opaque-gloves-protected.png');maps=np.load(ROOT/'maps/03-source02-part-map.npz',allow_pickle=False)
 reconstructed=base.copy();reconstructed[repair]=0
 for ident,source in [(1,donor),(2,donor),(3,base)]:
  for y,x in np.argwhere(maps['source_id']==ident):sx,sy=map(int,maps['source_xy'][y,x]);reconstructed[y,x]=source[sy,sx]
 reconstructed[upper|glove]=base[upper|glove];assert np.array_equal(reconstructed,arr('candidate/03.png'));assert np.array_equal(reconstructed[~repair],base[~repair]);assert np.array_equal(reconstructed[upper|glove],base[upper|glove])
 rows=[]
 for i in range(8):
  dest=out/f'{i:02}.png'
  if i==3:Image.fromarray(reconstructed).save(dest)
  else:shutil.copy2(ROOT/'candidate'/f'{i:02}.png',dest)
  assert dest.read_bytes()==(ROOT/'candidate'/f'{i:02}.png').read_bytes();rows.append({'phase':i,'PNG_bytes_exact':True,'RGBA_exact':True})
 receipt={'status':'PASS direct03 complete source-map reconstruction','generation_calls':0,'external_artwork_dependencies':[],'candidate03_sha256':hashlib.sha256((out/'03.png').read_bytes()).hexdigest(),'all8_output_bytes_exact':True,'source03_upper_hem_gloves_exact':True,'frozen_guide_unchanged':True,'frames':rows,'stage':[128,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'art_acceptance':'pending parent comparison'}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
