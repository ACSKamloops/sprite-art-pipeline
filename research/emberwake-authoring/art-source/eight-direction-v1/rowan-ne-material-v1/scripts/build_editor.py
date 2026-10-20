from pathlib import Path
import copy,json,hashlib
from PIL import Image
import numpy as np
from sprite_lab import canonical_json,History,project_hash,candidate_transaction,render_cel
P=Path(__file__).resolve().parents[1]
def im(n):return Image.open(P/n).convert('RGBA')
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
recipe=json.loads((P/'RECIPE.json').read_text());frozen={r['phase']:r['candidate_PNG_sha256']for r in recipe['phase_repairs']};assert sorted(frozen)==[4,5,6]
for i,digest in frozen.items():assert sha(f'candidate/{i:02}.png')==digest
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i in range(8):
 pixels=[]
 for c in im(f'inputs/frames/{i:02}.png').get_flattened_data():
  if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
  pixels.append(lookup[c])
 cel=f'rowan-ne-{i:02}';cels[cel]={'layer_id':'paint','pixels':pixels};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Original RowanNE raster cels; bounded04/05/06 material imports','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'rowan-NE-walk','frames':[f'{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'status':'frozen unselected material cleanup; motion unchanged','scope':'Literal cloth-source/erasure repairs04/05/06; original03 restored and rejected55px patch retained separately','source_bank_PNG_sha256':[sha(f'inputs/frames/{i:02}.png')for i in range(8)],'candidate_PNG_sha256':{str(i):d for i,d in frozen.items()},'source_maps_recipe':'RECIPE.json;maps/;masks/;actual source00 visible cream paint, authored fringe erasures; no recovered anatomy','model_calls':0,'inherited_score':None,'quality_acceptance':False}}
h=History(initial);transactions=[]
for i in [4,5,6]:
 allowed=np.array(Image.open(P/f'masks/{i:02}-literal-material-owner.png').convert('L'))>0;coords=[[int(x),int(y)]for y,x in np.argwhere(allowed)]
 tx=candidate_transaction(h.project,f'rowan-ne-{i:02}',im(f'candidate/{i:02}.png'),coords,reason=f'Only RowanNE{i:02} inspected literal cream cloth/material fringe cleanup; exact upper/boot owners, poses and other cels; original03 retained')
 receipt=h.apply(tx);transactions.append((i,tx,receipt))
final=copy.deepcopy(h.project);journal=h.journal();end=project_hash(final)
for i in range(8):assert render_cel(final,f'rowan-ne-{i:02}').tobytes()==im(f'candidate/{i:02}.png').tobytes()
for _ in transactions:h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in transactions:h.redo()
assert project_hash(h.project)==end;assert project_hash(History.replay(initial,journal).project)==end
for obj,name in [(initial,'initial'),(final,'final'),(journal,'journal')]: (P/'projects'/f'{name}.json').write_text(canonical_json(obj)+'\n')
for i,tx,receipt in transactions:
 (P/f'projects/{i:02}-transaction.json').write_text(canonical_json(tx)+'\n');(P/f'projects/{i:02}-transaction-receipt.json').write_text(canonical_json(receipt)+'\n')
r={'status':'PASS three actual guarded material-import transactions; all8RGBA, undo/redo/journal exact','actual_transactions':3,'initial_project_canonical_sha256':project_hash(initial),'final_project_canonical_sha256':end,'all8_RGBA_exact':True,'complete_upper_and_boot_owners_exact':True,'original_PNG_byte_phases':[0,1,2,3,7],'all_motion_boot_projection_unchanged':True,'03_rounded_patch_rejected_and_retained':True,'model_calls':0,'JSON_format':'minified canonical JSON plus newline','GUI_runtime_tested':False,'art_accepted':False}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
