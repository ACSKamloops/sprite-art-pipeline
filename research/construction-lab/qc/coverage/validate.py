#!/usr/bin/env python3
"""Exact family/actor/equipment/direction coverage gate; aliases never substitute.
Requirements are a separately hash-recorded production contract, not inferred
from whatever asset names happen to remain in a candidate matrix.
"""
import argparse, hashlib, json, sys
from pathlib import Path
FIELDS = ('family', 'actor', 'equipment', 'direction', 'variant')

def validate(matrix, contract, gate_name, verify_sources=False):
    issues = []
    tests = 0
    atoms = {}
    families = {}

    def issue(code, detail):
        issues.append({'code': code, 'detail': detail})
    if matrix.get('schema') != 'sprite-family-coverage/v1' or contract.get('schema') != 'sprite-family-requirements/v1':
        issue('schema', 'Unsupported coverage or requirement schema')
    if verify_sources and 'current_corrected_player_gpu_bridge' in matrix.get('source_ledger', {}):
        from current_gpu_bridge import verify_bridge
        ledger = matrix['source_ledger']
        result = verify_bridge(Path(ledger['current_corrected_player_gpu_bridge']['path']), Path(ledger['native_player']['path']).parents[1], Path(ledger['native_gpu_audit']['path']))
        tests += 1
        if not result['passed']:
            issue('current_gpu_bridge_hashchain_failed', result)
    gate = contract['gates'][gate_name]
    if not matrix.get('source_audit', {}).get('catalog_consistency_passed', False):
        issue('source_audit_failed', 'Nativecatalog/source count consistency audit does not pass')
    for gap in gate.get('unresolved_scope_gaps', []):
        issue('unresolved_scope_gap', gap)
    for row in matrix['families']:
        tests += 1
        if row['id'] in families:
            issue('duplicate_family', row['id'])
        families[row['id']] = row
        if row.get('quality_approved') is True and (not row.get('newly_authored', {}).get('clips') or row.get('quality_decision') != 'approved_production'):
            issue('unsupported_art_approval', row['id'])
    for atom in matrix['atoms']:
        tests += 1
        expected = '|'.join((str(atom[k]) for k in FIELDS))
        if atom['id'] != expected:
            issue('identity_mismatch', atom['id'])
        if atom['id'] in atoms:
            issue('duplicate_binding', atom['id'])
        if atom['family'] not in families:
            issue('unregistered_family', atom['id'])
        if any((k in atom for k in ['alias', 'fallback', 'fallback_id', 'default_direction'])):
            issue('alias_fallback_forbidden', atom['id'])
        if not all((e in matrix['source_ledger'] for e in atom.get('evidence', []))):
            issue('missing_source_binding', atom['id'])
        atoms[atom['id']] = atom
    required_by_id = {r['id']: r for r in contract['production_atoms']}
    for id in gate.get('required_families', []):
        tests += 1
        if id not in families:
            issue('missing_family', id)
    for id in gate.get('required_ids', []):
        tests += 1
        candidate = atoms.get(id)
        expected = required_by_id[id]
        if candidate is None:
            issue('missing_animation_binding', id)
            continue
        if any((candidate[k] != expected[k] for k in FIELDS)):
            issue('binding_dimension_mismatch', id)
        state = candidate.get('stages', {}).get(gate['stage'], 'not_covered')
        if state not in gate['accepted_states']:
            issue('stage_incomplete', {'id': id, 'stage': gate['stage'], 'state': state})
        if gate['stage'] == 'quality_approved' and state == 'approved_production':
            art = candidate.get('authored_asset_binding')
            review = candidate.get('art_review_binding')
            if not isinstance(art, dict) or not art.get('frame_ids') or art.get('project_evidence') not in matrix['source_ledger'] or (not art.get('export_evidence')):
                issue('approval_without_authored_assets', id)
            if not isinstance(review, dict) or review.get('decision') != 'approved' or review.get('evidence') not in matrix['source_ledger'] or (id not in review.get('clip_ids', [])) or (not review.get('input_fingerprint')):
                issue('approval_without_current_review', id)
            if isinstance(art, dict) and isinstance(review, dict) and (review.get('evidence') in matrix['source_ledger']):
                evidence = matrix['source_ledger']
                review_path = Path(evidence[review['evidence']]['path'])
                if not review_path.is_file():
                    issue('approval_review_unavailable', id)
                else:
                    actual_review = json.loads(review_path.read_text())
                    if hashlib.sha256(review_path.read_bytes()).hexdigest() != evidence[review['evidence']]['sha256']:
                        issue('stale_approval_review', id)
                    if actual_review.get('decision') != 'approved' or id not in actual_review.get('clip_ids', []) or actual_review.get('input_fingerprint') != review.get('input_fingerprint'):
                        issue('actual_review_does_not_approve_binding', id)
                    asset_ids = [art.get('project_evidence')] + (art.get('export_evidence') if isinstance(art.get('export_evidence'), list) else [])
                    if not isinstance(art.get('export_evidence'), list) or not art['export_evidence']:
                        issue('approval_missing_export_artifacts', id)
                    for asset_id in asset_ids:
                        if asset_id not in evidence or actual_review.get('asset_sha256', {}).get(asset_id) != evidence.get(asset_id, {}).get('sha256'):
                            issue('approval_not_bound_to_current_asset', {'id': id, 'asset': asset_id})
                    if art.get('project_evidence') in evidence:
                        project_path = Path(evidence[art['project_evidence']]['path'])
                        if not project_path.is_file():
                            issue('authored_project_unavailable', id)
                        else:
                            project = json.loads(project_path.read_text())
                            if project.get('schema') != 'sprite-edit-project/v1' or project.get('provenance', {}).get('asset_role') != 'authored_new_art':
                                issue('native_or_untyped_asset_cannot_count_as_new_art', id)
                            if not set(art.get('frame_ids', [])).issubset({f['id'] for f in project.get('frames', [])}):
                                issue('approval_missing_actual_authored_frames', id)
    if verify_sources:
        for id, s in matrix['source_ledger'].items():
            tests += 1
            p = Path(s['path'])
            if not p.is_file():
                issue('source_unavailable', {'id': id, 'path': str(p)})
                continue
            if hashlib.sha256(p.read_bytes()).hexdigest() != s['sha256']:
                issue('stale_source_binding', id)
        tests += 1
        fingerprint = hashlib.sha256(json.dumps(matrix['source_ledger'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if fingerprint != matrix['input_fingerprint']:
            issue('input_fingerprint_mismatch', fingerprint)
    return {'schema': 'sprite-family-gate-result/v1', 'gate': gate_name, 'passed': not issues, 'checks': tests, 'issues': issues, 'counts': dict(__import__('collections').Counter((i['code'] for i in issues))), 'scope': contract['scope'], 'input_fingerprint': matrix['input_fingerprint'], 'source_QA_warnings': [c['name'] for c in matrix['source_audit']['checks'] if not c['passed']], 'note': 'Passing accounting or decoded projection does not approve new art, enginecombat or whole-game family inventory.'}
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('matrix', type=Path)
    p.add_argument('--requirements', type=Path, required=True)
    p.add_argument('--gate', required=True)
    p.add_argument('--verify-sources', action='store_true')
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    r = validate(json.loads(a.matrix.read_text()), json.loads(a.requirements.read_text()), a.gate, a.verify_sources)
    r['matrix_sha256'] = hashlib.sha256(a.matrix.read_bytes()).hexdigest()
    r['requirements_sha256'] = hashlib.sha256(a.requirements.read_bytes()).hexdigest()
    a.report.write_text(json.dumps(r, indent=2) + '\n')
    print(json.dumps({'gate': r['gate'], 'passed': r['passed'], 'checks': r['checks'], 'issues_by_code': r['counts']}))
    sys.exit(0 if r['passed'] else 1)
