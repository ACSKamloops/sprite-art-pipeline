"""Local, non-executing model handoffs and raw-result admission.

This is host orchestration, not a recovered PixelLab inference algorithm.
No provider client, credential reader, agent launcher or image cleanup lives here.
"""
from copy import deepcopy
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

from .core import ValidationError, UnsupportedCapability, canonical_json, digest, validate_id
from .export import png_bytes, output_directory, validated_sequence

BOUNDARY = ('Local handoff/import protocol; original PixelLab procedural code remains separate. '
            'Private inference is unavailable. No model calls or automatic execution.')
PROFILE_VERSION = 'model-handoff-v1'
PROFILES = [
    {'id': 'codex.imagegen', 'label': 'Codex image-generation tool',
     'status': 'external-agent-tool; not callable by this web server',
     'orchestrator_provider': 'OpenAI', 'orchestrator_model': None,
     'image_provider': 'OpenAI', 'requested_image_model': None,
     'capabilities': {'tasks': ['still', 'edit'], 'ordered_image_references': True,
                      'transparent_background_parameter': True, 'local_input_limit': 8,
                      'typed_size': False, 'seed': False, 'exact_mask': False,
                      'joint_conditioning': False, 'animation_clock': False},
     'evidence': 'Current built-in imagegen tool schema; underlying model identity undisclosed',
     'boundary': 'Agent-mediated tool handoff; no direct HTTP transport or generation performed'},
    {'id': 'hermes.image_generate', 'label': 'Hermes / MiniMax agent',
     'status': 'needs-image-provider-selection; runtime untested',
     'orchestrator_provider': 'minimax-oauth', 'orchestrator_model': 'MiniMax-M3.1-Flash-Preview',
     'image_provider': None, 'requested_image_model': None,
     'image_vendor_if_configured': 'OpenAI',
     'required_configuration': {'image_gen.provider': 'openai-codex',
                                'image_gen.model': 'gpt-image-2-medium'},
     'capabilities': {'tasks': ['still', 'edit'], 'ordered_image_references': True,
                      'transparent_background_parameter': False, 'local_input_limit': 8,
                      'typed_size': False, 'seed': False, 'exact_mask': False,
                      'joint_conditioning': False, 'animation_clock': False},
     'evidence': 'Installed Hermes 71d34bad104, openai-codex image plugin; inspected 2026-10-14',
     'boundary': 'Capabilities refer to the explicitly required installed image plugin. '
                 'Active image provider is unselected; no auth validity or live availability proof. '
                 'MiniMax chat is the orchestrator, not the image renderer.'},
]


def catalog():
    return {'version': 1, 'protocol': PROFILE_VERSION, 'executors': deepcopy(PROFILES),
            'boundary': BOUNDARY, 'provider_calls': 0, 'execution_status': 'held',
            'supported_scope': 'Still/reference generation and semantic edits only',
            'unsupported': ['animation', 'interpolation', 'typed joint conditioning',
                            'exact-mask guarantees', 'seed control', 'enforced native pixel size'],
            'prompt_policy': 'Exact user prompt retained; deterministic visible requirement appendix only; no enhancement'}


def _load(store, ident, kind):
    value = store.get_json(validate_id(ident))
    if value.get('kind') != kind or value.get('version') != 1:
        raise ValidationError('Expected ' + kind + ' version 1')
    return value


def _index(store):
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS model_handoff_tasks '
                   '(task TEXT PRIMARY KEY, experiment TEXT NOT NULL, executor TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS model_handoff_results '
                   '(result TEXT PRIMARY KEY, task TEXT NOT NULL, sequence TEXT NOT NULL)')


def _prompt(brief):
    text = brief['prompt']
    lines = ['Requested output (constraints to inspect after return; not typed guarantees):']
    size = brief['requirements']['desired_size']
    if size:
        lines.append(f"Desired canvas: {size[0]} by {size[1]} pixels. Do not claim compliance without checking the file.")
    lines.append('Background: ' + ('transparent.' if brief['requirements']['transparent_background'] else 'no transparency requirement.'))
    lines.extend(f"Image {i+1}: {item['role']}." for i, item in enumerate(brief['inputs']))
    if brief['task'] == 'edit':
        lines.append('Image 1 is the edit target; apply the requested change. Other images are references.')
    return text + '\n\n' + '\n'.join(lines)


