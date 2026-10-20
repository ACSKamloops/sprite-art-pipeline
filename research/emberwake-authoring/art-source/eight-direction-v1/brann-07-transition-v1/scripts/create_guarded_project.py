"""Exact actualtwo guarded transactions: inspected07return and2pixel03underpaint. No new painting."""
from pathlib import Path
import copy,json
import numpy as np
from PIL import Image
from sprite_lab import History,candidate_transaction,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def im(n):return Image.open(R/n).convert('RGBA')
palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
for i in range(8):
 for f in [f'inputs/control/{i:02}.png',f'frames/{i:02}.png']:
  for c in im(f).get_flattened_data():
   if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'FrozenBrann new03base plus exact07return andliteral2pixel03underpaint','locked':False}],'cels':{f'brann-se-{i:02}':{'layer_id':'paint','pixels':[lookup[c] for c in im(f'inputs/control/{i:02}.png').get_flattened_data()]} for i in range(8)},'frames':[{'id':f'brann-se-{i:02}','duration_ticks':9,'cels':{'paint':f'brann-se-{i:02}'},'landmarks':{'pivot':[64,112]}} for i in range(8)],'animations':[{'id':'walk','frames':[f'brann-se-{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'base':'inputs/control/00..07.png','07source_recipe':'RECIPE.json','07source_map':'maps/07-newP-source00.npz','03seam_witnesses':'03-UNDERPAINT-JOURNAL.json','status':'Parent-inspected exact07return plus explicit03two-pixelunderpaint;pendingreview,no whole-cycle acceptance.'}}
h=History(initial);txs=[];counts={}
for i,reason in [(3,'Only2named03partialalpha join pixels receive actual00darkcuff underpaint behind preservedfront'),(7,'Exact parent-inspected07lower shorter projectedPreturn;Qretains distinctbentbacksurface,actualupper fixed')]:
 before=np.array(im(f'inputs/control/{i:02}.png'));after=np.array(im(f'frames/{i:02}.png'));diff=np.any(before!=after,axis=-1);coords=[[int(x),int(y)] for y,x in np.argwhere(diff)];counts[str(i)]=len(coords);tx=candidate_transaction(h.project,f'brann-se-{i:02}',im(f'frames/{i:02}.png'),coords,reason=reason);h.apply(tx);txs.append(tx)
final=copy.deepcopy(h.project);finalhash=project_hash(final);beforeguard=project_hash(h.project);guard={}
try:h.apply(txs[0]);raise AssertionError('staleguard failed')
except Exception as e:
 assert str(e)!='staleguard failed';assert project_hash(h.project)==beforeguard;guard['stale_project_transaction']={'rejected':True,'atomic_no_mutation':True,'error':str(e)}
# A candidate withone unowned change must be rejected before any transaction canbeapplied.
bad=im('frames/03.png').copy();bad.putpixel((0,0),(1,1,1,255))
try:candidate_transaction(h.project,'brann-se-03',bad,[[67,96],[68,97]],reason='guardprobeonly');raise AssertionError('outsideguard failed')
except Exception as e:
 assert str(e)!='outsideguard failed';assert project_hash(h.project)==beforeguard;guard['outside_literal_seam_owner']={'rejected':True,'atomic_no_mutation':True,'error':str(e)}
h.undo();h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==finalhash
for i in range(8):assert render_cel(h.project,f'brann-se-{i:02}').tobytes()==im(f'frames/{i:02}.png').tobytes()
for name,obj in [('initial',initial),('final',final),('journal',h.journal())]:(R/'projects'/f'{name}.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
receipt={'actual_guarded_transactions':len(h.journal()['receipts']),'changed_RGBA_coordinates':counts,'actual_undo2_redo2':True,'all8RGBA_exact':True,'guards':guard,'initial_project_sha256':project_hash(initial),'final_project_sha256':finalhash,'palette_RGBA_entries':len(palette),'new07pixels_after_inspection':0,'03underpaint_pixels':2,'hold':[9,160],'cycle':[9,20]};(R/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
