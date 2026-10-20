#!/usr/bin/env python3
"""Coverage gate: missing pair/view or stale source invalidates completion, never approves art."""
import argparse,json,hashlib
from pathlib import Path
from transition_contract import load_contract,pair_tuple,KINDS
from verify_inheritance import verify_inheritance
def verify(evidence,review,manifest,state_contract=None,require_supported_states=False):
 errors=[];sha=hashlib.sha256(manifest.read_bytes()).hexdigest();m=json.loads(manifest.read_text())
 if evidence['manifest_sha256']!=sha or review['manifest_sha256']!=sha:errors.append('stale_manifest')
 if evidence['binding_errors']:errors.append('source_binding_errors')
 for name,want in m['source_bindings'].items():
  source=manifest.parent.parent/name
  if not source.exists()or hashlib.sha256(source.read_bytes()).hexdigest()!=want:errors.append('current_source_binding_changed')
 checked=set()
 for row in evidence['pairs']:
  for side in ['before','after']:
   key=(row[side+'_clip'],row[side+'_frame'])
   if key in checked:continue
   checked.add(key);c,i=key
   if c not in m['clips']or i>=len(m['clips'][c]['frames']):continue
   source=manifest.parent/m['clips'][c]['frames'][i]['png']
   if not source.exists()or hashlib.sha256(source.read_bytes()).hexdigest()!=row[side+'_file_sha256']:errors.append('current_png_binding_changed')
 ids=[p['id']for p in evidence['pairs']]
 if len(ids)!=len(set(ids)):errors.append('duplicate_pair_id')
 if set(review['visually_viewed_pair_ids'])!=set(ids):errors.append('visual_pair_coverage_incomplete')
 expected={(c,i,c,i+1)for c,x in m['clips'].items()for i in range(len(x['frames'])-1)}
 actual={(p['before_clip'],p['before_frame'],p['after_clip'],p['after_frame'])for p in evidence['pairs']if p['kind']=='adjacent'}
 if actual!=expected:errors.append('ordinary_adjacency_missing_or_extra')
 expected_boundaries=set()
 for c,x in m['clips'].items():
  if x['loop']:expected_boundaries.add((c,len(x['frames'])-1,c,0,'loop_wrap'))
  elif x.get('base_clip',c.split('/')[0])in ['slash','thrust','shoot','cast','hurt']:expected_boundaries.add((c,len(x['frames'])-1,c,0,'deliberate_replay_reset'))
 transitions=[('knockdown','recover'),('recover','idle'),('idle','slash'),('slash','idle'),('idle','thrust'),('thrust','idle'),('idle','shoot'),('shoot','idle'),('idle','cast'),('cast','idle'),('idle','hurt'),('hurt','idle')]
 for view in {c.split('/')[1]for c in m['clips']}:
  for a,b in transitions:
   ca,cb=a+'/'+view,b+'/'+view
   if ca in m['clips']and cb in m['clips']:expected_boundaries.add((ca,len(m['clips'][ca]['frames'])-1,cb,0,'state_transition'))
 bound_contract=None
 if state_contract:
  try:bound_contract=load_contract(state_contract,m)
  except (ValueError,OSError,KeyError):errors.append('invalid_supported_state_contract')
 elif evidence.get('state_contract'):
  try:bound_contract=load_contract(evidence['state_contract']['path'],m)
  except (ValueError,OSError,KeyError):errors.append('invalid_supported_state_contract')
 if require_supported_states and not bound_contract:errors.append('supported_state_contract_required')
 if bound_contract:
  if not evidence.get('state_contract')or evidence['state_contract']['sha256']!=bound_contract['sha256']or review.get('state_contract_sha256')!=bound_contract['sha256']:errors.append('stale_supported_state_contract')
  expected_boundaries.update(pair_tuple(row)for row in bound_contract['transitions'])
  for row in bound_contract['transitions']:
   matches=[p for p in evidence['pairs']if pair_tuple(p)==pair_tuple(row)]
   if len(matches)!=1 or matches[0].get('supported_state_contract')!=row:errors.append('supported_transition_metadata_missing_or_changed')
 actual_boundaries={(p['before_clip'],p['before_frame'],p['after_clip'],p['after_frame'],p['kind'])for p in evidence['pairs']if p['kind']!='adjacent'}
 if actual_boundaries!=expected_boundaries:errors.append('boundary_coverage_missing_or_extra')
 tuples=[(p['before_clip'],p['before_frame'],p['after_clip'],p['after_frame'],p['kind'])for p in evidence['pairs']]
 if len(tuples)!=len(set(tuples)):errors.append('duplicate_pair_comparison')
 if set(review['clip_ids'])!=set(m['clips']):errors.append('clip_or_direction_coverage_incomplete')
 for p in evidence['pairs']:
  for side in ['before','after']:
   c=p[side+'_clip'];i=p[side+'_frame']
   if c not in m['clips']or i>=len(m['clips'][c]['frames'])or p[side+'_pixel_sha256']!=m['clips'][c]['frames'][i]['pixel_sha256']:errors.append('pair_pixel_binding_changed');break
 errors.extend(verify_inheritance(evidence,review))
 return sorted(set(errors))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);p.add_argument('review',type=Path);p.add_argument('manifest',type=Path);p.add_argument('--state-contract',type=Path);p.add_argument('--require-supported-states',action='store_true');a=p.parse_args();errors=verify(json.loads(a.evidence.read_text()),json.loads(a.review.read_text()),a.manifest,a.state_contract,a.require_supported_states);print(json.dumps({'coverage_passed':not errors,'errors':errors,'art_approval':False}));raise SystemExit(bool(errors))
