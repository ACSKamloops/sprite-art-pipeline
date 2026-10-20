from pathlib import Path
import copy,json,sys,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import History,project_hash,render_frame,render_cel
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
donors=json.loads((ROOT/'DONORS.json').read_text());sources=json.loads((ROOT/'INPUTS.json').read_text())
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for d in donors:
    a=np.array(Image.open(ROOT/d['cutout']).convert('RGBA'))
    for c in a.reshape(-1,4):
        key=tuple(map(int,c))
        if key not in lookup:lookup[key]=len(palette);palette.append(list(key))
for source in sources:
    fid=f'{source["actor"]}-{source["view"]}-{source["phase"]:02}';bindings={}
    for side in ['left','right']:
        cid=f'{fid}-{side}';cels[cid]={'layer_id':side,'pixels':[0]*16384};bindings[side]=cid
    frames.append({'id':fid,'duration_ticks':1,'cels':bindings,'landmarks':{'source_pixel_origin':[0,0]}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[0,0],'ground_pivot':[0,0]},'palette':palette,'layers':[{'id':'left','name':'Screen-left visible source boot surface','locked':False},{'id':'right','name':'Screen-right visible source boot surface','locked':False}],'cels':cels,'frames':frames,'animations':[],'provenance':{'scope':'Static visible-boot inventory, not an animation or complete hidden anatomical rig','transform':'identity source/destination XY on original128stage','required_editor_pivots':'both0,0 mark inventory source origin only; no ground/contact assertion','model_calls':0}}
history=History(initial);records=[]
for source in sources:
    fid=f'{source["actor"]}-{source["view"]}-{source["phase"]:02}';operations=[]
    for side in ['left','right']:
        d=next(d for d in donors if d['actor']==source['actor']and d['view']==source['view']and d['phase']==source['phase']and d['screen_position']==side)
        a=np.array(Image.open(ROOT/d['cutout']).convert('RGBA'));ys,xs=np.where(a[:,:,3]>0);points=[[int(x),int(y),lookup[tuple(map(int,a[y,x]))]]for y,x in zip(ys,xs)]
        operations.append({'op':'paint','cel_id':f'{fid}-{side}','points':points,'mask':[[x,y]for x,y,_ in points]})
    history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),'reason':'Copy only hand-scoped literal visible boot source texels at identity source coordinates; no hidden anatomy, scale, fitting or animation','operations':operations})
for d in donors:
    fid=f'{d["actor"]}-{d["view"]}-{d["phase"]:02}';im=render_cel(history.project,f'{fid}-{d["screen_position"]}');assert im.tobytes()==Image.open(ROOT/d['cutout']).convert('RGBA').tobytes()
    records.append({'donor':d['id'],'source_texels_RGBA_exact':True,'editor_cel_RGBA_exact':True,'PNG_sha256':sha(ROOT/d['cutout'])})
final=project_hash(history.project);save(ROOT/'initial-project.json',initial);save(ROOT/'project.json',history.project);save(ROOT/'journal.json',history.journal())
replayed=History.replay(initial,history.journal());assert project_hash(replayed.project)==final
for d in donors:
    fid=f'{d["actor"]}-{d["view"]}-{d["phase"]:02}';assert render_cel(replayed.project,f'{fid}-{d["screen_position"]}').tobytes()==Image.open(ROOT/d['cutout']).convert('RGBA').tobytes()
for _ in range(len(history.records)):history.undo()
assert project_hash(history.project)==project_hash(initial)
for _ in range(len(history.records)):history.redo()
assert project_hash(history.project)==final
save(ROOT/'EDITOR-RECEIPT.json',{'canonical_project_sha256':final,'inventory_source_cels':15,'individual_visible_donors':30,'transactions':len(history.records),'literal_editor_cels':records,'actual_undo_redo_replay_exact':True,'animations':0,'pivots':'inventory source origin0,0; not game ground/contact anchors','art_status':'unselected visible source inventory; no full boot or gait approval'})
print('30/30 literal donor cels in15 static inventory frames; actual guarded journal undo/redo/replay exact.')
