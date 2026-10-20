"""Portable observed instances and a real native atlas, never constructor claims."""
from collections import Counter
import copy
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.capabilities import CapabilityRegistry
from sprite_workbench.core import Store, ValidationError, canonical_json, digest, load_sequence
from sprite_workbench.observed_vfx import observed_catalog, observed_default, OBSERVED_SHA256
from sprite_workbench.source_vfx import bind_source_vfx
from sprite_workbench.source_workflow import source_catalog

FIXTURE = Path(__file__).parent / 'fixtures/observed-vfx'


def registry(store):
    result = CapabilityRegistry()
    bind_source_vfx(result, store)
    return result


def test_catalog_identity_preserves_presets_and_all_observed_controls(tmp_path):
    catalog = source_catalog()
    assert len(catalog['presets']) == 2
    assert catalog['presets_sha256'] == 'f0c0e9d1a84fb1feb244b70124218381729850ed27d60448ab97aad892bbc40f'
    observed = registry(Store(tmp_path)).invoke('local.pixellab.vfx.observed_catalog', {})
    assert observed['sha256'] == OBSERVED_SHA256
    assert len(observed['defaults']) == 105
    assert sum(len(e['recipe']['controls']) for e in observed['defaults']) == 350
    types = Counter(c['type'] for e in observed['defaults'] for c in e['recipe']['controls'])
    assert types == {'slider': 207, 'ramp': 113, 'toggle': 29, 'select': 1}
    assert catalog['observed_defaults'] == observed['defaults']
    assert len(observed['subject_examples']) == 3
    assert catalog['observed_subject_examples'] == observed['subject_examples']
    assert {e['provenance']['part'] for e in observed['defaults'] if e['provenance']['needs_subject']} == {'burning_edge', 'hurt_flash', 'sprite_dust'}
    # Portable contract contains no provider storage links, account fields or credentials.
    text = json.dumps(observed)
    for forbidden in ('https://', 'Bearer ', 'preview_url', 'animation_url', 'subject_png_base64', '/home/astra/'):
        assert forbidden not in text
    for entry in observed['defaults']:
        proof = entry['provenance']
        assert digest(canonical_json(entry['recipe'])) == proof['recipe_sha256']
        assert proof['comparison']['native_frame_RGBA_sha256'] == proof['comparison']['source_frame_RGBA_sha256']


def test_real_store_render_matches_retained_native_atlas_and_keeps_observation(tmp_path):
    store = Store(tmp_path)
    services = registry(store)
    entry = services.invoke('local.pixellab.vfx.observed_default', {'id': 'observed.alert_pop'})
    before = copy.deepcopy(entry)
    result = services.invoke('local.pixellab.vfx.render_observed', {'id': entry['id']})
    sequence, frames = load_sequence(store, result['sequence'])
    with Image.open(FIXTURE / 'alert_pop.png') as image:
        atlas = np.array(image.convert('RGBA'))
    manifest = json.loads((FIXTURE / 'alert_pop.json').read_text())
    assert digest((FIXTURE / 'alert_pop.png').read_bytes()) == entry['provenance']['native_atlas_png_sha256']
    for actual, native in zip(frames, manifest['frames'], strict=True):
        r = native['frame']
        assert np.array_equal(actual, atlas[r['y']:r['y']+r['h'], r['x']:r['x']+r['w']])
    receipt = store.get_json(result['observed_default'])
    assert receipt['library_sha256'] == OBSERVED_SHA256 and receipt['default_values'] is True
    assert sequence['metadata']['observed_vfx_default'] == result['observed_default']
    assert store.get_json(result['control_receipt'])['declared_recipe'] == entry['recipe']
    assert before == entry
    from sprite_workbench.export import export_sequence, import_editable
    exported = export_sequence(store, result['sequence'], tmp_path / 'export', formats=('editable',))
    fresh = Store(tmp_path / 'fresh')
    import_editable(fresh, tmp_path / 'export/editable')
    assert fresh.get_json(result['observed_default']) == receipt
    toggle = next(c for c in entry['recipe']['controls'] if c['type'] == 'toggle')
    changed = services.invoke('local.pixellab.vfx.render_observed', {'id': entry['id'], 'values': {toggle['id']: False}})
    assert store.get_json(changed['observed_default'])['default_values'] is False
    assert changed['sequence'] != result['sequence']


