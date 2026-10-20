"""Host plumbing for unchanged PixelLab browser functions and retained presets.

These helpers select immutable inputs, keep jobs responsive and retain results.
Recipe validation, controls and effect pixels execute the original factories.
"""
import json
from pathlib import Path

from .core import ValidationError, digest
from .source_vfx import bind_source_vfx, run_source_vfx

PRESETS_SHA256 = 'f0c0e9d1a84fb1feb244b70124218381729850ed27d60448ab97aad892bbc40f'
RENDER_JOB = 'local.pixellab.vfx.render'
OBSERVED_RENDER_JOB = 'local.pixellab.vfx.render_observed'


def source_catalog():
    raw = (Path(__file__).parent / 'contracts/SOURCE-VFX-PRESETS.json').read_bytes()
    if digest(raw) != PRESETS_SHA256:
        raise ValidationError('Retained source presets differ from their pinned authority')
    from .observed_vfx import observed_catalog
    observed = observed_catalog()
    return {'observed_defaults': observed['defaults'], 'observed_subject_examples': observed['subject_examples'], 'observed_sha256': observed['sha256'],
            'observed_boundary': observed['boundary'], 'observed_counts': observed['counts'], 'observed_render_job': OBSERVED_RENDER_JOB,
            'source': run_source_vfx('describe'), 'presets': json.loads(raw)['presets'],
            'presets_sha256': digest(raw), 'render_job': RENDER_JOB,
            'boundary': 'Unchanged retained browser functions and authentic returned presets; '
                        'private models and current server build remain unavailable.'}


def invoke_source_vfx(store, method, request):
    from .capabilities import CapabilityRegistry
    if method not in {'describe', 'validate', 'controls', 'render', 'observed_catalog', 'observed_default', 'render_observed'}:
        raise ValidationError('Unknown recovered PixelLab method')
    registry = CapabilityRegistry()
    bind_source_vfx(registry, store)
    return registry.invoke('local.pixellab.vfx.' + method, request)


def register_source_job(manager, *, before_run=None):
    from .jobs import JobResult

    def execute(method, request, context):
        if before_run:
            before_run()
        context.progress(0.05, {'phase': 'original source validation and controls'})
        result = invoke_source_vfx(manager.store, method, request)
        if before_run:
            before_run()
        context.progress(1, {'phase': 'original source frames retained'})
        return JobResult(result['sequence'], 'candidate', {
            'source_result': result, 'visual_approval': 'unreviewed',
            'execution': 'unchanged pinned PixelLab browser factories'})

    manager.register(RENDER_JOB, lambda request, context: execute('render', request, context))
    manager.register(OBSERVED_RENDER_JOB, lambda request, context: execute('render_observed', request, context))
