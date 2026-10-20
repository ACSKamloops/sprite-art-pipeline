"""The same explicit Studio contract for HTTP, CLI, JSONL and plans."""
from .construction_services import ID, TEXT, schema
from .core import ValidationError

COMMON = {'project': ID, 'history': ID, 'animation_id': TEXT,
          'selection_receipts': {'type': 'array', 'items': ID, 'maxItems': 1024, 'uniqueItems': True}}
SCHEMAS = {
    'catalog': schema({}, []),
    'load_example': schema({'id': {'enum': ['hero-walk', 'hero-slash']}}, ['id']),
    'from_sequence': schema({'sequence': ID, 'animation_id': TEXT, 'normalize_hidden_rgb': {'type': 'boolean'}}, ['sequence']),
    'verify': schema(COMMON, ['project', 'history', 'animation_id']),
    'export': schema(COMMON, ['project', 'history', 'animation_id']),
}


def bind_studio(registry, store, *, base_dir=None):
    from . import studio
    handlers = {'catalog': lambda r: studio.catalog(), 'load_example': lambda r: studio.load_example(store, r['id']),
        'from_sequence': lambda r: studio.from_sequence(store, **r),
        'verify': lambda r: studio.verify(store, **r),
        'export': lambda r: studio.export(store, base_dir=base_dir or '.', **r)}
    for name, handler in handlers.items():
        registry.register_local('local.studio.'+name, handler, classification='supplied-art',
            request_schema=SCHEMAS[name], evidence={'implementation': 'sprite_workbench.studio',
                'policy': 'Raw inputs retained; explicit editable derivative; format readback separate from art approval'})


def invoke_studio(store, method, request, *, base_dir=None):
    from .capabilities import CapabilityRegistry
    if method not in SCHEMAS:
        raise ValidationError('Unknown local Studio method')
    registry = CapabilityRegistry()
    bind_studio(registry, store, base_dir=base_dir)
    return registry.invoke('local.studio.'+method, request)
