#!/usr/bin/env python3
"""Read-only intake verification, including independent browser/native parity."""
from pathlib import Path
from fractions import Fraction
import hashlib, json, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import load_json, project_hash, render_frame
def read(name): return load_json((ROOT/name).read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'SHA256SUMS'
    count=0
    for line in manifest.read_text().splitlines():
        digest,name=line.split('  ',1)
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and sha(path)==digest, name
        count+=1
    package=read('PACKAGE.json'); frozen=read('INPUT-FREEZE.json')
    original=read('upstream/ORIGINAL-INPUTS.json')
    for name,expected in original['files_sha256'].items(): assert sha(ROOT/'inputs'/name)==expected
    for row in frozen['copied_files']: assert sha(ROOT/row['path'])==row['sha256']
    action=read('upstream/ACTION-PACKET-INPUTS.json')
    assert [int(Fraction(*hold)*1000) for hold in action['holds']]==frozen['source_holds_ms']
    assert action['duration']==[41,100] and action['loop'] is False and action['pivot']==[64,112]
    source=read('run/source-project.json'); final=read('run/preferred-project.json')
    assert project_hash(source)==package['source_project_sha256'] and project_hash(final)==package['preferred_project_sha256']
    assert len(final['layers'])==1 and len(final['cels'])==8
    assert source['canvas']==final['canvas'] and source['animations']==final['animations']
    assert final['animations'][0]['events']==[] and final['animations'][0]['loop'] is False
    assert [f['duration_ticks'] for f in final['frames']]==[12,14,11,11,13,7,7,7]
    assert final['animations'][0]['fps']==200
    changed_cels=[name for name in source['cels'] if source['cels'][name]!=final['cels'][name]]
    assert changed_cels==[source['frames'][3]['cels']['flat-source']]
    tx=read('run/candidate-transaction.json')
    assert len(tx['operations'])==1 and tx['operations'][0]['op']=='candidate_patch'
    with np.load(ROOT/'upstream/SOURCE-MAP.npz') as maps:
        ys,xs=np.where(maps['old_owner']|maps['target_owner'])
    assert tx['operations'][0]['mask']==[[int(x),int(y)] for y,x in zip(ys,xs)]
    for directory in ['run','replay-check']:
        report=read(directory+'/VERIFIED.json')
        assert report['passed'] and len(report['checks'])==79 and all(c['passed'] for c in report['checks'])
        assert report['source_project_sha256']==package['source_project_sha256']
        assert report['preferred_project_sha256']==package['preferred_project_sha256']
        assert read(directory+'/source-project.json')==source and read(directory+'/preferred-project.json')==final
        native=read(directory+'/native/NATIVE-PROOF.json')
        assert native['passed'] and native['rgba_exact_all_eight'] and native['native_holds_ms']==frozen['source_holds_ms']
        assert native['events']==[] and len(native['individual_pngs'])==8
        assert all(row['rgba_equal'] and not row['raw_png_encoding_equal'] for row in native['individual_pngs'])
        for name in ['preferred.aseprite','preferred-saved.aseprite','preferred-reopened.aseprite']:
            assert read(directory+'/native/'+name+'.reimport.json')==final
    for name in ['source-project.json','preferred-project.json','candidate-transaction.json','candidate-receipt.json','journal.json']:
        assert (ROOT/'run'/name).read_bytes()==(ROOT/'replay-check'/name).read_bytes()
    assert (ROOT/'run/native/preferred.aseprite').read_bytes()==(ROOT/'replay-check/native/preferred.aseprite').read_bytes()
    assert (ROOT/'run/native/preferred-reopened.aseprite').read_bytes()==(ROOT/'replay-check/native/preferred-reopened.aseprite').read_bytes()
    browser=read('output/playwright/BROWSER-PROOF.json')
    assert browser['passed'] and len(browser['checks'])==14 and all(c['passed'] for c in browser['checks'])
    assert browser['source_project_sha256']==project_hash(source) and browser['preferred_project_sha256']==project_hash(final)
    assert read('output/playwright/browser-saved-project.json')==final
    assert read('output/playwright/browser-saved-journal.json')==read('run/journal.json')==browser['browser_journal']
    for row in browser['canonical_rgba']:
        expected=np.asarray(render_frame(final,row['frame'])).tobytes()
        assert hashlib.sha256(expected).hexdigest()==row['rgba_sha256']
    assert len(browser['canonical_rgba'])==8
    assert len(browser['negative_cases'])==3 and all(c['error'] and c['unchanged'] for c in browser['negative_cases'])
    print(json.dumps({'passed':True,'manifest_files':count,'targeted_checks_per_offline_replay':79,'fresh_replay_exact':True,'browser_checks':14,'independent_browser_rgba_hashes':8,'preferred_project_sha256':project_hash(final),'native_RGBA_exact_all8':True,'native_PNG_encoding_exact':False}))
if __name__=='__main__': main()
