"""Fake-token/network adapter tests and real local diagnostic video admission."""
import base64
from http.client import IncompleteRead
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from PIL import Image

from sprite_workbench import motion_provider as mp
from sprite_workbench.core import Store, ValidationError, canonical_json, digest


def png(color=(20, 40, 60, 128), size=(256, 256)):
    output = BytesIO(); Image.new('RGBA', size, color).save(output, format='PNG')
    return output.getvalue()


@pytest.fixture
def prepared(tmp_path):
    store = Store(tmp_path / 'store')
    packet = mp.prepare_packet(store, png(), ' literal motion\nwithout rewriting ')
    run = tmp_path / 'run'
    mp.write_prepared(store, packet['packet'], run)
    return store, packet['packet'], run


def test_exact_first_last_packet_preserves_png_bytes_and_literal_prompt(tmp_path):
    store = Store(tmp_path / 'store'); first = png(); last = png((80, 90, 10, 0))
    result = mp.prepare_packet(store, first, ' jump\nland ', last_png=last, duration=9, resolution='2K')
    doc, wire = mp.load_packet(store, result['packet']); body = json.loads(wire)
    assert body == {'model': 'MiniMax-H3', 'duration': 9, 'resolution': '2K', 'ratio': 'adaptive',
        'content': [{'type': 'text', 'text': ' jump\nland '},
            *[{'type': 'image_url', 'role': role, 'image_url': {'url': 'data:image/png;base64,'+base64.b64encode(raw).decode()}}
              for role, raw in [('first_frame', first), ('last_frame', last)]]]}
    assert doc['prompt_sha256'] == digest(b' jump\nland ') and doc['checkpoint'] is None
    assert [store.get_bytes(i['png']) for i in doc['inputs']] == [first, last]
    assert not any(k in body for k in ['seed', 'fps', 'no_background', 'enhance_prompt', 'frame_count'])


@pytest.mark.parametrize('options', [{'duration': True}, {'duration': 3}, {'duration': 16}, {'duration': 4.0},
    {'resolution': '480P'}, {'prompt': ''}, {'prompt': 'x' * 7001}, {'first_png': png(size=(255, 256))}])
def test_contract_refuses_invalid_controls_before_store_write(tmp_path, options):
    store = Store(tmp_path / 'store'); args = dict(first_png=png(), prompt='walk'); args.update(options)
    with pytest.raises(ValidationError):
        mp.prepare_packet(store, **args)
    assert not list((store.path / 'blobs').iterdir())


def test_authorization_and_tampered_wire_fail_before_credentials_or_network(prepared, monkeypatch):
    store, packet, run = prepared
    def forbidden():
        pytest.fail('Credential loader called before validation/authorization')
    monkeypatch.setattr(mp, '_capture', lambda *a: pytest.fail('Network called'))
    with pytest.raises(ValidationError, match='authorization'):
        mp.submit_prepared(store, packet, run, credential_loader=forbidden)
    (run / 'request.json').write_text('{}')
    with pytest.raises(ValidationError, match='prepared run'):
        mp.submit_prepared(store, packet, run, credential_loader=forbidden, authorized=True)
    assert not (store.path / 'motion-provider-claims').exists()


def test_no_duplicate_paid_call_even_across_new_run(prepared, monkeypatch, tmp_path):
    store, packet, run = prepared; calls = []
    def capture(*args):
        assert json.loads((run / 'state.json').read_text())['status'] == 'submission-attempted'
        assert json.loads((store.path / 'motion-provider-claims' / packet).read_text())['status'] == 'attempted'
        calls.append(args)
        return {'http_status': 200, 'ambiguous': False, 'truncated': False}, {'task_id': 'task-1'}, {}
    monkeypatch.setattr(mp, '_capture', capture)
    assert mp.submit_prepared(store, packet, run, credential_loader=lambda:'FAKE', authorized=True)['status'] == 'accepted'
    with pytest.raises(ValidationError, match='Already attempted'):
        mp.submit_prepared(store, packet, run, credential_loader=lambda:'FAKE', authorized=True)
    other = tmp_path / 'other'; mp.write_prepared(store, packet, other)
    with pytest.raises(ValidationError, match='already claimed'):
        mp.submit_prepared(store, packet, other, credential_loader=lambda:'FAKE', authorized=True)
    assert len(calls) == 1


class Response:
    code = 200
    def __init__(self, raw, fail=False): self.raw, self.fail = raw, fail
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, maximum):
        if self.fail: raise IncompleteRead(self.raw, 50)
        return self.raw[:maximum]


def fake_opener(monkeypatch, response, seen):
    class Opener:
        def open(self, req, timeout):
            seen.append(req)
            assert req.full_url.startswith(mp.API + '/v2/') and timeout == 60
            return response
    def build(*handlers):
        assert any(isinstance(h, mp.NoRedirect) for h in handlers)
        assert any(isinstance(h, mp.request.ProxyHandler) and h.proxies == {} for h in handlers)
        return Opener()
    monkeypatch.setattr(mp.request, 'build_opener', build)


