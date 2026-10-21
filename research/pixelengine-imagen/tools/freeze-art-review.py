#!/usr/bin/env python3
"""Freeze supplied manifests and reference into an anonymous art review packet."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    spec = json.loads(args.spec.read_text())
    out = args.output.absolute()
    if out.exists():
        raise ValueError('Fresh packet required')
    out.mkdir(parents=True)
    shutil.copy2(spec['appearance_reference'], out / 'appearance-reference.png')
    rows, pins = [], []
    for record in spec['clips']:
        name = record['id']
        if not name.isalnum():
            raise ValueError('Alphanumeric anonymous ID required')
        source = Path(record['manifest']).resolve()
        manifest = json.loads(source.read_text())
        if manifest['canvas'] != [80, 80] or manifest['duration'] != [1, 1] or len(manifest['frames']) != 8:
            raise ValueError('This packet is a fixed8x1/8second80px comparison')
        dest = out / 'clips' / name
        (dest / 'frames').mkdir(parents=True)
        frames = []
        for i, frame in enumerate(manifest['frames']):
            path = source.parent / frame['file']
            if frame['hold'] != [1, 8] or sha(path) != frame['sha256']:
                raise ValueError('Source timing or hash mismatch')
            target = dest / 'frames' / f'{i:04d}.png'
            shutil.copy2(path, target)
            frames.append({'file': f'clips/{name}/frames/{i:04d}.png', 'hold': [1, 8], 'sha256': sha(target)})
        shutil.copy2(source.parent / 'apng/animation.apng.png', dest / 'animation.png')
        simple = {'canvas': [80, 80], 'duration': [1, 1], 'loop': True,
                  'frames': [{**f, 'file': 'frames/' + Path(f['file']).name} for f in frames]}
        (dest / 'manifest.json').write_text(json.dumps(simple, indent=2) + '\n')
        rows.append({'id': name, 'title': name, 'note': record.get('role', 'Anonymous candidate'),
                     'frames': frames, 'manifest': f'clips/{name}/manifest.json', 'apng': f'clips/{name}/animation.png'})
        pins.append({'id': name, 'role': record.get('role', 'candidate'), 'frames': frames,
                     'apng_sha256': sha(dest / 'animation.png'), 'manifest_sha256': sha(dest / 'manifest.json')})
    report = {'appearance_reference_sha256': sha(out / 'appearance-reference.png'), 'clips': pins,
              'scope': 'Drawing, identity, primary/secondary motion and loop compared to supplied reference; score alpha/delivery separately from art.',
              'perception_limit': 'State actual motion perception limits. No target rating or producer/history supplied.'}
    report['input_fingerprint'] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    (out / 'INPUTS.json').write_text(json.dumps(report, indent=2) + '\n')
    loader = importlib.util.spec_from_file_location('review_page', Path(__file__).with_name('make-review.py'))
    ui = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(ui)
    payload = json.dumps({'clips': rows}, separators=(',', ':')).replace('<', '\\u003c')
    page = ui.PAGE.replace('DATA', payload, 1).replace('EXTRAS', '', 1)
    page = page.replace('PixelEngine baselines retain their opaque source mattes.', 'Reference is the comparison target. Judge artwork and motion separately from matte/alpha handling.')
    (out / 'index.html').write_text(page)
    montage = Image.new('RGB', (1280, 190 * len(rows)), (125, 125, 125))
    draw = ImageDraw.Draw(montage)
    for r, row in enumerate(rows):
        draw.text((4, 190 * r + 3), row['id'], fill='white')
        for i, frame in enumerate(row['frames']):
            im = Image.open(out / frame['file']).convert('RGBA').resize((160, 160), Image.Resampling.NEAREST)
            montage.paste(im, (160 * i, 190 * r + 22), im)
    montage.save(out / 'chronology.png')
    print(json.dumps({'packet': str(out), 'input_fingerprint': report['input_fingerprint']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
