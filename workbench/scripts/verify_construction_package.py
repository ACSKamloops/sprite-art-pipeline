#!/usr/bin/env python3
"""Run a supplied construction example and real editor exchange from a package.

Use the isolated environment's Python with -I; --expected-prefix guards against
accidentally testing the checkout instead of the installed package.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--example', required=True)
    parser.add_argument('--expected-prefix', required=True)
    args = parser.parse_args()
    import sprite_workbench
    package = Path(sprite_workbench.__file__).resolve().parent
    if not package.is_relative_to(Path(args.expected_prefix).resolve()):
        raise SystemExit('Wrong imported package: ' + str(package))
    out = Path(args.output).absolute()
    if out.exists() or any(p.is_symlink() for p in [out, *out.parents]):
        raise SystemExit('Use an absent output directory without symlink parents')
    out.mkdir(parents=True)
    report = {'package': str(package), 'python': sys.executable, 'checks': [],
              'provider_calls': 0, 'visual_acceptance': 'unreviewed',
              'continuous_motion_viewed': False}
    def check(name, value):
        report['checks'].append({'name': name, 'passed': bool(value)})
        if not value:
            raise RuntimeError(name)
    def write(path, value):
        path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    try:
        from sprite_workbench.core import Store
        from sprite_workbench.pipeline import execute_plan
        from sprite_workbench.construction import load_project, load_history
        from sprite_workbench.construction_services import invoke_construction
        from sprite_workbench.export import export_sequence, import_editable
        files = [{'file': str(p.relative_to(package)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in sorted(package.rglob('*')) if p.is_file() and p.suffix in {'.py', '.json', '.js', '.cjs'}]
        write(out / 'PACKAGE-FILES.json', files)
        example = out / 'example'
        shutil.copytree(args.example, example)
        store = Store(out / 'store')
        run = execute_plan(store, json.loads((example / 'plan.json').read_text()), base_dir=example)
        write(out / 'PLAN.json', run)
        check('declared plan completed', run['status'] == 'completed')
        native = run['results']['native']
        editor = shutil.which('libresprite')
        check('native editor available', editor is not None)
        version = subprocess.run([editor, '--version'], capture_output=True, text=True, timeout=15)
        report['editor'] = {'path': editor, 'version': version.stdout.strip(),
                            'sha256': hashlib.sha256(Path(editor).read_bytes()).hexdigest()}
        command = [editor, '--batch', native['ase_path'], '--save-as', str(out / 'native-resaved.aseprite')]
        result = subprocess.run(command, capture_output=True, text=True, timeout=45)
        write(out / 'EDITOR.json', {'command': command, 'exit': result.returncode,
                                   'stdout': result.stdout, 'stderr': result.stderr})
        check('native file actually saved', result.returncode == 0 and (out / 'native-resaved.aseprite').is_file())
        imported = invoke_construction(store, 'ase_import', {
            'path': str(out / 'native-resaved.aseprite'), 'sidecar': native['sidecar_path']})
        write(out / 'IMPORT.json', imported)
        check('complete editable document equality', load_project(store, imported['project']) == load_project(store, native['project']))
        history = run['results']['edit']['history']
        rendered = invoke_construction(store, 'render', {'project': imported['project'], 'history': history,
            'animation_id': 'diagnostic', 'import_provenance': imported['import_provenance']})
        report['sequence'] = rendered['sequence']
        export_sequence(store, rendered['sequence'], out / 'portable', ['editable', 'apng', 'godot', 'review'])
        fresh = Store(out / 'fresh-store')
        check('fresh Store closure import', import_editable(fresh, out / 'portable/editable') == rendered['sequence'])
        check('fresh indexed document equality', load_project(fresh, imported['project']) == load_project(store, native['project']))
        check('fresh history replay', load_history(fresh, history)['project'] == imported['project'])
        from sprite_workbench.construction_exchange import validate_import_provenance
        check('fresh native audit dependencies', validate_import_provenance(fresh, imported['import_provenance'], project_id=imported['project'])['imported_project'] == imported['project'])
        report['status'] = 'completed'
    except Exception as exc:
        report.update(status='failed', error={'type': type(exc).__name__, 'message': str(exc)})
    write(out / 'REPORT.json', report)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'completed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
