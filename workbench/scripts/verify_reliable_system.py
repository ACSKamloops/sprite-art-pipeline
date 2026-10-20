#!/usr/bin/env python3
"""Exercise the real installed Studio, selection and all local command channels.

Run with the isolated installation's Python -I. Evidence contains artifact IDs,
never HTTP tokens, credentials or provider requests. No provider is launched.
"""
import argparse
from io import StringIO, BytesIO
import json
from pathlib import Path
import subprocess
import sys
import threading
from urllib.request import Request, urlopen
import zipfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--expected-prefix', required=True)
    args = parser.parse_args()
    import sprite_workbench
    from sprite_workbench import construction, studio
    from sprite_workbench.core import Store, digest, load_sequence, ValidationError
    from sprite_workbench.selection import create_selection, apply_selection, load_selection, validate_edit_receipt
    from sprite_workbench.pipeline import execute_plan
    from sprite_workbench.channel import serve
    from sprite_workbench.web_server import ControlServer
    from sprite_workbench.readiness import source_fingerprint
    import numpy as np

    package = Path(sprite_workbench.__file__).resolve().parent
    if not package.is_relative_to(Path(args.expected_prefix).resolve()):
        raise SystemExit('Unexpected package import: '+str(package))
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {'kind': 'reliable-system-installed-proof', 'version': 1,
              'package_version': sprite_workbench.__version__, 'package': str(package),
              'source_fingerprint': source_fingerprint(), 'provider_calls': 0,
              'visual_acceptance': 'unreviewed', 'checks': []}
    def check(name, passed):
        report['checks'].append({'id': name, 'status': 'passed' if passed else 'failed'})
        if not passed:
            raise AssertionError(name)
    def write(name, value):
        (output/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    try:
        store = Store(output/'store')
        loaded = studio.load_example(store, 'hero-walk'); write('INITIAL.json', loaded)
        project = construction.load_project(store, loaded['project'])
        cel = project['frames'][0]['cels']['paint']
        selected = create_selection(store, loaded['project'], cel, [128,128], 0)
        selection, mask = load_selection(store, selected['selection'])
        check('actual_recovered_godot_selection', 0 < selected['selected_pixels'] < 256*256)
        edited = apply_selection(store, loaded['history'], selected['selection'], 'erase')
        write('EDIT.json', edited)
        check('selection_receipt_replay', validate_edit_receipt(store, edited['selection_receipt'])['project_after'] == edited['project'])
        after = construction.load_project(store, edited['project'])
        before_indices = np.array(project['cels'][cel]['pixels'])
        after_indices = np.array(after['cels'][cel]['pixels'])
        outside = mask[...,3].reshape(-1) == 0
        check('outside_selection_indices_unchanged', np.array_equal(before_indices[outside], after_indices[outside]))
        check('visible_edit_changes_project', edited['project'] != loaded['project'] and edited['changed_indices'] > 0)
        undo = construction.move_history(store, edited['history'], 'undo')
        check('undo_exact_project_identity', undo['project'] == loaded['project'])
        redo = construction.move_history(store, undo['history'], 'redo')
        check('redo_exact_project_identity', redo['project'] == edited['project'])
        try:
            apply_selection(store, redo['history'], selected['selection'], 'erase')
            check('stale_mask_rejected', False)
        except ValidationError:
            check('stale_mask_rejected', True)
        receipts = [edited['selection_receipt']]
        checked = studio.verify(store, redo['project'], redo['history'], loaded['animation_id'], receipts)
        check('reopened_history_verified', checked['mechanical_ready'] and checked['visual_acceptance'] == 'unreviewed')
        exported = studio.export(store, redo['project'], redo['history'], loaded['animation_id'],
                                base_dir=output, selection_receipts=receipts)
        write('EXPORT.json', exported)
        check('final_export_reverification', studio.verify_export(store, exported['sequence'], exported['directory'],
                    project=redo['project'], history=redo['history'])['status'] == 'passed')
        archive = studio.download(store, exported['export'])
        with zipfile.ZipFile(BytesIO(archive)) as zipped:
            check('download_zip_crc_and_inventory', zipped.testzip() is None and 'PACKAGE.json' in zipped.namelist())
            check('selection_mask_and_receipt_retained', all('editable/artifacts/'+x in zipped.namelist()
                  for x in (edited['selection_receipt'], selected['selection'], selection['mask_raster'])))
        (output/'verified-walk-package.zip').write_bytes(archive)
        slash = studio.load_example(store, 'hero-slash')
        v = studio.verify(store, slash['project'], slash['history'], slash['animation_id'])
        sequence, _ = load_sequence(store, v['sequence'])
        check('real_slash_one_shot', sequence['play_count'] == 1 and v['frame_count'] == 16 and v['duration'] == [2,1])
        verify_request = {'project':redo['project'], 'history':redo['history'],
                          'animation_id':loaded['animation_id'], 'selection_receipts':receipts}
        planned = execute_plan(store, {'version':1,'steps':[{'id':'checked','action':'studio','method':'verify','request':verify_request}]}, base_dir=output)
        check('declarative_plan_channel', planned['status'] == 'completed' and planned['results']['checked']['sequence'] == exported['sequence'])
        source = StringIO(json.dumps({'id':1,'method':'local.studio.verify','params':verify_request})+'\n')
        sink = StringIO(); serve(store, base_dir=output, result_ref='studio-proof', workers=2, source=source, sink=sink)
        replies = [json.loads(line) for line in sink.getvalue().splitlines()]
        check('jsonl_channel', any(r.get('id') == 1 and r.get('status') == 'completed' and
                                  r['result']['sequence'] == exported['sequence'] for r in replies))
        request_file = output/'verify-request.json'; request_file.write_text(json.dumps(verify_request)+'\n')
        cli = subprocess.run([sys.executable,'-I','-m','sprite_workbench','--workspace',str(store.path),
                'studio','verify',str(request_file)], cwd=output, capture_output=True, text=True, timeout=30)
        check('cli_channel', cli.returncode == 0 and json.loads(cli.stdout)['sequence'] == exported['sequence'])
        server = ControlServer(store, base_dir=output, port=0, workers=2)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with urlopen(server.url+'/api/bootstrap', timeout=30) as response:
                bootstrap = json.load(response)
            body = json.dumps({'method':'local.studio.verify','params':{'project':redo['project'],'history':redo['history'],
                    'animation_id':loaded['animation_id'],'selection_receipts':receipts}}).encode()
            request = Request(server.url+'/api/invoke', data=body,
                headers={'Content-Type':'application/json','X-Workbench-Token':bootstrap['csrf_token'], 'Origin':server.url})
            with urlopen(request, timeout=30) as response:
                invoked = json.load(response)
            check('http_verified_project', invoked['result']['mechanical_ready'])
            with urlopen(server.url+exported['download_url'], timeout=30) as response:
                check('http_download_identity', digest(response.read()) == exported['zip'])
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)
        report['status'] = 'passed'
    except Exception as exc:
        report |= {'status':'failed','error':{'type':type(exc).__name__,'message':str(exc)}}
    write('REPORT.json', report)
    print(json.dumps({'status':report['status'],'checks':len(report['checks']),'report':str(output/'REPORT.json')}))
    return 0 if report['status'] == 'passed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