def prepare(store, brief, executors):
    # Validate the whole batch before writing tasks or preparing PNGs.
    if brief['hard_controls']:
        raise UnsupportedCapability('local.models.prepare',
            'Typed hard controls are unsupported; seed, mask, joints and clocks cannot be silently dropped')
    if not brief['prompt'].strip():
        raise ValidationError('Provide a nonblank user prompt')
    roles = [item['role'] for item in brief['inputs']]
    if brief['task'] == 'edit' and (not roles or roles[0] != 'edit_target' or roles.count('edit_target') != 1):
        raise ValidationError('Edit requires exactly one edit_target as input slot 0')
    if brief['task'] == 'still' and 'edit_target' in roles:
        raise ValidationError('An edit_target requires the edit task')
    if len(executors) != len(set(executors)):
        raise ValidationError('Executor IDs must be unique')
    by_id = {p['id']: p for p in PROFILES}
    if any(ident not in by_id for ident in executors):
        raise UnsupportedCapability('local.models.prepare', 'Unknown executor; no fallback')
    prepared = []
    for item in brief['inputs']:
        array = store.get_raster(item['raster'])
        prepared.append((item, array, png_bytes(array)))
    if sum(len(raw) for _, _, raw in prepared) > 8 * 1024 * 1024:
        raise ValidationError('Reference PNGs exceed the declared local 8 MiB handoff budget')
    brief_id = store.put_json({'kind': 'model-brief', 'version': 1, 'brief': brief,
                              'prompt_sha256': digest(brief['prompt'].encode()),
                              'algorithm_ownership': 'user instruction plus local host envelope',
                              'pixellab_inference_recovered': False})
    inputs = []
    for i, (item, array, raw) in enumerate(prepared):
        inputs.append({**item, 'slot': i, 'filename': f'inputs/{i:03d}-{item["role"]}.png',
                       'png': store.put_bytes(raw), 'decoded_rgba_sha256': digest(array.tobytes()),
                       'canvas': [array.shape[1], array.shape[0]],
                       'transform': 'Lossless PNG encoding only; no resize, cleanup or quantization'})
    tasks = []
    for ident in executors:
        profile = deepcopy(by_id[ident])
        task = {'kind': 'model-task', 'version': 1, 'protocol': PROFILE_VERSION,
                'brief': brief_id, 'executor': ident, 'backend_snapshot': profile,
                'inputs': inputs, 'submitted_prompt_draft': _prompt(brief),
                'execution_status': 'held', 'provider_calls': 0,
                'settings': {'desired_size': 'prompt-only',
                             'transparency': 'typed parameter' if ident == 'codex.imagegen' else 'prompt-only',
                             'effective_seed': None, 'effective_size': None, 'image_model': None},
                'boundary': BOUNDARY}
        task_id = store.put_json(task)
        tasks.append({'task': task_id, 'executor': ident, 'status': 'prepared; execution held'})
    experiment = store.put_json({'kind': 'model-experiment', 'version': 1, 'brief': brief_id,
                                 'tasks': tasks, 'scope': 'Preparation only', 'execution_status': 'held'})
    _index(store)
    with store.connect() as db:
        for item in tasks:
            db.execute('INSERT OR IGNORE INTO model_handoff_tasks VALUES(?,?,?)',
                       (item['task'], experiment, item['executor']))
    return {'experiment': experiment, 'brief': brief_id, 'tasks': tasks,
            'execution_status': 'held', 'provider_calls': 0, 'boundary': BOUNDARY}


