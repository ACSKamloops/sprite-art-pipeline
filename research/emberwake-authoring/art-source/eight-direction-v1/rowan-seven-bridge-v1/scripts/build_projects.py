from pathlib import Path
import json,hashlib,copy
import numpy as np
from PIL import Image
from sprite_lab import project_hash,canonical_json,candidate_transaction,History,render_cel,EditError,cel_hash
P=Path(__file__).resolve().parents[1]
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i in range(8):
 im=Image.open(P/'inputs/A'/f'{i:02}.png').convert('RGBA');indices=[]
 for rgba in im.getdata():
  if rgba not in lookup:lookup[rgba]=len(palette);palette.append(list(rgba))
  indices.append(lookup[rgba])
 cel=f'rowan-se-{i:02}';cels[cel]={'layer_id':'paint','pixels':indices};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Source-owned complete painted cels;07 replacement guarded by lower mask','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'rowan-SE-walk','frames':[f'{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'asset':'Rowan southeast walk07 bridge trial','source_bank':'inputs/A/00..07.png','frame_hashes':[sha(f'inputs/A/{i:02}.png') for i in range(8)],'generation_provider':'built-in OpenAI ImageGen','generation_calls':1,'raw_sha256':sha('generation/raw.png'),'registration':'single1254x1254→128x128 nearest whole-stage resize; no per-posefit','editable_scope':'Raster cels with exact full-cel source pixels; source-part guide/maps retained separately; no hidden rig or inferred anatomy','approval_scope':'Parent inspected producer preview; combined04+07/independent art review remains parent-owned'}}
mask=np.array(Image.open(P/'masks/07-lower-repair-owner.png').convert('L'))>0;coords=[[int(x),int(y)] for y,x in np.argwhere(mask)]
candidate=Image.open(P/'trial/07.png').convert('RGBA')
tx=candidate_transaction(initial,'rowan-se-07',candidate,coords,reason='Import the exact parent-inspected generated07 lower pose through its literal lower repair owner; stable upper/blue-gold hem and full original visible gloves retained')
h=History(initial);receipt=h.apply(tx);final=copy.deepcopy(h.project);journal=h.journal()
for i in range(8):assert render_cel(final,f'rowan-se-{i:02}').tobytes()==Image.open(P/'trial'/f'{i:02}.png').convert('RGBA').tobytes()
finalhash=project_hash(final);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
replayed=History.replay(initial,journal);assert project_hash(replayed.project)==finalhash
# The exact actual outside-mask import guard must reject a deliberately changed protected pixel.
bad=candidate.copy();px=bad.getpixel((64,40));bad.putpixel((64,40),((px[0]+1)%256,*px[1:]));rejected=False
try:candidate_transaction(initial,'rowan-se-07',bad,coords)
except EditError:rejected=True
assert rejected and project_hash(initial)==journal['initial_project_sha256']
badtx=copy.deepcopy(tx);badtx['expected_project_sha256']='0'*64;before=project_hash(h.project);badpre=False
try:h.apply(badtx)
except EditError:badpre=True
assert badpre and project_hash(h.project)==before
for value,name in [(initial,'initial'),(final,'final'),(journal,'journal'),(tx,'transaction'),(receipt,'transaction-receipt')]:
 (P/'projects'/f'{name}.json').write_text(canonical_json(value)+'\n')
checks={'schema':'rowan07-editor-replay-receipt/v1','initial_project_sha256':project_hash(initial),'final_project_sha256':finalhash,'actual_guarded_transactions':1,'target_cel':'rowan-se-07','full_canvas_candidate_precondition':True,'literal_owner_mask_pixels':len(coords),'actual_changed_RGBA_pixels':int(np.any(np.array(candidate)!=np.array(Image.open(P/'inputs/A/07.png').convert('RGBA')),axis=2).sum()),'exact_all8_RGBA':True,'unchanged_other7_png_bytes':True,'journal_replay_exact':True,'undo_to_initial_exact':True,'redo_to_final_exact':True,'outside_mask_candidate_rejected':rejected,'stale_project_precondition_rejected_atomically':badpre,'no_canvas_or_timing_or_pivot_changes':True,'external_GUI_editor_tested':False,'game_runtime_tested':False}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
