import json,unittest,hashlib
from pathlib import Path
from .analyse import image,HERE
class DensePilotProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=json.loads((HERE/'comparison-report.json').read_text());cls.raw=json.loads((HERE/'gpu-observations.json').read_text())
    def test_actual_capture_completeness_and_model_slots(self):
        self.assertEqual(len(self.raw['dense']),60);self.assertEqual(len(self.raw['world']),903)
        for mode in ['old_12_hold5','dense_60_hold1','continuous_rig']:
            rows=[r for r in self.raw['world']if r['mode']==mode];self.assertEqual(len(rows),301);self.assertEqual(rows[-1]['tick'],60);self.assertEqual(rows[-1]['phase'],0)
    def test_dense_does_not_claim_quality_or_loosen_rule(self):
        self.assertFalse(self.report['art_quality_approved']);self.assertEqual(self.report['status'],'changes_requested');models={m['mode']:m for m in self.report['models']}
        for mode,maximum,passed in [('old_12_hold5',4,False),('dense_60_hold1',1,False),('continuous_rig',0,True)]:
            for side in models[mode]['actual_gpu']:
                self.assertEqual(side['actual_gpu_max_within_hold_world_range_px'],maximum);self.assertEqual(side['unchanged_slip_limit_px'],.5);self.assertIs(side['actual_gpu_within_hold_rule_satisfied'],passed);self.assertEqual(side['ground_rows'],[139])
    def test_source_identity_composition_and_project_bound(self):
        self.assertLessEqual((HERE/'project.json').stat().st_size,25_000_000);self.assertTrue(self.report['construction']['source_colors_preserved']);self.assertTrue(self.report['construction']['actual_gpu_composite_equality']);self.assertEqual(self.report['construction']['baseline_phase_composite_mismatches'],[])
        for key,path in [('dense_project_sha256','project.json'),('gpu_observations_sha256','gpu-observations.json'),('rig_sha256','cutout_rig.gd'),('capture_script_sha256','render_dense.gd'),('analysis_script_sha256','analyse.py')]:self.assertEqual(self.report['inputs'][key],hashlib.sha256((HERE/path).read_bytes()).hexdigest())
    def test_native_readback_hash_rejects_wrong_claim(self):
        ref=self.raw['dense'][0]['composite'];self.assertEqual(image(ref).size,(128,160));bad={**ref,'rgba_sha256':'0'*64}
        with self.assertRaises(AssertionError):image(bad)
if __name__=='__main__':unittest.main()
