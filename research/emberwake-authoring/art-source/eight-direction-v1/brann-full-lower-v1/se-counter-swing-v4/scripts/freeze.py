from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
diagnostics=ROOT/'diagnostics';diagnostics.mkdir(exist_ok=True)
if (ROOT/'replayed').exists():
    (ROOT/'replayed').rename(diagnostics/'overbroad-row-invariant-replay-partial')
    (diagnostics/'README.md').write_text('The first replay asserted all RGBA in rows92–127 were unchanged. It stopped at phase02 because two complete moving-glove fringe pixels (alpha1 and5) enter previously transparent air at row92. Actual original boot/contact pixels remain exact. The final replay binds the source-owner invariant and records those coordinates explicitly. The partial old replay is retained here; it is not a final export.\n')
shutil.copy2(ROOT/'replayed-final'/'REPLAY-RECEIPT.json',ROOT/'SOURCE-REPLAY-RECEIPT.json')
bindings=[]
for i in range(8):
    bindings += [(f'inputs/control/{i:02}.png',Path('/home/astra/artifacts/emberwake-underarm-shadow-pilot-v1/frames')/f'{i:02}.png','closed-slit starting control'),(f'inputs/motion-intent/{i:02}.png',ROOT.parent/'se'/'frames'/f'{i:02}.png','motion intent only; torso/gloves not copied from these varying poses'),(f'inputs/lower-owner-{i:02}.png',ROOT.parent/'manual-pilot-v2'/'inputs'/'se'/f'lower-{i:02}.png','original lower-pose ownership witness')]
bindings += [('inputs/whole-arm-donor.png',ROOT.parent/'manual-pilot-v2/inputs/se-whole-arm-donor.png','complete SE00 same-view arm paint'),('inputs/closed-slit-source-witnesses.json',Path('/home/astra/artifacts/emberwake-underarm-shadow-pilot-v1/EDITS.json'),'literal closed-slit witnesses retained'),('inputs/legacy-near-owner.png',ROOT.parent/'manual-pilot-v2/masks/near-complete-forearm.png','2D complete near forearm ownership'),('inputs/legacy-far-owner.png',ROOT.parent/'manual-pilot-v2/masks/far-complete-forearm.png','2D complete far forearm ownership')]
sources=[]
for local,source,role in bindings:
    assert sha(ROOT/local)==sha(source)
    sources.append({'input':local,'actual_source':str(source),'sha256':sha(ROOT/local),'role':role})
toolkit=[{'path':str(p.relative_to(ROOT.parent)),'sha256':sha(p)}for p in sorted((ROOT.parent/'toolkit/sprite_lab').rglob('*.py'))]
save(ROOT/'SOURCE-PROVENANCE.json',{'model_calls':0,'status':'unselected bounded SE experiment','sources':sources,'shared_toolkit_dependency':toolkit,'no_frozen_inputs_modified':True})
motion=json.loads((ROOT/'MOTION.json').read_text());joins=json.loads((ROOT/'UNDERPAINT.json').read_text());receipt=json.loads((ROOT/'SOURCE-REPLAY-RECEIPT.json').read_text())
frames=[]
for i in range(8):
    frames.append({'phase':i,'png':f'frames/{i:02}.png','sha256':sha(ROOT/'frames'/f'{i:02}.png'),'duration':{'numerator':9,'denominator':160},'maps':[f'maps/{i:02}-{s}.npz'for s in ['body','near','far']],'source_arm_translations':{'near':motion[i]['near_translation'],'far':motion[i]['far_translation']},'literal_join_underpaint':joins[i]['literal_inspected_join_underpaint_before_arms'],'rigid_cuff_glove_plateaus':motion[i]['rigid_plateaus'],'actual_lower_pose_owner_occlusions':motion[i]['original_lower_pixels_occluded_by_arms'],'source_boot_contact_RGBA_exact':True})
save(ROOT/'MANIFEST.json',{'scope':'One complete SE counter-swing experiment; no rear port, new generation or art selection','canvas':[128,128],'render_pivot':[64,112],'ground_pivot':[64,112],'timebase_ticks_per_second':160,'loop_ticks':72,'loop_seconds':0.45,'fixed_head_chest_top_and_pauldron_pixels_exact':True,'original_lower_pose_coordinates_unchanged':True,'underpaint':'literal source-colored authored sleeve/tunic material before source-over arms','project_sha256':receipt['project_sha256'],'editor_source':'initial-project.json','editor_target':'project.json','actual_editor_journal':'journal.json','frames':frames,'verification':'SOURCE-REPLAY-RECEIPT.json','media_verification':'MEDIA-RECEIPT.json','art_status':'unselected; no score or anatomy/engine certification'})
files=sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='SHA256SUMS'and'__pycache__'not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n'for p in files))
print('Frozen eight actual frames, metadata, source maps, guarded journal, exact replay and output hash ledger.')
print('MANIFEST.json SHA256 '+sha(ROOT/'MANIFEST.json'))
print('project canonical SHA256 '+receipt['project_sha256'])
