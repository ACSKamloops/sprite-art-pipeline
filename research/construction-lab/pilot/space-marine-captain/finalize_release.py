"""Append delivery evidence while preserving the exact ledger tested by Godot."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--integration', type=Path, required=True)
    parser.add_argument('--browser', type=Path, required=True)
    args = parser.parse_args()
    release = args.release.resolve()
    root = Path(__file__).resolve().parents[2]
    report = json.loads(args.integration.read_text())
    ledger_file = release / 'release-files.json'
    ledger = json.loads(ledger_file.read_text())
    assert report['passed'] and not report['failures']
    assert report['release_ledger_sha256'] == sha(ledger_file)
    assert report['candidate_manifest_sha256'] == sha(release / 'sprites/manifest.json')
    assert report['preview_sha256'] == sha(release / 'preview.gd')
    assert report['clock_sha256'] == sha(release / 'hold_clock.gd')
    assert all(sha(release / path) == digest for path, digest in ledger['files'].items())
    proof = release / 'proofs'
    assert not (proof / 'tested-source-ledger.json').exists(), 'Already finalized; retain original ledger'
    shutil.copy2(ledger_file, proof / 'tested-source-ledger.json')
    copies = {
        'release-integration.json': args.integration,
        'release-summary.json': root / 'pilot/captain72-godot/proof/release-v2-integration-summary.json',
        'release-first-import-failure.json': root / 'pilot/captain72-godot/proof/release-v1-failed-import-summary.json',
        'final-browser.json': args.browser,
    }
    for name, source in copies.items():
        shutil.copy2(source, proof / name)
    notes = release / 'notes'
    notes.mkdir(exist_ok=True)
    for skill, reference in [('sprite-construction-editing', 'detailed-humanoid-parts.md'),
                             ('sprite-animation-pipeline', 'held-pose-world-contact.md')]:
        shutil.copy2(root / 'skills' / skill / 'references' / reference, notes / reference)
    with (release / 'README.md').open('a') as stream:
        stream.write('\nFinal standalone delivery: **1043 checks, zero failures**. '
                     '`proofs/release-integration.json` binds the unchanged scene, imported frames and '
                     '`proofs/tested-source-ledger.json`. The current content ledger adds reports/notes only; '
                     'all originally tested files except this explanatory README remain byte-identical. '
                     '`proofs/final-browser.json` records 361 separate checks of the delivered browser player. '
                     'Reusable construction/contact/import lessons are copied into `notes/`; installed '
                     'skills live in `/home/astra/.codex/skills/`.\n')
    unchanged = {path: digest for path, digest in ledger['files'].items() if path != 'README.md'}
    assert all(sha(release / path) == digest for path, digest in unchanged.items())
    final = {
        'schema': 'captain-delivery-evidence-extension/v1',
        'tested_ledger_sha256': report['release_ledger_sha256'],
        'integration_report_sha256': sha(args.integration),
        'unchanged_tested_files': len(unchanged),
        'only_changed_preexisting_file': 'README.md',
        'finalizer_sha256': sha(Path(__file__)),
        'scope': 'Evidence/document extension; no sprite, timing, resource, scene or import changes',
    }
    (proof / 'finalization.json').write_text(json.dumps(final, indent=2) + '\n')
    files = {str(path.relative_to(release)): sha(path) for path in sorted(release.rglob('*'))
             if path.is_file() and '.godot' not in path.relative_to(release).parts
             and path != ledger_file}
    ledger_file.write_text(json.dumps({'approval_sha256': sha(release / 'approval.json'),
                                      'files': files}, indent=2) + '\n')
    assert all(sha(release / path) == digest for path, digest in files.items())
    print(json.dumps({'release': str(release), 'files_verified': len(files),
                      'unchanged_tested_files': len(unchanged), 'integration_passed': True}))


if __name__ == '__main__':
    main()
