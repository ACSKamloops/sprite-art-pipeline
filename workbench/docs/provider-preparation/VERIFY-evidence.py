#!/usr/bin/env python3
"""Check retained performed browser observations; does not replay or grade art."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

from sprite_workbench.core import Store
from sprite_workbench.export import png_bytes

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def observation(name):
    text = (OUT / 'evidence' / name).read_text()
    return json.JSONDecoder().raw_decode(text.split('### Result\n', 1)[1].lstrip())[0]


def verify():
    checks = []
    def check(name, value):
        assert value, name
        checks.append({'name': name, 'passed': True})
    store = Store(ROOT / 'workspaces/web-control/store')
    flow = observation('models-flow-observation.log')
    before = observation('models-prepared-observation.log')
    check('actual model page and successful form actions', flow['title'] == 'Model Lab · Sprite workbench'
          and flow['url'].endswith('#models') and not flow['errorVisible'])
    check('paired tasks are held and share a frozen brief', len(flow['prepared']['tasks']) == 2
          and flow['prepared']['execution_status'] == 'held' and flow['prepared']['provider_calls'] == 0)
    tasks = [store.get_json(row['task']) for row in flow['prepared']['tasks']]
    brief = store.get_json(flow['prepared']['brief'])['brief']
    check('original prompt whitespace retained', brief['prompt'] == before['prompt']
          and brief['prompt'].startswith('  ') and brief['prompt'].endswith('  '))
    check('same submitted draft and ordered references', tasks[0]['brief'] == tasks[1]['brief']
          and tasks[0]['submitted_prompt_draft'] == tasks[1]['submitted_prompt_draft']
          and tasks[0]['inputs'] == tasks[1]['inputs'])
    directory = Path(flow['exported']['directory'])
    packet = json.loads((directory / 'packet.json').read_text())
    check('complete folder has exact inspected packet', packet == flow['packet'])
    for item in packet['inputs']:
        raw = (directory / item['filename']).read_bytes()
        check('exported PNG retains source pixels and encoded hash',
              hashlib.sha256(raw).hexdigest() == item['png']
              and raw == png_bytes(store.get_raster(item['raster'])))
    source = json.loads((OUT / 'evidence/models-supplied.json').read_text())
    for name in ('first', 'second'):
        result = flow[name]
        receipt = store.get_json(result['result'])
        check(name + ' remains supplied diagnostic and raw pixels unchanged',
              result['raw_sequence'] == source['sequence']
              and receipt['execution']['kind'] == 'supplied-diagnostic'
              and receipt['observed']['source_bytes'] == source['source_bytes']
              and receipt['observed']['canvas'] == [48, 48]
              and receipt['audit']['desired_size_matches'] is False
              and receipt['artistic_acceptance'] == 'unreviewed')
    audit = flow['audit']
    check('diagnostic pair is not a model comparison or quality score', audit['same_frozen_brief']
          and audit['exact_pixels_equal'] and not audit['comparison_eligible_by_attestation']
          and audit['quality_score'] is None)
    persisted = observation('models-persisted-observation.log')
    check('new tab reloads two retained results', persisted['resultCount'] == 2 and not persisted['errorVisible'])
    mobile = observation('models-mobile-observation.log')
    check('mobile fits 390px viewport', mobile['documentWidth'] == mobile['viewport'] == 390 and not mobile['errorVisible'])
    check('fresh tab console has no errors or warnings', 'Total messages: 0 (Errors: 0, Warnings: 0)'
          in (OUT / 'evidence/models-fresh-console.log').read_text())
    with urllib.request.urlopen('http://127.0.0.1:8874/api/readiness', timeout=20) as response:
        live = json.load(response)
    package = json.loads((OUT / 'package/RECEIPT.json').read_text())
    check('current source setup passed; model comparison stays held', live['setup_ready']
          and not live['comparison_ready'] and not live['restart_required']
          and live['source_fingerprint'] == package['source_fingerprint'])
    setup = store.get_json(live['verification']['artifact'])
    (OUT / 'evidence/SETUP-VERIFICATION.json').write_text(json.dumps(setup, indent=2) + '\n')
    report = {'version': 1, 'updated_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
              'runtime_commit': package['source_commit'], 'source_fingerprint': live['source_fingerprint'],
              'experiment': flow['prepared']['experiment'],
              'result_ids': [flow[k]['result'] for k in ('first', 'second')],
              'browser': 'Playwright CLI Chromium; Browser plugin not available',
              'viewports': [[1440, 1050], [390, 844]],
              'model_calls': 0, 'artistic_acceptance': 'unreviewed', 'execution_status': 'held',
              'boundary': 'Root executed UI actions and inspected desktop/mobile screenshots; this script checks retained observations against current Store/files. It does not replay interactions or prove model/art quality.',
              'excluded_attempt': 'Initial incorrect CLI select command left edit_target in a still brief; server correctly rejected with400. Successful later edit flow and clean fresh tab are accepted instead.'}
    (OUT / 'evidence/BROWSER-PROOF.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'checks': len(checks), 'passed': True, 'source_fingerprint': live['source_fingerprint']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
