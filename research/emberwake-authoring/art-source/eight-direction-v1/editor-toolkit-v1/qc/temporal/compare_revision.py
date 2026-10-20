#!/usr/bin/env python3
"""Compare every bound frame before inheriting any prior visual observation."""
import argparse,gzip,hashlib,json
from pathlib import Path
from PIL import Image

def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('output',type=Path);a=p.parse_args();old=load(a.before);new=load(a.after)
 if a.output.exists():raise SystemExit('Fresh report required')
 issues=[];rows=[];changed=[];inherited=[]
 if set(old['clips'])!=set(new['clips']):issues.append('Binding set changed')
 for c,x in new['clips'].items():
  if c not in old['clips']:continue
  y=old['clips'][c];frames=[];same=[]
  if len(x['frames'])!=len(y['frames']):issues.append('Frame count changed: '+c);continue
  for i,(before,after)in enumerate(zip(y['frames'],x['frames'])):
   src=a.after.parent/after['png'];pixels=hashlib.sha256(Image.open(src).convert('RGBA').tobytes()).hexdigest()
   if pixels!=after['pixel_sha256']:issues.append('Actual PNG differs current manifest: '+c+':'+str(i))
   changed_pose=before['pose']!=after['pose'];changed_rgba=before['pixel_sha256']!=pixels
   item={'frame':i,'before_pixel_sha256':before['pixel_sha256'],'current_actual_pixel_sha256':pixels,'pose_metadata_changed':changed_pose,'rgba_changed':changed_rgba}
   frames.append(item)
   if not changed_rgba and not changed_pose:same.append(i)
  action_changes=[i['frame']for i in frames if i['rgba_changed']or i['pose_metadata_changed']]
  timing_same={k:x.get(k)for k in ['duration_ticks','loop','events','view','equipment_selection','base_clip']}=={k:y.get(k)for k in ['duration_ticks','loop','events','view','equipment_selection','base_clip']}
  if action_changes or not timing_same:changed.append(c)
  else:inherited.append(c)
  rows.append({'clip_id':c,'timing_events_equipment_unchanged':timing_same,'fully_unchanged_rgba_and_pose':not action_changes,'changed_frames':action_changes,'frames':frames})
 out={'schema':'sprite.temporal.revision_comparison.v1','before_manifest_raw_sha256':hashlib.sha256(gzip.decompress(a.before.read_bytes())if a.before.suffix=='.gz'else a.before.read_bytes()).hexdigest(),'after_manifest_sha256':sha(a.after),'before_source_bindings':old['source_bindings'],'after_source_bindings':new['source_bindings'],'current_actual_pngs_checked':sum(len(r['frames'])for r in rows),'changed_bindings':changed,'inheritance_eligible_bindings':inherited,'issues':issues,'rows':rows,'scope':'Per-frame decoded actual current RGBA versus historical manifest SHA plus exact pose metadata/timing comparison. Inheritance is eligibility only; changed bindings require actual fresh visual inspection. No art approval.'}
 a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['current_actual_pngs_checked','changed_bindings','issues']}));raise SystemExit(bool(issues))
if __name__=='__main__':main()
