#!/usr/bin/env python3
"""Matched PixelLab public comparison. Preparation/extraction are offline.

Only submit makes a paid POST, once per persistently claimed run. No retries.
HAR is producer HTTP evidence, not browser capture. No native H3 FPS is inferred.
"""
from __future__ import annotations
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import io
from http.client import IncompleteRead
import json
import os
from pathlib import Path
import re
import time
from urllib import error, request
import zipfile

API = 'https://api.pixellab.ai'
EXTENSION = Path('/home/astra/projects/pixellab-local-test-20261011/extension-download/PixelLab.aseprite-extension')
MAX_BODY = 16 * 1024 * 1024
MAX_HAR = 32 * 1024 * 1024


def now(): return datetime.now(timezone.utc).isoformat()
def digest(raw): return hashlib.sha256(raw).hexdigest()
def read_json(path): return json.loads(path.read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w') as stream:
        json.dump(value, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def verify_inputs(run):
    case = read_json(run / 'case.json')
    for name, expected in case['input_hashes'].items():
        path = run / name
        if not path.resolve().is_relative_to(run.resolve()) or digest(path.read_bytes()) != expected:
            raise ValueError('Prepared input changed')
    return case


def prepare(run, native_run):
    native_case = read_json(native_run / 'case.json')
    hashes = native_case['input_hashes']
    if not {'source.png', 'request.json'} <= set(hashes):
        raise ValueError('Native case must pin its source and actual request')
    for name, expected in hashes.items():
        path = native_run / name
        if not path.resolve().is_relative_to(native_run.resolve()) or digest(path.read_bytes()) != expected:
            raise ValueError('Native prepared input changed')
    source = (native_run / 'source.png').read_bytes()
    native = read_json(native_run / 'request.json')
    texts = [x['text'] for x in native['content'] if x.get('type') == 'text']
    images = [x for x in native['content'] if x.get('type') == 'image_url']
    if len(texts) != 1 or len(images) != 1 or images[0].get('role') != 'first_frame':
        raise ValueError('Matched pilot requires exactly one literal prompt and one first-frame image')
    uri = images[0]['image_url']['url']
    if not uri.startswith('data:image/png;base64,') or base64.b64decode(uri.split(',', 1)[1], validate=True) != source:
        raise ValueError('Native submitted PNG does not match retained source')
    from PIL import Image
    with Image.open(io.BytesIO(source)) as image:
        if image.format != 'PNG' or image.size != (256, 256) or getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Matched pilot requires a single 256x256 PNG')
    payload = {'first_frame': {'type': 'base64', 'base64': uri, 'format': 'png'},
               'description': texts[0], 'frame_count': 16, 'seed': 123,
               'no_background': True, 'enhance_prompt': False}
    run.mkdir(parents=True, exist_ok=False)
    (run / 'source.png').write_bytes(source)
    write_json(run / 'request.json', payload)
    pair = {'version': 1, 'native_run': str(native_run.resolve()), 'native_case_sha256': digest((native_run / 'case.json').read_bytes()),
            'native_request_sha256': digest((native_run / 'request.json').read_bytes()),
            'source_png_sha256': digest(source), 'literal_prompt_sha256': digest(texts[0].encode()),
            'image_bytes_match': True, 'literal_prompt_match': True,
            'native_contract': {k: native.get(k) for k in ['model', 'duration', 'resolution', 'ratio']},
            'pixellab_contract': {k: payload[k] for k in ['frame_count', 'seed', 'no_background', 'enhance_prompt']},
            'omitted_pixellab_fields': ['last_frame', 'subject_description', 'initial_pose', 'view', 'direction'],
            'unmatched_controls': {'frame_count': '16 PixelLab generated frames; native seconds are not a frame-count mapping',
                'seed': '123 in PixelLab only; native inspected H3 V2 has no seed field',
                'no_background': 'PixelLab true; no native H3 output-alpha guarantee',
                'enhance_prompt': 'PixelLab false; no native Context-IR request or private processing parity established',
                'resolution': 'Native video resolution is not the 256px PixelLab sprite canvas',
                'fps': 'Native source FPS unknown until video inspection; PixelLab nominal 2-second review player is analyst-selected'},
            'same_subject_as_old_pixellab_capture': False,
            'scope': 'New generic RPG subject and matched literal inputs; historical PixelLab capture is a method reference only',
            'checkpoint_or_private_conversion_parity': False}
    write_json(run / 'pair.json', pair)
    write_json(run / 'case.json', {'version': 1, 'created_utc': now(), 'input_hashes': {
        name: digest((run / name).read_bytes()) for name in ['source.png', 'request.json', 'pair.json']}})
    write_json(run / 'state.json', {'status': 'prepared', 'submission_attempts': 0})
    return {'status': 'prepared', 'run': str(run), 'source_png_sha256': digest(source),
            'literal_prompt_sha256': pair['literal_prompt_sha256']}


def credential():
    # Authorized personal extension key. No fallback, environment, printing or token persistence.
    with zipfile.ZipFile(EXTENSION) as archive:
        names = [n for n in archive.namelist() if n.endswith('/package.json')]
        if len(names) != 1: raise ValueError('Expected exactly one extension package manifest')
        value = json.loads(archive.read(names[0])).get('secret')
    if not isinstance(value, str) or not value.strip(): raise ValueError('Extension key missing')
    return value


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None


def sanitize_response(raw, token):
    """Scrub decoded JSON keys/values, including Unicode-escaped credentials.

    Preserve exact response text when safe; a redacted JSON representation is
    explicitly marked and its original bytes remain bound only by their hash.
    """
    text = raw.decode('utf-8', errors='replace')
    try:
        parsed = json.loads(text)
    except (ValueError, UnicodeDecodeError):
        safe_text = text.replace(token, '[REDACTED]')
        return ({'non_json_body': True, 'body_sha256_before_scrub': digest(raw), 'bytes': len(raw)},
                safe_text, safe_text != text)
    changed = False

    def scrub(value):
        nonlocal changed
        if isinstance(value, str):
            if token in value:
                changed = True
                return value.replace(token, '[REDACTED]')
            return value
        if isinstance(value, list): return [scrub(item) for item in value]
        if isinstance(value, dict): return {scrub(key): scrub(item) for key, item in value.items()}
        return value

    clean = scrub(parsed)
    safe_text = json.dumps(clean, sort_keys=True, separators=(',', ':'), ensure_ascii=False) if changed else text
    return clean, safe_text, changed


def _capture(run, method, path, token, payload=None):
    allowed = ((method == 'POST' and path == '/v2/animate-pixminimax') or
               (method == 'GET' and (path == '/v2/balance' or
                re.fullmatch(r'/v2/background-jobs/[A-Za-z0-9_-]+', path))))
    if not allowed: raise ValueError('Unexpected method or destination')
    har_path = run / 'network.har'
    har = read_json(har_path) if har_path.exists() else {'log': {'version': '1.2',
        'creator': {'name': 'pixellab_h3_comparison.py producer HTTP recorder', 'version': '1'},
        'comment': 'Actual urllib calls, not browser instrumentation. Authorization/cookies omitted before persistence.', 'entries': []}}
    # Stop before another call once cumulative evidence could crowd out a bounded response.
    if len(json.dumps(har).encode()) > MAX_HAR // 3:
        raise ValueError('HAR retention budget exhausted before another request')
    raw_request = b'' if payload is None else json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
    if len(raw_request) > MAX_BODY: raise ValueError('Request exceeds body limit')
    req = request.Request(API + path, data=None if payload is None else raw_request, method=method,
                          headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    started = now(); clock = time.monotonic(); status = 0; mime = ''; raw = b''; transport = 'response'
    try:
        try: response = request.build_opener(NoRedirect).open(req, timeout=60)
        except error.HTTPError as exc: response = exc
        with response:
            status = response.code; mime = response.headers.get('Content-Type', '')
            raw = response.read(MAX_BODY + 1)
            if len(raw) > MAX_BODY:
                raw = raw[:MAX_BODY]; transport = 'response-body-limit'
    except (error.URLError, TimeoutError, OSError, IncompleteRead) as exc:
        transport = 'failed-or-ambiguous'; transport_type = type(exc).__name__
        if isinstance(getattr(exc, 'partial', None), bytes): raw = exc.partial[:MAX_BODY]
    elapsed = round((time.monotonic() - clock) * 1000, 3)
    # Hash untouched response bytes, then scrub the known credential before any disk write.
    result, text, text_redacted = sanitize_response(raw, token)
    safe_request = raw_request.decode().replace(token, '[REDACTED]')
    entry = {'startedDateTime': started, 'time': elapsed,
             'request': {'method': method, 'url': API + path, 'httpVersion': '',
                'headers': [{'name': 'Content-Type', 'value': 'application/json'}], 'cookies': [], 'queryString': [],
                'headersSize': -1, 'bodySize': len(raw_request)},
             'response': {'status': status, 'statusText': '', 'httpVersion': '',
                'headers': [{'name': 'Content-Type', 'value': mime}] if mime else [], 'cookies': [],
                'content': {'size': len(raw), 'mimeType': mime, 'text': text, 'text_redacted': text_redacted}, 'redirectURL': '', 'headersSize': -1, 'bodySize': len(raw)},
             'cache': {}, 'timings': {k: -1 for k in ['blocked', 'dns', 'connect', 'send', 'wait', 'receive', 'ssl']},
             '_producer': 'urllib actual request/response; component timings unavailable',
             '_request_body_sha256': digest(raw_request), '_response_body_sha256_before_scrub': digest(raw),
             '_response_body_sha256_scope': 'complete-body' if transport == 'response' else 'retained-prefix-only', '_transport': transport}
    if payload is not None: entry['request']['postData'] = {'mimeType': 'application/json', 'text': safe_request}
    if transport == 'failed-or-ambiguous': entry['_transport_error_type'] = transport_type
    if transport == 'response-body-limit': entry['_response_truncated'] = True
    har['log']['entries'].append(entry)
    write_json(har_path, har)
    if har_path.stat().st_size > MAX_HAR: raise ValueError('HAR exceeded declared case budget; retained evidence, stop further requests')
    return {'http_status': status or None, 'elapsed_ms': elapsed, 'transport': transport}, result


def submit(run):
    verify_inputs(run); state = read_json(run / 'state.json')
    if state.get('status') != 'prepared' or state.get('submission_attempts') != 0:
        raise ValueError('Submission already attempted; never duplicate a paid job')
    token = credential()
    fd = os.open(run / '.submission.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try: os.fsync(fd)
    finally: os.close(fd)
    state.update(status='submission-attempted', submission_attempts=1, submitted_utc=now())
    write_json(run / 'state.json', state)
    meta, body = _capture(run, 'POST', '/v2/animate-pixminimax', token, read_json(run / 'request.json'))
    write_json(run / 'submit-response.json', {'captured_utc': now(), **meta, 'body': body})
    job = body.get('background_job_id') if isinstance(body, dict) else None
    if meta['http_status'] == 200 and isinstance(job, str) and re.fullmatch('[A-Za-z0-9_-]+', job):
        state.update(status='accepted', background_job_id=job)
    else: state['status'] = ('submission-failed' if meta['http_status'] and meta['transport'] == 'response' else 'submission-ambiguous')
    write_json(run / 'state.json', state)
    return {'status': state['status'], **meta}


def poll(run):
    verify_inputs(run); state = read_json(run / 'state.json'); job = state.get('background_job_id')
    if not isinstance(job, str) or not re.fullmatch('[A-Za-z0-9_-]+', job): raise ValueError('No accepted job; nothing queried')
    meta, body = _capture(run, 'GET', '/v2/background-jobs/' + job, credential())
    folder = run / 'polls'; folder.mkdir(exist_ok=True); index = len(list(folder.glob('*.json')))
    write_json(folder / f'{index:04d}.json', {'captured_utc': now(), **meta, 'body': body})
    if meta['http_status'] == 200 and isinstance(body, dict):
        state.update(status=body.get('status', state['status']), last_polled_utc=now())
        if body.get('status') == 'completed': write_json(run / 'completed-response.json', body)
    write_json(run / 'state.json', state)
    return {'status': state['status'], **meta, 'poll_index': index}


def balance(run, output=None):
    run.mkdir(parents=True, exist_ok=True)
    meta, body = _capture(run, 'GET', '/v2/balance', credential())
    write_json(output or run / ('balance-' + str(time.time_ns()) + '.json'), {'captured_utc': now(), **meta, 'body': body})
    return {'status': 'balance-recorded', **meta}


def extract(run):
    verify_inputs(run)
    response = read_json(run / 'completed-response.json')
    if response.get('status') != 'completed': raise ValueError('Only final completed images may be extracted')
    images = response.get('last_response', {}).get('images')
    if not isinstance(images, list) or not images: raise ValueError('Completed response has no images')
    from PIL import Image, ImageDraw
    out = run / 'extracted'; out.mkdir(exist_ok=False)
    source_raw = (run / 'source.png').read_bytes()
    with Image.open(io.BytesIO(source_raw)) as im: source = im.convert('RGBA'); source.load()
    frames = []; rows = []
    for index, value in enumerate(images):
        encoded = value.get('base64') if isinstance(value, dict) else value
        if not isinstance(encoded, str): raise ValueError('Expected encoded PNG image')
        if encoded.startswith('data:'):
            if not encoded.startswith('data:image/png;base64,'): raise ValueError('Unexpected image media type')
            encoded = encoded.split(',', 1)[1]
        raw = base64.b64decode(encoded, validate=True)
        with Image.open(io.BytesIO(raw)) as im:
            if im.format != 'PNG' or getattr(im, 'n_frames', 1) != 1: raise ValueError('Expected one PNG per returned image')
            frame = im.convert('RGBA'); frame.load()
        name = f'frame-{index:03d}.png'; (out / name).write_bytes(raw)
        rgba = frame.tobytes(); alpha = frame.getchannel('A'); counts = alpha.histogram()
        palette = frame.getcolors(maxcolors=frame.width * frame.height) or []
        rows.append({'index': index, 'file': name, 'role': 'returned reference slot 0' if index == 0 else 'generated slot per PixelLab count+1 contract',
            'png_sha256': digest(raw), 'decoded_rgba_sha256': digest(rgba), 'canvas': list(frame.size),
            'alpha': {'zero': counts[0], 'partial': sum(counts[1:255]), 'opaque': counts[255]},
            'unique_rgba_colours': len(palette), 'visible_unique_rgba_colours': sum(1 for _, colour in palette if colour[3] > 0)})
        frames.append(frame)
    first = rows[0]
    manifest = {'version': 1, 'expected_count': 17, 'actual_count': len(rows), 'requested_generated_frames': 16,
        'source_png_sha256': digest(source_raw), 'returned_0_byte_identity': first['png_sha256'] == digest(source_raw),
        'returned_0_decoded_identity': frames[0].size == source.size and frames[0].tobytes() == source.tobytes(),
        'reference_handling': 'All returned images retained in order. Slot0 shown separately, not deduplicated.',
        'native_fps': None, 'review_timing': 'Nominal 2-second inspection cycle over returned slots1..N; analyst-selected, not provider FPS',
        'pixellab_checkpoint_or_conversion_parity': False, 'frames': rows}
    generated = frames[1:]
    if generated:
        w = max(f.width for f in generated); h = max(f.height for f in generated); columns = min(4, len(generated)); nrows = (len(generated)+columns-1)//columns
        atlas = Image.new('RGBA', (w*columns, h*nrows))
        contact = Image.new('RGB', (w*columns, (h+22)*nrows), '#dddddd'); draw = ImageDraw.Draw(contact)
        for i, f in enumerate(generated):
            x, y = (i % columns)*w, (i // columns)*h; atlas.paste(f, (x, y))
            cy = (i // columns)*(h+22)
            for yy in range(0, h, 8):
                for xx in range(0, w, 8): draw.rectangle((x+xx,cy+yy,x+min(xx+7,w-1),cy+min(yy+7,h-1)),fill='#dddddd' if (xx//8+yy//8)%2 else '#888888')
            contact.paste(f, (x, cy), f); draw.text((x+3,cy+h+3),f'returned {i+1}',fill='black')
        atlas.save(out / 'generated-atlas.png'); contact.save(out / 'generated-contact-checker.png')
    names = [row['file'] for row in rows[1:]]
    html = '''<!doctype html><meta charset="utf-8"><title>Matched PixelLab inspection</title><style>body{background:#222;color:white}img{image-rendering:pixelated;background:repeating-conic-gradient(#888 0 25%,#ddd 0 50%) 0/16px 16px}</style><h1>PixelLab returned PNG inspection</h1><p>Reference slot0 shown separately. Playback below is an analyst-selected nominal 2-second cycle, not native FPS. No quality or conversion-parity claim.</p><h2>Returned reference0</h2><img src="frame-000.png"><h2>Generated slots1..N</h2><button id="toggle">Pause / play</button><input id="seek" type="range" min="0" value="0"><span id="label"></span><br><img id="player"><script>const files=FILES;let i=0,play=true;const p=document.querySelector('#player'),s=document.querySelector('#seek'),l=document.querySelector('#label');s.max=Math.max(0,files.length-1);function show(){if(files.length){p.src=files[i];s.value=i;l.textContent='returned '+(i+1)}}s.oninput=()=>{play=false;i=Number(s.value);show()};document.querySelector('#toggle').onclick=()=>play=!play;show();if(files.length)setInterval(()=>{if(play){i=(i+1)%files.length;show()}},2000/files.length);</script>'''.replace('FILES', json.dumps(names))
    (out / 'index.html').write_text(html)
    write_json(out / 'manifest.json', manifest)
    return {'status': 'extracted', 'expected': 17, 'actual': len(rows), 'reference0_byte_identity': manifest['returned_0_byte_identity'], 'reference0_decoded_identity': manifest['returned_0_decoded_identity']}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('command', choices=['prepare','submit','poll','extract','balance']); parser.add_argument('run', type=Path)
    parser.add_argument('--native-run', type=Path); parser.add_argument('--output', type=Path); args = parser.parse_args()
    try:
        run = args.run.resolve()
        if args.command == 'prepare':
            if args.native_run is None: parser.error('prepare requires --native-run')
            result = prepare(run, args.native_run.resolve())
        elif args.command == 'balance': result = balance(run, args.output)
        else: result = {'submit': submit, 'poll': poll, 'extract': extract}[args.command](run)
        print(json.dumps(result))
    except Exception as exc:
        print(json.dumps({'status':'error','type':type(exc).__name__,'details':'Inspect retained local state/evidence; no automatic retry.'})); raise SystemExit(2)


if __name__ == '__main__': main()
