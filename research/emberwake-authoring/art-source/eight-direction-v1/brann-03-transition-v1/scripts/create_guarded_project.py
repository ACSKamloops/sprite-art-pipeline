"""One actual guarded edit transaction for the exact parent-inspected Brann03; no new paint."""
from pathlib import Path
import copy,json
import numpy as np
from PIL import Image
from sprite_lab import History,candidate_transaction,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def im(n):return Image.open(R/n).convert('RGBA')
palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
for i in range(8):
 for path in [f'inputs/control/{i:02}.png',f'frames/{i:02}.png']:
  for rgba in im(path).get_flattened_data():
   if rgba not in lookup:lookup[rgba]=len(palette);palette.append(list(rgba))
project={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen Brann SEthree-pose base with only03lower transition trial','locked':False}],'cels':{f'brann-se-{i:02}':{'layer_id':'paint','pixels':[lookup[c] for c in im(f'inputs/control/{i:02}.png').get_flattened_data()]} for i in range(8)},'frames':[{'id':f'brann-se-{i:02}','duration_ticks':9,'cels':{'paint':f'brann-se-{i:02}'},'landmarks':{'pivot':[64,112]}} for i in range(8)],'animations':[{'id':'walk','frames':[f'brann-se-{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'base':'inputs/control/00..07.png','03trial':'RECIPE.json','source_map':'maps/03-newQ-source00.npz','status':'Exact parent-inspected03only trial, pending changed-art review. No whole-cycle acceptance.'}}
initial=copy.deepcopy(project);history=History(initial);base=im('inputs/control/03.png');candidate=im('frames/03.png');changed=np.any(np.array(candidate)!=np.array(base),axis=-1);coords=[[int(x),int(y)] for y,x in np.argwhere(changed)]
tx=candidate_transaction(history.project,'brann-se-03',candidate,coords,reason='Only inspected03lower Qcuff/boot projected source surface transition, preserveactualupper andallother7exact')
history.apply(tx);final=copy.deepcopy(history.project);final_hash=project_hash(final);history.undo();assert project_hash(history.project)==project_hash(initial);history.redo();assert project_hash(history.project)==final_hash
for i in range(8):assert render_cel(history.project,f'brann-se-{i:02}').tobytes()==im(f'frames/{i:02}.png').tobytes()
for name,obj in [('initial',initial),('final',final),('journal',history.journal())]:(R/'projects'/f'{name}.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
receipt={'actual_guarded_transactions':len(history.journal()['receipts']),'changed_coordinates':len(coords),'actual_undo_redo':True,'all8RGBA_exact':True,'initial_project_sha256':project_hash(initial),'final_project_sha256':final_hash,'palette_RGBA_entries':len(palette),'no_new_paint':True,'hold':[9,160],'cycle':[9,20]};(R/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
