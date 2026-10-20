"""Independent fail-closed checks for the source/comparison readiness boundary."""
import copy
import json
from pathlib import Path

import pytest

from sprite_workbench.core import Store
from sprite_workbench import readiness as gates


@pytest.fixture
def green_setup(tmp_path, monkeypatch):
    store = Store(tmp_path / 'store')
    monkeypatch.setattr(gates, 'source_fingerprint', lambda: 'a' * 64)
    proof = {'kind': 'readiness-verification', 'version': 1,
             'source_fingerprint': 'a' * 64, 'status': 'completed',
             'checks': [{'name': n, 'passed': True} for n in gates.REQUIRED_CHECKS],
             'recipes': {'status': 'completed', 'flows': [
                 {'flow': f'F{i:02}', 'status': 'completed'} for i in range(1, 12)]}}
    store.set_head(gates.LATEST_HEAD, store.put_json(proof), expected=None)
    return store, proof


def _catalog(monkeypatch, value):
    monkeypatch.setattr(gates, 'analysis_catalog', lambda: copy.deepcopy(value))


def _claimed_closed_catalog():
    """Start from the real inventory but explicitly assert row completion.

    This is a negative fixture: it is not an updated analysis result. Independent
    required grammar and command/flow gates must survive summary alterations.
    """
    doc = copy.deepcopy(gates.analysis_catalog())
    doc['blockers'] = []
    for r in doc['requirements']:
        r['status'] = 'closed_verified'
        r['whole_question_closed'] = True
    return doc


def _synthetically_closed_independent_rows():
    """Negative-test fixture only: explicitly alter every independent row."""
    doc = _claimed_closed_catalog()
    doc['grammar']['complete'] = True
    for key in ('commands', 'flows', 'transport_flows'):
        for row in doc[key]:
            row['status'] = 'closed_verified'
    return doc


def test_actual_complete_inventory_remains_held_even_with_green_setup(green_setup):
    store, _ = green_setup
    state = gates.readiness(store)
    assert state['setup_ready'] is True
    assert state['comparison_ready'] is False
    assert len(state['blockers']) >= 63


def test_nonempty_invented_requirement_cannot_replace_original_ledger(green_setup, monkeypatch):
    store, _ = green_setup
    _catalog(monkeypatch, {'version': 1, 'scope': {'analysis_accounted': True, 'comparison_ready': True},
        'requirements': [{'id': 'invented', 'status': 'source_answered', 'required_for': ['comparison']}],
        'blockers': [], 'flows': [], 'commands': [], 'grammar': {'complete': False}})
    state = gates.readiness(store)
    assert state['comparison_ready'] is False
    assert state['blockers']


def test_losing_one_original_question_cannot_open_gate(green_setup, monkeypatch):
    store, _ = green_setup
    doc = _claimed_closed_catalog()
    removed = doc['requirements'].pop()
    doc['counts']['original_requirements'] = 62  # cannot redefine the expected ledger
    _catalog(monkeypatch, doc)
    state = gates.readiness(store)
    assert state['comparison_ready'] is False
    assert state['blockers']
    assert removed['id'] not in {r['id'] for r in doc['requirements']}


def test_incomplete_nested_grammar_is_an_independent_prerequisite(green_setup, monkeypatch):
    store, _ = green_setup
    doc = _claimed_closed_catalog()
    doc['grammar']['complete'] = False
    doc['scope']['comparison_ready'] = True
    _catalog(monkeypatch, doc)
    state = gates.readiness(store)
    assert state['comparison_ready'] is False
    assert state['blockers']


def test_unimplemented_command_rows_cannot_be_hidden_by_clearing_blocker_summary(green_setup, monkeypatch):
    store, _ = green_setup
    doc = _claimed_closed_catalog()
    assert any(c['status'] == 'local_pending' for c in doc['commands'])
    _catalog(monkeypatch, doc)
    state = gates.readiness(store)
    assert state['comparison_ready'] is False


