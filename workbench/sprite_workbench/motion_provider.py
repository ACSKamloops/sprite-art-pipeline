"""Bounded native H3 packets/receipts. Local host code, not PixelLab inference.

Preparation/admission are offline. Submit/poll require explicit authorization
and an injected process-only credential loader. This module never reads auth.
"""
from datetime import datetime, timezone
import fcntl
from functools import wraps
from http.client import IncompleteRead, HTTPException
from io import BytesIO
import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib import request, error, parse

from PIL import Image

from .core import ValidationError, UnsupportedCapability, canonical_json, digest, validate_id

API = 'https://api.minimax.io'
CREATE = '/v2/video_generation'
MODEL = 'MiniMax-H3'
MAX_IMAGE = 4 * 1024 * 1024  # Local packet limit, stricter than vendor 30 MB.
MAX_WIRE = 12 * 1024 * 1024
MAX_RESPONSE = 4 * 1024 * 1024
MAX_VIDEO = 512 * 1024 * 1024
SOURCES = {
    'create': 'https://platform.minimax.io/docs/api-reference/video-generation-v2-create',
    'query': 'https://platform.minimax.io/docs/api-reference/video-generation-v2-query',
    'context_ir': 'https://platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir',
}
BOUNDARY = 'Native MiniMax-H3 video; private checkpoint unknown; no PixelLab conversion or alpha/loop/seed guarantee'


def catalog():
    return {'provider': 'MiniMax', 'model': MODEL, 'checkpoint': None,
        'adapter': 'native-h3-first-last-v1', 'first_frame': True, 'last_frame': True,
        'duration_seconds': list(range(4, 16)), 'resolution': ['768P', '2K'],
        'context_ir': 'Separate asynchronous prompt-only endpoint; not called by this adapter',
        'unsupported': ['seed', 'frame_count', 'fps', 'no_background', 'enhance_prompt', 'pixel_palette',
                        'rig', 'joints', 'reference_media', 'MiniMax-H3-Max'],
        'sources': SOURCES, 'boundary': BOUNDARY, 'execution': 'Explicit authorization required; no automatic retries'}


