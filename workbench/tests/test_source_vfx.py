"""Mechanical source calls and pinned pixels; no artistic acceptance claims."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from sprite_workbench.capabilities import CapabilityRegistry
from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.source_vfx import bind_source_vfx, run_source_vfx, source_provenance

CASES = json.loads((Path(__file__).parent / 'fixtures/effects/reference-cases.json').read_text())['cases']


def test_describe_calls_source_exports_and_retains_provenance():
    out = run_source_vfx('describe')
    assert len(out['families']) == 17
    assert set(out['families']) == {c['family'] for c in CASES}
    assert out['families']['arc']['radius']['required'] is True
    assert out['families']['particles']['count']['bounds'] == [0, 256]
    assert out['ramps']['fire'][0] == '#3d0a0a'
    assert out['executed_modules'] == [47381, 91722, 22178, 39503, 78501]
    assert out['presets'] == []  # No invented example recipes.
    assert all(m['original_utf16'] and m['original_source_sha256'] for m in out['provenance']['modules'])


def test_original_normalizer_defaults_and_rejections():
    recipe = {'canvas': {'w': 16, 'h': 16}, 'ramps': {'main': 'fire'},
              'layers': [{'id': 'x', 'type': 'glow', 'radius': 3}]}
    before = copy.deepcopy(recipe)
    out = run_source_vfx('validate', recipe)
    assert recipe == before
    assert out['recipe']['frames'] == 8 and out['recipe']['fps'] == 12
    assert out['recipe']['origin'] == [8, 8]
    # Preserve this original boundary: normalized output is a readonly preview,
    # not a raw input document. The renderer must receive the original recipe.
    assert out['recipe']['layers'][0]['rng'] is None
    with pytest.raises(ValidationError, match='rng'):
        run_source_vfx('validate', out['recipe'])
    for change, match in [({'magic': 1}, 'unknown top-level'),
                           ({'layers': [{'id': 'x', 'type': 'invented'}]}, 'type'),
                           ({'canvas': {'w': 15, 'h': 16}}, 'canvas')]:
        with pytest.raises(ValidationError, match=match):
            run_source_vfx('validate', {**recipe, **change})


@pytest.mark.parametrize('case', CASES, ids=lambda c: c['family'])
def test_registered_render_preserves_source_pinned_outputs(tmp_path, case):
    store = Store(tmp_path)
    registry = CapabilityRegistry()
    bind_source_vfx(registry, store)
    request = {'recipe': case['recipe']}
    if case['subject'] is not None:
        request['subject'] = store.put_raster(np.array(case['subject'], np.uint8))
    result = registry.invoke('local.pixellab.vfx.render', request)
    for stream, ident in result['streams'].items():
        _, frames = load_sequence(store, ident)
        assert [hashlib.sha256(a.tobytes()).hexdigest() for a in frames] == case['expected'][stream]
    assert 55110 in result['provenance']['executed_modules']
    assert registry.describe('local.pixellab.vfx.render')['local_classification'] == 'deterministic-source'


def test_manifest_and_factory_integrity_are_enforced(tmp_path, monkeypatch):
    import sprite_workbench.source_vfx as source
    root = tmp_path / 'vendor/vfx'
    root.mkdir(parents=True)
    actual = Path(source.__file__).parent / 'vendor/vfx'
    (root / 'manifest.json').write_bytes((actual / 'manifest.json').read_bytes())
    manifest = json.loads((root / 'manifest.json').read_text())
    for module in manifest['modules']:
        (root / module['file']).write_bytes((actual / module['file']).read_bytes())
    (root / manifest['modules'][0]['file']).write_bytes(b'changed')
    monkeypatch.setattr(source, '__file__', str(tmp_path / 'source_vfx.py'))
    with pytest.raises(ValidationError, match='integrity'):
        source_provenance()
