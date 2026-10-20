#!/usr/bin/env python3
"""Use the persistent local channel with an explicit supplied image.

Run using the workbench's Python. Creates a fresh output directory; the Store
and complete request/reply receipt stay there. Does not approve visual quality.
"""
import argparse
import json
from pathlib import Path
import select
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.image.resolve()
    output = args.output.absolute()
    if not source.is_file():
        raise SystemExit('Supply an existing PNG/APNG image')
    if output.exists() or output.is_symlink():
        raise SystemExit('Supply an absent output directory')
    output.mkdir(parents=True)
    records = []
    process = subprocess.Popen([sys.executable, '-m', 'sprite_workbench', '--workspace', str(output / 'store'),
        'channel', '--base-dir', str(source.parent), '--result-ref', 'source.sequence', '--workers', '2'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def receive():
        if not select.select([process.stdout], [], [], 40)[0]:
            raise RuntimeError('Local channel response timed out')
        line = process.stdout.readline()
        if not line:
            raise RuntimeError('Local channel closed unexpectedly')
        result = json.loads(line)
        records.append({'response': result})
        return result
    def call(method, params=None):
        request = {'id': len(records), 'method': method, 'params': params or {}}
        records.append({'request': request})
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        reply = receive()
        if reply.get('id') != request['id'] or reply.get('status') != 'completed':
            raise RuntimeError('Channel request failed: ' + json.dumps(reply))
        return reply['result']
    try:
        ready = receive()
        if ready.get('event') != 'ready':
            raise RuntimeError('No ready event')
        plan = {'version': 1, 'steps': [{'id': 'source', 'action': 'import', 'path': source.name}]}
        job_id = call('local.jobs.submit', {'handler': 'local.pipeline', 'request': {'plan': plan}})
        job = call('local.jobs.wait', {'job_id': job_id, 'timeout': 30})
        if job['status'] != 'completed' or job['result_status'] != 'candidate':
            raise RuntimeError('Returned job did not produce a candidate')
        candidate = call('local.library.create_candidate', {'artifact_id': job['artifact'], 'source_id': source.name})
        selected = call('local.library.select', {'candidate_ids': [candidate], 'source_ids': [source.name]})
        entity = call('local.library.promote', {'candidate_ids': selected, 'name': source.stem})
        saved = call('local.library.get', {'entity_id': entity})
        call('system.shutdown')
        _, stderr = process.communicate(timeout=10)
        if process.returncode:
            raise RuntimeError('Local channel exited unsuccessfully')
        (output / 'channel-stderr.txt').write_text(stderr)
        summary = {'status': 'completed', 'sequence': job['artifact'], 'candidate': candidate,
                   'entity': entity, 'revision': saved['revision_id'], 'workspace': str(output / 'store'),
                   'artistic_acceptance': 'unreviewed'}
        print(json.dumps(summary, indent=2))
        (output / 'RESULT.json').write_text(json.dumps(summary, indent=2) + '\n')
    finally:
        if process.poll() is None:
            process.terminate()
            process.communicate(timeout=10)
        (output / 'SESSION-RECEIPT.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    main()
