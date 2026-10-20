"""Offline test doubles only; never write simulated responses into the prepared run."""
import base64
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('palette_compare', HERE / 'compare_palette_construction.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PREPARED = Path('/home/astra/artifacts/pixellab-palette-construction-20261014')


class OfflineComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='palette-test-double-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['PLAN.json', 'ORIGINAL-HELPER-REPLAY.json']:
            shutil.copyfile(PREPARED / name, self.root / name)
        for case in json.loads((self.root / 'PLAN.json').read_text())['requests']:
            run = self.root / case['variant']
            run.mkdir()
            shutil.copyfile(PREPARED / case['variant'] / 'request.json', run / 'request.json')
            images = json.loads((run / 'request.json').read_text())['images']
            # A real1px strip test double. Source identity outputs test relation checks only.
            from PIL import Image
            import io
            data = io.BytesIO()
            Image.new('RGBA', (2, 1), (0, 0, 0, 255)).save(data, format='PNG')
            palette = {'base64': 'data:image/png;base64,' + base64.b64encode(data.getvalue()).decode()}
            (run / 'response.json').write_text(json.dumps({'images': images, 'palette': palette,
                'n_colors': 2, '_test_double': True}))

    def test_same_color_relations_and_alpha(self):
        result = MODULE.compare(self.root)
        self.assertTrue(all(result['comparisons'].values()))
        self.assertTrue(all(f['exact_alpha_preserved'] for r in result['cases'] for f in r['frames']))

    def test_request_tampering_rejected(self):
        run = self.root / 'joint-ab-4/request.json'
        run.write_text(run.read_text() + ' ')
        with self.assertRaisesRegex(ValueError, 'Frozen request changed'):
            MODULE.compare(self.root)

    def test_missing_second_frame_rejected(self):
        run = self.root / 'joint-ab-4/response.json'
        response = json.loads(run.read_text())
        response['images'].pop()
        run.write_text(json.dumps(response))
        with self.assertRaisesRegex(ValueError, 'both output frames'):
            MODULE.compare(self.root)

    def test_saved_output_mismatch_rejected(self):
        (self.root / 'joint-ab-4/output-00.png').write_bytes(b'not-the-response-image')
        with self.assertRaisesRegex(ValueError, 'Saved output differs'):
            MODULE.compare(self.root)


if __name__ == '__main__':
    unittest.main()
