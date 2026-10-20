#!/usr/bin/env python3
"""Isolated installed-wheel source-workflow proof, independent of checkout imports."""
import argparse
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import threading
from urllib.request import urlopen

import numpy as np
import sprite_workbench
from sprite_workbench.core import Store, canonical_json, load_sequence
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.readiness import source_fingerprint
from sprite_workbench.source_controls import apply_controls
from sprite_workbench.source_vfx import source_provenance
from sprite_workbench.source_workflow import source_catalog, invoke_source_vfx
from sprite_workbench.web_server import ControlServer


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def frame_hashes(store, sequence):
    _, frames = load_sequence(store, sequence)
    return [sha(frame.tobytes()) for frame in frames]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected', type=Path, required=True)
    parser.add_argument('--oracle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    expected = json.loads(args.expected.read_text())
    package = Path(sprite_workbench.__file__).resolve().parent
    assert sys.flags.isolated == 1
    assert not Path.cwd().resolve().is_relative_to(Path(expected['checkout']))
    assert not package.is_relative_to(Path(expected['checkout']))
    assert package.is_relative_to(Path(sys.prefix).resolve())
    assert importlib.metadata.version('sprite-workbench') == expected['version']
    assert source_fingerprint() == expected['source_fingerprint']
    installed = []
    for row in expected['runtime_files']:
        raw = (package/row['file']).read_bytes()
        assert sha(raw) == row['sha256']
        installed.append({**row, 'bytes': len(raw)})
    write(args.output/'INSTALLED-FILES.json', installed)
    catalog = source_catalog()
    describe = invoke_source_vfx(Store(args.output/'describe-store'), 'describe', {})
    assert len(describe['families']) == 17
    assert describe['provenance']['classification'] == 'deterministic-source'
    assert catalog['presets_sha256'] == sha((package/'contracts/SOURCE-VFX-PRESETS.json').read_bytes())
    assert {p['id'] for p in catalog['presets']} == {'slash_arc', 'energy_orb'}
    assert all(p['provenance']['request_contains_recipe'] is False for p in catalog['presets'])
    assert all(sha(canonical_json(p['recipe'])) == p['provenance']['recipe_sha256'] for p in catalog['presets'])
    write(args.output/'SOURCE-CATALOG.json', catalog)
    write(args.output/'SOURCE-DESCRIBE.json', describe)
    store = Store(args.output/'store')
    preset_proofs = []
    for preset in catalog['presets']:
        recipe = deepcopy(preset['recipe'])
        defaults = apply_controls(recipe)
        control = next(c for c in defaults['controls'] if c['type'] == 'slider' and c['value'] != c['min'])
        values = {control['id']: control['min']}
        variation = apply_controls(recipe, values)
        assert variation['hashes']['values_sha256'] != defaults['hashes']['values_sha256']
        result = invoke_source_vfx(store, 'render', {'recipe': recipe, 'values': values})
        receipt = store.get_json(result['control_receipt'])
        assert receipt['hashes'] == variation['hashes']
        assert result['provenance']['classification'] == 'deterministic-source'
        doc = store.get_json(result['sequence'])
        assert doc['metadata']['pixellab_controls'] == result['control_receipt']
        export_path = args.output/('portable-' + preset['id'])
        export_sequence(store, result['sequence'], export_path, formats=['png', 'manifest', 'editable'])
        index = json.loads((export_path/'editable/index.json').read_text())
        assert result['control_receipt'] in index['artifact_ids']
        fresh = Store(args.output/('fresh-' + preset['id']))
        restored = import_editable(fresh, export_path/'editable')
        assert restored == result['sequence']
        assert fresh.get_json(result['control_receipt']) == receipt
        assert frame_hashes(fresh, restored) == frame_hashes(store, result['sequence'])
        preset_proofs.append({'preset': preset['id'], 'preset_recipe_sha256': preset['provenance']['recipe_sha256'],
                              'changed_values': values, 'sequence': result['sequence'],
                              'control_receipt': result['control_receipt'], 'control_hashes': result['control_hashes'],
                              'portable_artifacts': len(index['artifact_ids']),
                              'rgba_sha256': frame_hashes(store, result['sequence']), 'fresh_store_closure': True})
    write(args.output/'PRESET-VARIATIONS.json', preset_proofs)
    raw_oracle = args.oracle.read_bytes()
    assert sha(raw_oracle) == expected['oracle_sha256']
    cases = json.loads(raw_oracle)['cases']
    assert len(cases) == 17
    oracle_rows = []
    for case in cases:
        request = {'recipe': case['recipe']}
        if case['subject'] is not None:
            request['subject'] = store.put_raster(np.array(case['subject'], np.uint8))
        result = invoke_source_vfx(store, 'render', request)
        observed = {stream: frame_hashes(store, sequence) for stream, sequence in result['streams'].items()}
        assert observed == case['expected'], case['family']
        oracle_rows.append({'family': case['family'], 'id': case['id'], 'matches': True,
                            'observed_rgba_sha256': observed, 'executed_modules': result['executed_modules']})
    write(args.output/'SOURCE-ORACLE-MATCHES.json', oracle_rows)
    # Fetch the installed UI bytes and source catalog from its actual HTTP server.
    server = ControlServer(Store(args.output/'http-store'), base_dir=args.output, port=0, workers=1)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    static = []
    try:
        for endpoint, relative in [('/', 'web/index.html'), ('/app.js', 'web/app.js'),
                                   ('/style.css', 'web/style.css'), ('/source-vfx.js', 'web/source-vfx.js')]:
            with urlopen(server.url + endpoint, timeout=30) as response:
                raw = response.read()
                assert response.status == 200 and raw == (package/relative).read_bytes()
                static.append({'endpoint': endpoint, 'file': relative, 'sha256': sha(raw)})
        with urlopen(server.url + '/api/pixellab/source', timeout=30) as response:
            http_catalog = json.load(response)
        assert http_catalog['presets_sha256'] == catalog['presets_sha256']
        assert http_catalog['source']['provenance']['classification'] == 'deterministic-source'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
    write(args.output/'HTTP-SOURCE.json', {'static': static, 'presets_sha256': http_catalog['presets_sha256']})
    result = {'passed': True, 'isolated': sys.flags.isolated, 'package_path': str(package),
              'version': expected['version'], 'source_fingerprint': source_fingerprint(),
              'installed_runtime_files': len(installed), 'baseline_runtime_files_retained': expected['baseline_runtime_files'],
              'unchanged_vendor_files': len(expected['unchanged_vendor_files']),
              'presets_sha256': catalog['presets_sha256'], 'preset_variations': preset_proofs,
              'original_fixture_sha256': sha(raw_oracle), 'original_fixture_cases_matched': len(oracle_rows),
              'source_flags': {'classification': source_provenance()['classification'], 'provider_calls': 0,
                               'current_server_equivalence': False, 'artistic_acceptance': 'unreviewed'},
              'http_source_and_static': True, 'portable_fresh_store_closure': True}
    assert result['source_fingerprint'] == expected['source_fingerprint']
    write(args.output/'RESULT.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
