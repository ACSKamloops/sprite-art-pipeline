"""Inspect actual GPU snapshots; contact sheets are evidence, never art approval."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('folder')
args = parser.parse_args()
source = Path(__file__).resolve().parent
output = (source / args.folder).resolve()
if not output.is_relative_to(source):
    parser.error('Output must remain within the V2 source folder')
samples = json.loads((output / 'samples.json').read_text())
clips = json.loads((source / 'clips.json').read_text())['clips']
baseline = json.loads((source.parent / 'rigged-character' / 'clips.json').read_text())['clips']
checks = []
views = ['right', 'left', 'front', 'back']
for clip, spec in clips.items():
    sheet = Image.new('RGB', (1536, 848), (40, 43, 48))
    draw = ImageDraw.Draw(sheet)
    for row, view in enumerate(views):
        frames = []
        for index in range(8):
            path = output / f'{clip}-{view}-{index}.png'
            image = Image.open(path).convert('RGBA')
            sheet.paste(image, (192 * index, 212 * row + 20), image)
            draw.text((192 * index + 4, 212 * row + 3), f'{view} {index}', fill='white')
            bounds = image.getbbox()
            passes = bounds is not None and bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 192 and bounds[3] < 192
            checks.append({'kind': 'canvas_bounds', 'file': path.name, 'bbox': bounds, 'pass': passes})
            background = Image.new('RGBA', image.size, (40, 43, 48, 255))
            background.alpha_composite(image)
            frames.append(background.convert('RGB').resize((384, 384), Image.Resampling.NEAREST))
        intervals = 8 if spec['loop'] else 7
        duration = round(1000 * spec['duration_ticks'] / 60 / intervals)
        durations = [duration] * 8
        if not spec['loop']:
            durations[-1] = 1000 // 60
        frames[0].save(output / f'{clip}-{view}-sampled-2x.gif', save_all=True, append_images=frames[1:], duration=durations, loop=0)
    sheet.save(output / f'{clip}-four-view.png')
    checks.append({'kind': 'clock_preservation', 'clip': clip, 'pass': all(spec[key] == baseline[clip][key] for key in ['duration_ticks', 'loop', 'events'])})

def identical(first, second):
    return Image.open(output / first).convert('RGBA').tobytes() == Image.open(output / second).convert('RGBA').tobytes()

for view in views:
    pairs = [
        (f'knockdown-{view}-7.png', f'recover-{view}-0.png', 'fallen_rest_closure'),
        (f'knockdown-{view}-0.png', f'idle-{view}-0.png', 'fall_neutral_start'),
        (f'recover-{view}-7.png', f'idle-{view}-0.png', 'recovery_neutral_end'),
    ]
    for first, second, name in pairs:
        checks.append({'kind': name, 'view': view, 'pass': identical(first, second)})
for sample in samples:
    checks.append({'kind': 'sample_reach', 'file': sample['file'], 'pass': max(sample['pose']['ik_target_error_px'].values()) < 0.001})
report = {
    'schema': 'copper-scout-v2-candidate-review/v1',
    'status': 'pending_temporal_art_review',
    'source_sha256': {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in ['rig.gd', 'rig_side.gd', 'design.json', 'clips.json', 'render_candidate.gd']},
    'gpu': 'Godot4.7.2 gl_compatibility Mesa26.0.3 llvmpipe LLVM21.1.8',
    'sample_count': len(samples),
    'checks': checks,
    'failed_checks': [check for check in checks if not check['pass']],
    'scope': '384 actual GPU phase snapshots. Sampled GIFs are incomplete per-tick playback. No artistic production approval; worker owns full playback and raster moving-world contact proof.',
}
(output / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'failed': report['failed_checks']}, indent=2))
