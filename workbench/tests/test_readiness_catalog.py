"""Independent accounting checks: losing a row must never open a readiness gate."""
from collections import Counter
import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json'


@pytest.fixture(scope='module')
def catalog():
    return json.loads(CATALOG.read_text())


def test_all_original_questions_preserve_identity_and_authority(catalog):
    original = json.loads((ROOT / 'docs/consolidation-review/source-coverage/ORIGINAL-63-DISPOSITIONS.json').read_text())['rows']
    actual = catalog['requirements']
    assert len(actual) == len(original) == 63
    assert len({r['id'] for r in actual}) == 63
    for new, old in zip(actual, original):
        assert (new['id'], new['title'], new['family'], new['original_authorities']) == (
            old['id'], old['original_question'], old['family'], old['original_resolution_authorities'])
        assert new['whole_question_closed'] is False
        assert new['required_for'] == ['comparison']
        assert new['next_action'] and new['gap'] and new['evidence']


def test_authority_buckets_are_not_completion_counts(catalog):
    rows = catalog['requirements']
    assert Counter(r['status'] for r in rows) == {
        'runtime_pending': 24, 'source_partial': 18, 'unavailable_server': 21}
    for r in rows:
        if r['status'] == 'unavailable_server':
            assert r['original_authorities'] == ['server-source-or-provider-disclosure']
        if r['status'] == 'source_partial':
            assert 'shipped-source-trace' in r['original_authorities']
    assert catalog['counts']['original_requirements_closed'] == 0


def test_catalog_does_not_enable_its_own_setup_or_comparisons(catalog):
    assert catalog['version'] == 1
    scope = catalog['scope']
    assert scope['setup_ready'] is False
    assert scope['comparison_ready'] is False
    assert scope['all_questions_answered'] is False
    assert scope['new_art_or_model_calls'] == scope['new_provider_feature_calls'] == 0
    ids = {r['requirement'] for r in catalog['blockers'] if 'requirement' in r}
    assert ids == {r['id'] for r in catalog['requirements']}
    assert all(b['required_for'] == ['comparison'] for b in catalog['blockers'])


def test_feature_families_and_comparisons_are_distinct(catalog):
    families = {r['family'] for r in catalog['requirements']}
    flows = {r['id']: r for r in catalog['flows']}
    assert len(families) == 21
    assert set(flows) == families | {'pixel-art-workbench', 'procedural-vfx'}
    assert len(flows) == 23
    assert len(catalog['comparisons']) == 11
    comparison_ids = {f'F{i:02d}' for i in range(1, 12)}
    assert {r['id'] for r in catalog['comparisons']} == comparison_ids
    for r in catalog['requirements']:
        assert r['flow'] in comparison_ids
        assert r['flow'] in flows[r['family']]['comparison_flows']
    for f in flows.values():
        assert f['steps'] and f['gaps'] and f['evidence']
        assert f['status'] == 'partial'


def test_every_help_command_has_a_real_individual_disposition(catalog):
    expected = {
        'inspect', 'edit', 'draw', 'describe', 'lint', 'measure', 'explain',
        'clusters', 'parts', 'silhouette', 'motion', 'storyboard', 'reveal',
        'crop', 'sweep', 'score', 'extract-palette', 'repair', 'shade', 'selout',
        'reoutline', 'clean-lines', 'aa', 'mirror', 'cluster', 'paste', 'compare', 'palette'}
    commands = catalog['commands']
    assert len(commands) == len(expected) == 28
    assert {r['name'] for r in commands} == expected
    assert Counter(r['status'] for r in commands) == {'partial_local': 13, 'local_pending': 15}
    for r in commands:
        assert r['syntax'] and r['semantics'] and r['gap'] and r['evidence']
        assert r['vendor_handler_recovered'] is False
        assert r['vendor_conformance_complete'] is False
        if r['status'] == 'local_pending':
            assert r['local_route'] == []


def test_truncated_grammar_is_not_completed_by_a_prefix(catalog):
    g = catalog['grammar']
    assert g['complete'] is False
    assert g['status'] == 'incomplete_vendor_grammar'
    assert g['draw_commands_visible_prefix'] == ['rect', 'ellipse', 'circle', 'polygon', 'path']
    assert g['draw_commands_visible_prefix_is_exhaustive'] is False
    assert g['missing_draw_commands_suffix_lines_as_reported'] == 82
    assert g['full_flag_result'].startswith('Explicit error:')
    assert len(g['declared_conditionals']) == 56
    assert {r['id'] for r in g['declared_conditionals']} == {f'C{i:02d}' for i in range(1, 57)}
    assert 'additionalProperties' in g['outer_mcp_schema']


def test_all_thirty_source_transport_flows_are_accounted(catalog):
    rows = catalog['transport_flows']
    assert len(rows) == len({r['id'] for r in rows}) == 30
    for r in rows:
        assert r['steps'] and r['minimum_input'] is not None
        assert r['minimum_output'] is not None and r['gap']
        assert r['vendor_runtime_verified_by_this_pass'] is False
        assert set(r['comparison_flows']) <= {f'F{i:02d}' for i in range(1, 12)}
        assert r['missing_anchor_ids'] == []
        assert {a['id'] for a in r['source_anchor_records']} == set(r['source_anchor_ids'])


