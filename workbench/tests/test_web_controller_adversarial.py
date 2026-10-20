"""Independent live-HTTP boundary and readiness-gate discriminators."""
import http.client
import json
from pathlib import Path
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
import pytest

from sprite_workbench.core import Store
from sprite_workbench import readiness as gates
from sprite_workbench import replication
from sprite_workbench.web_server import ControlServer, MAX_REQUEST


@pytest.fixture
def controller(tmp_path, monkeypatch):
    source = ['a'*64]
    monkeypatch.setattr(gates, 'source_fingerprint', lambda: source[0])
    server = ControlServer(Store(tmp_path/'store'), base_dir=tmp_path/'files', port=0, workers=1)
    server.test_source = source
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


def request(server, path, payload=None, headers=None, *, token=True, raw=False):
    headers = dict(headers or {})
    if payload is not None:
        headers.setdefault('Content-Type', 'application/json')
        if token:
            headers.setdefault('X-Workbench-Token', server.token)
        payload = payload if raw else json.dumps(payload).encode()
    req = Request(server.url+path, data=payload, headers=headers)
    try:
        with urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read())
    except HTTPError as response:
        return response.code, json.loads(response.read())


def invoke(server, method, params):
    return request(server, '/api/invoke', {'method': method, 'params': params})


@pytest.mark.parametrize('headers', [None, {'X-Workbench-Token': 'wrong'},
    {'Origin': 'null'}, {'Origin': 'http://127.0.0.1.attacker.invalid'},
    {'Host': '127.0.0.1.attacker.invalid:80'}, {'Host': 'attacker.invalid'}])
def test_rejected_http_envelopes_cannot_mutate(controller, headers):
    before = set((controller.store.path/'blobs').iterdir())
    status, _ = request(controller, '/api/plan', {'plan': {'version': 1, 'steps': []}},
                        headers=headers, token=headers is not None)
    assert status == 403
    assert set((controller.store.path/'blobs').iterdir()) == before


@pytest.mark.parametrize('headers', [
    {'Content-Length': str(MAX_REQUEST+1)},
    {'Content-Length': '-1'}, {'Content-Length': 'bad'},
    {'Content-Length': '2', 'Transfer-Encoding': 'chunked'}])
def test_bad_framing_rejects_before_buffering(controller, headers):
    headers = {**headers, 'Content-Type': 'application/json', 'X-Workbench-Token': controller.token}
    connection = http.client.HTTPConnection('127.0.0.1', controller.server_port, timeout=5)
    try:
        connection.request('POST', '/api/verify', body=b'{}', headers=headers)
        response = connection.getresponse()
        assert response.status == 400
        assert json.loads(response.read())['status'] == 'validation_error'
    finally:
        connection.close()


def fake_verification(monkeypatch):
    calls = []
    monkeypatch.setattr(replication, 'doctor', lambda: {'all_replay_dependencies_ready': True})
    monkeypatch.setattr(replication, 'replay', lambda _out: {'status': 'completed',
        'flows': [{'flow': f'F{i:02}', 'status': 'completed'} for i in range(1, 12)]})
    monkeypatch.setattr(replication, 'verify_run', lambda _out: {'status': 'completed'})
    def construction(_store, _out):
        calls.append('executed')
        names = gates.REQUIRED_CHECKS-{'all replay dependencies available', 'all eleven local recipe subsets',
            'recipe artifact integrity', 'source unchanged during verification'}
        return [{'name': name, 'passed': True} for name in names]
    monkeypatch.setattr(gates, '_construction_check', construction)
    return calls


