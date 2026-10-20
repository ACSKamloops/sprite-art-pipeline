"""Local service adapters around unchanged recovered PixelLab VFX factories."""
import json
from pathlib import Path
import subprocess

from .core import ValidationError, canonical_json, digest
from .effects import PINNED_MANIFEST_SHA256, render_effect


def source_provenance(executed=()):
    root = Path(__file__).parent / 'vendor' / 'vfx'
    raw = (root / 'manifest.json').read_bytes()
    if digest(raw) != PINNED_MANIFEST_SHA256:
        raise ValidationError('Source VFX manifest identity changed')
    manifest = json.loads(raw)
    for module in manifest['modules']:
        if digest((root / module['file']).read_bytes()) != module['sha256']:
            raise ValidationError(f"Source VFX factory integrity failed {module['id']}")
    return {'classification': 'deterministic-source', 'manifest_sha256': digest(raw),
            'executed_modules': list(executed), 'modules': manifest['modules'],
            'original_exports': {'normalize': '47381.W$', 'render': '39852.sY',
                                 'apply_controls': '47381.uY'},
            'boundary': 'Recovered website factories only; no neural generation, character animation, '
                        'current server or MCP equivalence claim. IPC, resource limits and storage are local wrappers.'}


def run_source_vfx(action, recipe=None, values=None):
    """Execute source describe/normalizer/control methods with local IPC limits."""
    if action not in {'describe', 'validate', 'apply_controls'}:
        raise ValidationError('Unsupported source VFX action')
    provenance = source_provenance()
    payload = canonical_json({'action': action, 'recipe': recipe, 'values': values})
    if len(payload) > 2 * 1024 * 1024:
        raise ValidationError('Local source VFX JSON budget exceeded')
    try:
        result = subprocess.run(['node', '--max-old-space-size=256',
                                 str(Path(__file__).with_name('source_vfx_runner.cjs'))],
                                input=payload, capture_output=True, timeout=30, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise ValidationError('Source VFX Node runtime unavailable or local 30 second budget exceeded') from exc
    try:
        out = json.loads(result.stdout)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValidationError('Source VFX adapter produced no structured result') from exc
    if result.returncode or out.get('status') == 'validation_error':
        raise ValidationError(out.get('reason', 'Source VFX method failed'))
    if out['manifest_sha256'] != provenance['manifest_sha256']:
        raise ValidationError('Source VFX runtime manifest differs')
    provenance['executed_modules'] = out['executed_modules']
    out['provenance'] = provenance
    return out


def bind_source_vfx(registry, store):
    """Register explicitly local services; no provider forwarding or substitutes."""
    def render(request):
        from .source_controls import render_controlled_effect
        result = render_controlled_effect(store, request['recipe'], values=request.get('values'),
                                           subject=request.get('subject'), images=request.get('images'),
                                           timeout=request.get('timeout', 60))
        result['provenance'] = source_provenance(result['executed_modules'])
        return result

    def controls(request):
        from .source_controls import apply_controls
        return apply_controls(request['recipe'], values=request.get('values'))

    obj = {'type': 'object'}
    schemas = {
        'describe': {'type': 'object', 'properties': {}, 'additionalProperties': False},
        'validate': {'type': 'object', 'properties': {'recipe': obj}, 'required': ['recipe'],
                     'additionalProperties': False},
        'controls': {'type': 'object', 'properties': {'recipe': obj, 'values': obj},
                     'required': ['recipe'], 'additionalProperties': False},
        'render': {'type': 'object', 'properties': {'recipe': obj, 'subject': {'type': 'string'},
                   'images': {'type': 'object', 'additionalProperties': {'type': 'string'}}, 'values': obj,
                   'timeout': {'type': 'number', 'exclusiveMinimum': 0, 'maximum': 120}},
                   'required': ['recipe'], 'additionalProperties': False},
    }
    handlers = {'describe': lambda request: run_source_vfx('describe'),
                'validate': lambda request: run_source_vfx('validate', request['recipe']),
                'controls': controls, 'render': render}
    from .observed_vfx import observed_catalog, observed_default, render_observed, BOUNDARY, OBSERVED_SHA256
    schemas.update({
        'observed_catalog': schemas['describe'],
        'observed_default': {'type': 'object', 'properties': {'id': {'type': 'string'}},
                             'required': ['id'], 'additionalProperties': False},
        'render_observed': {'type': 'object', 'properties': {'id': {'type': 'string'},
                            'values': obj, 'subject': {'type': 'string'},
                            'images': {'type': 'object', 'additionalProperties': {'type': 'string'}},
                            'timeout': {'type': 'number', 'exclusiveMinimum': 0, 'maximum': 120}},
                            'required': ['id'], 'additionalProperties': False},
    })
    handlers.update({'observed_catalog': lambda request: observed_catalog(),
                     'observed_default': lambda request: observed_default(request['id']),
                     'render_observed': lambda request: render_observed(store, request)})
    evidence = source_provenance()
    evidence['observed_library_boundary'] = BOUNDARY
    evidence['observed_library_sha256'] = OBSERVED_SHA256
    for name, handler in handlers.items():
        registry.register_local('local.pixellab.vfx.' + name, handler,
                                classification='deterministic-source',
                                request_schema=schemas[name], evidence=evidence)
