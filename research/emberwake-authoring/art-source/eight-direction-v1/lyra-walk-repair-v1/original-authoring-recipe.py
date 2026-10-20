from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys,importlib.util
R=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1');T=R/'editor-toolkit-v1';sys.path.insert(0,str(T))
from sprite_lab import History,project_hash,canonical_json,render_frame
s=importlib.util.spec_from_file_location('construct',T/'scripts/sprite_construct.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
B=Path('/home/astra/artifacts/emberwake-lyra-walk-pixel-repair-v1');S=B/'trial3';O=B/'material-repair-v3';O.mkdir(exist_ok=False)
arrays={(v,i):np.array(Image.open(S/v/f'{i:02}.png').convert('RGBA')) for v in ['southeast','northeast'] for i in range(8)}
w=[]
def copy_pixel(i,x,y,sx,sy,view='southeast'):
 a=arrays[(view,i)];old=a[y,x].copy();new=a[sy,sx].copy();assert new[3]>0;a[y,x]=new;w.append({'view':view,'frame':i,'xy':[x,y],'donor_xy':[sx,sy],'before':old.tolist(),'after':new.tolist(),'kind':'same-frame material copy'})
def erase(i,x,y,view='southeast'):
 a=arrays[(view,i)];old=a[y,x].copy();a[y,x]=0
 if old[3]:w.append({'view':view,'frame':i,'xy':[x,y],'before':old.tolist(),'after':[0,0,0,0],'kind':'literal spur erasure'})
# The interrupted material here is leather, NOT a new flat charcoal thigh block.
a=arrays[('southeast',1)]
for x in range(47,55):
 if a[84,x,3]<24:copy_pixel(1,x,84,x,83)
# Preserve the drawn cuff and boot texture, bridge only its three-row empty cut.
a=arrays[('southeast',7)]
for y in [86,87,88]:
 for x in range(47,54):
  if a[y,x,3]<24:copy_pixel(7,x,y,x,85)
# A thin artificial slit in the upper cloth is closed; the true lower negative space stays.
for y in range(84,89):
 if a[y,62,3]<24:copy_pixel(7,62,y,61,y)
for y in range(98,101):erase(7,61,y)
# Remove the specified stretched glove spur without repainting intact cloth.
for y in range(88,93):
 for x in range(46,58):erase(3,x,y)
# Tiny outline remnant beyond the new raised thigh.
for y in range(77,83):
 for x in range(81,85):erase(5,x,y)
for y in range(90,94):erase(5,71,y,'northeast')
# New generated leather is matched to the existing boot palette, with position/alpha exact.
old=np.array(Image.open(R/'walk-bundle-rowan-lyra/authorities/lyra/southeast/00.png').convert('RGBA'))[85:115];rr,gg,bb=[old[:,:,k].astype(float) for k in range(3)];palette=old[(rr>gg*1.18)&(rr>bb*1.5)&(old[:,:,3]==255)]
for i in [5,6]:
 a=arrays[('southeast',i)];rr,gg,bb=[a[:,:,k].astype(float) for k in range(3)];yy,xx=np.indices((128,128));ys,xs=np.where((rr>gg*1.18)&(rr>bb*1.5)&(a[:,:,3]>0)&(yy>=84))
 for y,x in zip(ys,xs):
  color=palette[np.argmin(((palette[:,:3].astype(float)-a[y,x,:3]*.82)**2).sum(axis=1))];before=a[y,x].copy();a[y,x,:3]=color[:3]
  if np.any(before!=a[y,x]):w.append({'view':'southeast','frame':i,'xy':[int(x),int(y)],'before':before.tolist(),'after':a[y,x].tolist(),'kind':'existing boot-palette match (RGB only)'})
spec={'schema':'sprite-construction-spec/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'layers':[{'id':'body','name':'Editable body','locked':False}],'frames':[],'animations':[],'provenance':{'actor':'lyra','scope':'Clear actual material cuts with sparse same-frame leather/cloth copies, literal spur erasures, and existing-palette match; no hidden anatomy recovery','game_scale':.66}}
for view in ['southeast','northeast']:
 (O/view).mkdir()
 for i in range(8):
  filename=f'{view}-{i:02}-source.png';Image.open(S/view/f'{i:02}.png').save(O/filename);spec['frames'].append({'id':f'{view}-{i:02}','duration_ticks':9,'cels':{'body':{'image':filename,'at':[0,0]}},'landmarks':{}})
 spec['animations'].append({'id':f'{view}_walk','frames':[f'{view}-{i:02}' for i in range(8)],'fps':160,'loop':True,'events':[]})
(O/'construction-spec.json').write_text(json.dumps(spec,indent=2)+'\n');source=m.construct(O/'construction-spec.json');h=History(source);pal=[list(c) for c in source['palette']];ops=[];changes=[]
for (view,i),a in arrays.items():
 old=np.array(Image.open(O/f'{view}-{i:02}-source.png').convert('RGBA'));ys,xs=np.where(np.any(a!=old,axis=2));points=[]
 for y,x in zip(ys,xs):
  color=a[y,x].tolist()
  if color not in pal:ops.append({'op':'palette_add','rgba':color});pal.append(color)
  points.append([int(x),int(y),pal.index(color)]);changes.append({'view':view,'frame':i,'xy':[int(x),int(y)],'before':old[y,x].tolist(),'after':color})
 if points:ops.append({'op':'paint','cel_id':next(f for f in source['frames'] if f['id']==f'{view}-{i:02}')['cels']['body'],'points':points,'mask':[p[:2] for p in points]})
r=h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(source),'reason':'Sparse material-owned seam fills and spur erasures; restore complete leather/cloth volume without flat replacement polygons; existing boot material match.','operations':ops});assert project_hash(h.undo())==project_hash(source);h.redo();assert project_hash(History.replay(source,h.journal()).project)==project_hash(h.project)
for (view,i),a in arrays.items():np.testing.assert_array_equal(np.array(render_frame(h.project,f'{view}-{i:02}')),a);Image.fromarray(a).save(O/view/f'{i:02}.png')
for name,j in [('source-project.json',source),('edited-project.json',h.project),('journal.json',h.journal()),('receipt.json',r),('material-witnesses.json',w),('actual-changes.json',changes)]: (O/name).write_text(canonical_json(j)+'\n')
sys.path.insert(0,str(R/'walk-bundle-rowan-lyra/scripts'));from animation_media import emit_media
for view in ['southeast','northeast']:
 ims=[Image.open(O/view/f'{i:02}.png') for i in range(8)];sheet=Image.new('RGBA',(2048,512),(229,226,213,255))
 for i,im in enumerate(ims):sheet.alpha_composite(Image.open(B/'selected-v2'/view/f'{i:02}.png').resize((256,256),Image.Resampling.NEAREST),(i*256,0));sheet.alpha_composite(im.resize((256,256),Image.Resampling.NEAREST),(i*256,256))
 sheet.save(O/view/'old-polygon-above-sparse-material-below.png');emit_media(ims,O/view/'candidate-native',1);emit_media(ims,O/view/'candidate-game',.66)
print({'changed_pixels':len(changes),'source_copy_and_color_witnesses':len(w),'output':str(O)})
