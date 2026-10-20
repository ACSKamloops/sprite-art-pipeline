"""Fresh-output visible-source map reconstruction; no model, editor or canonical dependency."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(ROOT/n).convert('RGBA'))
def m(n):return np.array(Image.open(ROOT/n).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output required';out.mkdir(parents=True);(out/'layers').mkdir()
 intake=json.loads((ROOT/'INTAKE.json').read_text())
 for row in intake['frames']:assert sha(ROOT/row['file'])==row['sha256']
 sources={i:a(f'inputs/A/{i:02}.png') for i in [0,2,6]};rebuilt={};partrows=[]
 for phase in [3,4]:
  base=a(f'inputs/A/{phase:02}.png');repair=m(f'masks/{phase:02}-repair-owner.png');upper=m(f'masks/{phase:02}-stable-upper-hem-owner.png');gloves=m(f'masks/{phase:02}-full-visible-gloves-owner.png');hip=m(f'masks/{phase:02}-actual02-hip-underpaint.png');body=base.copy();body[repair]=0;body[hip]=sources[2][hip]
  for side in ['right','left']:
   z=np.load(ROOT/f'maps/{phase:02}-{side}-leg.npz',allow_pickle=False);sid=int(z['source_phase']);fg=np.zeros_like(base)
   for y,x in np.argwhere(z['owner']):sx,sy=map(int,z['source_xy'][y,x]);assert 0<=sx<128 and 0<=sy<128;fg[y,x]=sources[sid][sy,sx]
   assert np.array_equal(fg,a(f'source-parts/{phase:02}-{side}-mapped-leg.png'));Image.fromarray(fg).save(out/'layers'/f'{phase:02}-{side}.png')
   # Independent scalar source-over preserves existing hip/leg underpaint at partial contours.
   for y,x in np.argwhere(fg[...,3]>0):
    sr,sg,sb,sa=map(int,fg[y,x]);dr,dg,db,da=map(int,body[y,x]);N=sa*255+da*(255-sa);body[y,x]=[(s*sa*255+d*da*(255-sa)+N//2)//N for s,d in [(sr,dr),(sg,dg),(sb,db)]]+[(N+127)//255]
   partrows.append({'phase':phase,'side':side,'source_phase':sid,'mapped_source_pixels':int(z['owner'].sum()),'source_layer_RGBA_exact':True})
  body[upper|gloves]=base[upper|gloves];body[body[...,3]==0]=0;assert np.array_equal(body,a(f'candidate/{phase:02}.png'));assert np.array_equal(body[upper|gloves],base[upper|gloves]);assert np.array_equal(body[~repair],base[~repair]);rebuilt[phase]=body
 rows=[]
 for phase in range(8):
  dst=out/f'{phase:02}.png'
  if phase in rebuilt:Image.fromarray(rebuilt[phase]).save(dst)
  else:shutil.copy2(ROOT/'inputs/A'/f'{phase:02}.png',dst)
  assert dst.read_bytes()==(ROOT/'candidate'/f'{phase:02}.png').read_bytes();rows.append({'phase':phase,'source_map_RGBA_exact':True,'PNG_bytes_exact':True,'sha256':sha(dst),'hold':[9,160]})
 receipt={'status':'PASS actual visible-source scalar reconstruction; no editor packaging in this replay','generation_calls':0,'new_authored_layout_not_recovered_hidden_anatomy':True,'all8_RGBA_and_PNG_bytes_exact':True,'other6_original_PNGs_exact':True,'each_original03_04_full_upper_hem_gloves_RGBA_exact':True,'source_layers':partrows,'frames':rows,'external_artwork_dependencies':[],'stage':[128,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'inherited_quality_score':None,'runtime_tested':False}
 (out/'SOURCE-REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
