from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import History,render_frame,project_hash,validate_project

def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p))>0
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n')
def png(p,a):Image.fromarray(a.astype('uint8')).save(p)
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype('uint8')
recipe=json.loads((ROOT/'RECIPE.json').read_text());guide=json.loads((ROOT/'inputs/guide04-recipe.json').read_text());source=[arr(ROOT/'inputs/v5-frames'/f'{i:02}.png')for i in range(8)]
names=['base','cloth','rear','proximal','front'];allparts=[];records=[]
for i in range(8):
 layers={name:np.zeros((128,128,4),dtype='uint8')for name in names};layers['base']=source[i].copy()
 if i in [3,4,5]:
  upper=mask(ROOT/'masks'/f'{i:02}-whole-upper.png');layers['base'][~upper]=0
  if i==4:
   witnesses=guide['literal_trouser_source_witnesses'];boots=guide['boot_sources'];ids=[b['id']for b in boots]
   for w in witnesses:
    x,y=w['destination'];sx,sy=w['source'];c=source[0][sy,sx];assert c.tolist()==w['RGBA'];layers['cloth'][y,x]=c
   for b,name in zip(boots,['rear','front']):
    data=np.load(ROOT/'inputs/guide04-maps'/f'{b["id"]}.npz');xy=data['source_xy'];own=xy[:,:,0]>=0;ys,xs=np.where(own);part=layers[name];part[ys,xs]=source[0][xy[ys,xs,1],xy[ys,xs,0]];part[upper]=0
    np.savez_compressed(ROOT/'maps'/f'04-{b["id"]}.npz',source_xy=xy,source_rgba=source[0],source_owner_translation=b['translation'])
  else:
   witnesses=recipe['frames'][f'{i:02}']['literal_cloth_witnesses'];boots=recipe['frames'][f'{i:02}']['parts_in_back_to_front_order'];ids=[b['id']for b in boots]
   for w in witnesses:
    x,y=w['destination'];sx,sy=w['source'];c=source[w['source_phase']][sy,sx];assert c.tolist()==w['RGBA'];dest='proximal'if w['role'].startswith('literal rounded rear-thigh')else'cloth';layers[dest][y,x]=c
   for b,name in zip(boots,['rear','front']):
    data=np.load(ROOT/'maps'/f'{i:02}-{b["id"]}.npz');xy=data['source_xy'];own=xy[:,:,0]>=0;ys,xs=np.where(own);layers[name][ys,xs]=source[b['source_phase']][xy[ys,xs,1],xy[ys,xs,0]];layers[name][upper]=0
  for name in names[1:]:assert not (layers[name][upper]!=0).any()
  # Final source contribution respects real later opaque owners, rather
  # than calling every placed source pixel visible.
  for name,identity in zip(['rear','front'],ids):
   index=names.index(name);placed=layers[name][:,:,3]>0;opaque=np.zeros((128,128),bool);partial=np.zeros((128,128),bool)
   for later in names[index+1:]:opaque|=layers[later][:,:,3]==255;partial|=(layers[later][:,:,3]>0)&(layers[later][:,:,3]<255)
   contributes=placed&~opaque;Image.fromarray((contributes*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-{identity}-target-visible.png');Image.fromarray(((placed&opaque)*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-{identity}-opaque-later-occlusion.png')
   records.append({'phase':i,'part':identity,'positive_after_upper_occlusion':int(placed.sum()),'fully_occluded_by_later_part_pixels':int((placed&opaque).sum()),'positive_final_contribution_pixels':int(contributes.sum()),'partially_overlaid_pixels':int((placed&partial&~opaque).sum()),'part_layer':name,'later_owners':names[index+1:]})
  png(ROOT/'masks'/f'{i:02}-actual-change.png',np.repeat((np.any(arr(ROOT/'frames'/f'{i:02}.png')!=source[i],axis=2)*255).astype('uint8')[:,:,None],4,axis=2))
 rendered=np.zeros((128,128,4),dtype='uint8')
 for name in names:
  png(ROOT/'layers'/f'editor-{i:02}-{name}.png',layers[name]);rendered=over(rendered,layers[name])
 assert np.array_equal(rendered,arr(ROOT/'frames'/f'{i:02}.png')),(i,np.argwhere(np.any(rendered!=arr(ROOT/'frames'/f'{i:02}.png'),axis=2)).tolist()[:10])
 allparts.append(layers)
# Actual palette contains every layer pixel color; no quantization.
colors={(0,0,0,0)}
for a in source:colors.update(map(tuple,a.reshape(-1,4).tolist()))
for layers in allparts:
 for a in layers.values():colors.update(map(tuple,a.reshape(-1,4).tolist()))
palette=[[0,0,0,0]]+[list(c)for c in sorted(colors-{(0,0,0,0)})];lookup={tuple(c):j for j,c in enumerate(palette)}
def indexed(a):return[lookup[tuple(c)]for c in a.reshape(-1,4).tolist()]
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':n,'name':{'base':'Exact v5 frame authority with explicit lower erasure','cloth':'Literal source-color authored charcoal joins','rear':'Complete visible rear boot/leg source surface','proximal':'Literal source06 rear thigh occlusion','front':'Complete visible passing/foreground source surface'}[n],'locked':False}for n in names],'cels':{},'frames':[],'animations':[{'id':'walk','frames':[f'f{i}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'status':'unselected three-pose source-pixel candidate','scope':'OnlySE03/04/05 lower repair; v5 full upper and endpoints00/01/02/06/07 exact','model_calls':0,'boot03_projection':'Source07 screen-right visible boot, x translation-17, vertical5/6 about source_y93 -> target_y91; nearest sampling. Not an unscaled source-perfect boot.'}}
for i in range(8):
 initial['frames'].append({'id':f'f{i}','duration_ticks':9,'cels':{n:f'{n}{i}'for n in names},'landmarks':{}})
 for n in names:initial['cels'][f'{n}{i}']={'layer_id':n,'pixels':indexed(source[i])if n=='base'else[0]*16384}
