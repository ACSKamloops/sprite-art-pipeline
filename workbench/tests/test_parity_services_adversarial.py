"""Independent integration checks for explicit local source-backed adapters."""
from copy import deepcopy
from io import BytesIO, StringIO
import json
from pathlib import Path
import subprocess
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, digest, load_sequence, save_sequence


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / 'store')


@pytest.fixture
def services():
    from sprite_workbench import parity_services
    return parity_services


@pytest.fixture
def raster(store):
    return store.put_raster(np.array([[[37, 59, 83, 255], [7, 8, 9, 0]],
                                      [[1, 2, 3, 127], [4, 5, 6, 255]]], dtype=np.uint8))


def _blobs(store):
    return {p.name for p in (store.path / 'blobs').iterdir()}


@pytest.mark.parametrize('method,payload', [
    ('catalog', {'extra': True}), ('palette', {'raster': True}),
    ('palette', {'raster': '0' * 64, 'extra': True}),
    ('pixels', {'operation': 'transparency', 'request': {'raster': '0' * 64, 'extra': True}}),
    ('pixels', {'operation': 'decode', 'request': {'media': '0' * 64, 'width': True, 'height': 1}}),
    ('pixels', {'operation': 'decode', 'request': {'media': '0' * 64, 'width': 1.5, 'height': 1}}),
    ('pixels', {'operation': 'mask', 'request': {'mask': '0' * 64, 'art': '0' * 64, 'fill_background': 1}}),
    ('pixels', {'operation': 'place', 'request': {'source': '0' * 64, 'destination': '0' * 64, 'origin': [True, 0]}}),
    ('pixels', {'operation': 'server_cutout', 'request': {}}),
    ('footprints', {'commands': [{'method': 'ellipse-outline', 'pos': [True, 1], 'size': [2, 2]}]}),
    ('footprints', {'commands': [{'method': 'ellipse-outline', 'pos': [1, 1], 'size': [2, 2], 'radius': 1}]}),
    ('footprints', {'commands': []}),
    ('paint', {'history': '0' * 64, 'cel_id': 'a', 'command': {'method': 'ellipse-outline', 'pos': [1, 1], 'size': [2, 2]}, 'palette_index': True}),
    ('to_sequence', {'receipt': '0' * 64, 'duration': [True, 1]}),
    ('to_sequence', {'receipt': '0' * 64, 'duration': [1, 0]}),
    ('to_sequence', {'receipt': '0' * 64, 'duration': [1, 1], 'loop': True}),
])
def test_service_schemas_reject_extra_and_wrong_types_before_execution(services, store, method, payload):
    before = _blobs(store)
    with pytest.raises(ValidationError): services.invoke_parity(store, method, payload)
    assert _blobs(store) == before


@pytest.fixture
def pixel_receipt(services, store, raster):
    return services.invoke_parity(store, 'pixels', {'operation': 'serialize', 'request': {'raster': raster}})


@pytest.mark.parametrize('mutation', ['unknown_operation', 'missing_request', 'missing_execution',
                                      'execution_nonobject', 'input_mutation', 'method_hash',
                                      'source_hash', 'output_hash', 'input_hash', 'missing_raw',
                                      'version_bool'])
def test_partial_or_altered_receipts_cannot_be_promoted(services, store, pixel_receipt, mutation):
    doc = deepcopy(store.get_json(pixel_receipt['receipt']))
    if mutation == 'unknown_operation': doc['operation'] = 'invented_server_generator'
    elif mutation == 'missing_request': doc.pop('request')
    elif mutation == 'missing_execution': doc.pop('execution')
    elif mutation == 'execution_nonobject': doc['execution'] = []
    elif mutation == 'input_mutation': doc['execution']['input_unchanged'] = False
    elif mutation == 'method_hash':
        key = next(iter(doc['execution']['method_sha256']))
        doc['execution']['method_sha256'][key] = '0' * 64
    elif mutation == 'source_hash': doc['execution']['source_manifest_sha256'] = '0' * 64
    elif mutation == 'output_hash': doc['output_rgba_sha256'] = '0' * 64
    elif mutation == 'input_hash': doc['input_rgba_sha256']['input'] = '0' * 64
    elif mutation == 'missing_raw': doc.pop('raw_rgba')
    else: doc['version'] = True
    changed = store.put_json(doc)
    before = _blobs(store)
    with pytest.raises(ValidationError):
        services.invoke_parity(store, 'to_sequence', {'receipt': changed, 'duration': [1, 7]})
    assert _blobs(store) == before