def test_actual_producer_har_scrubs_escaped_token_keys_values_no_auth(prepared, monkeypatch):
    store, packet, run = prepared; seen = []; token = 'FAKE-SECRET'
    raw = b'{ "task_id":"task-2", "FAKE-\\u0053ECRET": ["FAKE-\\u0053ECRET"] }'
    fake_opener(monkeypatch, Response(raw), seen)
    result = mp.submit_prepared(store, packet, run, credential_loader=lambda:token, authorized=True)
    assert result['status'] == 'accepted' and len(seen) == 1
    assert seen[0].get_header('Authorization') == 'Bearer '+token  # Fake only; never persisted.
    captured = json.loads((run / 'network.har').read_text())['log']['entries'][0]
    assert captured['request']['headers'] == [] and captured['request']['cookies'] == []
    assert json.loads(captured['response']['content']['text'])['[REDACTED]'] == ['[REDACTED]']
    assert captured['_capture']['raw_body_sha256'] == digest(raw)
    assert captured['_capture']['text_redacted'] is True
    for path in run.rglob('*'):
        if path.is_file():
            assert token.encode() not in path.read_bytes() and b'FAKE-\\u0053ECRET' not in path.read_bytes()


def test_transport_ambiguity_retains_prefix_and_blocks_repeat(prepared, monkeypatch):
    store, packet, run = prepared; seen = []
    fake_opener(monkeypatch, Response(b'{"task_id":"maybe"', fail=True), seen)
    assert mp.submit_prepared(store, packet, run, credential_loader=lambda:'FAKE', authorized=True)['status'] == 'submission-ambiguous'
    response = json.loads((run / 'submit-response.json').read_text())
    assert response['transport']['raw_body_sha256_scope'] == 'prefix'
    assert response['transport']['raw_body_sha256'] == digest(b'{"task_id":"maybe"')
    with pytest.raises(ValidationError):
        mp.submit_prepared(store, packet, run, credential_loader=lambda:'FAKE', authorized=True)
    assert len(seen) == 1


def test_duplicate_json_echo_and_loader_exceptions_cannot_leak(prepared, monkeypatch):
    store, packet, run = prepared; seen = []; token = 'FAKE-SECRET'
    # A permissive parser would lose the first value and retain unsafe raw text.
    raw = b'{"echo":"FAKE-\\u0053ECRET","echo":"benign","task_id":"t1"}'
    fake_opener(monkeypatch, Response(raw), seen)
    mp.submit_prepared(store, packet, run, credential_loader=lambda:token, authorized=True)
    capture = (run/'network.har').read_text()
    assert token not in capture and 'FAKE-' not in capture and 'omitted' in capture
    assert json.loads((run/'submit-response.json').read_text())['body'] is None
    def broken_loader(): raise OSError(token)
    with pytest.raises(ValidationError, match='details withheld') as exc:
        mp._authorized(True, broken_loader)
    assert token not in str(exc.value)


def test_raw_json_preserved_without_redaction_and_oversize_is_prefix(monkeypatch):
    seen = []; raw = b'{ "task_id": "task-x" }\n'
    fake_opener(monkeypatch, Response(raw), seen)
    transport, body, entry = mp._capture('POST', mp.CREATE, b'{}', 'FAKE')
    assert entry['response']['content']['text'] == raw.decode() and transport['text_redacted'] is False
    monkeypatch.setattr(mp, 'MAX_RESPONSE', 10)
    transport, body, entry = mp._capture('POST', mp.CREATE, b'{}', 'FAKE')
    assert transport['truncated'] is True and transport['raw_body_sha256_scope'] == 'prefix'
    assert body is None
    assert 'omitted' in entry['response']['content']['text']


def test_route_rejection_and_no_redirect(monkeypatch):
    monkeypatch.setattr(mp.request, 'build_opener', lambda *a: pytest.fail('Invalid route reached opener'))
    with pytest.raises(ValidationError, match='route'):
        mp._capture('GET', '/v2/query/video_generation/../../elsewhere', b'', 'FAKE')
    assert mp.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://elsewhere') is None


