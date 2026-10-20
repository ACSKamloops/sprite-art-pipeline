"""Frozen, observed prepared-effect instances; never a private constructor."""
import copy
from collections import Counter
import json
import re
from pathlib import Path

from .core import ValidationError, canonical_json, digest
from .effects import PINNED_MANIFEST_SHA256

OBSERVED_SHA256 = '6d5fdf5cbe283c4910f6217882e275ac5650c90695e8ae2cacb5825b39c0220a'
BOUNDARY = ('Retained server-fitted instances: 105 defaults and three subject examples, rendered by unchanged browser factories. '
            'Declared controls are editable locally. Arbitrary prepared constructors, refitting, '
            'off-default server equivalence and current server identity are not supplied.')


def observed_catalog():
    raw = (Path(__file__).parent / 'contracts/OBSERVED-VFX-DEFAULTS.json').read_bytes()
    if digest(raw) != OBSERVED_SHA256:
        raise ValidationError('Observed VFX library differs from its pinned authority')
    value = json.loads(raw)
    if set(value) != {'version', 'boundary', 'defaults', 'subject_examples'} or value['version'] != 1:
        raise ValidationError('Invalid observed VFX library schema')
    entries = value['defaults']
    if len(entries) != 105 or len({e['id'] for e in entries}) != 105:
        raise ValidationError('Observed VFX library must retain exactly 105 unique defaults')
    examples = value['subject_examples']
    if len(examples) != 3 or len({e['id'] for e in entries + examples}) != 108:
        raise ValidationError('Observed library must retain three distinct subject examples')
    for entry in entries + examples:
        if set(entry) not in ({'id', 'label', 'recipe', 'provenance'},
                              {'id', 'label', 'recipe', 'provenance', 'subject_png'}):
            raise ValidationError('Invalid observed default schema')
        if not isinstance(entry['id'], str) or not re.fullmatch(r'observed\.[a-z0-9_]+', entry['id']):
            raise ValidationError('Invalid observed default ID')
        if not isinstance(entry['label'], str) or not isinstance(entry['recipe'], dict):
            raise ValidationError('Invalid observed default record')
        provenance = entry['provenance']
        for key in ('response_sha256', 'recipe_sha256', 'input_bindings_sha256',
                    'native_atlas_png_sha256', 'native_atlas_json_sha256', 'source_manifest_sha256'):
            if not re.fullmatch('[0-9a-f]{64}', provenance.get(key, '')):
                raise ValidationError('Invalid observed default evidence hash')
        if digest(canonical_json(entry['recipe'])) != provenance['recipe_sha256']:
            raise ValidationError('Observed default recipe integrity failed')
        if 'subject_png' in entry:
            if entry['subject_png'] != 'observed_examples/own-r9.png':
                raise ValidationError('Invalid observed example subject path')
            subject_raw = (Path(__file__).parent / entry['subject_png']).read_bytes()
            if digest(subject_raw) != provenance['subject_png_sha256']:
                raise ValidationError('Observed example subject integrity failed')
        comparison = provenance['comparison']
        if (comparison['RGBA_mismatches'] != 0 or comparison['exact_native_RGBA'] is not True
                or comparison['frames'] != entry['recipe']['frames']
                or len(comparison['native_frame_RGBA_sha256']) != comparison['frames']
                or comparison['native_frame_RGBA_sha256'] != comparison['source_frame_RGBA_sha256']
                or provenance['source_manifest_sha256'] != PINNED_MANIFEST_SHA256):
            raise ValidationError('Observed default lacks exact retained native comparison')
    types = Counter(control['type'] for entry in entries for control in entry['recipe'].get('controls', []))
    if sum(types.values()) != 350 or set(types) != {'slider', 'ramp', 'toggle', 'select'}:
        raise ValidationError('Observed library must retain all 350 original controls')
    return {**value, 'sha256': digest(raw),
            'counts': {'defaults': len(entries), 'subject_examples': len(examples), 'controls': sum(types.values()), 'control_types': dict(types)}}


def observed_default(ident):
    catalog = observed_catalog()
    for entry in catalog['defaults'] + catalog['subject_examples']:
        if entry['id'] == ident:
            return copy.deepcopy(entry)
    raise ValidationError('Unknown observed VFX default ID')


def render_observed(store, request):
    from .source_controls import render_controlled_effect
    from .source_vfx import source_provenance
    entry = observed_default(request['id'])
    subject = request.get('subject')
    if subject is None and entry.get('subject_png'):
        # Check original controls before retaining a packaged raster for a bad request.
        from .source_controls import apply_controls
        apply_controls(entry['recipe'], request.get('values'))
        import numpy as np
        from PIL import Image
        with Image.open(Path(__file__).parent / entry['subject_png']) as image:
            subject = store.put_raster(np.array(image.convert('RGBA')))
    result = render_controlled_effect(store, entry['recipe'], values=request.get('values'),
                                     subject=subject, images=request.get('images'),
                                     timeout=request.get('timeout', 60))
    default_values = all(request.get('values', {}).get(c['id'], c['value']) == c['value']
                         for c in entry['recipe'].get('controls', []))
    observation = {'kind': 'observed-vfx-default', 'version': 1,
                   'id': entry['id'], 'library_sha256': OBSERVED_SHA256,
                   'provenance': entry['provenance'], 'boundary': BOUNDARY,
                   'default_values': default_values,
                   'retained_default_inputs': default_values and not request.get('subject') and not request.get('images'),
                   'supplied_subject': subject, 'packaged_subject': bool(entry.get('subject_png')) and 'subject' not in request, 'supplied_images': request.get('images', {})}
    receipt = store.put_json(observation)
    streams = {}
    for name, sequence_id in result['streams'].items():
        document = store.get_json(sequence_id)
        document['metadata'] = {**document['metadata'], 'observed_vfx_default': receipt}
        streams[name] = store.put_json(document)
    return {**result, 'sequence': streams['frames'], 'streams': streams,
            'observed_default': receipt, 'observed_id': entry['id'],
            'provenance': source_provenance(result['executed_modules'])}
