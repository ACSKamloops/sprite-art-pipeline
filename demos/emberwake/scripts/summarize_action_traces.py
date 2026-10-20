#!/usr/bin/env python3
"""Summarize a completed ordinary browser run without turning samples into ticks."""
from pathlib import Path
import argparse
import hashlib
import json
import statistics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    assert report['passed'] is True
    assert all(row['ok'] is True for row in report['receipts'])
    assert not report['consoleMessages'] and not report['pageErrors']
    expected = {(actor, view, action) for actor in ['rowan', 'lyra', 'brann']
                for view in ['northeast', 'southwest', 'southeast', 'northwest']
                for action in ['attack', 'cast']}
    traces = report['actionTraces']
    assert len(traces) == 24
    assert {(t['context']['id'], t['context']['view'], t['context']['pose'])
            for t in traces} == expected
    rows = []
    for trace in traces:
        assert trace['status'] == 'action_ended'
        samples = trace['samples']
        assert 2 <= len(samples) <= 96
        gaps = [b['snapshot']['physics_tick'] - a['snapshot']['physics_tick']
                for a, b in zip(samples, samples[1:])]
        observed = [b['observed_ms'] - a['observed_ms']
                    for a, b in zip(samples, samples[1:])]
        assert min(gaps) >= 0 and max(gaps) > 0 and min(observed) >= 0
        rows.append({'context': trace['context'], 'samples': len(samples),
                     'physics_tick_gap_max': max(gaps),
                     'physics_tick_gap_median': statistics.median(gaps),
                     'observer_ms_gap_median': statistics.median(observed),
                     'observer_ms_gap_max': max(observed),
                     'reported_fps_range': [min(s['snapshot']['fps'] for s in samples),
                                            max(s['snapshot']['fps'] for s in samples)]})
    result = {'source_report_sha256': hashlib.sha256(args.report.read_bytes()).hexdigest(),
              'successful_assertions': len(report['receipts']),
              'complete_action_traces': len(rows), 'rows': rows,
              'scope': 'Sampled observation coverage, not every physics tick, exact launch, '
                       'art acceptance or a baseline comparison of diagnostic overhead.'}
    assert not args.out.exists(), 'Preserve earlier observation summaries'
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(f'{len(rows)} complete action traces; {len(report["receipts"])} assertions')


if __name__ == '__main__':
    main()