def test_arbitrary_manifest_stamped_output_is_not_a_pixel_execution(services, store, raster):
    from sprite_workbench import parity_pixels
    fake = store.put_json({'kind': 'original-pixel-method', 'version': 1,
        'operation': 'invented_server_generator', 'output_raster': raster,
        'output_rgba_sha256': digest(store.get_raster(raster).tobytes()),
        'execution': {'source_manifest_sha256': parity_pixels._MANIFEST_SHA}})
    before = _blobs(store)
    with pytest.raises(ValidationError):
        services.invoke_parity(store, 'to_sequence', {'receipt': fake, 'duration': [1, 7]})
    assert _blobs(store) == before


@pytest.mark.parametrize('operation', ['serialize', 'decode', 'place', 'mask', 'reference_palette'])
def test_output_sequence_cold_closure_preserves_all_input_and_raw_bytes(services, store, raster, tmp_path, operation):
    from sprite_workbench.export import export_sequence, import_editable, _artifact_closure
    requests = {'serialize': {'raster': raster}, 'reference_palette': {'raster': raster},
                'mask': {'mask': raster, 'art': raster, 'fill_background': True},
                'place': {'source': raster, 'destination': raster, 'preserve_mask': raster}}
    if operation == 'decode':
        data = BytesIO()
        Image.fromarray(store.get_raster(raster)).save(data, format='PNG')
        requests[operation] = {'media': store.put_bytes(data.getvalue()), 'width': 1, 'height': 1}
    receipt = services.invoke_parity(store, 'pixels', {'operation': operation, 'request': requests[operation]})
    converted = services.invoke_parity(store, 'to_sequence', {'receipt': receipt['receipt'], 'duration': [1, 7]})
    before, arrays = load_sequence(store, converted['sequence'])
    assert before['frames'][0]['duration'] == [1, 7] and before['loop'] is False
    closure = _artifact_closure(store, converted['sequence'])
    assert receipt['receipt'] in closure and receipt['output_raster'] in closure
    for value in requests[operation].values():
        if isinstance(value, str) and len(value) == 64: assert value in closure
    if 'raw_rgba' in receipt: assert receipt['raw_rgba'] in closure
    export_sequence(store, converted['sequence'], tmp_path / 'export', ['editable'])
    fresh = Store(tmp_path / 'cold')
    assert import_editable(fresh, tmp_path / 'export/editable') == converted['sequence']
    for ident in closure: assert fresh.get_bytes(ident) == store.get_bytes(ident)
    cold, restored = load_sequence(fresh, converted['sequence'])
    assert cold == before
    np.testing.assert_array_equal(restored[0], arrays[0])


