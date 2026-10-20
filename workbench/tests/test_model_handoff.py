"""Model handoff diagnostics only: no generated art or provider calls."""
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import subprocess
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
import pytest

from sprite_workbench.acquisition import import_image
from sprite_workbench.channel import serve
from sprite_workbench.core import Store, ValidationError, save_sequence
from sprite_workbench.export import export_sequence, import_editable, png_bytes
from sprite_workbench.model_handoff import invoke_models
from sprite_workbench.web_server import ControlServer


@pytest.fixture
def supplied(tmp_path):
    store = Store(tmp_path / 'store')
    array = np.arange(4 * 5 * 4, dtype=np.uint8).reshape(4, 5, 4)
    array[..., 3] = 255; array[0, 0, 3] = 0; array[1, 1, 3] = 127
    path = tmp_path / 'supplied.png'; path.write_bytes(png_bytes(array))
    imported = import_image(store, path)
    return store, array, imported


def brief(raster=None, task='still'):
    return {'version': 1, 'task': task, 'prompt': '  Keep this instruction verbatim.\n',
            'inputs': [] if raster is None else [{'role': 'edit_target' if task == 'edit' else 'subject', 'raster': raster}],
            'requirements': {'transparent_background': True, 'desired_size': [256, 256]}, 'hard_controls': {}}


def prepare(store, value=None):
    return invoke_models(store, 'prepare', {'brief': value or brief(),
        'executors': ['codex.imagegen', 'hermes.image_generate']})


def attach(store, task, sequence, execution=None):
    return invoke_models(store, 'ingest', {'task': task, 'sequence': sequence,
        'execution': execution or {'kind': 'supplied-diagnostic'}})


def test_paired_requests_share_exact_instruction_roles_pixels_and_visible_appendix(supplied, monkeypatch):
    store, array, imported = supplied
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('No agent/provider may be launched'))
    value = brief(imported['rasters'][0], 'edit'); batch = prepare(store, value)
    assert batch['execution_status'] == 'held' and batch['provider_calls'] == 0
    packets = [invoke_models(store, 'packet', {'task': row['task']}) for row in batch['tasks']]
    assert packets[0]['brief'] == packets[1]['brief'] == batch['brief']
    assert packets[0]['request']['prompt'] == value['prompt']
    assert packets[0]['transport_draft']['arguments']['prompt'] == packets[1]['transport_draft']['arguments']['prompt']
    assert packets[0]['transport_draft']['arguments']['prompt'].startswith(value['prompt'])
    assert packets[0]['transport_draft']['arguments']['referenced_image_paths'] == ['inputs/000-edit_target.png']
    assert packets[1]['transport_draft']['arguments']['image_url'] == 'inputs/000-edit_target.png'
    for packet in packets:
        assert not packet['execution_authorized_by_packet']
        assert packet['inputs'][0]['raster'] == imported['rasters'][0]
        assert store.get_bytes(packet['inputs'][0]['png']) == png_bytes(array)
    assert packets[1]['backend']['image_provider'] is None
    assert packets[1]['backend']['orchestrator_model'] == 'MiniMax-M3.1-Flash-Preview'


@pytest.mark.parametrize('change', ['seed', 'mask', 'joints', 'clock', 'animation', 'unknown', 'end_frame', 'whitespace'])
def test_unsupported_inputs_reject_before_task_or_blob_publication(supplied, change):
    store, _, _ = supplied; value = brief()
    if change in ['seed', 'mask', 'joints', 'clock']:
        value['hard_controls'][change] = 123
    elif change == 'animation': value['task'] = 'animation'
    elif change == 'end_frame': value['inputs'] = [{'role': 'end_frame', 'raster': 'a' * 64}]
    elif change == 'whitespace': value['prompt'] = ' \n'
    else: value['unknown'] = True
    before = set((store.path / 'blobs').iterdir())
    with pytest.raises(ValidationError): prepare(store, value)
    assert set((store.path / 'blobs').iterdir()) == before


