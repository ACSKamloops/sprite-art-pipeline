"""Adapter differential, using exact full original chunks as the algorithm oracle.

External retained research is optional in an ordinary clean clone. Set
PIXELLAB_RESEARCH_ROOT to run these source checks elsewhere. A missing original
is reported as a skip; an available but changed original must fail.
"""
import base64
import copy
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from sprite_workbench.core import Store, load_sequence
from sprite_workbench.effects import render_effect
from sprite_workbench.core import ValidationError
from sprite_workbench.source_controls import apply_controls, render_controlled_effect
from sprite_workbench.source_vfx import run_source_vfx

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'sprite_workbench/vendor/vfx'
FIXTURES = ROOT / 'tests/fixtures/effects'
RESEARCH = Path(os.environ.get('PIXELLAB_RESEARCH_ROOT',
    str(ROOT.parent / 'pixellab-local-test-20261011')))
MANIFEST = json.loads((VENDOR / 'manifest.json').read_text())
CASES = json.loads((FIXTURES / 'reference-cases.json').read_text())['cases']
SERVER_CASES = json.loads((FIXTURES / 'server-cases.json').read_text())['cases']


@pytest.fixture(scope='module')
def original_root():
    if not (RESEARCH / 'website-art-bundles').is_dir():
        pytest.skip('Retained original bundles absent; set PIXELLAB_RESEARCH_ROOT for source differential')
    return RESEARCH


def sha(data):
    return hashlib.sha256(data).hexdigest()


def test_source_fidelity_vendored_factory_hashes_and_closed_inventory():
    assert len(MANIFEST['modules']) == 46
    assert {p.name for p in VENDOR.glob('*.js')} == {m['file'] for m in MANIFEST['modules']}
    assert len({m['id'] for m in MANIFEST['modules']}) == 46
    for module in MANIFEST['modules']:
        assert sha((VENDOR / module['file']).read_bytes()) == module['sha256']


def test_source_fidelity_all_original_utf16_ranges_are_byte_exact(original_root):
    for module in MANIFEST['modules']:
        raw = (original_root / module['original_source']).read_bytes()
        assert sha(raw) == module['original_source_sha256']
        start, end = module['original_utf16']
        exact = raw.decode('utf8').encode('utf-16-le')[2*start:2*end].decode('utf-16-le').encode('utf8')
        assert exact == (VENDOR / module['file']).read_bytes(), module['id']
    index = json.loads((original_root / 'analysis-root/workbench-gap-closure/CLIENT-MODULE-INDEX.json').read_text())
    manifest_by_id = {module['id']: module for module in MANIFEST['modules']}
    for original in index['modules']:
        module = manifest_by_id[original['module_id']]
        assert module['original_source'] == original['source']
        assert module['original_source_sha256'] == original['source_sha256']
        assert module['original_utf16'] == original['utf16']
        assert module['sha256'] == original['factory_sha256']


def test_source_fidelity_retained_reference_receipts(original_root):
    for case in CASES:
        receipt = case['source_receipt']
        raw = (original_root / receipt['path']).read_bytes()
        assert sha(raw) == receipt['sha256']
        selected = json.loads(raw)
        for component in receipt['json_pointer'].strip('/').split('/'):
            selected = selected[int(component)] if isinstance(selected, list) else selected[component]
        # Retained outcome structure is a receipt, not a fresh quality assessment.
        assert selected['id'] == case['id']
    for case in SERVER_CASES:
        assert sha((FIXTURES / case['sheet']).read_bytes()) == case['target_png_sha256']
        assert sha((FIXTURES / case['manifest']).read_bytes()) == case['target_json_sha256']


@pytest.mark.parametrize('name,request_id,response_sha', [
    ('energy_orb', 110, 'e3a368a4804c1c3c6621787c5e63faf1f43914ae6b123b79a219976dc51091b4'),
    ('slash_arc', 124, '942cdb8798f06a8c8deae24c629eb5639e8263afde0b4d22271dc637f4941897'),
])
def test_source_fidelity_presets_are_returned_vendor_data(original_root, name, request_id, response_sha):
    capture = original_root / 'controlled-tests/prepared-parts/capture'
    raw = (capture / f'responses/{request_id}-metadata-preset-{name}.json').read_bytes()
    assert sha(raw) == response_sha
    response = json.loads(raw)
    assert response['id'] == request_id
    text = response['result']['content'][0]['text']
    returned = json.JSONDecoder().raw_decode(text.split('\n', 1)[1])[0]
    fixture = next(case for case in SERVER_CASES if case['name'] == name)
    assert returned == fixture['recipe']
    preset = (original_root / f'controlled-tests/prepared-parts/presets/{name}.json').read_bytes()
    assert sha(preset) == fixture['source_recipe_sha256']
    assert json.loads(preset) == returned
    # Examine only the selected request, never print or copy the surrounding HAR.
    entries = json.loads((capture / 'documentation-curated.har').read_text())['log']['entries']
    selected = []
    for entry in entries:
        request = json.loads(entry['request'].get('postData', {}).get('text', '{}'))
        if request.get('id') == request_id:
            selected.append(request)
    assert len(selected) == 1
    request = selected[0]
    assert request['params']['name'] == 'vfx_workbench'
    argv = request['params']['arguments']['argv']
    assert argv[1] == 'get_preset'
    assert json.loads(argv[2]) == {'name': name, 'peek': True}


