#!/usr/bin/env python3
"""Build/install a hash-pinned wheel and run independent isolated HTTP proof."""
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


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    checkout = Path(__file__).resolve().parents[2]
    package = checkout/'sprite_workbench'
    files = [{'file': p.relative_to(package).as_posix(), 'sha256': sha(p.read_bytes())}
        for p in sorted(package.rglob('*')) if p.is_file() and not p.is_symlink()
        and p.suffix in {'.py', '.json', '.js', '.cjs', '.css', '.html'} and '__pycache__' not in p.parts]
    source_hash = sha(json.dumps(files, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())
    source_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, text=True).strip()
    runtime_changes = subprocess.check_output(['git', 'status', '--short', '--', 'sprite_workbench', 'pyproject.toml', 'requirements-local.lock'], cwd=checkout, text=True)
    assert not runtime_changes, runtime_changes
    expected = {'source_commit': source_commit, 'checkout': str(checkout), 'source_fingerprint': source_hash,
                'runtime_files': files}
    write(args.output/'SOURCE.json', expected)
    for name in ['PACKAGE-runtime.py', 'PACKAGE-proof.py']:
        shutil.copyfile(Path(__file__).resolve().parent/name, args.output/name)
    for name in ['requirements-local.lock', 'requirements-local.in', 'pyproject.toml']:
        shutil.copyfile(checkout/name, args.output/name)
    commands = []
    def run(command, cwd):
        outcome = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        record = {'command': command, 'cwd': str(cwd), 'exit': outcome.returncode,
                  'stdout': outcome.stdout[-24000:], 'stderr': outcome.stderr[-24000:]}
        commands.append(record)
        write(args.output/'COMMANDS.json', commands)
        if outcome.returncode:
            raise RuntimeError(json.dumps(record))
        return outcome
    uv = shutil.which('uv')
    assert uv
    run([uv, 'build', '--wheel', '--no-build-isolation', '--python', sys.executable,
         '--out-dir', str(args.output/'wheel'), str(checkout)], checkout)
    wheel, = list((args.output/'wheel').glob('*.whl'))
    assert wheel.name == 'sprite_workbench-0.4.0-py3-none-any.whl'
    wheel_hash = sha(wheel.read_bytes())
    run([uv, 'venv', '--python', sys.executable, str(args.output/'venv')], args.output)
    python = args.output/'venv/bin/python'
    run([uv, 'pip', 'install', '--python', str(python), '--require-hashes', '-r',
         str(args.output/'requirements-local.lock')], args.output)
    run([uv, 'pip', 'install', '--python', str(python), '--no-deps', str(wheel)], args.output)
    run([uv, 'pip', 'check', '--python', str(python)], args.output)
    with zipfile.ZipFile(wheel) as archive:
        entries = [{'file': name, 'sha256': sha(archive.read(name)), 'bytes': len(archive.read(name))}
                   for name in archive.namelist() if not name.endswith('/')]
    write(args.output/'WHEEL-FILES.json', entries)
    outcome = run([str(python), '-I', str(args.output/'PACKAGE-runtime.py'), '--expected',
                  str(args.output/'SOURCE.json'), '--output', str(args.output/'runtime')], args.output)
    result = json.loads((args.output/'runtime/RESULT.json').read_text())
    assert result['passed'] and result['source_fingerprint'] == source_hash
    lock = args.output/'requirements-local.lock'
    receipt = {'schema': 'installed-package-readiness-receipt/v1', 'passed': True,
        'source_commit': source_commit, 'source_fingerprint': source_hash,
        'wheel': str(wheel), 'wheel_sha256': wheel_hash, 'wheel_bytes': wheel.stat().st_size,
        'wheel_file_count': len(entries), 'requirements_lock_sha256': sha(lock.read_bytes()),
        'uv_version': subprocess.check_output([uv, '--version'], text=True).strip(),
        'proof_scripts': [{'file': name, 'sha256': sha((args.output/name).read_bytes())}
                          for name in ['PACKAGE-proof.py', 'PACKAGE-runtime.py']],
        'runtime': result, 'provider_calls': 0, 'artistic_acceptance': 'unreviewed'}
    write(args.output/'RECEIPT.json', receipt)
    print(json.dumps({'passed': True, 'receipt': str(args.output/'RECEIPT.json'),
        'wheel_sha256': wheel_hash, 'runtime_files': len(files), 'setup_ready': result['setup_ready'],
        'comparison_ready': result['comparison_ready']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
