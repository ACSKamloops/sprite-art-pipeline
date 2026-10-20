"""Synthetic verifier regression fixtures: no service or REA execution evidence."""
import base64
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import pytest


@pytest.fixture
def verifier(monkeypatch):
    scripts = Path(__file__).parents[1] / 'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location('phase_verifier', scripts / 'verify_pixellab_probe_phase.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


@pytest.fixture
def fixture(verifier, tmp_path):
    probe = verifier.probe
    root = tmp_path / 'plan'
    run = root / 'case'
    run.mkdir(parents=True)
    buf = io.BytesIO()
    Image.new('RGBA', (1, 1), (12, 34, 56, 255)).save(buf, format='PNG')
    image = {'type': 'base64', 'format': 'png', 'base64': base64.b64encode(buf.getvalue()).decode()}
    payload = {'images': [image, image], 'num_colors': 2, 'dithering': 'none'}
    write(run / 'request.json', payload)
    wire = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
    write(root / 'PLAN.json', {'endpoint': 'https://api.pixellab.ai/v2/reduce-colors',
        'max_posts': 1, 'automatic_retries': 0, 'requests': [{'variant': 'case',
        'request_sha256': verifier.sha(run / 'request.json'), 'wire_sha256': probe.digest(wire)}]})
    plan_sha = verifier.sha(root / 'PLAN.json')
    response_value = {'images': [image, image], 'palette': image, 'n_colors': 1,
                      'usage': {'type': 'generations', 'generations': 0.1}}

    class Response(io.BytesIO):
        code = 200
        headers = {'Content-Type': 'application/json'}

    with patch.object(probe.capture, 'credential', return_value='FAKE-TEST-TOKEN'), \
            patch.object(probe.request, 'build_opener') as opener:
        opener.return_value.open.return_value = Response(json.dumps(response_value).encode())
        assert probe.submit(root, 'case', plan_sha)['status'] == 'completed'
        assert opener.return_value.open.call_count == 1
    har = verifier.read(run / 'network.har')
    # Deliberately synthetic adapter-shaped record. Not a real REA receipt.
    write(run / 'REA-EVIDENCE.json', {'operation': 'inspect_web_network_capture',
        'evidence_id': 'synthetic-unit-test', 'subject': {'local_path': str(run / 'network.har'),
        'digest': {'sha256': verifier.sha(run / 'network.har')}}, 'normalized_result': {
        'artifact': {'sha256': verifier.sha(run / 'network.har')}, 'total_records': 1,
        'records': [{'ordinal': 0, 'reported': deepcopy(har['log']['entries'][0])}]}})
    phase_path = tmp_path / 'PHASE.json'
    write(phase_path, {'plans': [{'path': str(root / 'PLAN.json'), 'sha256': plan_sha,
        'variants': ['case']}], 'max_new_post_attempts': 1, 'max_reported_generations_before_manual_audit': 1})
    return phase_path, run


def checked(verifier, phase_path):
    with patch.object(verifier.probe.capture, 'credential', side_effect=AssertionError('Auth forbidden')), \
            patch.object(verifier.probe.request, 'build_opener', side_effect=AssertionError('Network forbidden')):
        return verifier.verify(phase_path, verifier.sha(phase_path))


def test_valid_synthetic_bindings_need_no_credentials_or_network(verifier, fixture):
    phase_path, _ = fixture
    result = checked(verifier, phase_path)
    assert (result['cases_checked'], result['pngs_bound'], result['reported_generations']) == (1, 3, '0.1')


@pytest.mark.parametrize('change', ['png', 'har-body', 'rea-subject', 'rea-body',
                                  'auth-header', 'redacted-body', 'usage', 'duplicate-variant', 'repeat-group'])
def test_corruption_and_duplicate_counts_are_rejected(verifier, fixture, change):
    phase_path, run = fixture
    if change == 'png':
        with (run / 'output-00.png').open('ab') as file:
            file.write(b'changed')
    elif change in {'har-body', 'auth-header', 'redacted-body'}:
        path = run / 'network.har'
        value = verifier.read(path)
        entry = value['log']['entries'][0]
        if change == 'har-body':
            entry['response']['content']['text'] = '{}'
        elif change == 'auth-header':
            entry['request']['headers'].append({'name': 'Authorization', 'value': 'FAKE'})
        else:
            entry['response']['content']['text_redacted'] = True
        write(path, value)
    elif change in {'rea-subject', 'rea-body'}:
        path = run / 'REA-EVIDENCE.json'
        value = verifier.read(path)
        if change == 'rea-subject':
            value['subject']['digest']['sha256'] = '0' * 64
        else:
            value['normalized_result']['records'][0]['reported']['response']['content']['text'] = '{}'
        write(path, value)
    elif change == 'usage':
        path = run / 'state.json'
        value = verifier.read(path)
        value['usage']['generations'] = 0.2
        write(path, value)
    else:
        value = verifier.read(phase_path)
        value['max_new_post_attempts'] = 2
        if change == 'duplicate-variant':
            value['plans'][0]['variants'].append('case')
        else:
            value['plans'].append(deepcopy(value['plans'][0]))
        write(phase_path, value)
    with pytest.raises(ValueError):
        checked(verifier, phase_path)


def test_duplicate_json_keys_are_rejected(verifier, fixture):
    phase_path, run = fixture
    (run / 'response.json').write_text('{"images": [], "images": []}')
    with pytest.raises(ValueError, match='Duplicate JSON key'):
        checked(verifier, phase_path)