def oracle(original_root, recipe, subject=None, images=None):
    def encode(array):
        if array is None:
            return None
        return {'width': array.shape[1], 'height': array.shape[0],
                'rgba_base64': base64.b64encode(array.tobytes()).decode()}
    request = {'recipe': recipe, 'subject': encode(subject),
               'images': {key: encode(value) for key, value in (images or {}).items()}}
    result = subprocess.run(['node', str(ROOT / 'tests/source_fidelity_oracle.cjs'), str(original_root)],
        input=json.dumps(request), text=True, capture_output=True, timeout=60, check=False)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def original_method(original_root, action, recipe):
    result = subprocess.run(['node', str(ROOT / 'tests/source_fidelity_oracle.cjs'), str(original_root)],
        input=json.dumps({'action': action, 'recipe': recipe}), text=True,
        capture_output=True, timeout=60, check=False)
    return result.returncode, json.loads(result.stdout) if result.returncode == 0 else result.stderr.strip()


def compare(tmp_path, original_root, recipe, subject=None, images=None):
    expected = oracle(original_root, recipe, subject, images)
    store = Store(tmp_path)
    actual = render_effect(store, recipe,
        subject=store.put_raster(subject) if subject is not None else None,
        images={key: store.put_raster(value) for key, value in (images or {}).items()})
    normalized = store.get_json(actual['recipe'])['normalized']
    assert normalized == expected['recipe']
    assert actual['executed_modules'] == expected['executed']
    for name, ident in actual['streams'].items():
        document, frames = load_sequence(store, ident)
        assert [frame.tobytes() for frame in frames] == [base64.b64decode(frame) for frame in expected['streams'][name]]
        assert document['metadata']['subject_box'] == expected['subjectBox']
        assert all(Fraction(*frame['duration']) == 1/Fraction(str(normalized['fps'])) for frame in document['frames'])
    return expected


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['family'])
def test_source_fidelity_original_bundle_all17_families(tmp_path, original_root, case):
    subject = np.array(case['subject'], np.uint8) if case['subject'] is not None else None
    result = compare(tmp_path, original_root, case['recipe'], subject)
    for stream, frames in result['streams'].items():
        assert [sha(base64.b64decode(frame)) for frame in frames] == case['expected'][stream]


@pytest.mark.parametrize('case', SERVER_CASES, ids=lambda case: case['name'])
def test_source_fidelity_original_bundle_retained_server_recipes(tmp_path, original_root, case):
    compare(tmp_path, original_root, case['recipe'])


@pytest.mark.parametrize('mirror', ['none', 'x'])
@pytest.mark.parametrize('loop', [False, True])
def test_source_fidelity_subject_alpha_mirror_motion_and_clock(tmp_path, original_root, mirror, loop):
    # A supplied test raster probes the source threshold; it is not a new art method.
    subject = np.array([[[231, 17, 19, alpha] for alpha in [0, 1, 127, 128, 254, 255]]], np.uint8)
    recipe = {'canvas': {'w': 32, 'h': 32}, 'frames': 4, 'fps': 7, 'seed': 123,
        'ramps': {'main': 'arcane'},
        'loop': loop, 'mirror': mirror, 'layers': [],
        'subject': {'x': 16, 'y': 16, 'align': 'center', 'dx': {'from': 0, 'to': 4}}}
    result = compare(tmp_path, original_root, recipe, subject)
    assert all(set(base64.b64decode(frame)[3::4]) <= {0, 255} for frame in result['streams']['frames'])
    assert all(sum(alpha != 0 for alpha in base64.b64decode(frame)[3::4]) == 3 for frame in result['streams']['frames'])
    assert len(set(result['streams']['frames'])) > 1
    assert all(not any(base64.b64decode(frame)) for name in ['back', 'front'] for frame in result['streams'][name])


