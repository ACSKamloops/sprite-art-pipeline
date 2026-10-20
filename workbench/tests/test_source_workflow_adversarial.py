"""Real HTTP and persistence review of the recovered-source host wrappers."""
from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
import pytest

from sprite_workbench.core import Store, canonical_json, digest, load_sequence
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.source_workflow import PRESETS_SHA256, RENDER_JOB, source_catalog
from sprite_workbench.web_server import ControlServer

ROOT = Path(__file__).parents[1]
PRESETS = json.loads((ROOT / 'sprite_workbench/contracts/SOURCE-VFX-PRESETS.json').read_bytes())['presets']


@contextmanager
def controller(path):
    server = ControlServer(Store(path / 'store'), base_dir=path / 'files', port=0, workers=1)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def http(server, path='/api/invoke', body=None):
    headers = {'X-Workbench-Token': server.token, 'Content-Type': 'application/json'}
    request = Request(server.url + path, None if body is None else json.dumps(body).encode(), headers)
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def invoke(server, method, params):
    status, result = http(server, body={'method': method, 'params': params})
    assert status == 200, result
    assert result['status'] == 'completed'
    return result['result']


def job(server, request, **options):
    return invoke(server, 'local.jobs.submit', {'handler': RENDER_JOB, 'request': request, **options})


def finished(server, ident):
    return invoke(server, 'local.jobs.wait', {'job_id': ident, 'timeout': 20})


def blobs(store):
    return {p.name for p in (store.path / 'blobs').iterdir()}


def test_http_all_four_methods_do_not_change_raw_recipe_or_double_apply(tmp_path):
    recipe = deepcopy(PRESETS[1]['recipe'])
    before = deepcopy(recipe)
    with controller(tmp_path) as web:
        description = invoke(web, 'local.pixellab.vfx.describe', {})
        assert len(description['families']) == 17
        normalized = invoke(web, 'local.pixellab.vfx.validate', {'recipe': recipe})
        assert normalized['recipe']['layers'][0]['rng'] is None
        controls = invoke(web, 'local.pixellab.vfx.controls', {'recipe': recipe})
        result = invoke(web, 'local.pixellab.vfx.render', {'recipe': recipe})
        receipt = web.store.get_json(result['control_receipt'])
        assert receipt['renderer_input'] == recipe
        assert receipt['hashes'] == controls['hashes']
        assert recipe == before
        assert web.store.get_json(result['sequence'])['visual_approval'] == 'unreviewed'
        assert result['provenance']['classification'] == 'deterministic-source'
        assert 55110 in result['executed_modules']


@pytest.mark.parametrize('params', [None, [], 'bad', {'recipe': []}, {'recipe': {}},
    {'recipe': PRESETS[0]['recipe'], 'algorithm': 'new-neural-effect'},
    {'recipe': PRESETS[0]['recipe'], 'values': {'unknown': 1}},
    {'recipe': {**PRESETS[0]['recipe'], 'layers': [{'id': 'x', 'type': 'private-neural-magic'}]}},
    {'recipe': PRESETS[0]['recipe'], 'timeout': True},
    {'recipe': {**PRESETS[0]['recipe'], 'canvas': {'w': 513, 'h': 16}}},
    {'recipe': {**PRESETS[0]['recipe'], 'frames': 33}},
    {'recipe': PRESETS[0]['recipe'], 'subject': '0' * 64}])
def test_bad_http_render_inputs_create_no_artifacts_or_heads(tmp_path, params):
    with controller(tmp_path) as web:
        before = blobs(web.store)
        status, result = http(web, body={'method': 'local.pixellab.vfx.render', 'params': params})
        assert status == 400 and result['status'] == 'validation_error'
        assert blobs(web.store) == before
        assert web.store.get_head('effect') is None
        assert http(web, '/api/jobs')[1] == []


def test_private_and_unregistered_methods_never_fallback(tmp_path):
    with controller(tmp_path) as web:
        before = blobs(web.store)
        for method in ('mcp.create_character', 'local.pixellab.vfx.neural', 'local.pixellab.character.animate'):
            status, result = http(web, body={'method': method, 'params': {}})
            assert status == 400 and result['status'] == 'unsupported'
        assert blobs(web.store) == before
        assert http(web, '/api/jobs')[1] == []


