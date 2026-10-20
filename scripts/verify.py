#!/usr/bin/env python3
"""Run offline package checks without enabling paid generation or servers."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path)
    ap.add_argument('--only',nargs='+',help='Run only the named check(s); receipt remains explicitly partial.')
    args=ap.parse_args()
    out=(args.output or ROOT/'output/verification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')).absolute()
    out.mkdir(parents=True,exist_ok=False);py=sys.executable
    toolkit=ROOT/'skills/sprite-construction-editing/assets/toolkit'
    env={**os.environ,'LP_NUM_THREADS':'4','OMP_NUM_THREADS':'4','PYTHONDONTWRITEBYTECODE':'1'}
    env.pop('PYTHONPATH',None)
    steps=[
      ('repository-content',[py,str(ROOT/'scripts/check_repository.py'),'--report',str(out/'content.json')],ROOT),
      ('workbench-tests',[py,'-m','pytest','-q','tests'],ROOT/'workbench'),
      ('editable-toolkit-tests',[py,'-m','unittest','discover','-s','tests','-v'],toolkit),
      ('approved-walk-manifest',[py,str(ROOT/'skills/sprite-animation-pipeline/scripts/animation_assets.py'),'validate',str(ROOT/'examples/approved-hero/clips.json'),'--report',str(out/'walk-validation.json')],ROOT),
      ('approved-editable',[py,str(toolkit/'scripts/sprite_edit.py'),'validate',str(ROOT/'examples/approved-hero/editable/walk.project.json')],ROOT),
      ('approved-native-bake',[py,str(ROOT/'examples/approved-hero/tools/bake_native_sprites.py'),'--video',str(ROOT/'examples/approved-hero/reproduction/returned-h3-native.mp4'),'--recipe',str(ROOT/'examples/approved-hero/reproduction/bake-recipe.json'),'--output',str(out/'native-bake')],ROOT),
      ('exact-apng',[py,str(ROOT/'skills/sprite-animation-pipeline/scripts/exact_apng.py'),str(ROOT/'skills/sprite-animation-pipeline/assets/apng-smoke/manifest.json'),str(out/'apng')],ROOT),
      ('lyra-rebuild',[py,str(ROOT/'examples/lyra-leg-repair/rebuild.py'),'--output',str(out/'lyra-replay')],ROOT),
    ]
    available=[s[0]for s in steps]
    if args.only:
        unknown=set(args.only)-set(available)
        if unknown:raise SystemExit('Unknown checks: '+repr(sorted(unknown)))
        steps=[s for s in steps if s[0]in args.only]
    records=[]
    for name,cmd,cwd in steps:
        start=time.monotonic()
        try:
            r=subprocess.run(cmd,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
            text=r.stdout;code=r.returncode
        except subprocess.TimeoutExpired as e:
            text=(e.stdout.decode(errors='replace')if isinstance(e.stdout,bytes)else e.stdout or'')+'\nTIMEOUT after300s\n';code=124
        if name=='approved-native-bake' and code==0:
            original=ROOT/'examples/approved-hero/approved/walk'
            old=json.loads((original/'manifest.json').read_text())['frames']
            new=json.loads((out/'native-bake/manifest.json').read_text())['frames']
            matches=len(old)==len(new)==30 and all((original/a['file']).read_bytes()==(out/'native-bake'/b['file']).read_bytes() for a,b in zip(old,new))
            text+='\nAll30 approved PNGs byte-identical: '+str(matches)+'\n'
            if not matches:code=1
        if name=='lyra-rebuild' and code==0:
            expected=ROOT/'examples/lyra-leg-repair/candidate-v4'
            mismatches=[f'{i:02}.png' for i in range(8)
                        if (out/'lyra-replay'/f'{i:02}.png').read_bytes()!=(expected/f'{i:02}.png').read_bytes()]
            text+='\nAll eight replay PNGs byte-identical: '+str(not mismatches)+'\n'
            if mismatches:code=1;text+='Mismatch: '+repr(mismatches)+'\n'
        (out/(name+'.log')).write_text(text)
        tail='\n'.join(text.strip().splitlines()[-5:])
        records.append({'name':name,'command':cmd,'cwd':str(cwd),'exit_code':code,'passed':code==0,'seconds':round(time.monotonic()-start,3),'summary':tail,'log':name+'.log'})
        print(name,'PASS'if code==0 else'FAIL',tail[-350:],flush=True)
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'all_passed':all(r['passed']for r in records),'complete_default_check_set':args.only is None,'available_checks':available,'checks':records,'scope':'Fresh selected offline code/artifact checks. No provider job, server, continuous visual acceptance or whole-PixelLab parity.'}
    (out/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print('Receipt:',out/'RESULTS.json')
    raise SystemExit(0 if report['all_passed'] else 1)
if __name__=='__main__':main()