@pytest.mark.parametrize('route', ['direct_submit', 'retry'])
def test_stale_source_cannot_verify_via_generic_job_routes(controller, monkeypatch, route):
    calls = fake_verification(monkeypatch)
    if route == 'retry':
        with controller.manager._condition:
            previous = controller.manager.submit(gates.HANDLER, {}, head=gates.LATEST_HEAD)
            assert controller.manager.cancel(previous)
    controller.test_source[0] = 'b'*64
    assert request(controller, '/api/readiness')[1]['restart_required']
    if route == 'direct_submit':
        status, payload = invoke(controller, 'local.jobs.submit', {'handler': gates.HANDLER,
            'request': {}, 'head': gates.LATEST_HEAD})
    else:
        status, payload = invoke(controller, 'local.jobs.retry', {'job_id': previous})
    if status == 200:
        result = payload['result']
        job_id = result if isinstance(result, str) else result['job_id']
        terminal = controller.manager.wait(job_id, timeout=5)
        assert terminal['status'] in {'validation_error', 'technical_failure', 'cancelled'}
    else:
        assert status in {400, 409}
    assert calls == []
    assert controller.store.get_head(gates.LATEST_HEAD) is None
    state = request(controller, '/api/readiness')[1]
    assert not state['setup_ready'] and not state['comparison_ready']


def test_retry_rechecks_frozen_pipeline_paths(controller, tmp_path):
    outside = tmp_path/'outside.png'
    from sprite_workbench.export import png_bytes
    outside.write_bytes(png_bytes(np.zeros((2, 2, 4), np.uint8)))
    plan = {'version': 1, 'steps': [{'id': 'outside', 'action': 'import', 'path': str(outside)}]}
    with controller.manager._condition:
        previous = controller.manager.submit('local.pipeline', {'plan': plan})
        assert controller.manager.cancel(previous)
    status, payload = invoke(controller, 'local.jobs.retry', {'job_id': previous})
    if status == 200:
        job_id = payload['result']
        terminal = controller.manager.wait(job_id, timeout=5)
        assert terminal['status'] in {'validation_error', 'technical_failure', 'cancelled'}
    else:
        assert status in {400, 409}


def test_resolved_plan_path_cannot_escape_project(controller, tmp_path):
    outside = tmp_path/'escaped-output.json'
    document = json.loads((Path(__file__).resolve().parents[1]/
        'sprite_workbench/contracts/SETUP-CONSTRUCTION.json').read_text())
    document['animations'][0]['id'] = str(outside)
    plan = {'version': 1, 'steps': [
        {'id': 'source', 'action': 'construction', 'method': 'save', 'request': {'document': document}},
        {'id': 'info', 'action': 'construction', 'method': 'get', 'request': {'project': {'ref': 'source.project'}}},
        {'id': 'write', 'action': 'construction', 'method': 'write', 'request': {
            'project': {'ref': 'source.project'}, 'path': {'ref': 'info.animation_ids.0'}}},
    ]}
    status, payload = invoke(controller, 'local.jobs.submit', {'handler': 'local.pipeline', 'request': {'plan': plan}})
    if status == 200:
        terminal = controller.manager.wait(payload['result'], timeout=5)
        assert terminal['status'] in {'validation_error', 'technical_failure', 'cancelled'}
    else:
        assert status in {400, 409}
    assert not outside.exists()


def test_symlink_input_and_output_paths_stay_in_project(controller, tmp_path):
    outside = tmp_path/'external'; outside.mkdir()
    (controller.base/'bridge').symlink_to(outside, target_is_directory=True)
    original = b'{"private":"sentinel"}'
    (outside/'source.json').write_bytes(original)
    assert invoke(controller, 'local.construction.read', {'path': 'bridge/source.json'})[0] == 400
    document = json.loads((Path(__file__).resolve().parents[1]/
        'sprite_workbench/contracts/SETUP-CONSTRUCTION.json').read_text())
    status, result = invoke(controller, 'local.construction.save', {'document': document})
    assert status == 200
    assert invoke(controller, 'local.construction.write', {'project': result['result']['project'],
        'path': 'bridge/output.json'})[0] == 400
    assert (outside/'source.json').read_bytes() == original and not (outside/'output.json').exists()


def test_setup_diagnostics_cannot_erase_missing_grammar(controller, monkeypatch):
    monkeypatch.setattr(gates, 'analysis_catalog', lambda: {'requirements': [{
        'id': 'grammar', 'title': 'Complete nested grammar', 'status': 'unresolved',
        'required_for': ['comparison']}], 'commands': [], 'flows': [], 'blockers': []})
    fake_verification(monkeypatch)
    status, submitted = request(controller, '/api/verify', {})
    assert status == 200
    terminal = controller.manager.wait(submitted['result']['job_id'], timeout=5)
    assert terminal['status'] == 'completed'
    state = request(controller, '/api/readiness')[1]
    assert state['setup_ready'] and not state['comparison_ready']
    assert any(blocker['id'] == 'grammar' for blocker in state['blockers'])
    assert request(controller, '/api/compare', {})[0] == 409


