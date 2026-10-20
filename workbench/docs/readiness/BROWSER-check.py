#!/usr/bin/env python3
"""Bind retained real-browser observations to local diagnostic artifacts.

This reads CLI observations; it does not replay the browser interactions or
approve animation quality. See BROWSER-REVIEW.md for the performed actions.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

from sprite_workbench.core import Store
from sprite_workbench.construction import load_history, load_project
from sprite_workbench.readiness import source_fingerprint


def observation(path):
    text = path.read_text()
    marker = '### Result\n'
    if marker not in text:
        raise ValueError(f'No browser result in {path}')
    return json.JSONDecoder().raw_decode(text.split(marker, 1)[1].lstrip())[0]


def verify(browser_output, store_path, output, url, runtime_commit):
    output.mkdir(parents=True, exist_ok=True)
    obs = {name: observation(browser_output / (name + '.log')) for name in (
        'final-editor-dom', 'plan-status', 'grammar-dom', 'transport-dom',
        'interfaces-dom', 'fixed-method-dom', 'vendor-dom',
        'fixed-setup-pending', 'final-setup-completed', 'mobile-fixed-dom')}
    checks = []

    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
        if not value:
            raise AssertionError(name)

    editor = obs['final-editor-dom']
    store = Store(store_path)
    project = load_project(store, editor['project'])
    history = load_history(store, editor['history'])
    raw_history = store.get_json(editor['history'])
    initial = load_project(store, history['initial_project'])
    check('real browser paint retained at exact cel coordinate',
          initial['cels']['marker-a']['pixels'][12] == 0
          and project['cels']['marker-a']['pixels'][12] == 1
          and raw_history['journal']['receipts'][0]['transaction']['operations'][0]['points'] == [[4, 1, 1]])
    check('undo and redo returned to exact verified checkpoint',
          raw_history['version'] == 2 and history['project'] == editor['project']
          and raw_history['journal']['cursor'] == 1
          and editor['undoDisabled'] is False and editor['redoDisabled'] is True
          and editor['errorVisible'] is False)
    sequence = store.get_json(editor['sequence'])
    check('render retains shared cel frame dependencies',
          sequence['metadata']['construction_project'] == editor['project']
          and sequence['metadata']['construction_history'] == editor['history']
          and set(raw_history['journal']['receipts'][0]['diff']['frames']) == {'first', 'third'}
          and raw_history['journal']['receipts'][0]['diff']['unchanged_frames'] == ['second'])
    for frame in sequence['frames']:
        store.get_raster(frame['raster'])
    plan = store.get_json(obs['plan-status']['plan'])
    job = json.loads(obs['plan-status']['detail'])
    check('saved plan executed as actual local pipeline job',
          plan['kind'] == 'pipeline-plan' and job['status'] == 'completed'
          and job['handler'] == 'local.pipeline' and job['error'] is None
          and plan['plan']['steps'][0]['request']['project'] == editor['project']
          and store.get_json(job['artifact'])['frames'] == sequence['frames'])
    check('grammar, transport and interface tabs rendered', obs['grammar-dom']['rows'] == 108
          and obs['transport-dom']['rows'] == 30 and obs['interfaces-dom']['rows'] == 213)
    check('local method invoked through real controls',
          obs['fixed-method-dom'] == {'method': 'local.library.list', 'response': [], 'errorVisible': False})
    check('captured vendor method is visibly unavailable', obs['vendor-dom']['disabled'] is True
          and obs['vendor-dom']['method'] == 'public:POST:/generate-image-v2')
    check('setup button disables during job and refreshes on completion',
          obs['fixed-setup-pending']['disabled'] is True
          and obs['final-setup-completed']['disabled'] is False
          and obs['final-setup-completed']['verification']['status'] == 'completed'
          and obs['final-setup-completed']['comparisonDisabled'] is True)
    check('narrow viewport has no document overflow',
          obs['mobile-fixed-dom']['viewport'] == obs['mobile-fixed-dom']['documentWidth'] == 390)
    with urllib.request.urlopen(url + '/api/readiness', timeout=20) as response:
        current = json.load(response)
    check('live setup proof matches final runtime', current['setup_ready'] is True
          and current['comparison_ready'] is False and current['restart_required'] is False
          and current['source_fingerprint'] == source_fingerprint()
          and current['verification'] == obs['final-setup-completed']['verification'])
    setup = store.get_json(current['verification']['artifact'])
    (output / 'SETUP-VERIFICATION.json').write_text(json.dumps(setup, indent=2) + '\n')
    retained = []
    names = [name + '.log' for name in obs] + [
        'method-diagnostic.log', 'console-final.log', 'readiness-final.png',
        'readiness-mobile.png', 'editor-final.png', 'grammar.png', 'jobs.png', 'methods.png',
        'final-paint.log', 'final-undo.log', 'final-redo.log', 'final-render.log',
        'plan-save.log', 'plan-submit.log']
    for name in names:
        raw = (browser_output / name).read_bytes()
        shutil.copy2(browser_output / name, output / name)
        retained.append({'file': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    report = {'version': 1, 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'checks': checks, 'observations': obs, 'retained_files': retained,
              'runtime_fingerprint': source_fingerprint(), 'runtime_commit': runtime_commit,
              'actions_commit': '846e391', 'final_layout_commit': 'ca74489',
              'browser': 'Playwright Chromium 1243; isolated diagnostic session',
              'viewports': [[1440, 1050], [390, 844]], 'url': url,
              'artistic_acceptance': 'unreviewed', 'continuous_motion_quality_reviewed': False,
              'provider_calls': 0,
              'boundary': 'Real browser controls plus independent retained-artifact checks; supplied 8x4 three-frame diagnostic only. No generated humanoid or private-handler parity claim.'}
    (output / 'BROWSER-PROOF.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'checks': len(checks), 'passed': all(c['passed'] for c in checks), 'runtime_fingerprint': source_fingerprint()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-output', type=Path, required=True)
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--url', default='http://127.0.0.1:8874')
    parser.add_argument('--runtime-commit', required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.browser_output, args.store, args.output, args.url, args.runtime_commit), indent=2))
