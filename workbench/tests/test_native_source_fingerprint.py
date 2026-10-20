"""Compiled native behavior must invalidate an earlier source-bound proof."""
from sprite_workbench import readiness as gates
from sprite_workbench.core import Store


def test_native_helper_change_invalidates_cached_verification(tmp_path, monkeypatch):
    package = tmp_path / 'package'
    helper = package / 'native/font_unhinted.c'
    helper.parent.mkdir(parents=True)
    helper.write_text('int main(void) { return 0; }\n')
    monkeypatch.setattr(gates, '__file__', str(package / 'readiness.py'))
    monkeypatch.setattr(gates, 'analysis_catalog', lambda: {'requirements': [], 'blockers': []})
    fingerprint = gates.source_fingerprint()
    store = Store(tmp_path / 'store')
    proof = {'kind': 'readiness-verification', 'version': 1,
             'source_fingerprint': fingerprint, 'status': 'completed',
             'checks': [{'name': name, 'passed': True} for name in gates.REQUIRED_CHECKS],
             'recipes': {'status': 'completed', 'flows': [
                 {'flow': f'F{index:02}', 'status': 'completed'} for index in range(1, 12)]}}
    store.set_head(gates.LATEST_HEAD, store.put_json(proof), expected=None)
    assert gates.readiness(store)['setup_ready'] is True
    helper.write_text('int main(void) { return 1; }\n')
    assert gates.source_fingerprint() != fingerprint
    assert gates.readiness(store)['setup_ready'] is False
