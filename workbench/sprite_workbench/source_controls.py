"""Control inspection and application through unchanged retained PixelLab code.

The applied recipe is a preview/receipt. Rendering uses the declared recipe,
otherwise the source renderer would apply mul/add controls for a second time.
"""
from .core import canonical_json, digest
from .effects import render_effect
from .source_vfx import run_source_vfx


def _hash(value):
    return digest(canonical_json(value))


def describe_controls(recipe):
    """Return original normalized declarations; no synthetic controls are added."""
    return apply_controls(recipe)


def apply_controls(recipe, values=None):
    """Set declared values and execute original normalization and applyControls.

    IDs and JSON/resource envelope checks belong to the adapter; all bind paths,
    mapped values, expressions, rounding, validation and copies are source code.
    """
    result = run_source_vfx('apply_controls', recipe=recipe, values=values)
    declared = result['declared_recipe']
    applied = result['recipe']
    controls = result['controls']
    return {
        **result,
        'hashes': {
            'input_recipe_sha256': _hash(recipe),
            'declared_recipe_sha256': _hash(declared),
            'normalized_recipe_sha256': _hash(result['normalized_recipe']),
            'applied_recipe_sha256': _hash(applied),
            'controls_sha256': _hash(controls),
            'values_sha256': _hash({c['id']: c['value'] for c in controls}),
        },
        'renderer_input': declared,
        'render_policy': 'original renderer applies declared controls exactly once',
    }


def render_controlled_effect(store, recipe, values=None, *, subject=None, images=None, timeout=60):
    """Render using the original renderer, with control values source-validated."""
    controls = apply_controls(recipe, values)
    rendered = render_effect(store, controls['renderer_input'], subject=subject, images=images, timeout=timeout)
    receipt = store.put_json({'kind': 'source-controls', 'version': 1, **controls})
    streams = {}
    for name, sequence_id in rendered['streams'].items():
        document = store.get_json(sequence_id)
        document['metadata'] = {**document['metadata'], 'pixellab_controls': receipt}
        streams[name] = store.put_json(document)
    return {**rendered, 'sequence': streams['frames'], 'streams': streams,
            'control_receipt': receipt, 'control_hashes': controls['hashes'],
            'controls': controls['controls'], 'controlled_recipe': controls['recipe']}
