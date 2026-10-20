from pathlib import Path
import sys,json,hashlib,copy
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import History,project_hash

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n')
initial=json.loads((ROOT/'initial-project.json').read_text());target=json.loads((ROOT/'project.json').read_text());journal=json.loads((ROOT/'journal.json').read_text());bad=copy.deepcopy(initial);bad['frames'][0]['duration_ticks']=10
try:History.replay(bad,journal)
except ValueError as e:guard={'stale_initial_journal_rejected':True,'exception':str(e)}
else:raise AssertionError('stale project was accepted')
# Transaction owners are exact literal lower-owner masks; inspect every point.
upperguard={}
for receipt in journal['receipts']:
 t=receipt['transaction']
 for op in t['operations']:
  i=int(op['cel_id'].removeprefix(op['cel_id'].rstrip('0123456789')));upper=np.array(Image.open(ROOT/'masks'/f'{i:02}-whole-upper.png'))>0
  assert op['mask']==[[x,y]for x,y,_ in op['points']]
  assert all(not upper[y,x]for x,y,_ in op['points'])
  upperguard[op['cel_id']]=len(op['points'])
guard['every_actual_transaction_point_excludes_full_upper_owner']=True;guard['actual_operation_point_counts']=upperguard;save(ROOT/'GUARD-RECEIPT.json',guard)
recipe=json.loads((ROOT/'RECIPE.json').read_text());frames=[]
for i in range(8):
 frame=ROOT/'frames'/f'{i:02}.png';source=ROOT/'inputs/v5-frames'/f'{i:02}.png';actual=np.array(Image.open(frame).convert('RGBA'));control=np.array(Image.open(source).convert('RGBA'))
 assert sha(source)==recipe['source_hashes'][f'{i:02}'];assert sha(ROOT/'replayed-frames'/f'{i:02}.png')==sha(frame)
 if i in [3,4,5]:
  upper=np.array(Image.open(ROOT/'masks'/f'{i:02}-whole-upper.png'))>0;assert np.array_equal(actual[upper],control[upper])
 else:assert sha(frame)==sha(source)
 frames.append({'phase':i,'path':str(frame.relative_to(ROOT)),'sha256':sha(frame),'RGBA_changes_from_v5':int(np.any(actual!=control,axis=2).sum()),'full_upper_exact_v5':True,'PNG_bytes_exact_v5':i not in [3,4,5],'duration_ticks':9})
manifest={'status':'frozen unselected three-pose candidate; pending independent art review','art_pixels_unchanged_after_root_inspected_preview':True,'model_calls':0,'clock':{'ticks_per_second':160,'ticks_per_exposure':9,'loop_ticks':72,'loop_seconds':.45},'project_canonical_sha256':project_hash(target),'source_authority':'frozen BrannSE near-attachment-v5; earlier source-guide04','03_boot_vertical_projection':[5,6],'03_boot_unscaled_source_perfect':False,'frames':frames,'guarded_editor_replay_and_source_map_recipe_exact_8_of_8':True,'physical_contact_or_acceptance_claim':False}
save(ROOT/'MANIFEST.json',manifest)
files=sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='SHA256SUMS'and'__pycache__'not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n'for p in files))
print('Frozen',len(files),'files; MANIFEST',sha(ROOT/'MANIFEST.json'),'project',project_hash(target))
