"""Exercise frozen-input rejection and faithful script-boundary escaping."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audition', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    builder = Path(__file__).with_name('build_player.py')
    source_root = args.audition.parents[1]
    ledger = json.loads((args.audition / 'sha256-receipt.json').read_text())
    files = ledger['frozen_files_excluding_this_manifest']
    checks = []
    with tempfile.TemporaryDirectory(prefix='sprite-player-preflight-') as tmp:
        lab = Path(tmp) / 'lab'
        case = lab / 'artifacts' / args.audition.name
        case.mkdir(parents=True)
        for relative in files:
            target = lab / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            # These input links are read-only during the entire fixture.
            try:
                os.link(source_root / relative, target)
            except OSError:
                shutil.copy2(source_root / relative, target)
        for name in ['stale', 'unlisted-frame', 'unknown-schema', 'escaping']:
            data = json.loads(json.dumps(ledger))
            if name == 'stale':
                key = f'artifacts/{case.name}/baseline/frame-000.png'
                data['frozen_files_excluding_this_manifest'][key] = '0' * 64
            elif name == 'unlisted-frame':
                key = f'artifacts/{case.name}/front-values/frame-064.png'
                del data['frozen_files_excluding_this_manifest'][key]
            elif name == 'unknown-schema':
                data = {'unknown': {}}
            (case / 'sha256-receipt.json').write_text(json.dumps(data))
            output = Path(tmp) / name
            label = '</script><script>window.__unexpected=1</script>'
            description = '<fold & cloth>'
            run = subprocess.run(
                ['python3', str(builder), '--audition', str(case),
                 '--output', str(output), '--candidate', 'front-values',
                 '--candidate-label', label, '--description', description],
                capture_output=True, text=True)
            if name != 'escaping':
                assert run.returncode != 0 and not output.exists(), name
                checks.append({'case': name, 'rejected_before_output': True})
                continue
            assert run.returncode == 0, run.stderr
            html = (output / 'start-here.html').read_text()
            line = next(x for x in html.splitlines()
                        if x.startswith('const manifest='))
            embedded = line.split('const manifest=', 1)[1].split(', $=id', 1)[0]
            parsed = json.loads(embedded)
            assert parsed['description'] == description
            assert parsed['variants'][1]['label'] == label
            assert html.count('</script>') == 1
            assert '<' not in embedded
            checks.append({'case': name, 'script_boundary_safe': True,
                           'strings_roundtrip_exact': True})
    report = {'state': 'PASS_FROZEN_PREFLIGHT_AND_JSON_BOUNDARY_CONTROLS',
              'builder_sha256': hashlib.sha256(builder.read_bytes()).hexdigest(),
              'checks': checks,
              'scope': 'Frozen source rejection and generated HTML/JSON; '
                       'not a browser timing or art review'}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
