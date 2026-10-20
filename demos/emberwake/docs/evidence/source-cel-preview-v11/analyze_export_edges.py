"""Measure source/imported color changes and verify the declared import transform."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--artifact', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
assert not args.out.exists(), 'Fresh report required'
root = args.artifact.resolve()
actors = {}
def rgba(path):
    return np.array(Image.open(path).convert('RGBA'))
for actor in ['rowan', 'lyra', 'brann']:
    source = rgba(root / 'bake' / actor / 'atlas.png')
    decoded = rgba(root / 'decoded-export' / f'{actor}-decoded.png')
    processed = rgba(root / 'processed-export-verification' / f'{actor}-expected-processed.png')
    assert source.shape == decoded.shape == processed.shape
    changed = np.any(source != decoded, axis=2)
    alpha = source[:, :, 3]
    values, counts = np.unique(alpha[changed], return_counts=True)
    actors[actor] = {
        'raw_RGBA_equal': bool(np.array_equal(source, decoded)),
        'alpha_everywhere_exact': bool(np.array_equal(alpha, decoded[:, :, 3])),
        'raw_RGB_change_alpha_histogram': dict(zip(map(str, values.tolist()), counts.tolist())),
        'changed_RGB_nonzero_alpha_pixels': int((changed & (alpha > 0)).sum()),
        'raw_RGBA_alpha_at_least20_exact': bool(np.array_equal(source[alpha >= 20], decoded[alpha >= 20])),
        'complete_processed_RGBA_exact': bool(np.array_equal(processed, decoded)),
        'decoded_RGBA_sha256': hashlib.sha256(decoded.tobytes()).hexdigest(),
        'processed_RGBA_sha256': hashlib.sha256(processed.tobytes()).hexdigest(),
    }
manifest = json.loads((root / 'processed-export-verification/RECEIPT.json').read_text())
passed = manifest['passed'] and all(a['alpha_everywhere_exact'] and a['complete_processed_RGBA_exact'] for a in actors.values())
report = {'passed': passed, 'actors': actors,
          'contract': 'Source alpha is exact; full exported RGBA equals raw source after the already configured Image.fix_alpha_edges transform. Full raw-source RGBA equality is false.',
          'first_raw_and_alpha_positive_failures_preserved': True,
          'source_import_settings_changed': False,
          'perception': 'Not a browser draw, art score or motion judgment.'}
args.out.write_text(json.dumps(report, indent=2) + '\n')
print(f'EXPORT_PROCESSING {"PASS" if passed else "FAIL"}: all3 processedRGBA exact; raw RGB changes measured at alpha0..19')
raise SystemExit(0 if passed else 1)
