"""Execute pinned, unchanged shipped client methods in an isolated Godot host.

Capture is an explicit flattened-RGBA input; undo is an output sink. These
boundaries do not recreate PixelLab's private image/video processing service.
"""
from __future__ import annotations

from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image

from .core import ValidationError, UnsupportedCapability, canonical_json, digest, validate_raster

MAX_SIDE = 512
MAX_BYTES = MAX_SIDE * MAX_SIDE * 4
MAX_ENCODED_BYTES = 2 * MAX_BYTES
_VENDOR = Path(__file__).parent / 'vendor' / 'parity_pixels'
_MANIFEST_SHA = 'eef1442ea3df2a3340db1e1fb44287c6357cb1339d10ea0116e8a87567a785b1'
OPERATIONS = ('serialize', 'transparency', 'reference_palette', 'mask', 'decode', 'place')
BOUNDARY = ('Unchanged shipped Godot client method bodies. Supplied flattened capture and undo sink; '
            'not private cutout, quantization, video conversion or full editor parity.')


def _bundle():
    try:
        raw = (_VENDOR / 'manifest.json').read_bytes()
        if digest(raw) != _MANIFEST_SHA:
            raise ValidationError('Original pixel method manifest integrity failed')
        manifest = json.loads(raw)
        sources = {}
        for name, pin in manifest['files'].items():
            content = (_VENDOR / name).read_bytes()
            if digest(content) != pin:
                raise ValidationError('Original pixel source integrity failed')
            sources[name] = content.decode('utf8')
        host = (_VENDOR / 'host.gd.fragment').read_bytes()
        for method, entry in manifest['methods'].items():
            match = re.search(r'^func ' + re.escape(method) + r'\(.*?(?=^func |\Z)',
                              sources[entry['file']], re.M | re.S)
            if not match or digest(match.group().encode()) != entry['sha256']:
                raise ValidationError('Original pixel function slice integrity failed')
            host += b'\n' + match.group().encode()
        return manifest, host, (_VENDOR / 'runner.gd').read_bytes()
    except OSError as exc:
        raise UnsupportedCapability('local.original_pixels', 'Packaged original pixel sources unavailable') from exc


def describe():
    manifest, _, _ = _bundle()
    return {'operations': list(OPERATIONS), 'source_manifest_sha256': _MANIFEST_SHA,
            'source_provenance': manifest, 'boundary': BOUNDARY,
            'limits': {'side': MAX_SIDE, 'raw_bytes': MAX_BYTES, 'encoded_bytes': MAX_ENCODED_BYTES,
                       'wall_seconds': 30, 'cpu_seconds': 20, 'address_space_bytes': 4294967296},
            'mask_encodings': {'mask_output': 'opaque black=protect, opaque white=edit; consume RGB',
                               'place_preserve_mask': 'alpha>0 copies source, alpha0 protects destination',
                               'manual_selection': 'separate white RGB/binary alpha; consume alpha'},
            'reference_palette': '64x64 unique visible RGBA, x-major first-seen order, at most4096 entries; not server quantizer'}


def _dimensions(width, height):
    if type(width) is not int or type(height) is not int or not 1 <= width <= MAX_SIDE or not 1 <= height <= MAX_SIDE:
        raise ValidationError('Original pixel canvas must be1..512 per side')


def _raster(store, ident):
    # Validate before loading bytes: avoid expanding a larger Store artifact.
    meta = store.get_json(ident)
    _dimensions(meta.get('width'), meta.get('height'))
    result = store.get_raster(ident)
    validate_raster(result)
    return result


def _pair(value, name, *, negative=False):
    if not isinstance(value, list) or len(value) != 2 or any(type(v) is not int for v in value):
        raise ValidationError(name + ' must be integer XY')
    low = -MAX_SIDE if negative else 1
    if any(v < low or v > MAX_SIDE for v in value):
        raise ValidationError(name + ' exceeds bounded geometry')
    return value


