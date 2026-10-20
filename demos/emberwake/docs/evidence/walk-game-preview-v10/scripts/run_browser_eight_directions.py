#!/usr/bin/env python3
"""Run the existing CLI scenario and fail on its actual result, not CLI exit alone."""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', default='emberwake-eight-systems')
    parser.add_argument('--out', type=Path, default=ROOT / 'output/playwright/eight-directions-browser.json')
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cli = Path('/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh')
    command = [str(cli), '--session', args.session, '--raw', 'run-code',
               '--filename=' + str(ROOT / 'tests/browser_eight_directions.js')]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=180)
    args.out.with_suffix('.cli.log').write_text(result.stdout)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {'passed': False, 'error': 'CLI did not return a JSON scenario result',
                  'cli_exit_code': result.returncode}
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    successful = sum(item.get('ok') is True for item in report.get('receipts', []))
    incomplete = sum(item.get('ok') is None for item in report.get('receipts', []))
    failed = sum(item.get('ok') is False for item in report.get('receipts', []))
    passed = (result.returncode == 0 and report.get('passed') is True
              and incomplete == 0 and failed == 0)
    print(f"EIGHT_BROWSER {'PASS' if passed else 'FAIL'}: {successful} assertions; "
          f"{incomplete} incomplete asynchronous observations; {args.out}")
    if not passed:
        print(report.get('error', 'CLI, scenario, or observation completeness failed'), file=sys.stderr)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
