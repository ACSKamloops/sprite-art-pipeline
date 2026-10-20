#!/usr/bin/env python3
"""Freeze an anonymous Emberwake walk comparison; no model calls.

Primary SE or NE and optional second NE paint are real inputs. Mirroring is opt-in for the
current symmetric unarmed costumes. Source identities stay outside input/ so
a cold reviewer receives only cels, clocks, context and hashes.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from fractions import Fraction
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'art-source/eight-direction-v1'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--actor', choices=['rowan', 'lyra', 'brann'], required=True)
    p.add_argument('--control-se', '--control-primary', type=Path, required=True,
                   help='Control bank for the declared primary view')
    p.add_argument('--trial-se', '--trial-primary', type=Path, required=True,
                   help='Trial bank for the declared primary view')
    p.add_argument('--primary-view', choices=['southeast', 'northeast'],
                   default='southeast')
    p.add_argument('--trial-spec', type=Path,
                   help='Optional JSON frames:[{file,hold:[numerator,denominator]}]')
    p.add_argument('--control-ne', type=Path)
    p.add_argument('--trial-ne', type=Path)
    p.add_argument('--mirror-symmetric', action='store_true')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if bool(a.control_ne) != bool(a.trial_ne):
        p.error('Supply both NE banks or neither')
    if a.control_ne and a.primary_view != 'southeast':
        p.error('The optional second NE bank requires primary southeast')
    if a.out.exists():
        p.error('A fresh output directory is required')
    sources = {'A': {a.primary_view: a.control_se.resolve()},
               'B': {a.primary_view: a.trial_se.resolve()}}
    exposures = {label: [{'file':f'{i:02}.png','hold':[9,160]} for i in range(8)]
                 for label in sources}
    if a.trial_spec:
        exposures['B'] = json.loads(a.trial_spec.read_text())['frames']
        if not exposures['B']:
            p.error('The trial must contain actual exposures')
        for entry in exposures['B']:
            pair = entry['hold']
            if len(pair) != 2 or any(type(n) is not int for n in pair):
                p.error('Hold values must be integer numerator/denominator pairs')
            if pair[0] <= 0 or pair[1] <= 0:
                p.error('All trial holds must be positive')
        if sum(Fraction(*entry['hold']) for entry in exposures['B']) != Fraction(9,20):
            p.error('The actual trial must preserve the .45 second cycle')
    if a.control_ne:
        sources['A']['northeast'] = a.control_ne.resolve()
        sources['B']['northeast'] = a.trial_ne.resolve()
    # Preflight before producing a partially valid packet.
    for label, views in sources.items():
        for folder in views.values():
            for entry in exposures[label]:
                path = (folder / entry['file']).resolve()
                if not path.is_relative_to(folder):
                    p.error('Exposure source must remain inside its bank')
                with Image.open(path) as im:
                    if im.size != (128, 128) or im.mode != 'RGBA':
                        p.error(f'Expected native 128x128 RGBA: {path}')
    target = a.out / 'input'
    target.mkdir(parents=True)
    record = {'actor': a.actor, 'stage': [128,128], 'pivot': [64,112],
              'game_scale': .66, 'holds': [[9,160]]*8, 'duration': [9,20],
              'variants': {}, 'context': [],
              'scope': 'Anonymous full walk variants. Cardinal imagery establishes identity and turn context only. No art or physical-contact certification is implied.'}
    if a.trial_spec:
        record['variant_holds'] = {'B':[entry['hold'] for entry in exposures['B']]}
    for label, views in sources.items():
        record['variants'][label] = {}
        for view, folder in views.items():
            outputs = [(view, False)]
            if a.mirror_symmetric:
                outputs.append(({'southeast':'southwest','northeast':'northwest'}[view], True))
            for name, mirrored in outputs:
                d = target / label / name
                d.mkdir(parents=True)
                entries = []
                for i, exposure in enumerate(exposures[label]):
                    source, destination = folder/exposure['file'], d/f'{i:02}.png'
                    if mirrored:
                        frame = Image.new('RGBA',(128,128))
                        frame.alpha_composite(ImageOps.mirror(Image.open(source)),(1,0))
                        frame.save(destination)
                    else:
                        shutil.copyfile(source,destination)
                        assert sha(source) == sha(destination)
                    entries.append({'path':destination.relative_to(target).as_posix(), 'sha256':sha(destination)})
                record['variants'][label][name] = entries
    context = target / 'context'
    context.mkdir()
    shutil.copyfile(BASE/'references'/f'{a.actor}-appearance.png',context/'appearance.png')
    baseline = BASE/'baseline'/a.actor
    manifest = json.loads((baseline/'animations.json').read_text())
    atlas, columns = Image.open(baseline/'atlas.png'), manifest['columns']
    cardinal_views = (['south','east','north','west'] if a.control_ne else
                      ['north','east','west'] if a.primary_view == 'northeast' else
                      ['south','east','west'])
    for view in cardinal_views:
        for action in ['walk','idle']:
            for i, frame in enumerate(manifest['animations'][view+'_'+action]['frames']):
                x,y = (frame%columns)*128,(frame//columns)*128
                atlas.crop((x,y,x+128,y+128)).save(context/f'{view}-{action}-{i:02}.png')
    for path in sorted(context.glob('*.png')):
        record['context'].append({'path':path.relative_to(target).as_posix(),'sha256':sha(path)})
    (target/'INPUTS.json').write_text(json.dumps(record,indent=2)+'\n')
    parent = {'script_sha256':sha(Path(__file__)), 'mirror_symmetric':a.mirror_symmetric,
              'primary_view':a.primary_view,
              'source_directories':{k:{v:str(s)for v,s in values.items()}for k,values in sources.items()},
              'source_exposures':exposures,
              'qualification':'Parent provenance only; do not supply this mapping to a blind reviewer.'}
    if a.trial_spec:
        parent['trial_spec'] = {'path':str(a.trial_spec.resolve()),'sha256':sha(a.trial_spec)}
    (a.out/'PARENT-ONLY-MAPPING.json').write_text(json.dumps(parent,indent=2)+'\n')
    print(f'{len(list(target.rglob("*.png")))} nominated images frozen at {target}')

if __name__ == '__main__':
    main()
