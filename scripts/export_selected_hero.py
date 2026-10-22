#!/usr/bin/env python3
"""Copy only the selected RPG character bindings into a fresh portable package."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def export(source, output):
    source, output = source.resolve(), output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('Output must be a fresh directory')
    library = json.loads((source / 'library.json').read_text())
    if library['schema'] != 'rpg-review-library/v1':
        raise ValueError('Unsupported library schema')
    selected = set(library['selected'].values())
    clips = [c for c in library['clips'] if c['id'] in selected]
    if len(clips) != len(selected) or library['reference'] not in selected:
        raise ValueError('Missing/duplicate selected clips or preferred reference')
    output.mkdir(parents=True)
    copied = {}
    for clip in clips:
        manifest = (source / clip['manifest']).resolve()
        if not manifest.is_relative_to(source) or sha(manifest) != clip['manifest_sha256']:
            raise ValueError('Escaping or changed manifest')
        destination = output / manifest.parent.relative_to(source)
        for path in manifest.parent.rglob('*'):
            if path.is_symlink():
                raise ValueError('Symlink in clip: ' + str(path))
        shutil.copytree(manifest.parent, destination)
        for path in manifest.parent.rglob('*'):
            if path.is_file():
                rel = path.relative_to(source)
                if sha(output / rel) != sha(path):
                    raise ValueError('Copy differs: ' + str(rel))
                copied[str(rel)] = sha(path)
    library['clips'] = clips
    write(output / 'library.json', library)
    shutil.copyfile(source / 'COVERAGE.json', output / 'COVERAGE.json')
    page = (source / 'index.html').read_text()
    page = page.replace('../play-v4/', '../README.md')
    page = page.replace('../godot-v4/bank.json', '../README.md#build-the-godot-inspector')
    page = page.replace('ASSEMBLY-RESULT.json', 'SNAPSHOT.json')
    page = page.replace('Playable controller', 'Build/play instructions')
    page = page.replace('Engine input bindings', 'Godot rebuild')
    page = page.replace('Baseline byte-preservation receipt', 'Snapshot receipt')
    (output / 'index.html').write_text(page)
    receipt = {
        'schema': 'selected-character-snapshot/v1',
        'source_library_sha256': sha(source / 'library.json'),
        'snapshot_library_sha256': sha(output / 'library.json'),
        'selected_bindings': len(library['selected']),
        'selected_clips': len(clips),
        'selected_exposures': sum(len(c['frames']) for c in clips),
        'omitted_unselected_clips': len(json.loads((source / 'library.json').read_text())['clips']) - len(clips),
        'copied_clip_files': len(copied),
        'all_copied_clip_files_byte_identical': True,
        'selected_ids_pixels_holds_events_loops_unchanged': True,
        'preferred_reference': library['reference'],
        'source_hash_verified_without_requiring_original_machine_path': True,
        'scope': 'Selected generated character art, editable sources and timing. No raw provider captures, credentials, game-ROM assets, engine binary or art approval.',
    }
    write(output / 'SNAPSHOT.json', receipt)
    write(output / 'FILESET.json', {
        str(p.relative_to(output)): sha(p)
        for p in sorted(output.rglob('*')) if p.is_file()
    })
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.source, args.output), indent=2))


if __name__ == '__main__':
    main()