def test_poll_binds_task_model_and_terminal_does_not_call_again(prepared, monkeypatch):
    store, packet, run = prepared
    monkeypatch.setattr(mp, '_capture', lambda *a: ({'http_status': 200, 'ambiguous': False, 'truncated': False}, {'task_id':'t1'}, {}))
    mp.submit_prepared(store, packet, run, credential_loader=lambda:'FAKE', authorized=True)
    response = {'task': {'id':'t1','model':mp.MODEL,'status':'succeeded','content':{'url':'https://cdn.example/video.mp4'}}}
    monkeypatch.setattr(mp, '_capture', lambda *a: ({'http_status':200,'ambiguous':False,'truncated':False}, response, {}))
    assert mp.poll_prepared(store, packet, run, credential_loader=lambda:'FAKE', authorized=True)['status'] == 'succeeded'
    assert json.loads((run / 'completed-response.json').read_text()) == response
    monkeypatch.setattr(mp, '_capture', lambda *a:pytest.fail('Terminal poll called provider'))
    assert mp.poll_prepared(store, packet, run, credential_loader=lambda:'FAKE')['status'] == 'succeeded'


def test_real_local_mp4_admission_records_measured_not_requested_clock(prepared, tmp_path):
    store, packet, _ = prepared; video = tmp_path / 'supplied-diagnostic.mp4'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', 'color=red:size=32x32:rate=7',
        '-frames:v', '5', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(video)], check=True, timeout=30)
    result = mp.admit_video(store, packet, video)
    assert store.get_bytes(result['video']) == video.read_bytes()
    probe = store.get_json(result['probe'])
    assert probe['streams'][0]['nb_frames'] == '5' and probe['streams'][0]['avg_frame_rate'] == '7/1'
    assert float(probe['format']['duration']) < 1  # Request remains4s; no substituted duration.
    assert result['quality'] is None and result['classification'] == 'supplied-video'
    assert result['checkpoint'] is None and result['supplied_completion'] is None
    assert 'not independently authenticated' in result['origin']


def test_admission_does_not_accept_nonvideo_or_wrong_completion(prepared, tmp_path, monkeypatch):
    store, packet, _ = prepared; video = tmp_path / 'not-video.mp4'; video.write_bytes(png())
    with pytest.raises(ValidationError, match='MP4'):
        mp.admit_video(store, packet, video)
    video.write_bytes(b'\0\0\0\x18ftyp' + b'fake diagnostic')
    monkeypatch.setattr(mp, '_probe_video', lambda *a: {'streams': []})
    with pytest.raises(ValidationError, match='completion'):
        mp.admit_video(store, packet, video, completed_response={'task':{'status':'succeeded','model':'Hailuo','duration':4,'resolution':'768P'}})


def succeed_run(run, *, url='https://video-product.cdn.minimax.io/retained.mp4?temporary=not-logged'):
    state = json.loads((run / 'state.json').read_text())
    state.update(status='succeeded', submission_attempts=1, task_id='t1')
    (run / 'state.json').write_bytes(canonical_json(state))
    completed = {'task': {'id':'t1', 'status':'succeeded', 'model':mp.MODEL,
        'duration':4, 'resolution':'768P', 'content':{'url':url}}}
    (run / 'completed-response.json').write_bytes(canonical_json(completed))


def test_cdn_download_sends_no_credentials_binds_exact_bytes_and_is_idempotent(prepared, tmp_path, monkeypatch):
    store, packet, run = prepared; source = tmp_path / 'diagnostic.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','color=blue:size=32x32:rate=7',
        '-frames:v','3','-c:v','libx264','-pix_fmt','yuv420p',str(source)], check=True, timeout=30)
    raw = source.read_bytes(); succeed_run(run); requests = []
    class MediaResponse(Response):
        headers = {'Content-Length':str(len(raw))}
        def __init__(self): self.source = BytesIO(raw)
        def read(self, maximum): return self.source.read(maximum)
    class Opener:
        def open(self, req, timeout):
            requests.append(req)
            assert req.get_header('Authorization') is None and req.get_header('Cookie') is None
            return MediaResponse()
    monkeypatch.setattr(mp.request, 'build_opener', lambda *handlers: Opener())
    result = mp.download_prepared(store, packet, run, authorized=True)
    assert store.get_bytes(result['video']) == raw and (run/'native-video.mp4').read_bytes() == raw
    receipt = store.get_json(result['download_receipt'])
    assert receipt['authorization_sent'] is False and receipt['cookies_sent'] is False
    assert receipt['source_host'] == 'video-product.cdn.minimax.io'
    assert 'temporary=' not in (run/'download-receipt.json').read_text()
    assert mp.download_prepared(store, packet, run) == result and len(requests) == 1
    (run/'native-video.mp4').write_bytes(b'changed')
    with pytest.raises(ValidationError, match='changed'):
        mp.download_prepared(store, packet, run)


@pytest.mark.parametrize('url', ['http://video-product.cdn.minimax.io/a.mp4',
    'https://user:pass@video-product.cdn.minimax.io/a.mp4', 'https://127.0.0.1/a.mp4',
    'https://video-product.cdn.minimax.io.evil.example/a.mp4', 'https://video-product.cdn.minimax.io:8443/a.mp4'])
