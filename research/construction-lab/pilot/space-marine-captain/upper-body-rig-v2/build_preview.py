"""Unchanged root assembler, isolated new upper module; no root or v1 writes."""
from pathlib import Path
import json,runpy,sys,os,shutil,argparse
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
def main(out):
 if out.exists():raise ValueError('Refuse frozen output')
 out.mkdir(parents=True);snapshot=out/'snapshot';private=snapshot/'pilot/space-marine-captain';upper=private/'upper-body-rig-v1';upper.mkdir(parents=True)
 for n in ['build.py','design.json','pixel_affine.py']:shutil.copy2(ROOT/n,upper/n)
 (upper/'source').mkdir();shutil.copy2(ROOT/'source/approved-256.png',upper/'source/approved-256.png')
 root=Path('/home/astra/projects/sprite-construction-lab');(snapshot/'pilot/captain-leg-rig-v1').symlink_to(root/'pilot/captain-leg-rig-v1',target_is_directory=True);captain=root/'pilot/space-marine-captain';cwd=Path.cwd();args=sys.argv[:]
 try:
  os.chdir(snapshot);sys.argv=[str(captain/'assemble.py'),'--legs','pilot/captain-leg-rig-v1/convex-near-greave-v1/long-stride-keyshape-v3','--upper-rotation','scale2x8-approximation','--upper-motion','weighted','--inline-foreground','--output',str(out/'fixed')];ns=runpy.run_path(str(captain/'assemble.py'),run_name='isolated_upper_trial');ns['main'].__globals__['ROOT']=private;ns['main']()
  sys.argv=[str(captain/'retime.py'),'--candidate',str(out/'fixed'),'--output',str(out/'weighted')];runpy.run_path(str(captain/'retime.py'),run_name='__main__')
 finally:os.chdir(cwd);sys.argv=args
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/loaded-v1');a=p.parse_args();main(a.output.resolve())
