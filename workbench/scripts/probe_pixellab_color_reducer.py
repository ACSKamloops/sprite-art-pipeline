#!/usr/bin/env python3
"""Bounded synthetic characterization of the exposed reducer, not PixMiniMax internals.

Three explicit variants in each calibration phase, plus one held-out validation;
one persistent claim per paid POST; no retry. Reuses
the existing credential resolver and decoded-JSON redactor without printing keys.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import time
from urllib import request, error

import numpy as np
from PIL import Image

import pixellab_h3_comparison as capture


VARIANTS = {'fixed-none': 'none', 'fixed-repeat': 'none', 'fixed-2x2': '2x2'}
PHASE2 = {'six-color-none': 'none', 'bw-2x2-zero': '2x2', 'bw-2x2-ten': '2x2'}
PHASE3 = {'weighted-holdout': 'none'}
ENDPOINT = 'https://api.pixellab.ai/v2/reduce-colors'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(path):
    return {'type': 'base64', 'base64': 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode(), 'format': 'png'}


def prepare(root, phase=1):
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'inputs'
    inputs.mkdir()
    # Complete 16^3 RGB cube followed by repeated 8-bit gray ramps. No AI art.
    levels = np.rint(np.linspace(0, 255, 16)).astype(np.uint8)
    cube = np.stack(np.meshgrid(levels, levels, levels, indexing='ij'), axis=-1).reshape(16, 256, 3)
    first = np.zeros((32, 256, 4), dtype=np.uint8)
    first[:16, :, :3] = cube
    first[16:, :, :3] = np.arange(256, dtype=np.uint8)[None, :, None]
    first[..., 3] = 255
    second = first.copy()
    second[..., 3] = np.tile(np.repeat(np.array([0, 64, 128, 255], dtype=np.uint8), 64), (32, 1))
    Image.fromarray(first).save(inputs / 'rgb-cube-gray.png')
    Image.fromarray(second).save(inputs / 'rgba-stripes.png')
    Image.fromarray(np.array([[[0, 0, 0, 255], [255, 255, 255, 255]]], dtype=np.uint8)).save(inputs / 'black-white-palette.png')
    Image.fromarray(np.array([[[0, 0, 0, 255], [255, 255, 255, 255], [255, 0, 0, 255],
                              [0, 255, 0, 255], [0, 0, 255, 255], [128, 128, 128, 255]]], dtype=np.uint8)).save(inputs / 'six-color-palette.png')
    frozen = []
    variants = VARIANTS if phase == 1 else PHASE2
    for variant, dithering in variants.items():
        run = root / variant
        run.mkdir()
        payload = {'images': [descriptor(inputs / f) for f in ['rgb-cube-gray.png', 'rgba-stripes.png']],
                   'palette_image': descriptor(inputs / ('six-color-palette.png' if variant == 'six-color-none' else 'black-white-palette.png')),
                   'dithering': dithering, 'dithering_strength': (0.0 if variant == 'bw-2x2-zero' else 10.0 if variant == 'bw-2x2-ten' else 5.0)}
        capture.write_json(run / 'request.json', payload)
        frozen.append({'variant': variant, 'request_sha256': sha((run / 'request.json').read_bytes())})
    capture.write_json(root / 'PLAN.json', {'version': 1, 'prepared_utc': capture.now(),
        'endpoint': ENDPOINT, 'phase': phase, 'max_posts': 3, 'automatic_retries': 0, 'requests': frozen,
        'hypotheses': ['Fixed palette mapping versus RGB, weighted luminance or perceptual alternatives',
                       'Alpha preservation versus flattening/thresholding', 'Ordered 2x2 pattern and phase',
                       'Exact repeatability for one identical request'],
        'scope': 'Separate public reducer characterization; no assertion that animation uses this endpoint or exact private algorithm recovered'})
    return {'prepared': str(root), 'variants': list(variants), 'posts': 0}


def submit(root, variant):
    if variant not in (VARIANTS | PHASE2 | PHASE3):
        raise ValueError('Unknown variant')
    plan = capture.read_json(root / 'PLAN.json')
    run = root / variant
    raw_request_file = (run / 'request.json').read_bytes()
    expected = next(e['request_sha256'] for e in plan['requests'] if e['variant'] == variant)
    if sha(raw_request_file) != expected:
        raise ValueError('Prepared request changed')
    token = capture.credential()
    fd = os.open(run / '.submission.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    capture.write_json(run / 'state.json', {'status': 'attempted', 'automatic_retry_allowed': False, 'utc': capture.now()})
    raw_request = json.dumps(json.loads(raw_request_file), separators=(',', ':'), ensure_ascii=False).encode()
    req = request.Request(ENDPOINT, data=raw_request, method='POST', headers={
        'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    started = capture.now()
    clock = time.monotonic()
    status, mime, raw, failure = 0, '', b'', None
    try:
        try:
            response = request.build_opener(capture.NoRedirect).open(req, timeout=60)
        except error.HTTPError as exc:
            response = exc
        with response:
            status, mime = response.code, response.headers.get('Content-Type', '')
            raw = response.read(4 * 1024 * 1024 + 1)
            if len(raw) > 4 * 1024 * 1024:
                raise ValueError('Response limit exceeded; no retry')
    except (error.URLError, TimeoutError, OSError) as exc:
        failure = type(exc).__name__
    result, safe_text, redacted = capture.sanitize_response(raw, token)
    elapsed = (time.monotonic() - clock) * 1000
    entry = {'startedDateTime': started, 'time': elapsed,
             'request': {'method': 'POST', 'url': ENDPOINT, 'httpVersion': '',
                         'headers': [{'name': 'Content-Type', 'value': 'application/json'}],
                         'cookies': [], 'queryString': [], 'headersSize': -1, 'bodySize': len(raw_request),
                         'postData': {'mimeType': 'application/json', 'text': raw_request.decode()}},
             'response': {'status': status, 'statusText': '', 'httpVersion': '',
                          'headers': [{'name': 'Content-Type', 'value': mime}], 'cookies': [],
                          'content': {'size': len(raw), 'mimeType': mime, 'text': safe_text, 'text_redacted': redacted},
                          'redirectURL': '', 'headersSize': -1, 'bodySize': len(raw)}, 'cache': {},
             'timings': {k: -1 for k in ['blocked', 'dns', 'connect', 'send', 'wait', 'receive', 'ssl']},
             '_request_body_sha256': sha(raw_request), '_response_body_sha256_before_scrub': sha(raw),
             '_producer': 'Actual urllib request, authorization/cookies omitted, not browser instrumentation'}
    capture.write_json(run / 'network.har', {'log': {'version': '1.2', 'creator': {
        'name': 'probe_pixellab_color_reducer.py', 'version': '1'}, 'entries': [entry]}})
    capture.write_json(run / 'response.json', result)
    valid_result = (isinstance(result, dict) and isinstance(result.get('images'), list)
                    and len(result['images']) == 2 and isinstance(result.get('palette'), dict))
    state = {'status': ('completed' if valid_result else 'response-invalid') if status == 200 and failure is None else 'failed-or-ambiguous',
             'http_status': status, 'transport_failure': failure, 'usage': result.get('usage') if isinstance(result, dict) else None,
             'automatic_retry_allowed': False, 'utc': capture.now()}
    capture.write_json(run / 'state.json', state)
    if status == 200 and valid_result:
        for i, value in enumerate(result.get('images', [])):
            (run / f'output-{i:02}.png').write_bytes(base64.b64decode(value['base64'].split(',')[-1], validate=True))
        if result.get('palette'):
            (run / 'palette.png').write_bytes(base64.b64decode(result['palette']['base64'].split(',')[-1], validate=True))
    return state


def prepare_holdout(root):
    """Fresh input/palette with a prediction fixed before requesting an output."""
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / 'inputs'
    inputs.mkdir()
    rng = np.random.default_rng(20261014)
    first = rng.integers(0, 256, (64, 64, 4), dtype=np.uint8)
    first[..., 3] = 255
    second = first.copy()
    second[..., 3] = np.tile(np.repeat(np.array([0, 64, 128, 255], dtype=np.uint8), 16), (64, 1))
    colors = [[21, 27, 43], [238, 222, 192], [152, 37, 48], [43, 133, 73],
              [47, 68, 167], [206, 147, 43], [121, 74, 146], [53, 153, 163], [130, 119, 113]]
    Image.fromarray(first).save(inputs / 'rgb-holdout.png')
    Image.fromarray(second).save(inputs / 'rgba-holdout.png')
    Image.fromarray(np.array([[c + [255] for c in colors]], dtype=np.uint8)).save(inputs / 'holdout-palette.png')
    run = root / 'weighted-holdout'
    run.mkdir()
    payload = {'images': [descriptor(inputs / name) for name in ['rgb-holdout.png', 'rgba-holdout.png']],
               'palette_image': descriptor(inputs / 'holdout-palette.png'),
               'dithering': 'none', 'dithering_strength': 5.0}
    capture.write_json(run / 'request.json', payload)
    capture.write_json(root / 'PLAN.json', {'version': 1, 'prepared_utc': capture.now(), 'phase': 3,
        'endpoint': ENDPOINT, 'max_posts': 1, 'automatic_retries': 0,
        'requests': [{'variant': 'weighted-holdout', 'request_sha256': sha((run / 'request.json').read_bytes())}],
        'source_seed': 20261014, 'source_rng': 'numpy default_rng/PCG64', 'palette_rgb': colors,
        'predeclared_prediction': 'Nearest fixed palette in Oklab by 0.25*dL^2+da^2+db^2; preserve exact source alpha and quantize hidden RGB too',
        'scope': 'Held-out validation of a fitted nondithered reducer behavior; not private source, clustering, animation conversion, model identity or general uniqueness proof'})
    return {'prepared': str(root), 'variants': list(PHASE3), 'posts': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'submit'])
    parser.add_argument('root', type=Path)
    parser.add_argument('--variant', choices=VARIANTS | PHASE2 | PHASE3)
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], default=1)
    args = parser.parse_args()
    if args.action == 'submit' and not args.variant:
        parser.error('--variant required for submit')
    print(json.dumps((prepare_holdout(args.root) if args.phase == 3 else prepare(args.root, args.phase))
                     if args.action == 'prepare' else submit(args.root, args.variant)))