def _png(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_IMAGE:
        raise ValidationError('PNG must be bytes within local 4 MiB limit')
    try:
        with Image.open(BytesIO(raw)) as im:
            w, h = im.size
            if (im.format != 'PNG' or not 256 <= min(w, h) <= max(w, h) <= 5760
                    or not .4 <= w / h <= 2.5 or w*h > 16_777_216 or getattr(im, 'n_frames', 1) != 1):
                raise ValidationError('Expected one PNG, 256..5760px, ratio .4..2.5, local <=16M pixels')
            im.load()
            rgba_sha = digest(im.convert('RGBA').tobytes())
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValidationError('Invalid or out-of-bounds conditioning PNG') from exc
    return {'sha256': digest(raw), 'rgba_sha256': rgba_sha, 'size': [w, h], 'bytes': len(raw)}


def prepare_packet(store, first_png, prompt, *, last_png=None, duration=4, resolution='768P'):
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 7000:
        raise ValidationError('Literal nonblank prompt required; local limit 7000 characters')
    if type(duration) is not int or not 4 <= duration <= 15 or resolution not in ('768P', '2K'):
        raise ValidationError('H3 requires integer duration 4..15 and resolution 768P or 2K')
    images = [('first_frame', first_png)] + ([] if last_png is None else [('last_frame', last_png)])
    records = [(role, raw, _png(raw)) for role, raw in images]
    content = [{'type': 'text', 'text': prompt}]
    for role, raw, _ in records:
        content.append({'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + base64.b64encode(raw).decode()}, 'role': role})
    body = {'model': MODEL, 'content': content, 'resolution': resolution, 'duration': duration, 'ratio': 'adaptive'}
    wire = canonical_json(body)
    if len(wire) > MAX_WIRE:
        raise ValidationError('Prepared request exceeds local wire limit')
    packet = {'kind': 'motion-provider-packet', 'version': 1, 'provider': 'MiniMax',
        'model': MODEL, 'checkpoint': None, 'endpoint': API + CREATE,
        'request': store.put_bytes(wire), 'request_sha256': digest(wire),
        'prompt': prompt, 'prompt_sha256': digest(prompt.encode()),
        'inputs': [dict(role=role, png=store.put_bytes(raw), **meta) for role, raw, meta in records],
        'duration': duration, 'resolution': resolution, 'context_ir_applied': False, 'boundary': BOUNDARY}
    return {'packet': store.put_json(packet), **packet}


def load_packet(store, packet):
    doc = store.get_json(validate_id(packet))
    fields = {'kind', 'version', 'provider', 'model', 'checkpoint', 'endpoint', 'request', 'request_sha256',
        'prompt', 'prompt_sha256', 'inputs', 'duration', 'resolution', 'context_ir_applied', 'boundary'}
    if (set(doc) != fields or doc['kind'] != 'motion-provider-packet' or type(doc['version']) is not int
            or doc['version'] != 1 or doc['provider'] != 'MiniMax' or doc['model'] != MODEL
            or doc['checkpoint'] is not None or doc['endpoint'] != API + CREATE
            or doc['context_ir_applied'] is not False or doc['boundary'] != BOUNDARY
            or not isinstance(doc['inputs'], list) or len(doc['inputs']) not in (1, 2)):
        raise ValidationError('Invalid native H3 packet schema/identity')
    raws = []
    for role, item in zip(['first_frame', 'last_frame'], doc['inputs']):
        if not isinstance(item, dict) or set(item) != {'role', 'png', 'sha256', 'rgba_sha256', 'size', 'bytes'} or item['role'] != role:
            raise ValidationError('Invalid H3 packet frame roles')
        raw = store.get_bytes(validate_id(item['png']), max_bytes=MAX_IMAGE)
        if {k: item[k] for k in ('sha256', 'rgba_sha256', 'size', 'bytes')} != _png(raw):
            raise ValidationError('Conditioning image metadata mismatch')
        raws.append(raw)
    # Reconstruct the declared contract, rather than trust arbitrary prepared JSON.
    replay = prepare_packet(store, raws[0], doc['prompt'], last_png=raws[1] if len(raws) == 2 else None,
                            duration=doc['duration'], resolution=doc['resolution'])
    if replay['packet'] != packet:
        raise ValidationError('Packet differs from exact supported native request')
    return doc, store.get_bytes(doc['request'], max_bytes=MAX_WIRE)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write(path, value, *, exclusive=False):
    raw = canonical_json(value)
    if exclusive:
        with path.open('xb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
    else:
        fd, name = tempfile.mkstemp(prefix='.motion-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(raw); f.flush(); os.fsync(f.fileno())
            os.replace(name, path)
        finally:
            Path(name).unlink(missing_ok=True)
    _fsync_dir(path.parent)


def write_prepared(store, packet, run):
    doc, wire = load_packet(store, packet)
    run = Path(run)
    run.mkdir(parents=True, exist_ok=False)
    _write(run / 'packet.json', {'packet': packet, 'document': doc}, exclusive=True)
    with (run / 'request.json').open('xb') as f:
        f.write(wire); f.flush(); os.fsync(f.fileno())
    _write(run / 'state.json', {'packet': packet, 'status': 'prepared', 'submission_attempts': 0}, exclusive=True)
    return {'packet': packet, 'run': str(run), 'status': 'prepared'}


def _prepared(store, packet, run):
    doc, wire = load_packet(store, packet)
    run = Path(run)
    try:
        state = json.loads((run / 'state.json').read_bytes())
        if (run / 'request.json').read_bytes() != wire or json.loads((run / 'packet.json').read_bytes()) != {'packet': packet, 'document': doc}:
            raise ValidationError('Prepared run was changed')
        if state['packet'] != packet:
            raise ValidationError('Prepared state packet mismatch')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValidationError('Invalid prepared run') from exc
    return run, doc, wire, state


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _scrub(obj, token):
    if isinstance(obj, str):
        return obj.replace(token, '[REDACTED]')
    if isinstance(obj, list):
        return [_scrub(v, token) for v in obj]
    if isinstance(obj, dict):
        return {_scrub(k, token): _scrub(v, token) for k, v in obj.items()}
    return obj


def _response_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError('Duplicate response JSON key')
            result[key] = value
        return result
    obj = json.loads(raw, object_pairs_hook=pairs)
    canonical_json(obj)
    return obj


def _capture(method, path, wire, token):
    if not (method == 'POST' and path == CREATE or method == 'GET' and re.fullmatch(r'/v2/query/video_generation/[A-Za-z0-9_-]{1,128}', path)):
        raise ValidationError('Provider route refused')
    req = request.Request(API + path, data=wire if method == 'POST' else None, method=method,
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    started = _now(); start = time.monotonic(); raw = b''; status = None; ambiguous = False; content_type = ''
    try:
        try:
            response = request.build_opener(request.ProxyHandler({}), NoRedirect()).open(req, timeout=60)
        except error.HTTPError as exc:
            response = exc
        with response:
            status = response.code
            content_type = str(getattr(response, 'headers', {}).get('Content-Type', ''))[:256].replace(token, '[REDACTED]')
            raw = response.read(MAX_RESPONSE + 1)
    except IncompleteRead as exc:
        raw = exc.partial[:MAX_RESPONSE + 1]
        ambiguous = True
    except (OSError, error.URLError, TimeoutError, HTTPException):
        ambiguous = True  # Error strings/exception payloads may contain credentials.
    truncated = len(raw) > MAX_RESPONSE
    raw = raw[:MAX_RESPONSE]
    text = raw.decode('utf-8', errors='replace'); parsed = None
    try:
        parsed = _response_json(raw)
        safe = _scrub(parsed, token)
        if safe != parsed:
            text = canonical_json(safe).decode()
        parsed = safe
    except (ValueError, UnicodeDecodeError):
        parsed = None
        text = '[Non-JSON or incomplete response omitted; raw hash retained]'
    transport = {'http_status': status, 'ambiguous': ambiguous, 'truncated': truncated,
        'raw_body_sha256': digest(raw), 'raw_body_sha256_scope': 'prefix' if truncated or ambiguous else 'full',
        'text_redacted': token in raw.decode('utf-8', errors='replace') or text != raw.decode('utf-8', errors='replace'),
        'captured_utc': started, 'elapsed_ms': round((time.monotonic()-start)*1000, 3)}
    entry = {'startedDateTime': started, 'time': transport['elapsed_ms'],
        'request': {'method': method, 'url': API + path, 'httpVersion': '', 'headers': [], 'cookies': [],
            'queryString': [], 'headersSize': -1, 'bodySize': len(wire) if method == 'POST' else 0},
        'response': {'status': status or 0, 'statusText': '', 'httpVersion': '', 'headers': [], 'cookies': [],
            'content': {'size': len(raw), 'mimeType': content_type, 'text': text}, 'redirectURL': '', 'headersSize': -1, 'bodySize': len(raw)},
        'cache': {}, 'timings': {'send': -1, 'wait': -1, 'receive': -1}, '_capture': transport}
    if method == 'POST':
        safe_request = _scrub(json.loads(wire), token)
        request_text = wire.decode() if safe_request == json.loads(wire) else canonical_json(safe_request).decode()
        entry['request']['postData'] = {'mimeType': 'application/json', 'text': request_text}
        entry['_request_text_redacted'] = request_text != wire.decode()
    return transport, parsed, entry


def _authorized(authorized, credential_loader):
    if authorized is not True:
        raise ValidationError('Explicit provider-call authorization required')
    try:
        token = credential_loader()
    except Exception:
        raise ValidationError('Credential loader failed; details withheld') from None
    if not isinstance(token, str) or not token or any(not 33 <= ord(c) <= 126 for c in token):
        raise ValidationError('Process-only credential loader must supply a nonempty token')
    return token


def _run_guard(operation):
    """Serialize the entire read/network/persist operation across processes.

    This advisory lock is released by close/process exit. It is distinct from
    the permanent paid-attempt claim, which is never cleared for retry.
    """
    @wraps(operation)
    def guarded(store, packet, run, *args, **kwargs):
        try:
            fd = os.open(Path(run) / '.provider-operation.lock', os.O_CREAT | os.O_RDWR, 0o600)
        except OSError:
            raise ValidationError('Prepared provider run is unavailable') from None
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValidationError('Provider operation busy; current operation must finish before another begins') from None
            return operation(store, packet, run, *args, **kwargs)
        finally:
            os.close(fd)
    return guarded


def packet_status(store, packet, run):
    """Read the atomically published safe state without credentials or network.

    A concurrent operation may advance it immediately after this snapshot.
    """
    _, _, _, state = _prepared(store, packet, run)
    statuses = {'prepared', 'submission-attempted', 'accepted', 'submission-ambiguous',
                'submission-failed', 'queued', 'running', 'succeeded', 'failed', 'cancelled'}
    if (state.get('status') not in statuses or type(state.get('submission_attempts')) is not int
            or state['submission_attempts'] not in (0, 1)):
        raise ValidationError('Invalid provider state')
    task = state.get('task_id')
    if task is not None and (not isinstance(task, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', task)):
        raise ValidationError('Invalid provider task identity')
    return {'packet': packet, 'status': state['status'], 'submission_attempts': state['submission_attempts'],
            'task_id': task, 'snapshot': True}


@_run_guard
def submit_prepared(store, packet, run, *, credential_loader, authorized=False):
    run, _, wire, state = _prepared(store, packet, run)
    if state.get('status') != 'prepared' or state.get('submission_attempts') != 0:
        raise ValidationError('Already attempted; never resubmit an ambiguous paid request')
    if any((run / n).exists() for n in ('network.har', 'submit-response.json', '.submission.lock')):
        raise ValidationError('Prior capture evidence exists; submission refused')
    token = _authorized(authorized, credential_loader)
    claims = store.path / 'motion-provider-claims'; claims.mkdir(exist_ok=True)
    # The Store-wide packet claim also blocks submitting the same packet in a new run.
    try:
        _write(claims / packet, {'packet': packet, 'status': 'attempted', 'run': str(run.resolve())}, exclusive=True)
    except FileExistsError as exc:
        raise ValidationError('Packet already claimed in this Store; no automatic retry') from exc
    _write(run / '.submission.lock', {'packet': packet}, exclusive=True)
    state |= {'status': 'submission-attempted', 'submission_attempts': 1, 'attempted_utc': _now()}
    _write(run / 'state.json', state)
    # After these markers, crashes/ambiguity require manual reconciliation, never retry.
    transport, result, entry = _capture('POST', CREATE, wire, token)
    _write(run / 'network.har', {'log': {'version': '1.2', 'creator': {'name': 'motion-provider-http-producer', 'version': '1'}, 'entries': [entry]}})
    _write(run / 'submit-response.json', {'transport': transport, 'body': result})
    task = result.get('task_id') if isinstance(result, dict) else None
    if transport['http_status'] == 200 and not transport['ambiguous'] and not transport['truncated'] and isinstance(task, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', task):
        state |= {'status': 'accepted', 'task_id': task}
    else:
        state['status'] = 'submission-ambiguous' if transport['ambiguous'] or transport['truncated'] else 'submission-failed'
    _write(run / 'state.json', state)
    return {'packet': packet, 'status': state['status'], 'task_id': state.get('task_id')}


@_run_guard
def poll_prepared(store, packet, run, *, credential_loader, authorized=False):
    run, _, _, state = _prepared(store, packet, run)
    task = state.get('task_id')
    if not isinstance(task, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', task):
        raise ValidationError('No accepted task to poll')
    if state.get('status') in ('succeeded', 'failed', 'cancelled'):
        return {'packet': packet, 'status': state['status'], 'task_id': task}
    token = _authorized(authorized, credential_loader)
    polls = run / 'polls'; polls.mkdir(exist_ok=True)
    # Exclusive per-poll slot, before network; no silent overwrite by concurrent pollers.
    index = 0
    while True:
        slot = polls / f'{index:04d}'
        try:
            slot.mkdir(); break
        except FileExistsError:
            index += 1
        if index >= 1024:
            raise ValidationError('Poll retention budget exhausted')
    transport, result, entry = _capture('GET', '/v2/query/video_generation/' + task, b'', token)
    _write(slot / 'network.har', {'log': {'version': '1.2', 'creator': {'name': 'motion-provider-http-producer', 'version': '1'}, 'entries': [entry]}})
    _write(slot / 'response.json', {'transport': transport, 'body': result})
    obj = result.get('task', {}) if isinstance(result, dict) else {}
    if transport['http_status'] == 200 and not transport['ambiguous'] and not transport['truncated'] and isinstance(obj, dict):
        if obj.get('id') == task and obj.get('model') == MODEL and obj.get('status') in ('queued', 'running', 'succeeded', 'failed', 'cancelled'):
            state['status'] = obj['status']
            if obj['status'] == 'succeeded':
                _write(run / 'completed-response.json', result)
    _write(run / 'state.json', state)
    return {'packet': packet, 'status': state['status'], 'task_id': task}


def _probe_video(path):
    ffprobe, prlimit = shutil.which('ffprobe'), shutil.which('prlimit')
    if not ffprobe or not prlimit:
        raise UnsupportedCapability('motion-video-probe', 'Local ffprobe and Linux prlimit required')
    with tempfile.TemporaryFile() as output:
        try:
            result = subprocess.run([prlimit, '--as=1073741824', '--cpu=20', '--fsize=1048576', '--', ffprobe,
                '-v', 'error', '-protocol_whitelist', 'file,pipe', '-select_streams', 'v:0', '-show_entries',
                'stream=codec_name,width,height,pix_fmt,avg_frame_rate,time_base,duration,nb_frames:format=format_name,duration',
                '-of', 'json', str(path)], stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL, timeout=30)
            output.seek(0); raw = output.read(65537)
            if result.returncode or len(raw) > 65536:
                raise ValidationError('Native video probe failed or exceeded bounds')
            probe = json.loads(raw)
            stream = probe['streams'][0]
            w, h = stream['width'], stream['height']
            if type(w) is not int or type(h) is not int or min(w, h) < 1 or w*h > 16_777_216:
                raise ValidationError('Native video dimensions exceed local limit')
            return probe
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, IndexError) as exc:
            raise ValidationError('Native video probe failed') from exc


def admit_video(store, packet, video_path, *, completed_response=None):
    """Retain supplied raw video + measured metadata, without trusting its origin.

    completed_response is a supplied JSON object, not authenticated provenance.
    No request duration is substituted for the container's measured duration.
    """
    doc, _ = load_packet(store, packet)
    source = Path(video_path)
    if source.is_symlink() or not source.is_file() or not 0 < source.stat().st_size <= MAX_VIDEO:
        raise ValidationError('Expected bounded regular native video file')
    raw = source.read_bytes()
    if len(raw) > MAX_VIDEO or len(raw) < 12 or raw[4:8] != b'ftyp':
        raise ValidationError('Expected bounded MP4 container')
    # Probe this exact byte snapshot; the source path may change concurrently.
    with tempfile.TemporaryDirectory(prefix='motion-admission-') as temporary:
        snapshot = Path(temporary) / 'native.mp4'; snapshot.write_bytes(raw)
        probe = _probe_video(snapshot)
    response_id = None
    if completed_response is not None:
        obj = completed_response.get('task', {}) if isinstance(completed_response, dict) else {}
        if (obj.get('status') != 'succeeded' or obj.get('model') != MODEL
                or obj.get('duration') != doc['duration'] or obj.get('resolution') != doc['resolution']):
            raise ValidationError('Supplied completion does not match requested H3 contract')
        response_id = store.put_json(completed_response)
    record = {'kind': 'motion-native-video', 'version': 1, 'packet': packet, 'video': store.put_bytes(raw),
        'video_sha256': digest(raw), 'bytes': len(raw), 'probe': store.put_json(probe),
        'supplied_completion': response_id, 'requested_model': MODEL, 'checkpoint': None,
        'origin': 'supplied raw video; provider origin not independently authenticated',
        'classification': 'supplied-video', 'quality': None, 'boundary': BOUNDARY}
    return {'native_video': store.put_json(record), **record}


CDN_HOSTS = frozenset({'video-product.cdn.minimax.io', 'cdn.hailuoai.com'})


@_run_guard
def download_prepared(store, packet, run, *, authorized=False):
    """One bounded, unauthenticated CDN GET; no redirects or resubmission.

    The persisted binding documents this process's observations. Supplied disk
    captures are not signatures or independent attestation by the provider.
    """
    run, doc, _, state = _prepared(store, packet, run)
    task = state.get('task_id')
    if state.get('status') != 'succeeded' or not isinstance(task, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', task):
        raise ValidationError('A succeeded matching task is required for download')
    try:
        completed_raw = (run / 'completed-response.json').read_bytes()
        if len(completed_raw) > MAX_RESPONSE:
            raise ValidationError('Completion exceeds local response bound')
        completed = json.loads(completed_raw); obj = completed['task']
        if (obj['id'] != task or obj['status'] != 'succeeded' or obj['model'] != MODEL
                or obj['duration'] != doc['duration'] or obj['resolution'] != doc['resolution']):
            raise ValidationError('Completion differs from prepared task/model/controls')
        url = obj['content']['url']; parts = parse.urlsplit(url)
        if (parts.scheme != 'https' or parts.hostname not in CDN_HOSTS or parts.port not in (None, 443)
                or parts.username or parts.password or parts.fragment or len(url) > 8192):
            raise ValidationError('Returned media URL is outside the explicit HTTPS MiniMax CDN allowlist')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValidationError('Invalid or mismatched completion/media URL') from exc
    result_file = run / 'download-result.json'; video = run / 'native-video.mp4'
    if result_file.exists():
        result = json.loads(result_file.read_bytes())
        record = store.get_json(result['native_video'])
        receipt = store.get_json(result['download_receipt'])
        if (record['packet'] != packet or record['video'] != result['video']
                or record['video_sha256'] != digest(video.read_bytes())
                or receipt['completed_response_sha256'] != digest(completed_raw)
                or receipt['packet'] != packet or receipt['task_id'] != task):
            raise ValidationError('Retained download changed; no automatic overwrite')
        store.get_bytes(record['video'], max_bytes=MAX_VIDEO)
        return result
    if authorized is not True:
        raise ValidationError('Explicit media-download authorization required')
    if any((run / name).exists() for name in ('.download.lock', 'native-video.mp4', 'native-video.mp4.partial', 'download-receipt.json')):
        raise ValidationError('Prior download attempt/evidence exists; manual reconciliation required')
    _write(run / '.download.lock', {'packet': packet, 'task_id': task, 'status': 'attempted'}, exclusive=True)
    partial = run / 'native-video.mp4.partial'; start = time.monotonic(); count = 0
    try:
        # There is no credential parameter or Authorization/cookie header here.
        req = request.Request(url, method='GET', headers={})
        with request.build_opener(request.ProxyHandler({}), NoRedirect()).open(req, timeout=30) as response:
            if response.code != 200:
                raise ValidationError('Media response status is not 200')
            declared = response.headers.get('Content-Length')
            if declared is not None and (not declared.isdecimal() or not 0 < int(declared) <= MAX_VIDEO):
                raise ValidationError('Media Content-Length is invalid or exceeds local limit')
            with partial.open('xb') as target:
                while True:
                    chunk = response.read(min(1024*1024, MAX_VIDEO-count+1))
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > MAX_VIDEO or time.monotonic()-start > 120:
                        raise ValidationError('Media size/time bound exceeded')
                    target.write(chunk)
                target.flush(); os.fsync(target.fileno())
            if count == 0 or declared is not None and count != int(declared):
                raise ValidationError('Media size differs from declared Content-Length')
        os.link(partial, video); partial.unlink(); _fsync_dir(run)
        admitted = admit_video(store, packet, video, completed_response=completed)
        receipt = {'kind': 'motion-media-download', 'version': 1, 'packet': packet, 'task_id': task,
            'completed_response_sha256': digest(completed_raw), 'source_host': parts.hostname,
            'url_sha256': digest(url.encode()), 'video': admitted['video'], 'bytes': count,
            'authorization_sent': False, 'cookies_sent': False, 'redirects_followed': False,
            'elapsed_ms': round((time.monotonic()-start)*1000, 3),
            'binding': 'Producer-observed matching task/packet/media bytes; not external provider attestation'}
        _write(run / 'download-receipt.json', receipt, exclusive=True)
        result = {'native_video': admitted['native_video'], 'video': admitted['video'],
            'download_receipt': store.put_json(receipt), 'packet': packet, 'status': 'downloaded'}
        _write(result_file, result, exclusive=True)
        return result
    except Exception:
        _write(run / 'download-failure.json', {'packet': packet, 'status': 'failed-or-ambiguous',
            'retained_bytes': count, 'automatic_retry': False})
        raise ValidationError('Media download/admission failed; details withheld; retained attempt requires reconciliation') from None
