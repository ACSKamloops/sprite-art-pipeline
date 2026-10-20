import io
import json
import subprocess
import sys

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence, save_sequence
from sprite_workbench.construction_services import invoke_construction, bind_construction, SCHEMAS
from sprite_workbench.capabilities import CapabilityRegistry
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.pipeline import execute_plan


def supplied(store):
    a = np.zeros((3, 5, 4), np.uint8)
    a[1, 1] = [31, 67, 101, 255]
    b = a.copy(); b[1, 3] = [170, 40, 10, 255]
    return save_sequence(store, [a, b], durations=[[1, 60], [2, 60]],
                         pivots=[[2, 2], [2, 2]], directions=['east', 'east'], loop=True)


def test_edit_history_render_portable_closure_and_fresh_replay(tmp_path):
    from sprite_workbench.construction import load_project, load_history
    store = Store(tmp_path / 'store')
    source = supplied(store)
    call = lambda m, r: invoke_construction(store, m, r, base_dir=tmp_path)
    project = call('from_sequence', {'sequence': source, 'animation_id': 'walk'})
    raw = load_project(store, project['project'])
    history = call('history', {'project': project['project']})
    cel = next(iter(raw['cels']))
    tx = {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': project['project_hash'],
          'reason': 'single pixel correction', 'operations': [{'op': 'paint', 'cel_id': cel,
                                                               'points': [[0, 0, 1]]}]}
    edited = call('edit', {'history': history['history'], 'transaction': tx})
    assert edited['project_hash'] != project['project_hash']
    undone = call('undo', {'history': edited['history']})
    assert undone['project'] == project['project']
    redone = call('redo', {'history': undone['history']})
    assert redone['project'] == edited['project']
    result = call('render', {'project': redone['project'], 'history': redone['history'], 'animation_id': 'walk'})
    seq, arrays = load_sequence(store, result['sequence'])
    assert seq['frames'][0]['duration'] == [1, 60]
    assert seq['frames'][1]['duration'] == [1, 30]
    assert seq['frames'][0]['pivot'] == [2, 2] and seq['frames'][0]['direction'] == 'east'
    assert arrays[0][0, 0].tolist() == raw['palette'][1]
    export_sequence(store, result['sequence'], tmp_path / 'export', ['editable'])
    fresh = Store(tmp_path / 'fresh')
    assert import_editable(fresh, tmp_path / 'export/editable') == result['sequence']
    assert fresh.get_bytes(source) == store.get_bytes(source)
    assert load_project(fresh, edited['project']) == load_project(store, edited['project'])
    load_history(fresh, redone['history'])
    restored = invoke_construction(fresh, 'undo', {'history': redone['history']})
    assert restored['project'] == project['project']
    with pytest.raises(ValidationError, match='History'):
        call('render', {'project': project['project'], 'history': redone['history'], 'animation_id': 'walk'})
    corrupt = store.get_json(redone['history']); corrupt['journal']['cursor'] = 0
    with pytest.raises(ValidationError):
        call('render', {'project': redone['project'], 'history': store.put_json(corrupt), 'animation_id': 'walk'})


