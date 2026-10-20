from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image
from sprite_lab import canonical_json,History,project_hash,candidate_transaction,render_cel,EditError
P=Path(__file__).resolve().parents[1]
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
def image(n):return Image.open(P/n).convert('RGBA')
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
def color_index(c):
 if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
 return lookup[c]
for i in range(8):
 pixels=[color_index(c) for c in image(f'preview/control-frames/{i:02}.png').getdata()];cel=f'rowan-se-{i:02}';cels[cel]={'layer_id':'paint','pixels':pixels};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
# Unused source swatches are retained so each actual cuff stroke can use its literal source RGBA.
for c in image('inputs/A/07.png').getdata():color_index(c)
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Complete source-owned cels;07 source-boot replacement and bounded cuff finish','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'rowan-SE-walk','frames':[f'{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'scope':'No-generation07 boot-only hybrid; unselected pending fullcycle review','incoming07_sha256':sha('inputs/generated07.png'),'donor_old07_sha256':sha('inputs/A/07.png'),'final07_sha256':sha('proposal/07.png'),'whole_boot_native_translations':{'screen-left':[2,2],'screen-right':[0,-2]},'generated_cream_knee_upper_hem_gloves_exact':True,'preview_context':'Original03 and firstnew04; root owns combined direct03/hybrid04/hybrid07 review','generation_calls_in_this_package':0,'layers_claim':'Complete painted raster cels, not a recovered hidden rig'}}
repair=np.array(Image.open(P/'proposal/07-boot-repair-owner.png').convert('L'))>0;coords=[[int(x),int(y)] for y,x in np.argwhere(repair)]
h=History(initial);part_tx=candidate_transaction(initial,'rowan-se-07',image('proposal/07-before-cuff.png'),coords,reason='Replace generated07 boot paint with literal complete old07 source-boot owners at fixed native translations; retain generated cream knees and actual stable upper')
part_receipt=h.apply(part_tx);part_project=copy.deepcopy(h.project)
source=image('inputs/A/07.png');editfile=json.loads((P/'proposal/cuff-source-edits.json').read_text());points=[]
for row in editfile['actual_edits']:
 x,y=row['at'];sx,sy=row['source_at'];color=source.getpixel((sx,sy));idx=h.project['palette'].index(list(color));assert render_cel(h.project,'rowan-se-07').getpixel((x,y))[3]==0;points.append([x,y,idx])
cuff_tx={'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'Fill35 newly exposed alpha0 cuff gaps using literal old07 boot source texels; leave every pasted whole-boot texel and generated cream-knee pixel unchanged','operations':[{'op':'paint','cel_id':'rowan-se-07','mask':[[x,y] for x,y,_ in points],'points':points}]}
cuff_receipt=h.apply(cuff_tx);final=copy.deepcopy(h.project);journal=h.journal()
assert len(points)==35
for i in range(8):assert render_cel(final,f'rowan-se-{i:02}').tobytes()==image(f'preview/frames/{i:02}.png').tobytes()
endhash=project_hash(final);h.undo();assert project_hash(h.project)==project_hash(part_project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==endhash;assert project_hash(History.replay(initial,journal).project)==endhash
bad=image('proposal/07-before-cuff.png');c=bad.getpixel((64,40));bad.putpixel((64,40),((c[0]+1)%256,*c[1:]));outside=False
try:candidate_transaction(initial,'rowan-se-07',bad,coords)
except EditError:outside=True
assert outside
badtx=copy.deepcopy(cuff_tx);badtx['expected_project_sha256']='0'*64;before=project_hash(h.project);stale=False
try:h.apply(badtx)
except EditError:stale=True
assert stale and project_hash(h.project)==before
for value,name in [(initial,'initial'),(part_project,'after-parts'),(final,'final'),(part_tx,'part-transaction'),(cuff_tx,'cuff-transaction'),(journal,'journal'),(part_receipt,'part-receipt'),(cuff_receipt,'cuff-receipt')]:
 (P/'projects'/f'{name}.json').write_text(canonical_json(value)+'\n')
receipt={'status':'PASS actual guarded part import plus literal source-colored cuff edit journal','initial_project_sha256':project_hash(initial),'after_parts_project_sha256':project_hash(part_project),'final_project_sha256':endhash,'actual_guarded_transactions':2,'literal_cuff_stroke_pixels':35,'final07_sha256':sha('proposal/07.png'),'exact_all8_RGBA':True,'journal_replay_exact':True,'two_step_undo_redo_exact':True,'outside_mask_candidate_rejected':outside,'stale_precondition_rejected_atomically':stale,'no_clock_stage_pivot_changes':True,'external_GUI_tested':False,'runtime_tested':False,'art_approval':'unselected pending parent fullcycle review'}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
