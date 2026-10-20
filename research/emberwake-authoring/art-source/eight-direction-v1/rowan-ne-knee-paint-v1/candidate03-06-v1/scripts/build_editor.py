from pathlib import Path
import copy,json,hashlib
from PIL import Image
import numpy as np
from sprite_lab import canonical_json,History,project_hash,candidate_transaction,render_cel
P=Path(__file__).resolve().parents[1]
def im(n):return Image.open(P/n).convert('RGBA')
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
inputs=json.loads((P/'INPUTS.json').read_text());assert inputs['changed_phases']==[3,6]
for i in range(8):assert sha(f'frames/{i:02}.png')==inputs['candidate_PNG_sha256'][f'{i:02}']
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i in range(8):
 pixels=[]
 for c in im(f'inputs/source-frames/{i:02}.png').get_flattened_data():
  if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
  pixels.append(lookup[c])
 cel=f'rowan-ne-{i:02}';cels[cel]={'layer_id':'paint','pixels':pixels};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Original RowanNE cels; guarded03/06 cream paint only','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'rowan-NE-walk','frames':[f'{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'status':'approved for independent changed-art review, not art acceptance','changed_phases':[3,6],'original_PNG_byte_phases':[0,1,2,4,5,7],'scope':'Frozen03/06 cloth owners only; source upper/hem/gloves/whole boots and negative space exact','source_bank_PNG_sha256':inputs['source_PNG_sha256'],'candidate_PNG_sha256':inputs['candidate_PNG_sha256'],'actual_raw1254_sha256':inputs['raw_sha256'],'normalization':'One whole1254→256nearest, fixed4cells; no per-pose fitting or later alpha/paint/mask normalization','root_built_in_generation_calls_in_provenance':1,'packaging_lane_model_calls':0,'rejected04':'Retained; protected goldV/new shadow seam not stronger','unimported05':'Raw crossing cuff material extends2rows; source05 retained','quality_score':None,'editor_layers':'Complete raster cels; frozen sourceXY/masks retained separately'}}
h=History(initial);transactions=[]
for i in [3,6]:
 allowed=np.array(Image.open(P/f'inputs/owners/{i:02}-allowed-trouser-knee-cuff.png').convert('L'))>0;coords=[[int(x),int(y)]for y,x in np.argwhere(allowed)]
 tx=candidate_transaction(h.project,f'rowan-ne-{i:02}',im(f'frames/{i:02}.png'),coords,reason=f'Import exact root-inspected RowanNE{i:02} cream paint from actual raw shared normalization through frozen owner; preserve original upper/hem/full gloves/whole boots/negative space and other cels')
 receipt=h.apply(tx);transactions.append((i,tx,receipt))
final=copy.deepcopy(h.project);journal=h.journal();end=project_hash(final)
for i in range(8):assert render_cel(final,f'rowan-ne-{i:02}').tobytes()==im(f'frames/{i:02}.png').tobytes()
for _ in transactions:h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in transactions:h.redo()
assert project_hash(h.project)==end;assert project_hash(History.replay(initial,journal).project)==end
for value,name in [(initial,'initial'),(final,'final'),(journal,'journal')]: (P/f'projects/{name}.json').write_text(canonical_json(value)+'\n')
for i,tx,receipt in transactions:
 (P/f'projects/{i:02}-transaction.json').write_text(canonical_json(tx)+'\n');(P/f'projects/{i:02}-transaction-receipt.json').write_text(canonical_json(receipt)+'\n')
r={'status':'PASS two actual guarded imports; independent art review pending','actual_guarded_transactions':2,'initial_project_canonical_sha256':project_hash(initial),'final_project_canonical_sha256':end,'all8_RGBA_exact':True,'undo_redo_journal_exact':True,'changed_phases':[3,6],'original04_05_and_other4_exact':True,'upper_whole_boots_and_outside_owner_exact':True,'project_storage':'minified canonical JSON plus trailing newline','external_GUI_runtime_tested':False,'new_model_calls':0}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
