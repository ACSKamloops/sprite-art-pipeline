#!/usr/bin/env python3
"""Current bound coverage negatives. Deliberately missing art evidence must fail."""
import argparse,copy,json
from pathlib import Path
from verify_review import verify
root=Path(__file__).resolve().parents[2];base=root/'qc/temporal';parser=argparse.ArgumentParser();parser.add_argument('--evidence',type=Path,default=base/'final96-v3/pairs.json');parser.add_argument('--review',type=Path,default=base/'final96-review.json');parser.add_argument('--contract',type=Path,default=base/'final96-state-contract.json');parser.add_argument('--output',type=Path,default=base/'final96-negative-tests.json');args=parser.parse_args();ep=args.evidence;rp=args.review;e=json.loads(ep.read_text());r=json.loads(rp.read_text());m=Path(e['input_manifest']);contract=args.contract
checks=[]
def check(name,e1,r1,expected,require=True):
 errors=verify(e1,r1,m,contract,require);checks.append({'name':name,'errors':errors,'expected':expected,'passed':expected in errors if expected else not errors})
check('fresh_complete',e,r,None)
for kind,expected in [('adjacent','ordinary_adjacency_missing_or_extra'),('loop_wrap','boundary_coverage_missing_or_extra'),('deliberate_replay_reset','boundary_coverage_missing_or_extra'),('supported_state_transition','boundary_coverage_missing_or_extra')]:
 a=copy.deepcopy(e);b=copy.deepcopy(r);row=next(x for x in a['pairs']if x['kind']==kind);a['pairs'].remove(row);b['visually_viewed_pair_ids'].remove(row['id']);check('missing_'+kind,a,b,expected)
a=copy.deepcopy(r);a['clip_ids'].remove('thrust/right');check('missing_direction',e,a,'clip_or_direction_coverage_incomplete')
a=copy.deepcopy(r);a['visually_viewed_pair_ids'].pop();check('unviewed_pair',e,a,'visual_pair_coverage_incomplete')
a=copy.deepcopy(r);a['manifest_sha256']='0'*64;check('stale_manifest',e,a,'stale_manifest')
a=copy.deepcopy(e);next(x for x in a['pairs']if x['kind']=='supported_state_transition')['supported_state_contract']['policy']='Invented seamless blend';check('altered_transition_policy',a,r,'supported_transition_metadata_missing_or_changed')
if r.get('visual_inheritance'):
 a=copy.deepcopy(r);a['visual_inheritance']['inputs']['comparison']['sha256']='0'*64;check('stale_inheritance_receipt',e,a,'stale_visual_inheritance_input')
 a=copy.deepcopy(r);a['visual_inheritance']['freshly_viewed_pair_ids'].pop();check('missing_fresh_visual_comparison',e,a,'visual_inheritance_coverage_missing_or_overlap')
 a=copy.deepcopy(r);row=next(x for x in e['pairs']if x['before_clip']=='thrust/right'and x['kind']=='adjacent');a['visual_inheritance']['freshly_viewed_pair_ids'].remove(row['id']);a['visual_inheritance']['inherited_pair_ids'].append(row['id']);check('changed_thrust_cannot_inherit',e,a,'changed_pair_cannot_inherit')
out={'checks':checks,'passed':all(x['passed']for x in checks),'scope':'Coverage gate only; never automatic art approval.'};args.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'passed':out['passed']}));raise SystemExit(not out['passed'])