def packet(store, task):
    doc = _load(store, task, 'model-task')
    brief = _load(store, doc['brief'], 'model-brief')['brief']
    paths = [i['filename'] for i in doc['inputs']]
    arguments = {'prompt': doc['submitted_prompt_draft']}
    if doc['executor'] == 'codex.imagegen':
        arguments['transparent_background'] = brief['requirements']['transparent_background']
        if paths:
            arguments['referenced_image_paths'] = paths
        tool = 'image_gen.imagegen'
        preflight = ['Inspect every input with view_image before editing or supplying local references.',
                     'Resolve relative reference paths from the exported packet directory.']
    elif doc['executor'] == 'hermes.image_generate':
        if brief['task'] == 'edit':
            arguments['image_url'] = paths[0]
            paths = paths[1:]
        if paths:
            arguments['reference_image_urls'] = paths
        tool = 'image_generate'
        preflight = ['Explicitly select the recorded openai-codex image provider; current selection is unset.',
                     'Verify supported local-file input handling in the active tool session.',
                     'Refuse provider fallback; capture actual selected provider and image model.',
                     'Do not substitute MiniMax chat OAuth into an Image-01 API request.']
    else:
        raise UnsupportedCapability('local.models.packet', 'Unknown frozen executor; no fallback')
    return {'kind': 'model-handoff-packet', 'version': 1, 'task': task,
            'executor': doc['executor'], 'brief': doc['brief'], 'request': brief,
            'backend': doc['backend_snapshot'], 'inputs': doc['inputs'],
            'transport_draft': {'tool': tool, 'arguments': arguments},
            'execution_status': 'held', 'execution_authorized_by_packet': False,
            'preflight': preflight + ['Do not run while the model/art experiment prerequisites remain held.',
                                     'Retain actual tool arguments, reported model identity and original output bytes.',
                                     'No automatic prompt enhancement, resizing, background removal or sprite-sheet splitting.'],
            'import_service': 'local.models.ingest', 'boundary': BOUNDARY}


def export_packet(store, task, directory, *, base_dir=None):
    target = Path(directory)
    if base_dir is not None:
        base = Path(base_dir).resolve()
        target = target if target.is_absolute() else base / target
        if not target.resolve().is_relative_to(base):
            raise ValidationError('Handoff export must remain inside the configured workspace')
    value = packet(store, task)
    with output_directory(target) as stage:
        for item in value['inputs']:
            dest = stage / item['filename']; dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(store.get_bytes(item['png']))
        (stage / 'packet.json').write_bytes(canonical_json(value) + b'\n')
        (stage / 'README.txt').write_text('PREPARATION ONLY. No model execution authorized by this packet.\n'
            'See packet.json for exact user instruction, visible prompt appendix, roles, hashes and missing controls.\n'
            'Inputs are lossless PNG encodings of existing Store rasters. Keep raw returned bytes; import without cleanup.\n')
    return {'task': task, 'directory': str(target.absolute()), 'packet': 'packet.json',
            'input_files': len(value['inputs']), 'execution_status': 'held'}


