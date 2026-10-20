#!/usr/bin/env python3
"""Run with the installed interpreter's -I flag from outside every checkout."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import sprite_workbench
from sprite_workbench import construction as construction
from sprite_workbench.core import Store
from sprite_workbench.jobs import TERMINAL
from sprite_workbench.readiness import source_fingerprint, REQUIRED_CHECKS
from sprite_workbench.web_server import ControlServer


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    expected = json.loads(args.expected.read_text())
    package = Path(sprite_workbench.__file__).resolve().parent
    assert sys.flags.isolated == 1
    assert not Path.cwd().resolve().is_relative_to(Path(expected['checkout']))
    assert not package.is_relative_to(Path(expected['checkout']))
    assert package.is_relative_to(Path(sys.prefix).resolve())
    assert importlib.metadata.version('sprite-workbench') == '0.4.0'
    assert source_fingerprint() == expected['source_fingerprint']
    installed_files = []
    for row in expected['runtime_files']:
        actual = (package/row['file']).read_bytes()
        assert sha(actual) == row['sha256']
        installed_files.append({'file': row['file'], 'sha256': sha(actual), 'bytes': len(actual)})
    write(args.output/'INSTALLED-FILES.json', installed_files)
    server = ControlServer(Store(args.output/'store'), base_dir=args.output/'files', port=0, workers=2)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def call(path, payload=None, *, token=None, want_json=True):
        headers = {}
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            headers['X-Workbench-Token'] = token if token is not None else server.token
        request = Request(server.url+path, data=None if payload is None else json.dumps(payload).encode(), headers=headers)
        try:
            response = urlopen(request, timeout=20)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read()
            return response.status, json.loads(raw) if want_json else raw, dict(response.headers)

    try:
        status, bootstrap, _ = call('/api/bootstrap')
        assert status == 200 and bootstrap['csrf_token'] == server.token
        # Session tokens remain in memory and are never written to proof files.
        assert bootstrap['readiness']['setup_ready'] is False
        assert bootstrap['readiness']['comparison_ready'] is False
        static = []
        for endpoint, relative in [('/', 'web/index.html'), ('/app.js', 'web/app.js'), ('/style.css', 'web/style.css')]:
            status, raw, headers = call(endpoint, want_json=False)
            assert status == 200 and raw == (package/relative).read_bytes()
            assert headers.get('X-Content-Type-Options') == 'nosniff'
            static.append({'endpoint': endpoint, 'file': relative, 'sha256': sha(raw), 'bytes': len(raw)})
        catalog = call('/api/catalog')[1]
        counts = {name: len(catalog[name]) for name in ['requirements', 'commands', 'flows', 'transport_flows', 'interfaces']}
        assert counts == {'requirements': 63, 'commands': 28, 'flows': 23, 'transport_flows': 30, 'interfaces': 213}
        assert len(catalog['grammar']['documented_primitives']) == 9
        assert len(catalog['grammar']['retained_grammar_claims']) == 42
        jobs_before = call('/api/jobs')[1]
        wrong_token = call('/api/verify', {}, token='independent-wrong-token')[0]
        assert wrong_token == 403 and call('/api/jobs')[1] == jobs_before
        comparison_status = call('/api/compare', {})[0]
        assert comparison_status == 409
        started = time.monotonic()
        status, submitted, _ = call('/api/verify', {})
        assert status == 200
        job_id = submitted['result']['job_id']
        deadline = time.monotonic()+180
        while time.monotonic() < deadline:
            job = next(j for j in call('/api/jobs')[1] if j['id'] == job_id)
            if job['status'] in TERMINAL:
                break
            time.sleep(0.1)
        else:
            raise AssertionError('Installed setup verification did not complete within180seconds')
        write(args.output/'HTTP-JOB.json', job)
        assert job['status'] == 'completed', job.get('error')
        assert len(job['outputs']) == 1 and job['outputs'][0]['result_status'] == 'technically_verified'
        report_id = job['outputs'][0]['artifact_id']
        report = call('/api/artifact/'+report_id)[1]
        write(args.output/'HTTP-SETUP-REPORT.json', report)
        assert report['status'] == 'completed'
        assert report['source_fingerprint'] == expected['source_fingerprint']
        assert {row['name'] for row in report['checks']} == REQUIRED_CHECKS
        assert all(row['passed'] is True for row in report['checks'])
        assert {row['flow'] for row in report['recipes']['flows']} == {f'F{i:02}' for i in range(1, 12)}
        assert all(row['status'] == 'completed' for row in report['recipes']['flows'])
        assert report['environment']['all_replay_dependencies_ready']
        assert report['provider_calls'] == 0 and report['artistic_acceptance'] == 'unreviewed'
        readiness = call('/api/readiness')[1]
        write(args.output/'HTTP-READINESS.json', readiness)
        assert readiness['setup_ready'] is True and readiness['comparison_ready'] is False
        assert readiness['restart_required'] is False and readiness['blockers']
        assert call('/api/compare', {})[0] == 409
        # An independent multi-edit portable closure covers intermediate v2
        # checkpoints, not only the setup check's initial/final single edit.
        from sprite_workbench.construction_services import invoke_construction
        from sprite_workbench.export import export_sequence, import_editable
        source = json.loads((package/'contracts/SETUP-CONSTRUCTION.json').read_text())
        state = construction.save_project(server.store, source)
        initial_id = state['project']
        state = construction.create_history(server.store, initial_id)
        for index in range(3):
            state = construction.edit_history(server.store, state['history'], {
                'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': state['project_hash'],
                'reason': 'installed package exact portable checkpoint '+str(index),
                'operations': [{'op': 'paint', 'cel_id': 'marker-a', 'points': [[index, 0, 3]]}]})
        assert server.store.get_json(state['history'])['version'] == 2
        rendered = invoke_construction(server.store, 'render', {'project': state['project'],
            'history': state['history'], 'animation_id': 'diagnostic'})
        export_sequence(server.store, rendered['sequence'], args.output/'three-edit-portable', ['editable'])
        fresh = Store(args.output/'three-edit-fresh-store')
        imported = import_editable(fresh, args.output/'three-edit-portable/editable')
        assert imported == rendered['sequence']
        construction.clear_history_proofs()
        assert construction.load_history(fresh, state['history'])['journal']['cursor'] == 3
        for _ in range(3):
            state = construction.move_history(fresh, state['history'], 'undo')
        assert state['project'] == initial_id
        editor = json.loads((Path(report['output'])/'EDITOR.json').read_text())
        assert editor['exit'] == 0
        result = {'schema': 'installed-readiness-proof/v1', 'passed': True,
            'python_isolated': sys.flags.isolated, 'python': sys.executable, 'cwd': str(Path.cwd()),
            'package': str(package), 'version': importlib.metadata.version('sprite-workbench'),
            'source_fingerprint': source_fingerprint(), 'runtime_file_count': len(installed_files),
            'static_assets': static, 'catalog_counts': counts, 'documented_primitives': 9, 'grammar_claims': 42,
            'wrong_token_http_status': wrong_token, 'comparison_http_status': comparison_status,
            'job_id': job_id, 'job_status': job['status'], 'verification_artifact': report_id,
            'required_checks': len(REQUIRED_CHECKS), 'local_recipe_count': 11,
            'setup_ready': readiness['setup_ready'], 'comparison_ready': readiness['comparison_ready'],
            'remaining_blockers': len(readiness['blockers']), 'native_editor_exit': editor['exit'],
            'three_edit_v2_closure': 'fresh Store cold replay, three exact undos matched initial project',
            'elapsed_seconds': time.monotonic()-started, 'provider_calls': 0, 'artistic_acceptance': 'unreviewed'}
        write(args.output/'RESULT.json', result)
        print(json.dumps(result, separators=(',', ':')))
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