def test_real_source_job_completion_and_failed_input_are_durable(tmp_path):
    with controller(tmp_path) as web:
        successful = job(web, {'recipe': PRESETS[0]['recipe']})
        complete = finished(web, successful)
        assert complete['status'] == 'completed'
        assert complete['outputs'][0]['disposition'] == 'candidate'
        source = complete['outputs'][0]['metadata']['source_result']
        assert source['sequence'] == complete['artifact']
        assert web.store.get_json(source['control_receipt'])['renderer_input'] == PRESETS[0]['recipe']
        invalid = job(web, {'recipe': {'canvas': {'w': 16, 'h': 16}, 'layers': []}})
        failed = finished(web, invalid)
        assert failed['status'] == 'validation_error' and failed['outputs'] == []
        assert failed['artifact'] is None
    with controller(tmp_path) as restarted:
        assert invoke(restarted, 'local.jobs.get', {'job_id': successful})['artifact'] == complete['artifact']
        assert invoke(restarted, 'local.jobs.get', {'job_id': invalid})['status'] == 'validation_error'


def test_queued_cancel_and_restart_retry_execute_original_source_once(tmp_path):
    entered, release = threading.Event(), threading.Event()
    with controller(tmp_path) as web:
        def barrier(request, context):
            from sprite_workbench.jobs import JobResult
            entered.set()
            assert release.wait(15)
            return JobResult(web.store.put_json({'kind': 'scheduler-barrier'}))
        web.manager.register('local.review.barrier', barrier)
        blocking = invoke(web, 'local.jobs.submit', {'handler': 'local.review.barrier', 'request': {}})
        assert entered.wait(5)
        try:
            cancelled = job(web, {'recipe': PRESETS[1]['recipe']}, head='review-candidate')
            assert invoke(web, 'local.jobs.cancel', {'job_id': cancelled}) is True
            assert finished(web, cancelled)['status'] == 'cancelled'
            assert web.store.get_head('review-candidate') is None
        finally:
            release.set()
        finished(web, blocking)
    with controller(tmp_path) as restarted:
        retried = invoke(restarted, 'local.jobs.retry', {'job_id': cancelled})
        # Retrying the same cancelled job is idempotent across persistence.
        assert invoke(restarted, 'local.jobs.retry', {'job_id': cancelled}) == retried
        done = finished(restarted, retried)
        assert done['status'] == 'completed' and done['retry_of'] == cancelled and done['attempt'] == 2
        assert restarted.store.get_head('review-candidate') == done['artifact']
        assert done['outputs'][0]['metadata']['source_result']['executed_modules']


def test_source_drift_blocks_sync_catalog_and_queued_execution_without_generation(tmp_path, monkeypatch):
    import sprite_workbench.readiness as readiness
    with controller(tmp_path) as web:
        before = blobs(web.store)
        monkeypatch.setattr(readiness, 'source_fingerprint', lambda: 'changed-after-start')
        assert http(web, '/api/pixellab/source')[0] == 400
        assert http(web, body={'method': 'local.pixellab.vfx.render', 'params': {'recipe': PRESETS[0]['recipe']}})[0] == 400
        assert blobs(web.store) == before
        ident = job(web, {'recipe': PRESETS[0]['recipe']})
        admitted = blobs(web.store)
        result = finished(web, ident)
        assert result['status'] == 'validation_error' and result['outputs'] == []
        assert 'Restart' in result['error']['reason']
        assert blobs(web.store) == admitted  # Only job request was retained.


@pytest.mark.parametrize('interruption', ['cancel', 'source-change'])
def test_source_job_interrupted_after_original_render_never_publishes(tmp_path, monkeypatch, interruption):
    import sprite_workbench.source_workflow as workflow
    import sprite_workbench.readiness as readiness
    entered, release = threading.Event(), threading.Event()
    original = workflow.invoke_source_vfx
    rendered = {}
    def pause_after_actual_render(*args, **kwargs):
        result = original(*args, **kwargs)
        rendered.update(result)
        entered.set()
        assert release.wait(15)
        return result
    monkeypatch.setattr(workflow, 'invoke_source_vfx', pause_after_actual_render)
    with controller(tmp_path) as web:
        ident = job(web, {'recipe': PRESETS[0]['recipe']}, head='interrupted-render')
        assert entered.wait(10)
        try:
            if interruption == 'cancel':
                assert invoke(web, 'local.jobs.cancel', {'job_id': ident}) is True
            else:
                monkeypatch.setattr(readiness, 'source_fingerprint', lambda: 'changed-during-render')
        finally:
            release.set()
        result = finished(web, ident)
        assert result['status'] == ('cancelled' if interruption == 'cancel' else 'validation_error')
        assert result['outputs'] == [] and result['artifact'] is None
        assert web.store.get_head('interrupted-render') is None
        # Computed immutable artifacts remain retained but have no publication head.
        assert web.store.get_json(rendered['sequence'])['kind'] == 'sequence'