def test_repeated_recipe_id_does_not_count_as_eleven_unique_results(green_setup):
    store, proof = green_setup
    proof['recipes']['flows'].append({'flow': 'F01', 'status': 'completed'})
    store.set_head(gates.LATEST_HEAD, store.put_json(proof), expected=store.get_head(gates.LATEST_HEAD))
    assert gates.readiness(store)['setup_ready'] is False


def test_failed_recipe_cannot_coexist_with_green_setup(green_setup):
    store, proof = green_setup
    proof['recipes']['flows'][3]['status'] = 'failed'
    store.set_head(gates.LATEST_HEAD, store.put_json(proof), expected=store.get_head(gates.LATEST_HEAD))
    assert gates.readiness(store)['setup_ready'] is False


def test_missing_recipe_status_does_not_count_as_success(green_setup):
    store, proof = green_setup
    del proof['recipes']['flows'][3]['status']
    store.set_head(gates.LATEST_HEAD, store.put_json(proof), expected=store.get_head(gates.LATEST_HEAD))
    assert gates.readiness(store)['setup_ready'] is False


def test_requirement_id_substitution_is_not_closed_by_count_alone(green_setup, monkeypatch):
    store, _ = green_setup
    doc = _claimed_closed_catalog()
    assert len(doc['requirements']) == 63
    doc['requirements'][0]['id'] = 'invented-replacement'
    _catalog(monkeypatch, doc)
    assert gates.readiness(store)['comparison_ready'] is False


def test_catalog_retains_current_addition_without_claiming_a_local_handler():
    catalog = gates.analysis_catalog()
    added = next(i for i in catalog['interfaces'] if i['id'] == 'current-public:POST:/normal-map')
    assert added['status'] == 'unsupported_remote_handler' and added['local_route'] is None
    assert catalog['counts']['current_public_interfaces'] == 112
    assert catalog['counts']['historical_public_interfaces'] == 111
    assert catalog['counts']['historical_mcp_interfaces'] == 101


def test_mutable_required_for_cannot_remove_an_original_prerequisite(green_setup, monkeypatch):
    store, _ = green_setup
    doc = _synthetically_closed_independent_rows()
    doc['requirements'][0].update(status='runtime_pending', whole_question_closed=False, required_for=[])
    _catalog(monkeypatch, doc)
    assert gates.readiness(store)['comparison_ready'] is False


def test_status_label_cannot_close_an_explicitly_unclosed_original_question(green_setup, monkeypatch):
    store, _ = green_setup
    doc = _synthetically_closed_independent_rows()
    doc['requirements'][0].update(status='source_answered', whole_question_closed=False)
    _catalog(monkeypatch, doc)
    assert gates.readiness(store)['comparison_ready'] is False


def test_baseline_and_catalog_cannot_jointly_redefine_the_original_ids(green_setup, monkeypatch, tmp_path):
    store, _ = green_setup
    doc = _synthetically_closed_independent_rows()
    baseline_file = Path(gates.__file__).resolve().parent / 'contracts/ANALYSIS-BASELINE.json'
    baseline = json.loads(baseline_file.read_text())
    old_id = doc['requirements'][0]['id']
    doc['requirements'][0]['id'] = 'substituted-in-catalog-and-baseline'
    baseline['requirements'] = ['substituted-in-catalog-and-baseline' if r == old_id else r for r in baseline['requirements']]
    fake_code = tmp_path / 'substituted-source' / 'readiness.py'
    fake_baseline = fake_code.parent / 'contracts/ANALYSIS-BASELINE.json'
    fake_baseline.parent.mkdir(parents=True)
    fake_baseline.write_text(json.dumps(baseline))
    _catalog(monkeypatch, doc)
    monkeypatch.setattr(gates, 'Path', lambda *_: fake_code)
    assert gates.readiness(store)['comparison_ready'] is False
