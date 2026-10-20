#!/usr/bin/env python3
"""Rebuild the flat8cel editor package and verify actual LibreSprite exchange.

Requires Pillow and a LibreSprite executable. Writes only a fresh --out folder.
"""
import argparse, hashlib, importlib.util, json, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, __version__ as pillow_version

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE/'toolkit'))
from sprite_lab import canonical_json, project_hash, render_frame, export_project, candidate_transaction
from sprite_lab.history import History
from sprite_lab.aseprite import export_aseprite, read_aseprite, import_aseprite

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im): return im.convert('RGBA').tobytes()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--libresprite',default='libresprite')
    parser.add_argument('--raw',action='store_true',help='Rebuild the preserved raw-reviewed source before the explicit production cleanup')
    args=parser.parse_args(); out=args.out.resolve()
    if out.exists(): raise ValueError('Fresh output folder required')
    tool=shutil.which(args.libresprite)
    if not tool: raise ValueError('LibreSprite executable not found')
    source=json.loads((PACKAGE/'inputs/SOURCES.json').read_text())
    for entry in source['frames']:
        p=PACKAGE/'inputs'/entry['path']; assert sha(p)==entry['sha256']
        assert hashlib.sha256(rgba(Image.open(p))).hexdigest()==entry['rgba_sha256']
    (out/'inputs').mkdir(parents=True);(out/'native').mkdir();(out/'evidence').mkdir()
    for n in range(8): shutil.copy2(PACKAGE/'inputs/frames'/f'{n:02}.png',out/'inputs'/f'{n:02}.png')
    spec={'schema':'sprite-construction-spec/v1',
      'canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},
      'layers':[{'id':'paint','name':'Brann NE flat painted cel','locked':False}],
      'frames':[{'id':f'walk{n:02}','duration_ticks':9,'landmarks':{},
                 'cels':{'paint':{'image':f'inputs/{n:02}.png','at':[0,0]}}} for n in range(8)],
      'animations':[{'id':'brann-ne-walk','frames':[f'walk{n:02}' for n in range(8)],'fps':160,'loop':True,'events':[]}],
      'provenance':{'name':'Brann northeast walk — flat8cel editable source',
         'source_freeze_sha256':source['source_freeze_sha256'],'source_frames':source['frames'],
         'art_review':source['art_review'],'structure':'One flat layer; no inferred limbs, rig or hidden paint.',
         'clock':'160Hz×9ticks per exposure;8exposures=72ticks=0.45s. fps is tick frequency.',
         'conditional_nw':'Derived mirror x_new=128-x_old; this primary project edits NE only.'}}
    spec_path=out/'construction-spec.json';spec_path.write_text(json.dumps(spec,indent=2)+'\n')
    loader=importlib.util.spec_from_file_location('construct',PACKAGE/'toolkit/scripts/sprite_construct.py')
    mod=importlib.util.module_from_spec(loader);loader.loader.exec_module(mod)
    project=mod.construct(spec_path)
    cleanup_summary=None
    cleanup_path=PACKAGE/'inputs/BORDER-CLEANUP.json'
    if cleanup_path.exists() and not args.raw:
        (out/'raw-project.json').write_text(canonical_json(project)+'\n')
        original=project;raw_hash=project_hash(project);history=History(project)
        cleanup=json.loads(cleanup_path.read_text());total=0;changed_cels=0
        for n,row in enumerate(cleanup['rows']):
            clean=PACKAGE/'inputs/cleaned-frames'/row['file']
            assert sha(clean)==row['output_sha256']
            assert sha(out/'inputs'/row['file'])==row['source_sha256']
            candidate=Image.open(clean).convert('RGBA');baseline=render_frame(history.project,f'walk{n:02}')
            mask=[x['xy'] for x in row['edits']]
            for entry in row['edits']:
                x,y=entry['xy'];assert x in [0,127] or y in [0,127]
                assert list(baseline.getpixel((x,y)))==entry['expected_rgba']==[0,0,0,1]
                assert list(candidate.getpixel((x,y)))==entry['replacement_rgba']==[0,0,0,0]
            actual=[[i%128,i//128] for i,(a,b) in enumerate(zip(baseline.getdata(),candidate.getdata())) if a!=b]
            assert actual==sorted(mask,key=lambda q:(q[1],q[0]))
            if mask:
                cel=history.project['frames'][n]['cels']['paint']
                tx=candidate_transaction(history.project,cel,candidate,mask,
                    reason=f'Apply root BORDER-CLEANUP.json to walk{n:02}: remove only literal black alpha1 background border texels; all outside-maskRGBA exact')
                history.apply(tx);changed_cels+=1;total+=len(mask)
        assert total==cleanup['changed_pixels']==11 and changed_cels==7
        clean_hash=project_hash(history.project)
        for _ in range(changed_cels):history.undo()
        assert project_hash(history.project)==raw_hash
        for _ in range(changed_cels):history.redo()
        assert project_hash(history.project)==clean_hash
        journal=history.journal();replayed=History.replay(original,journal)
        assert project_hash(replayed.project)==clean_hash
        project=history.project
        (out/'cleanup-journal.json').write_text(json.dumps(journal,indent=2)+'\n')
        cleanup_summary={'source_receipt_sha256':sha(cleanup_path),'changed_pixels':11,'changed_cels':7,
            'raw_project_sha256':raw_hash,'clean_project_sha256':clean_hash,'outside_mask_RGBA_exact':True,
            'undo_all_exact':True,'redo_all_exact':True,'journal_replay_exact':True,'no_invented_strokes':True}
        (out/'CLEANUP-VERIFY.json').write_text(json.dumps(cleanup_summary,indent=2)+'\n')
    project_path=out/'project.json';project_path.write_text(canonical_json(project)+'\n')
    export_project(project,out/'exports')
    expected=[Image.open(out/'inputs'/f'{n:02}.png').convert('RGBA') for n in range(8)]
    if cleanup_summary:expected=[Image.open(PACKAGE/'inputs/cleaned-frames'/f'{n:02}.png').convert('RGBA') for n in range(8)]
    for n in range(8): assert rgba(render_frame(project,f'walk{n:02}'))==rgba(expected[n])
    initial=out/'evidence/exported.aseprite'; native=out/'native/brann-ne-walk.aseprite'
    sidecar=out/'native/brann-ne-walk.aseprite.sprite-lab.json'
    metadata=export_aseprite(project,initial,'brann-ne-walk',sidecar)
    version=subprocess.run([tool,'--version'],capture_output=True,text=True,check=True)
    commands=[]
    def run(cmd,label):
        result=subprocess.run(cmd,capture_output=True,text=True,check=True)
        (out/'evidence'/f'{label}.log').write_text(result.stdout+result.stderr)
        commands.append(cmd)
    run([tool,'-b',str(initial),'--save-as',str(native)],'libresprite-save')
    reopened=out/'evidence/reopened.aseprite';sheet=out/'evidence/libresprite-sheet.png'
    data=out/'evidence/libresprite-sheet.json'
    run([tool,'-b',str(native),'--list-layers','--save-as',str(reopened),
         '--sheet',str(sheet),'--sheet-type','horizontal','--data',str(data),'--format','json-array'],
         'libresprite-reopen-render')
    assert native.is_file() and reopened.is_file() and sheet.is_file() and data.is_file()
    native_decoded=read_aseprite(native); reopened_decoded=read_aseprite(reopened)
    expected_ms=[56,57,56,56,56,57,56,56]
    for decoded in [native_decoded,reopened_decoded]:
        assert (decoded['width'],decoded['height'])==(128,128)
        assert len(decoded['layers'])==1 and len(decoded['frames'])==8
        assert [f['milliseconds'] for f in decoded['frames']]==expected_ms
        for n,f in enumerate(decoded['frames']): assert rgba(f['cels'][0])==rgba(expected[n])
    rendered=Image.open(sheet).convert('RGBA');data_json=json.loads(data.read_text())
    assert rendered.size==(1024,128) and len(data_json['frames'])==8
    for n,entry in enumerate(data_json['frames']):
        assert entry['duration']==expected_ms[n]
        rect=entry['frame'];assert [rect['x'],rect['y'],rect['w'],rect['h']]==[128*n,0,128,128]
        assert rgba(rendered.crop((128*n,0,128*(n+1),128)))==rgba(expected[n])
    imported=import_aseprite(native,sidecar);reimported=import_aseprite(reopened,sidecar)
    assert project_hash(imported)==project_hash(project)==project_hash(reimported)
    (out/'evidence/reimported-project.json').write_text(canonical_json(reimported)+'\n')
    checks={'passed':True,'structure':'one flat editable layer,8cels,8frames',
      'source_pngs_verified':8,'flat_project_decoded_RGBA_exact':8,
      'actual_libresprite_saved_decoded_RGBA_exact':8,'actual_reopened_decoded_RGBA_exact':8,
      'actual_libresprite_sheet_decoded_RGBA_exact':8,'alpha_included':True,
      'project_roundtrip_exact':True,'project_sha256':project_hash(project),
      'native_millisecond_holds':expected_ms,'native_total_ms':sum(expected_ms),
      'exact_authoritative_clock':{'tick_hz':160,'hold_ticks':[9]*8,'loop':True,'events':[],
        'render_pivot':[64,112],'ground_pivot':[64,112],'cycle_seconds':[9,20]},
      'per_frame_quantization_ms':[x-56.25 for x in expected_ms],
      'cumulative_boundaries_ms':[sum(expected_ms[:i+1]) for i in range(8)],
      'cumulative_boundary_errors_ms':[sum(expected_ms[:i+1])-56.25*(i+1) for i in range(8)],
      'sidecar_authoritative':True,'sidecar_exported_ase_hash':metadata['ase_sha256'],
      'primary_native_sha256':sha(native),'sidecar_sha256':sha(sidecar),
      'libresprite_executable':tool,'libresprite_version_output':version.stdout+version.stderr,
      'pillow_version':pillow_version,'commands':commands,
      'only_declared_production_cleanup':cleanup_summary,
      'no_invented_edit_journal':True,'edits':'Literal root cleanup candidate patches only; no strokes or extra cleanup.' if cleanup_summary else 'No art edit; raw-reviewed evidence.',
      'boundary':'Native/editor exchange receipt, not a new art score or gameengine acceptance.'}
    (out/'VERIFY.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps({'passed':True,'out':str(out),'native':str(native),'holds_ms':expected_ms,'total_ms':450}))
if __name__=='__main__': main()
