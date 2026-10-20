"""Compact fresh-output inverse-source-map replay; no editor package or model call."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype('uint8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh output required';out.mkdir(parents=True)
 base=a('inputs/control/03.png');source=a('inputs/control/00.png');z=np.load(R/'maps/03-newQ-source00.npz');part=np.zeros_like(base);owned=z['owner']
 for y,x in np.argwhere(owned):sx,sy=z['source_xy'][y,x];part[y,x]=source[sy,sx]
 assert np.array_equal(part,a('layers/03-newQ-projected-boot.png'))
 composed=over(over(over(a('inputs/03-after-erasure.png'),a('inputs/03-authored-trousers.png')),a('inputs/03-right-retreating-placed.png')),part)
 upper=np.array(Image.open(R/'inputs/owners/03-upper.png'))>0;composed[upper]=base[upper];expected=a('frames/03.png');assert np.array_equal(composed,expected);assert np.array_equal(composed[upper],base[upper]);assert np.array_equal(composed[:86],base[:86]);rows=[]
 initial=json.loads((R/'projects/initial.json').read_text());journal=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,journal);final=json.loads((R/'projects/final.json').read_text());assert project_hash(h.project)==project_hash(final);assert len(journal['receipts'])==1;final_hash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final_hash;(out/'editor').mkdir()
 for i in range(8):
  if i==3:Image.fromarray(composed).save(out/f'{i:02}.png')
  else:
   assert (R/'frames'/f'{i:02}.png').read_bytes()==(R/'inputs/control'/f'{i:02}.png').read_bytes();shutil.copy2(R/'inputs/control'/f'{i:02}.png',out/f'{i:02}.png')
  assert sha(out/f'{i:02}.png')==sha(R/'frames'/f'{i:02}.png');edited=render_cel(h.project,f'brann-se-{i:02}');assert edited.tobytes()==a(f'frames/{i:02}.png').tobytes();edited.save(out/'editor'/f'{i:02}.png');assert sha(out/'editor'/f'{i:02}.png')==sha(R/'frames'/f'{i:02}.png');rows.append({'phase':i,'PNG_RGBA_exact':True,'editor_RGBA_PNG_exact':True,'sha256':sha(out/f'{i:02}.png')})
 receipt={'status':'Construction-only replay, no art/motion acceptance','model_calls':0,'all8_source_map_RGBA_PNG_exact':True,'all8_editor_RGBA_PNG_exact':True,'actual_guarded_editor_transactions':1,'actual_undo_redo':True,'03_actualupper_RGBA_exact':True,'other7_original_PNG_bytes_exact':True,'newQactual00_source_RGBA_exact':True,'explicit_integer_source_over':'Part samples source-perfect; partial-alpha blend derived exactly, not falsely claimed direct donorRGB','hold':[9,160],'cycle':[9,20],'rows':rows}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
