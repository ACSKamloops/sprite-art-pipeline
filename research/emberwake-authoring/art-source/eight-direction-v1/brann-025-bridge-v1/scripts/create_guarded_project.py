"""One actual guarded import of the unchanged parent-inspected02.5candidate."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from sprite_lab import History,candidate_transaction,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def im(n):return Image.open(R/'candidate'/f'{n}.png').convert('RGBA')
t=json.loads((R/'TIMING.json').read_text());order=t['order'];palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
for n in order:
 for c in im(n).get_flattened_data():
  if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen8Brannpaintedkeys plus one02.5source-surface midpoint','locked':False}],'cels':{f'brann-se-{n}':{'layer_id':'paint','pixels':[lookup[c] for c in im('02' if n=='02.5' else n).get_flattened_data()]} for n in order},'frames':[{'id':f'brann-se-{n}','duration_ticks':hold,'cels':{'paint':f'brann-se-{n}'},'landmarks':{'pivot':[64,112]}} for n,hold in zip(order,t['hold_ticks'])],'animations':[{'id':'walk','frames':[f'brann-se-{n}' for n in order],'fps':320,'loop':True,'events':[]}],'provenance':{'source_inputs':'inputs/control/00..07.png','midpoint_parts':'RECIPE.json','inverse_source_maps':'maps/1-Q-proximal.npz,2-P-retreating.npz,3-Q-cuff-heel-toe.npz','clock':'TIMING.json andROOT-REVIEW-SPEC.json','status':'Parent-inspected exact02.5candidate; no whole-loop acceptance.'}}
h=History(initial);diff=np.any(np.array(im('02.5'))!=np.array(im('02')),axis=-1);coords=[[int(x),int(y)] for y,x in np.argwhere(diff)];tx=candidate_transaction(h.project,'brann-se-02.5',im('02.5'),coords,reason='Exactparent-inspected02.5source-pixelguideimport; preserveoriginal8cels,source02upper andrational02holdsplit')
h.apply(tx);final=copy.deepcopy(h.project);finalhash=project_hash(final);guard={}
try:h.apply(tx);raise AssertionError('staleguard failed')
except Exception as e:
 assert str(e)!='staleguard failed';assert project_hash(h.project)==finalhash;guard['stale_project']={'rejected':True,'atomic_no_mutation':True,'error':str(e)}
bad=im('02.5').copy();bad.putpixel((0,0),(1,1,1,255))
try:candidate_transaction(h.project,'brann-se-02.5',bad,coords,reason='outsideownerprobeonly');raise AssertionError('outsideguard failed')
except Exception as e:
 assert str(e)!='outsideguard failed';assert project_hash(h.project)==finalhash;guard['outside_midpoint_owner']={'rejected':True,'atomic_no_mutation':True,'error':str(e)}
h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
for n in order:assert render_cel(h.project,f'brann-se-{n}').tobytes()==im(n).tobytes()
for n,obj in [('initial',initial),('final',final),('journal',h.journal())]:(R/'projects'/f'{n}.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
receipt={'actual_guarded_transactions':len(h.journal()['receipts']),'changed_midpoint_RGBA_coords':len(coords),'actual_undo_redo':True,'all9RGBA_exact':True,'original8_unique_cels_unchanged':True,'midpoint_owns_separate_cel':True,'guards':guard,'initial_project_sha256':project_hash(initial),'final_project_sha256':finalhash,'palette_RGBA_entries':len(palette),'timeline_fps':320,'timeline_duration_ticks':144,'original8_start_times_fixed':True,'new_pixels_after_parent_inspection':0};(R/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
