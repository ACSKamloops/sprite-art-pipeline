import io
import json
from pathlib import Path
import select
import subprocess
import sys

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, save_sequence
from sprite_workbench.channel import serve
from sprite_workbench.replication import compare_sequences, replay, verify_run
from sprite_workbench.replay_state import run_flow, FLOW_IDS


@pytest.mark.parametrize('flow', FLOW_IDS)
def test_callable_state_recipes(flow, tmp_path):
    result = run_flow(flow, Store(tmp_path / 'store'), tmp_path / flow)
    assert result['checks'] and all(c['passed'] is True for c in result['checks'])
    assert result['artifacts']['sequence']
    assert result['limitations']


def test_comparison_detects_hidden_rgb_clock_and_count_changes(tmp_path):
    store = Store(tmp_path / 'store')
    a = np.zeros((3, 5, 4), np.uint8)
    a[1, 1] = [100, 20, 30, 255]
    b = a.copy(); b[0, 0, 0] = 9
    left = save_sequence(store, [a, a], durations=[[1, 10], [2, 10]])
    right = save_sequence(store, [b], durations=[[2, 10]])
    result = compare_sequences(store.path, left, store.path, right, tmp_path / 'comparison')
    assert not result['exact_sequence_match']
    assert result['frames'][0]['rgba_changed_pixels'] == 1
    assert result['frames'][0]['alpha_changed_pixels'] == 0
    assert not result['frames'][0]['duration_equal']
    assert not result['frames'][1]['candidate_present']
    assert verify_run(tmp_path / 'comparison')['status'] == 'completed'
    target = tmp_path / 'comparison/baseline/frames/frame-0000.png'
    target.write_bytes(target.read_bytes() + b'changed')
    assert 'baseline/frames/frame-0000.png' in verify_run(tmp_path / 'comparison')['changed']


def test_replay_integrity_existing_output_and_traversal(tmp_path):
    out = tmp_path / 'run'
    result = replay(out, ['F05'])
    assert result['status'] == 'completed'
    assert not result['whole_vendor_replication_complete']
    assert verify_run(out)['status'] == 'completed'
    with pytest.raises(ValidationError):
        replay(out, ['F05'])
    manifest = json.loads((out / 'MANIFEST.json').read_text())
    manifest['files'].append({'file': '../escape', 'bytes': 0, 'sha256': '0' * 64})
    (out / 'MANIFEST.json').write_text(json.dumps(manifest))
    with pytest.raises(ValidationError):
        verify_run(out)


def test_channel_bad_message_does_not_break_next_request(tmp_path):
    source = io.StringIO('not json\n' + json.dumps({'id': 1, 'method': 'public:POST:/generate-image-v2'}) + '\n'
                         + json.dumps({'id': 2, 'method': 'system.ping'}) + '\n')
    sink = io.StringIO()
    serve(Store(tmp_path / 'store'), base_dir=tmp_path, result_ref='import.sequence', source=source, sink=sink)
    messages = [json.loads(line) for line in sink.getvalue().splitlines()]
    assert messages[0]['event'] == 'ready'
    assert messages[1]['status'] == messages[2]['status'] == 'validation_error'
    assert messages[3] == {'id': 2, 'status': 'completed', 'result': {'alive': True}}


def test_geometry_recipe_preserves_dangling_output_symlink(tmp_path):
    from sprite_workbench.replay_geometry import run_flow as geometry_flow
    link = tmp_path / 'link'
    target = tmp_path / 'must-not-create'
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValidationError):
        geometry_flow('F02', Store(tmp_path / 'store'), link)
    assert link.is_symlink() and not target.exists()


def test_real_channel_process_jobs_and_library_persist(tmp_path):
    from PIL import Image
    Image.fromarray(np.full((3, 5, 4), [31, 67, 101, 255], np.uint8)).save(tmp_path / 'source.png')
    process = subprocess.Popen([sys.executable, '-m', 'sprite_workbench', '--workspace', str(tmp_path / 'store'),
                                'channel', '--base-dir', str(tmp_path), '--result-ref', 'source.sequence'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def receive():
        assert select.select([process.stdout], [], [], 10)[0], 'Channel response timed out'
        line = process.stdout.readline()
        assert line, 'Channel exited unexpectedly'
        return json.loads(line)
    def send(i, method, params=None):
        process.stdin.write(json.dumps({'id': i, 'method': method, 'params': params or {}}) + '\n')
        process.stdin.flush()
        result = receive()
        assert result['id'] == i and result['status'] == 'completed', result
        return result['result']
    try:
        assert receive()['event'] == 'ready'
        names = {r['id'] for r in send(1, 'system.capabilities')}
        assert {'local.jobs.submit', 'local.library.promote'} <= names
        plan = {'version': 1, 'steps': [{'id': 'source', 'action': 'import', 'path': 'source.png'}]}
        job_id = send(2, 'local.jobs.submit', {'handler': 'local.pipeline', 'request': {'plan': plan}})
        result = send(3, 'local.jobs.wait', {'job_id': job_id})
        assert result['status'] == 'completed'
        candidate = send(4, 'local.library.create_candidate', {'artifact_id': result['artifact'], 'source_id': 'supplied'})
        entity = send(5, 'local.library.promote', {'candidate_ids': [candidate], 'name': 'local-test'})
        send(6, 'system.shutdown')
        process.communicate(timeout=10)
        assert process.returncode == 0
        from sprite_workbench.library import Library
        assert Library(Store(tmp_path / 'store')).get(entity)['document']['name'] == 'local-test'
    finally:
        if process.poll() is None:
            process.terminate(); process.communicate(timeout=10)
