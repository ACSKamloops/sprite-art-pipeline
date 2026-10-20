"""Inherited visual judgments require unchanged pixels, pose metadata and timing."""
import gzip,hashlib,json
from pathlib import Path

def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def verify_inheritance(evidence,review):
 chain=review.get('visual_inheritance')
 if not chain:return []
 errors=[]
 for item in chain['inputs'].values():
  p=Path(item['path'])
  if not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('stale_visual_inheritance_input')
 if errors:return errors
 old=read(chain['inputs']['prior_evidence']['path']);oldreview=read(chain['inputs']['prior_review']['path']);comparison=read(chain['inputs']['comparison']['path'])
 if comparison['issues']or comparison['after_manifest_sha256']!=review['manifest_sha256']or comparison['before_manifest_raw_sha256']!=oldreview['manifest_sha256']:errors.append('invalid_visual_revision_comparison')
 eligible=set(comparison['inheritance_eligible_bindings']);lookup={(x['before_clip'],x['before_frame'],x['after_clip'],x['after_frame'],x['kind']):x for x in old['pairs']if x['id']in oldreview['visually_viewed_pair_ids']}
 ids=set(chain['inherited_pair_ids']);fresh=set(chain['freshly_viewed_pair_ids']);allids={r['id']for r in evidence['pairs']}
 if ids&fresh or ids|fresh!=allids:errors.append('visual_inheritance_coverage_missing_or_overlap')
 for r in evidence['pairs']:
  if r['id']not in ids:continue
  before=lookup.get((r['before_clip'],r['before_frame'],r['after_clip'],r['after_frame'],r['kind']))
  if not before or r['before_clip']not in eligible or r['after_clip']not in eligible:errors.append('changed_pair_cannot_inherit');continue
  for side in ['before','after']:
   if r[side+'_pixel_sha256']!=before[side+'_pixel_sha256']or r[side+'_motion_contract']!=before[side+'_motion_contract']:errors.append('changed_pair_cannot_inherit')
 return sorted(set(errors))
