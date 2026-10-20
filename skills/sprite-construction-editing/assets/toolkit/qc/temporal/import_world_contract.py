#!/usr/bin/env python3
"""Bind actual presented controller transitions; do not invent skipped endpoints."""
import argparse,hashlib,json
from pathlib import Path
from transition_contract import pair_tuple,load_contract

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('controller',type=Path);p.add_argument('manifest',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 if a.output.exists():raise SystemExit('Fresh output required')
 d=json.loads(a.report.read_text());m=json.loads(a.manifest.read_text())
 if not d['passed']or d['failures']or sha(a.controller)!=d['controller_sha256']:raise SystemExit('Unverified/stale world proof')
 for name,want in d['source_bindings'].items():
  if m['source_bindings'].get(name)!=want:raise SystemExit('Source differs: '+name)
 rows={}
 for group,li,ledger in [(group,li,row)for group in ['ledger','thrust_ledger']for li,row in enumerate(d.get(group,[]))]:
  for ti,t in enumerate(ledger['transitions']):
   kind='equipment_selection_transition'if 'Explicit selection' in t['policy']else'supported_state_transition'
   before=t['from_binding'];after=t['to_binding']
   if before not in m['clips']or after not in m['clips']:raise SystemExit('Unbaked world binding')
   row={'before_clip':before,'before_frame':t['from_frame'],'after_clip':after,'after_frame':t['to_frame'],'kind':kind,'before_state':before.split('/')[0],'after_state':after.split('/')[0],'before_equipment':m['clips'][before]['frames'][t['from_frame']]['pose']['effective_equipment'],'after_equipment':t['equipment'],'policy':t['policy'],'evidence':[{'report_path':str(a.report.resolve()),'report_sha256':sha(a.report),'ledger_group':group,'ledger_index':li,'transition_index':ti,'clock':t['tick'],'scope':'Last actually presented GPU frame as logged, including explicit terminal-hold captures; not inferred terminal frame.'}]}
   key=pair_tuple(row)
   if key in rows:rows[key]['evidence'].extend(row['evidence'])
   else:row['id']='observed-world-%03d'%len(rows);rows[key]=row
 out={'schema':'sprite.supported_state_review.v1','manifest_sha256':sha(a.manifest),'controller_source_bindings':{str(a.controller.resolve()):sha(a.controller),str(a.report.resolve()):sha(a.report)},'transitions':list(rows.values()),'scope':'Observed eight equipment/view paths and explicit thrust guards when present; finite sampled controller ledger, not all possible interruptions or visual blend approval. Inspection-only base boundaries remain separate.'}
 a.output.write_text(json.dumps(out,indent=2)+'\n');load_contract(a.output,m);print(json.dumps({'transitions':len(rows),'report_checks':len(d['checks']),'sha256':sha(a.output)}))
if __name__=='__main__':main()