def ingest(store, task, sequence, execution):
    doc = _load(store, task, 'model-task')
    brief = _load(store, doc['brief'], 'model-brief')['brief']
    raw, arrays = validated_sequence(store, sequence)
    # Still/edit contracts never infer animation from an APNG or candidate sheet.
    if len(arrays) != 1:
        raise UnsupportedCapability('local.models.ingest',
            'Still/edit admission requires exactly one raw frame; animation needs an explicit role map and clock')
    if execution['kind'] == 'supplied-diagnostic' and any(
            execution.get(key) is not None for key in ('orchestrator_provider', 'orchestrator_model',
                'image_provider', 'image_transport', 'image_model', 'tool')):
        raise ValidationError('Supplied diagnostics cannot claim a model/tool execution')
    if execution['kind'] == 'external-generation' and not execution.get('tool'):
        raise ValidationError('External results require an executor-attested actual tool name')
    encoded = raw.get('metadata', {}).get('source_bytes')
    if execution['kind'] == 'external-generation':
        if not encoded:
            raise ValidationError('Import the untouched returned image file first; original encoded bytes are required')
        original = store.get_bytes(encoded, max_bytes=256 * 1024 * 1024)
        try:
            with Image.open(BytesIO(original)) as image:
                if image.size != tuple(raw['canvas']) or getattr(image, 'n_frames', 1) != 1:
                    raise ValidationError('Original returned bytes differ in canvas or frame count')
                if not np.array_equal(np.array(image.convert('RGBA')), arrays[0]):
                    raise ValidationError('Returned bytes differ from admitted pixels; import without transformations')
        except (OSError, ValueError) as exc:
            raise ValidationError('Original output bytes cannot be verified against the admitted pixels') from exc
    # Closed metadata avoids persisting raw HTTP headers, bearer tokens or arbitrary replies.
    if len(canonical_json(execution)) > 128 * 1024:
        raise ValidationError('Execution receipt exceeds 128 KiB')
    observed = {'canvas': raw['canvas'], 'frames': len(arrays),
                'decoded_rgba_sha256': [digest(a.tobytes()) for a in arrays],
                'source_bytes': raw.get('metadata', {}).get('source_bytes'),
                'has_transparent_pixels': bool(np.any(arrays[0][..., 3] < 255)),
                'nonzero_alpha_pixels': int(np.count_nonzero(arrays[0][..., 3])),
                'timing_origin': 'Not model timing: still/edit frame; source sequence clock retained only for container compatibility',
                'source_acquisition': {key: raw.get('metadata', {}).get(key) for key in (
                    'acquisition', 'source_format', 'decoder', 'missing_duration_policy', 'source_frame_indices')}}
    required = brief['requirements']; size = required['desired_size']
    expected_inputs = [{key: item[key] for key in ('slot', 'role', 'decoded_rgba_sha256')} for item in doc['inputs']]
    expected_tool = 'image_gen.imagegen' if doc['executor'] == 'codex.imagegen' else 'image_generate'
    expected_transport = 'builtin.imagegen' if doc['executor'] == 'codex.imagegen' else 'openai-codex'
    profile = doc['backend_snapshot']
    actual_provider = execution.get('orchestrator_provider')
    provider_matches = (actual_provider.casefold() == profile['orchestrator_provider'].casefold()
                        if actual_provider else None)
    model_matches = (execution.get('orchestrator_model') == profile['orchestrator_model']
                     if profile['orchestrator_model'] else True)
    expected_image_vendor = profile.get('image_provider') or profile.get('image_vendor_if_configured')
    actual_image_vendor = execution.get('image_provider')
    image_vendor_matches = (actual_image_vendor.casefold() == expected_image_vendor.casefold()
                            if actual_image_vendor and expected_image_vendor else None)
    controls = execution.get('submitted_controls')
    expected_controls = ({'transparent_background': required['transparent_background']}
                         if doc['executor'] == 'codex.imagegen' else {})
    audit = {'desired_size_matches': None if size is None else raw['canvas'] == size,
             'requested_transparency_observed': None if not required['transparent_background'] else observed['has_transparent_pixels'],
             'prompt_matches_draft': None if execution.get('actual_prompt') is None else execution['actual_prompt'] == doc['submitted_prompt_draft'],
             'geometry_policy': 'Full native canvas; no alignment, resize or hidden postprocessing',
             'frame_semantics': 'one supplied returned image, never inferred animation',
             'binding': {'actual_tool_matches': None if execution.get('tool') is None else execution['tool'] == expected_tool,
                         'image_transport_matches': None if execution.get('image_transport') is None else execution['image_transport'] == expected_transport,
                         'orchestrator_provider_matches': provider_matches,
                         'orchestrator_model_matches': model_matches,
                         'image_vendor_matches': image_vendor_matches,
                         'submitted_input_hashes_and_order_match': None if execution.get('submitted_inputs') is None else execution['submitted_inputs'] == expected_inputs,
                         'submitted_controls_match': None if controls is None else controls == expected_controls},
             'artistic_acceptance': 'unreviewed'}
    receipt = {'kind': 'model-result', 'version': 1, 'task': task, 'brief': doc['brief'],
               'executor': doc['executor'], 'raw_sequence': sequence, 'observed': observed,
               'execution': execution, 'execution_provenance': 'executor-attested, not independently authenticated',
               'audit': audit, 'created_utc': datetime.now(timezone.utc).isoformat(),
               'pixellab_inference_recovered': False, 'artistic_acceptance': 'unreviewed',
               'boundary': 'Bytes and dimensions verified locally; imported execution metadata is caller supplied. '
                           'External generation is not invoked or certified by this host.'}
    result = store.put_json(receipt)
    candidate = store.put_json({**raw, 'metadata': {**raw.get('metadata', {}), 'model_result': result}})
    _index(store)
    with store.connect() as db:
        db.execute('INSERT INTO model_handoff_results VALUES(?,?,?)', (result, task, candidate))
    return {'result': result, 'sequence': candidate, 'raw_sequence': sequence,
            'task': task, 'executor': doc['executor'], 'manifest': observed, 'audit': audit,
            'execution': execution, 'artistic_acceptance': 'unreviewed'}