def test_bad_observed_calls_reject_without_artifacts(tmp_path):
    store = Store(tmp_path); services = registry(store)
    before = list((store.path / 'blobs').iterdir())
    for request in ({'id': 'missing'}, {'id': 'observed.alert_pop', 'size': 2},
                    {'id': 'observed.alert_pop', 'recipe': {}},
                    {'id': 'observed.alert_pop', 'values': {'unknown': 1}}):
        with pytest.raises(ValidationError):
            services.invoke('local.pixellab.vfx.render_observed', request)
    assert list((store.path / 'blobs').iterdir()) == before


def test_frozen_library_corruption_and_recipe_hash_are_enforced(tmp_path, monkeypatch):
    import sprite_workbench.observed_vfx as observed
    raw = (Path(observed.__file__).parent / 'contracts/OBSERVED-VFX-DEFAULTS.json').read_bytes()
    contracts = tmp_path / 'contracts'; contracts.mkdir()
    path = contracts / 'OBSERVED-VFX-DEFAULTS.json'; path.write_bytes(raw + b' ')
    monkeypatch.setattr(observed, '__file__', str(tmp_path / 'observed_vfx.py'))
    with pytest.raises(ValidationError, match='pinned authority'):
        observed.observed_catalog()
    value = json.loads(raw); value['defaults'][0]['recipe']['seed'] += 1
    altered = canonical_json(value); path.write_bytes(altered)
    monkeypatch.setattr(observed, 'OBSERVED_SHA256', digest(altered))
    with pytest.raises(ValidationError, match='recipe integrity'):
        observed.observed_catalog()


def test_observed_library_cli_channel_and_http_job(tmp_path, capsys):
    from sprite_workbench.cli import main
    from sprite_workbench.channel import serve
    from sprite_workbench.web_server import ControlServer
    import io
    import threading
    from urllib.request import Request, urlopen

    request_file = tmp_path / 'request.json'
    request_file.write_text('{"id":"observed.alert_pop"}')
    main(['--workspace', str(tmp_path / 'cli-store'), 'pixellab-vfx', 'observed_default', str(request_file)])
    assert json.loads(capsys.readouterr().out)['id'] == 'observed.alert_pop'
    source = io.StringIO(json.dumps({'id': 'pick', 'method': 'local.pixellab.vfx.observed_default',
                                   'params': {'id': 'observed.alert_pop'}}) + '\n')
    sink = io.StringIO()
    serve(Store(tmp_path / 'channel-store'), base_dir=tmp_path, result_ref='unused',
                source=source, sink=sink, workers=1)
    channel = [json.loads(line) for line in sink.getvalue().splitlines()]
    assert channel[1]['result']['id'] == 'observed.alert_pop'
    web = ControlServer(Store(tmp_path / 'http-store'), base_dir=tmp_path, port=0, workers=1)
    thread = threading.Thread(target=web.serve_forever, daemon=True); thread.start()
    try:
        def invoke(method, params):
            request = Request(web.url + '/api/invoke', json.dumps({'method': method, 'params': params}).encode(),
                              {'X-Workbench-Token': web.token, 'Content-Type': 'application/json'})
            with urlopen(request, timeout=30) as response:
                value = json.loads(response.read())
                assert value['status'] == 'completed'
                return value['result']
        ident = invoke('local.jobs.submit', {'handler': 'local.pixellab.vfx.render_observed',
                                           'request': {'id': 'observed.alert_pop'}})
        result = invoke('local.jobs.wait', {'job_id': ident, 'timeout': 20})
        assert result['status'] == 'completed'
        assert result['outputs'][0]['metadata']['source_result']['observed_id'] == 'observed.alert_pop'
    finally:
        web.shutdown(); web.server_close(); thread.join(timeout=5)


def test_every_observed_recipe_is_accepted_by_original_controls():
    from sprite_workbench.source_controls import apply_controls
    catalog = observed_catalog()
    for entry in catalog['defaults'] + catalog['subject_examples']:
        result = apply_controls(entry['recipe'])
        assert result['declared_recipe'] == entry['recipe']
        assert [c['id'] for c in result['controls']] == [c['id'] for c in entry['recipe']['controls']]
        assert result['caller_input_unchanged'] is True


