import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from transition_contract import load_contract
from verify_review import verify
ROOT=Path(__file__).resolve().parents[2]
class SupportedStateContract(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
  self.source=self.base/'controller.gd';self.source.write_text('# synthetic test controller\n')
  self.manifest=ROOT/'pilot/rigged-character/generated/manifest.json';self.m=json.loads(self.manifest.read_text())
  self.contract={'schema':'sprite.supported_state_review.v1','controller_source_bindings':{str(self.source):hashlib.sha256(self.source.read_bytes()).hexdigest()},'transitions':[{'id':'synthetic_idle_to_cast','kind':'supported_state_transition','before_clip':'idle/right','before_frame':0,'after_clip':'cast/right','after_frame':0,'before_state':'synthetic_ready','after_state':'synthetic_cast','before_equipment':'none','after_equipment':'none','policy':'Synthetic test policy, not real controller evidence','evidence':'Test only'}]}
  self.path=self.base/'contract.json'
 def tearDown(self):self.tmp.cleanup()
 def save(self):self.path.write_text(json.dumps(self.contract));return self.path
 def test_valid_explicit_contract(self):self.assertEqual(len(load_contract(self.save(),self.m)['transitions']),1)
 def test_missing_equipment_direction_does_not_alias(self):
  self.contract['transitions'][0]['before_clip']='idle_sword/front'
  with self.assertRaisesRegex(ValueError,'Missing action/equipment/direction'):load_contract(self.save(),self.m)
 def test_changed_controller_hash_fails(self):
  self.save();self.source.write_text('# changed controller\n')
  with self.assertRaisesRegex(ValueError,'Stale controller'):load_contract(self.path,self.m)
 def test_unstated_equipment_policy_fails(self):
  self.contract['transitions'][0]['before_equipment']=''
  with self.assertRaisesRegex(ValueError,'Missing explicit'):load_contract(self.save(),self.m)
 def test_default_clip_inspection_does_not_prove_supported_states(self):
  e=json.loads((ROOT/'qc/temporal/baseline-v3/pairs.json').read_text());r=json.loads((ROOT/'qc/temporal/baseline-review.json').read_text())
  self.assertIn('supported_state_contract_required',verify(e,r,self.manifest,require_supported_states=True))
 def test_claiming_contract_without_transition_comparison_fails(self):
  c=load_contract(self.save(),self.m)
  e=json.loads((ROOT/'qc/temporal/baseline-v3/pairs.json').read_text());r=json.loads((ROOT/'qc/temporal/baseline-review.json').read_text());e['state_contract']=c;r['state_contract_sha256']=c['sha256']
  self.assertIn('boundary_coverage_missing_or_extra',verify(e,r,self.manifest,self.path,True))
 def bound_positive(self):
  c=load_contract(self.save(),self.m)
  e=json.loads((ROOT/'qc/temporal/baseline-v3/pairs.json').read_text());r=json.loads((ROOT/'qc/temporal/baseline-review.json').read_text());e['state_contract']=c;r['state_contract_sha256']=c['sha256']
  row=c['transitions'][0];p={'id':max(x['id']for x in e['pairs'])+1,**{k:row[k]for k in ['kind','before_clip','before_frame','after_clip','after_frame']},'supported_state_contract':copy.deepcopy(row)}
  for side in ['before','after']:
   f=self.m['clips'][row[side+'_clip']]['frames'][row[side+'_frame']]
   p[side+'_pixel_sha256']=f['pixel_sha256'];p[side+'_file_sha256']=hashlib.sha256((self.manifest.parent/f['png']).read_bytes()).hexdigest()
  e['pairs'].append(p);r['visually_viewed_pair_ids'].append(p['id']);return e,r
 def test_explicit_hash_bound_state_comparison_passes_coverage_only(self):
  e,r=self.bound_positive();self.assertEqual(verify(e,r,self.manifest,self.path,True),[])
 def test_equipment_state_metadata_mutation_fails(self):
  e,r=self.bound_positive();e['pairs'][-1]['supported_state_contract']['after_equipment']='blaster'
  self.assertIn('supported_transition_metadata_missing_or_changed',verify(e,r,self.manifest,self.path,True))
if __name__=='__main__':unittest.main()
