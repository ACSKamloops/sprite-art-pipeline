from pathlib import Path
import json,hashlib,copy
import numpy as np
from PIL import Image
from sprite_lab import History,canonical_json,project_hash,candidate_transaction,render_cel,EditError
P=Path(__file__).resolve().parents[1]
def im(n):return Image.open(P/n).convert('RGBA')
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
expected='9b62df0f5faf9bb22a2e8c1e4bdddf9c3f359ad5fbaa01bd6a1348d0b796a618';assert sha('candidate/07.png')==expected
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i in range(8):
 indices=[]
 for c in im(f'inputs/cycle/{i:02}.png').getdata():
  if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
  indices.append(lookup[c])
 cel=f'rowan-se-{i:02}';cels[cel]={'layer_id':'paint','pixels':indices};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Actual combined-cycle-v2 cels; one guarded source-leg07 replacement','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'rowan-SE-walk','frames':[f'{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'scope':'ONE new authored07 transition from visible source06 leg paint and actual source07 hip underpaint; no recovered hidden anatomy','incoming_cycle_sha256':[sha(f'inputs/cycle/{i:02}.png') for i in range(8)],'candidate07_sha256':expected,'source06_sha256':sha('inputs/source06.png'),'source07_sha256':sha('inputs/original07.png'),'hip_underpaint_pixels':117,'generated07_lower_paint_used':False,'generation_calls':0,'source_composition':'maps/COMPOSITION.json','approval':'Unselected pending fresh comparison; producer preview inspected by root','layer_claim':'Complete painted raster cels; deformed source surfaces are authored layout, not a recovered rig'}}
repair=np.array(Image.open(P/'masks/07-lower-repair-owner.png').convert('L'))>0;gloves=np.array(Image.open(P/'inputs/masks/07-opaque-gloves-protected.png').convert('L'))>0;allowed=repair&~gloves;Image.fromarray(allowed.astype('uint8')*255).save(P/'masks/07-editor-allowed-owner.png');coords=[[int(x),int(y)] for y,x in np.argwhere(allowed)]
tx=candidate_transaction(initial,'rowan-se-07',im('candidate/07.png'),coords,reason='Import exact inspected newly authored source-leg07 transition: visible source06 bent trousers/cuff mapped toward00, whole rounded source boots and117 source07 hip-underpaint pixels; stable upper/hem/gloves and other7cels fixed')
h=History(initial);receipt=h.apply(tx);final=copy.deepcopy(h.project);journal=h.journal()
for i in range(8):assert render_cel(final,f'rowan-se-{i:02}').tobytes()==im(f'candidate/{i:02}.png').tobytes()
finalhash=project_hash(final);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash;assert project_hash(History.replay(initial,journal).project)==finalhash
bad=im('candidate/07.png');c=bad.getpixel((64,40));bad.putpixel((64,40),((c[0]+1)%256,*c[1:]));outside=False
try:candidate_transaction(initial,'rowan-se-07',bad,coords)
except EditError:outside=True
assert outside
badtx=copy.deepcopy(tx);badtx['expected_project_sha256']='0'*64;before=project_hash(h.project);stale=False
try:h.apply(badtx)
except EditError:stale=True
assert stale and project_hash(h.project)==before
for value,name in [(initial,'initial'),(final,'final'),(tx,'transaction'),(receipt,'transaction-receipt'),(journal,'journal')]:
 (P/'projects'/f'{name}.json').write_text(canonical_json(value)+'\n')
report={'status':'PASS actual guarded editor import and journal','candidate07_sha256':expected,'initial_project_sha256':project_hash(initial),'final_project_sha256':finalhash,'actual_guarded_transactions':1,'all8_RGBA_exact':True,'undo_redo_exact':True,'journal_replay_exact':True,'outside_mask_candidate_rejected':outside,'stale_precondition_rejected_atomically':stale,'stable_upper_hem_and_opaque_gloves_excluded_from_editor_owner':True,'hidden_anatomy_recovered':False,'external_GUI_tested':False,'game_runtime_tested':False,'art_selection':'unselected pending fresh comparison'}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
