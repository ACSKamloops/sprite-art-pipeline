"""Explicit local construction services, shared by CLI, JSONL and plans.

All edits produce immutable candidates. Filesystem paths are trusted local
paths relative to the configured base; this interface is not a sandbox.
"""
from pathlib import Path

from .core import MAX_DOCUMENT_BYTES, ValidationError, canonical_json, digest

ID = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
TEXT = {'type': 'string', 'minLength': 1}


def schema(properties, required):
    return {'type': 'object', 'properties': properties, 'required': required,
            'additionalProperties': False}


SCHEMAS = {
    'save': schema({'document': {'type': 'object'}}, ['document']),
    'read': schema({'path': TEXT}, ['path']),
    'get': schema({'project': ID}, ['project']),
    'write': schema({'project': ID, 'path': TEXT}, ['project', 'path']),
    'history': schema({'project': ID}, ['project']),
    'edit': schema({'history': ID, 'transaction': {'type': 'object'}}, ['history', 'transaction']),
    'undo': schema({'history': ID}, ['history']),
    'redo': schema({'history': ID}, ['history']),
    'from_sequence': schema({'sequence': ID, 'animation_id': TEXT,
                             'fps': {'type': 'integer', 'minimum': 1, 'maximum': 9007199254740991}}, ['sequence']),
    'render': schema({'project': ID, 'animation_id': TEXT, 'history': ID,
                      'import_provenance': ID}, ['project', 'animation_id']),
    'ase_export': schema({'project': ID, 'directory': TEXT, 'animation': TEXT}, ['project', 'directory']),
    'ase_import': schema({'path': TEXT, 'sidecar': TEXT}, ['path', 'sidecar']),
}


def bind_construction(registry, store, *, base_dir=None):
    from . import construction as core
    base = Path(base_dir or '.').resolve()

    def path(value):
        p = Path(value)
        return p if p.is_absolute() else base / p

    def read(request):
        from .construction_core.loading import load_json
        with path(request['path']).open('rb') as stream:
            raw = stream.read(MAX_DOCUMENT_BYTES + 1)
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise ValidationError('Construction input exceeds 16MiB')
        try:
            document = load_json(raw)
        except (ValueError, UnicodeDecodeError, OverflowError, RecursionError) as exc:
            raise ValidationError('Invalid portable construction JSON') from exc
        return core.save_project(store, document)

    def get(request):
        p = core.load_project(store, request['project'])
        animation_ids = [a['id'] for a in p['animations'][:64] if len(a['id']) <= 128]
        return {'project': request['project'], 'project_hash': core.project_hash(p),
                'canvas': p['canvas'], 'layers': len(p['layers']),
                'palette_entries': len(p['palette']), 'cels': len(p['cels']),
                'frames': len(p['frames']), 'animations': len(p['animations']),
                'animation_ids': animation_ids,
                'animation_ids_omitted': len(p['animations']) - len(animation_ids),
                'document_omitted': 'Use write to export the editable JSON to a file'}

    def write(request):
        raw = canonical_json(core.load_project(store, request['project'])) + b'\n'
        target = path(request['path'])
        # Exclusive creation rejects existing files and dangling symlinks.
        with target.open('xb') as stream:
            stream.write(raw)
        return {'project': request['project'], 'path': str(target),
                'bytes': len(raw), 'sha256': digest(raw)}

    def render(request):
        metadata = {}
        if 'history' in request:
            history = store.get_json(request['history'])
            if history.get('kind') != 'construction-history' or history.get('project') != request['project']:
                raise ValidationError('History must refer to the rendered current project')
            # Replay validates receipts, cursor and project/hash guards.
            core.load_history(store, request['history'])
            metadata['construction_history'] = request['history']
        if 'import_provenance' in request:
            from .construction_exchange import validate_import_provenance
            validate_import_provenance(store, request['import_provenance'], project_id=request['project'])
            metadata['construction_import'] = request['import_provenance']
        out = core.render_animation(store, request['project'], request['animation_id'])
        if metadata:
            sequence = store.get_json(out['sequence'])
            sequence['metadata'] = {**sequence['metadata'], **metadata}
            out = {**out, 'sequence': store.put_json(sequence)}
        return out

    def ase_export(request):
        from .construction_exchange import export_ase
        return export_ase(store, request['project'], path(request['directory']), animation=request.get('animation'))

    def ase_import(request):
        from .construction_exchange import import_ase
        return import_ase(store, path(request['path']), path(request['sidecar']))

    handlers = {
        'save': lambda r: core.save_project(store, r['document']), 'read': read,
        'get': get, 'write': write, 'history': lambda r: core.create_history(store, r['project']),
        'edit': lambda r: core.edit_history(store, r['history'], r['transaction']),
        'undo': lambda r: core.move_history(store, r['history'], 'undo'),
        'redo': lambda r: core.move_history(store, r['history'], 'redo'),
        'from_sequence': lambda r: core.from_sequence(store, r['sequence'],
            animation_id=r.get('animation_id', 'clip'), fps=r.get('fps')),
        'render': render, 'ase_export': ase_export, 'ase_import': ase_import,
    }
    for name, handler in handlers.items():
        registry.register_local('local.construction.' + name, handler,
            classification='supplied-art', request_schema=SCHEMAS[name],
            evidence={'implementation': 'sprite_workbench.construction',
                      'policy': 'Immutable local indexed edits; no vendor model or host parity claim'})


def invoke_construction(store, method, request, *, base_dir=None):
    from .capabilities import CapabilityRegistry
    if method not in SCHEMAS:
        raise ValidationError('Unknown local construction method')
    registry = CapabilityRegistry()
    bind_construction(registry, store, base_dir=base_dir)
    return registry.invoke('local.construction.' + method, request)
