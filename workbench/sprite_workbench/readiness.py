"""Source-bound setup verification and explicit comparison prerequisites.

Environment probes and supplied-art diagnostics cannot close undisclosed server
algorithms or approve artwork. The comparison gate stays closed while any of
its independently catalogued prerequisites remain unresolved.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import uuid

from .core import Store, ValidationError, canonical_json, digest

LATEST_HEAD = '_readiness/latest'
HANDLER = 'local.readiness.verify'
BASELINE_SHA256 = '9b567b43bdf50badee7093b10fddf71bdeecc5e9c671725d0ef013b8087ebf04'
REQUIRED_CHECKS = {'all replay dependencies available', 'all eleven local recipe subsets',
                   'recipe artifact integrity', 'exact undo and redo',
                   'native editable project identity', 'fresh Store editable sequence',
                   'fresh Store exact history', 'fresh Store native dependencies',
                   'source unchanged during verification'}


def _catalog_blockers(catalog):
    """Do not let lost rows or optimistic aggregate flags open comparisons."""
    baseline_path = Path(__file__).resolve().parent / 'contracts/ANALYSIS-BASELINE.json'
    try:
        baseline_raw = baseline_path.read_bytes()
        if digest(baseline_raw) != BASELINE_SHA256:
            raise ValidationError('Analysis baseline differs from its code-pinned authority')
        baseline = json.loads(baseline_raw)
    except (ValueError, OSError):
        return [{'id': 'baseline-unavailable', 'title': 'Restore the analysis baseline',
                 'reason': 'The original requirement and command identities are unavailable.'}]
    problems = []
    grammar = catalog.get('grammar')
    grammar = grammar if isinstance(grammar, dict) else {}
    for name, records, field in [
        ('requirements', catalog.get('requirements'), 'id'),
        ('commands', catalog.get('commands'), 'name'),
        ('flows', catalog.get('flows'), 'id'),
        ('transport_flows', catalog.get('transport_flows'), 'id'),
        ('interfaces', catalog.get('interfaces'), 'id'),
        ('documented_primitives', grammar.get('documented_primitives'), 'name'),
        ('grammar_claims', grammar.get('retained_grammar_claims'), 'id')]:
        valid = isinstance(records, list) and all(isinstance(r, dict) and isinstance(r.get(field), str) for r in records)
        ids = [r[field] for r in records] if valid else []
        expected = baseline.get(name)
        if (not valid or not isinstance(expected, list) or len(ids) != len(set(ids))
                or set(ids) != set(expected)):
            problems.append({'id': 'inventory:' + name, 'title': 'Restore complete ' + name.replace('_', ' '),
                             'reason': 'The recorded identities differ from the retained, individually reconciled baseline.'})
    if grammar.get('complete') is not True:
        problems.append({'id': 'complete-grammar', 'title': 'Complete the drawing grammar evidence',
                         'reason': 'Documented primitives and recovered grammar claims do not recover every private nested parser rule.'})
    for field in ('commands', 'flows', 'transport_flows'):
        records = catalog.get(field)
        if (not isinstance(records, list) or not records or any(not isinstance(r, dict)
                or r.get('status') not in {'implemented_verified', 'closed_verified'} for r in records)):
            problems.append({'id': 'verified:' + field, 'title': 'Verify the required ' + field.replace('_', ' '),
                             'reason': 'Inventory entries and partial local substitutes cannot certify complete behavior.'})
    return problems


def source_fingerprint():
    root = Path(__file__).resolve().parent
    files = [{'file': p.relative_to(root).as_posix(), 'sha256': digest(p.read_bytes())}
             for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()
             and p.suffix in {'.py', '.json', '.js', '.cjs', '.c', '.css', '.html', '.png', '.gd', '.template', '.fragment', '.mp4'}
             and '__pycache__' not in p.parts]
    return digest(canonical_json(files))


def analysis_catalog():
    path = Path(__file__).resolve().parent / 'contracts/RECONSTRUCTION-CATALOG.json'
    if not path.is_file():
        return {'version': 1, 'scope': 'Analysis reconciliation pending', 'requirements': [],
                'flows': [], 'commands': [], 'grammar': {'complete': False},
                'blockers': [{'id': 'analysis-catalog', 'title': 'Analysis reconciliation',
                              'reason': 'The complete evidence-bound catalog has not been installed.'}]}
    raw = path.read_bytes()
    if len(raw) > 2 * 1024 * 1024:
        raise ValidationError('Analysis catalog exceeds 2MiB')
    doc = json.loads(raw)
    if not isinstance(doc, dict) or type(doc.get('version')) is not int or doc['version'] != 1:
        raise ValidationError('Unsupported analysis catalog')
    canonical_json(doc)
    return doc


def readiness(store, manager=None):
    catalog = analysis_catalog()
    fingerprint = source_fingerprint()
    proof = None
    ident = store.get_head(LATEST_HEAD)
    if ident:
        try:
            candidate = store.get_json(ident)
            if (candidate.get('kind') == 'readiness-verification'
                    and candidate.get('source_fingerprint') == fingerprint):
                proof = candidate
        except ValidationError:
            pass
    proof_checks = proof.get('checks') if proof else None
    proof_flows = proof.get('recipes', {}).get('flows') if proof and isinstance(proof.get('recipes'), dict) else None
    valid = bool(proof and type(proof.get('version')) is int and proof['version'] == 1
                 and proof.get('status') == 'completed' and isinstance(proof_checks, list)
                 and len(proof_checks) == len(REQUIRED_CHECKS)
                 and all(isinstance(c, dict) and c.get('passed') is True for c in proof_checks)
                 and {c.get('name') for c in proof_checks} == REQUIRED_CHECKS
                 and isinstance(proof_flows, list) and len(proof_flows) == 11
                 and proof['recipes'].get('status') == 'completed'
                 and all(isinstance(f, dict) and f.get('status') == 'completed' for f in proof_flows)
                 and {f.get('flow') for f in proof_flows}
                     == {f'F{i:02}' for i in range(1, 12)})
    blockers = []
    seen = set()
    for record in catalog.get('blockers', []):
        key = record.get('requirement') or record.get('id')
        seen.add(key)
        blockers.append({**record, 'title': record.get('title') or record.get('requirement') or record.get('id'),
                         'reason': record.get('reason') or record.get('gap') or record.get('next_action')})
    if not catalog.get('requirements'):
        blockers.append({'id': 'analysis-not-reconciled', 'title': 'Reconcile the full analysis',
                         'reason': 'Requirement evidence must be installed before a comparison can be authorized.'})
    # Do not permit a summary flag to erase unresolved individual requirements.
    resolved = {'implemented_verified', 'source_answered', 'closed_verified'}
    for requirement in catalog.get('requirements', []):
        if (requirement['id'] not in seen
                and (requirement.get('status') not in resolved
                     or requirement.get('whole_question_closed') is not True)):
            blockers.append({'id': requirement['id'], 'title': requirement.get('title', requirement['id']),
                             'reason': requirement.get('gap') or 'Required evidence or behavior remains unresolved.'})
    blockers.extend(_catalog_blockers(catalog))
    checks = [{'id': 'analysis-inventory', 'label': 'Evidence and workflow inventory',
               'status': 'passed' if catalog.get('requirements') else 'pending',
               'detail': f"{len(catalog.get('requirements', []))} requirements; {len(catalog.get('commands', []))} retained commands"},
              {'id': 'setup-proof', 'label': 'Setup diagnostics on this source version',
               'status': 'passed' if valid else 'pending',
               'detail': 'Environment, F01–F11, editing and native exchange; supplied diagnostic inputs only'},
              {'id': 'comparison-prerequisites', 'label': 'Art and model comparison prerequisites',
               'status': 'blocked' if blockers else 'passed',
               'detail': f'{len(blockers)} unresolved prerequisite records'}]
    jobs = manager.list('queued', limit=1000) + manager.list('running', limit=1000) if manager else []
    active = next((j for j in jobs if j['handler'] == HANDLER and j['status'] in {'queued', 'running'}), None)
    comparison = valid and not blockers
    return {'status': 'ready' if comparison else 'blocked', 'setup_ready': valid,
            'comparison_ready': comparison, 'source_fingerprint': fingerprint,
            'checks': checks, 'blockers': blockers,
            'verification': ({'job_id': active['id'], 'status': active['status']} if active else
                             {'artifact': ident, 'status': proof.get('status')} if proof else None),
            'next_actions': ['Resolve analysis prerequisites', 'Run setup verification',
                             'Review complete character inputs and comparison specification'],
            'provider_calls': 0, 'artistic_acceptance': 'unreviewed'}


def _construction_check(store, out):
    from .construction import save_project, load_project, create_history, edit_history, move_history, load_history
    from .construction_exchange import export_ase, import_ase, validate_import_provenance
    from .construction_services import invoke_construction
    from .export import export_sequence, import_editable
    fixture = Path(__file__).resolve().parent / 'contracts/SETUP-CONSTRUCTION.json'
    raw = json.loads(fixture.read_text())
    project = save_project(store, raw)
    history = create_history(store, project['project'])
    transaction = {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': project['project_hash'],
                   'reason': 'Setup verification pixel correction',
                   'operations': [{'op': 'paint', 'cel_id': 'marker-a', 'points': [[1, 1, 3]]}]}
    edited = edit_history(store, history['history'], transaction)
    undone = move_history(store, edited['history'], 'undo')
    redone = move_history(store, undone['history'], 'redo')
    checks = [{'name': 'exact undo and redo', 'passed': undone['project'] == project['project']
               and redone['project'] == edited['project']}]
    native = export_ase(store, edited['project'], out / 'native', animation='diagnostic')
    editor = shutil.which('libresprite')
    if not editor:
        raise ValidationError('LibreSprite is required for native exchange setup verification')
    command = [editor, '--batch', native['ase_path'], '--save-as', str(out / 'resaved.aseprite')]
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    (out / 'EDITOR.json').write_bytes(canonical_json({'command': command, 'exit': result.returncode,
        'stdout': result.stdout[:16000], 'stderr': result.stderr[:16000]}))
    if result.returncode or not (out / 'resaved.aseprite').is_file():
        raise ValidationError('Native editor did not create the expected setup output')
    imported = import_ase(store, out / 'resaved.aseprite', native['sidecar_path'])
    checks.append({'name': 'native editable project identity', 'passed': imported['project'] == edited['project']
                   and load_project(store, imported['project']) == load_project(store, edited['project'])})
    rendered = invoke_construction(store, 'render', {'project': imported['project'], 'history': redone['history'],
        'animation_id': 'diagnostic', 'import_provenance': imported['import_provenance']})
    export_sequence(store, rendered['sequence'], out / 'portable', ['editable', 'apng', 'godot', 'review'])
    fresh = Store(out / 'fresh-store')
    sequence = import_editable(fresh, out / 'portable/editable')
    checks.extend([{'name': 'fresh Store editable sequence', 'passed': sequence == rendered['sequence']},
        {'name': 'fresh Store exact history', 'passed': load_history(fresh, redone['history'])['project'] == edited['project']},
        {'name': 'fresh Store native dependencies', 'passed': validate_import_provenance(fresh,
            imported['import_provenance'], project_id=imported['project'])['imported_project'] == edited['project']}])
    return checks


def register_verification(manager, *, base_dir, runtime_fingerprint=None):
    from .jobs import JobResult
    expected_source = runtime_fingerprint or source_fingerprint()
    def handler(request, context):
        if request:
            raise ValidationError('Setup verification takes no request parameters')
        from .replication import doctor, replay, verify_run
        before = source_fingerprint()
        if before != expected_source:
            raise ValidationError('Restart the local controller after source changes before verifying setup')
        output = Path(base_dir).resolve() / 'setup-runs' / uuid.uuid4().hex
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir()
        checks = []
        context.progress(0.02, {'stage': 'environment'})
        environment = doctor()
        checks.append({'name': 'all replay dependencies available', 'passed': environment['all_replay_dependencies_ready']})
        context.progress(0.10, {'stage': 'F01–F11 supplied diagnostics'})
        recipes = replay(output / 'recipes')
        checks.append({'name': 'all eleven local recipe subsets', 'passed': recipes['status'] == 'completed'
                       and len(recipes['flows']) == 11 and all(f['status'] == 'completed' for f in recipes['flows'])})
        integrity = verify_run(output / 'recipes')
        checks.append({'name': 'recipe artifact integrity', 'passed': integrity['status'] == 'completed'})
        context.progress(0.75, {'stage': 'native editing and portable history'})
        try:
            checks.extend(_construction_check(context.store, output))
        except Exception as exc:
            checks.append({'name': 'native editing and portable history', 'passed': False,
                           'error': str(exc)[:1000], 'exception_type': type(exc).__name__})
        context.check_cancel()
        stable = before == source_fingerprint()
        checks.append({'name': 'source unchanged during verification', 'passed': stable})
        success = all(c['passed'] is True for c in checks)
        report = {'kind': 'readiness-verification', 'version': 1, 'status': 'completed' if success else 'failed',
                  'source_fingerprint': before, 'created_utc': datetime.now(timezone.utc).isoformat(),
                  'output': str(output), 'environment': environment, 'recipes': recipes, 'checks': checks,
                  'scope': 'Setup diagnostics only; not full vendor equivalence or an art/model comparison',
                  'provider_calls': 0, 'artistic_acceptance': 'unreviewed'}
        ident = context.store.put_json(report)
        (output / 'REPORT.json').write_bytes(canonical_json(report))
        context.progress(1, {'stage': report['status']})
        return JobResult(ident, 'technically_verified' if success else 'technical_failure',
                         {'verification': report['status'], 'provider_calls': 0})
    manager.register(HANDLER, handler)


def submit_verification(store, manager):
    active = next((j for j in manager.list('queued', limit=1000) + manager.list('running', limit=1000) if j['handler'] == HANDLER
                   and j['status'] in {'queued', 'running'}), None)
    if active:
        return {'job_id': active['id']}
    ident = manager.submit(HANDLER, {}, head=LATEST_HEAD, expected=store.get_head(LATEST_HEAD))
    return {'job_id': ident}
