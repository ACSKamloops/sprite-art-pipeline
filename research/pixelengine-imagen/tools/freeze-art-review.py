#!/usr/bin/env python3
"""Freeze supplied manifests and reference into an anonymous art review packet."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from fractions import Fraction
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
    rows, pins, boundaries = [], [], {Fraction(0)}
    for record in spec['clips']:
        name = record['id']
        if not name.isalnum():
            raise ValueError('Alphanumeric anonymous ID required')
        source = Path(record['manifest']).resolve()
        manifest = json.loads(source.read_text())
        if manifest['canvas'] != [80, 80] or manifest['duration'] != [1, 1] or not 2 <= len(manifest['frames']) <= 128:
            raise ValueError('This packet is a same-period1second80px comparison')
        dest = out / 'clips' / name
        (dest / 'frames').mkdir(parents=True)
        frames = []
        cursor = Fraction(0)
        for i, frame in enumerate(manifest['frames']):
            path = source.parent / frame['file']
            hold = Fraction(*frame['hold'])
            if hold <= 0 or sha(path) != frame['sha256']:
                raise ValueError('Source timing or hash mismatch')
            target = dest / 'frames' / f'{i:04d}.png'
            shutil.copy2(path, target)
            boundaries.add(cursor)
            cursor += hold
            frames.append({'file': f'clips/{name}/frames/{i:04d}.png', 'hold': frame['hold'], 'sha256': sha(target)})
        if cursor != 1:
            raise ValueError('Frame holds must sum to1second')
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
    starts = [float(t) for t in sorted(boundaries)]
    payload = json.dumps({'clips': rows, 'union_starts': starts}, separators=(',', ':')).replace('<', '\\u003c')
    page = ui.PAGE.replace('DATA', payload, 1).replace('EXTRAS', '', 1)
    # Reuse the existing cards/controls but index each lane by its own exact
    # holds. Stepping follows the union of all authored pose boundaries.
    first = page.index('function draw(t){')
    last = page.index('\nfunction tick()', first)
    draw = '''function laneIndex(row,t){let end=0;for(let i=0;i<row.frames.length;i++){end+=row.frames[i].hold[0]/row.frames[i].hold[1];if(t<end-1e-10)return i;}return row.frames.length-1;}
function draw(t){const phase=((t%1)+1)%1;current=0;for(let i=0;i<data.union_starts.length;i++)if(phase+1e-10>=data.union_starts[i])current=i;const scale=Number($('scale').value);const positions={};for(const card of cards){const index=laneIndex(card.row,phase);positions[card.row.id]=index;for(const [canvas,i] of [[card.c,index],[card.pcs[0],(index+card.images.length-1)%card.images.length],[card.pcs[1],index]]){canvas.style.width=(80*scale)+'px';canvas.style.height=(80*scale)+'px';const ctx=canvas.getContext('2d');ctx.clearRect(0,0,80,80);if(card.images[i])ctx.drawImage(card.images[i],0,0)}}$('seek').max=data.union_starts.length-1;$('seek').value=current;$('status').textContent=`${(phase*1000).toFixed(0)}ms/1000ms · boundary${current} · ${playing?'playing':'paused'}`;$('play').textContent=playing?'Pause':'Play';window.reviewState={ready,playing,current,time:t,speed,draws:++draws,cycles:Math.floor(t),positions};}'''
    page = page[:first] + draw + page[last:]
    old = 'function step(delta){pause();current=(current+delta+8)%8;elapsed=current/8;draw(elapsed)}'
    if old not in page:
        raise ValueError('Review template changed; update explicit clock binding')
    page = page.replace(old, 'function step(delta){pause();current=(current+delta+data.union_starts.length)%data.union_starts.length;elapsed=data.union_starts[current];draw(elapsed)}')
    page = page.replace('elapsed=f/8;draw(elapsed)', 'elapsed=data.union_starts[f];draw(elapsed)')
    page = page.replace('eight ordered poses, exact125ms per pose and a one-second cycle', 'ordered poses with original exact holds and a shared one-second cycle')
    page = page.replace('Pause or step to inspect every adjacent pair, including7→0.', 'Pause or step through the union of pose boundaries; each lane retains its own holds and wrap.')
    page = page.replace('PixelEngine baselines retain their opaque source mattes.', 'Reference is the comparison target. Judge artwork and motion separately from matte/alpha handling.')
    (out / 'index.html').write_text(page)
    montage = Image.new('RGB', (160 * max(len(r['frames']) for r in rows), 190 * len(rows)), (125, 125, 125))
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
