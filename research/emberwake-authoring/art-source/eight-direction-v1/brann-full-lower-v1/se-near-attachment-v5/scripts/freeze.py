from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];V4=ROOT.parent/'se-counter-swing-v4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
diagnostics=ROOT/'diagnostics';diagnostics.mkdir(exist_ok=True)
for old,new in [('replayed','pillow-rounding-check-partial'),('replayed-final','before-two-inner-join-pixels')]:
    if(ROOT/old).exists():(ROOT/old).rename(diagnostics/new)
(diagnostics/'README.md').write_text('The first source replayer used Pillow alpha compositing and stopped at05 on a1/255 red-channel rounding difference at a translucent cuff edge. The final replayer implements the editor integer straight-RGBA rule. The second replay passed all8 before the final one-pixel internal sleeve-channel closure in05 and07; its frames are retained separately. Neither folder is the final export.\n')
shutil.copy2(ROOT/'replay-frozen/REPLAY-RECEIPT.json',ROOT/'SOURCE-REPLAY-RECEIPT.json')
bindings=[]
for p in sorted((ROOT/'inputs').rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(ROOT/'inputs')
    if rel.parts[0]=='v4':source=V4/Path(*rel.parts[1:])
    elif rel.parts[0]=='lower-owners':source=V4/'inputs'/f'lower-owner-{rel.name}'
    elif rel.name=='whole-arm-donor.png':source=V4/'inputs/whole-arm-donor.png'
    elif rel.name=='near-source-owner.png':source=V4/'masks/near-complete-source-owner.png'
    else:raise ValueError(rel)
    assert sha(p)==sha(source)
    bindings.append({'input':str(p.relative_to(ROOT)),'actual_source':str(source),'sha256':sha(p),'role':'frozen v4 source/control; original128stage and source origin retained'})
toolkit=[{'path':str(p.relative_to(ROOT.parent)),'sha256':sha(p)}for p in sorted((ROOT.parent/'toolkit/sprite_lab').rglob('*.py'))]
save(ROOT/'SOURCE-PROVENANCE.json',{'model_calls':0,'inputs':bindings,'shared_toolkit_dependency':toolkit,'no_source_inputs_modified':True})
records=json.loads((ROOT/'ATTACHMENT.json').read_text());receipt=json.loads((ROOT/'SOURCE-REPLAY-RECEIPT.json').read_text())
save(ROOT/'MANIFEST.json',{'scope':'SE near-arm attachment05–07 only; unselected bounded repair','model_calls':0,'canvas':[128,128],'pivot':[64,112],'ticks_per_second':160,'loop_ticks':72,'all_original_lower_owner_pixels_RGBA_exact_v4':True,'fixed_head_pauldron_central_torso_exact_v4':True,'unchanged_phases':[0,1,2,3,4],'same_v4_palm_excursion':True,'new_rigid_cuff_glove_degrees':{'05':3,'06':5,'07':3},'literal_final_inner_join_pixels':{'05':[[47,67]],'07':[[47,66]]},'project_sha256':receipt['project_sha256'],'editor_initial':'initial-project.json','editor_target':'project.json','actual_journal':'journal.json','source_replay_receipt':'SOURCE-REPLAY-RECEIPT.json','frames':[{'phase':i,'png':f'frames/{i:02}.png','sha256':sha(ROOT/'frames'/f'{i:02}.png'),'hold':{'numerator':9,'denominator':160},'attachment':records[i]}for i in range(8)],'art_status':'unselected; no score or whole-cycle motion approval'})
files=sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='SHA256SUMS'and'__pycache__'not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n'for p in files))
print('Frozen near-attachment v5. MANIFEST SHA256 '+sha(ROOT/'MANIFEST.json'))
print('Canonical project SHA256 '+receipt['project_sha256'])
