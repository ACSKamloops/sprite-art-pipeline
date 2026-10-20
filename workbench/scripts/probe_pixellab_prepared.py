#!/usr/bin/env python3
"""One-shot producer capture for a SHA-pinned prepared cleanup plan. No retries."""
import argparse
import base64
import hashlib
from http.client import IncompleteRead
import io
import json
import os
from pathlib import Path
import re
import time
from urllib import error, request

from PIL import Image
import pixellab_h3_comparison as capture

ENDPOINTS = {'https://api.pixellab.ai/v2/reduce-colors',
             'https://api.pixellab.ai/v2/remove-background'}
MAX_BODY = 4 * 1024 * 1024
MAX_HAR = 64 * 1024 * 1024
SAFE_NAME = re.compile(r'[a-z0-9][a-z0-9_-]{0,63}\Z')
SHA = re.compile(r'[0-9a-f]{64}\Z')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('Nonfinite JSON number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def png(value):
    if not isinstance(value, dict) or not isinstance(value.get('base64'), str):
        raise ValueError('Expected Base64Image')
    if value.get('type', 'base64') != 'base64' or value.get('format', 'png').lower() != 'png':
        raise ValueError('Expected PNG base64 image')
    encoded = value['base64']
    if encoded.startswith('data:'):
        if not encoded.startswith('data:image/png;base64,'):
            raise ValueError('Expected PNG data URI')
        encoded = encoded.split(',', 1)[1]
    if len(encoded) > MAX_BODY * 4 // 3 + 8:
        raise ValueError('Image body limit')
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > MAX_BODY or not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Expected bounded PNG bytes')
    with Image.open(io.BytesIO(raw)) as image:
        width, height = image.size
        if (image.format != 'PNG' or getattr(image, 'n_frames', 1) != 1
                or not 1 <= width <= 2048 or not 1 <= height <= 2048
                or width * height > 1048576):
            raise ValueError('PNG dimensions/frame limit')
        image.verify()
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
    return raw, (width, height)


def within(root, path):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Prepared path escaped root')
    return path


def verify_plan(root, expected):
    if not isinstance(expected, str) or not SHA.fullmatch(expected):
        raise ValueError('Explicit plan SHA required')
    plan_bytes = (root / 'PLAN.json').read_bytes()
    if len(plan_bytes) > MAX_BODY or digest(plan_bytes) != expected:
        raise ValueError('Plan SHA changed')
    plan = strict_json(plan_bytes)
    endpoint = plan.get('endpoint')
    maximum, cases = plan.get('max_posts'), plan.get('requests')
    if endpoint not in ENDPOINTS:
        raise ValueError('Endpoint not allowed')
    if (type(maximum) is not int or not 1 <= maximum <= 12 or not isinstance(cases, list)
            or not 1 <= len(cases) <= maximum):
        raise ValueError('Plan slot count invalid')
    checked = {}
    for case in cases:
        name = case.get('variant') if isinstance(case, dict) else None
        if not isinstance(name, str) or not SAFE_NAME.fullmatch(name) or name in checked:
            raise ValueError('Unsafe/duplicate variant')
        run = within(root, root / name)
        raw = within(root, run / 'request.json').read_bytes()
        if len(raw) > MAX_BODY or digest(raw) != case.get('request_sha256'):
            raise ValueError('Prepared request changed')
        payload = strict_json(raw)
        if not isinstance(payload, dict):
            raise ValueError('Request must be an object')
        wire_path = within(root, run / 'request-wire.json')
        wire = wire_path.read_bytes() if wire_path.exists() else json.dumps(
            payload, separators=(',', ':'), ensure_ascii=False).encode()
        if len(wire) > MAX_BODY or strict_json(wire) != payload:
            raise ValueError('Wire/request JSON differ')
        expected_wire = [case[k] for k in ('wire_sha256', 'compact_http_body_sha256') if k in case]
        if not expected_wire or any(digest(wire) != value for value in expected_wire):
            raise ValueError('Prepared wire changed')
        images = payload.get('images') if endpoint.endswith('/reduce-colors') else [payload.get('image')]
        if not isinstance(images, list) or not 1 <= len(images) <= 256:
            raise ValueError('Invalid input images')
        dimensions = [png(value)[1] for value in images]
        if endpoint.endswith('/reduce-colors'):
            if len(set(dimensions)) != 1 or sum(w * h for w, h in dimensions) > 262144:
                raise ValueError('Reducer input size limit')
        elif payload.get('image_size') != dict(zip(('width', 'height'), dimensions[0])):
            raise ValueError('Cutout image_size differs from PNG')
        checked[name] = {'run': run, 'wire': wire, 'dimensions': dimensions}
    return endpoint, checked


def validate_result(endpoint, result, dimensions):
    if not isinstance(result, dict):
        raise ValueError('Expected response object')
    reducer = endpoint.endswith('/reduce-colors')
    values = result.get('images') if reducer else [result.get('image')]
    if not isinstance(values, list) or len(values) != len(dimensions):
        raise ValueError('Response frame count differs')
    files = {}
    for index, (value, expected) in enumerate(zip(values, dimensions)):
        raw, size = png(value)
        if size != expected:
            raise ValueError('Response image dimensions differ')
        files[f'output-{index:02}.png'] = raw
    if reducer:
        raw, size = png(result.get('palette'))
        if size[1] != 1 or size[0] > 256:
            raise ValueError('Palette must be a bounded1px strip')
        files['palette.png'] = raw
    return files


def submit(root, variant, plan_sha):
    endpoint, checked = verify_plan(root, plan_sha)  # All slots, before auth or transport.
    if variant not in checked:
        raise ValueError('Variant not in frozen plan')
    slot = checked[variant]
    run, wire = slot['run'], slot['wire']
    if (any((run / name).exists() for name in ('state.json', 'network.har', 'response.json', 'palette.png'))
            or any(run.glob('output-*.png'))):
        raise FileExistsError('Prior capture evidence exists; refusing overwrite')
    fd = os.open(run / '.submission.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, json.dumps({'plan_sha256': plan_sha, 'wire_sha256': digest(wire)}).encode())
        os.fsync(fd)
    finally:
        os.close(fd)
    fd = os.open(run, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    state = {'status': 'attempted', 'automatic_retry_allowed': False,
             'plan_sha256': plan_sha, 'wire_sha256': digest(wire), 'utc': capture.now()}
    capture.write_json(run / 'state.json', state)
    try:
        token = capture.credential()
        if not isinstance(token, str) or not token:
            raise ValueError('Credential unavailable')
    except Exception as exc:
        state.update(status='credential-unavailable', failure_type=type(exc).__name__)
        capture.write_json(run / 'state.json', state)
        return state
    started, clock = capture.now(), time.monotonic()
    status, mime, raw, failure, complete, observed = 0, '', b'', None, True, 0
    req = request.Request(endpoint, data=wire, method='POST', headers={
        'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    try:
        try:
            response = request.build_opener(capture.NoRedirect).open(req, timeout=60)
        except error.HTTPError as exc:
            response = exc
        with response:
            status, mime = response.code, response.headers.get('Content-Type', '')
            try:
                raw = response.read(MAX_BODY + 1)
            except IncompleteRead as exc:
                raw = exc.partial
                raise
            observed = len(raw)
            if observed > MAX_BODY:
                raw, complete, failure = raw[:MAX_BODY], False, 'BodyLimitExceeded'
    except (error.URLError, TimeoutError, OSError, IncompleteRead) as exc:
        observed = len(raw)
        raw, complete, failure = raw[:MAX_BODY], False, type(exc).__name__
    elapsed = (time.monotonic() - clock) * 1000
    strict_response_json = True
    try:
        strict_json(raw)
    except Exception:
        strict_response_json = False
    try:
        result, safe_text, redacted = capture.sanitize_response(raw, token)
    except Exception:
        result, safe_text, redacted = {'response_parse_failed': True}, '', True
    omitted = not complete or not strict_response_json
    # A truncated/non-JSON body may split a JSON-escaped credential. Retain its
    # byte SHA/extent, but omit text rather than persist an unparseable echo.
    if omitted:
        safe_text, redacted = '', True
    try:
        _, safe_wire, wire_redacted = capture.sanitize_response(wire, token)
    except Exception:
        safe_wire, wire_redacted = '', True
    mime = mime.replace(token, '[REDACTED]')
    entry = {'startedDateTime': started, 'time': elapsed,
        'request': {'method': 'POST', 'url': endpoint, 'httpVersion': '',
            'headers': [{'name': 'Content-Type', 'value': 'application/json'}], 'cookies': [],
            'queryString': [], 'headersSize': -1, 'bodySize': len(wire),
            'postData': {'mimeType': 'application/json', 'text': safe_wire, 'text_redacted': wire_redacted}},
        'response': {'status': status, 'statusText': '', 'httpVersion': '',
            'headers': [{'name': 'Content-Type', 'value': mime}], 'cookies': [],
            'content': {'size': len(raw), 'mimeType': mime, 'text': safe_text, 'text_redacted': redacted},
            'redirectURL': '', 'headersSize': -1, 'bodySize': len(raw) if complete else -1},
        'cache': {}, 'timings': {k: -1 for k in ['blocked', 'dns', 'connect', 'send', 'wait', 'receive', 'ssl']},
        '_request_body_sha256': digest(wire), '_response_body_sha256_before_scrub': digest(raw),
        '_response_body_sha256_scope': 'full' if complete else 'prefix',
        '_response_text_omitted_non_json_or_incomplete': omitted,
        '_response_prefix_bytes': len(raw), '_response_bytes_observed': observed,
        '_producer': 'Actual urllib call; authorization/cookies omitted; not browser instrumentation'}
    har = {'log': {'version': '1.2', 'creator': {'name': 'probe_pixellab_prepared.py', 'version': '1'}, 'entries': [entry]}}
    if len(json.dumps(har).encode()) > MAX_HAR:
        raise ValueError('HAR bound exceeded; claimed slot cannot retry')
    capture.write_json(run / 'network.har', har)
    capture.write_json(run / 'response.json', result)
    files, invalid = {}, None
    if status == 200 and complete and failure is None:
        try:
            if not strict_response_json:
                raise ValueError('Response is not strict JSON')
            files = validate_result(endpoint, result, slot['dimensions'])
        except Exception as exc:
            invalid = type(exc).__name__
    state.update(status=('completed' if invalid is None else 'response-invalid')
                 if status == 200 and complete and failure is None else 'failed-or-ambiguous',
                 http_status=status, transport_failure=failure, response_validation_failure=invalid,
                 response_body_sha256_scope='full' if complete else 'prefix',
                 usage=result.get('usage') if isinstance(result, dict) else None, utc=capture.now())
    for name, raw_png in files.items():
        (run / name).write_bytes(raw_png)
    capture.write_json(run / 'state.json', state)
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--plan-sha', required=True)
    parser.add_argument('--variant', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(submit(args.root, args.variant, args.plan_sha)))
    except Exception as exc:
        print(json.dumps({'status': 'rejected-or-stopped', 'failure_type': type(exc).__name__}))
        raise SystemExit(2)