@pytest.mark.parametrize('executors', [['imaginary'], ['codex.imagegen', 'codex.imagegen'], []])
def test_unknown_or_duplicate_executor_never_falls_back(supplied, executors):
    store, _, _ = supplied
    with pytest.raises(ValidationError): invoke_models(store, 'prepare', {'brief': brief(), 'executors': executors})


def test_edit_target_required_first_without_silent_reordering(supplied):
    store, _, imported = supplied; value = brief(imported['rasters'][0], 'edit')
    value['inputs'].insert(0, {'role': 'style', 'raster': imported['rasters'][0]})
    with pytest.raises(ValidationError, match='slot 0'): prepare(store, value)


def test_ingest_retains_raw_size_alpha_hidden_rgb_and_unreviewed_identity(supplied):
    store, array, imported = supplied; batch = prepare(store)
    result = attach(store, batch['tasks'][0]['task'], imported['sequence'])
    assert result['sequence'] != imported['sequence']
    assert result['audit']['desired_size_matches'] is False
    assert result['manifest']['canvas'] == [5, 4]
    assert result['audit']['requested_transparency_observed'] is True
    assert result['manifest']['source_bytes'] == imported['source_bytes']
    assert result['artistic_acceptance'] == 'unreviewed'
    assert np.array_equal(store.get_raster(store.get_json(result['sequence'])['frames'][0]['raster']), array)
    assert 'Not model timing' in result['manifest']['timing_origin']
    rows = invoke_models(store, 'results', {'experiment': batch['experiment']})['results']
    assert rows[0]['result'] == result['result'] and rows[0]['execution']['kind'] == 'supplied-diagnostic'


def test_animations_and_diagnostic_model_claims_are_rejected(supplied):
    store, array, imported = supplied; task = prepare(store)['tasks'][0]['task']
    multiple = save_sequence(store, [array, array])
    with pytest.raises(ValidationError, match='one raw frame'): attach(store, task, multiple)
    with pytest.raises(ValidationError, match='cannot claim'): attach(store, task, imported['sequence'],
        {'kind': 'supplied-diagnostic', 'image_model': 'imaginary-model'})


def test_external_result_requires_original_bytes_and_matching_decoded_pixels(supplied):
    store, array, imported = supplied; task = prepare(store)['tasks'][0]['task']
    execution = {'kind': 'external-generation', 'tool': 'synthetic-test-attestation'}
    without_bytes = save_sequence(store, [array])
    with pytest.raises(ValidationError, match='original encoded bytes'): attach(store, task, without_bytes, execution)
    altered = array.copy(); altered[0, 0, 0] ^= 1
    forged = save_sequence(store, [altered], metadata={'source_bytes': imported['source_bytes']})
    with pytest.raises(ValidationError, match='cannot be verified'): attach(store, task, forged, execution)
    # Synthetic attestation exercises parsing only, not real generation evidence.
    result = attach(store, task, imported['sequence'], execution)
    assert store.get_json(result['result'])['execution_provenance'].startswith('executor-attested')


def test_result_and_all_references_survive_editable_roundtrip(supplied, tmp_path):
    store, array, imported = supplied
    batch = prepare(store, brief(imported['rasters'][0], 'edit'))
    result = attach(store, batch['tasks'][0]['task'], imported['sequence'])
    export_sequence(store, result['sequence'], tmp_path / 'export', ['editable'])
    fresh = Store(tmp_path / 'fresh')
    assert import_editable(fresh, tmp_path / 'export/editable') == result['sequence']
    receipt = fresh.get_json(result['result']); task = fresh.get_json(receipt['task'])
    assert fresh.get_json(task['brief'])['brief']['prompt'].startswith('  Keep')
    assert fresh.get_bytes(task['inputs'][0]['png']) == png_bytes(array)
    assert fresh.get_bytes(imported['source_bytes']) == store.get_bytes(imported['source_bytes'])


