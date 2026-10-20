#!/usr/bin/env python3
"""Build the frozen v0.6 source workflow wheel and prove its isolated install.

Run only after the runtime/UI/catalog freeze. Artifacts always use a new directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    checkout = Path(__file__).resolve().parents[3]
    package = checkout / 'sprite_workbench'
    changes = subprocess.check_output(['git', 'status', '--short', '--', 'sprite_workbench',
                                      'pyproject.toml', 'requirements-local.lock'], cwd=checkout, text=True)
    assert not changes, changes
    files = [{'file': p.relative_to(package).as_posix(), 'sha256': sha(p.read_bytes())}
             for p in sorted(package.rglob('*')) if p.is_file() and not p.is_symlink()
             and p.suffix in {'.py', '.json', '.js', '.cjs', '.css', '.html'} and '__pycache__' not in p.parts]
    baseline = json.loads((checkout/'docs/readiness/PACKAGE-SOURCE.json').read_text())
    assert len(baseline['runtime_files']) == 97
    names = {row['file'] for row in files}
    assert {row['file'] for row in baseline['runtime_files']} <= names
    required = {'source_vfx_runner.cjs', 'source_vfx.py', 'source_controls.py', 'source_workflow.py',
                'contracts/SOURCE-VFX-PRESETS.json', 'web/source-vfx.js', 'model_handoff.py', 'web/model-lab.js'}
    assert required <= names, required - names
    current = {row['file']: row['sha256'] for row in files}
    factories = [row for row in baseline['runtime_files'] if row['file'].startswith('vendor/vfx/')]
    assert factories and all(current[row['file']] == row['sha256'] for row in factories)
    expected = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, text=True).strip(),
                'checkout': str(checkout), 'source_fingerprint': sha(canonical(files)), 'runtime_files': files,
                'baseline_runtime_files': 97, 'unchanged_vendor_files': factories,
                'required_new_files': sorted(required), 'version': '0.6.0'}
    write(output/'SOURCE.json', expected)
    proof_dir = Path(__file__).resolve().parent
    for name in ['PACKAGE-proof.py', 'PACKAGE-runtime.py']:
        shutil.copyfile(proof_dir/name, output/name)
    for name in ['requirements-local.lock', 'requirements-local.in', 'pyproject.toml']:
        shutil.copyfile(checkout/name, output/name)
    commands = []

    def run(command):
        outcome = subprocess.run(command, cwd=output, capture_output=True, text=True)
        commands.append({'command': command, 'cwd': str(output), 'exit': outcome.returncode,
                         'stdout': outcome.stdout[-24000:], 'stderr': outcome.stderr[-24000:]})
        write(output/'COMMANDS.json', commands)
        if outcome.returncode:
            raise RuntimeError(json.dumps(commands[-1]))

    uv = shutil.which('uv')
    assert uv
    run([uv, 'build', '--wheel', '--no-build-isolation', '--python', sys.executable,
         '--out-dir', str(output/'wheel'), str(checkout)])
    wheel, = (output/'wheel').glob('*.whl')
    assert wheel.name == 'sprite_workbench-0.6.0-py3-none-any.whl'
    with zipfile.ZipFile(wheel) as archive:
        entries = [{'file': name, 'sha256': sha(archive.read(name)), 'bytes': len(archive.read(name))}
                   for name in archive.namelist() if not name.endswith('/')]
        for row in files:
            assert sha(archive.read('sprite_workbench/' + row['file'])) == row['sha256']
    write(output/'WHEEL-FILES.json', entries)
    run([uv, 'venv', '--python', sys.executable, str(output/'venv')])
    python = output/'venv/bin/python'
    run([uv, 'pip', 'install', '--python', str(python), '--require-hashes', '-r', str(output/'requirements-local.lock')])
    run([uv, 'pip', 'install', '--python', str(python), '--no-deps', str(wheel)])
    run([uv, 'pip', 'check', '--python', str(python)])
    run([str(python), '-I', str(output/'PACKAGE-runtime.py'), '--expected', str(output/'SOURCE.json'),
 '--output', str(output/'runtime')])
    result = json.loads((output/'runtime/RESULT.json').read_text())
    assert result['passed'] and result['source_fingerprint'] == expected['source_fingerprint']
    receipt = {'schema': 'installed-model-handoff-package-proof/v1', 'passed': True, **expected,
               'wheel': str(wheel), 'wheel_sha256': sha(wheel.read_bytes()), 'wheel_bytes': wheel.stat().st_size,
               'wheel_file_count': len(entries), 'requirements_lock_sha256': sha((output/'requirements-local.lock').read_bytes()),
               'uv_version': subprocess.check_output([uv, '--version'], text=True).strip(),
               'proof_scripts': [{'file': n, 'sha256': sha((output/n).read_bytes())}
                                 for n in ['PACKAGE-proof.py', 'PACKAGE-runtime.py']],
               'runtime': result, 'provider_calls': 0, 'artistic_acceptance': 'unreviewed'}
    write(output/'RECEIPT.json', receipt)
    print(json.dumps({'passed': True, 'receipt': str(output/'RECEIPT.json'),
                      'wheel_sha256': receipt['wheel_sha256'], 'runtime_files': len(files)}, indent=2))


if __name__ == '__main__':
    main()
