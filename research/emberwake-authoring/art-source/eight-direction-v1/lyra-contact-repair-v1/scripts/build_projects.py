from pathlib import Path
import json,hashlib,copy
from PIL import Image
import numpy as np
from sprite_lab import canonical_json,History,project_hash,candidate_transaction,render_cel,EditError
P=Path(__file__).resolve().parents[1]
def im(n):return Image.open(P/n).convert('RGBA')
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
expected={3:'3aa39d61d900e563555f2e6dfd99bf24478ac2535e185ca59ba5dd903664de32',4:'af8109e3810036d90f476658bc52c2f5cf7ef8011fd4c6409b86dbae17d83eac'}
for i,h in expected.items():assert sha(f'candidate/{i:02}.png')==h
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i in range(8):
 pixels=[]
 for c in im(f'inputs/A/{i:02}.png').getdata():
  if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
  pixels.append(lookup[c])
 cel=f'lyra-se-{i:02}';cels[cel]={'layer_id':'paint','pixels':pixels};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Original coherent LyraSE cels;03/04 guarded source-pixel replacement only','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'lyra-SE-walk','frames':[f'{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'scope':'New authored03/04 source-pixel layout; no generation, mirroring, whole-pose fit or recovered hidden anatomy','source_bank_sha256':[sha(f'inputs/A/{i:02}.png') for i in range(8)],'candidate03_04_sha256':{str(i):v for i,v in expected.items()},'visible_donor_status':'inputs/VISIBLE-DONOR-STATUS.json','pose_roles_and_maps':'POSE-ROLES.json; maps/control-meshes.json','source02_hip_underpaint_pixels_per_changed_cel':138,'source_over_partial_alpha_joins':{'03':5,'04':0},'unchanged_endpoint05':True,'generation_calls':0,'inherited_quality_score':None,'editor_layers':'Complete raster cels; source-part layers retained separately; no hidden rig claim','selection':'unselected candidate pending independent comparison'}}
h=History(initial);transactions=[]
for phase in [3,4]:
 allowed=np.array(Image.open(P/'masks'/f'{phase:02}-repair-owner.png').convert('L'))>0;gloves=np.array(Image.open(P/'masks'/f'{phase:02}-full-visible-gloves-owner.png').convert('L'))>0;allowed&=~gloves;Image.fromarray(allowed.astype('uint8')*255).save(P/'masks'/f'{phase:02}-editor-allowed-owner.png');coords=[[int(x),int(y)] for y,x in np.argwhere(allowed)]
 tx=candidate_transaction(h.project,f'lyra-se-{phase:02}',im(f'candidate/{phase:02}.png'),coords,reason=f'Import inspected LyraSE{phase:02} source-painted contact/passing repair through literal lower mask; preserve original full upper/hem/gloves and all other cels')
 receipt=h.apply(tx);transactions.append((phase,tx,receipt))
final=copy.deepcopy(h.project);journal=h.journal();endhash=project_hash(final)
for i in range(8):assert render_cel(final,f'lyra-se-{i:02}').tobytes()==im(f'candidate/{i:02}.png').tobytes()
h.undo();h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==endhash;assert project_hash(History.replay(initial,journal).project)==endhash
# Exercise the actual candidate import boundary and transaction preconditions, preserving state on rejection.
bad=im('candidate/03.png');c=bad.getpixel((64,40));bad.putpixel((64,40),((c[0]+1)%256,*c[1:]));allowed=np.array(Image.open(P/'masks/03-editor-allowed-owner.png').convert('L'))>0;coords=[[int(x),int(y)] for y,x in np.argwhere(allowed)];outside=False
try:candidate_transaction(initial,'lyra-se-03',bad,coords)
except EditError:outside=True
assert outside
badtx=copy.deepcopy(transactions[0][1]);badtx['expected_project_sha256']='0'*64;before=project_hash(h.project);stale=False
try:h.apply(badtx)
except EditError:stale=True
assert stale and project_hash(h.project)==before
for value,name in [(initial,'initial'),(final,'final'),(journal,'journal')]:
 (P/'projects'/f'{name}.json').write_text(canonical_json(value)+'\n')
for phase,tx,receipt in transactions:
 (P/'projects'/f'{phase:02}-transaction.json').write_text(canonical_json(tx)+'\n');(P/'projects'/f'{phase:02}-transaction-receipt.json').write_text(canonical_json(receipt)+'\n')
receipt={'status':'PASS two actual guarded editor imports and journal replay','initial_project_sha256':project_hash(initial),'final_project_sha256':endhash,'actual_guarded_transactions':2,'candidate03_04_sha256':{str(i):v for i,v in expected.items()},'all8_RGBA_exact':True,'other6_original_PNG_bytes_exact':True,'each_original_full_upper_hem_gloves_RGBA_exact':True,'two_step_undo_redo_exact':True,'journal_replay_exact':True,'outside_mask_candidate_rejected':outside,'stale_project_precondition_rejected_atomically':stale,'generation_calls':0,'inherited_quality_score':None,'external_GUI_tested':False,'game_runtime_tested':False}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
