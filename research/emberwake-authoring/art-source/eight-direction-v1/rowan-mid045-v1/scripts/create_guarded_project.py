"""Create the actual editor project/journal for the frozen inspected drawing; no new pixels."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,candidate_transaction,render_cel
R=Path(__file__).resolve().parents[1]
def image(n):return Image.open(R/'candidate'/f'{n}.png').convert('RGBA')
t=json.loads((R/'TIMING.json').read_text());order=t['candidate_order'];palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
for n in order:
 for color in image(n).get_flattened_data():
  if color not in lookup:lookup[color]=len(palette);palette.append(list(color))
def pixels(im):return [lookup[c] for c in im.get_flattened_data()]
cels={f'rowan-se-{n}':{'layer_id':'paint','pixels':pixels(image('04' if n=='04.5' else n))} for n in order}
project={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen best8 painted keys plus one projected midpoint04.5','locked':False}],'cels':cels,'frames':[{'id':f'rowan-se-{n}','duration_ticks':hold,'cels':{'paint':f'rowan-se-{n}'},'landmarks':{'pivot':[64,112]}} for n,hold in zip(order,t['candidate_holds'])],'animations':[{'id':'walk','frames':[f'rowan-se-{n}' for n in order],'fps':320,'loop':True,'events':[]}],'provenance':{'authority':'inputs/control/00..07.png','surface_projection':'CONSTRUCTION.json','inverse_source_map':'maps/04.5-sources.npz','timeline':'TIMING.json','art_status':'One parent-inspected midpoint, unselected whole-cycle trial. No inherited art acceptance.'}}
initial=copy.deepcopy(project);h=History(initial);candidate=image('04.5');changed=np.any(np.array(candidate)!=np.array(image('04')),axis=-1);coords=[[int(x),int(y)] for y,x in np.argwhere(changed)]
transaction=candidate_transaction(h.project,'rowan-se-04.5',candidate,coords,reason='Frozen one-drawing04.5 projected material surface midpoint from actual04/05paint; only04hold split, all original keys exact')
h.apply(transaction);final=copy.deepcopy(h.project);final_hash=project_hash(final);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final_hash
for n in order:assert render_cel(h.project,f'rowan-se-{n}').tobytes()==image(n).tobytes()
for name,obj in [('initial',initial),('final',final),('journal',h.journal())]:(R/'projects'/f'{name}.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
(R/'projects/EDITOR-RECEIPT.json').write_text(json.dumps({'actual_guarded_transactions':1,'actual_changed_RGBA_coordinates':len(coords),'expected_initial_project_sha256':project_hash(initial),'final_project_sha256':final_hash,'actual_undo_redo':True,'original8_cel_RGBA_exact':True,'new_midpoint_cel_RGBA_exact':True,'actual_source_palette_RGBA_entries':len(palette),'timeline_fps':320,'timeline_duration_ticks':sum(t['candidate_holds'])},indent=2)+'\n')
print('actualguarded journal, undo/redo and all9RGBA verified',len(coords),'changedcoords')
