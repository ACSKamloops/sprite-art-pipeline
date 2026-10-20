"""No real credentials or transport: supplied PNGs and fake HTTP only."""
import base64
import importlib.util
from http.client import IncompleteRead
import io
import json
from pathlib import Path
import sys
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from PIL import Image
import pytest

SCRIPTS = Path(__file__).parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location('prepared_probe', SCRIPTS / 'probe_pixellab_prepared.py')
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def image(size=(4, 4)):
    data = io.BytesIO()
    Image.new('RGBA', size, (31, 72, 103, 255)).save(data, format='PNG')
    return {'type': 'base64', 'format': 'png', 'base64': 'data:image/png;base64,' + base64.b64encode(data.getvalue()).decode()}


def prepare(root, endpoint='reduce-colors', count=2):
    rows = []
    for i in range(count):
        run = root / f'case-{i}'
        run.mkdir()
        payload = {'images': [image(), image()], 'num_colors': 4} if endpoint == 'reduce-colors' else {
            'image': image(), 'image_size': {'width': 4, 'height': 4}}
        probe.capture.write_json(run / 'request.json', payload)
        wire = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
        rows.append({'variant': run.name, 'request_sha256': probe.digest((run / 'request.json').read_bytes()),
                     'compact_http_body_sha256': probe.digest(wire)})
    plan = {'endpoint': 'https://api.pixellab.ai/v2/' + endpoint, 'max_posts': count, 'requests': rows}
    probe.capture.write_json(root / 'PLAN.json', plan)
    return probe.digest((root / 'PLAN.json').read_bytes())


class Response:
    code = 200
    headers = {'Content-Type': 'application/json', 'Set-Cookie': 'must-not-save'}

    def __init__(self, payload=None, raw=None, failure=None):
        self.raw = json.dumps(payload).encode() if raw is None else raw
        self.failure = failure

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def read(self, limit):
        if self.failure:
            raise self.failure
        return self.raw[:limit]


@pytest.fixture
def mocked():
    with patch.object(probe.capture, 'credential', return_value='fake-SENSITIVE-token') as cred, \
            patch.object(probe.request, 'build_opener') as transport:
        yield cred, transport


def set_response(transport, result):
    transport.return_value.open.return_value = Response(result)


@pytest.mark.parametrize('change', ['plan', 'request', 'wire', 'route', 'duplicate', 'unsafe', 'slots'])
def test_all_preflight_before_credentials_and_network(tmp_path, mocked, change):
    cred, transport = mocked
    seal = prepare(tmp_path)
    plan = json.loads((tmp_path / 'PLAN.json').read_text())
    if change == 'plan':
        (tmp_path / 'PLAN.json').write_text('{}')
    elif change == 'request':  # Even an unselected slot is validated before auth.
        (tmp_path / 'case-1/request.json').write_text('{}')
    elif change == 'wire':
        (tmp_path / 'case-1/request-wire.json').write_text('{}')
    else:
        if change == 'route':
            plan['endpoint'] = 'https://api.pixellab.ai.evil.test/v2/reduce-colors'
        elif change == 'duplicate':
            plan['requests'][1]['variant'] = 'case-0'
        elif change == 'unsafe':
            plan['requests'][1]['variant'] = '../outside'
        elif change == 'slots':
            plan['max_posts'] = 13
        probe.capture.write_json(tmp_path / 'PLAN.json', plan)
        seal = probe.digest((tmp_path / 'PLAN.json').read_bytes())
    with pytest.raises(ValueError):
        probe.submit(tmp_path, 'case-0', seal)
    cred.assert_not_called()
    transport.assert_not_called()
    assert not (tmp_path / 'case-0/.submission.lock').exists()