def test_cli_dispatches_parity_catalog_and_rejects_extra_fields(tmp_path):
    request = tmp_path / 'request.json'
    request.write_text('{}')
    command = [sys.executable, '-m', 'sprite_workbench', '--workspace', str(tmp_path / 'store'),
               'parity', 'catalog', str(request)]
    result = subprocess.run(command, text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload.get('whole_system_parity') is False
    request.write_text('{"extra":true}')
    invalid = subprocess.run(command, text=True, capture_output=True, timeout=20)
    assert invalid.returncode != 0


def test_jsonl_classification_validation_and_no_vendor_fallback(store, tmp_path):
    from sprite_workbench.channel import serve
    rows = [{'id': 1, 'method': 'system.capabilities'},
            {'id': 2, 'method': 'local.parity.catalog', 'params': {}},
            {'id': 3, 'method': 'local.parity.catalog', 'params': {'extra': True}},
            {'id': 4, 'method': 'public:POST:/animate-pixminimax', 'params': {}},
            {'id': 5, 'method': 'system.ping'}]
    source = StringIO(''.join(json.dumps(r) + '\n' for r in rows)); sink = StringIO()
    serve(store, base_dir=tmp_path, result_ref='input.sequence', source=source, sink=sink)
    messages = [json.loads(s) for s in sink.getvalue().splitlines()]
    assert messages[0]['provider_forwarding'] is False
    results = {m['id']: m for m in messages[1:]}
    capabilities = results[1]['result']
    # The registry exposes all local entries as records; do not infer a provider binding.
    if isinstance(capabilities, dict): capabilities = capabilities.get('capabilities', capabilities.get('entries', []))
    parity = {item['id']: item for item in capabilities if item['id'].startswith('local.parity.')}
    assert len(parity) == 6
    assert all(item['provider_forwarding'] is False and item['vendor_equivalence'] is False
               for item in parity.values())
    for name in ['catalog', 'palette', 'pixels', 'footprints']:
        item = parity['local.parity.' + name]
        assert item['local_classification'] == 'deterministic-source'
        assert item['provider_forwarding'] is False
    assert results[2]['status'] == 'completed'
    assert results[2]['result']['whole_system_parity'] is False
    assert results[3]['status'] == results[4]['status'] == 'validation_error'
    assert results[5]['result']['alive'] is True


def test_actual_http_local_surface_has_no_provider_fallback(store, tmp_path):
    from sprite_workbench.web_server import ControlServer
    server = ControlServer(store, base_dir=tmp_path / 'files', port=0, workers=1)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        def post(method, params):
            request = Request(server.url + '/api/invoke',
                json.dumps({'method': method, 'params': params}).encode(),
                {'X-Workbench-Token': server.token, 'Content-Type': 'application/json'})
            try:
                with urlopen(request, timeout=10) as response: return response.status, json.load(response)
            except HTTPError as error: return error.code, json.load(error)
        code, result = post('local.parity.catalog', {})
        assert code == 200 and result['result']['whole_system_parity'] is False
        code, result = post('local.parity.catalog', {'extra': True})
        assert code == 400 and result['status'] == 'validation_error'
        code, result = post('public:POST:/animate-pixminimax', {})
        assert code == 400 and result['status'] == 'unsupported'
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
        assert not thread.is_alive()


def test_source_paint_footprint_survives_history_export_cold_restore(services, store, tmp_path):
    from sprite_workbench.construction_services import invoke_construction
    from sprite_workbench import construction
    from sprite_workbench.export import export_sequence, import_editable, _artifact_closure
    art = np.zeros((12, 12, 4), dtype=np.uint8)
    art[0, 0] = [255, 255, 255, 255]
    source = save_sequence(store, [art], durations=[[1, 12]])
    project = invoke_construction(store, 'from_sequence', {'sequence': source, 'animation_id': 'still'})
    raw = construction.load_project(store, project['project'])
    history = invoke_construction(store, 'history', {'project': project['project']})
    command = {'method': 'ellipse-outline', 'pos': [3, 3], 'size': [4, 4]}
    painted = services.invoke_parity(store, 'paint', {'history': history['history'],
        'cel_id': next(iter(raw['cels'])), 'command': command, 'palette_index': 1})
    footprint = painted['footprint']
    original = store.get_json(footprint)
    assert original['results'] and original['source_provenance']
    rendered = invoke_construction(store, 'render', {'project': painted['project'],
        'history': painted['history'], 'animation_id': 'still'})
    closure = _artifact_closure(store, rendered['sequence'])
    assert footprint in closure, 'Source footprint evidence must remain reachable from painted history'
    export_sequence(store, rendered['sequence'], tmp_path / 'paint-export', ['editable'])
    fresh = Store(tmp_path / 'paint-cold')
    assert import_editable(fresh, tmp_path / 'paint-export/editable') == rendered['sequence']
    assert fresh.get_json(footprint) == original
    assert fresh.get_bytes(painted['history']) == store.get_bytes(painted['history'])
    construction.load_history(fresh, painted['history'])
    undone = invoke_construction(fresh, 'undo', {'history': painted['history']})
    assert undone['project'] == project['project']


def test_pipeline_resolves_source_receipt_without_provider_fallback(store, raster, tmp_path):
    from sprite_workbench.pipeline import execute_plan
    from sprite_workbench.export import import_editable
    plan = {'version': 1, 'steps': [
        {'id': 'pixel', 'action': 'parity', 'method': 'pixels',
         'request': {'operation': 'serialize', 'request': {'raster': raster}}},
        {'id': 'still', 'action': 'parity', 'method': 'to_sequence',
         'request': {'receipt': {'ref': 'pixel.receipt'}, 'duration': [2, 9]}},
        {'id': 'export', 'action': 'export', 'sequence': {'ref': 'still.sequence'},
         'directory': 'pipeline-export', 'formats': ['editable']},
    ]}
    result = execute_plan(store, plan, base_dir=tmp_path)
    assert result['status'] == 'completed', result
    sequence = result['results']['still']['sequence']
    assert load_sequence(store, sequence)[0]['frames'][0]['duration'] == [2, 9]
    fresh = Store(tmp_path / 'pipeline-cold')
    assert import_editable(fresh, tmp_path / 'pipeline-export/editable') == sequence
    assert fresh.get_bytes(result['results']['pixel']['receipt']) == store.get_bytes(result['results']['pixel']['receipt'])


@pytest.mark.parametrize('mutation', ['command_controls', 'points_hash', 'source_provenance',
                                      'receipt_bool', 'extra_entry', 'nonobject_artifact'])
def test_painted_history_rejects_altered_source_evidence(services, store, mutation):
    from sprite_workbench import construction
    from sprite_workbench.construction_services import invoke_construction
    art = np.zeros((12, 12, 4), dtype=np.uint8); art[0, 0] = [255, 255, 255, 255]
    seq = save_sequence(store, [art], durations=[[1, 12]])
    saved = invoke_construction(store, 'from_sequence', {'sequence': seq, 'animation_id': 'still'})
    project = construction.load_project(store, saved['project'])
    initial = invoke_construction(store, 'history', {'project': saved['project']})
    painted = services.invoke_parity(store, 'paint', {'history': initial['history'],
        'cel_id': next(iter(project['cels'])), 'palette_index': 1,
        'command': {'method': 'ellipse-outline', 'pos': [3, 3], 'size': [4, 4]}})
    history = deepcopy(store.get_json(painted['history']))
    footprint = deepcopy(store.get_json(painted['footprint']))
    if mutation == 'command_controls': footprint['results'][0]['command']['pos'] = [4, 4]
    elif mutation == 'points_hash': footprint['results'][0]['ordered_points_sha256'] = '0' * 64
    elif mutation == 'source_provenance': footprint['source_provenance']['source_sha256'] = '0' * 64
    elif mutation == 'receipt_bool': history['source_evidence'][0]['receipt_index'] = True
    elif mutation == 'extra_entry': history['source_evidence'][0]['extra'] = True
    else: footprint = []
    history['source_evidence'][0]['artifact'] = (store.put_json(footprint) if isinstance(footprint, dict)
        else store.put_bytes(json.dumps(footprint).encode()))
    forged = store.put_json(history)
    with pytest.raises(ValidationError): construction.load_history(store, forged)