def test_documented_nine_primitive_inventory_is_separate_from_incomplete_schema(catalog):
    g = catalog['grammar']
    assert g['documented_primitive_inventory_complete'] is True
    assert g['complete'] is False
    primitives = {r['name']: r for r in g['documented_primitives']}
    assert set(primitives) == {'copy', 'path', 'brush', 'polygon', 'rect', 'ellipse', 'circle', 'pixels', 'grid'}
    assert primitives['copy']['required_fields_as_documented'] == ['op', 'part']
    assert primitives['grid']['optional_fields_as_documented'] == ['at', 'mode']
    assert primitives['pixels']['required_fields_as_documented'] == ['op', 'pixels']
    assert len(g['retained_grammar_claims']) == 42
    assert g['coordinates_as_disclosed']['frames'].startswith('1-based')
    assert set(g['change_operations_as_disclosed']) == {
        'set_node', 'patch_command', 'duration', 'add_node', 'set_track', 'raster (pixel_edits)', 'pixels / replace_color'}
    for p in primitives.values():
        assert p['local_route'] is None  # documented syntax is not an executable adapter
        assert p['evidence']['one_based_line'] > 0 and len(p['evidence']['line_sha256']) == 64


def test_all_original_source_anchor_bytes_were_rechecked(catalog):
    v = catalog['source_anchor_verification']
    assert v['anchors_checked'] == len(v['checks']) == 64
    assert v['all_passed'] is True
    assert len({r['id'] for r in v['checks']}) == 64
    assert all(r['source_hash_matches'] and r['range_in_bounds'] and r['slice_hash_matches'] for r in v['checks'])


def test_all_retained_interfaces_remain_individually_unsupported(catalog):
    public = json.loads((ROOT / 'sprite_workbench/contracts/PUBLIC-OPERATION-CONTRACTS.json').read_text())['operations']
    mcp = json.loads((ROOT / 'sprite_workbench/contracts/MCP-TOOL-CONTRACTS.json').read_text())['tools']
    expected = {r['id'] for r in public + mcp}
    actual = {r['id'] for r in catalog['interfaces'] if r['domain'] != 'current-public-addition'}
    assert len(expected) == 212 and actual == expected
    assert all(r['status'] == 'unsupported_remote_handler' and r['local_route'] is None for r in catalog['interfaces'])


def test_current_primary_source_addition_does_not_rewrite_frozen_baseline(catalog):
    c = catalog['counts']
    assert (c['historical_public_interfaces'], c['historical_mcp_interfaces']) == (111, 101)
    assert c['current_public_interfaces'] == 112
    assert c['tracked_interface_records'] == 213
    added = [r for r in catalog['interfaces'] if r['domain'] == 'current-public-addition']
    assert [r['id'] for r in added] == ['current-public:POST:/normal-map']
    d = catalog['current_public_drift']
    assert d['added'] == ['POST /normal-map'] and d['removed'] == []
    assert len(d['changed']) == 5
    assert d['schemas_added'] == ['NormalMapRequest', 'NormalMapResponse']
    assert d['schemas_changed'] == ['AnimateWithTextV2Request', 'CreateCharacterAnimationRequest', 'TargetPalette']
    pointers = {r['pointer'] for r in d['leaf_changes']}
    assert '/components/schemas/TargetPalette/properties/smart' in pointers
    assert '/paths/~1normal-map' in pointers
    assert {r['id'] for r in d['current_semantic_additions']} == {
        'normal-map', 'smart-target-palette', 'pro-output-grid-size-buckets', 'template-animation-batch-billing'}


def test_retained_diagnostic_receipts_do_not_close_broad_flows(catalog):
    for r in catalog['comparisons']:
        assert r['whole_flow_complete'] is False
        assert r['art_quality_accepted'] is False
        assert r['retained_checks'] == r['retained_checks_passed'] > 0
        receipt = ROOT / f"docs/local-replication/evidence/checkout-replay/{r['id']}-RECEIPT.json"
        original = json.loads(receipt.read_text())
        assert original['whole_flow_completed'] is False
        assert len(original['checks']) == r['retained_checks']


def test_every_workbench_evidence_digest_matches_retained_bytes(catalog):
    rows = catalog['source_manifest']
    identities = [(r['namespace'], r['path']) for r in rows]
    assert len(identities) == len(set(identities))
    for r in rows:
        assert len(r['sha256']) == 64 and all(c in '0123456789abcdef' for c in r['sha256'])
        assert not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts
        if r['namespace'] == 'workbench':
            assert hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], r['path']


def test_normal_map_contract_records_prose_constraints_separately():
    public = json.loads((ROOT / 'docs/readiness/ANALYSIS-public/openapi.json').read_text())
    op = public['paths']['/normal-map']['post']
    req = public['components']['schemas']['NormalMapRequest']
    assert 'up to 32 frames' in op['description']
    assert req['properties']['frames']['minimum'] == 1
    assert 'maximum' not in req['properties']['frames']  # prose is not a schema-enforced bound
    assert req['additionalProperties'] is False
    assert req['properties']['convention']['enum'] == ['opengl', 'directx']