def test_schema_rejects_unknown_method_fields_and_file_preservation(tmp_path):
    store = Store(tmp_path / 'store')
    registry = CapabilityRegistry(); bind_construction(registry, store, base_dir=tmp_path)
    assert len(registry.list('local')) == len(SCHEMAS)
    assert registry.snapshot['implemented_vendor_handlers'] == 0
    project = registry.invoke('local.construction.from_sequence', {'sequence': supplied(store)})
    with pytest.raises(ValidationError):
        registry.invoke('local.construction.get', {'project': project['project'], 'include_document': True})
    summary = registry.invoke('local.construction.get', {'project': project['project']})
    assert 'document' not in summary and summary['palette_entries'] == 3
    assert summary['animation_ids'] == ['clip'] and summary['animations'] == 1
    request = {'project': project['project'], 'path': 'source.json'}
    saved = registry.invoke('local.construction.write', request)
    assert saved['bytes'] > 0
    raw = (tmp_path / 'source.json').read_bytes()
    with pytest.raises(FileExistsError):
        registry.invoke('local.construction.write', request)
    assert (tmp_path / 'source.json').read_bytes() == raw
    target = tmp_path / 'no-write'; link = tmp_path / 'symlink.json'; link.symlink_to(target)
    with pytest.raises(FileExistsError):
        registry.invoke('local.construction.write', {**request, 'path': 'symlink.json'})
    assert link.is_symlink() and not target.exists()
    loaded = registry.invoke('local.construction.read', {'path': 'source.json'})
    # read imports the raw construction document; typed sequence lineage is
    # carried by editable bundles, not implied by arbitrary JSON provenance.
    assert loaded['project_hash'] == project['project_hash']
    (tmp_path / 'unsafe.json').write_text('{"bad":1e999}')
    with pytest.raises(ValidationError):
        registry.invoke('local.construction.read', {'path': 'unsafe.json'})


def test_declared_construction_plan_then_cli_and_jsonl(tmp_path):
    from sprite_workbench.channel import serve
    store = Store(tmp_path / 'store'); source = supplied(store)
    plan = {'version': 1, 'steps': [
        {'id': 'project', 'action': 'construction', 'method': 'from_sequence', 'request': {'sequence': source}},
        {'id': 'history', 'action': 'construction', 'method': 'history', 'request': {'project': {'ref': 'project.project'}}},
        {'id': 'render', 'action': 'construction', 'method': 'render', 'request': {
            'project': {'ref': 'project.project'}, 'history': {'ref': 'history.history'}, 'animation_id': 'clip'}},
        {'id': 'export', 'action': 'export', 'sequence': {'ref': 'render.sequence'}, 'directory': 'out', 'formats': ['editable']},
    ]}
    run = execute_plan(store, plan, base_dir=tmp_path)
    assert run['status'] == 'completed', run
    request = {'project': run['results']['project']['project']}
    (tmp_path / 'get.json').write_text(json.dumps(request))
    cli = subprocess.run([sys.executable, '-m', 'sprite_workbench', '--workspace', str(store.path),
                          'construct', 'get', str(tmp_path / 'get.json')], capture_output=True, text=True, timeout=20)
    assert cli.returncode == 0, cli.stderr + cli.stdout
    assert json.loads(cli.stdout)['project'] == request['project']
    messages = [
        {'id': 1, 'method': 'local.construction.get', 'params': {**request, 'extra': True}},
        {'id': 2, 'method': 'local.construction.get', 'params': request},
        {'id': 3, 'method': 'system.capabilities'},
    ]
    sink = io.StringIO()
    serve(store, base_dir=tmp_path, result_ref='render.sequence',
          source=io.StringIO(''.join(json.dumps(m) + '\n' for m in messages)), sink=sink)
    replies = [json.loads(line) for line in sink.getvalue().splitlines()]
    assert replies[1]['status'] == 'validation_error'
    assert replies[2]['result']['project'] == request['project']
    assert 'local.construction.ase_import' in {entry['id'] for entry in replies[3]['result']}
    assert all(not entry['vendor_equivalence'] for entry in replies[3]['result'])


def test_compact_get_does_not_dump_large_animation_metadata(tmp_path):
    from sprite_workbench.construction import load_project
    store = Store(tmp_path / 'store')
    result = invoke_construction(store, 'from_sequence', {'sequence': supplied(store)})
    document = load_project(store, result['project'])
    document['animations'][0]['id'] = 'x' * 10000
    document['animations'][0]['frames'] *= 1000
    saved = invoke_construction(store, 'save', {'document': document})
    summary = invoke_construction(store, 'get', {'project': saved['project']})
    assert summary['animations'] == 1 and summary['animation_ids_omitted'] == 1
    assert summary['animation_ids'] == [] and len(json.dumps(summary)) < 1024