def test_valid_reducer_saved_exact_pngs_and_actual_sanitized_har(tmp_path, mocked):
    cred, transport = mocked
    seal = prepare(tmp_path)
    body = {'images': [image(), image()], 'palette': image((4, 1)), 'usage': {'usd': 0.01}}
    set_response(transport, body)
    state = probe.submit(tmp_path, 'case-0', seal)
    assert state['status'] == 'completed'
    run = tmp_path / 'case-0'
    assert (run / 'output-00.png').read_bytes() == probe.png(body['images'][0])[0]
    assert (run / 'output-01.png').exists() and (run / 'palette.png').exists()
    entry = json.loads((run / 'network.har').read_text())['log']['entries'][0]
    assert entry['_response_body_sha256_scope'] == 'full'
    assert entry['_request_body_sha256'] == json.loads((tmp_path / 'PLAN.json').read_text())['requests'][0]['compact_http_body_sha256']
    assert entry['request']['cookies'] == entry['response']['cookies'] == []
    assert [h['name'] for h in entry['request']['headers']] == ['Content-Type']
    assert 'fake-SENSITIVE-token' not in (run / 'network.har').read_text()
    assert 'must-not-save' not in (run / 'network.har').read_text()
    assert all(v == -1 for v in entry['timings'].values())
    assert transport.return_value.open.call_args.kwargs == {'timeout': 60}
    assert transport.call_args.args == (probe.capture.NoRedirect,)
    with pytest.raises(FileExistsError):
        probe.submit(tmp_path, 'case-0', seal)
    assert cred.call_count == transport.return_value.open.call_count == 1


def test_exact_wire_file_is_used(tmp_path, mocked):
    _, transport = mocked
    prepare(tmp_path, count=1)
    run = tmp_path / 'case-0'
    wire = (run / 'request.json').read_bytes()  # Whitespace differs from compact form.
    (run / 'request-wire.json').write_bytes(wire)
    plan = json.loads((tmp_path / 'PLAN.json').read_text())
    case = plan['requests'][0]
    del case['compact_http_body_sha256']
    case['wire_sha256'] = probe.digest(wire)
    probe.capture.write_json(tmp_path / 'PLAN.json', plan)
    seal = probe.digest((tmp_path / 'PLAN.json').read_bytes())
    set_response(transport, {'images': [image(), image()], 'palette': image((4, 1))})
    probe.submit(tmp_path, 'case-0', seal)
    assert transport.return_value.open.call_args.args[0].data == wire


def test_cutout_single_image(tmp_path, mocked):
    _, transport = mocked
    seal = prepare(tmp_path, 'remove-background')
    set_response(transport, {'image': image()})
    assert probe.submit(tmp_path, 'case-0', seal)['status'] == 'completed'
    assert (tmp_path / 'case-0/output-00.png').exists()
    assert not (tmp_path / 'case-0/palette.png').exists()


def test_json_escaped_token_scrubbed_in_keys_values_before_persistence(tmp_path, mocked):
    _, transport = mocked
    seal = prepare(tmp_path)
    raw = b'{"fake-SENSITIVE-\\u0074oken":"fake-SENSITIVE-\\u0074oken","usage":{"echo":"fake-SENSITIVE-token"}}'
    transport.return_value.open.return_value = Response(raw=raw)
    assert probe.submit(tmp_path, 'case-0', seal)['status'] == 'response-invalid'
    run = tmp_path / 'case-0'
    for name in ['network.har', 'response.json', 'state.json']:
        text = (run / name).read_text()
        assert 'fake-SENSITIVE-token' not in text and '\\u0074oken' not in text
    entry = json.loads((run / 'network.har').read_text())['log']['entries'][0]
    assert entry['response']['content']['text_redacted']
    assert entry['_response_body_sha256_before_scrub'] == probe.digest(raw)


@pytest.mark.parametrize('body', [{}, {'images': [image()], 'palette': image((4, 1))},
    {'images': [image((5, 4)), image()], 'palette': image((4, 1))},
    {'images': [image(), image()], 'palette': image((4, 2))},
    {'images': [{'base64': '%%%%'}, image()], 'palette': image((4, 1))}])
