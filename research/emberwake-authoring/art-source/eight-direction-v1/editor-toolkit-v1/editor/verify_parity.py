"""Compare real-browser operation fixtures with the independent Python core."""
import argparse,json,pathlib,sys
p=argparse.ArgumentParser();p.add_argument('--core-root',type=pathlib.Path,required=True);p.add_argument('--fixture',type=pathlib.Path,default=pathlib.Path(__file__).parent/'output/playwright/browser-check.json');a=p.parse_args();sys.path.insert(0,str(a.core_root));from sprite_lab import project_hash,render_frame,apply_transaction
from sprite_lab.history import History
r=json.loads(a.fixture.read_text());state=r['initial_project'];checks=[]
def check(value,name):
 checks.append(dict(name=name,passed=bool(value)))
 if not value:raise AssertionError(name)
check(project_hash(state)==r['initial_sha256'],'Initial canonical hash')
for i,step in enumerate(r['parity_steps']):
 result=apply_transaction(state,step['transaction']);check(result['project']==step['project'],f'Operation{i} exact project');check(result['receipt']==step['receipt'],f'Operation{i} exact receipt/hash/diff')
 for frame,rgba in step['frames'].items():check(list(render_frame(result['project'],frame).tobytes())==rgba,f'Operation{i}/{frame} exact RGBA')
 state=result['project']
history=History.replay(r['initial_project'],r['mouse_journal']);check(history.project==r['mouse_saved_project'],'Actual mouse journal Python replay');out=dict(passed=True,checks=checks,count=len(checks),operation_count=len(r['parity_steps']),fixture=str(a.fixture),core_root=str(a.core_root));(a.fixture.parent/'python-parity.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'operations':len(r['parity_steps'])}))
