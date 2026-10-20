#!/usr/bin/env python3
"""Independent raw RGBA binding preservation and rendered guard-boundary checks."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(p):return Image.open(p).convert('RGBA').tobytes()
def main():
 p=argparse.ArgumentParser();p.add_argument('old',type=Path);p.add_argument('new',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 if a.output.exists():raise ValueError('Refuse overwrite existing audit')
 old=json.loads((a.old/'manifest.json').read_text());new=json.loads((a.new/'manifest.json').read_text())
 assert old['clips'].keys()==new['clips'].keys()
 changed=[];unchanged=[];checks=[];boundaries=[];samples=0
 for name,c in new['clips'].items():
  oc=old['clips'][name];ticks=[]
  assert c['duration_ticks']==oc['duration_ticks'] and c['events']==oc['events'] and c['loop']==oc['loop']
  for t,(of,nf) in enumerate(zip(oc['frames'],c['frames'])):
   samples+=1
   if pixels(a.old/of['png'])!=pixels(a.new/nf['png']):ticks.append(t)
  (changed if ticks else unchanged).append({'binding':name,'changed_ticks':ticks})
  if name.startswith('thrust/'):
   view=c['view'];idle=new['clips']['idle_sword/'+view]['frames'][0]
   for t in [0,len(c['frames'])-1]:
    f=c['frames'][t];same=pixels(a.new/f['png'])==pixels(a.new/idle['png'])
    fields=['feet','hands','hips','landmarks','grip','fx_anchors','surface_frames']
    diff=[k for k in fields if f['pose'][k]!=idle['pose'][k]]
    boundaries.append({'binding':name,'tick':t,'RGBA_exact_idle_sword_tick0':same,'different_geometric_metadata':diff})
    checks.append(same and not diff)
 expected={'thrust/right','thrust/left','thrust/front'}
 checks += [set(x['binding'] for x in changed)==expected,samples==6000,len(unchanged)==93]
 report={'schema':'copper-scout-thrust-guard-recovery/v1','passed':all(checks),'old_manifest_sha256':digest(a.old/'manifest.json'),'new_manifest_sha256':digest(a.new/'manifest.json'),'source_bindings':new['source_bindings'],'RGBA_frames_compared':samples,'changed_bindings':changed,'unchanged_bindings':unchanged,'exact_guard_boundaries':boundaries,'timing_and_events_preserved':True,'scope':'All 6000 full RGBA frames compared; actual rendered first/last thrust frame versus equipped idle tick0 in all four views. Orthographic depth reach readability and general artistic approval remain separate.'}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'changed':[x['binding'] for x in changed],'unchanged':len(unchanged),'boundaries':boundaries}))
 if not report['passed']:raise SystemExit(2)
if __name__=='__main__':main()
