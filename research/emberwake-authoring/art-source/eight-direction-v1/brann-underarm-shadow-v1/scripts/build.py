"""Bounded torso-edge underpaint trial. Not selected art; no model calls."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image,ImageDraw
from sprite_lab import History,project_hash,render_frame

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/home/astra/artifacts/emberwake-brann-full-lower-paint-v1/manual-loops-v3/se')
def save(path,data):path.write_text(json.dumps(data,separators=(',',':'))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['inputs','frames','masks','proof']:(ROOT/name).mkdir(exist_ok=True)
arrays=[]
for i in range(8):
 p=ROOT/'inputs'/f'{i:02}.png'
 if not p.exists():shutil.copyfile(SOURCE/f'{i:02}.png',p)
 arrays.append(np.array(Image.open(p).convert('RGBA')))
palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
for i,a in enumerate(arrays):
 pixels=[]
 for row in a.reshape(-1,4):
  rgba=tuple(map(int,row))
  if rgba not in lookup:lookup[rgba]=len(palette);palette.append(list(rgba))
  pixels.append(lookup[rgba])
 cid=f'se{i}';cels[cid]={'layer_id':'paint','pixels':pixels};frames.append({'id':cid,'duration_ticks':9,'cels':{'paint':cid},'landmarks':{}})
initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Unselected torso-edge shadow trial','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[f'se{i}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'model_calls':0,'status':'unselected bounded underpaint trial'}}
h=History(initial);records=[]
for i,a in enumerate(arrays):
 out=a.copy();points=[];witnesses=[]
 # Only bounded one-pixel internal channels. No outer silhouette expansion,
 # no filled elbow space wider than one native pixel, no trouser/boot changes.
 if i in (3,4,5):
  for lo,hi,yl,yh,donor_dx in [(46,55,62,81,1),(76,84,62,79,-1)]:
   for y in range(yl,yh):
    for x in range(lo,hi):
     if a[y,x,3]==0 and a[y,x-1,3]>128 and a[y,x+1,3]>128:
      donor=a[y,x+donor_dx]
      # Explicit torso side, existing edge shade; never invent a bright seam.
      if max(map(int,donor[:3]))>105:continue
      color=tuple(map(int,donor));out[y,x]=donor
      points.append([x,y,lookup[color]])
      witnesses.append({'destination':[x,y],'donor':[x+donor_dx,y],'rgba':list(color)})
 if points:
  h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'Trial existing same-cel dark torso-edge paint behind the moved whole forearm; close only explicit one-pixel internal channels, preserving other negative spaces','operations':[{'op':'paint','cel_id':f'se{i}','points':points,'mask':[[x,y]for x,y,_ in points]}]})
 diff=np.any(out!=a,axis=2);assert not diff[81:].any()
 Image.fromarray(out).save(ROOT/'frames'/f'{i:02}.png');Image.fromarray((diff*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}.png')
 assert render_frame(h.project,f'se{i}').tobytes()==out.tobytes()
 records.append({'phase':i,'actual_changed_pixels':int(diff.sum()),'literal_source_witnesses':witnesses,'source_sha256':sha(ROOT/'inputs'/f'{i:02}.png'),'output_sha256':sha(ROOT/'frames'/f'{i:02}.png')})
final_hash=project_hash(h.project);journal=h.journal();replayed=History.replay(initial,journal)
assert project_hash(replayed.project)==final_hash
for i in range(8):assert render_frame(replayed.project,f'se{i}').tobytes()==Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
for _ in range(len(h.records)):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(len(h.records)):h.redo()
assert project_hash(h.project)==final_hash
for name,obj in [('initial-project',initial),('project',h.project),('journal',journal),('EDITS',records)]:save(ROOT/f'{name}.json',obj)
sheet=Image.new('RGBA',(320*3,320*2),(235,232,219,255));d=ImageDraw.Draw(sheet)
for col,i in enumerate((3,4,5)):
 for row,sub in enumerate(('inputs','frames')):
  im=Image.open(ROOT/sub/f'{i:02}.png').crop((28,50,108,130)).resize((320,320),Image.Resampling.NEAREST)
  sheet.alpha_composite(im,(col*320,row*320));d.text((col*320+3,row*320+3),f'{sub} {i:02}',fill='black')
sheet.save(ROOT/'proof'/'before-after-4x.png')
save(ROOT/'REPLAY-RECEIPT.json',{'frames':8,'exact_RGBA':True,'actual_undo_redo':True,'journal_replay':True,'project_sha256':final_hash,'scope':'Unselected same-cel shadow-pixel trial; not recovered anatomy or art acceptance'})
print('8/8 guarded journal frames exact;',sum(r['actual_changed_pixels']for r in records),'source-owned pixels painted')
