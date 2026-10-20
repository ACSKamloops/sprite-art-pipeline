"""JSON Lines services; native provider calls require explicit enablement."""
import json
from pathlib import Path
import sys

from .core import Store, ValidationError, canonical_json
from .capabilities import CapabilityRegistry
from .jobs import JobManager
from .library import Library
from .pipeline import register_pipeline_job

MAX_LINE = 4 * 1024 * 1024


def serve(store: Store, *, base_dir, result_ref, workers=2, source=None, sink=None, enable_motion_provider=False):
    """One request/reply per line; jobs keep running between requests.

    EOF/shutdown drains workers for the manager's bounded close timeout. It is
    not a force kill. Use get/list polling to keep this channel responsive;
    local.jobs.wait deliberately blocks request dispatch until it returns.
    """
    source = source if source is not None else sys.stdin
    sink = sink if sink is not None else sys.stdout
    base = Path(base_dir).resolve()
    if not base.is_dir():
        raise ValidationError('Channel base directory must exist')
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValidationError('Channel workers must be 1..8')
    if not isinstance(result_ref, str) or not result_ref:
        raise ValidationError('Supply the pipeline result reference')
    def emit(value):
        sink.write(json.dumps(value, allow_nan=False, separators=(',', ':')) + '\n')
        sink.flush()
    with JobManager(store, workers=workers) as manager:
        registry = CapabilityRegistry()
        registry.bind_source_validation()
        registry.bind_library(Library(store))
        registry.bind_jobs(manager)
        from .construction_services import bind_construction
        bind_construction(registry, store, base_dir=base)
        from .source_vfx import bind_source_vfx
        from .source_workflow import register_source_job
        bind_source_vfx(registry, store)
        from .model_handoff import bind_models
        bind_models(registry, store, base_dir=base)
        from .selection_services import bind_selection
        from .studio_services import bind_studio
        bind_selection(registry, store, base_dir=base)
        bind_studio(registry, store, base_dir=base)
        from .motion_services import bind_motion
        bind_motion(registry, store, base_dir=base, live_provider_enabled=enable_motion_provider)
        from .parity_services import bind_parity
        bind_parity(registry, store, base_dir=base)
        register_source_job(manager)
        register_pipeline_job(manager, base_dir=base, result_ref=result_ref)
        emit({'event': 'ready', 'protocol': 'sprite-workbench-jsonl-v1', 'workspace': str(store.path),
              'pipeline_handler': 'local.pipeline', 'base_dir': str(base), 'result_ref': result_ref,
              'workers': workers, 'provider_forwarding': enable_motion_provider is True})
        while True:
            line = source.readline(MAX_LINE + 2)
            if not line:
                break
            request_id = None
            try:
                if len(line.encode('utf-8')) > MAX_LINE:
                    while not line.endswith('\n'):
                        line = source.readline(MAX_LINE + 2)
                        if not line:
                            break
                    raise ValidationError('Channel request exceeds 4MiB')
                request = json.loads(line)
                canonical_json(request)
                if not isinstance(request, dict) or set(request) - {'id', 'method', 'params'}:
                    raise ValidationError('Request needs id, method and optional params only')
                request_id = request.get('id')
                if type(request_id) not in (str, int) or isinstance(request_id, str) and len(request_id) > 128:
                    request_id = None
                    raise ValidationError('Request id must be an integer or bounded string')
                method = request.get('method')
                params = request.get('params', {})
                if not isinstance(method, str) or not isinstance(params, dict):
                    raise ValidationError('Method must be text and params an object')
                shutdown = False
                if method == 'system.ping':
                    if params:
                        raise ValidationError('Ping takes no parameters')
                    result = {'alive': True}
                elif method == 'system.capabilities':
                    if params:
                        raise ValidationError('Capabilities takes no parameters')
                    result = registry.list('local')
                elif method == 'system.shutdown':
                    if params:
                        raise ValidationError('Shutdown takes no parameters')
                    result = {'closing': True, 'running_jobs': 'bounded cooperative drain; no forced rollback'}
                    shutdown = True
                elif method.startswith('local.'):
                    result = registry.invoke(method, params)
                else:
                    raise ValidationError('Channel accepts explicit local.* services and system.* controls only')
                emit({'id': request_id, 'status': 'completed', 'result': result})
                if shutdown:
                    break
            except TimeoutError:
                emit({'id': request_id, 'status': 'timeout', 'error': {
                    'status': 'timeout', 'reason': 'Wait expired; inspect or cancel the still-active job'}})
            except (ValidationError, OSError, KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
                error = exc.to_dict() if isinstance(exc, ValidationError) else {
                    'status': 'validation_error', 'reason': 'Invalid local channel input',
                    'exception_type': type(exc).__name__}
                emit({'id': request_id, 'status': error['status'], 'error': error})
    return 0
