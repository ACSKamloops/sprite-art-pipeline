"""Independent actual RGBA, protected-source, stale rejection and reversible replay checks."""
from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(label,result):checks.append({'label':label,'passed':bool(result)})
for view in ['front','right','back','left']:
 for i,frame in enumerate([0,10,20]):
  rgba=lambda p:Image.open(p).convert('RGBA').tobytes()
  check(f'{view} frame{frame} actual rollback RGBA',rgba(ROOT/'baseline'/view/f'{i:02}.png')==rgba(ROOT/'rollback'/view/f'{i:02}.png'))
  check(f'{view} frame{frame} actual edited packed reopen RGBA',rgba(ROOT/'edited'/view/f'{i:02}.png')==rgba(ROOT/'edited/reopen'/f'{view}-frame{frame}.png'))
comparison=json.loads((ROOT/'comparison.json').read_text())
check('All12 baseline actual RGBA equals v11',comparison['all12_baseline_RGBA_exact_final_v11'])
for row in comparison['rows']:
 check(f"{row['view']} frame{row['source_frame']} unchanged alpha",row['alpha_changed_pixels']==0)
 check(f"{row['view']} frame{row['source_frame']} delta4+ localized",row['thresholded_regions']['4']['outside_feature_domain_plus2px']==0)
protected=json.loads((ROOT/'protected-before.json').read_text())
for p,digest in protected.items():check('Protected source/output '+p,sha(ROOT.parent/p)==digest)
check('Rolled back exact descriptor bytes',(ROOT/'face_detail.json').read_bytes()==(ROOT/'descriptor-before.json').read_bytes())
proc=subprocess.run([sys.executable,str(ROOT/'apply_edit.py'),'apply'],text=True,capture_output=True,check=True);apply=json.loads(proc.stdout)
old=sha(ROOT/'face_detail.json');proc=subprocess.run([sys.executable,str(ROOT/'apply_edit.py'),'apply'],text=True,capture_output=True)
check('Stale replay rejects atomically',proc.returncode!=0 and sha(ROOT/'face_detail.json')==old)
proc=subprocess.run([sys.executable,str(ROOT/'apply_edit.py'),'undo'],text=True,capture_output=True,check=True);undo=json.loads(proc.stdout)
check('Replay and exact undo',apply['exact_snapshot_bytes']and undo['exact_snapshot_bytes']and(ROOT/'face_detail.json').read_bytes()==(ROOT/'descriptor-before.json').read_bytes())
report={'schema':'source-attached-fineedit-reversible-proof/v1','passed':all(x['passed']for x in checks),'checks':checks,'replay_apply':apply,'replay_undo':undo,'actual_comparison_sha256':sha(ROOT/'comparison.json'),'outside_domain_delta1_pixels':sum(x['thresholded_regions']['1']['outside_feature_domain_plus2px']for x in comparison['rows']),'scope':'12 bounded sourceframes, actual native renderer pixels and packed reopening. Delta1 remote variation is reported rather than strict outside-zero claim; no art approval or fullcycle claim.'}
(ROOT/'final-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',report['passed'],'checks',len(checks))
if not report['passed']:raise SystemExit(2)
