#!/usr/bin/env python3
"""Replay the saved recovery experiments into a fresh portable work area."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--repo',type=Path,default=HERE.parents[1]);p.add_argument('--godot',action='store_true');a=p.parse_args()
 out=a.output.absolute();repo=a.repo.resolve()
 if out.exists() or out.is_symlink():raise ValueError('Fresh output directory required')
 out.mkdir(parents=True)
 def run(script,*args):subprocess.run([sys.executable,str(script),*map(str,args)],check=True)
 run(HERE/'build.py','--repo',repo,'--output',out/'comparison-v2')
 run(HERE/'repair_leg.py','--repo',repo,'--base',out/'comparison-v2','--output',out/'leg-repaired-v2')
 expected=json.loads((HERE/'evidence/expected-leg-clip.json').read_text())
 actual=json.loads((out/'leg-repaired-v2/actions/get_up/manifest.json').read_text())
 for left,right in zip(expected['frames'],actual['frames']):
  if (left['rgba_sha256'],left['hold'])!=(right['rgba_sha256'],right['hold']):raise ValueError('Replay differs from saved final candidate')
 if len(expected['frames'])!=len(actual['frames']):raise ValueError('Frame count differs')
 run(HERE/'assemble_candidate.py','--repo',repo,'--clip',out/'leg-repaired-v2/actions/get_up','--output',out/'package-trial')
 for name in ['review','leg-review']:shutil.copytree(HERE/name,out/name)
 if a.godot:run(repo/'research/pixelengine-imagen/tools/build-rpg-preview.py','--package',out/'package-trial','--output',out/'godot-trial','--check')
 result={'frames':len(actual['frames']),'all_saved_RGBA_and_holds_exact':True,'godot_checks_requested':a.godot,'no_generation_requests':True,'visual_acceptance':False}
 (out/'REPLAY-VERIFIED.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
