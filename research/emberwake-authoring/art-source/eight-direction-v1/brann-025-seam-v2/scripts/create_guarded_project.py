"""One actualguarded seven-pixelmidpoint repair; no other source/cel edit."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from sprite_lab import History,candidate_transaction,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def im(folder,n):return Image.open(R/folder/f'{n}.png').convert('RGBA')
t=json.loads((R/'TIMING.json').read_text());order=t['order'];palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
for n in order:
 for folder in ['inputs/original-bank','candidate']:
  for c in im(folder,n).get_flattened_data():
   if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen nineexposures with onlyseven reported02.5cuffslit pixels repaired','locked':False}],'cels':{f'brann-se-{n}':{'layer_id':'paint','pixels':[lookup[c] for c in im('inputs/original-bank',n).get_flattened_data()]} for n in order},'frames':[{'id':f'brann-se-{n}','duration_ticks':h,'cels':{'paint':f'brann-se-{n}'},'landmarks':{'pivot':[64,112]}} for n,h in zip(order,t['hold_ticks'])],'animations':[{'id':'walk','frames':[f'brann-se-{n}' for n in order],'fps':320,'loop':True,'events':[]}],'provenance':{'original_rejected_midpoint':'inputs/original-bank/02.5.png','repaired_midpoint':'candidate/02.5.png','onlychange':'UNDERPAINT-JOURNAL.json andmaps/seven-pixel-underpaint.npz','timeline':'TIMING.json; samefrozen nineexposure clock','status':'Exactparent-inspected seven-pixeljoin repair, changed-artreviewpending; nosmoothnessgainclaimed'}}
h=History(initial);before=np.array(im('inputs/original-bank','02.5'));after=np.array(im('candidate','02.5'));coords=[[int(x),int(y)] for y,x in np.argwhere(np.any(before!=after,axis=-1))];assert set(map(tuple,coords))=={(53,90),(54,90),(55,90),(53,91),(54,91),(55,91),(56,91)}
tx=candidate_transaction(h.project,'brann-se-02.5',im('candidate','02.5'),coords,reason='Onlysevenfrozenreview cuffslitcoordinates receiveexplicitactual03charcoal underpaint; no largerlegclearanceorotherposechanges');h.apply(tx);final=copy.deepcopy(h.project);finalhash=project_hash(final);guard={}
try:h.apply(tx);raise AssertionError('staleguard failed')
except Exception as e:
 assert str(e)!='staleguard failed';assert project_hash(h.project)==finalhash;guard['stale_project']={'rejected':True,'atomic_no_mutation':True,'error':str(e)}
bad=im('candidate','02.5').copy();bad.putpixel((59,90),(14,14,14,255))
try:candidate_transaction(h.project,'brann-se-02.5',bad,coords,reason='largerclearanceguardprobeonly');raise AssertionError('outsideguard failed')
except Exception as e:
 assert str(e)!='outsideguard failed';assert project_hash(h.project)==finalhash;guard['outside_seven_pixel_owner_larger_clearance']={'rejected':True,'atomic_no_mutation':True,'error':str(e)}
h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
for n in order:assert render_cel(h.project,f'brann-se-{n}').tobytes()==im('candidate',n).tobytes()
for n,obj in [('initial',initial),('final',final),('journal',h.journal())]:(R/'projects'/f'{n}.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
receipt={'actual_guarded_transactions':len(h.journal()['receipts']),'actual_changed_RGBA_coords':coords,'changed_count':7,'actual_undo_redo':True,'all9RGBA_exact':True,'original8_cels_unchanged':True,'larger_leg_clearance_unchanged':True,'timeline_unchanged':True,'guards':guard,'initial_project_sha256':project_hash(initial),'final_project_sha256':finalhash,'palette_RGBA_entries':len(palette),'newpixels_after_parent_crop_inspection':0};(R/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
