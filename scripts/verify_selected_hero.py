#!/usr/bin/env python3
"""Verify the bundled character snapshot without a model or original workspace."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(package):
    package = package.resolve()
    files = json.loads((package / 'FILESET.json').read_text())
    actual = {str(p.relative_to(package)) for p in package.rglob('*')
              if p.is_file() and p != package / 'FILESET.json' and '__pycache__' not in p.parts}
    if actual != set(files):
        raise ValueError('Snapshot file membership changed')
    for name, expected in files.items():
        path = (package / name).resolve()
        if not path.is_relative_to(package) or sha(path) != expected:
            raise ValueError('Snapshot file changed: ' + name)
    library = json.loads((package / 'library.json').read_text())
    snapshot = json.loads((package / 'SNAPSHOT.json').read_text())
    if sha(package / 'library.json') != snapshot['snapshot_library_sha256']:
        raise ValueError('Library receipt mismatch')
    clips = {c['id']: c for c in library['clips']}
    expected = {a + '_' + d for a in library['actions'] for d in library['directions']}
    if set(library['selected']) != expected or set(clips) != set(library['selected'].values()):
        raise ValueError('Incomplete selected direction/action matrix')
    frames = 0
    for key, clip_id in library['selected'].items():
        clip = clips[clip_id]
        manifest = package / clip['manifest']
        if sha(manifest) != clip['manifest_sha256']:
            raise ValueError('Manifest changed: ' + key)
        data = json.loads(manifest.read_text())
        if len(data['frames']) != len(clip['frames']):
            raise ValueError('Frame count differs: ' + key)
        for native, frame in zip(data['frames'], clip['frames']):
            path = package / frame['file']
            if path.resolve() != (manifest.parent / native['file']).resolve():
                raise ValueError('Frame path differs: ' + key)
            with Image.open(path) as image:
                rgba = image.convert('RGBA')
                if rgba.size != tuple(library['canvas']):
                    raise ValueError('Canvas differs: ' + key)
                if hashlib.sha256(rgba.tobytes()).hexdigest() != frame['rgba_sha256']:
                    raise ValueError('Decoded RGBA differs: ' + key)
            if frame['hold'] != native['hold'] or Fraction(*frame['hold']) <= 0:
                raise ValueError('Timing differs: ' + key)
            frames += 1
        if sum((Fraction(*f['hold']) for f in clip['frames']), Fraction()) != Fraction(*clip['duration']):
            raise ValueError('Clip duration differs: ' + key)
    if library['selected']['walk_SE'] != library['reference']:
        raise ValueError('Preferred walk changed')
    return {'selected_bindings': len(library['selected']), 'exposures': frames,
            'files_checked': len(files), 'all_files_and_selected_RGBA_exact': True,
            'scope': 'Distribution/source/timing integrity, not visual quality or engine behavior.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1] / 'examples/current-hero/package')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = verify(args.package)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
