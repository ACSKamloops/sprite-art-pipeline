"""Independent invariants on model functions, not an artistic acceptance test."""
import json,math,hashlib
from pathlib import Path
import build as b
out=b.HERE/'artifacts/frozen-v1'
report={'scope':'continuous geometry/clock/contact; not rendered sprite material or art quality','checks':{}}
max_slip=0; samples=0; contacts={}; min_z=1e9; bone_error=0
for i in range(4321):
 q=-.1+1.2*i/4320; f=b.pose(q)
 for name,l in f['legs'].items():
  ft=l['foot']; min_z=min(min_z,min(p[2] for p in ft['sole_world']))
  bone_error=max(bone_error,abs(l['bone_lengths'][0]-42),abs(l['bone_lengths'][1]-48))
  if ft['contact']:
   names=['heel','toe'] if ft['role']=='flat' else [ft['role']]
   for n in names:
    key=(name,ft['episode'],n); p=ft['points_world'][n]
    if key in contacts: max_slip=max(max_slip,b.length(b.sub(p,contacts[key])))
    else: contacts[key]=p
  samples+=1
assert max_slip<1e-10 and min_z>-1e-10 and bone_error<1e-10
max_boundary=0
for boundary in [0,.08,.48,.58,1]:
 for name,off,rest in [('far',0,[-12,-10,0]),('near',.5,[12,0,0])]:
  q=boundary-off
  left=b.foot(q-1e-8,off,rest); right=b.foot(q+1e-8,off,rest)
  for n in ['heel','toe','ankle']:max_boundary=max(max_boundary,b.length(b.sub(left['points_world'][n],right['points_world'][n])))
assert max_boundary<1e-4
loop_error=0
for n in ['far','near']:
 for point in ['hip','knee','ankle','heel','toe']:
  p0=b.pose(0)['legs'][n]['world'][point];p1=b.pose(1)['legs'][n]['world'][point]
  loop_error=max(loop_error,b.length(b.sub(b.sub(p1,p0),b.mul(b.F,b.D))))
assert loop_error<1e-10
packet=json.loads((out/'poses.json').read_text());assert sum(f['duration_ms'] for f in packet['frames'])==1200
assert packet['builder_sha256']==hashlib.sha256((b.HERE/'build.py').read_bytes()).hexdigest()
assert packet['design_sha256']==hashlib.sha256((b.HERE/'design.json').read_bytes()).hexdigest()
report['checks']={'contact_samples':samples,'max_contact_material_world_slip':max_slip,'min_sole_world_z':min_z,'max_bone_length_error':bone_error,'max_atomic_role_boundary_delta_at_2e_minus8_phase':max_boundary,'loop_translation_error':loop_error,'clock_ms':1200,'source_bindings_current':True}
(out/'invariant-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