def _engine(operation, arrays, controls, received=None):
    manifest, host, runner = _bundle()
    godot, prlimit = shutil.which('godot'), shutil.which('prlimit')
    if not godot or not prlimit:
        raise UnsupportedCapability('local.original_pixels.' + operation, 'Godot4 and Linux prlimit required on PATH')
    with tempfile.TemporaryDirectory(prefix='workbench-original-pixels-') as directory:
        root = Path(directory)
        request = {'operation': operation, 'dimensions': {}, **controls}
        for name, array in arrays.items():
            height, width = array.shape[:2]
            _dimensions(width, height)
            request['dimensions'][name] = [width, height]
            (root / (name + '.rgba')).write_bytes(array.tobytes())
        if received is not None:
            (root / 'received.bin').write_bytes(received)
        (root / 'request.json').write_bytes(canonical_json(request))
        (root / 'host.gd').write_bytes(host)
        (root / 'main.gd').write_bytes(runner)
        (root / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="Original pixel methods"\n[threading]\nworker_pool/max_threads=2\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
        for name in ('home', 'data', 'cache', 'config'):
            (root / name).mkdir()
        env = {'PATH': os.defpath, 'LANG': 'C.UTF-8', 'HOME': str(root / 'home'),
               'XDG_DATA_HOME': str(root / 'data'), 'XDG_CACHE_HOME': str(root / 'cache'),
               'XDG_CONFIG_HOME': str(root / 'config')}
        command = [prlimit, '--as=4294967296', '--cpu=20', '--fsize=2097152', '--nofile=128',
                   '--', godot, '--headless', '--quit-after', '1800', '--path', directory, '--script', 'res://main.gd']
        with (root / 'engine.log').open('w+b') as log:
            try:
                process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                         env=env, timeout=30, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise UnsupportedCapability('local.original_pixels.' + operation, 'Bounded original method execution unavailable or timed out') from exc
            log.seek(0)
            raw_log = log.read(65537)
        lines = raw_log.decode('utf8', errors='replace').splitlines()
        if (process.returncode or len(raw_log) > 65536 or lines.count('PIXELS_OK') != 1
                or any('SCRIPT ERROR:' in line or line.startswith('ERROR:') for line in lines)):
            raise UnsupportedCapability('local.original_pixels.' + operation, 'Original method host failed within resource limits')
        try:
            observed = json.loads((root / 'result.json').read_bytes())
            if observed.get('input_unchanged') is not True:
                raise ValidationError('Original method changed supplied input')
            output = None
            if operation != 'transparency':
                w, h = observed['width'], observed['height']
                _dimensions(w, h)
                raw = (root / 'output.rgba').read_bytes()
                if len(raw) != w * h * 4 or observed['raw_size'] != len(raw):
                    raise ValidationError('Original method output dimensions differ')
                output = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
            elif type(observed.get('has_exact_zero_alpha')) is not bool:
                raise ValidationError('Original method transparency result invalid')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValidationError('Original method produced invalid output') from exc
        execution = {'engine': next((line for line in lines if line.startswith('Godot Engine')), 'Godot4'),
                     'input_unchanged': True, 'host_sha256': digest(host), 'runner_sha256': digest(runner),
                     'source_manifest_sha256': _MANIFEST_SHA,
                     'method_sha256': {name: entry['sha256'] for name, entry in manifest['methods'].items()}}
        return output, observed, execution


def _encoded_input(store, media, width, height):
    _dimensions(width, height)
    raw = store.get_bytes(media, max_bytes=MAX_ENCODED_BYTES)
    # Match original PNG branch detection, but reject malformed/unbounded inputs
    # before calling the original decoder. Valid raw RGBA is otherwise exact.
    png = len(raw) >= 8 and raw[:4] == b'\x89PNG'
    if png:
        try:
            with Image.open(BytesIO(raw)) as image:
                if image.format != 'PNG' or getattr(image, 'n_frames', 1) != 1:
                    raise ValidationError('Only a single bounded PNG is accepted')
                _dimensions(*image.size)
                image.verify()
        except (OSError, ValueError, SyntaxError) as exc:
            raise ValidationError('Invalid or unbounded received PNG') from exc
    elif len(raw) != width * height * 4:
        raise ValidationError('Raw received RGBA length differs from dimensions')
    return raw, 'png' if png else 'raw-rgba'


def execute(store, operation, **request):
    """Return immutable input/output hashes and a source-stamped method receipt."""
    if operation not in OPERATIONS:
        raise ValidationError('Unknown original pixel operation')
    fields = {'serialize': ({'raster'}, set()), 'transparency': ({'raster'}, set()),
              'reference_palette': ({'raster'}, set()),
              'mask': ({'mask', 'art'}, {'fill_background', 'inpaint_empty_image'}),
              'decode': ({'media', 'width', 'height'}, set()),
              'place': ({'source', 'destination'}, {'origin', 'extent', 'preserve_mask'})}
    required, optional = fields[operation]
    if required - request.keys() or request.keys() - required - optional:
        raise ValidationError('Original pixel request fields differ')
    controls, arrays, received = {}, {}, None
    if operation in ('serialize', 'transparency', 'reference_palette'):
        arrays['input'] = _raster(store, request['raster'])
    elif operation == 'mask':
        arrays = {name: _raster(store, request[name]) for name in ('mask', 'art')}
        if arrays['mask'].shape != arrays['art'].shape:
            raise ValidationError('Mask and art capture dimensions differ')
        for name in ('fill_background', 'inpaint_empty_image'):
            controls[name] = request.get(name, False)
            if type(controls[name]) is not bool:
                raise ValidationError('Mask controls must be boolean')
    elif operation == 'decode':
        received, encoding = _encoded_input(store, **request)
        controls = {'width': request['width'], 'height': request['height'], 'encoding': encoding}
    else:
        arrays = {name: _raster(store, request[name]) for name in ('source', 'destination')}
        h, w = arrays['source'].shape[:2]
        controls = {'source_size': [w, h], 'origin': _pair(request.get('origin', [0, 0]), 'origin', negative=True),
                    'extent': _pair(request.get('extent', [w, h]), 'extent')}
        if 'preserve_mask' in request:
            arrays['preserve_mask'] = _raster(store, request['preserve_mask'])
            if arrays['preserve_mask'].shape != arrays['source'].shape:
                raise ValidationError('Placement preserve mask must match source dimensions')
    output, observed, execution = _engine(operation, arrays, controls, received)
    receipt = {'kind': 'original-pixel-method', 'version': 1, 'operation': operation,
               'request': request, 'controls': controls, 'execution': execution,
               'input_rgba_sha256': {name: digest(array.tobytes()) for name, array in arrays.items()},
               'boundary': BOUNDARY}
    if output is not None:
        receipt.update(output_raster=store.put_raster(output), output_rgba_sha256=digest(output.tobytes()),
                       width=output.shape[1], height=output.shape[0])
        if operation == 'serialize':
            receipt.update(raw_rgba=store.put_bytes(output.tobytes()), encoding='raw-rgba; not PNG')
        if operation == 'mask':
            receipt['mask_encoding'] = 'opaque black=protect, opaque white=edit; consume RGB, not alpha'
        if operation == 'reference_palette':
            count = int(np.count_nonzero(output[..., 3]))
            receipt.update(palette_entries=count, capacity=4096, order='x-major input and output; unique visible RGBA once')
    else:
        receipt['has_exact_zero_alpha'] = observed['has_exact_zero_alpha']
    return {'receipt': store.put_json(receipt), **receipt}


def verify_receipt(store, receipt):
    """Re-execute before promotion; public source hashes alone are not proof.

    A valid local receipt is deterministic on its recorded Godot runtime. A
    different engine version requires a fresh explicit execution/receipt.
    """
    doc = store.get_json(receipt)
    common = {'kind', 'version', 'operation', 'request', 'controls', 'execution',
              'input_rgba_sha256', 'boundary'}
    if (doc.get('kind') != 'original-pixel-method' or type(doc.get('version')) is not int
            or doc['version'] != 1 or not isinstance(doc.get('operation'), str)
            or doc['operation'] not in OPERATIONS or not isinstance(doc.get('request'), dict)
            or not isinstance(doc.get('execution'), dict)):
        raise ValidationError('Expected a complete original pixel receipt')
    extra = {'has_exact_zero_alpha'} if doc['operation'] == 'transparency' else {
        'output_raster', 'output_rgba_sha256', 'width', 'height'}
    extra |= {'serialize': {'raw_rgba', 'encoding'}, 'mask': {'mask_encoding'},
              'reference_palette': {'palette_entries', 'capacity', 'order'}}.get(doc['operation'], set())
    if set(doc) != common | extra:
        raise ValidationError('Original pixel receipt fields differ')
    manifest, host, runner = _bundle()
    execution = doc['execution']
    expected = {'source_manifest_sha256': _MANIFEST_SHA, 'host_sha256': digest(host),
                'runner_sha256': digest(runner), 'input_unchanged': True,
                'method_sha256': {name: entry['sha256'] for name, entry in manifest['methods'].items()}}
    if (set(execution) != set(expected) | {'engine'} or
            any(canonical_json({'v': execution.get(k)}) != canonical_json({'v': v}) for k, v in expected.items())
            or not isinstance(execution.get('engine'), str)):
        raise ValidationError('Original pixel execution provenance differs')
    replayed = execute(store, doc['operation'], **doc['request'])
    if replayed['receipt'] != receipt:
        raise ValidationError('Original pixel receipt differs from actual Godot replay; execute again on this runtime')
    return doc
