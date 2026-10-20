from pathlib import Path
import sys,json,argparse,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History,render_frame,project_hash
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
if args.output:
    if not args.output.is_absolute()or args.output.exists():raise SystemExit('Output must be absolute and fresh')
    args.output.mkdir(parents=True)
initial=json.loads((ROOT/'initial-project.json').read_text());journal=json.loads((ROOT/'journal.json').read_text())
h=History.replay(initial,journal);finalhash=project_hash(h.project)
assert finalhash==project_hash(json.loads((ROOT/'project.json').read_text()))
records=[];tab=arr(ROOT/'inputs'/'transported-ne-tabard.png')
for view in ['se','ne']:
 for i in range(8):
    old=arr(ROOT/'inputs'/view/f'{i:02}.png');actual=arr(ROOT/view/f'{i:02}.png');expected=old.copy()
    if view=='se':
        mask=np.array(Image.open(ROOT/'masks'/f'se-{i:02}-extraneous-hem-owner.png'))>0;expected[mask]=0
        assert np.array_equal(actual[88:],old[88:])
    elif i in(2,6):expected=arr(ROOT/'inputs'/f'ne-reviewed-preview-{i:02}.png')
    else:
        mask=np.array(Image.open(ROOT/'masks'/f'ne-{i:02}-accessory-visible.png'))>0;expected[mask]=tab[mask]
        assert np.array_equal(actual[~mask],old[~mask])
    expected[expected[:,:,3]==0]=0
    assert np.array_equal(expected,actual)
    image=render_frame(h.project,f'{view}{i}');assert image.tobytes()==Image.fromarray(actual).tobytes()
    if args.output:
        d=args.output/view;d.mkdir(exist_ok=True);image.save(d/f'{i:02}.png');assert sha(d/f'{i:02}.png')==sha(ROOT/view/f'{i:02}.png')
    records.append({'view':view,'phase':i,'source_recipe_and_journal_RGBA_exact':True,'PNG_sha256':sha(ROOT/view/f'{i:02}.png')})
for _ in range(len(h.records)):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(len(h.records)):h.redo()
assert project_hash(h.project)==finalhash
receipt={'project_sha256':finalhash,'undo_redo_replay_exact':True,'frames':records,'scope':'PNG/source recipe/journal mechanics; no art acceptance or planted-contact claim'}
if args.output:(args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: 16/16 source recipes, final RGBA/PNG bytes and toolkit undo/redo/replay.')
