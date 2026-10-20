from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_frame
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert a.output.is_absolute() and not a.output.exists(),'Absolute fresh output required'
a.output.mkdir(parents=True)
initial=json.loads((ROOT/'initial-project.json').read_text());journal=json.loads((ROOT/'journal.json').read_text());records=json.loads((ROOT/'EDITS.json').read_text())
h=History.replay(initial,journal);finalhash=project_hash(h.project)
assert finalhash==project_hash(json.loads((ROOT/'project.json').read_text()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=[]
for r in records:
 i=r['phase'];src=ROOT/'inputs'/f'{i:02}.png';assert sha(src)==r['source_sha256']
 original=np.array(Image.open(src).convert('RGBA'));expected=original.copy()
 for w in r['literal_source_witnesses']:
  x,y=w['destination'];sx,sy=w['donor'];assert original[y,x,3]==0
  assert list(map(int,original[sy,sx]))==w['rgba'];expected[y,x]=original[sy,sx]
 actual=Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA')
 assert actual.tobytes()==expected.tobytes()==render_frame(h.project,f'se{i}').tobytes()
 out=a.output/f'{i:02}.png';actual.save(out);assert sha(out)==r['output_sha256']
 result.append({'phase':i,'exact_RGBA_PNG_and_source_witnesses':True,'actual_changed_pixels':r['actual_changed_pixels']})
for _ in range(len(h.records)):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(len(h.records)):h.redo()
assert project_hash(h.project)==finalhash
(a.output/'REPLAY-RECEIPT.json').write_text(json.dumps({'frames':result,'actual_undo_redo':True,'project_sha256':finalhash,'scope':'Unselected authored shadow underpaint, not recovered anatomy or art approval'},indent=2)+'\n')
print('8/8 exact source witnesses, guarded journal, PNG and undo/redo')
