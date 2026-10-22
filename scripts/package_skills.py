#!/usr/bin/env python3
"""Create a deterministic, self-contained ZIP of the four pipeline skills."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('reference-art-production', 'imagegen-sprite-animation',
         'sprite-construction-editing', 'sprite-animation-pipeline')

INSTALL = '''# Install or read the pipeline skills

This archive contains all four complete skill folders, the installer and a
SHA-256 file manifest. Keep the folders under skills/ as siblings.

From this extracted archive:

    python3 scripts/install_skills.py --destination "$HOME/.codex/skills"

The installer skips identical files and preserves differing existing skills.
Choose a fresh destination to compare an existing installation. Other AI clients
may read each SKILL.md directly or copy the folders to their supported location.
Read skills/INDEX.json, then load the relevant entrypoint and references as needed.

Python raster tools require Pillow/NumPy; new warp triangulations need SciPy.
Image generation, LibreSprite, Godot, Blender, codecs and licensed model inputs
are separate capabilities. The environment-provided OpenAI ImageGen tool/system
skill is not bundled. No credential is needed for installation or frozen offline
replay, and no provider generation is launched by these steps. H3 and local
generative models remain disabled for current production.

Full pipeline, current character and honest remaining quality gaps:
https://github.com/ACSKamloops/sprite-art-pipeline/blob/main/docs/AI-HANDOFF.md

The bundled examples do not establish whole-library 9/10 quality or recovered
private PixelLab/PixelEngine model parity. Preserve included upstream notices;
public access does not assign a blanket license to every item.
'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def package(output, allow_dirty=False):
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh archive path required')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    if dirty and not allow_dirty:
        raise ValueError('Commit/review source first, or explicitly use --allow-dirty for a test archive')
    payload = {}
    counts = {}
    for name in NAMES:
        skill = ROOT / 'skills' / name
        if not (skill / 'SKILL.md').is_file():
            raise ValueError('Missing skill: ' + name)
        counts[name] = 0
        for path in sorted(skill.rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlink in skill: ' + str(path))
            if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            payload[path.relative_to(ROOT).as_posix()] = path.read_bytes()
            counts[name] += 1
    for rel in ('scripts/install_skills.py', 'skills/INDEX.json'):
        payload[rel] = (ROOT / rel).read_bytes()
    payload['INSTALL.md'] = INSTALL.encode()
    manifest = {'schema': 'sprite-skill-bundle/v1', 'source_revision': revision,
                'source_worktree_dirty': dirty, 'skill_file_counts': counts,
                'files_sha256': {name: sha(raw) for name, raw in sorted(payload.items())},
                'scope': 'Four complete skill copies and installer; no engine/model binary, provider credential or whole-library art acceptance.'}
    payload['BUNDLE-MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
    with zipfile.ZipFile(output) as archive:
        if set(archive.namelist()) != set(payload):
            raise ValueError('Archive membership mismatch')
        for name, raw in payload.items():
            if archive.read(name) != raw:
                raise ValueError('Archive content mismatch: ' + name)
    return {'archive': str(output), 'sha256': sha(output.read_bytes()),
            'bytes': output.stat().st_size, 'files': len(payload),
            'source_revision': revision, 'source_worktree_dirty': dirty,
            'skill_file_counts': counts, 'all_archive_bytes_verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-dirty', action='store_true', help='Explicitly label an uncommitted test bundle')
    args = parser.parse_args()
    print(json.dumps(package(args.output, args.allow_dirty), indent=2))


if __name__ == '__main__':
    main()
