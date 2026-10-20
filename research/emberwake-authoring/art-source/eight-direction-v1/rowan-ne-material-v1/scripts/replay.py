from pathlib import Path
import argparse,copy,json,hashlib,runpy,sys
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,candidate_transaction,EditError,load_json
P=Path(__file__).resolve().parents[1]
def load(n):return load_json((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(n):return np.array(Image.open(P/n).convert('RGBA'))
def mask(n):return np.array(Image.open(P/n).convert('L'))>0
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
if args.output:assert args.output.is_absolute()and not args.output.exists(),'Output must be a fresh absolute directory';args.output.mkdir(parents=True)
# Retained literal-source replay is local, read-only unless explicitly exporting.
saved=sys.argv[:];sys.argv=[str(P/'scripts/replay_source.py')]+(['--output',str(args.output/'source-map')]if args.output else[])
try:runpy.run_path(str(P/'scripts/replay_source.py'),run_name='__main__')
finally:sys.argv=saved
initial=load('projects/initial.json');target=load('projects/final.json');journal=load('projects/journal.json');recipe=load('RECIPE.json');h=History.replay(initial,journal);end=project_hash(h.project);assert end==project_hash(target)and len(h.records)==3
repairs={r['phase']:r for r in recipe['phase_repairs']};assert sorted(repairs)==[4,5,6];assert {i:r['actual_changed_RGBA_pixels']for i,r in repairs.items()}=={4:17,5:25,6:21}
frames=[]
if args.output:(args.output/'editor').mkdir()
for i in range(8):
 original=arr(f'inputs/frames/{i:02}.png');frozen=arr(f'candidate/{i:02}.png');editor=np.array(render_cel(h.project,f'rowan-ne-{i:02}'));assert np.array_equal(editor,frozen);assert np.array_equal(np.array(render_cel(initial,f'rowan-ne-{i:02}')),original)
 if i in repairs:
  assert sha(P/f'candidate/{i:02}.png')==repairs[i]['candidate_PNG_sha256'];upper=mask(f'masks/{i:02}-protected-upper.png');boot=mask(f'masks/{i:02}-exact-complete-boot.png');allowed=mask(f'masks/{i:02}-literal-material-owner.png');assert not np.any(allowed&(upper|boot));assert np.array_equal(frozen[upper],original[upper]);assert np.array_equal(frozen[boot],original[boot]);assert np.array_equal(frozen[~allowed],original[~allowed])
 else:assert (P/f'candidate/{i:02}.png').read_bytes()==(P/f'inputs/frames/{i:02}.png').read_bytes()
 if args.output:
  dest=args.output/'editor'/f'{i:02}.png'
  if i in repairs:Image.fromarray(editor).save(dest)
  else:dest.write_bytes((P/f'inputs/frames/{i:02}.png').read_bytes())
  assert sha(dest)==sha(P/f'candidate/{i:02}.png')
 frames.append({'phase':i,'RGBA_sha256':hashlib.sha256(frozen.tobytes()).hexdigest(),'PNG_sha256':sha(P/f'candidate/{i:02}.png'),'source_and_editor_RGBA_PNG_exact':True,'changed_RGBA_pixels':int(np.any(frozen!=original,axis=2).sum())})
for _ in range(3):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(3):h.redo()
assert project_hash(h.project)==end
negative=[]
def reject(name,fn,hist=None):
 before=project_hash(hist.project)if hist is not None else None;cursor=hist.cursor if hist is not None else None
 try:fn()
 except EditError as e:
  if hist is not None:assert project_hash(hist.project)==before and hist.cursor==cursor
  negative.append({'guard':name,'rejected':True,'state_unchanged':True,'message':str(e)});return
 raise AssertionError(name+' unexpectedly accepted')
allowed=mask('masks/04-literal-material-owner.png');coords=[[int(x),int(y)]for y,x in np.argwhere(allowed)];bad=Image.fromarray(arr('candidate/04.png'));c=bad.getpixel((64,40));bad.putpixel((64,40),((c[0]+1)%256,*c[1:]));reject('candidate changes outside explicit cloth mask',lambda:candidate_transaction(initial,'rowan-ne-04',bad,coords))
h0=History(initial);badtx=copy.deepcopy(journal['receipts'][0]['transaction']);badtx['expected_project_sha256']='0'*64;reject('stale project hash',lambda:h0.apply(badtx),h0)
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);patch=next(o for o in badtx['operations']if o['op']=='candidate_patch');patch['expected_cel_sha256']='0'*64;reject('stale candidate cel hash',lambda:h0.apply(badtx),h0)
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);patch=next(o for o in badtx['operations']if o['op']=='candidate_patch');assert not allowed[0,0];patch['candidate_pixels'][0]=1;reject('transaction patch index outside cloth mask',lambda:h0.apply(badtx),h0)
# Preserve and independently replay the rejected03 alternative; never promote it.
alt=load('rejected/03-rounded-patch-v1/RECIPE.json');r3=alt['repairs'];rejected=arr('inputs/frames/03.png')
for op in r3['operations']:
 x,y=op['target'];sx,sy=op['source'];sp=op['source_phase'];c=arr(f'inputs/frames/{sp:02}.png')[sy,sx];assert c.tolist()==op['source_RGBA'];rejected[y,x]=c
assert np.array_equal(rejected,arr('rejected/03-rounded-patch-v1/candidate.png'));assert sha(P/'rejected/03-rounded-patch-v1/candidate.png')==r3['candidate_PNG_sha256'];assert int(np.any(rejected!=arr('inputs/frames/03.png'),axis=2).sum())==55
assert all(f['duration_ticks']==9 for f in target['frames'])and target['animations'][0]['fps']==160
receipt={'status':'PASS producer mechanics; independent material review pending; no motion-quality improvement inferred','all8':frames,'actual_guarded_transactions':3,'initial_project_canonical_sha256':project_hash(initial),'final_project_canonical_sha256':end,'undo_redo_exact':True,'upper_head_torso_arms_gloves_RGBA_exact':True,'complete_original_boot_owners_RGBA_exact':True,'boot_toe_projections_and_whole_stage_placement_unchanged':True,'unchanged_original_PNGs':[0,1,2,3,7],'negative_guards':negative,'03_rejected_alternative_retained_and_source_replayed_exact':True,'03_rejected_changed_pixels':55,'03_current_candidate_is_original':True,'clock':'8x9/160s=.45s loop','model_calls':0,'external_GUI_or_game_runtime_tested':False,'inherited_score':None}
if args.output:(args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS current all8 source/editor RGBA and PNG; guarded3tx, undo/redo, four negative guards; original03 retained, rejected55px alternative replayed separately.')
