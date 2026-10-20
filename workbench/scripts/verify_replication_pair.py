#!/usr/bin/env python3
"""Compare independently executed checkout/wheel replays, preserving both inputs."""
import argparse
import json
from pathlib import Path

from sprite_workbench.core import ValidationError, digest
from sprite_workbench.replication import (FLOW_NAMES, compare_sequences, fresh_directory,
                                         verify_run, write_json)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    roots = [args.baseline.resolve(), args.candidate.resolve()]
    before = [verify_run(root) for root in roots]
    if any(item['status'] != 'completed' for item in before):
        raise ValidationError('Input replay integrity failed')
    runs = [json.loads((root / 'RUN.json').read_text()) for root in roots]
    specs = [json.loads((root / 'SPECIFICATION.json').read_text()) for root in roots]
    if any(run['status'] != 'completed' or run['selected_flows'] != list(FLOW_NAMES) for run in runs):
        raise ValidationError('Pair verification requires completed ordered all-eleven diagnostic runs')
    out = fresh_directory(args.output)
    comparisons = []
    for flow in FLOW_NAMES:
        receipts = [json.loads((root / (flow + '-RECEIPT.json')).read_text()) for root in roots]
        result = compare_sequences(roots[0] / 'stores' / flow, receipts[0]['artifacts']['sequence'],
                                   roots[1] / 'stores' / flow, receipts[1]['artifacts']['sequence'], out / flow)
        comparisons.append({'flow': flow, 'primary_sequence_exact': result['exact_sequence_match'],
                            'inputs_equal': receipts[0]['inputs'] == receipts[1]['inputs'],
                            'comparison': flow + '/COMPARISON.json'})
    after = [verify_run(root) for root in roots]
    package_equal = specs[0]['package_files'] == specs[1]['package_files']
    good = (package_equal and all(r['primary_sequence_exact'] and r['inputs_equal'] for r in comparisons)
            and all(item['status'] == 'completed' for item in after))
    result = {'kind': 'local-replication-pair-verification', 'status': 'completed' if good else 'failed',
              'package_source_hashes_equal': package_equal, 'flows': comparisons,
              'input_run_paths': [str(root) for root in roots], 'input_integrity_before': before,
              'input_integrity_after': after,
              'run_report_hashes': [digest((root / 'RUN.json').read_bytes()) for root in roots],
              'scope': 'All primary supplied diagnostic sequences and declared inputs; state UUIDs/timestamps and engine wall time are not expected to be byte-identical.',
              'artistic_acceptance': 'unreviewed', 'whole_vendor_replication_complete': False}
    write_json(out / 'PAIR-VERIFICATION.json', result)
    print(json.dumps({'status': result['status'], 'flows': len(comparisons),
                      'package_source_hashes_equal': package_equal,
                      'all_primary_sequences_exact': all(r['primary_sequence_exact'] for r in comparisons)}, indent=2))
    return 0 if good else 2


if __name__ == '__main__':
    raise SystemExit(main())
