#!/usr/bin/env python3
"""Verify prepared producer captures and REA/PNG bindings; no network or auth."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import probe_pixellab_prepared as probe


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return probe.strict_json(path.read_bytes())


def verify(phase_path, expected):
    require(sha(phase_path) == expected, 'Phase plan changed')
    phase = read(phase_path)
    rows, total, seen_slots = [], Decimal(0), set()
    for group in phase['plans']:
        plan_path = Path(group['path'])
        require(sha(plan_path) == group['sha256'], 'Subplan changed')
        endpoint, checked = probe.verify_plan(plan_path.parent, group['sha256'])
        variants = group['variants']
        require(isinstance(variants, list) and len(variants) == len(set(variants)), 'Duplicate phase variants')
        require(set(checked) == set(variants), 'Phase/subplan variant mismatch')
        for name in group['variants']:
            slot = checked[name]
            run, wire = slot['run'], slot['wire']
            require(run.resolve() not in seen_slots, 'Repeated resolved capture slot')
            seen_slots.add(run.resolve())
            state, lock = read(run / 'state.json'), read(run / '.submission.lock')
            require(state['status'] == 'completed' and state['http_status'] == 200, 'Incomplete slot')
            require(state['automatic_retry_allowed'] is False, 'Unexpected retry policy')
            require(state['plan_sha256'] == lock['plan_sha256'] == group['sha256'], 'Claim/plan mismatch')
            require(state['wire_sha256'] == lock['wire_sha256'] == probe.digest(wire), 'Claim/wire mismatch')
            har_path = run / 'network.har'
            entries = read(har_path)['log']['entries']
            require(len(entries) == 1, 'Expected exactly one producer record')
            entry = entries[0]
            req, response = entry['request'], entry['response']
            require(req['method'] == 'POST' and req['url'] == endpoint, 'Wrong producer route')
            require(req['postData']['text'].encode() == wire, 'Producer request differs from frozen wire')
            require(entry['_request_body_sha256'] == probe.digest(wire), 'Producer request hash mismatch')
            for packet in (req, response):
                require(packet['cookies'] == [], 'Unexpected retained cookies')
                require({h['name'].lower() for h in packet['headers']} <= {'content-type'}, 'Unexpected retained headers')
            content = response['content']
            require(response['status'] == 200 and not content['text_redacted'], 'Expected complete nonredacted result')
            require(entry['_response_body_sha256_scope'] == 'full', 'Prefix is not a complete response')
            raw_response = content['text'].encode()
            require(probe.digest(raw_response) == entry['_response_body_sha256_before_scrub'], 'Raw response binding failed')
            result = read(run / 'response.json')
            require(probe.strict_json(raw_response) == result, 'Saved response differs from producer body')
            pngs = probe.validate_result(endpoint, result, slot['dimensions'])
            for filename, raw in pngs.items():
                require((run / filename).read_bytes() == raw, 'Saved PNG differs from returned descriptor')
            rea_path = run / 'REA-EVIDENCE.json'
            rea = read(rea_path)
            require(rea['operation'] == 'inspect_web_network_capture', 'Wrong REA operation')
            require(rea['subject']['digest']['sha256'] == sha(har_path), 'REA subject hash differs')
            require(Path(rea['subject']['local_path']).resolve() == har_path.resolve(), 'REA subject path differs')
            norm = rea['normalized_result']
            require(norm['artifact']['sha256'] == sha(har_path), 'REA artifact hash differs')
            require(norm['total_records'] == 1 and [r['ordinal'] for r in norm['records']] == [0], 'REA record selection differs')
            observed = norm['records'][0]['reported']
            require(observed == entry, 'REA decoded record differs from producer record')
            usage = state['usage']
            require(usage == result['usage'] and usage['type'] == 'generations', 'Unrecognized reported usage')
            total += Decimal(str(usage['generations']))
            files = ['request.json', '.submission.lock', 'state.json', 'network.har', 'response.json', 'REA-EVIDENCE.json', *pngs]
            rows.append({'variant': name, 'endpoint': endpoint, 'rea_evidence_id': rea['evidence_id'],
                         'generations_reported': usage['generations'], 'output_png_count': len(pngs),
                         'files': [{'path': str(run / f), 'sha256': sha(run / f)} for f in files]})
    require(len(rows) <= phase['max_new_post_attempts'], 'Phase attempt budget exceeded')
    require(total <= Decimal(str(phase['max_reported_generations_before_manual_audit'])), 'Phase usage budget exceeded')
    return {'classification': 'producer-and-REA-binding-verification-not-private-algorithm-proof',
            'phase_path': str(phase_path), 'phase_sha256': expected, 'cases_checked': len(rows),
            'reported_generations': str(total), 'pngs_bound': sum(r['output_png_count'] for r in rows),
            'no_provider_calls': True, 'failures': [], 'cases': rows,
            'limits': ['HAR records actual urllib traffic, not a browser debugger trace.',
                       'REA independently decodes retained HAR; it does not attest vendor internals or original network authenticity.',
                       'Reported generations are response usage values, not an independent account balance reconciliation.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase_path', type=Path)
    parser.add_argument('--phase-sha', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = verify(args.phase_path, args.phase_sha)
    with args.output.open('x') as file:
        file.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('cases_checked', 'reported_generations', 'pngs_bound', 'failures')}))
