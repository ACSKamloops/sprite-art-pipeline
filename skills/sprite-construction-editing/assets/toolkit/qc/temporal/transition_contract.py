"""Explicit state transitions are evidence inputs, not inferred from clip names."""
import hashlib,json
from pathlib import Path
KINDS={'supported_state_transition','equipment_selection_transition'}
def load_contract(path,manifest):
 path=Path(path);contract=json.loads(path.read_text());rows=contract.get('transitions',[])
 if contract.get('schema')!='sprite.supported_state_review.v1':raise ValueError('Unsupported state contract schema')
 if not rows:raise ValueError('Empty supported state transition contract')
 if not contract.get('controller_source_bindings'):raise ValueError('Missing controller source bindings')
 for source,want in contract['controller_source_bindings'].items():
  p=Path(source)
  if not p.is_absolute():p=path.parent/p
  if not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise ValueError('Stale controller source binding: '+source)
 seen=set()
 for row in rows:
  if not row.get('id')or row['id']in seen:raise ValueError('Missing or duplicate transition ID')
  seen.add(row['id'])
  if row.get('kind')not in KINDS:raise ValueError('Unknown state transition kind')
  for side in ['before','after']:
   binding=row.get(side+'_clip');index=row.get(side+'_frame')
   if binding not in manifest['clips']:raise ValueError('Missing action/equipment/direction: '+str(binding))
   if not isinstance(index,int)or isinstance(index,bool)or index<0 or index>=len(manifest['clips'][binding]['frames']):raise ValueError('Invalid state transition frame')
   if not row.get(side+'_state')or not row.get(side+'_equipment'):raise ValueError('Missing explicit state/equipment')
  if not row.get('policy')or not row.get('evidence'):raise ValueError('Missing transition policy/evidence')
 return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'controller_source_bindings':contract['controller_source_bindings'],'transitions':rows}
def pair_tuple(row):return (row['before_clip'],row['before_frame'],row['after_clip'],row['after_frame'],row['kind'])