def test_malformed_200_retained_without_any_png(tmp_path, mocked, body):
    _, transport = mocked
    seal = prepare(tmp_path)
    set_response(transport, body)
    assert probe.submit(tmp_path, 'case-0', seal)['status'] == 'response-invalid'
    assert (tmp_path / 'case-0/response.json').exists()
    assert not list((tmp_path / 'case-0').glob('*.png'))


@pytest.mark.parametrize('failure', [URLError('ambiguous'), IncompleteRead(b'{"partial":', 50)])
def test_transport_ambiguity_records_prefix_and_cannot_repeat(tmp_path, mocked, failure):
    cred, transport = mocked
    seal = prepare(tmp_path)
    if isinstance(failure, IncompleteRead):
        transport.return_value.open.return_value = Response(failure=failure)
    else:
        transport.return_value.open.side_effect = failure
    state = probe.submit(tmp_path, 'case-0', seal)
    assert state['status'] == 'failed-or-ambiguous'
    assert state['response_body_sha256_scope'] == 'prefix'
    assert (tmp_path / 'case-0/network.har').exists()
    with pytest.raises(FileExistsError):
        probe.submit(tmp_path, 'case-0', seal)
    assert cred.call_count == transport.return_value.open.call_count == 1


def test_bounded_read_marks_prefix(tmp_path, mocked):
    _, transport = mocked
    seal = prepare(tmp_path)
    transport.return_value.open.return_value = Response(raw=b'x' * (probe.MAX_BODY + 1))
    state = probe.submit(tmp_path, 'case-0', seal)
    assert state['transport_failure'] == 'BodyLimitExceeded'
    entry = json.loads((tmp_path / 'case-0/network.har').read_text())['log']['entries'][0]
    assert entry['_response_prefix_bytes'] == probe.MAX_BODY
    assert entry['_response_bytes_observed'] == probe.MAX_BODY + 1
    assert entry['_response_body_sha256_scope'] == 'prefix'


def test_http_error_json_retained(tmp_path, mocked):
    _, transport = mocked
    seal = prepare(tmp_path)
    raw = b'{"detail":"quota test double"}'
    transport.return_value.open.side_effect = HTTPError('https://api.pixellab.ai/v2/reduce-colors',
        402, 'payment', {'Content-Type': 'application/json'}, io.BytesIO(raw))
    state = probe.submit(tmp_path, 'case-0', seal)
    assert state['http_status'] == 402 and state['status'] == 'failed-or-ambiguous'
    entry = json.loads((tmp_path / 'case-0/network.har').read_text())['log']['entries'][0]
    assert entry['response']['content']['text'] == raw.decode()
    assert entry['_response_body_sha256_scope'] == 'full'


@pytest.mark.parametrize('name', ['state.json', 'network.har', 'response.json', 'output-00.png', 'palette.png'])
def test_existing_evidence_without_lock_is_preserved(tmp_path, mocked, name):
    cred, transport = mocked
    seal = prepare(tmp_path)
    target = tmp_path / 'case-0' / name
    target.write_bytes(b'original evidence')
    with pytest.raises(FileExistsError):
        probe.submit(tmp_path, 'case-0', seal)
    assert target.read_bytes() == b'original evidence'
    assert not (tmp_path / 'case-0/.submission.lock').exists()
    cred.assert_not_called()
    transport.assert_not_called()


def test_duplicate_json_keys_cannot_hide_token_echo(tmp_path, mocked):
    _, transport = mocked
    seal = prepare(tmp_path)
    raw = b'{"duplicate":"fake-SENSITIVE-\\u0074oken","duplicate":"safe"}'
    transport.return_value.open.return_value = Response(raw=raw)
    assert probe.submit(tmp_path, 'case-0', seal)['status'] == 'response-invalid'
    har = (tmp_path / 'case-0/network.har').read_text()
    assert 'fake-SENSITIVE' not in har
    entry = json.loads(har)['log']['entries'][0]
    assert entry['response']['content']['text'] == ''
    assert entry['_response_body_sha256_before_scrub'] == probe.digest(raw)