def test_packet_file_export_is_lossless_bounded_and_non_overwriting(supplied, tmp_path):
    store, array, imported = supplied
    task = prepare(store, brief(imported['rasters'][0]))['tasks'][0]['task']
    invoke_models(store, 'export_packet', {'task': task, 'directory': 'packet'}, base_dir=tmp_path)
    value = json.loads((tmp_path / 'packet/packet.json').read_text())
    assert value['execution_status'] == 'held'
    assert (tmp_path / 'packet/inputs/000-subject.png').read_bytes() == png_bytes(array)
    with pytest.raises(ValidationError): invoke_models(store, 'export_packet', {'task': task, 'directory': 'packet'}, base_dir=tmp_path)
    with pytest.raises(ValidationError): invoke_models(store, 'export_packet', {'task': task, 'directory': '../outside'}, base_dir=tmp_path)


def test_diagnostics_and_unknown_or_same_image_models_cannot_be_ranked(supplied):
    store, _, imported = supplied; batch = prepare(store); tasks = batch['tasks']
    left = attach(store, tasks[0]['task'], imported['sequence'])
    right = attach(store, tasks[1]['task'], imported['sequence'])
    audit = invoke_models(store, 'audit_pair', {'left': left['result'], 'right': right['result'], 'scope': 'image-backend'})
    assert audit['exact_pixels_equal'] and not audit['comparison_eligible_by_attestation']
    assert audit['quality_score'] is None and audit['artistic_acceptance'] == 'unreviewed'
    external = []
    for item in tasks:
        draft = invoke_models(store, 'packet', {'task': item['task']})['transport_draft']['arguments']['prompt']
        external.append(attach(store, item['task'], imported['sequence'], {
            'kind': 'external-generation',
            'tool': 'image_gen.imagegen' if item['executor'] == 'codex.imagegen' else 'image_generate',
            'image_transport': 'builtin.imagegen' if item['executor'] == 'codex.imagegen' else 'openai-codex',
            'orchestrator_provider': 'OpenAI' if item['executor'] == 'codex.imagegen' else 'minimax-oauth',
            'orchestrator_model': 'synthetic-test-model' if item['executor'] == 'codex.imagegen' else 'MiniMax-M3.1-Flash-Preview',
            'image_provider': 'OpenAI' if item['executor'] == 'codex.imagegen' else 'openai',
            'image_model': 'same-model', 'actual_prompt': draft,
            'submitted_inputs': [], 'submitted_controls': {'transparent_background': True} if item['executor'] == 'codex.imagegen' else {}}))
    ids = {'left': external[0]['result'], 'right': external[1]['result']}
    assert not invoke_models(store, 'audit_pair', {**ids, 'scope': 'image-backend'})['comparison_eligible_by_attestation']
    assert invoke_models(store, 'audit_pair', {**ids, 'scope': 'orchestrator'})['comparison_eligible_by_attestation']


@pytest.mark.parametrize('contradiction', ['same-agent', 'different-image-models', 'wrong-tool',
    'wrong-transport', 'missing-inputs', 'wrong-input-order', 'wrong-controls', 'rewritten-prompt', 'impossible-image-vendor'])
def test_contradictory_or_missing_execution_attestations_never_qualify(supplied, contradiction):
    store, _, imported = supplied; batch = prepare(store, brief(imported['rasters'][0]))
    attached = []
    for index, item in enumerate(batch['tasks']):
        packet = invoke_models(store, 'packet', {'task': item['task']})
        codex = item['executor'] == 'codex.imagegen'
        attestation = {'kind': 'external-generation',
            'tool': 'image_gen.imagegen' if codex else 'image_generate',
            'image_transport': 'builtin.imagegen' if codex else 'openai-codex',
            'orchestrator_provider': 'OpenAI' if codex else 'minimax-oauth',
            'orchestrator_model': 'synthetic-test-model' if codex else 'MiniMax-M3.1-Flash-Preview',
            'image_provider': 'OpenAI', 'image_model': 'same-model',
            'actual_prompt': packet['transport_draft']['arguments']['prompt'],
            'submitted_inputs': [{k: r[k] for k in ['slot', 'role', 'decoded_rgba_sha256']} for r in packet['inputs']],
            'submitted_controls': {'transparent_background': True} if codex else {}}
        if index == 1:
            if contradiction == 'same-agent':
                attestation.update(orchestrator_provider='OpenAI', orchestrator_model='synthetic-test-model')
            elif contradiction == 'different-image-models': attestation['image_model'] = 'different-image-model'
            elif contradiction == 'wrong-tool': attestation['tool'] = 'unrelated-tool'
            elif contradiction == 'wrong-transport': attestation['image_transport'] = 'unrelated-transport'
            elif contradiction == 'missing-inputs': attestation.pop('submitted_inputs')
            elif contradiction == 'wrong-input-order': attestation['submitted_inputs'][0]['slot'] = 1
            elif contradiction == 'wrong-controls': attestation['submitted_controls'] = {'transparent_background': True}
            elif contradiction == 'impossible-image-vendor': attestation['image_provider'] = 'unmapped-image-vendor'
            else: attestation['actual_prompt'] += ' silent rewrite'
        attached.append(attach(store, item['task'], imported['sequence'], attestation)['result'])
    report = invoke_models(store, 'audit_pair', {'left': attached[0], 'right': attached[1], 'scope': 'orchestrator'})
    assert not report['comparison_eligible_by_attestation']
    assert report['artistic_acceptance'] == 'unreviewed' and report['quality_score'] is None


