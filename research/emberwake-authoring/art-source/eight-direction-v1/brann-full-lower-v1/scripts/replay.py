#!/usr/bin/env python3
"""Read-only verification by default; --output requires a fresh directory."""
from pathlib import Path
import argparse,json,sys,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import History,render_frame,render_cel,project_hash
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args()
if args.output:
    if not args.output.is_absolute() or args.output.exists():raise SystemExit('Output must be absolute and fresh')
    args.output.mkdir(parents=True)
# Regenerate all registered native keys from raw pixels at the single declared
# sheet transform, independently of the authored construction map generator.
for v in ['se','ne']:
    raw=Image.open(ROOT/'raw'/f'{v}.png').convert('RGBA').resize((512,256),Image.Resampling.NEAREST)
    for i in range(8):
        crop=raw.crop(((i%4)*128,(i//4)*128,(i%4+1)*128,(i//4+1)*128))
        assert crop.tobytes()==Image.open(ROOT/'registered'/v/f'{i:02}.png').convert('RGBA').tobytes()
raw=Image.open(ROOT/'raw'/'se-opposed.png').convert('RGBA').resize((256,128),Image.Resampling.NEAREST)
for j,i in enumerate([2,4]):
    crop=raw.crop((j*128,0,(j+1)*128,128))
    assert crop.tobytes()==Image.open(ROOT/'registered'/'se'/f'corrected-{i:02}.png').convert('RGBA').tobytes()
receipts={}
for v in ['se','ne']:
    initial=json.loads((ROOT/v/'initial-project.json').read_text());journal=json.loads((ROOT/v/'journal.json').read_text())
    for i in range(8):
        spec=json.loads((ROOT/v/'maps'/f'{i:02}.json').read_text());mp=np.load(ROOT/v/'maps'/f'{i:02}.npz')
        owner=mp['owner'];xy=mp['source_xy'];expected=np.zeros((128,128,4),dtype='uint8')
        for j,path in enumerate(spec['sources']):
            selected=owner==j;a=arr(ROOT/path);expected[selected]=a[xy[:,:,1][selected],xy[:,:,0][selected]]
        assert np.array_equal(expected,np.array(render_cel(initial,f'lower{i}')))
        old=arr(ROOT/'inputs'/v/f'{i:02}.png');allowed=np.array(Image.open(ROOT/v/'maps'/f'{i:02}-allowed.png'))>0
        body=old.copy();body[allowed]=0
        assert np.array_equal(body,np.array(render_cel(initial,f'body{i}')))
    live=History.replay(initial,journal).project
    assert project_hash(live)==project_hash(json.loads((ROOT/v/'project.json').read_text()))
    records=[]
    for i in range(8):
        im=render_frame(live,f'f{i}');canonical=ROOT/v/'frames'/f'{i:02}.png'
        assert im.tobytes()==Image.open(canonical).convert('RGBA').tobytes()
        if args.output:
            d=args.output/v;d.mkdir(exist_ok=True);im.save(d/f'{i:02}.png');assert sha(d/f'{i:02}.png')==sha(canonical)
        records.append({'phase':i,'rgba_and_png_exact':True,'sha256':sha(canonical)})
    receipts[v]={'raw_registration_and_integer_map_replay':True,'journal_replay':True,'project_sha256':project_hash(live),'frames':records}
if args.output:(args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('PASS: 16/16 raw-registration, source-map, journal, protected-body and final RGBA frames replay exactly.')
