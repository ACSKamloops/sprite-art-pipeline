"""Real-corpus verifier checks plus explicit negative data perturbations; no source writes."""
import copy,json,unittest
from pathlib import Path
from index_captures import Verifier,continuity,actor_state
ROOT=Path('/home/astra/projects/som-sprite-lab-site/native-godot')
class CatalogTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  idx=json.loads((ROOT/'capture-index.json').read_text());cls.route=json.loads((ROOT/idx['routes'][0]['path']).read_text());cls.frame=cls.route['frames'][0];cls.verify=Verifier(ROOT,'/home/astra/projects/som-native-effect-renderer')
 def test_real_frame_five_hashes_and_raw_selection(self):
  r=self.verify.frame(self.frame);self.assertEqual(len(r[0]),5);self.assertEqual(r[1][self.frame['actor_slot']][0],self.frame['actor']['generic_index'])
 def test_wrong_wram_hash_rejected(self):
  f=copy.deepcopy(self.frame);f['source_hashes']['wram.bin']='0'*64
  with self.assertRaisesRegex(ValueError,'Wrong raw source SHA'):self.verify.frame(f)
 def test_wrong_display_hash_rejected(self):
  f=copy.deepcopy(self.frame);f['expected_pixel_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Expected display'):self.verify.frame(f)
 def test_wrong_selected_generic_rejected(self):
  f=copy.deepcopy(self.frame);f['actor']['generic_index']+=1
  with self.assertRaisesRegex(ValueError,'Raw-selected generic'):self.verify.frame(f)
 def test_missing_tick_rejected(self):
  frames=copy.deepcopy(self.route['frames'][:3]);frames.pop(1)
  with self.assertRaisesRegex(ValueError,'source tick'):continuity(frames)
 def test_duplicate_tick_rejected(self):
  frames=copy.deepcopy(self.route['frames'][:2]);frames[1]['source_tick']=frames[0]['source_tick']
  with self.assertRaisesRegex(ValueError,'source tick'):continuity(frames)
 def test_flattened_hold_rejected(self):
  frames=copy.deepcopy(self.route['frames'][:2]);frames[0]['duration_ticks']=2
  with self.assertRaisesRegex(ValueError,'invented holds'):continuity(frames)
 def test_invalid_actor_slot_rejected(self):
  with self.assertRaisesRegex(ValueError,'actor slot'):actor_state(bytes(131072),1)
if __name__=='__main__':unittest.main()
