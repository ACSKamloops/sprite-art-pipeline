"""Compare actual RGBA samples, independently of PNG metadata and producer claims."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def compare(a, b):
    x = np.asarray(Image.open(a).convert('RGBA')).astype(np.int16)
    y = np.asarray(Image.open(b).convert('RGBA')).astype(np.int16)
    assert x.shape == y.shape
    error = np.abs(x - y)
    return {
        'a': a.name, 'b': b.name,
        'max_channel_error': int(error.max()),
        'different_pixels': int(np.any(error, axis=2).sum()),
        'RGBA_exact': bool(np.array_equal(x, y)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--repeat', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    pairs = [
        (args.repeat / 'gpu-0-source033.png', args.original / 'gpu-source033.png'),
        (args.repeat / 'gpu-1-source103.png', args.original / 'gpu-source103.png'),
        (args.repeat / 'gpu-2-source033.png', args.repeat / 'gpu-0-source033.png'),
    ]
    rows = [compare(a, b) for a, b in pairs]
    exact = all(row['RGBA_exact'] for row in rows)
    report = {'state': 'PASS_GPU_PIXEL_REPLAY' if exact else 'GPU_PIXEL_REPLAY_FAILED',
              'pairs': rows, 'gate': 'Exact RGBA, no tolerance exception'}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(report['state'])
    return 0 if exact else 1


if __name__ == '__main__':
    raise SystemExit(main())
