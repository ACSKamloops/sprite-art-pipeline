#!/usr/bin/env python3
"""Fresh, offline replay of this exact source-hand import and native exchange."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, platform, shutil, subprocess, sys
import numpy as np
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'toolkit'))
from sprite_lab import (History, EditError, apply_transaction, candidate_transaction,
    canonical_json, cel_hash, export_aseprite, export_project, import_aseprite,
    project_hash, read_aseprite, render_frame)

IDS = ['08','09','10','11','12','13','14','22']
TICKS = [12,14,11,11,13,7,7,7]
HOLDS = [60,70,55,55,65,35,35,35]
CANDIDATE_SHA = 'c68dd7f8f86a2d06b432b0c604e3014279316954649474680c7191105f507350'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rgba(path): return np.asarray(Image.open(path).convert('RGBA'))
def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(canonical_json(value) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True, help='Must not exist')
    parser.add_argument('--libresprite', default='libresprite')
    args = parser.parse_args()
    out = args.out.resolve()
    assert not out.exists(), 'Fresh output directory required'
    freeze = json.loads((ROOT/'INPUT-FREEZE.json').read_text())
    for row in freeze['copied_files']:
        assert sha(ROOT/row['path']) == row['sha256'], 'Frozen input changed: '+row['path']
    assert sha(ROOT/'upstream/11.png') == CANDIDATE_SHA
    out.mkdir(parents=True)
    (out/'native').mkdir(); (out/'negative').mkdir(); (out/'native/render').mkdir()
    checks = []
    def check(value, name):
        checks.append({'name': name, 'passed': bool(value)})
        assert value, name

    # The upstream ownership remains separate from the flat editor project.
    donor, original, candidate = rgba(ROOT/'inputs/10.png'), rgba(ROOT/'inputs/11.png'), rgba(ROOT/'upstream/11.png')
    with np.load(ROOT/'upstream/SOURCE-MAP.npz') as z:
        old, target, xy = z['old_owner'], z['target_owner'], z['source_xy']
    domain = old | target
    yy, xx = np.indices(old.shape)
    donor_owner = ((yy >= 31)&(yy <= 49)&(xx >= 94)&(xx <= 114)&(2*xx >= yy+153)&(donor[:,:,3]>0))
    expected_old = ((yy >= 28)&(yy <= 48)&(xx >= 94)&(xx <= 115)&(2*xx >= yy+157)&(original[:,:,3]>0))
    expected_xy = np.full((128,128,2), -1, dtype=np.int16)
    dy, dx = np.where(donor_owner)
    expected_xy[dy-2, dx+1] = np.stack([dx,dy], axis=1)
    check(np.array_equal(old, expected_old) and np.array_equal(xy, expected_xy) and np.array_equal(target, xy[:,:,0]>=0), 'Upstream owner masks and every donor source coordinate reconstructed exactly')
    reconstructed = original.copy(); reconstructed[old] = 0
    reconstructed[target] = donor[xy[target,1], xy[target,0]]
    Image.fromarray(reconstructed).save(out/'reconstructed-source11.png')
    check(np.array_equal(reconstructed, candidate), 'Upstream donor transplant reconstructs all candidate11 RGBA exactly')
    check(sha(out/'reconstructed-source11.png') == CANDIDATE_SHA, 'Upstream candidate11 PNG encoding reproduced exactly on recorded Pillow version')
    changed = np.any(candidate != original, axis=2)
    check(int(changed.sum()) == 234 and not np.any(changed & ~domain), '234 changed pixels stay inside old_owner union target_owner')
    check(np.array_equal(candidate[yy>=50], original[yy>=50]), 'Source11 body at and below y50 remains exact')
    mask = [[int(x),int(y)] for y,x in zip(*np.where(domain))]
    write(out/'allowed-mask.json', mask)

    spec = importlib.util.spec_from_file_location('construction', ROOT/'toolkit/scripts/sprite_construct.py')
    construction = importlib.util.module_from_spec(spec); spec.loader.exec_module(construction)
    source = construction.construct(ROOT/'construction.json')
    write(out/'source-project.json', source)
    check(len(source['layers']) == 1 and len(source['cels']) == 8, 'Honest flat one-layer eight-cel source project')
    for name in IDS:
        check(np.array_equal(np.asarray(render_frame(source,'source-'+name)), rgba(ROOT/'inputs'/f'{name}.png')), 'Source construction all RGBA exact: '+name)
    cel_id = source['frames'][3]['cels']['flat-source']
    transaction = candidate_transaction(source, cel_id, Image.open(ROOT/'upstream/11.png'), mask,
        reason='Import preferred source10 clenched hand into source11 through frozen old_owner|target_owner only; no new paint or timing edits')
    check(len(transaction['operations']) == 1 and transaction['operations'][0]['op'] == 'candidate_patch', 'One guarded candidate import; no paint, palette, timing or pivot operation')
    write(out/'candidate-transaction.json', transaction)
    history = History(source); receipt = history.apply(transaction); final = copy.deepcopy(history.project)
    write(out/'candidate-receipt.json', receipt); write(out/'preferred-project.json', final)
    check(history.undo() == source, 'Undo restores exact complete source project')
    check(history.redo() == final, 'Redo restores exact complete preferred project')
    journal = history.journal(); write(out/'journal.json', journal)
    replayed = History.replay(source, journal).project; write(out/'journal-replayed-project.json', replayed)
    check(replayed == final, 'Journal replay restores exact complete project and receipt')
    expected = [rgba(ROOT/('upstream/11.png' if name=='11' else 'inputs/'+name+'.png')) for name in IDS]
    for name, pixels in zip(IDS, expected):
        check(np.array_equal(np.asarray(render_frame(final, 'source-'+name)), pixels), 'Preferred rendered cel all RGBA exact: '+name)
    check(source['canvas'] == final['canvas'] == {'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]}, 'Both pivots remain exactly [64,112]')
    check(source['animations'] == final['animations'] and [f['duration_ticks'] for f in final['frames']] == TICKS and final['animations'][0]['fps']==200 and not final['animations'][0]['loop'] and final['animations'][0]['events']==[], 'Native tick clock .410 seconds nonloop and no authored events remain exact')

    # Each failure tests a real competing state or a real outside-mask pixel.
    # Prefixing palette_add on the latter two also tests rollback after an
    # earlier valid operation has already mutated the isolated working copy.
    negatives = []
    def reject(name, state, tx, expected_message):
        before = copy.deepcopy(state); encoded = canonical_json(state); error = None
        try: apply_transaction(state, tx)
        except (ValueError, KeyError, TypeError) as exc: error = str(exc)
        check(error is not None and expected_message in error and state == before and canonical_json(state)==encoded, name+' rejects atomically')
        row = {'name':name,'error':error,'before_sha256':project_hash(before),'after_sha256':project_hash(state),'input_unchanged':True,'transaction':tx,'input_project':before}
        negatives.append(row); write(out/'negative'/(name+'.json'), row)
    alternate = copy.deepcopy(source)
    other = alternate['cels'][alternate['frames'][0]['cels']['flat-source']]['pixels']
    other[next(i for i,v in enumerate(other) if v)] = 0
    check(project_hash(alternate) != project_hash(source), 'Stale-project fixture has a real competing cel edit')
    reject('stale-project', alternate, transaction, 'Stale project')
    alternate_cel = copy.deepcopy(source)
    target_pixels = alternate_cel['cels'][cel_id]['pixels']
    target_pixels[next(i for i,v in enumerate(target_pixels) if v)] = 0
    stale_cel_tx = copy.deepcopy(transaction)
    stale_cel_tx['expected_project_sha256'] = project_hash(alternate_cel)
    stale_cel_tx['operations'].insert(0, {'op':'palette_add','rgba':[1,2,3,4]})
    check(cel_hash(alternate_cel,cel_id) != transaction['operations'][0]['expected_cel_sha256'], 'Stale-cel fixture rebinds project precondition to isolate changed cel precondition')
    reject('stale-cel', alternate_cel, stale_cel_tx, 'Stale candidate cel')
    outside_tx = copy.deepcopy(transaction)
    outside_index = int(np.flatnonzero(~domain.ravel())[0])
    outside_tx['operations'][0]['candidate_pixels'][outside_index] = 1
    outside_tx['operations'].insert(0, {'op':'palette_add','rgba':[1,2,3,4]})
    reject('outside-mask', source, outside_tx, 'outside')
    polluted = candidate.copy(); oy,ox = divmod(outside_index,128); polluted[oy,ox] = [1,2,3,255]
    gate_before=copy.deepcopy(source); gate_error=None
    try: candidate_transaction(source,cel_id,Image.fromarray(polluted),mask)
    except ValueError as exc: gate_error=str(exc)
    check(gate_error is not None and 'outside mask' in gate_error and source==gate_before, 'Candidate PNG gate rejects a real outside-domain RGBA edit without mutation')
    write(out/'negative-summary.json', {'passed':True,'cases':[{k:v for k,v in row.items() if k not in ['transaction','input_project']} for row in negatives], 'png_gate_error':gate_error,'outside_coordinate':[ox,oy],'rollback_probe':'stale-cel and outside-mask prepend valid palette_add before candidate rejection'})

    export_project(source, out/'exports-source')
    export_project(final, out/'exports-preferred')
    native = out/'native'
    metadata = export_aseprite(final, native/'preferred.aseprite', animation_id='brann-ne-jab')
    check([t['milliseconds'] for t in metadata['timing']] == HOLDS and all(t['quantization_error_ms']==0 and t['cumulative_boundary_error_ms']==0 for t in metadata['timing']), '200Hz ticks produce exact native millisecond holds with zero quantization error')
    commands = []
    def run(label, args_list):
        process = subprocess.run(args_list, cwd=ROOT, capture_output=True, text=True)
        (native/(label+'.log')).write_text('$ '+shlex_join(args_list)+'\n'+process.stdout+process.stderr)
        commands.append({'label':label,'argv':args_list,'returncode':process.returncode,'log':str(native/(label+'.log'))})
        check(process.returncode==0, 'Native command succeeded: '+label)
        return process
    resolved = shutil.which(args.libresprite)
    assert resolved, 'LibreSprite executable required (offline dependency)'
    version = run('version', [resolved,'--version']).stdout
    run('save', [resolved,'-b','--list-layers',str(native/'preferred.aseprite'),'--save-as',str(native/'preferred-saved.aseprite'),'--sheet',str(native/'saved-sheet.png'),'--sheet-type','horizontal','--data',str(native/'saved-data.json'),'--format','json-array'])
    run('reopen', [resolved,'-b','--list-layers',str(native/'preferred-saved.aseprite'),'--save-as',str(native/'preferred-reopened.aseprite'),'--sheet',str(native/'reopened-sheet.png'),'--sheet-type','horizontal','--data',str(native/'reopened-data.json'),'--format','json-array'])
    run('render-pngs', [resolved,'-b',str(native/'preferred-reopened.aseprite'),'--save-as',str(native/'render/frame.png')])
    imports={}; native_rows=[]
    for filename in ['preferred.aseprite','preferred-saved.aseprite','preferred-reopened.aseprite']:
        path=native/filename; check(path.exists() and path.stat().st_size>128, 'Actual native artifact exists: '+filename)
        decoded=read_aseprite(path)
        check(len(decoded['layers'])==1 and len(decoded['frames'])==8 and [f['milliseconds'] for f in decoded['frames']]==HOLDS,'Actual ASE flat structure and exact native holds: '+filename)
        check(all(np.array_equal(np.asarray(f['cels'][0]),e) for f,e in zip(decoded['frames'],expected)), 'All eight actual ASE cel RGBA payloads exact: '+filename)
        imported = import_aseprite(path, native/'preferred.aseprite.sprite-lab.json')
        write(native/(filename+'.reimport.json'), imported)
        check(imported==final, 'Exact full project reimport including ticks, pivots and no events: '+filename)
        imports[filename]=project_hash(imported)
        native_rows.append({'path':str(path),'sha256':sha(path),'size':path.stat().st_size,'milliseconds':[f['milliseconds'] for f in decoded['frames']]})
    for prefix in ['saved','reopened']:
        sheet=rgba(native/(prefix+'-sheet.png')); data=json.loads((native/(prefix+'-data.json')).read_text())
        rows=data['frames']
        check(len(rows)==8 and [r['duration'] for r in rows]==HOLDS, 'Actual LibreSprite JSON has all original holds: '+prefix)
        for i,row in enumerate(rows):
            box=row['frame']; patch=sheet[box['y']:box['y']+box['h'],box['x']:box['x']+box['w']]
            check(patch.shape==(128,128,4) and np.array_equal(patch,expected[i]), 'Actual LibreSprite rendered sheet RGBA exact: '+prefix+' '+IDS[i])
    pngs=sorted((native/'render').glob('*.png'))
    check(len(pngs)==8, 'Actual LibreSprite wrote eight separate PNG frames')
    png_rows=[]
    for name,path,pixels in zip(IDS,pngs,expected):
        # LibreSprite's normal frame1..frame8 order is recorded explicitly.
        check(np.array_equal(rgba(path),pixels), 'Actual LibreSprite individual PNG RGBA exact: '+name)
        expected_path=ROOT/('upstream/11.png' if name=='11' else 'inputs/'+name+'.png')
        png_rows.append({'source_frame':name,'actual_native_png':str(path),'rgba_equal':True,'rgba_sha256':hashlib.sha256(pixels.tobytes()).hexdigest(),'native_png_sha256':sha(path),'expected_source_png_sha256':sha(expected_path),'raw_png_encoding_equal':sha(path)==sha(expected_path)})
    # Exercise CLI failure with preexisting output sentinels: rejected apply
    # must not replace either file, regardless of the staged palette operation.
    sentinel_project=out/'negative/cli-live.json'; sentinel_receipt=out/'negative/cli-receipt.json'
    sentinel_project.write_bytes(b'preserve project output\n'); sentinel_receipt.write_bytes(b'preserve receipt output\n')
    write(out/'negative/outside-mask-transaction.json', outside_tx)
    cli=[sys.executable,str(ROOT/'toolkit/scripts/sprite_edit.py'),'apply',str(out/'source-project.json'),str(out/'negative/outside-mask-transaction.json'),'--output',str(sentinel_project),'--receipt',str(sentinel_receipt)]
    process=subprocess.run(cli,cwd=ROOT,capture_output=True,text=True)
    (out/'negative/cli-rejection.log').write_text('$ '+shlex_join(cli)+'\n'+process.stdout+process.stderr)
    check(process.returncode==2 and sentinel_project.read_bytes()==b'preserve project output\n' and sentinel_receipt.read_bytes()==b'preserve receipt output\n', 'Rejected CLI apply preserves both existing output files exactly')
    write(native/'NATIVE-PROOF.json',{'passed':True,'actual_libresprite_commands':commands,'libresprite_resolved':resolved,'libresprite_entry_sha256':sha(resolved),'version_output':version,'actual_native_artifacts':native_rows,'reimport_project_sha256':imports,'individual_pngs':png_rows,'rgba_exact_all_eight':True,'native_holds_ms':HOLDS,'native_total_ms':sum(HOLDS),'native_quantization_error_ms':0,'loop_authority':'JSON project and required sidecar false; native ASE player transport is not a game loop claim','events':[],'limits':['One flat baked layer; no dedicated hand or weapon layers','Native PNG encoding may differ while decoded RGBA is exact','No motion acceptance or runtime hit-window claim']})
    write(out/'VERIFIED.json',{'passed':True,'checks':checks,'source_project_sha256':project_hash(source),'preferred_project_sha256':project_hash(final),'candidate11_png_sha256':CANDIDATE_SHA,'changed_rgba_pixels':234,'allowed_domain_pixels':int(domain.sum()),'mask_sha256':sha(out/'allowed-mask.json'),'transaction_sha256':sha(out/'candidate-transaction.json'),'journal_sha256':sha(out/'journal.json'),'native_proof':'native/NATIVE-PROOF.json','environment':{'python':platform.python_version(),'Pillow':pillow_version,'numpy':np.__version__},'acceptance':'Mechanical checks only. Preferred source correction supplied by parent; no new motion acceptance inferred.'})
    print(json.dumps({'passed':True,'checks':len(checks),'output':str(out),'source_project_sha256':project_hash(source),'preferred_project_sha256':project_hash(final),'native_holds_ms':HOLDS,'rgba_exact_all_eight':True}))

def shlex_join(args):
    import shlex
    return shlex.join(args)

if __name__ == '__main__': main()
