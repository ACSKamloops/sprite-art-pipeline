#!/usr/bin/env python3
"""Rebuild frozen-input experiments into a fresh folder, never over originals."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, runpy, sys

root=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
out=a.out.resolve()
if out.exists():p.error('Use a fresh output directory')
frozen=json.loads((root/'INPUTS-FROZEN.json').read_text())
for e in frozen:
    path=root/e['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256'],path
spec=importlib.util.spec_from_file_location('build',root/'build.py')
module=importlib.util.module_from_spec(spec);sys.modules['build']=module;spec.loader.exec_module(module)
out.mkdir(parents=True);(out/'inputs').mkdir()
module.ROOT=out;module.SRC=root/'inputs';module.main()
runpy.run_path(str(root/'test_single_donor.py'),run_name='__main__')
exact_pngs=0
for original in [*sorted((root/'frames').rglob('*.png')),*sorted((root/'proof').glob('*.png')),*sorted((root/'single-donor-v2').rglob('*.png'))]:
    replayed=out/original.relative_to(root)
    assert replayed.exists(),replayed
    assert original.read_bytes()==replayed.read_bytes(),replayed
    exact_pngs+=1
receipt={'frozen_inputs':len(frozen),'exact_pngs':exact_pngs,'coordinate_control':json.loads((out/'single-donor-v2/METHOD.json').read_text())['inverse_coordinate_control'],'art_acceptance':False}
(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