@pytest.mark.parametrize('outcome', ['failed', 'cancelled'])
def test_failed_or_cancelled_verification_never_publishes_green_setup(controller, monkeypatch, outcome):
    fake_verification(monkeypatch)
    entered, release = threading.Event(), threading.Event()
    def construction(_store, _out):
        if outcome == 'failed':
            raise RuntimeError('deliberate independent diagnostic failure')
        entered.set()
        assert release.wait(timeout=5)
        return []
    monkeypatch.setattr(gates, '_construction_check', construction)
    status, submitted = request(controller, '/api/verify', {})
    assert status == 200
    job_id = submitted['result']['job_id']
    if outcome == 'cancelled':
        try:
            assert entered.wait(timeout=3)
            assert invoke(controller, 'local.jobs.cancel', {'job_id': job_id}) == (200, {'status': 'completed', 'result': True})
        finally:
            release.set()
    terminal = controller.manager.wait(job_id, timeout=5)
    assert terminal['status'] == ('cancelled' if outcome == 'cancelled' else 'technical_failure')
    assert controller.store.get_head(gates.LATEST_HEAD) is None
    state = request(controller, '/api/readiness')[1]
    assert not state['setup_ready'] and not state['comparison_ready']


def test_artifact_get_is_read_only_inert_json(controller):
    ident = controller.store.put_json({'kind': 'diagnostic', 'value': '<script>alert(1)</script>',
                                     'path': '../../outside', 'method': 'local.jobs.submit'})
    before = set((controller.store.path/'blobs').iterdir())
    status, value = request(controller, '/api/artifact/'+ident)
    assert status == 200 and value['value'] == '<script>alert(1)</script>'
    assert set((controller.store.path/'blobs').iterdir()) == before
    assert request(controller, '/api/artifact/../../outside')[0] == 400


def test_source_change_during_verification_keeps_proof_unpublished(controller, monkeypatch):
    fake_verification(monkeypatch)
    names = gates.REQUIRED_CHECKS-{'all replay dependencies available', 'all eleven local recipe subsets',
        'recipe artifact integrity', 'source unchanged during verification'}
    def changed(_store, _out):
        controller.test_source[0] = 'b'*64
        return [{'name': name, 'passed': True} for name in names]
    monkeypatch.setattr(gates, '_construction_check', changed)
    status, submitted = request(controller, '/api/verify', {})
    assert status == 200
    terminal = controller.manager.wait(submitted['result']['job_id'], timeout=5)
    assert terminal['status'] == 'technical_failure'
    assert controller.store.get_head(gates.LATEST_HEAD) is None
    assert request(controller, '/api/readiness')[1]['restart_required']


@pytest.mark.parametrize('step_count', [1, 2])
def test_source_change_during_pipeline_blocks_next_step_and_publication(controller, monkeypatch, step_count):
    from sprite_workbench import construction
    original = construction._save_project
    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        controller.test_source[0] = 'b'*64
        return result
    monkeypatch.setattr(construction, '_save_project', changed)
    document = json.loads((Path(__file__).resolve().parents[1]/
        'sprite_workbench/contracts/SETUP-CONSTRUCTION.json').read_text())
    steps = [{'id': 'source', 'action': 'construction', 'method': 'save', 'request': {'document': document}}]
    if step_count == 2:
        steps.append({'id': 'write', 'action': 'construction', 'method': 'write',
            'request': {'project': {'ref': 'source.project'}, 'path': 'should-not-exist.json'}})
    status, submitted = invoke(controller, 'local.jobs.submit', {'handler': 'local.pipeline',
        'request': {'plan': {'version': 1, 'steps': steps}}, 'head': 'test:stale-pipeline'})
    assert status == 200
    terminal = controller.manager.wait(submitted['result'], timeout=5)
    assert terminal['status'] in {'validation_error', 'technical_failure'}
    assert controller.store.get_head('test:stale-pipeline') is None
    assert not (controller.base/'should-not-exist.json').exists()