def test_media_url_allowlist_rejects_before_network(prepared, monkeypatch, url):
    store, packet, run = prepared; succeed_run(run, url=url)
    monkeypatch.setattr(mp.request, 'build_opener', lambda *a:pytest.fail('Untrusted media URL reached network'))
    with pytest.raises(ValidationError):
        mp.download_prepared(store, packet, run, authorized=True)
    assert not (run/'.download.lock').exists()


def test_media_ambiguous_attempt_is_not_automatically_repeated(prepared, monkeypatch):
    store, packet, run = prepared; succeed_run(run); seen = []
    class Opener:
        def open(self, req, timeout):
            seen.append(req); raise OSError('FAKE server URL must not leak')
    monkeypatch.setattr(mp.request, 'build_opener', lambda *a:Opener())
    with pytest.raises(ValidationError, match='details withheld') as exc:
        mp.download_prepared(store, packet, run, authorized=True)
    assert 'FAKE' not in str(exc.value)
    with pytest.raises(ValidationError, match='Prior download'):
        mp.download_prepared(store, packet, run, authorized=True)
    assert len(seen) == 1


def test_concurrent_poll_cannot_regress_terminal_state_or_overwrite_capture(prepared, monkeypatch):
    store, packet, run = prepared
    state = json.loads((run/'state.json').read_bytes())
    state.update(status='accepted', submission_attempts=1, task_id='t1')
    (run/'state.json').write_bytes(canonical_json(state))
    entered, release = threading.Event(), threading.Event(); calls = []
    def capture(*args):
        calls.append(args)
        entered.set(); assert release.wait(5)
        # A stale running reply would be returned if another call reached GET.
        status = 'succeeded' if len(calls) == 1 else 'running'
        return {'http_status':200,'ambiguous':False,'truncated':False}, {
            'task': {'id':'t1','model':mp.MODEL,'status':status}}, {'marker':status}
    monkeypatch.setattr(mp, '_capture', capture)
    with ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(mp.poll_prepared, store, packet, run, credential_loader=lambda:'FAKE', authorized=True)
        try:
            assert entered.wait(5)
            # Another process must observe the same advisory lock.
            lock_check = subprocess.run([sys.executable, '-c',
                'import fcntl,sys; f=open(sys.argv[1],"a+b");\n'
                'try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)\n'
                'except BlockingIOError: sys.exit(0)\n'
                'sys.exit(1)', str(run/'.provider-operation.lock')], timeout=5)
            assert lock_check.returncode == 0
            with pytest.raises(ValidationError, match='busy'):
                mp.poll_prepared(store, packet, run, credential_loader=lambda:pytest.fail('Busy poll read credentials'), authorized=True)
            assert mp.packet_status(store, packet, run)['status'] == 'accepted'
        finally:
            release.set()
        assert first.result(timeout=5)['status'] == 'succeeded'
    completed = (run/'completed-response.json').read_bytes()
    captures = {str(p.relative_to(run)):p.read_bytes() for p in (run/'polls').rglob('*') if p.is_file()}
    assert mp.poll_prepared(store, packet, run, credential_loader=lambda:pytest.fail('Terminal poll read credentials'))['status'] == 'succeeded'
    assert len(calls) == 1 and (run/'completed-response.json').read_bytes() == completed
    assert captures == {str(p.relative_to(run)):p.read_bytes() for p in (run/'polls').rglob('*') if p.is_file()}
    assert mp.packet_status(store, packet, run) == {'packet':packet,'status':'succeeded','submission_attempts':1,'task_id':'t1','snapshot':True}


def test_concurrent_download_returns_busy_then_reuses_exact_completed_evidence(prepared, monkeypatch):
    store, packet, run = prepared; succeed_run(run)
    entered, release = threading.Event(), threading.Event(); calls = []
    raw = b'\0\0\0\x18ftyp' + b'local diagnostic bytes; probe stub for concurrency only'
    monkeypatch.setattr(mp, '_probe_video', lambda path: {'streams':[{'codec_name':'diagnostic-stub'}]})
    class MediaResponse(Response):
        headers = {'Content-Length':str(len(raw))}
        def __init__(self): self.source = BytesIO(raw)
        def read(self, maximum):
            entered.set(); assert release.wait(5)
            return self.source.read(maximum)
    class Opener:
        def open(self, req, timeout): calls.append(req); return MediaResponse()
    monkeypatch.setattr(mp.request, 'build_opener', lambda *a:Opener())
    with ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(mp.download_prepared, store, packet, run, authorized=True)
        try:
            assert entered.wait(5)
            with pytest.raises(ValidationError, match='busy'):
                mp.download_prepared(store, packet, run, authorized=True)
        finally:
            release.set()
        result = first.result(timeout=5)
    evidence = {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    assert mp.download_prepared(store, packet, run) == result
    assert len(calls) == 1 and evidence == {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
