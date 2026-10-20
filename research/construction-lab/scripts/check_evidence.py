#!/usr/bin/env python3
"""Verify present evidence bindings and separate mechanical from art acceptance.
This does not rerun the emulator, external application or visual inspection.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    checks=[];failures=[]
    def check(label,ok):
        checks.append({'label':label,'passed':bool(ok)})
        if not ok:failures.append(label)
    def read(name):return json.loads((ROOT/name).read_text())
    for name in ['native/audit-report.json','native/core-crosscheck-report.json','native/native-rules-report.json','native/exchange-report.json',
        'study/ai-local-edit/mechanical-proof.json','study/layered-cutout/construction-proof.json','godot/verification.json','evidence/godot-pixels.json',
        'evidence/ase-current-proof.json','evidence/site-editor-check.json','evidence/skill-forward-test/report.json']:
        r=read(name);check(name,r.get('passed',r.get('pixel_composition_pass',r.get('outside_mask_changed')==0)))
    for name in ['editor/verification.json','native/core-crosscheck-report.json']:
        r=read(name)
        for path,value in r.get('source_sha256',r.get('core_source_sha256',{})).items():check(name+' binds '+path,sha(ROOT/path)==value)
    for path,value in read('native/handoff-hashes.json')['hashes'].items():check('native source '+path,sha(ROOT/'native'/path)==value)
    for review,base in [('native/authoring-review/localized-knee-review.json','study/ai-local-edit'),('native/authoring-review/layered-cutout/review.json','study/layered-cutout')]:
        r=read(review)
        for path,value in r.get('source_file_sha256',r.get('source_asset_sha256',{})).items():check(review+' binds '+path,sha(ROOT/base/path)==value)
        check(review+' retains art rejection',r['decision']=='changes_requested')
    r=read('study/layered-cutout/construction-proof.json');check('Actual ground contact and planted-world samples at pose boundaries only',all(s['ground_contact_pass'] and s['world_stance_slip_pass'] for s in r['stance_checks']))
    current_motion=read('qc/pixel_motion/dense_pilot/comparison-report.json')
    models={m['mode']:m['actual_gpu'] for m in current_motion['models']}
    check('Current whole-held motion failures remain explicit',current_motion['status']=='changes_requested' and
          all(not g['actual_gpu_within_hold_rule_satisfied'] and g['unchanged_slip_limit_px']==0.5
              for name in ['old_12_hold5','dense_60_hold1'] for g in models[name]))
    report={'passed':not failures,'checks':checks,'failures':failures,'mechanical_status':'named_checks_passed_with_motion_failures_retained' if not failures else 'stale_or_failed',
        'authored_art_status':'changes_requested','AI_patch_status':'changes_requested','production_art_approved':False,
        'functional_motion_status':'changes_requested; old raster4px and dense raster1px fail0.5px contact rule',
        'scope':'Current report/source bindings verified; recorded named tool checks remain separate from current held-frame movement and art failures. No production approval inferred.'}
    (ROOT/'evidence/final-evidence-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'failures':failures,'art':'changes_requested'}))
    if failures:raise SystemExit(2)
if __name__=='__main__':main()
