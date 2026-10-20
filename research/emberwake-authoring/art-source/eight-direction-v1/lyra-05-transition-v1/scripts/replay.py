from pathlib import Path
import argparse,copy,json,hashlib
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,candidate_transaction,EditError,load_json
P=Path(__file__).resolve().parents[1];EXPECTED='ae2aef07754fb69429f11b04f84b035d3e6cc621324dd0a40704b2ae7beff6f7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return load_json((P/n).read_text())
def arr(n):return np.array(Image.open(P/n).convert('RGBA'))
def mask(n):return np.array(Image.open(P/n).convert('L'))>0
def shifted(a,dx,dy):
 out=np.zeros_like(a);ys,xs=np.where(a)
 for y,x in zip(ys,xs):
  if 0<=x+dx<128 and 0<=y+dy<128:out[y+dy,x+dx]=True
 return out

def scalar_over(dst,src):
 # Independent scalar integer compositor, not build_trial's vectorized helper.
 out=dst.copy()
 for y in range(128):
  for x in range(128):
   s=list(map(int,src[y,x]));d=list(map(int,out[y,x]));sa=s[3];da=d[3]
   if sa==0:continue
   n=sa*255+da*(255-sa)
   out[y,x]=[(s[c]*sa*255+d[c]*da*(255-sa)+n//2)//n for c in range(3)]+[(n+127)//255]
 return out

ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
if args.output:assert args.output.is_absolute()and not args.output.exists(),'Output must be fresh absolute directory'
inputs=load('INPUTS.json')
for f in inputs['files']:assert sha(P/f['path'])==f['sha256'],f['path']
assert sha(P/'candidate/05.png')==EXPECTED
recipe=load('RECIPE.json');source={i:arr(f'inputs/cycle/{i:02}.png')for i in [2,6]};base=arr('inputs/cycle/05.png')
up=np.load(P/'inputs/05-upstream-visible-source-map.npz',allow_pickle=False);yy,xx=np.indices((128,128));protected=np.isin(up['layer_id'],[0,4,5,6])|shifted(mask('inputs/ownership/left-arm-owner.png'),1,1)|shifted(mask('inputs/ownership/right-arm-owner.png'),-1,1)|(yy<=76)
assert np.array_equal(protected,mask('masks/05-upper-hem-full-gloves-protected.png'))
repair=mask('masks/05-repair-owner.png');assert not np.any(protected&repair)
body=base.copy();body[repair]=0;assert np.array_equal(body,arr('layers/05-cleared-body.png'))
hip=mask('inputs/ownership/hip-underlay.png')&repair&(source[2][...,3]>0);assert np.array_equal(hip,mask('masks/05-actual02-hip-underpaint.png'))
under=np.zeros_like(base);under[hip]=source[2][hip];assert np.array_equal(under,arr('layers/05-actual02-hip-underpaint.png'));body=scalar_over(body,under);map_receipts=[]
for b in recipe['parts']:
 src=np.array(b['source_points']);dst=np.array(b['target_points']);triangles=np.array(b['triangles']);donor=source[b['source_phase']];owner=mask('inputs/source-parts/'+b['owner']);mapping=np.full((128,128,2),-1,np.int16);part=np.zeros_like(base)
 assert np.all(donor[...,3][owner]>0),'Owner must be positive visible source paint'
 for tri in triangles:
  st=src[tri];tt=dst[tri];sm=np.stack([st[1]-st[0],st[2]-st[0]],axis=1);tm=np.stack([tt[1]-tt[0],tt[2]-tt[0]],axis=1);assert np.linalg.det(sm)*np.linalg.det(tm)>0
  inv=np.linalg.inv(np.vstack([tt.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(tt[:,1].min()))),min(127,int(np.ceil(tt[:,1].max())))+1):
   for x in range(max(0,int(np.floor(tt[:,0].min()))),min(127,int(np.ceil(tt[:,0].max())))+1):
    bary=inv@np.array([x,y,1])
    if min(bary)<-1e-8:continue
    sx,sy=np.floor(bary@st+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and owner[sy,sx]and repair[y,x]:part[y,x]=donor[sy,sx];mapping[y,x]=[sx,sy]
 owned=mapping[...,0]>=0;stored=np.load(P/f'maps/05-{b["id"]}.npz',allow_pickle=False);assert np.array_equal(mapping,stored['source_xy']);assert np.array_equal(owned,stored['owner']);assert int(stored['source_phase'])==b['source_phase'];assert np.array_equal(part,arr(f'layers/05-{b["id"]}.png'))
 body=scalar_over(body,part);map_receipts.append({'part':b['id'],'declared_mesh_to_XY_map_exact':True,'source_texels_and_layer_RGBA_exact':True,'mapped_positive_pixels':int(owned.sum())})
body[protected]=base[protected];body[body[...,3]==0]=0
assert np.array_equal(body,arr('candidate/05.png'));assert np.array_equal(body[protected],base[protected]);assert np.array_equal(body[~repair],base[~repair])
initial=load('projects/initial.json');target=load('projects/final.json');journal=load('projects/journal.json');history=History.replay(initial,journal);end=project_hash(history.project);assert end==project_hash(target);assert len(history.records)==1
frames=[]
for i in range(8):
 original=arr(f'inputs/cycle/{i:02}.png');expected=body if i==5 else original;frozen=arr(f'candidate/{i:02}.png');editor=np.array(render_cel(history.project,f'lyra-se-{i:02}'))
 assert np.array_equal(expected,frozen)and np.array_equal(editor,frozen)
 assert render_cel(initial,f'lyra-se-{i:02}').tobytes()==Image.fromarray(original).tobytes()
 if i!=5:assert (P/f'candidate/{i:02}.png').read_bytes()==(P/f'inputs/cycle/{i:02}.png').read_bytes()
 frames.append({'phase':i,'RGBA_sha256':hashlib.sha256(frozen.tobytes()).hexdigest(),'PNG_sha256':sha(P/f'candidate/{i:02}.png'),'raw_source_and_editor_RGBA_exact':True,'other7_original_PNG_bytes_exact':i!=5})
history.undo();assert project_hash(history.project)==project_hash(initial);history.redo();assert project_hash(history.project)==end
negative=[]
def reject(name,fn,h=None):
 before=project_hash(h.project)if h is not None else None;cursor=h.cursor if h is not None else None
 try:fn()
 except EditError as e:
  if h is not None:assert project_hash(h.project)==before and h.cursor==cursor
  negative.append({'guard':name,'rejected':True,'message':str(e),'state_unchanged':True});return
 raise AssertionError(name+' unexpectedly accepted')
coords=[[int(x),int(y)]for y,x in np.argwhere(repair)];badimage=Image.fromarray(body);c=badimage.getpixel((64,40));badimage.putpixel((64,40),((c[0]+1)%256,c[1],c[2],c[3]));reject('outside-mask candidate RGBA',lambda:candidate_transaction(initial,'lyra-se-05',badimage,coords))
h0=History(initial);badtx=copy.deepcopy(journal['receipts'][0]['transaction']);badtx['expected_project_sha256']='0'*64;reject('stale project expected hash',lambda:h0.apply(badtx),h0)
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);patch=next(op for op in badtx['operations']if op['op']=='candidate_patch');patch['expected_cel_sha256']='0'*64;reject('stale candidate cel expected hash',lambda:h0.apply(badtx),h0)
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);patch=next(op for op in badtx['operations']if op['op']=='candidate_patch');assert not repair[0,0];patch['candidate_pixels'][0]=1;reject('transaction patch outside mask',lambda:h0.apply(badtx),h0)
assert all(f['duration_ticks']==9 for f in target['frames'])and target['animations'][0]['fps']==160
receipt={'status':'PASS source producer replay; not independent art review or acceptance','candidate05_PNG_sha256':EXPECTED,'all8':frames,'maps':map_receipts,'source02_hip_underpaint_pixels':int(hip.sum()),'scalar_integer_compositor_RGBA_exact':True,'one_actual_guarded_editor_transaction':True,'initial_project_canonical_sha256':project_hash(initial),'final_project_canonical_sha256':end,'undo_redo_exact':True,'actual05_upper_hem_full_arms_gloves_RGBA_exact':True,'other7_original_PNG_bytes_exact':True,'negative_guards':negative,'clock':'8x9/160s=.45s loop','model_calls':0,'hidden_anatomy_recovered':False,'runtime_or_external_editor_tested':False}
if args.output:
 for name in ['source-map','editor']:(args.output/name).mkdir(parents=True)
 for i in range(8):
  for folder in ['source-map','editor']:
   dest=args.output/folder/f'{i:02}.png'
   if i==5:Image.fromarray(body if folder=='source-map'else np.array(render_cel(target,'lyra-se-05'))).save(dest)
   else:dest.write_bytes((P/f'inputs/cycle/{i:02}.png').read_bytes())
   assert sha(dest)==sha(P/f'candidate/{i:02}.png')
 (args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS all8 source/scalar-compositor/editor RGBA and PNG, one journal transaction, undo/redo, upper/other7, four negative guards.')
