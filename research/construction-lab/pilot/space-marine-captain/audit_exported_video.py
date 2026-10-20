"""Compare decoded delivery video to its declared source clock and raster inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--decoded', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve earlier audits'
    receipt = json.loads(args.receipt.read_text())
    manifest = json.loads((args.candidate / 'manifest.json').read_text())
    assert receipt['video_sha256'] == sha(args.video)
    assert receipt['candidate_manifest_sha256'] == sha(args.candidate / 'manifest.json')
    files = sorted(args.decoded.glob('*.png'))
    assert len(files) == len(receipt['samples']) == 288
    frames = []
    for frame in manifest['frames']:
        path = args.candidate / frame['file']
        assert sha(path) == frame['sha256']
        frames.append(Image.open(path).convert('RGBA'))
    boundaries = np.cumsum([f['duration_ms'] for f in manifest['frames']])
    results = []
    for index, path in enumerate(files):
        sample = receipt['samples'][index]
        time = (index / 60 * 1000) % manifest['cycle_ms']
        expected_pose = int(np.searchsorted(boundaries, round(time, 6), side='right'))
        assert sample['source_pose'] == expected_pose
        zoom = 1 if index < 144 else 2
        expected = Image.new('RGBA', (512, 544), (38, 43, 49, 255))
        draw = ImageDraw.Draw(expected)
        draw.text((10, 10), 'Captain combat-ready walk | ' + ('Native 1x' if zoom == 1 else 'Nearest 2x'), fill='white')
        image = frames[expected_pose].resize((256 * zoom, 256 * zoom), Image.Resampling.NEAREST)
        expected.alpha_composite(image, (128, 160) if zoom == 1 else (0, 32))
        reference = np.asarray(expected.convert('RGB')).astype(np.int16)
        actual = np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
        assert actual.shape == reference.shape
        delta = np.abs(actual - reference)
        foreground = np.any(reference != [38, 43, 49], axis=2)
        # Encoding comparison only; no thresholds confer animation/art acceptance.
        results.append({'video_frame': index, 'time_ms': sample['time_ms'],
                        'source_pose': expected_pose, 'scale': zoom,
                        'mean_abs_RGB_error': float(delta.mean()),
                        'foreground_mean_abs_RGB_error': float(delta[foreground].mean()),
                        'decoded_sha256': sha(path)})
    cycles = []
    for start in [0, 72, 144, 216]:
        poses = [row['source_pose'] for row in results[start:start + 72]]
        cycles.append({'start_frame': start, 'distinct_presented_poses': len(set(poses)),
                       'omitted_poses': sorted(set(range(72)) - set(poses)),
                       'adjacent_repeated_poses': sum(a == b for a, b in zip(poses, poses[1:]))})
    report = {'schema': 'captain-decoded-video-audit/v1',
              'video_sha256': sha(args.video), 'manifest_sha256': sha(args.candidate / 'manifest.json'),
              'source_sampling_clock_verified': True, 'frames_compared': 288, 'cycles': cycles,
              'max_frame_mean_abs_RGB_error': max(row['mean_abs_RGB_error'] for row in results),
              'max_foreground_mean_abs_RGB_error': max(row['foreground_mean_abs_RGB_error'] for row in results),
              'frames': results,
              'limits': ['Decoded consecutive images are not continuous audiovisual ingestion',
                         'MP4 does not render root movement, floor or tested stance correction',
                         'Raster/timing agreement does not approve gait, anatomy or quality']}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['frames', 'cycles']}))


if __name__ == '__main__':
    main()