validate_project(initial);history=History(initial)
for i in [3,4,5]:
 operations=[]
 for n in names:
  before=source[i]if n=='base'else np.zeros_like(source[i]);after=allparts[i][n];points=[[int(x),int(y),lookup[tuple(map(int,after[y,x]))]]for y,x in np.argwhere(np.any(before!=after,axis=2))]
  if points:operations.append({'op':'paint','cel_id':f'{n}{i}','points':points,'mask':[[x,y]for x,y,_ in points]})
 history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),'reason':f'OnlySE{i:02} lower owner: erase old lower, establish literal charcoal joins, source rear part, declared proximal occlusion, source complete front part. Full upper/arms excluded from every new owner. SeeRECIPE.json and actual XY maps.','operations':operations})
target=history.project;validate_project(target)
for i in range(8):assert render_frame(target,f'f{i}').tobytes()==Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
final=project_hash(target);journal=history.journal();replay=History.replay(initial,journal);assert project_hash(replay.project)==final
for _ in range(len(history.records)):history.undo()
assert project_hash(history.project)==project_hash(initial)
for _ in range(len(history.records)):history.redo()
assert project_hash(history.project)==final
save(ROOT/'initial-project.json',initial);save(ROOT/'project.json',target);save(ROOT/'journal.json',journal);save(ROOT/'OCCLUSION.json',records)
save(ROOT/'EDITOR-RECEIPT.json',{'status':'unselected candidate; no acceptance/contact claim','source_layer_PNG_recipe_exact':True,'actual_editor_journal_transactions':len(history.records),'all8_rendered_RGBA_exact':True,'undo_redo_replay_exact':True,'initial_project_sha256':project_hash(initial),'project_sha256':final,'full_v5_upper_arms_exact':True,'endpoint_PNG_bytes_exact':[0,1,2,6,7],'03_boot_vertical_projection':[5,6],'03_boot_unscaled_source_perfect':False,'model_calls':0})
print('PASS actual toolkit3 guarded transactions,8/8 layer render, exact undo/redo and journal replay.')
