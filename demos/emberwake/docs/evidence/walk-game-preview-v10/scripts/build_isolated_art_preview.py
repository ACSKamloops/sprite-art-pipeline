#!/usr/bin/env python3
"""Copy a fresh Godot preview and replace only catalog-bound baked resources.

Run the bake verifier first. This helper never installs or publishes artwork.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bake', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    destination = args.out.resolve()
    assert not destination.exists(), 'A fresh preview directory is required'
    assert not destination.is_relative_to(source), 'Keep previews outside the source checkout'
    catalog = json.loads((source / 'assets/characters/catalog.json').read_text())
    replacements = []
    for actor in catalog['characters']:
        for kind, filename in [('atlas', 'atlas.png'), ('manifest', 'animations.json')]:
            resource = actor[kind]
            assert resource.startswith('res://')
            relative = Path(resource.removeprefix('res://'))
            original = (source / relative).resolve()
            assert original.is_relative_to(source) and relative.parts[0] == 'assets'
            baked = args.bake.resolve() / actor['id'] / filename
            assert original.is_file() and baked.is_file()
            replacements.append((actor['id'], relative, original, baked,
                                 sha(original), sha(baked)))
    # All bindings are checked before producing a partially useful project.
    assert len(replacements) == len(catalog['characters']) * 2
    destination.mkdir(parents=True)
    copied = {}
    for name in ['project.godot', 'export_presets.cfg']:
        shutil.copy2(source / name, destination / name)
        copied[name] = sha(source / name)
    for name in ['assets', 'scripts', 'scenes', 'tests']:
        shutil.copytree(source / name, destination / name,
                        ignore=shutil.ignore_patterns('__pycache__', '.godot'))
        for path in sorted((destination / name).rglob('*')):
            if path.is_file():
                relative = path.relative_to(destination)
                copied[relative.as_posix()] = sha(source / relative)
                assert sha(path) == copied[relative.as_posix()]
    rows = []
    for actor, relative, original, baked, before, expected in replacements:
        target = destination / relative
        shutil.copy2(baked, target)
        assert sha(target) == expected and sha(original) == before
        rows.append({'actor': actor, 'resource': relative.as_posix(),
                     'production_before_sha256': before, 'preview_sha256': expected,
                     'production_unchanged': True})
    for relative, expected in copied.items():
        assert sha(source / relative) == expected, 'Source changed during isolation'
    receipt = {'source_project': str(source), 'preview_project': str(destination),
               'config': str(args.config.resolve()), 'config_sha256': sha(args.config),
               'helper_sha256': sha(Path(__file__)), 'copied_source_hashes': copied,
               'resources': rows, 'production_assets_modified': False,
               'publication_performed': False,
               'scope': 'Isolated art preview only; no quality or runtime acceptance.'}
    (destination.parent / 'ISOLATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'Isolated {len(rows)} catalog resources; source remains unchanged: {destination}')


if __name__ == '__main__':
    main()
