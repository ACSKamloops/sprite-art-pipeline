"""Offline controls for a finite paid characterization, using fake credentials."""
import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

import numpy as np
from PIL import Image
import pytest


@pytest.fixture
def probe(monkeypatch):
    scripts = Path(__file__).parents[1] / 'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location('reducer_probe', scripts / 'probe_pixellab_color_reducer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def prepared(probe, tmp_path):
    root = tmp_path / 'cases'
    probe.prepare(root)
    return root


def test_repeat_is_byte_identical_and_cube_is_complete(prepared):
    assert (prepared / 'fixed-none/request.json').read_bytes() == (prepared / 'fixed-repeat/request.json').read_bytes()
    image = np.array(Image.open(prepared / 'inputs/rgb-cube-gray.png'))
    assert image.shape == (32, 256, 4)
    assert len(np.unique(image[:16, :, :3].reshape(-1, 3), axis=0)) == 16**3
    assert np.array_equal(image[16, :, 0], np.arange(256))


def test_changed_request_rejected_before_credentials_or_network(probe, prepared):
    (prepared / 'fixed-none/request.json').write_text('{}')
    with patch.object(probe.capture, 'credential') as credential, patch.object(probe.request, 'build_opener') as opener:
        with pytest.raises(ValueError, match='changed'):
            probe.submit(prepared, 'fixed-none')
        credential.assert_not_called()
        opener.assert_not_called()


def test_ambiguous_transport_is_retained_and_never_retried(probe, prepared):
    with patch.object(probe.capture, 'credential', return_value='FAKE'), patch.object(probe.request, 'build_opener') as opener:
        opener.return_value.open.side_effect = URLError('simulated')
        assert probe.submit(prepared, 'fixed-none')['status'] == 'failed-or-ambiguous'
        with pytest.raises(FileExistsError):
            probe.submit(prepared, 'fixed-none')
        assert opener.return_value.open.call_count == 1
    assert (prepared / 'fixed-none/network.har').exists()


def test_http_response_capture_omits_auth_and_redacts_escaped_echo(probe, prepared):
    class Response(io.BytesIO):
        code = 200
        headers = {'Content-Type': 'application/json'}
    response = Response(b'{"images":[],"error":"\\u0046AKE"}')
    with patch.object(probe.capture, 'credential', return_value='FAKE'), patch.object(probe.request, 'build_opener') as opener:
        opener.return_value.open.return_value = response
        state = probe.submit(prepared, 'fixed-none')
        assert state['status'] == 'response-invalid'
    har = json.loads((prepared / 'fixed-none/network.har').read_text())['log']['entries'][0]
    assert not any(h['name'].lower() == 'authorization' for h in har['request']['headers'])
    assert har['response']['content']['text_redacted']
    assert 'FAKE' not in json.dumps(har)
