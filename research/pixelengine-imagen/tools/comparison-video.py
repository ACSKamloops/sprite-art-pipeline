#!/usr/bin/env python3
"""Compose review lanes using the existing rational clock union and CFR verifier."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(args):
    packet, out = args.packet.resolve(), args.output.absolute()
    if out.exists() or not 1 <= args.loops <= 10:
        raise ValueError('Fresh output and1..10loops required')
    ledger = json.loads((packet / 'INPUTS.json').read_text())
    tracks = [(c.get('id', c.get('clip_id')), packet / 'clips' / c.get('id', c.get('clip_id')) / 'manifest.json') for c in ledger['clips']]
    union = module('review_union', REPO / 'skills/sprite-animation-pipeline/scripts/union_component_clocks.py')
    clock = union.schedule(tracks)
    if not 1 <= len(tracks) <= 6:
        raise ValueError('Bounded1..6comparison lanes')
    width, height = len(tracks) * 256, 312
    out.mkdir(parents=True)
    (out / 'source').mkdir()
    rows = []
    for i, state in enumerate(clock['states']):
        image = Image.new('RGBA', (width, height), (125, 125, 125, 255))
        draw = ImageDraw.Draw(image)
        for lane, (name, _) in enumerate(tracks):
            pos = state['components'][name]
            source = Path(clock['tracks'][name]['frames'][pos]['file'])
            frame = Image.open(source).convert('RGBA')
            if frame.size != (80, 80):
                raise ValueError('Native80px lane required')
            frame = frame.resize((240, 240), Image.Resampling.NEAREST)
            draw.text((256 * lane + 10, 12), name, fill='white')
            draw.text((256 * lane + 10, 29), f'Pose{pos} | t={state["start_tick"]}/{clock["clock_hz"]}s', fill='white')
            image.alpha_composite(frame, (256 * lane + 8, 58))
        path = out / 'source' / f'{i:04d}.png'
        image.save(path)
        rows.append({'file': path.name, 'hold': state['hold'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {'id': 'synchronized-comparison', 'canvas': [width, height], 'loop': False,
                'duration': [clock['duration'][0] * args.loops, clock['duration'][1]], 'frames': rows * args.loops}
    path = out / 'source/manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    (out / 'CLOCK.json').write_text(json.dumps(clock, indent=2) + '\n')
    encoder = module('review_cfr', REPO / 'skills/sprite-animation-pipeline/scripts/exact_cfr.py')
    receipt = encoder.encode(path, out / 'video', fps=clock['clock_hz'], scale=1)
    print(json.dumps({'video': str(out / 'video/preview-exact.mp4'), 'frames': receipt['frame_count'],
                      'duration': receipt['duration_rational'], 'actual_pts_exact': receipt['frame_PTS_and_duration_exact'],
                      'decoded_templates_correct': receipt['all_decoded_frames_classified_correctly_with_quality_bound']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--loops', type=int, default=5)
    run(p.parse_args())