def results(store, experiment):
    doc = _load(store, experiment, 'model-experiment')
    _index(store); found = []
    with store.connect() as db:
        for item in doc['tasks']:
            for result_id, sequence in db.execute('SELECT result,sequence FROM model_handoff_results '
                                                  'WHERE task=? ORDER BY rowid', (item['task'],)):
                receipt = _load(store, result_id, 'model-result')
                found.append({'result': result_id, 'sequence': sequence, 'raw_sequence': receipt['raw_sequence'],
                              'task': item['task'], 'executor': item['executor'],
                              'execution': receipt['execution'], 'audit': receipt['audit'],
                              'artistic_acceptance': 'unreviewed'})
    return {'experiment': experiment, 'results': found, 'artistic_acceptance': 'unreviewed'}


def audit_pair(store, left, right, scope):
    if left == right:
        raise ValidationError('Pair audit requires two distinct result artifacts')
    a, b = (_load(store, value, 'model-result') for value in (left, right))
    if a['brief'] != b['brief']:
        raise ValidationError('Pair audit requires the same frozen brief, inputs and requirements')
    _, aa = validated_sequence(store, a['raw_sequence']); _, bb = validated_sequence(store, b['raw_sequence'])
    same_canvas = aa[0].shape == bb[0].shape
    identities = [(r['execution'].get('image_provider'), r['execution'].get('image_model')) for r in (a, b)]
    canonical_identities = [(vendor.casefold() if vendor else None, model) for vendor, model in identities]
    observed_generations = all(r['execution']['kind'] == 'external-generation' for r in (a, b))
    known_distinct = all(all(v for v in identity) for identity in canonical_identities) and canonical_identities[0] != canonical_identities[1]
    prompt_matches = all(r['audit']['prompt_matches_draft'] is True for r in (a, b))
    bound = all(all(value is True for value in r['audit']['binding'].values()) for r in (a, b))
    orchestrators = [(r['execution'].get('orchestrator_provider'), r['execution'].get('orchestrator_model')) for r in (a, b)]
    known_orchestrators = all(all(value for value in identity) for identity in orchestrators)
    different_orchestrators = known_orchestrators and orchestrators[0] != orchestrators[1] and a['executor'] != b['executor']
    same_known_image_model = all(all(v for v in identity) for identity in canonical_identities) and canonical_identities[0] == canonical_identities[1]
    eligible = observed_generations and same_canvas and prompt_matches and bound and (
        (different_orchestrators and same_known_image_model) if scope == 'orchestrator' else known_distinct)
    return {'kind': 'model-pair-audit', 'version': 1, 'left': left, 'right': right,
            'scope': scope, 'same_frozen_brief': True, 'same_canvas': same_canvas,
            'exact_pixels_equal': bool(np.array_equal(aa[0], bb[0])) if same_canvas else None,
            'changed_pixels': int(np.count_nonzero(np.any(aa[0] != bb[0], axis=2))) if same_canvas else None,
            'image_identities': [list(i) for i in identities],
            'orchestrator_identities': [list(i) for i in orchestrators], 'task_bindings_match': bound,
            'comparison_eligible_by_attestation': eligible,
            'ineligible_reason': None if eligible else 'Requires original encoded outputs, matching actual tool/transport/orchestrator bindings, '
                'submitted prompt/input hashes/order/controls and canvases. Orchestrator scope holds a known image model fixed; '
                'image-backend scope requires known distinct image models. Missing attestations remain unknown.',
            'alpha_counts': [r['observed']['nonzero_alpha_pixels'] for r in (a, b)],
            'artistic_acceptance': 'unreviewed', 'quality_score': None,
            'boundary': 'Mechanical full-canvas diagnostics; no aesthetic score, causal model ranking, '
                        'temporal proof or PixelLab equivalence. Image identity is executor-attested.'}


