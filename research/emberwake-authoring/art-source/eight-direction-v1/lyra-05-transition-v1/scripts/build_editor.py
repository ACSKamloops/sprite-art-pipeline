from pathlib import Path
import copy,json,hashlib
from PIL import Image
import numpy as np
from sprite_lab import canonical_json,History,project_hash,candidate_transaction,render_cel,EditError
P=Path(__file__).resolve().parents[1]
FROZEN='ae2aef07754fb69429f11b04f84b035d3e6cc621324dd0a40704b2ae7beff6f7'
def im(n):return Image.open(P/n).convert('RGBA')
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
assert sha('candidate/05.png')==FROZEN
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i in range(8):
 pixels=[]
 for c in im(f'inputs/cycle/{i:02}.png').getdata():
  if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
  pixels.append(lookup[c])
 cel=f'lyra-se-{i:02}';cels[cel]={'layer_id':'paint','pixels':pixels};frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'paint':cel},'landmarks':{'pivot':[64,112]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen LyraSE cycle; one guarded05 lower import','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'lyra-SE-walk','frames':[f'{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'status':'unselected candidate; no inherited score','scope':'Only05 lower; exact existing03/04 and other7; actual05 upper/hem/full gloves protected','source_bank_PNG_sha256':[sha(f'inputs/cycle/{i:02}.png')for i in range(8)],'frozen05_PNG_sha256':FROZEN,'construction':'RECIPE.json; maps/; layers/; masks/; source visible texels and bounded authored projections, no recovered hidden anatomy','editor_layers':'Complete raster cels; source-part layers retained separately','model_calls':0,'quality_acceptance':False}}
allowed=np.array(Image.open(P/'masks/05-repair-owner.png').convert('L'))>0;coords=[[int(x),int(y)]for y,x in np.argwhere(allowed)]
h=History(initial);tx=candidate_transaction(initial,'lyra-se-05',im('candidate/05.png'),coords,reason='Import exact root-inspected ae2aef Lyra05 lower source-pixel transition; preserve all seven other cels and original05 upper/hem/full gloves')
receipt=h.apply(tx);final=copy.deepcopy(h.project);journal=h.journal();end=project_hash(final)
for i in range(8):assert render_cel(final,f'lyra-se-{i:02}').tobytes()==im(f'candidate/{i:02}.png').tobytes()
h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==end;assert project_hash(History.replay(initial,journal).project)==end
for value,name in [(initial,'initial'),(final,'final'),(journal,'journal'),(tx,'05-transaction'),(receipt,'05-transaction-receipt')]:
 (P/'projects'/f'{name}.json').write_text(canonical_json(value)+'\n')
r={'status':'PASS actual one guarded candidate import, all8RGBA, undo/redo/journal replay; unselected art','actual_transactions':1,'initial_project_canonical_sha256':project_hash(initial),'final_project_canonical_sha256':end,'candidate05_PNG_sha256':FROZEN,'all8RGBA_exact':True,'other7PNG_bytes_exact':True,'actual05_protected_RGBA_exact':True,'undo_redo_exact':True,'journal_replay_exact':True,'JSON_format':'Canonical minified, one trailing newline','external_GUI_tested':False,'runtime_tested':False,'model_calls':0,'inherited_score':None}
(P/'projects/EDITOR-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
