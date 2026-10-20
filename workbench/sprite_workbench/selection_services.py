"""Local recovered manual selector services; all edits use construction history."""
from pathlib import Path

from .core import ValidationError
from .construction_services import ID, TEXT, schema

SCHEMAS = {
    'raster': schema({'raster': ID,
        'seed': {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 2, 'maxItems': 2},
        'tolerance': {'type': 'number', 'minimum': 0, 'maximum': 1}}, ['raster', 'seed']),
    'create': schema({'project': ID, 'cel_id': TEXT,
        'seed': {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 2, 'maxItems': 2},
        'tolerance': {'type': 'number', 'minimum': 0, 'maximum': 1}}, ['project', 'cel_id', 'seed']),
    'apply': schema({'history': ID, 'selection': ID, 'action': {'type': 'string', 'enum': ['erase', 'paint']},
        'palette_index': {'type': 'integer', 'minimum': 0}}, ['history', 'selection', 'action']),
    'get': schema({'selection': ID}, ['selection']),
    'export_mask': schema({'selection': ID, 'path': TEXT}, ['selection', 'path']),
}


def bind_selection(registry, store, base_dir=None):
    from . import selection as core
    base = Path(base_dir or '.').resolve()

    def create(r):
        return core.create_selection(store, r['project'], r['cel_id'], r['seed'], r.get('tolerance', 0.0))

    def apply(r):
        return core.apply_selection(store, r['history'], r['selection'], r['action'], r.get('palette_index'))

    def get(r):
        doc, _ = core.load_selection(store, r['selection'])
        return {'selection': r['selection'], **{k: doc[k] for k in ('mask_raster', 'selected_pixels',
            'width', 'height', 'cel_id', 'source_project', 'source_project_hash', 'source_cel_rgba_sha256',
            'shared_frames', 'seed', 'tolerance')}, 'source_provenance': doc['source_provenance']}

    def export(r):
        path = Path(r['path'])
        return core.export_mask(store, r['selection'], path if path.is_absolute() else base / path)

    for name, handler in {'raster': lambda r: core.select_raster(store, **r), 'create': create, 'apply': apply, 'get': get, 'export_mask': export}.items():
        registry.register_local('local.selection.' + name, handler,
            classification='deterministic-source' if name in ('create','raster') else 'supplied-art',
            request_schema=SCHEMAS[name], evidence={
                'implementation': 'sprite_workbench.selection',
                'source_manifest_sha256': core._MANIFEST_SHA,
                'mode': ('Manual seed/tolerance on supplied raster; no active selection constraint' if name=='raster'
                         else 'Manual seed/tolerance on active cel; no active selection constraint'),
                'policy': 'Recovered Godot host seed/tolerance selector, no active selection; local guarded indexed edits; not automatic server cutout'})


def invoke_selection(store, method, request, *, base_dir=None):
    from .capabilities import CapabilityRegistry
    if method not in SCHEMAS:
        raise ValidationError('Unknown local selection method')
    registry = CapabilityRegistry()
    bind_selection(registry, store, base_dir)
    return registry.invoke('local.selection.' + method, request)
