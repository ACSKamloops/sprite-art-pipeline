import json
from pathlib import Path
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
import pytest

from sprite_workbench.core import Store
from sprite_workbench.export import png_bytes, export_sequence, import_editable
from sprite_workbench.web_server import ControlServer
from sprite_workbench import readiness as gates


@pytest.fixture
def web(tmp_path):
    store = Store(tmp_path / 'store')
    server = ControlServer(store, base_dir=tmp_path / 'files', port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        yield server
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


def call(web, path, body=None, *, headers=None, raw=False):
    headers = dict(headers or {})
    if body is not None:
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('X-Workbench-Token', web.token)
        body = body if raw else json.dumps(body).encode()
    request = Request(web.url + path, body, headers)
    try:
        with urlopen(request, timeout=20) as response:
            payload = response.read()
            return response.status, json.loads(payload) if response.headers.get_content_type() == 'application/json' else payload
    except HTTPError as error:
        return error.code, json.loads(error.read())


def invoke(web, method, params):
    status, payload = call(web, '/api/invoke', {'method': method, 'params': params})
    assert status == 200 and payload['status'] == 'completed', payload
    return payload['result']


def test_actual_http_upload_pixel_edit_history_and_portable_reload(web, tmp_path):
    a = np.zeros((4, 6, 4), np.uint8); a[1, 1] = [39, 87, 123, 255]
    status, source = call(web, '/api/upload', png_bytes(a), raw=True, headers={'Content-Type': 'image/png'})
    assert status == 200 and source['sequence']
    project = invoke(web, 'local.construction.from_sequence', {'sequence': source['sequence']})
    history = invoke(web, 'local.construction.history', {'project': project['project']})
    status, full = call(web, '/api/project/' + project['project'])
    assert status == 200 and full['project_hash'] == project['project_hash']
    cel = next(iter(full['document']['cels']))
    edited = invoke(web, 'local.construction.edit', {'history': history['history'], 'transaction': {
        'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': project['project_hash'],
        'reason': 'browser single-pixel correction', 'operations': [{'op': 'paint', 'cel_id': cel, 'points': [[2, 2, 1]]}]}})
    stale, error = call(web, '/api/invoke', {'method': 'local.construction.edit', 'params': {
        'history': edited['history'], 'transaction': {'schema': 'sprite-edit-transaction/v1',
        'expected_project_sha256': project['project_hash'], 'reason': 'stale', 'operations': []}}})
    assert stale == 400 and error['status'] == 'validation_error'
    undone = invoke(web, 'local.construction.undo', {'history': edited['history']})
    assert undone['project'] == project['project']
    redone = invoke(web, 'local.construction.redo', {'history': undone['history']})
    result = invoke(web, 'local.construction.render', {'project': redone['project'], 'history': redone['history'], 'animation_id': 'clip'})
    doc = call(web, '/api/artifact/' + result['sequence'])[1]
    assert call(web, '/api/raster/' + doc['frames'][0]['raster'] + '.png')[0] == 200
    export_sequence(web.store, result['sequence'], tmp_path / 'portable', ['editable'])
    fresh = Store(tmp_path / 'fresh'); import_editable(fresh, tmp_path / 'portable/editable')
    from sprite_workbench.construction import move_history
    assert move_history(fresh, redone['history'], 'undo')['project'] == project['project']


def test_origin_nonce_host_and_filesystem_boundaries(web):
    assert call(web, '/api/bootstrap')[0] == 200
    assert call(web, '/api/jobs', headers={'Host': 'attacker.invalid'})[0] == 403
    assert call(web, '/api/bootstrap', headers={'Origin': 'https://attacker.invalid'})[0] == 403
    assert call(web, '/api/verify', {}, headers={'X-Workbench-Token': 'wrong'})[0] == 403
    assert call(web, '/api/verify', {}, headers={'Origin': 'https://attacker.invalid'})[0] == 403
    status, _ = call(web, '/api/invoke', {'method': 'local.construction.read', 'params': {'path': '../secret.json'}})
    assert status == 400
    status, _ = call(web, '/api/invoke', {'method': 'local.jobs.submit', 'params': {'handler': 'local.pipeline',
        'request': {'plan': {'version': 1, 'steps': [{'id': 'a', 'action': 'import', 'path': '/etc/passwd'}]}}}})
    assert status == 400
    assert call(web, '/api/artifact/../../outside')[0] == 400
    assert call(web, '/api/compare', {})[0] == 409
    assert not call(web, '/api/readiness')[1]['comparison_ready']


def test_bad_upload_never_becomes_an_image_or_executes_a_request(web):
    assert call(web, '/api/upload', b'<svg onload="alert(1)"></svg>', raw=True)[0] == 400
    assert call(web, '/api/upload', b'\x89PNG\r\n\x1a\nBAD', raw=True)[0] == 400
    folder = web.base / 'uploads'
    if folder.exists():
        for item in folder.iterdir(): item.unlink()
        folder.rmdir()
    target = web.base.parent / 'external'; target.mkdir()
    folder.symlink_to(target, target_is_directory=True)
    a = np.zeros((1, 1, 4), np.uint8)
    assert call(web, '/api/upload', png_bytes(a), raw=True)[0] == 400
    assert not list(target.iterdir())
    assert call(web, '/api/jobs')[0] == 200


def test_readiness_never_infers_complete_analysis_from_green_setup(tmp_path, monkeypatch):
    store = Store(tmp_path)
    monkeypatch.setattr(gates, 'source_fingerprint', lambda: 'a' * 64)
    monkeypatch.setattr(gates, 'analysis_catalog', lambda: {'requirements': [
        {'id': 'R1', 'title': 'Missing grammar', 'status': 'runtime_pending', 'required_for': ['comparison']}],
        'commands': [], 'blockers': []})
    report = {'kind': 'readiness-verification', 'version': 1, 'source_fingerprint': 'a' * 64, 'status': 'completed',
              'checks': [{'name': n, 'passed': True} for n in gates.REQUIRED_CHECKS],
              'recipes': {'status': 'completed', 'flows': [{'flow': f'F{i:02}', 'status': 'completed'} for i in range(1, 12)]}}
    store.set_head(gates.LATEST_HEAD, store.put_json(report), expected=None)
    result = gates.readiness(store)
    assert result['setup_ready'] and not result['comparison_ready']
    assert result['blockers'][0]['id'] == 'R1'
    report['checks'] = [{'name': 'fake', 'passed': True}]
    store.set_head(gates.LATEST_HEAD, store.put_json(report), expected=store.get_head(gates.LATEST_HEAD))
    assert not gates.readiness(store)['setup_ready']
    monkeypatch.setattr(gates, 'source_fingerprint', lambda: 'b' * 64)
    assert not gates.readiness(store)['setup_ready']


def test_three_edit_checkpoint_closure_replays_cold_in_fresh_store(web, tmp_path):
    from sprite_workbench.construction import clear_history_proofs, load_history, move_history
    a = np.zeros((3, 5, 4), np.uint8); a[1, 1] = [100, 180, 210, 255]
    source = call(web, '/api/upload', png_bytes(a), raw=True)[1]
    state = invoke(web, 'local.construction.from_sequence', {'sequence': source['sequence']})
    initial = state['project']
    state = invoke(web, 'local.construction.history', {'project': initial})
    for x in range(3):
        state = invoke(web, 'local.construction.edit', {'history': state['history'], 'transaction': {
            'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': state['project_hash'],
            'reason': f'checkpoint {x}', 'operations': [{'op': 'paint', 'cel_id': 'cel-0', 'points': [[x, 0, 1]]}]}})
    result = invoke(web, 'local.construction.render', {'project': state['project'], 'history': state['history'], 'animation_id': 'clip'})
    export_sequence(web.store, result['sequence'], tmp_path / 'three-steps', ['editable'])
    fresh = Store(tmp_path / 'fresh-three')
    import_editable(fresh, tmp_path / 'three-steps/editable')
    clear_history_proofs()
    cold = load_history(fresh, state['history'])
    assert cold['journal']['cursor'] == 3
    for _ in range(3):
        state = move_history(fresh, state['history'], 'undo')
    assert state['project'] == initial


def test_plan_save_then_real_queued_execution_and_invalid_plan_refusal(web):
    fixture = json.loads((Path(__file__).parents[1] / 'examples/local-construction/source.json').read_text())
    source = call(web, '/api/upload', json.dumps(fixture).encode(), raw=True)[1]
    plan = {'version': 1, 'steps': [{'id': 'render', 'action': 'construction', 'method': 'render',
        'request': {'project': source['project'], 'animation_id': 'diagnostic'}}]}
    status, saved = call(web, '/api/plan', {'plan': plan})
    assert status == 200 and saved['plan']
    stored = call(web, '/api/artifact/' + saved['plan'])[1]
    job = invoke(web, 'local.jobs.submit', {'handler': 'local.pipeline', 'request': {'plan': stored['plan']}})
    result = web.manager.wait(job, timeout=10)
    assert result['status'] == 'completed' and result['artifact']
    assert call(web, '/api/plan', {'plan': {**plan, 'steps': [{'id': 'p', 'action': 'publish'}]}})[0] == 400
    assert call(web, '/api/plan', {'plan': {**plan, 'version': True}})[0] == 400


def test_json_and_raster_byte_limits_precede_full_blob_read(tmp_path, monkeypatch):
    import sprite_workbench.core as core
    from sprite_workbench.core import ValidationError
    store = Store(tmp_path)
    oversized = store.put_bytes(b'x' * 100)
    monkeypatch.setattr(core, 'MAX_DOCUMENT_BYTES', 16)
    original = Path.read_bytes
    def no_whole_read(path):
        if path == store.path / 'blobs' / oversized:
            raise AssertionError('Oversized immutable JSON was fully allocated')
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', no_whole_read)
    with pytest.raises(ValidationError):
        store.get_json(oversized)
    with pytest.raises(ValidationError, match='byte budget'):
        store.get_bytes(oversized, max_bytes=4)


def test_source_request_validation_http_layers_without_provider(web):
    def request(count):
        frame={'image':{'base64':'fixture'},'size':{'width':256,'height':256}}
        return {'image_size':{'width':256,'height':256},'reference_image':frame,'frames':[frame]*count}
    result=invoke(web,'local.requests.validate_source',{
        'capability':'public:POST:/transfer-outfit-v2','request':request(3)})
    assert result['status']=='validated' and result['source_semantics']['max_frames']==3
    status,payload=call(web,'/api/invoke',{'method':'local.requests.validate_source','params':{
        'capability':'public:POST:/transfer-outfit-v2','request':request(4)}})
    assert status==400 and payload['error']['validation_layer']=='source-derived'
    malformed=request(2);malformed['image_size']['width']=257
    status,payload=call(web,'/api/invoke',{'method':'local.requests.validate_source','params':{
        'capability':'public:POST:/transfer-outfit-v2','request':malformed}})
    assert status==400 and payload['error']['validation_layer']=='frozen-schema'
