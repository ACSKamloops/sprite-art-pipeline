"""Atomic hash-preconditioned descriptor apply and exact-byte undo in this isolated fixture."""
from pathlib import Path
import hashlib,json,sys,os
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def edit(mode):
 patch=json.loads((ROOT/'semantic-patch.json').read_text());current=ROOT/'face_detail.json';before=ROOT/'descriptor-before.json';after=ROOT/'descriptor-after.json'
 if mode not in ['apply','undo']:raise ValueError('Unknown operation')
 if sha(ROOT/'archived-renderer-v11.py')!=patch['expected_renderer_sha256']:raise ValueError('Stale renderer')
 if sha(before)!=patch['expected_descriptor_sha256']or sha(after)!=patch['after_sha256']:raise ValueError('Changed archived descriptors')
 expected=patch['expected_descriptor_sha256']if mode=='apply'else patch['after_sha256']
 if sha(current)!=expected:raise ValueError('Stale descriptor; rejected without mutation')
 old=json.loads(before.read_text());new=json.loads(after.read_text());candidate=json.loads(before.read_text())
 for op in patch['operations']:
  parts=op['path'].split('.')
  if len(parts)!=3 or parts[0]!='marks' or parts[1]not in ['0','1']or parts[2]not in ['color','radius']:raise ValueError('Unsupported field')
  index=int(parts[1]);key=parts[2]
  if candidate['marks'][index][key]!=op['before']:raise ValueError('Field precondition failed')
  candidate['marks'][index][key]=op['after']
 if candidate!=new:raise ValueError('Changes outside declared semantic patch')
 target=after if mode=='apply'else before;data=target.read_bytes();tmp=current.with_suffix('.pending');tmp.write_bytes(data);os.replace(tmp,current)
 return {'mode':mode,'before_sha256':expected,'after_sha256':sha(current),'exact_snapshot_bytes':current.read_bytes()==data}
if __name__=='__main__':print(json.dumps(edit(sys.argv[1])))
