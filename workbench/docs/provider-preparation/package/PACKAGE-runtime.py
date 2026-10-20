#!/usr/bin/env python3
"""Installed v0.6 handoff preparation proof; supplied diagnostic pixels only."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
import sprite_workbench
from sprite_workbench.acquisition import import_image
from sprite_workbench.core import Store, load_sequence
from sprite_workbench.export import export_sequence, import_editable, png_bytes
from sprite_workbench.model_handoff import invoke_models
from sprite_workbench.readiness import source_fingerprint
from sprite_workbench.web_server import ControlServer


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    expected = json.loads(args.expected.read_text())
    package = Path(sprite_workbench.__file__).resolve().parent
    assert sys.flags.isolated == 1
    assert not Path.cwd().resolve().is_relative_to(Path(expected['checkout']))
    assert not package.is_relative_to(Path(expected['checkout']))
    assert package.is_relative_to(Path(sys.prefix).resolve())
    assert importlib.metadata.version('sprite-workbench') == expected['version'] == '0.6.0'
    assert source_fingerprint() == expected['source_fingerprint']
    installed = []
    for row in expected['runtime_files']:
        raw = (package/row['file']).read_bytes()
        assert sha(raw) == row['sha256']
        installed.append({**row, 'bytes': len(raw)})
    write(args.output/'INSTALLED-FILES.json', installed)
    store = Store(args.output/'store')
    # Explicit non-art marker: native 5x4 RGBA including hidden RGB/partial alpha.
    marker = np.arange(4 * 5 * 4, dtype=np.uint8).reshape(4, 5, 4)
    marker[..., 3] = 255; marker[0, 0, 3] = 0; marker[1, 1, 3] = 127
    reference = np.flip(marker, axis=1).copy()
    raw = png_bytes(marker)
    supplied = args.output/'SUPPLIED-DIAGNOSTIC.png'; supplied.write_bytes(raw)
    imported = import_image(store, supplied)
    raster = imported['rasters'][0]; reference_id = store.put_raster(reference)
    catalog = invoke_models(store, 'catalog', {})
    assert catalog['provider_calls'] == 0 and catalog['execution_status'] == 'held'
    assert {p['id'] for p in catalog['executors']} == {'codex.imagegen', 'hermes.image_generate'}
    hermes = next(p for p in catalog['executors'] if p['id'] == 'hermes.image_generate')
    assert hermes['image_provider'] is None
    assert hermes['status'] == 'needs-image-provider-selection; runtime untested'
    assert hermes['orchestrator_model'] == 'MiniMax-M3.1-Flash-Preview'
    assert hermes['required_configuration']['image_gen.provider'] == 'openai-codex'
    brief = {'version': 1, 'task': 'edit', 'prompt': '  SUPPLIED DIAGNOSTIC ONLY. Keep this instruction verbatim.\n',
             'inputs': [{'role': 'edit_target', 'raster': raster}, {'role': 'style', 'raster': reference_id}],
             'requirements': {'transparent_background': True, 'desired_size': [256, 256]}, 'hard_controls': {}}
    prepared = invoke_models(store, 'prepare', {'brief': brief, 'executors': ['codex.imagegen', 'hermes.image_generate']})
    assert prepared['execution_status'] == 'held' and prepared['provider_calls'] == 0
    frozen = store.get_json(prepared['brief'])
    assert frozen['brief'] == brief and frozen['prompt_sha256'] == sha(brief['prompt'].encode())
    packets = []; ingested = []; closure = []
    for row in prepared['tasks']:
        task = row['task']; packet = invoke_models(store, 'packet', {'task': task})
        assert packet['brief'] == prepared['brief'] and packet['request'] == brief
        assert packet['execution_status'] == 'held' and packet['execution_authorized_by_packet'] is False
        assert packet['transport_draft']['arguments']['prompt'].startswith(brief['prompt'])
        assert [i['slot'] for i in packet['inputs']] == [0, 1]
        assert [i['role'] for i in packet['inputs']] == ['edit_target', 'style']
        folder = 'packet-' + row['executor']
        invoke_models(store, 'export_packet', {'task': task, 'directory': folder}, base_dir=args.output)
        exported = args.output/folder
        assert json.loads((exported/'packet.json').read_text()) == packet
        assert (exported/'README.txt').is_file()
        for index, array in enumerate([marker, reference]):
            item = packet['inputs'][index]
            assert item['decoded_rgba_sha256'] == sha(array.tobytes())
            assert (exported/item['filename']).read_bytes() == png_bytes(array)
        result = invoke_models(store, 'ingest', {'task': task, 'sequence': imported['sequence'],
                                                'execution': {'kind': 'supplied-diagnostic'}})
        assert result['manifest']['canvas'] == [5, 4] and result['manifest']['frames'] == 1
        assert result['audit']['desired_size_matches'] is False
        assert result['manifest']['source_bytes'] == imported['source_bytes']
        assert result['execution'] == {'kind': 'supplied-diagnostic'}
        doc, frames = load_sequence(store, result['sequence'])
        assert len(frames) == 1 and np.array_equal(frames[0], marker)
        assert doc['metadata']['model_result'] == result['result']
        portable = args.output/('portable-' + row['executor'])
        export_sequence(store, result['sequence'], portable, formats=['png', 'manifest', 'editable'])
        index_doc = json.loads((portable/'editable/index.json').read_text())
        fresh = Store(args.output/('fresh-' + row['executor']))
        assert import_editable(fresh, portable/'editable') == result['sequence']
        # Compare every exported artifact, including result/task/brief, raw bytes and input PNGs.
        for ident in index_doc['artifact_ids']:
            assert fresh.get_bytes(ident) == store.get_bytes(ident)
        receipt = fresh.get_json(result['result']); task_doc = fresh.get_json(receipt['task'])
        assert fresh.get_json(task_doc['brief']) == frozen
        assert fresh.get_bytes(imported['source_bytes']) == raw
        assert all(fresh.get_bytes(item['png']) == store.get_bytes(item['png']) for item in task_doc['inputs'])
        _, recovered = load_sequence(fresh, result['sequence'])
        assert np.array_equal(recovered[0], marker)
        closure.append({'executor': row['executor'], 'sequence': result['sequence'], 'result': result['result'],
                        'task': task, 'brief': prepared['brief'], 'artifact_count': len(index_doc['artifact_ids']),
                        'all_artifact_bytes_exact': True, 'raw_png_sha256': sha(raw),
                        'decoded_rgba_sha256': sha(marker.tobytes()), 'classification': 'supplied-diagnostic'})
        packets.append(packet); ingested.append(result)
    assert packets[0]['transport_draft']['arguments']['prompt'] == packets[1]['transport_draft']['arguments']['prompt']
    audits = [invoke_models(store, 'audit_pair', {'left': ingested[0]['result'], 'right': ingested[1]['result'], 'scope': scope})
              for scope in ['orchestrator', 'image-backend']]
    assert all(a['comparison_eligible_by_attestation'] is False and a['quality_score'] is None for a in audits)
    assert all(a['exact_pixels_equal'] is True and a['artistic_acceptance'] == 'unreviewed' for a in audits)
    write(args.output/'MODEL-CATALOG.json', catalog)
    write(args.output/'FROZEN-BRIEF.json', frozen)
    write(args.output/'HELD-TASKS.json', prepared)
    write(args.output/'PACKETS.json', packets)
    write(args.output/'SUPPLIED-DIAGNOSTIC-RESULTS.json', ingested)
    write(args.output/'PAIR-AUDITS.json', audits)
    write(args.output/'PORTABLE-CLOSURE.json', closure)
    server = ControlServer(Store(args.output/'http-store'), base_dir=args.output, port=0, workers=1)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    static = []
    def call(path, payload=None):
        headers = {'Content-Type': 'application/json', 'X-Workbench-Token': server.token}
        request = Request(server.url+path, data=None if payload is None else json.dumps(payload).encode(), headers=headers)
        try: response = urlopen(request, timeout=30)
        except HTTPError as error: response = error
        with response:
            return response.status, json.load(response)
    try:
        for endpoint, relative in [('/', 'web/index.html'), ('/app.js', 'web/app.js'),
                                  ('/style.css', 'web/style.css'), ('/source-vfx.js', 'web/source-vfx.js'),
                                  ('/model-lab.js', 'web/model-lab.js')]:
            with urlopen(server.url+endpoint, timeout=30) as response:
                body = response.read(); assert response.status == 200 and body == (package/relative).read_bytes()
                static.append({'endpoint': endpoint, 'file': relative, 'sha256': sha(body)})
        status, described = call('/api/invoke', {'method': 'local.models.catalog', 'params': {}})
        assert status == 200 and described['result'] == catalog
        status, absent = call('/api/invoke', {'method': 'local.models.execute', 'params': {}})
        assert absent['status'] == 'unsupported'
        execution_status = status
        status, readiness = call('/api/readiness')
        assert status == 200 and readiness['comparison_ready'] is False
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=10)
    write(args.output/'HTTP-MODEL-LAB.json', {'static': static, 'catalog_exact': True,
          'execute_status': absent['status'], 'execute_http_status': execution_status, 'comparison_ready': False})
    result = {'passed': True, 'version': expected['version'], 'isolated': sys.flags.isolated, 'package_path': str(package),
              'source_fingerprint': source_fingerprint(), 'installed_runtime_files': len(installed),
              'unchanged_vendor_files': len(expected['unchanged_vendor_files']), 'classification': 'supplied-diagnostic',
              'held_tasks': 2, 'shared_exact_frozen_brief': True, 'ordered_reference_pngs_exact': True,
              'portable_receipt_closure': closure, 'pair_comparison_eligible': False, 'quality_score': None,
              'actual_generators_established': False, 'hermes_discovery': 'read-only; image plugin proposed, unselected and untested',
              'http_assets_and_catalog': True, 'execute_status': absent['status'],
              'provider_calls': 0, 'agent_calls': 0, 'generated_art': False, 'artistic_acceptance': 'unreviewed'}
    assert result['source_fingerprint'] == expected['source_fingerprint']
    write(args.output/'RESULT.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
