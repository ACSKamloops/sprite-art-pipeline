#!/usr/bin/env python3
"""Verify actual external LibreSprite save/reopen without dumping large sidecars."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sprite_lab import project_hash, render_frame
from sprite_lab.aseprite import export_aseprite, import_aseprite
from sprite_lab.loading import load_project

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('project', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh directory; preserve earlier exchange proof')
    project = load_project(args.project.read_text())
    args.output.mkdir(parents=True)
    checks = []
    for animation in project['animations']:
        name = animation['id']
        ase = args.output / (name + '.aseprite')
        saved = args.output / (name + '-saved.aseprite')
        sidecar = args.output / (name + '.sprite-lab.json')
        export_aseprite(project, ase, name, sidecar)
        result = subprocess.run(['libresprite', '-b', str(ase), '--save-as', str(saved)], capture_output=True, text=True)
        (args.output / (name + '-tool.log')).write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('LibreSprite save failed: ' + name)
        imported = import_aseprite(saved, sidecar)
        pixels = all(render_frame(imported, frame).tobytes() == render_frame(project, frame).tobytes() for frame in animation['frames'])
        check = {'animation': name, 'full_project_sha_exact': project_hash(imported) == project_hash(project), 'rendered_rgba_exact': pixels, 'external_file_sha256': hashlib.sha256(saved.read_bytes()).hexdigest()}
        checks.append(check)
    passed = all(x['full_project_sha_exact'] and x['rendered_rgba_exact'] for x in checks)
    report = {'schema':'rig-external-editor-proof/v1', 'passed':passed, 'project_sha256':project_hash(project), 'checks':checks, 'scope':'Actual LibreSprite batch save and sidecar-backed import; exact layered project and selected rendered frames. No full motion/art acceptance.'}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed':passed, 'animations':len(checks), 'report':str(args.output / 'report.json')}))
    if not passed:
        raise SystemExit(2)
if __name__ == '__main__':
    main()
