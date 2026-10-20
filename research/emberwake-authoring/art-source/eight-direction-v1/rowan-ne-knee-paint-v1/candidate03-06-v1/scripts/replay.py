from pathlib import Path
import argparse,copy,json,hashlib
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,candidate_transaction,EditError,load_json
P=Path(__file__).resolve().parents[1]
def load(n):return load_json((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(n):return np.array(Image.open(P/n).convert('RGBA'))
def mask(n):return np.array(Image.open(P/n).convert('L'))>0
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
if a.output:assert a.output.is_absolute()and not a.output.exists(),'Output must be fresh absolute path'
inputs=load('INPUTS.json')
for f in inputs['immutable_replay_inputs']:assert sha(P/f['path'])==f['sha256'],f['path']
raw=arr('generation/raw.png');assert raw.shape==(1254,1254,4)and sha(P/'generation/raw.png')==inputs['raw_sha256']
# Recompute the entire one shared nearest registration from its rational rule.
coord=np.floor((np.arange(256)+.5)*1254/256).astype('int16');xx,yy=np.meshgrid(coord,coord);fullxy=np.stack([xx,yy],axis=-1);stored=np.load(P/'inputs/normalization/whole-grid-source-xy.npz',allow_pickle=False)['source_xy'];assert np.array_equal(fullxy,stored);grid=raw[yy,xx]
initial=load('projects/initial.json');final=load('projects/final.json');journal=load('projects/journal.json');h=History.replay(initial,journal);end=project_hash(h.project);assert end==project_hash(final)and len(h.records)==2
results=[];rawresults=[];source_outputs=[];editor_outputs=[]
for i in range(8):
 source=arr(f'inputs/source-frames/{i:02}.png');out=source.copy();assert sha(P/f'inputs/source-frames/{i:02}.png')==inputs['source_PNG_sha256'][f'{i:02}']
 if i in [3,6]:
  k=[3,4,5,6].index(i);cell=grid[(k//2)*128:(k//2+1)*128,(k%2)*128:(k%2+1)*128];owner=mask(f'inputs/owners/{i:02}-allowed-trouser-knee-cuff.png');upper=mask(f'inputs/owners/{i:02}-upper-hem-gloves.png');boots=mask(f'inputs/owners/{i:02}-complete-boot-protected-region.png');protected=mask(f'inputs/owners/{i:02}-protected-complete.png');assert np.array_equal(protected,~owner);assert not np.any(owner&(upper|boots))
  data=np.load(P/f'maps/{i:02}-raw-source-map.npz',allow_pickle=False);expectedxy=fullxy[(k//2)*128:(k//2+1)*128,(k%2)*128:(k%2+1)*128].copy();expectedxy[~owner]=-1;assert np.array_equal(owner,data['allowed'])and np.array_equal(expectedxy,data['raw_source_xy'])
  # Literal per-pixel source selection; no alpha edits, layer blend, fit or repaint.
  ys,xs=np.where(owner)
  for y,x in zip(ys,xs):sx,sy=map(int,expectedxy[y,x]);out[y,x]=raw[sy,sx]
  assert np.array_equal(out[owner],cell[owner]);assert np.array_equal(out[protected],source[protected]);assert np.array_equal(out[upper],source[upper]);assert np.array_equal(out[boots],source[boots])
  rawresults.append({'phase':i,'frozen_owner_pixels':int(owner.sum()),'whole_grid_sourceXY_recomputed_exact':True,'actual1254raw_RGBA_texels_exact':True,'protected_upper_hem_gloves_whole_boots_negative_space_exact':True,'alpha_normalization_or_new_paint':False})
 else:assert (P/f'frames/{i:02}.png').read_bytes()==(P/f'inputs/source-frames/{i:02}.png').read_bytes()
 target=arr(f'frames/{i:02}.png');rendered=np.array(render_cel(h.project,f'rowan-ne-{i:02}'));assert np.array_equal(out,target)and np.array_equal(rendered,target);assert np.array_equal(np.array(render_cel(initial,f'rowan-ne-{i:02}')),source);assert sha(P/f'frames/{i:02}.png')==inputs['candidate_PNG_sha256'][f'{i:02}'];assert final['frames'][i]['duration_ticks']==9
 results.append({'phase':i,'PNG_sha256':sha(P/f'frames/{i:02}.png'),'RGBA_sha256':hashlib.sha256(target.tobytes()).hexdigest(),'raw_source_and_separate_editor_RGBA_exact':True,'changed_RGBA_pixels':int(np.any(out!=source,axis=2).sum())});source_outputs.append(out);editor_outputs.append(rendered)
for _ in range(2):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(2):h.redo()
assert project_hash(h.project)==end
negative=[]
def reject(name,fn,hist=None):
 before=project_hash(hist.project)if hist is not None else None;cursor=hist.cursor if hist is not None else None;recordcount=len(hist.records)if hist is not None else None
 try:fn()
 except EditError as e:
  if hist is not None:assert project_hash(hist.project)==before and hist.cursor==cursor and len(hist.records)==recordcount
  negative.append({'guard':name,'rejected':True,'state_unchanged_atomically':True,'message':str(e)});return
 raise AssertionError(name+' unexpectedly accepted')
owner=mask('inputs/owners/03-allowed-trouser-knee-cuff.png');coords=[[int(x),int(y)]for y,x in np.argwhere(owner)];bad=Image.fromarray(arr('frames/03.png'));c=bad.getpixel((64,40));bad.putpixel((64,40),((c[0]+1)%256,*c[1:]));reject('outside-owner candidate RGBA',lambda:candidate_transaction(initial,'rowan-ne-03',bad,coords))
h0=History(initial);badtx=copy.deepcopy(journal['receipts'][0]['transaction']);badtx['expected_project_sha256']='0'*64;reject('stale project precondition',lambda:h0.apply(badtx),h0)
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);patch=next(o for o in badtx['operations']if o['op']=='candidate_patch');patch['expected_cel_sha256']='0'*64;reject('stale cel precondition after isolated palette additions',lambda:h0.apply(badtx),h0)
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);patch=next(o for o in badtx['operations']if o['op']=='candidate_patch');assert not owner[0,0];patch['candidate_pixels'][0]=1;reject('outside-owner transaction index in protected negative space',lambda:h0.apply(badtx),h0)
# Rejected/unimported witnesses remain source-bound and never enter frames04/05.
base4=arr('inputs/source-frames/04.png');owner4=mask('inputs/owners/04-allowed-trouser-knee-cuff.png');raw4=grid[:128,128:];proposal4=base4.copy();proposal4[owner4]=raw4[owner4];assert np.array_equal(proposal4,arr('rejected/04-proposed.png'));data4=np.load(P/'rejected/04-raw-source-map.npz');xy4=fullxy[:128,128:].copy();xy4[~owner4]=-1;assert np.array_equal(xy4,data4['raw_source_xy']);assert np.array_equal(data4['allowed'],owner4);assert np.array_equal(grid[128:,:128],arr('rejected/05-raw-unimported.png'));assert np.array_equal(arr('frames/04.png'),base4);assert np.array_equal(arr('frames/05.png'),arr('inputs/source-frames/05.png'))
assert final['animations'][0]['fps']==160 and final['animations'][0]['loop']is True
receipt={'status':'PASS producer source/editor mechanics; changed-art review pending, not acceptance','raw1254_sha256':inputs['raw_sha256'],'shared_normalization':'Recomputed whole1254→256nearest from center-rule; no per-cell fit or later normalization','all8':results,'sourceXY_witnesses':rawresults,'actual_editor_transactions':2,'initial_project_canonical_sha256':project_hash(initial),'final_project_canonical_sha256':end,'two_step_undo_redo_exact':True,'actual_journal_replay_exact':True,'negative_guards':negative,'original_PNG_byte_phases':[0,1,2,4,5,7],'rejected04_and_unimported05_raw_replayed_but_not_promoted':True,'clock':'8x9/160s=.45s loop','new_paint_masks_normalization_or_generation':False,'external_GUI_runtime_tested':False,'inherited_score':None}
if a.output:
 for folder,bank in [('source-raw',source_outputs),('editor',editor_outputs)]:
  (a.output/folder).mkdir(parents=True)
  for i,out in enumerate(bank):
   dest=a.output/folder/f'{i:02}.png'
   if i in [3,6]:Image.fromarray(out).save(dest)
   else:dest.write_bytes((P/f'inputs/source-frames/{i:02}.png').read_bytes())
   assert sha(dest)==sha(P/f'frames/{i:02}.png')
 (a.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS actual1254raw/sourceXY and independent editor: all8RGBA/PNG,2transactions,undo/redo,staleproject/cel/outsideowner atomic rejection;04/05 source exact.')
