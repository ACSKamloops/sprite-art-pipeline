#!/usr/bin/env python3
"""Append fresh boundary comparisons to immutable, hash-identical adjacency evidence."""
import argparse,copy,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from audit_pairs import metric,motion_contract,sha
from transition_contract import load_contract,pair_tuple

def main():
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--state-contract',type=Path);a=p.parse_args()
 if (a.out/'pairs.json').exists():raise SystemExit('Fresh output required')
 r=json.loads(a.evidence.read_text());manifest=Path(r['input_manifest']);m=json.loads(manifest.read_text());base=manifest.parent
 if r['manifest_sha256']!=sha(manifest)or r['binding_errors']:raise SystemExit('Prior source evidence is stale or failed')
 design=base.parent/'design.json'
 if r['design_sha256']!=sha(design):raise SystemExit('Design changed')
 for name,want in m['source_bindings'].items():
  if sha(base.parent/name)!=want:raise SystemExit('Source binding changed: '+name)
 seenfiles={}
 for row in r['pairs']:
  for side in ['before','after']:
   key=(row[side+'_clip'],row[side+'_frame']);want=row[side+'_file_sha256']
   if key in seenfiles and seenfiles[key]!=want:raise SystemExit('Inconsistent prior frame hashes')
   seenfiles[key]=want
 for (c,i),want in seenfiles.items():
  if sha(base/m['clips'][c]['frames'][i]['png'])!=want:raise SystemExit('Current PNG changed')
 existing={pair_tuple(row)for row in r['pairs']};extras=[];contract=load_contract(a.state_contract,m)if a.state_contract else None
 for c,x in m['clips'].items():
  if not x['loop']and x.get('base_clip',c.split('/')[0])in ['slash','thrust','shoot','cast','hurt']:
   row={'before_clip':c,'before_frame':len(x['frames'])-1,'after_clip':c,'after_frame':0,'kind':'deliberate_replay_reset'}
   if pair_tuple(row)not in existing:extras.append(row);existing.add(pair_tuple(row))
 if contract:
  for row in contract['transitions']:
   if pair_tuple(row)in existing:raise SystemExit('Supported comparison already exists; preserve prior evidence')
   extras.append(copy.deepcopy(row));existing.add(pair_tuple(row))
 a.out.mkdir(parents=True,exist_ok=True);palette=json.loads(design.read_text())['palette'];new=[];images={}
 for row in extras:
  record={k:row[k]for k in ['before_clip','before_frame','after_clip','after_frame','kind']};record['id']=len(r['pairs'])+len(new);arrays=[];poses=[]
  for side in ['before','after']:
   f=m['clips'][row[side+'_clip']]['frames'][row[side+'_frame']];path=base/f['png'];arr=np.array(Image.open(path).convert('RGBA'));arrays.append(arr);poses.append(f['pose']);px=hashlib.sha256(arr.tobytes()).hexdigest()
   if px!=f['pixel_sha256']:raise SystemExit('Current decoded RGBA changed')
   record[side+'_pixel_sha256']=px;record[side+'_file_sha256']=sha(path);record[side+'_phase']=f['pose']['phase'];record[side+'_motion_contract']=motion_contract(f['pose'])
  record['metrics']=metric(*arrays,*poses,palette)
  if row['kind']in ['supported_state_transition','equipment_selection_transition']:record['supported_state_contract']=row
  new.append(record);images[record['id']]=arrays
 # Preserve original sheet IDs/pixels; new comparison sheets are explicit supplements.
 start_sheet=max(s['sheet']for s in r['sheets'])+1
 for offset in range(0,len(new),32):
  sheet=Image.new('RGBA',(1568,1712),(29,34,42,255));draw=ImageDraw.Draw(sheet);chunk=new[offset:offset+32]
  for i,row in enumerate(chunk):
   x=i%4*392;y=i//4*214;aa,bb=images[row['id']];sheet.alpha_composite(Image.fromarray(aa),(x,y));sheet.alpha_composite(Image.fromarray(bb),(x+196,y));draw.text((x+2,y+193),f"{row['id']} {row['before_clip']} > {row['after_clip']} {row['kind']}",fill='white')
  n=start_sheet+offset//32;path=a.out/f'pairs-{n:03d}.png';sheet.save(path);r['sheets'].append({'sheet':n,'pair_ids':[row['id']for row in chunk],'files':{'pairs':{'path':str(path),'sha256':sha(path)}}})
 r['pairs'].extend(new);r['state_contract']=contract or r.get('state_contract');r['extended_from']={'path':str(a.evidence.resolve()),'sha256':sha(a.evidence),'existing_pair_count':len(r['pairs'])-len(new),'appended_pair_count':len(new),'source_reverification':'Current manifest, design, every source binding and every prior referenced PNG file rehashed; supplementary decoded RGBA checked against original manifest.'}
 (a.out/'pairs.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'existing':len(r['pairs'])-len(new),'appended':len(new),'total':len(r['pairs']),'new_sheets':len(new)//32+bool(len(new)%32)}))
if __name__=='__main__':main()
