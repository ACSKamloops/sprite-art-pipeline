"""Rebuild the finite, source-bound readiness catalog. No target/model calls.

This is an explicit editorial join, not a classifier or a completion detector.
Run from the checkout with --research /path/to/retained-investigation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


# Manually reviewed associations. A shared comparison ID does not mean that its
# diagnostic recipe implements the complete feature or any neural method.
FAMILIES = {
    'portrait-conversion-storage': ('F07', ['prepare:local-rgba-v1', 'library.set_state'],
        'No local portrait/character converter or portrait-assignment API. Supplied images can be retained without conversion.'),
    'portrait-dialogue': ('F08', ['pipeline.visemes', 'assets.save_viseme_timeline'],
        'Explicit supplied mouth images and letter map only; learned expressions, vendor alphabets and audio alignment unprovided.'),
    'font': ('F08', ['pipeline.font', 'pipeline.text'],
        'Captured local font bytes and supplied glyph atlas only; learned glyph generation, native TTF finalization and vendor typography not replicated.'),
    'ui-images-shape-panels': ('F08', ['pipeline.ui', 'assets.layout_shapes', 'assets.virtual_view'],
        'Supplied pieces and explicit layout geometry only; learned panel generation and interaction-state consistency unprovided.'),
    'prompt-caption': ('F07', ['prepare.prepare_prompt'],
        'Source-specific typed field/Auto packing only; caption/enhancement LLM and actual vendor callback runtime remain unprovided.'),
    'pro-tiles-connected-kits': ('F06', ['terrain.topology_indices', 'pipeline.terrain'],
        'Supplied local NESW diagnostic topology only; Pro material/road/building branches and matching target geometry require separate adapters.'),
    'isometric-single-tile': ('F06', [],
        'No local single-isometric provider or complete count1 adapter. Source guide/placement findings are retained separately from generated tile quality.'),
    'wang-topdown-sidescroller': ('F06', ['terrain.connectivity_sheet', 'pipeline.terrain'],
        'Explicit supplied local layout only; public Wang corner labels, private8x8/8x16 atlas and tall-cliff variants are distinct formats.'),
    'map-object-inpainting': ('F06', ['terrain.reblit_regions'],
        'Exact supplied-region reblit only; projected map placement, generation and vendor persisted placement IDs are not reproduced.'),
    'conversion-cleanup': ('F07', ['prepare.prepare_request', 'prepare.choose_unzoom', 'prepare.correction_strength'],
        'Versioned preparation and advisory source sampling only; learned segmentation/correction/background removal and true pixel-grid estimation unprovided.'),
    'persistent-object-review-state-animation': ('F05', ['local.library.create_candidate', 'local.library.select', 'local.library.promote', 'local.library.set_state'],
        'Local supplied candidate/state semantics only; vendor generated ranking, expansion scheduling, poll hooks and durable hosting remain unobserved.'),
    'persistent-character-state-rotation-export': ('F04', ['local.library.set_direction', 'local.library.set_state', 'local.library.set_animation', 'pipeline.export'],
        'Local supplied directions and animation clocks only; learned directions, reference scheduling and vendor URL lifetime/atomicity unprovided.'),
    'standalone-rotations': ('F03', ['pose.view_tilt', 'pose.flip_pose'],
        'Source-specific direction/flip math only; no local generator of unseen sprite directions or all-view quality guarantee.'),
    'interpolation': ('F03', ['pose.save_supplied_motion'],
        'Supplied exact motion clock only; no neural image interpolation backend, disocclusion model or vendor endpoint-preservation guarantee.'),
    'skeleton-estimation-animation': ('F03', ['pose.project_pose', 'pose.project_frames', 'pose.nearest_pose', 'pose.draw_depth_channels'],
        'Source-specific projection/depth/rank helpers only; skeleton estimation, missing templates/gear and pose-to-art rendering unprovided.'),
    'animation-edit-outfit': ('F01', ['pipeline.prepare', 'pipeline.edit'],
        'Supplied guarded frame edits only; semantic costume transfer and multi-frame identity preservation need an explicit backend.'),
    'text-template-wrapper-animation': ('F03', ['pose.save_supplied_motion', 'pipeline.tracks'],
        'Supplied clocks/tracks only; template/text neural animation, reference reuse and vendor accounting not reproduced.'),
    'image-edit-inpaint': ('F01', ['pipeline.prepare', 'pipeline.edit', 'raster.paste'],
        'Local exact ROI editing/reblit only; semantic inpainting and learned soft-mask conditioning unprovided.'),
    'style-reference-creation': ('F07', ['prepare.prepare_request'],
        'Ordered reference preparation only; style embeddings, learned reference attention and all-size output quality unprovided.'),
    'text-init-image-creation-environment': ('F07', ['prepare.prepare_request'],
        'Selected source acquisition/preparation only; depth/canny/pose/try-on neural generation and unseen environments unprovided.'),
    'jobs-uploads-cost-capabilities-library': ('F11', ['local.jobs.submit', 'local.jobs.get', 'local.jobs.cancel', 'local.jobs.retry', 'local.library.list'],
        'Local durable jobs/library only; vendor uploads, account costs, URL expiry, cloud chat/agents and sandboxes are separate unavailable services.'),
}

COMMAND_ROUTES = {
    'inspect': (['sprite-workbench inspect', 'sprite-workbench crop'], 'partial_local', 'Artifact inspection/crop, not the complete vendor inspection wire packet.'),
    'edit': (['sprite-workbench edit', 'local.construction.edit'], 'partial_local', 'Declared local raster and indexed transaction dialects; no vendor argv parser equivalence.'),
    'draw': (['pipeline.scene', 'pipeline.tracks'], 'partial_local', 'Local scene DAG/tracks use a separate explicit dialect; arbitrary nested vendor draw commands remain unavailable.'),
    'describe': (['sprite-workbench capabilities', 'sprite-workbench lab catalog'], 'partial_local', 'Local contracts/catalog only; no proxy to the hosted documentation command.'),
    'lint': (['sprite-workbench review'], 'partial_local', 'Selected exact diagnostics only; no fourteen-rule vendor lint parity.'),
    'measure': (['sprite-workbench review'], 'partial_local', 'Selected frame bounds/pixel counts only; full owner/node measure packet absent.'),
    'explain': ([], 'local_pending', 'No full pre-build node/command geometry explanation command.'),
    'clusters': ([], 'local_pending', 'No exposed versioned cluster-map command.'),
    'parts': (['pipeline.scene'], 'partial_local', 'Explicit source masks/overlap admission; automatic partitioning and owner visualization absent.'),
    'silhouette': (['sprite-workbench review'], 'partial_local', 'Selected bounds/alpha measures; complete body-selection diagnostic transforms absent.'),
    'motion': (['sprite-workbench review'], 'partial_local', 'Adjacent-frame and loop-seam packet only; semantic contacts/arcs/owner motion need authored requirements.'),
    'storyboard': (['sprite-workbench review'], 'partial_local', 'All frames and ordered pairs retained; no vendor reason-based storyboard selection.'),
    'reveal': ([], 'local_pending', 'No exposed registered-rest-mask disocclusion diagnostic.'),
    'crop': (['sprite-workbench crop'], 'partial_local', 'Inclusive local raster crop with a local content guard; transformed vendor node wire dialect absent.'),
    'sweep': ([], 'local_pending', 'No bounded Cartesian craft sweep service.'),
    'score': ([], 'local_pending', 'No local 0-100 pixel-discipline score or vendor formula; art acceptance remains separate.'),
    'extract-palette': ([], 'local_pending', 'No exposed exact-inventory/ramp-proposal command; raw project palettes can be edited separately.'),
    'repair': ([], 'local_pending', 'No named regrid/defringe/snap/stray/holes/deflicker craft service.'),
    'shade': ([], 'local_pending', 'No source-backed light/material shading craft service.'),
    'selout': ([], 'local_pending', 'No source-backed selective-outline craft service.'),
    'reoutline': ([], 'local_pending', 'No node-bake reoutline service; raster outline operation is a different contract.'),
    'clean-lines': ([], 'local_pending', 'No guarded doubled-corner craft service.'),
    'aa': ([], 'local_pending', 'No interior material-ramp antialias craft service.'),
    'mirror': ([], 'local_pending', 'No exposed node-to-node mirror/bake craft service; coordinate flip helpers do not supply artwork.'),
    'cluster': ([], 'local_pending', 'No fingerprint-bound cluster recolor/delete/nudge service.'),
    'paste': (['sprite-workbench paste'], 'partial_local', 'Guarded raw raster replace/stamp only; transformed/anchored vendor node destination semantics not implemented.'),
    'compare': (['sprite-workbench lab compare'], 'partial_local', 'Supplied sequences with exact pixels/clocks and explicit stores; no hidden registration or vendor drawing dialect.'),
    'palette': ([], 'local_pending', 'Palette transactions preserve aliases; no exposed hue-shifted ramp-generator command or vendor formula.'),
}

# Source-defined transport/lifecycle branches: explicit mappings, no fuzzy names.
TRANSPORT_COMPARISONS = {
    'web-chat-session-stream': ['F11'],
    'web-object-consistent-style-submit-poll': ['F05', 'F07'],
    'web-object-directions-submit-poll': ['F05'],
    'web-object-candidate-promotion': ['F05'],
    'web-object-expansion-accept-dismiss': ['F05'],
    'creator-generic-background-websocket': ['F11'],
    'godot-background-lifecycle': ['F11'],
    'lua-queued-retry-durable-archive': ['F11'],
    'enhancement-callback-lifetime': ['F07'],
    'creator-gallery-local-cloud': ['F04', 'F05'],
    'inline-standalone-editor-save-hosts': ['F01', 'F10'],
    'character-object-state-refresh-pagination': ['F04', 'F05'],
    'animation-group-writer-persistence': ['F04', 'F05'],
    'injected-retry-completion-delete-order': ['F11'],
    'ui-split-state-grid-layout-finalization': ['F08'],
    'font-gallery-download-reload': ['F08'],
    'vocal-expression-grid-autosave': ['F08'],
    'native-web-export-boundaries': ['F10'],
    'public-v2-job-control': ['F11'],
    'public-upload-ticket': ['F11'],
    'mcp-job-wait-control': ['F11'],
    'mcp-save-undo-promotion': ['F01', 'F05'],
    'godot-tool-dispatch-concurrency': ['F11'],
    'native-cel-write-undo-stale': ['F01', 'F10'],
    'chat-html-preview-composer-bridge': ['F11'],
    'mcp-pixel-vfx-command-dialects': ['F02', 'F09'],
    'chat-object-library-project-pagination': ['F05'],
    'native-font-atlas-ttf-history-file': ['F08', 'F10'],
    'ui-preset-raw-save-load-remount': ['F08'],
    'shared-object-list-and-active-job-refresh': ['F05', 'F11'],
}


def build(research):
    sources = []

    def evidence(path, namespace='workbench', pointer=None):
        base = ROOT if namespace == 'workbench' else research
        p = base / path
        row = {'namespace': namespace, 'path': path, 'sha256': sha(p)}
        if pointer is not None:
            row['pointer'] = pointer
        identity = (namespace, path)
        if identity not in {(x['namespace'], x['path']) for x in sources}:
            sources.append({k: v for k, v in row.items() if k != 'pointer'})
        return row

    original = 'docs/consolidation-review/source-coverage/ORIGINAL-63-DISPOSITIONS.json'
    family_path = 'analysis-contract/depth-round2/full-feature-gaps/FAMILY-STAGE-SPEC.json'
    family_data = load(research / family_path)
    source_rows = load(ROOT / original)['rows']
    command_path = 'analysis-root/full-reconstruction/PIXEL-COMMAND-CONTRACTS.json'
    commands_data = load(research / command_path)
    transport_path = 'analysis-contract/depth-round4/full-flow-contracts/FLOW-CONTRACTS.json'
    transport_data = load(research / transport_path)['flows']
    anchor_path = 'analysis-contract/depth-round4/full-flow-contracts/SOURCE-ANCHORS.json'
    anchors = load(research / anchor_path)['anchors']
    source_checks = []
    for a in anchors:
        p = research / a['source']
        raw = p.read_bytes()
        start, stop = a['utf8']
        source_checks.append({'id': a['id'], 'source': a['source'],
            'source_hash_matches': sha(p) == a['source_sha256'],
            'range_in_bounds': 0 <= start <= stop <= len(raw),
            'slice_hash_matches': hashlib.sha256(raw[start:stop]).hexdigest() == a['slice_sha256']})
        evidence(a['source'], 'research')
    anchor_ids = {a['id'] for a in anchors}
    requirements = []
    for i, r in enumerate(source_rows):
        auth = r['original_resolution_authorities']
        # The ledger's actual original authority is kept for every row. These
        # statuses describe evidence availability, not successful replication.
        if auth == ['server-source-or-provider-disclosure']:
            status, kind = 'unavailable_server', 'interface-only/private-implementation-unprovided'
            answer = 'No legitimately available server source/model artifact in the inspected sources resolves: ' + r['original_question'] + '.'
            next_action = 'Provider disclosure or released implementation/weights is required for exact parity. A named local substitute may be specified separately; it cannot close this original question.'
        elif 'shipped-source-trace' in auth:
            status, kind = 'source_partial', 'retained-shipped-source-analysis'
            answer = r['current_source_answer']
            next_action = 'Bind the named source methods to an executable versioned adapter and independently verify its complete declared branches. Preserve runtime/provider qualifications in this source answer.'
        else:
            status, kind = 'runtime_pending', 'selected-retained-observations'
            answer = 'Retained observations are bounded as follows: ' + ' '.join(family_data[r['family']]['existing_runtime_observations'])
            next_action = 'Freeze a discriminating protocol for this exact question and compare retained matched outputs where possible. Missing vendor-runtime branches cannot be inferred from local synthetic diagnostics.'
        family, routes, gap = FAMILIES[r['family']]
        requirements.append({
            'id': r['id'], 'title': r['original_question'], 'family': r['family'], 'flow': family,
            'status': status, 'evidence_type': kind, 'analysis_disposition': answer,
            'original_authorities': auth, 'whole_question_closed': False,
            'evidence': [evidence(original, pointer=f'/rows/{i}'), evidence(family_path, 'research', '/' + r['family'])],
            'source_authorities_as_recorded': r['current_source_authorities'],
            'local_route': routes, 'local_route_scope': 'bounded local substitute only',
            'gap': gap + ' Original question remains: ' + r['original_question'] + '.',
            'next_action': next_action, 'required_for': ['comparison'],
        })
    flows = []
    for family, data in family_data.items():
        comparison, routes, gap = FAMILIES[family]
        flows.append({
            'id': family, 'title': family.replace('-', ' '), 'status': 'partial',
            'comparison_flows': [comparison], 'steps': [
                {'id': stage, 'statement': statement,
                 'status': 'source_specification_partial',
                 'assessment_as_recorded': data['stage_assessment'][stage]}
                for stage, statement in data['stages'].items()],
            'named_branches': data['named_branches'], 'public_operations': data['public_operations'],
            'source_traces': data['verified_source_traces'],
            'runtime_observations': data['existing_runtime_observations'],
            'qa_requirements': data['QA_requirements'],
            'local_routes': routes, 'gaps': [gap, *data['remaining_unknowns']],
            'required_for': ['comparison'],
            'evidence': [evidence(family_path, 'research', '/' + family)],
        })
    flows.extend([
        {'id': 'pixel-art-workbench', 'title': 'Pixel-art command grammar and raster/construction crafts',
         'status': 'partial', 'comparison_flows': ['F01', 'F02'],
         'steps': [{'id': x, 'status': 'documented_or_partial_local'} for x in ['argv-and-subject-resolution', 'job-scene-validation', 'draw-and-edit', 'diagnose-and-craft', 'review-and-revise', 'save-undo-export']],
         'local_routes': ['sprite-workbench construct', 'sprite-workbench edit', 'pipeline.scene', 'pipeline.tracks'],
         'gaps': ['Nested draw_commands suffix is server-truncated; hosted handlers and heuristic crafts are not shipped source.',
                  '28 captured help commands are not28 executable local equivalents.'],
         'required_for': ['comparison'], 'evidence': [evidence(command_path, 'research')]},
        {'id': 'procedural-vfx', 'title': 'Procedural effect recipes, body layering and worker execution',
         'status': 'partial', 'comparison_flows': ['F09'],
         'steps': [{'id': x, 'status': 'partial_local'} for x in ['recipe-validation', 'subject-normal-acquisition', 'pinned-family-render', 'back-body-front-composition', 'clock-and-crop-export', 'worker-bootstrap-and-review']],
         'local_routes': ['pipeline.effects', 'pipeline.compose'],
         'gaps': ['17 recovered procedural families are executable; all105 prepared constructors are not recovered.',
                  'Browser Worker/bootstrap/GPU/CSP and continuous visual review are separate unverified branches.'],
         'required_for': ['comparison'], 'evidence': [evidence('docs/RASTER-AND-EFFECTS.md'), evidence('docs/COVERAGE.md')]},
    ])
    commands = []
    for i, c in enumerate(commands_data['commands']):
        routes, status, gap = COMMAND_ROUTES[c['command']]
        help_evidence = c['help']
        returned_help = load(research / help_evidence['response_path'])['result']['content'][0]['text']
        commands.append({
            'name': c['command'], 'status': status, 'category': c['category'],
            'syntax': returned_help.splitlines(), 'usage_lines_as_recorded': c['usage'],
            'syntax_authority': 'Verbatim returned help; subject/flag lines are not a fully typed nested schema.',
            'flags': [f['flag'] for f in c['flags']],
            'semantics': c['semantics'], 'local_route': routes,
            'local_policy': c['local_reconstruction_decision'],
            'gap': gap + ' Retained handler uncertainty: ' + c['remaining_handler_or_exact_algorithm_unknowns'],
            'vendor_handler_recovered': False, 'vendor_conformance_complete': False,
            'required_for': ['comparison'],
            'evidence': [evidence(command_path, 'research', f'/commands/{i}'),
                         evidence(help_evidence['response_path'], 'research', help_evidence['json_pointer'])],
        })
    transports = []
    for i, t in enumerate(transport_data):
        transports.append({
            'id': t['flow_id'], 'source_status_as_recorded': t['status'],
            'comparison_flows': TRANSPORT_COMPARISONS[t['flow_id']],
            'status': 'source_partial' if 'partial' in t['status'] or 'docs-only' in t['status'] else 'bounded_source_answer',
            'steps': t['operation_handler_adapter_state_output'],
            'minimum_input': t['minimum_input'], 'minimum_output': t['minimum_output'],
            'state_semantics': t['state_semantics'], 'clocks': t['clocks'],
            'failure_semantics': t['failure_semantics'],
            'cancel_stale_retry_semantics': t['cancel_stale_retry_semantics'],
            'persistence': t['persistence'], 'undo_promotion_semantics': t['undo_promotion_semantics'],
            'gap': t['unrecovered_boundary'],
            'source_anchor_ids': t['source_anchor_ids'],
            'source_anchor_records': [a for a in anchors if a['id'] in t['source_anchor_ids']],
            'missing_anchor_ids': sorted(set(t['source_anchor_ids']) - anchor_ids),
            'vendor_runtime_verified_by_this_pass': False,
            'evidence': [evidence(transport_path, 'research', f'/flows/{i}'), evidence(anchor_path, 'research')],
        })
    comparisons = []
    runtime = load(ROOT / 'docs/consolidation-review/runtime/FLOW-COVERAGE.json')
    for r in runtime['rows']:
        flow = r['flow']
        receipt = f'docs/local-replication/evidence/checkout-replay/{flow}-RECEIPT.json'
        actual = load(ROOT / receipt)
        comparisons.append({'id': flow, 'status': 'bounded_diagnostic_verified',
            'local_subset': r['local_subset'], 'broad_gap': r['still_open'],
            'whole_flow_complete': False, 'art_quality_accepted': False,
            'recipe': f'sprite-workbench lab replay --flow {flow} --output ABSENT_DIRECTORY',
            'retained_checks': len(actual['checks']),
            'retained_checks_passed': sum(x['passed'] for x in actual['checks']),
            'routine_order': actual.get('routine_order', []),
            'evidence': [evidence(receipt), evidence('docs/WHOLE-FLOW-COMPARISONS.md'), evidence('docs/COVERAGE.md')]})
    interfaces = []
    for path, key, domain in [('sprite_workbench/contracts/PUBLIC-OPERATION-CONTRACTS.json', 'operations', 'public'),
                              ('sprite_workbench/contracts/MCP-TOOL-CONTRACTS.json', 'tools', 'mcp')]:
        for i, op in enumerate(load(ROOT / path)[key]):
            interfaces.append({'id': op['id'], 'domain': domain, 'status': 'unsupported_remote_handler',
                'families': op.get('families', op.get('family_association', [])),
                'local_route': None, 'gap': 'Frozen interface/schema only; no remote handler or learned implementation is bound locally.',
                'evidence': [evidence(path, pointer=f'/{key}/{i}')]})
    drift = load(ROOT / 'docs/readiness/ANALYSIS-public/PUBLIC-DRIFT.json')
    current = load(ROOT / 'docs/readiness/ANALYSIS-public/openapi.json')
    evidence('docs/readiness/ANALYSIS-public/PUBLIC-DRIFT.json')
    evidence('analysis-root/sdk-transport-closure/public-sources/openapi-current.json', 'research')
    for name in drift['added']:
        method, path = name.split(' ', 1)
        interfaces.append({'id': 'current-public:' + method + ':' + path, 'domain': 'current-public-addition',
            'status': 'unsupported_remote_handler', 'families': ['normal-map'] if path == '/normal-map' else [],
            'local_route': None, 'gap': 'Current primary-source addition: schema and declared behavior recovered; server algorithm and local equivalent unprovided.',
            'evidence': [evidence('docs/readiness/ANALYSIS-public/openapi.json', pointer='/paths/' + path.replace('~','~0').replace('/','~1') + '/' + method.lower())]})
    grammar = {
        'status': 'incomplete_vendor_grammar', 'complete': False,
        'outer_mcp_schema': next(t['inputSchema'] for t in load(ROOT / 'sprite_workbench/contracts/MCP-TOOL-CONTRACTS.json')['tools'] if t['name'] == 'pixelart_workbench'),
        'captured_help_command_count': len(commands),
        'captured_conditional_question_count': len(commands_data['declared_conditional_questions']),
        'declared_conditionals': commands_data['declared_conditional_questions'],
        'draw_commands_visible_prefix': ['rect', 'ellipse', 'circle', 'polygon', 'path'],
        'draw_commands_visible_prefix_is_exhaustive': False,
        'missing_draw_commands_suffix_lines_as_reported': 82,
        'full_flag_result': 'Explicit error: --full is not available here; describe takes no flags.',
        'source_search_boundary': 'Retained selected595 JS/Lua/GD/Python/TS files; not proof of absence from arbitrary server/provider code.',
        'official_public_source_result': 'Current official MCP repository remains pinned README-only; current Python/JS heads unchanged. Public OpenAPI/llms describe REST interfaces, not nested hosted workbench draw grammar.',
        'public_sources_checked': ['https://api.pixellab.ai/v2/llms.txt', 'https://api.pixellab.ai/v2/openapi.json', 'https://github.com/pixellab-code/pixellab-mcp', 'https://github.com/pixellab-code/pixellab-js', 'https://github.com/pixellab-code/pixellab-python'],
        'local_dialects': [
            {'id': 'sprite-workbench-plan/v1', 'route': 'sprite-workbench run', 'evidence': evidence('sprite_workbench/pipeline.py'), 'scope': 'Local explicit action/argument dialect; not vendor argv parser parity.'},
            {'id': 'construction-services/v1', 'route': 'sprite-workbench construct', 'evidence': evidence('sprite_workbench/construction_services.py'), 'scope': 'Local typed indexed project/history/ASE service schemas; not native vendor indexed host parity.'},
            {'id': 'local-raster/v1', 'route': 'sprite-workbench edit', 'evidence': evidence('sprite_workbench/raster.py'), 'scope': 'Local guarded raster operations; not all workbench crafts.'},
        ],
        'next_evidence': 'A complete provider-issued schema/document or separately scoped authenticated read-only documentation capture exposing the omitted section. Do not try generation calls to guess the grammar.',
        'required_for': ['comparison'],
        'evidence': [evidence('analysis-root/workbench-grammar-capture/decoded-docs/078-pixelart-describe-draw_commands-high.text-0.md', 'research'),
                     evidence('analysis-root/workbench-grammar-capture/decoded-docs/082-pixelart-describe-draw_commands-full-probe.text-0.md', 'research'),
                     evidence('analysis-root/full-reconstruction/PIXEL-HANDLER-SOURCE-SEARCH.json', 'research'),
                     evidence('docs/readiness/ANALYSIS-public/RETRIEVAL.json')],
    }
    scene_path = 'analysis-root/workbench-grammar-capture/decoded-docs/013-pixelart-describe-scenes.text-0.md'
    scene_text = (research / scene_path).read_text()
    # Complete documented table, unlike the independently truncated structured
    # topic. The table's optional marker is the exact field authority here.
    required_optional = {
        'copy': (['part'], ['region', 'method']),
        'path': (['points', 'color'], ['outline', 'stroke_width']),
        'brush': (['points', 'color'], ['size', 'shape', 'pixel_perfect']),
        'polygon': (['points', 'color'], ['fill', 'outline', 'stroke_width']),
        'rect': (['box', 'color'], ['fill', 'outline', 'stroke_width']),
        'ellipse': (['box', 'color'], ['fill', 'outline', 'stroke_width']),
        'circle': (['center', 'radius', 'color'], ['fill', 'outline', 'stroke_width']),
        'pixels': (['pixels'], []),
        'grid': (['rows', 'legend'], ['at', 'mode']),
    }
    primitives = []
    for number, line in enumerate(scene_text.splitlines(), 1):
        if not line.startswith('| `'):
            continue
        cells = [x.strip() for x in line.split('|')[1:-1]]
        name = cells[0].strip('`')
        required, optional = required_optional[name]
        primitives.append({'name': name, 'required_fields_as_documented': ['op', *required],
            'optional_fields_as_documented': optional,
            'field_contract_verbatim': cells[1], 'behavior_verbatim': cells[2],
            'status': 'complete_documented_table_row_not_complete_handler_schema',
            'unknown_field_policy': 'not specified by this table',
            'local_route': None,
            'evidence': {**evidence(scene_path, 'research'), 'one_based_line': number,
                         'line_sha256': hashlib.sha256(line.encode()).hexdigest()}})
    changes_path = 'analysis-root/workbench-grammar-capture/decoded-docs/018-pixelart-describe-change_operations.text-0.md'
    coordinates_path = 'analysis-root/workbench-grammar-capture/decoded-docs/019-pixelart-describe-coordinates.text-0.md'
    claim_path = 'analysis-models/depth-round2/workbench-pixel-grammar/CLAIM-LEDGER.json'
    grammar.update({
        'documented_primitive_inventory_complete': True,
        'documented_primitive_inventory_authority': 'Complete nine-row describe-scenes table, not reconstruction of the missing JSON suffix.',
        'documented_primitives': primitives,
        'change_operations_as_disclosed': load(research / changes_path)['change_operations'],
        'coordinates_as_disclosed': load(research / coordinates_path)['coordinates'],
        'retained_grammar_claims': load(research / claim_path)['claims'],
        'specific_unresolved_syntax': [
            'patch_command command index base is not specified; one-based frame indexing does not establish command indexing.',
            'patch_command expect format and action-specific values/fields/value discriminator are not fully typed.',
            'Blank field descriptions in the truncated structured topic do not establish defaults or validation.',
            'Full copy/grid/pixels/brush nested validation and unknown-field acceptance are not a complete machine schema in the nine-row table.',
            'A prose operation name or module path does not recover its private heuristic/raster implementation.',
        ],
    })
    grammar['evidence'].extend([evidence(changes_path, 'research'), evidence(coordinates_path, 'research'), evidence(claim_path, 'research')])
    blockers = [{'id': 'requirement:' + r['id'], 'requirement': r['id'], 'status': r['status'],
                 'required_for': r['required_for'], 'gap': r['title'], 'next_action': r['next_action']} for r in requirements]
    blockers.extend([
        {'id': 'vendor-draw-grammar', 'status': 'unavailable_documentation', 'required_for': ['comparison'], 'gap': 'Full nested draw grammar still unprovided.', 'next_action': grammar['next_evidence']},
        {'id': 'local-command-coverage', 'status': 'local_pending', 'required_for': ['comparison'], 'gap': 'Captured28-command help inventory has partial or absent local equivalents.', 'next_action': 'Implement explicitly named local dialects and independent discriminating checks, preserving vendor algorithm unknowns.'},
        {'id': 'vfx-prepared-constructors', 'status': 'source_partial', 'required_for': ['comparison'], 'gap': '17 procedural families do not recover all105 prepared constructors.', 'next_action': 'Bind every constructor to exact source or explicit recipe data; keep unavailable ones unsupported.'},
        {'id': 'current-public-drift', 'status': 'contract_drift', 'required_for': ['comparison'], 'gap': 'Current112-operation surface adds normal-map and changes5 operationobjects relative to the prior public-source snapshot.', 'next_action': 'Bind the current snapshot separately; retain the old111/101 interfaces for historical comparisons and keep new handlers unsupported.'},
    ])
    result = {'version': 1,
        'scope': {'authority': 'Explicit finite evidence reconciliation, not universal vendor parity or art approval',
                  'analysis_accounted': True, 'all_questions_answered': False,
                  'setup_ready': False, 'comparison_ready': False,
                  'source_namespaces': {'workbench': 'this checkout', 'research': 'the retained PixelLab investigation root; path supplied at build time'},
                  'original_feature_families': 21, 'additional_analysis_families': ['pixel-art-workbench', 'procedural-vfx'],
                  'new_art_or_model_calls': 0, 'new_provider_feature_calls': 0,
                  'public_read_only_documentation_refresh': True,
                  'setup_verification_authority': 'The host readiness service must check setup live; this catalog never asserts setup success.'},
        'requirements': requirements, 'flows': flows, 'commands': commands, 'grammar': grammar,
        'transport_flows': transports, 'comparisons': comparisons, 'interfaces': interfaces,
        'source_anchor_verification': {'scope': 'Actual retained file and end-exclusive UTF8 slice hashes; not runtime execution.',
            'anchors_checked': len(source_checks), 'all_passed': all(
                c['source_hash_matches'] and c['range_in_bounds'] and c['slice_hash_matches'] for c in source_checks),
            'checks': source_checks},
        'current_public_drift': drift, 'blockers': blockers, 'source_manifest': sources,
        'counts': {'original_requirements': len(requirements), 'original_requirements_closed': 0,
                   'requirements_by_status': dict(Counter(r['status'] for r in requirements)),
                   'feature_flows': len(flows), 'captured_commands': len(commands),
                   'commands_by_status': dict(Counter(c['status'] for c in commands)),
                   'source_transport_flows': len(transports), 'comparison_recipes': len(comparisons),
                   'historical_public_interfaces': 111, 'historical_mcp_interfaces': 101,
                   'current_public_interfaces': len([1 for p in current['paths'].values() for m in p if m in {'get','post','put','patch','delete','head','options','trace'}]),
                   'tracked_interface_records': len(interfaces)},
    }
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--research', type=Path, required=True)
    p.add_argument('--output', type=Path, default=ROOT / 'sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json')
    args = p.parse_args()
    catalog = build(args.research.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=True, allow_nan=False) + '\n')
    print(json.dumps(catalog['counts'], indent=2))
