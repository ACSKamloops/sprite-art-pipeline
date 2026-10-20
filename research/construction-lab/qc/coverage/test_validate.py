#!/usr/bin/env python3
import copy, json, unittest
from pathlib import Path
from validate import validate
BASE = Path(__file__).resolve().parent

class CoverageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((BASE / 'matrix.json').read_text())
        cls.contract = json.loads((BASE / 'requirements.json').read_text())

    def errors(self, m, gate):
        return validate(m, self.contract, gate)['issues']

    def test_exact_decoded_idle_walk_with_fresh_source_precondition(self):
        m = copy.deepcopy(self.matrix)
        m['source_audit']['catalog_consistency_passed'] = True
        self.assertTrue(validate(m, self.contract, 'decoded_idle_walk_exact_views')['passed'])

    def test_discovered_family_accounting_with_fresh_source_precondition(self):
        m = copy.deepcopy(self.matrix)
        m['source_audit']['catalog_consistency_passed'] = True
        self.assertTrue(validate(m, self.contract, 'discovered_family_accounting')['passed'])

    def test_actual_frozen_release_freshness_is_fail_closed(self):
        for gate in ['discovered_family_accounting','decoded_idle_walk_exact_views']:
            r = validate(self.matrix, self.contract, gate)
            self.assertEqual(r['passed'], self.matrix['source_audit']['catalog_consistency_passed'])
            if not r['passed']:
                self.assertTrue(any(i['code']=='source_audit_failed' for i in r['issues']))

    def test_missing_family_not_substituted_by_any_walk_asset(self):
        m = copy.deepcopy(self.matrix)
        m['families'] = [r for r in m['families'] if r['id'] != 'projectile_boomerang']
        e = self.errors(m, 'discovered_family_accounting')
        self.assertIn({'code': 'missing_family', 'detail': 'projectile_boomerang'}, e)

    def test_missing_direction_fails_exact_binding(self):
        m = copy.deepcopy(self.matrix)
        id = 'walk|randi|default_sword|left|normal'
        m['atoms'] = [a for a in m['atoms'] if a['id'] != id]
        self.assertIn({'code': 'missing_animation_binding', 'detail': id}, self.errors(m, 'decoded_idle_walk_exact_views'))

    def test_alias_or_right_view_never_substitutes_missing_left(self):
        m = copy.deepcopy(self.matrix)
        id = 'walk|randi|default_sword|left|normal'
        m['atoms'] = [a for a in m['atoms'] if a['id'] != id]
        next((a for a in m['atoms'] if a['id'] == 'walk|randi|default_sword|right|normal'))['alias'] = id
        e = self.errors(m, 'decoded_idle_walk_exact_views')
        self.assertTrue(any((x['code'] == 'alias_fallback_forbidden' for x in e)))
        self.assertIn({'code': 'missing_animation_binding', 'detail': id}, e)

    def test_duplicate_binding_rejects(self):
        m = copy.deepcopy(self.matrix)
        m['atoms'].append(copy.deepcopy(m['atoms'][0]))
        self.assertTrue(any((x['code'] == 'duplicate_binding' for x in self.errors(m, 'decoded_idle_walk_exact_views'))))

    def test_wrong_equipment_and_actor_dont_match_target(self):
        m = copy.deepcopy(self.matrix)
        a = m['atoms'][0]
        a['actor'] = 'authored_pilot'
        a['equipment'] = 'none'
        self.assertTrue(any((x['code'] == 'identity_mismatch' for x in self.errors(m, 'decoded_idle_walk_exact_views'))))

    def test_native_counts_dont_satisfy_new_art(self):
        e = self.errors(self.matrix, 'new_art_complete')
        gaps = [x for x in e if x['code'] == 'stage_incomplete']
        self.assertEqual(len(gaps), len(self.contract['production_atoms']))

    def test_claimed_approval_without_assets_or_review_rejects(self):
        m = copy.deepcopy(self.matrix)
        for a in m['atoms']:
            a['stages']['quality_approved'] = 'approved_production'
        e = self.errors(m, 'new_art_complete')
        self.assertTrue(any((x['code'] == 'approval_without_authored_assets' for x in e)))
        self.assertTrue(any((x['code'] == 'approval_without_current_review' for x in e)))

    def test_actual_changes_requested_receipt_cannot_be_relabelled_approved(self):
        m = copy.deepcopy(self.matrix)
        a = m['atoms'][0]
        a['stages']['quality_approved'] = 'approved_production'
        a['authored_asset_binding'] = {'project_evidence': 'authored_pilot', 'export_evidence': ['authored_contact_proof'], 'frame_ids': ['walk_00']}
        a['art_review_binding'] = {'decision': 'approved', 'evidence': 'authored_review', 'clip_ids': [a['id']], 'input_fingerprint': 'fake'}
        e = self.errors(m, 'new_art_complete')
        self.assertTrue(any((x['code'] == 'actual_review_does_not_approve_binding' for x in e)))
        self.assertTrue(any((x['code'] == 'approval_not_bound_to_current_asset' for x in e)))

    def test_sampled_gpu_bridge_rejects_changed_route_hash(self):
        from current_gpu_bridge import verify_bridge
        bridge_path = BASE/'current-gpu/bridge.json'
        bad = json.loads(bridge_path.read_text())
        bad['routes'][0]['route_sha256']='0'*64
        test_path = bridge_path.parent/'tampered-bridge.json'
        try:
            test_path.write_text(json.dumps(bad))
            ledger=self.matrix['source_ledger']
            result=verify_bridge(test_path,Path(ledger['native_player']['path']).parents[1],Path(ledger['native_gpu_audit']['path']))
            self.assertFalse(result['passed'])
        finally:
            test_path.unlink(missing_ok=True)

    def test_stale_source_is_detected(self):
        m = copy.deepcopy(self.matrix)
        m['source_ledger']['normal_catalog']['sha256'] = '0' * 64
        e = validate(m, self.contract, 'decoded_idle_walk_exact_views', True)['issues']
        self.assertTrue(any((x['code'] == 'stale_source_binding' for x in e)))
        self.assertTrue(any((x['code'] == 'input_fingerprint_mismatch' for x in e)))
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CoverageTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (BASE / 'test-report.json').write_text(json.dumps({'passed': result.wasSuccessful(), 'tests': result.testsRun, 'failures': [(str(t), s) for t, s in result.failures], 'errors': [(str(t), s) for t, s in result.errors]}, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
