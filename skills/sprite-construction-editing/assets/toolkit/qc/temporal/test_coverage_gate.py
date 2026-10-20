"""Remove evidence and its claimed visual coverage together: completeness must still fail."""
import copy,json,unittest
from pathlib import Path
from verify_review import verify
ROOT=Path(__file__).resolve().parents[2]
class CoverageGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=ROOT/'pilot/rigged-character/generated/manifest.json'
  cls.evidence=json.loads((ROOT/'qc/temporal/baseline-v3/pairs.json').read_text())
  cls.review=json.loads((ROOT/'qc/temporal/baseline-review.json').read_text())
 def omitted(self,kind):
  evidence=copy.deepcopy(self.evidence);review=copy.deepcopy(self.review)
  removed=next(p for p in evidence['pairs']if p['kind']==kind)
  evidence['pairs'].remove(removed);review['visually_viewed_pair_ids'].remove(removed['id'])
  return verify(evidence,review,self.manifest)
 def test_fresh(self):self.assertEqual(verify(self.evidence,self.review,self.manifest),[])
 def test_omitted_adjacent_even_if_visual_claim_matches(self):self.assertIn('ordinary_adjacency_missing_or_extra',self.omitted('adjacent'))
 def test_omitted_loop_wrap_even_if_visual_claim_matches(self):self.assertIn('boundary_coverage_missing_or_extra',self.omitted('loop_wrap'))
 def test_omitted_replay_reset_even_if_visual_claim_matches(self):self.assertIn('boundary_coverage_missing_or_extra',self.omitted('deliberate_replay_reset'))
 def test_omitted_state_transition_even_if_visual_claim_matches(self):self.assertIn('boundary_coverage_missing_or_extra',self.omitted('state_transition'))
if __name__=='__main__':unittest.main()