def test_source_ui_keeps_select_values_and_toggle_booleans():
    """Host DOM boundary must preserve source JSON values, not '[object Object]'."""
    import subprocess
    script = r'''
const fs = require('fs'), vm = require('vm');
class Element {
  constructor() { this.children = []; this.events = {}; this.value = ''; }
  addEventListener(name, handler) { this.events[name] = handler; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute() {}
  get dataset() { return this._dataset ||= {}; }
}
const elements = new Map();
global.window = {}; global.document = {
  getElementById(id) { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); },
  createElement() { return new Element(); }
};
vm.runInThisContext(fs.readFileSync('sprite_workbench/web/source-vfx.js', 'utf8'));
const controls = [
 {id:'select', label:'Selection', type:'select', value: {mode:'first'}, options:[
  {label:'First', value:{mode:'first'}}, {label:'Second', value:[1,2,3]}]},
 {id:'toggle', label:'Enabled', type:'toggle', value:true},
 {id:'ramp', label:'Ramp', type:'ramp', value:'fire', options:['fire','frost']},
 {id:'custom', label:'Custom ramp', type:'ramp', value:['#ffffff','#ffffff'], options:['fire','frost']}
];
const ui = new window.PixelLabSourceUI({action:f=>f(), invoke:async()=>({controls})});
ui.$('recipe').value = '{}';
(async()=>{
 await ui.readControls();
 const rows = ui.$('controls').children;
 const select = rows[0].children[1];
 if (select.children[1].textContent !== 'Second') throw Error('Missing source label');
 select.value = select.children[1].value; select.events.change();
 if (JSON.stringify(ui.values.select) !== '[1,2,3]') throw Error('Lost typed select value');
 const toggle = rows[1].children[1]; toggle.checked = false; toggle.events.change();
 if (ui.values.toggle !== false) throw Error('Lost boolean toggle value');
 const ramp = rows[2].children[1]; ramp.value = 'frost'; ramp.events.change();
 if (ui.values.ramp !== 'frost') throw Error('Lost ramp value');
 const custom = rows[3].children[1];
 if (!custom.value) throw Error('Current custom ramp displayed as empty');
 custom.events.change();
 if (JSON.stringify(ui.values.custom) !== '["#ffffff","#ffffff"]') throw Error('Lost current custom ramp');
})().catch(error=>{console.error(error); process.exitCode=1;});
'''
    result = subprocess.run(['node', '-e', script], cwd=Path(__file__).parents[1], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr


def test_subject_dependent_default_preserves_absent_subject_declaration(tmp_path):
    store = Store(tmp_path)
    services = registry(store)
    subject = store.put_raster(np.full((32, 32, 4), 255, dtype=np.uint8))
    result = services.invoke('local.pixellab.vfx.render_observed',
                             {'id': 'observed.hurt_flash', 'subject': subject})
    receipt = store.get_json(result['observed_default'])
    assert receipt['supplied_subject'] == subject
    assert receipt['default_values'] is True and receipt['retained_default_inputs'] is False
    assert store.get_json(result['recipe'])['subject'] == subject
    _, frames = load_sequence(store, result['sequence'])
    # The unchanged renderer requires recipe.subject as well as the raster.
    # This frozen default has no subject declaration; never invent one silently.
    assert all(not frame[:, :, 3].any() for frame in frames)


def test_three_authentic_subject_examples_reproduce_native_frame_hashes(tmp_path):
    store = Store(tmp_path)
    services = registry(store)
    for entry in observed_catalog()['subject_examples']:
        result = services.invoke('local.pixellab.vfx.render_observed', {'id': entry['id']})
        _, frames = load_sequence(store, result['sequence'])
        actual = [digest(frame.tobytes()) for frame in frames]
        assert actual == entry['provenance']['comparison']['native_frame_RGBA_sha256']
        assert any(frame[:, :, 3].any() for frame in frames)
        receipt = store.get_json(result['observed_default'])
        assert receipt['packaged_subject'] is True
        assert receipt['supplied_subject'] is not None
        assert store.get_json(result['control_receipt'])['declared_recipe'] == entry['recipe']
