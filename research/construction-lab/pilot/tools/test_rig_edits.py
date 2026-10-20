import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import edit_rig_source as editor


class SourceEdits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / 'rigged-character'
        cls.design = (root / 'design.json').read_bytes()
        cls.clips = (root / 'clips.json').read_bytes()

    def change(self, source, path, value):
        document = json.loads(source)
        parent, key = editor.parent_at(document, path)
        return {'schema': 'rig-source-edit/v1', 'expected_sha256': hashlib.sha256(source).hexdigest(),
                'reason': 'Targeted reviewed parameter repair',
                'operations': [{'op': 'set', 'path': path, 'before': parent[key], 'value': value}]}

    def test_palette_edit_restores_exact_source_bytes(self):
        edit = self.change(self.design, ['palette', 'teal'], '217A83')
        changed, receipt = editor.apply(self.design, edit)
        self.assertEqual(editor.undo(changed, receipt), self.design)
        before, after = json.loads(self.design), json.loads(changed)
        before['palette']['teal'] = after['palette']['teal']
        self.assertEqual(before, after)
        self.assertIn('stale', receipt['downstream_status'])

    def test_pose_repair_changes_only_selected_key(self):
        path = ['clips', 'slash', 'tracks', 'pelvis', 2, 1, 0]
        changed, receipt = editor.apply(self.clips, self.change(self.clips, path, 109))
        self.assertEqual(json.loads(changed)['clips']['slash']['tracks']['pelvis'][2][1][0], 109)
        self.assertEqual(editor.undo(changed, receipt), self.clips)

    def test_invalid_later_operation_is_atomic(self):
        edit = self.change(self.design, ['palette', 'teal'], '217A83')
        edit['operations'].append({'op': 'set', 'path': ['dimensions', 'upper_arm'],
                                   'before': json.loads(self.design)['dimensions']['upper_arm'], 'value': -2})
        original = bytes(self.design)
        with self.assertRaises(ValueError):
            editor.apply(self.design, edit)
        self.assertEqual(self.design, original)

    def test_cannot_grant_art_approval_through_parameter_editor(self):
        with self.assertRaises(ValueError):
            editor.apply(self.design, self.change(self.design, ['quality_status'], 'approved'))

    def test_rejects_stale_edit_and_undo_over_newer_source(self):
        edit = self.change(self.design, ['palette', 'teal'], '217A83')
        changed, receipt = editor.apply(self.design, edit)
        with self.assertRaises(ValueError):
            editor.apply(changed, edit)
        with self.assertRaises(ValueError):
            editor.undo(changed + b' ', receipt)

    def test_rejects_reordered_key_and_nan_geometry(self):
        with self.assertRaises(ValueError):
            editor.apply(self.clips, self.change(self.clips, ['clips', 'slash', 'tracks', 'pelvis', 2, 0], 0.1))
        with self.assertRaises(ValueError):
            editor.apply(self.design, self.change(self.design, ['polygons', 'boot_outer', 0, 0], float('nan')))

    def test_rejects_engine_incompatible_parameter_shapes(self):
        for source, path, value in [
            (self.design, ['dimensions', 'upper_arm'], [22]),
            (self.design, ['dimensions', 'leg_widths'], []),
            (self.clips, ['clips', 'idle', 'defaults', 'front_foot'], 165),
            (self.clips, ['clips', 'slash', 'tracks', 'pelvis'], [[0, 1], [1, 2]])]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                editor.apply(source, self.change(source, path, value))

    def test_rejects_tampered_receipt(self):
        changed, receipt = editor.apply(self.design, self.change(self.design, ['palette', 'teal'], '217A83'))
        receipt = copy.deepcopy(receipt)
        receipt['edit']['operations'][0]['value'] = 'FFFFFF'
        with self.assertRaises(ValueError):
            editor.undo(changed, receipt)


if __name__ == '__main__':
    unittest.main()
