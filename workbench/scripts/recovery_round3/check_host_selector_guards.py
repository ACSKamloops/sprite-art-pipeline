"""Bounded CLI guard checks; no provider calls, no research modifications."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[2]
CLI=BASE/'scripts/recovery_round3/host_flood_mask.py'
OUT=BASE/'docs/recovery-round3-20261014'
IMAGE=Path('/home/astra/artifacts/pixellab-cutout-connectivity-20261014/inputs/connectivity-rgba.png')
sha=lambda b:hashlib.sha256(b).hexdigest()
def check():
    recorded=OUT/'manual-selector-examples/tolerance8/receipt.json';original=recorded.read_bytes();cases=[]
    with tempfile.TemporaryDirectory(prefix='selector-guard-',dir=OUT)as tmp:
        t=Path(tmp);oversize=t/'oversize.png';Image.new('RGBA',(513,1),(1,2,3,255)).save(oversize)
        invalid=t/'not-png.bin';invalid.write_bytes(b'synthetic non-PNG fixture')
        definitions=[('nonfinite_tolerance',IMAGE,0,0,'nan',t/'nan'),('seed_outside',IMAGE,96,0,'0',t/'seed'),('side_over512',oversize,0,0,'0',t/'oversize'),('not_png',invalid,0,0,'0',t/'nonpng'),('existing_directory',IMAGE,0,0,'0',recorded.parent)]
        for name,image,x,y,tolerance,target in definitions:
            p=subprocess.run([sys.executable,str(CLI),'--image',str(image),'--seed-x',str(x),'--seed-y',str(y),'--tolerance',tolerance,'--output-dir',str(target)],capture_output=True,text=True,timeout=10)
            assert p.returncode==2,(name,p.stdout,p.stderr)
            if name!='existing_directory':assert not target.exists(),name
            cases.append(dict(name=name,returncode=p.returncode,stderr=p.stderr.strip(),provider_calls=0))
    assert recorded.read_bytes()==original
    summaries=[]
    for name in ['tolerance8','tolerance32']:
        d=OUT/'manual-selector-examples'/name;r=json.loads((d/'receipt.json').read_text())
        assert r['harness_sha256']==sha(CLI.read_bytes())
        assert r['output_mask_png_sha256']==sha((d/'mask.png').read_bytes())
        summaries.append(dict(example=name,selected_pixels=r['observed']['selected_pixels'],mask_png_sha256=r['output_mask_png_sha256']))
    result=dict(classification='targeted-offline-cli-guard-checks',harness_sha256=sha(CLI.read_bytes()),cases=cases,existing_receipt_unchanged=True,examples=summaries,untested='Actual timeout and source-pin-mutation failure not induced; limits inspected in code.',provider_calls=0)
    (OUT/'HOST-SELECTOR-CLI-CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':check()
