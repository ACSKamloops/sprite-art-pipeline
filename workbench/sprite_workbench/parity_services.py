"""Explicit source-backed client operations, separate from private vendor APIs."""
from fractions import Fraction
import threading

from .construction_services import ID, TEXT, schema
from .core import ValidationError, digest, canonical_json, save_sequence

PAIR = {'type': 'array', 'minItems': 2, 'maxItems': 2, 'items': {'type': 'integer'}}
COMMAND = {'oneOf': [
    schema({'method': {'const': 'ellipse-outline'}, 'pos': PAIR, 'size': PAIR}, ['method', 'pos', 'size']),
    schema({'method': {'const': 'ellipse-filled'}, 'pos': PAIR, 'size': PAIR,
            'thickness': {'type': 'integer'}}, ['method', 'pos', 'size', 'thickness']),
    schema({'method': {'const': 'rounded-rect-outline'}, 'pos': PAIR, 'size': PAIR,
            'radius': {'type': 'integer'}, 'thickness': {'type': 'integer'}},
           ['method', 'pos', 'size', 'radius', 'thickness']),
    schema({'method': {'const': 'rounded-rect-filled'}, 'pos': PAIR, 'size': PAIR,
            'radius': {'type': 'integer'}}, ['method', 'pos', 'size', 'radius']),
]}
PIXEL_REQUESTS = {
    'serialize': schema({'raster': ID}, ['raster']),
    'transparency': schema({'raster': ID}, ['raster']),
    'reference_palette': schema({'raster': ID}, ['raster']),
    'mask': schema({'mask': ID, 'art': ID, 'fill_background': {'type': 'boolean'},
                    'inpaint_empty_image': {'type': 'boolean'}}, ['mask', 'art']),
    'decode': schema({'media': ID, 'width': {'type': 'integer', 'minimum': 1, 'maximum': 512},
                      'height': {'type': 'integer', 'minimum': 1, 'maximum': 512}}, ['media', 'width', 'height']),
    'place': schema({'source': ID, 'destination': ID, 'origin': PAIR, 'extent': PAIR,
                     'preserve_mask': ID}, ['source', 'destination']),
}
SCHEMAS = {
    'catalog': schema({}, []),
    'palette': schema({'raster': ID}, ['raster']),
    'pixels': {'oneOf': [schema({'operation': {'const': op}, 'request': request},
                                ['operation', 'request']) for op, request in PIXEL_REQUESTS.items()]},
    'footprints': schema({'commands': {'type': 'array', 'minItems': 1, 'maxItems': 16,
                                      'items': COMMAND}}, ['commands']),
    'paint': schema({'history': ID, 'cel_id': TEXT, 'command': COMMAND,
                     'palette_index': {'type': 'integer', 'minimum': 0}},
                    ['history', 'cel_id', 'command', 'palette_index']),
    'to_sequence': schema({'receipt': ID, 'duration': {'type': 'array', 'minItems': 2, 'maxItems': 2,
                                                    'items': {'type': 'integer', 'minimum': 1, 'maximum': 1000000}}},
                          ['receipt', 'duration']),
}


def palette(store, raster):
    from . import parity_pixels, parity_palette
    pixels = parity_pixels._raster(store, raster)
    result = parity_palette.import_palette_image(pixels)
    doc = {'kind': 'original-palette-import', 'version': 1, 'source_raster': raster, **result,
           'decoder_boundary': 'Supplied RGBA. Browser canvas PNG decoding is not repeated by this service; partial-alpha RGB can differ.'}
    return {'receipt': store.put_json(doc), **doc}


def to_sequence(store, receipt, duration):
    """Explicit one-frame preview/export, retaining all source receipts in closure."""
    from . import parity_pixels
    doc = parity_pixels.verify_receipt(store, receipt)
    if 'output_raster' not in doc:
        raise ValidationError('Original pixel operation has no image output')
    if (not isinstance(duration, list) or len(duration) != 2 or
            any(type(v) is not int or not 1 <= v <= 1000000 for v in duration)):
        raise ValidationError('Declare a positive exact still-image hold numerator/denominator')
    output = parity_pixels._raster(store, doc['output_raster'])
    if digest(output.tobytes()) != doc['output_rgba_sha256']:
        raise ValidationError('Pixel output receipt hash differs')
    sequence = save_sequence(store, [output], durations=[Fraction(*duration)], loop=False,
        metadata={'source_ids': [receipt], 'boundary': 'Explicit single still and authored hold; no animation generation',
                  'original_pixel_operation': doc['operation']})
    return {'sequence': sequence, 'receipt': receipt, 'frames': 1, 'duration': duration,
            'boundary': 'Explicit source-bound still; no inferred motion'}


def bind_parity(registry, store, *, base_dir=None):
    from . import parity_pixels, parity_commands, parity_palette
    slots = threading.BoundedSemaphore(2)
    def bounded(fn, request):
        if not slots.acquire(blocking=False):
            raise ValidationError('Two original-source operations are active; wait before retrying')
        try:
            return fn(**request)
        finally:
            slots.release()
    def catalog():
        from pathlib import Path
        import json
        delta = json.loads((Path(__file__).parent / 'contracts/PUBLIC-DELTA-20261014.json').read_bytes())
        return {'kind': 'original-client-methods-catalog', 'version': 1,
                'pixels': parity_pixels.describe(), 'footprints': parity_commands.describe(),
                'palette': {'policy': parity_palette.POLICY,
                            'source_asset_sha256': parity_palette.SOURCE_SHA256,
                            'boundary': 'Shipped image-to-palette handler on canvas-equivalent RGBA; no private clustering/dithering'},
                'schemas': SCHEMAS, 'public_contract_delta': delta,
                'whole_system_parity': False, 'boundary': 'Useful recovered client operations; private models and hosted command execution remain unresolved'}
    def footprints(commands):
        result = parity_commands.evaluate(commands)
        return {'footprint': store.put_json(result), **result}
    handlers = {
        'catalog': lambda r: catalog(),
        'palette': lambda r: bounded(lambda **q: palette(store, **q), r),
        'pixels': lambda r: bounded(lambda operation, request: parity_pixels.execute(store, operation, **request), r),
        'footprints': lambda r: bounded(footprints, r),
        'paint': lambda r: bounded(lambda **q: parity_commands.paint_primitive(store, **q), r),
        'to_sequence': lambda r: to_sequence(store, **r),
    }
    for method, handler in handlers.items():
        registry.register_local('local.parity.' + method, handler,
            classification='supplied-art' if method in ('paint', 'to_sequence') else 'deterministic-source',
            request_schema=SCHEMAS[method],
            evidence={'implementation': 'sprite_workbench.parity_services',
                      'boundary': 'Original shipped client math/pixel methods plus declared local adapters, no private vendor-equivalence claim'})


def invoke_parity(store, method, request, *, base_dir=None):
    from .capabilities import CapabilityRegistry
    if method not in SCHEMAS:
        raise ValidationError('Unknown original-source local method')
    registry = CapabilityRegistry()
    bind_parity(registry, store, base_dir=base_dir)
    return registry.invoke('local.parity.' + method, request)