def test_source_fidelity_seed_and_front_back_composition(tmp_path, original_root):
    recipe = copy.deepcopy(next(case['recipe'] for case in CASES if case['family'] == 'particles'))
    recipe.pop('subject', None)
    recipe['layers'][0]['source'] = 'area'
    recipe['layers'][0]['radius'] = 12
    recipe['layers'][0]['z'] = 'back'
    layer = copy.deepcopy(recipe['layers'][0]); layer['id'] += '_front'; layer['z'] = 'front'
    recipe['layers'].append(layer)
    first = compare(tmp_path / 'first', original_root, recipe)
    recipe['seed'] += 1
    second = compare(tmp_path / 'second', original_root, recipe)
    assert first['streams'] != second['streams']
    assert any(any(base64.b64decode(frame)) for frame in first['streams']['back'])
    assert any(any(base64.b64decode(frame)) for frame in first['streams']['front'])


@pytest.mark.parametrize('case', SERVER_CASES, ids=lambda case: case['name'])
def test_source_fidelity_original_normalizer_and_preset_controls(original_root, case):
    recipe = copy.deepcopy(case['recipe'])
    before = copy.deepcopy(recipe)
    code, expected = original_method(original_root, 'controls', recipe)
    assert code == 0, expected
    actual = apply_controls(recipe)
    assert recipe == before
    assert actual['normalized_recipe'] == expected['normalized']
    assert actual['recipe'] == expected['applied']
    assert actual['provenance']['executed_modules'] == expected['executed']
    assert run_source_vfx('validate', recipe)['recipe'] == expected['normalized']


def control_diagnostic(mode='mul'):
    recipe = copy.deepcopy(CASES[0]['recipe'])
    recipe['layers'][0]['radius'] = {'from': 3, 'to': 6} if mode != 'set' else 6
    recipe['controls'] = [{'id': 'radius', 'label': 'Radius', 'type': 'slider',
        'min': 1, 'max': 3, 'step': 1, 'value': 2,
        'binds': [{'path': 'layers.ring.radius', 'mode': mode}]}]
    return recipe


@pytest.mark.parametrize('mode', ['set', 'mul', 'add'])
@pytest.mark.parametrize('value', [None, 3])
def test_source_fidelity_controls_once_against_original(tmp_path, original_root, mode, value):
    recipe = control_diagnostic(mode)
    before = copy.deepcopy(recipe)
    supplied = None if value is None else {'radius': value}
    declared = copy.deepcopy(recipe)
    if value is not None:
        declared['controls'][0]['value'] = value
    code, expected = original_method(original_root, 'controls', declared)
    assert code == 0, expected
    actual = apply_controls(recipe, supplied)
    assert recipe == before
    assert actual['renderer_input'] == declared
    assert actual['normalized_recipe'] == expected['normalized']
    assert actual['recipe'] == expected['applied']
    # Render raw declarations; original renderer applies binds itself exactly once.
    expected_pixels = oracle(original_root, declared)
    store = Store(tmp_path)
    rendered = render_controlled_effect(store, recipe, supplied)
    for name, ident in rendered['streams'].items():
        _, frames = load_sequence(store, ident)
        assert [frame.tobytes() for frame in frames] == [base64.b64decode(frame) for frame in expected_pixels['streams'][name]]


@pytest.mark.parametrize('problem', ['range', 'overlap', 'normalized_again'])
def test_source_fidelity_normalizer_error_branches_match_original(original_root, problem):
    recipe = control_diagnostic()
    if problem == 'range':
        recipe['controls'][0]['value'] = 99
    elif problem == 'overlap':
        recipe['controls'].append({**copy.deepcopy(recipe['controls'][0]), 'id': 'other'})
    else:
        code, normalized = original_method(original_root, 'normalize', recipe)
        assert code == 0
        recipe = normalized['normalized']
    before = copy.deepcopy(recipe)
    code, reason = original_method(original_root, 'normalize', recipe)
    assert code != 0
    with pytest.raises(ValidationError) as error:
        run_source_vfx('validate', recipe)
    assert str(error.value) == reason
    assert recipe == before


def test_source_fidelity_unknown_control_is_an_explicit_local_guard(original_root):
    recipe = control_diagnostic()
    before = copy.deepcopy(recipe)
    # Original functions accept a recipe, not our wrapper's values dictionary.
    code, _ = original_method(original_root, 'normalize', recipe)
    assert code == 0
    with pytest.raises(ValidationError, match='Unknown control ID absent'):
        apply_controls(recipe, {'absent': 1})
    assert recipe == before
