"""Independent frozen source-map and guarded-journal replay; fresh output only."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
 for n in ['source','journal']:(a.output/n).mkdir()
 for rel,h in json.loads((R/'inputs/HASHES.json').read_text()).items():assert sha(R/'inputs'/rel)==h
 before=np.array(Image.open(R/'inputs/control/05.png').convert('RGBA'));z=np.load(R/'preview-v1/maps/05-projection.npz')
 owner=np.array(Image.open(R/'preview-v1/maps/source-foreleg-owner.png'))>0;protect=np.array(Image.open(R/'preview-v1/maps/protected-upper.png'))>0
 assert np.array_equal(z['row_dx'],np.floor(-3*np.clip((np.arange(128)-82)/16,0,1)+.5).astype(int))
 # Independently forward-construct from the source-owner and explicit row field,
 # then compare each actual retained inverse source sample and outputPNG.
 moved=np.zeros_like(before);expected_xy=np.full((128,128,2),-1,np.int16)
 for y,x in np.argwhere(owner):
  dx=int(z['row_dx'][y]);moved[y,x+dx]=before[y,x];expected_xy[y,x+dx]=[x,y]
 use=(moved[...,3]>0)&~protect;expected_xy[~use]=-1
 assert np.array_equal(use,z['placed']) and np.array_equal(expected_xy,z['source_xy'])
 built=before.copy();built[owner]=0;built[use]=moved[use];built[protect]=before[protect]
 assert np.array_equal(built[protect],before[protect])
 initial=json.loads((R/'projects/initial.json').read_text());journal=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,journal)
 assert project_hash(h.project)==project_hash(json.loads((R/'projects/final.json').read_text()))
 rows=[]
 for i in range(8):
  expected=R/'preview-v1/frames'/f'{i:02}.png';source=Image.fromarray(built)if i==5 else Image.open(R/'inputs/control'/f'{i:02}.png').convert('RGBA')
  source.save(a.output/'source'/f'{i:02}.png');render=render_cel(h.project,f'f{i:02}');render.save(a.output/'journal'/f'{i:02}.png')
  assert sha(a.output/'source'/f'{i:02}.png')==sha(expected);assert sha(a.output/'journal'/f'{i:02}.png')==sha(expected)
  assert source.tobytes()==render.tobytes()==Image.open(expected).convert('RGBA').tobytes()
  if i!=5:assert sha(expected)==sha(R/'inputs/control'/f'{i:02}.png')
  rows.append({'phase':i,'source_and_journal_RGBA_PNG_exact':True,'sha256':sha(expected)})
 final=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final
 receipt={'status':'PASS retained source projection plus independent actual guarded journal','frames':rows,'other7_PNG_exact':True,'protected05_RGBA_exact':True,'actual_undo_redo':True,'model_calls':0,'hold':[9,160],'cycle':[9,20],'art_approval':False,'GUI_or_engine_tested':False}
 (a.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS8/8 source-map and actual guarded journal RGBA/PNG; protected05, other7, undo/redo')
if __name__=='__main__':main()
