#!/usr/bin/env python3
"""Verify retained browser observations against Store bytes and original chunks.

This checks performed UI actions; it does not replay them or grade artwork.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request

from sprite_workbench.core import Store, canonical_json
from sprite_workbench.construction import load_project
from sprite_workbench.readiness import source_fingerprint


def read_observation(path):
    return json.JSONDecoder().raw_decode(path.read_text().split('### Result\n', 1)[1].lstrip())[0]


def verify(root, logs, store_path, research, output):
    output.mkdir(parents=True, exist_ok=True)
    store = Store(store_path); checks = []; records = {}
    def check(name, passed, detail=None):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})
        if not passed:
            raise AssertionError(name)

    for name, filename in [('slash', 'source-slash-result.log'),
                           ('orb_default', 'source-orb-default-result.log'),
                           ('orb_size14', 'source-orb-variant-result.log')]:
        observation = read_observation(logs / filename)
        result = observation['result']
        result = json.loads(result) if isinstance(result, str) else result
        check(name + ' browser action succeeded', observation['errorVisible'] is False)
        controls = store.get_json(result['control_receipt'])
        effect = store.get_json(result['recipe'])
        process = subprocess.run(['node', str(root / 'tests/source_fidelity_oracle.cjs'), str(research)],
                                 input=json.dumps({'recipe': controls['declared_recipe']}),
                                 capture_output=True, text=True, timeout=60, check=False)
        if process.returncode:
            raise AssertionError(process.stderr[:1000])
        original = json.loads(process.stdout)
        compared = 0
        for stream, sequence_id in result['streams'].items():
            sequence = store.get_json(sequence_id)
            assert len(sequence['frames']) == len(original['streams'][stream])
            for frame, encoded in zip(sequence['frames'], original['streams'][stream]):
                assert store.get_raster(frame['raster']).tobytes() == base64.b64decode(encoded)
                compared += 1
            assert sequence['metadata']['pixellab_controls'] == result['control_receipt']
        check(name + ' full-original-bundle oracle matches every stream frame',
              effect['normalized'] == original['recipe'], {'compared_rasters': compared})
        records[name] = {'sequence': result['sequence'], 'recipe': result['recipe'],
                         'control_receipt': result['control_receipt'],
                         'declared_recipe_sha256': controls['hashes']['declared_recipe_sha256']}

    default = store.get_json(records['orb_default']['control_receipt'])
    varied = store.get_json(records['orb_size14']['control_receipt'])
    check('source control variation retains raw and applied forms',
          default['recipe']['layers'][1]['radius'] == 10
          and varied['recipe']['layers'][1]['radius'] == 14
          and varied['declared_recipe']['layers'][1]['radius'] == 10
          and records['orb_default']['sequence'] != records['orb_size14']['sequence'])
    saved_path = root / '.playwright-cli/pixellab-declared-recipe.json'
    saved = json.loads(saved_path.read_text())
    check('download contains chosen raw declared recipe',
          hashlib.sha256(canonical_json(saved)).hexdigest() == varied['hashes']['declared_recipe_sha256'])
    shutil.copy2(saved_path, output / 'SAVED-DECLARED-RECIPE.json')

    playback = read_observation(logs / 'source-playback-samples.log')
    frames = store.get_json(records['orb_size14']['sequence'])['frames']
    for index, encoded in playback['samples'].items():
        assert base64.b64decode(encoded) == store.get_raster(frames[int(index)]['raster']).tobytes()
    transitions = playback['transitions']
    wraps = sum(a['frame'] > b['frame'] for a, b in zip(transitions, transitions[1:]))
    gaps = [b['ms'] - a['ms'] for a, b in zip(transitions, transitions[1:])]
    check('playing canvas shows every exact source frame and successive loop transitions',
          len(playback['samples']) == 8 and wraps >= 2
          and all((b['frame'] - a['frame']) % 8 == 1 for a, b in zip(transitions, transitions[1:])),
          {'transitions': len(transitions), 'loop_wraps': wraps,
           'transition_ms_min': min(gaps), 'transition_ms_max': max(gaps)})

    restored = read_observation(logs / 'source-restore-result.log')
    check('recent render restores its raw settings', restored['size'] == '14'
          and restored['sequence'] == records['orb_size14']['sequence']
          and restored['rawRecipe'] == varied['declared_recipe'])
    before = read_observation(logs / 'source-stale-before.log')
    after = read_observation(logs / 'source-final-input-result.log')
    check('recent render clears actually populated stale optional inputs',
          before['subject'] == 'a' * 64 and before['images'] == {'stale': 'b' * 64}
          and after['subject'] == '' and after['images'] == {}
          and after['sequence'] == records['orb_size14']['sequence'] and after['errorVisible'] is False)

    editor = read_observation(logs / 'source-editor-result.log')
    project = load_project(store, editor['project'])
    check('result opens in separate local editor with source preserved', editor['url'] == '#workspace'
          and not editor['errorVisible']
          and project['provenance']['workbench_source_sequence'] == records['orb_size14']['sequence'])
    mobile = read_observation(logs / 'source-mobile-dom.log')
    check('390px source UI stays within viewport', mobile['documentWidth'] == mobile['viewport'] == 390
          and mobile['errorVisible'] is False)
    invalid = read_observation(logs / 'source-invalid-result.log')
    check('original future-version validator rejects without replacing prior result',
          invalid['errorVisible'] is True and '999' in invalid['error']
          and invalid['result'] == records['orb_size14']['sequence'] and invalid['renderDisabled'] is True)

    with urllib.request.urlopen('http://127.0.0.1:8874/api/readiness', timeout=20) as response:
        live = json.load(response)
    check('final source setup proof is current and comparisons stay blocked',
          live['setup_ready'] is True and live['comparison_ready'] is False
          and live['restart_required'] is False and live['source_fingerprint'] == source_fingerprint())
    (output / 'SETUP-VERIFICATION.json').write_text(json.dumps(store.get_json(live['verification']['artifact']), indent=2) + '\n')

    names = ['source-slash-result.log', 'source-orb-default-result.log', 'source-orb-variant-result.log',
             'source-playback-samples.log', 'source-restore-result.log', 'source-stale-before.log',
             'source-final-input-result.log', 'source-editor-result.log', 'source-mobile-dom.log',
             'source-invalid-result.log', 'source-save-recipe.log', 'source-console.log',
             'pixellab-slash.png', 'pixellab-orb.png', 'pixellab-source-mobile.png']
    files = []
    for name in names:
        raw = (logs / name).read_bytes(); shutil.copy2(logs / name, output / name)
        files.append({'file': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    report = {'version': 1, 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'checks': checks, 'source_records': records, 'files': files,
              'runtime_fingerprint': source_fingerprint(), 'runtime_commit': 'f4e10a7',
              'render_actions_commit': '7bb25d9', 'final_input_restore_commit': 'f4e10a7',
              'original_oracle': 'Full retained original chunks; separate loader; no production factory slices',
              'artistic_acceptance': 'unreviewed', 'full_vendor_replication': False,
              'provider_calls': 0, 'viewports': [[1440, 1050], [390, 844]],
              'boundary': 'Source adapter and host UI reproduction for original returned presets and selected controls. Exact source execution is not private-model or all-branch parity. Pixel-frame capture checks playback mechanics; screenshots do not establish humanoid motion quality.'}
    (output / 'BROWSER-SOURCE-REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'checks': len(checks), 'passed': True, 'fingerprint': source_fingerprint()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--logs', type=Path, default=Path('output/playwright'))
    parser.add_argument('--store', type=Path, default=Path('workspaces/web-control/store'))
    parser.add_argument('--research', type=Path, default=Path('/home/astra/projects/pixellab-local-test-20261011'))
    parser.add_argument('--output', type=Path, default=Path('docs/source-faithful/evidence/browser'))
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.logs, args.store, args.research, args.output), indent=2))