def _object(properties, required=None):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required, 'additionalProperties': False}


ID = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
TEXT = {'type': ['string', 'null'], 'maxLength': 32768}
BRIEF = _object({'version': {'const': 1}, 'task': {'enum': ['still', 'edit']},
    'prompt': {'type': 'string', 'minLength': 1, 'maxLength': 32768},
    'inputs': {'type': 'array', 'maxItems': 8, 'items': _object({
        'role': {'enum': ['subject', 'style', 'edit_target']}, 'raster': ID})},
    'requirements': _object({'transparent_background': {'type': 'boolean'},
        'desired_size': {'anyOf': [{'type': 'null'}, {'type': 'array', 'minItems': 2, 'maxItems': 2,
            'items': {'type': 'integer', 'minimum': 1, 'maximum': 4096}}]}}),
    'hard_controls': {'type': 'object'}})
EXECUTION = _object({'kind': {'enum': ['supplied-diagnostic', 'external-generation']},
    'orchestrator_provider': TEXT, 'orchestrator_model': TEXT, 'image_provider': TEXT,
    'image_transport': TEXT, 'image_model': TEXT, 'tool': TEXT,
    'submitted_inputs': {'type': ['array', 'null'], 'maxItems': 8, 'items': _object({
        'slot': {'type': 'integer', 'minimum': 0, 'maximum': 7},
        'role': {'enum': ['subject', 'style', 'edit_target']}, 'decoded_rgba_sha256': ID})},
    'submitted_controls': {'anyOf': [{'type': 'null'}, _object({'transparent_background': {'type': 'boolean'}}, [])]},
    'actual_prompt': {'type': ['string', 'null'], 'maxLength': 65536}, 'parameters': _object({
        'seed': {'type': ['integer', 'null']}, 'reported_size': TEXT, 'reported_quality': TEXT,
        'requested_model': TEXT, 'request_id': TEXT, 'duration_seconds': {'type': ['number', 'null'], 'minimum': 0}} , [])}, ['kind'])
SCHEMAS = {'catalog': _object({}),
    'prepare': _object({'brief': BRIEF, 'executors': {'type': 'array', 'minItems': 1, 'maxItems': 2,
        'items': {'type': 'string'}}}),
    'packet': _object({'task': ID}), 'results': _object({'experiment': ID}),
    'export_packet': _object({'task': ID, 'directory': {'type': 'string', 'minLength': 1}}),
    'ingest': _object({'task': ID, 'sequence': ID, 'execution': EXECUTION}),
    'audit_pair': _object({'left': ID, 'right': ID, 'scope': {'enum': ['orchestrator', 'image-backend']}})}


def bind_models(registry, store, *, base_dir=None):
    handlers = {'catalog': lambda r: catalog(), 'prepare': lambda r: prepare(store, **r),
                'packet': lambda r: packet(store, **r), 'results': lambda r: results(store, **r),
                'export_packet': lambda r: export_packet(store, **r, base_dir=base_dir),
                'ingest': lambda r: ingest(store, **r), 'audit_pair': lambda r: audit_pair(store, **r)}
    for name, handler in handlers.items():
        registry.register_local('local.models.' + name, handler, classification='supplied-art',
            request_schema=SCHEMAS[name], evidence={'implementation': 'local model handoff host',
                'protocol': PROFILE_VERSION, 'boundary': BOUNDARY, 'model_execution': False})


def invoke_models(store, method, request, *, base_dir=None):
    from .capabilities import CapabilityRegistry
    registry = CapabilityRegistry(); bind_models(registry, store, base_dir=base_dir)
    return registry.invoke('local.models.' + method, request)
