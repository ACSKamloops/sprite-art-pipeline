#!/usr/bin/env python3
"""Reproducible supplied-data history benchmark; creates an absent work folder."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from sprite_workbench import construction as c
from sprite_workbench.core import Store


def supplied_fixture(layers):
    size = 256
    return {'schema': 'sprite-edit-project/v1',
        'canvas': {'width': size, 'height': size, 'render_pivot': [128, 128], 'ground_pivot': [128, 250]},
        'palette': [[0, 0, 0, 0], [199, 29, 37, 255], [21, 211, 51, 128], [199, 29, 37, 255], [11, 22, 33, 0]],
        'layers': [{'id': str(i), 'name': 'mechanical layer '+str(i), 'locked': i == layers-1 and layers > 1} for i in range(layers)],
        'cels': {str(i): {'layer_id': str(i), 'pixels': [1+(i%2) if (j+i)%17 == 0 else 0 for j in range(size*size)]} for i in range(layers)},
        'frames': [{'id': str(i), 'duration_ticks': (i%3)+1, 'cels': {str(j): str(j) for j in range(layers)},
                    'landmarks': {'marker': [128, 128]}} for i in range(24)],
        'animations': [{'id': 'markers', 'frames': [str(i) for i in range(24)], 'fps': 60,
                        'loop': True, 'events': [{'at_tick': 0, 'name': 'mechanical'}]}],
        'provenance': {'scope': 'supplied indexed diagnostic fixture; not generated art'}}


def cold(store_path, history_id):
    program = '''import json,sys,time,resource
from sprite_workbench import construction as c,construction_engine as engine
from sprite_workbench.core import Store
original=engine.apply_transaction
calls=[]
def counted(*a):
 calls.append(1)
 return original(*a)
engine.apply_transaction=counted
started=time.perf_counter()
state=c.load_history(Store(sys.argv[1]),sys.argv[2])
print(json.dumps({'elapsed_seconds':time.perf_counter()-started,'replayed_receipts':len(calls),
 'project_hash':state['project_hash'],'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
'''
    output = subprocess.run([sys.executable, '-c', program, str(store_path), history_id],
                            check=True, capture_output=True, text=True)
    return json.loads(output.stdout)


def memory():
    fields = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith(('VmRSS:', 'VmHWM:')):
            key, value, _unit = line.split()
            fields[key.rstrip(':')+'_kib'] = int(value)
    fields['rusage_peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return fields


def run(root, layers):
    store = Store(root/('layers-'+str(layers)))
    fixture = supplied_fixture(layers)
    started = time.perf_counter()
    state = c.create_history(store, c.save_project(store, fixture)['project'])
    initial_seconds = time.perf_counter()-started
    edits, memory_samples = [], []
    for index in range(20):
        transaction = {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': state['project_hash'],
            'reason': 'measured supplied one-pixel indexed edit '+str(index),
            'operations': [{'op': 'paint', 'cel_id': '0', 'points': [[index+1, 0, 2 if index%2 else 3]]}]}
        started = time.perf_counter()
        state = c.edit_history(store, state['history'], transaction)
        edits.append(time.perf_counter()-started)
        memory_samples.append(memory())
    final = state
    movement = {}
    for action in ['undo', 'redo']:
        started = time.perf_counter()
        state = c.move_history(store, state['history'], action)
        movement[action+'_seconds'] = time.perf_counter()-started
    assert state == {key: final[key] for key in ['history', 'project', 'project_hash']}
    independently_loaded = cold(store.path, final['history'])
    assert independently_loaded['replayed_receipts'] == 20
    assert independently_loaded['project_hash'] == final['project_hash']
    files = list((store.path/'blobs').iterdir())
    gates = {'every_edit_under_2s': max(edits) < 2,
        'movement_under_2s': max(movement.values()) < 2,
        'first_last_ratio_under_3': edits[-1]/edits[0] < 3,
        'cold_load_under_15s': independently_loaded['elapsed_seconds'] < 15,
        'cold_verified_all_20_receipts': independently_loaded['replayed_receipts'] == 20}
    return {'canvas': [256, 256], 'frames': 24, 'layers': layers, 'cels': layers,
        'fixture_sha256': hashlib.sha256(canonical(fixture)).hexdigest(),
        'initial_seconds': initial_seconds, 'edit_seconds': edits, 'first_last_ratio': edits[-1]/edits[0],
        **movement, 'memory_samples': memory_samples, 'post_cold_memory': memory(),
        'cold_load': independently_loaded, 'history': final['history'],
        'project': final['project'], 'project_hash': final['project_hash'],
        'blob_count': len(files), 'blob_bytes': sum(file.stat().st_size for file in files),
        'gates': gates, 'passed': all(gates.values())}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cases = [run(args.output, layers) for layers in [1, 11]]
    report = {'schema': 'construction-history-benchmark/v2', 'cases': cases,
        'interpreter': sys.version, 'benchmark_file_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope': 'mechanical supplied fixture; no art generation, aesthetic approval or vendor parity',
        'passed': all(case['passed'] for case in cases)}
    (args.output/'REPORT.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'passed': report['passed'], 'cases': [{
        'layers': case['layers'], 'first': case['edit_seconds'][0], 'last': case['edit_seconds'][-1],
        'max': max(case['edit_seconds']), 'cold': case['cold_load']['elapsed_seconds'],
        'gates': case['gates']} for case in cases], 'report': str(args.output/'REPORT.json')}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