def test_http_pipeline_action_uses_same_source_and_portable_receipt(tmp_path):
    with controller(tmp_path) as web:
        plan = {'version': 1, 'steps': [{'id': 'source', 'action': 'pixellab_vfx',
                                        'recipe': PRESETS[0]['recipe']}]}
        assert http(web, '/api/plan', {'plan': plan})[0] == 200
        ident = invoke(web, 'local.jobs.submit', {'handler': 'local.pipeline', 'request': {'plan': plan}})
        completed = finished(web, ident)
        assert completed['status'] == 'completed'
        doc = web.store.get_json(completed['artifact'])
        receipt = web.store.get_json(doc['metadata']['pixellab_controls'])
        assert receipt['renderer_input'] == PRESETS[0]['recipe']
        assert receipt['provenance']['classification'] == 'deterministic-source'


def test_fresh_store_editable_export_retains_receipt_frames_and_all_streams(tmp_path):
    with controller(tmp_path) as web:
        result = invoke(web, 'local.pixellab.vfx.render', {'recipe': PRESETS[1]['recipe']})
        expected_receipt = web.store.get_json(result['control_receipt'])
        for name, sequence in result['streams'].items():
            folder = tmp_path / ('export-' + name)
            export_sequence(web.store, sequence, folder, ['editable'])
            fresh = Store(tmp_path / ('fresh-' + name))
            assert import_editable(fresh, folder / 'editable') == sequence
            doc, arrays = load_sequence(fresh, sequence)
            _, original = load_sequence(web.store, sequence)
            assert all(np.array_equal(a, b) for a, b in zip(arrays, original))
            assert fresh.get_json(doc['metadata']['pixellab_controls']) == expected_receipt
            recipe = fresh.get_json(doc['metadata']['recipe'])
            assert fresh.get_bytes(recipe['renderer_manifest'])


def test_two_packaged_presets_are_exact_pinned_retained_raw_responses():
    catalog = source_catalog()
    assert catalog['presets_sha256'] == PRESETS_SHA256
    assert {p['id'] for p in catalog['presets']} == {'slash_arc', 'energy_orb'}
    capture = Path('/home/astra/projects/pixellab-local-test-20261011')
    if not capture.is_dir():
        pytest.skip('Original capture unavailable; packaged recipe pins covered by source catalog identity')
    fixtures = json.loads((ROOT / 'tests/fixtures/effects/server-cases.json').read_text())['cases']
    for preset in catalog['presets']:
        provenance = preset['provenance']
        raw = (capture / provenance['response_path']).read_bytes()
        assert digest(raw) == provenance['response_sha256']
        text = json.loads(raw)['result']['content'][0]['text']
        recipe_start = text[text.index('{'):]
        decoded, end = json.JSONDecoder().raw_decode(recipe_start)
        recipe_text = recipe_start[:end]
        assert digest(recipe_text.encode()) == provenance['response_recipe_text_sha256']
        assert decoded == preset['recipe']
        assert digest(canonical_json(preset['recipe'])) == provenance['recipe_sha256']
        assert next(c['recipe'] for c in fixtures if c['name'] == preset['id']) == preset['recipe']
        assert 'recipe' not in json.loads(provenance['request_argv'][2])
        assert provenance['request_contains_recipe'] is False


def test_cli_renders_retained_recipe_and_rejects_unsupported_method(tmp_path):
    request = tmp_path / 'request.json'
    request.write_bytes(canonical_json({'recipe': PRESETS[0]['recipe']}))
    store = tmp_path / 'cli-store'
    result = subprocess.run([sys.executable, '-m', 'sprite_workbench', '--workspace', str(store),
                             'pixellab-vfx', 'render', str(request)],
                            capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr.decode()
    payload = json.loads(result.stdout)
    assert Store(store).get_json(payload['control_receipt'])['renderer_input'] == PRESETS[0]['recipe']
    before = blobs(Store(store))
    invalid = subprocess.run([sys.executable, '-m', 'sprite_workbench', '--workspace', str(store),
                              'pixellab-vfx', 'neural', str(request)],
                             capture_output=True, timeout=10)
    assert invalid.returncode != 0
    assert blobs(Store(store)) == before