def test_pair_requires_same_frozen_brief_and_distinct_results(supplied):
    store, _, imported = supplied
    one = prepare(store); value = brief(); value['prompt'] = 'Different prompt'
    two = prepare(store, value)
    a = attach(store, one['tasks'][0]['task'], imported['sequence'])['result']
    b = attach(store, two['tasks'][0]['task'], imported['sequence'])['result']
    for other in [a, b]:
        with pytest.raises(ValidationError): invoke_models(store, 'audit_pair', {'left': a, 'right': other, 'scope': 'orchestrator'})


@pytest.mark.parametrize('extra', [{'Authorization': 'redacted-placeholder'}, {'parameters': {'api_key': 'redacted-placeholder'}}])
def test_receipt_schema_rejects_credential_or_unknown_metadata_fields(supplied, extra):
    store, _, imported = supplied; task = prepare(store)['tasks'][0]['task']
    with pytest.raises(ValidationError): attach(store, task, imported['sequence'], {'kind': 'supplied-diagnostic', **extra})


def test_jsonl_exposes_preparation_and_keeps_model_execution_absent(tmp_path):
    base = tmp_path / 'files'; base.mkdir()
    messages = [dict(id=1, method='local.models.prepare', params={'brief': brief(), 'executors': ['codex.imagegen']}),
                dict(id=2, method='local.models.execute', params={}), dict(id=3, method='system.shutdown', params={})]
    output = StringIO(); serve(Store(tmp_path / 'store'), base_dir=base, result_ref='result', workers=1,
        source=StringIO(''.join(json.dumps(v)+'\n' for v in messages)), sink=output)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    assert rows[1]['result']['execution_status'] == 'held'
    assert rows[2]['status'] == 'unsupported'


def test_actual_http_prepares_pair_returns_packets_and_leaves_comparison_gate_held(tmp_path):
    server = ControlServer(Store(tmp_path / 'store'), base_dir=tmp_path / 'files', port=0, workers=1)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        def request(path, body=None):
            headers = {'Content-Type': 'application/json', 'X-Workbench-Token': server.token}
            req = Request(server.url + path, data=None if body is None else json.dumps(body).encode(), headers=headers)
            with urlopen(req, timeout=10) as response: return json.load(response)
        created = request('/api/invoke', {'method': 'local.models.prepare', 'params': {
            'brief': brief(), 'executors': ['codex.imagegen', 'hermes.image_generate']}})['result']
        assert len(created['tasks']) == 2 and created['execution_status'] == 'held'
        value = request('/api/invoke', {'method': 'local.models.packet', 'params': {'task': created['tasks'][0]['task']}})['result']
        assert value['transport_draft']['tool'] == 'image_gen.imagegen'
        with urlopen(server.url + '/model-lab.js') as response: assert response.status == 200
        assert not request('/api/readiness')['comparison_ready']
        with pytest.raises(HTTPError) as error: request('/api/compare', {})
        assert error.value.code == 409
        error.value.close()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
