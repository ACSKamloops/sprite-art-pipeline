"""Portable exact source-map reconstruction plus independent guarded editor replay.
No geometry or painting decisions occur here. All part owners/maps are frozen.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys,platform
import numpy as np
from PIL import Image,__version__ as pillow_version
from sprite_lab import History,EditError,candidate_transaction,project_hash,cel_hash,render_frame,validate_project,load_json
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,separators=(',',':'))+'\n')
def mask(name):return np.array(Image.open(R/'masks'/name).convert('L'))>0
def png(a,p):p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a.astype('uint8')).save(p)
def source_over(src,dst):
 # Independent exact rational integer source-over; not Pillow alpha_composite.
 s=src.astype('int64');d=dst.astype('int64');sa=s[:,:,3];da=d[:,:,3]
 n=sa*255+da*(255-sa);out=np.zeros_like(s);live=n>0;out[:,:,3]=(n+127)//255
 for c in range(3):out[:,:,c][live]=(s[:,:,c][live]*sa[live]*255+d[:,:,c][live]*da[live]*(255-sa[live])+n[live]//2)//n[live]
 return out.astype('uint8')
def reconstruct(outdir):
 src=rgba(R/'inputs/control/06.png');donor=rgba(R/'inputs/control/07.png');m=np.load(R/'maps/source-map.npz');oldq=mask('old06-Q-erasure.png');prot=mask('upper-sash-P-protected.png');cm=m['cloth_source_xy'];bm=m['boot_source_xy'];out=src.copy();out[oldq]=0
 for y,x in np.argwhere(mask('projected-cloth-owner.png')):
  c=src[y,x];gray=c[3]>0 and int(c[:3].max())-int(c[:3].min())<18
  if gray and not oldq[y,x]:continue
  sx,sy=cm[y,x];out[y,x]=donor[sy,sx]
 assert np.array_equal(out,rgba(R/'parts/06-before-boot-over.png'))
 boot=np.zeros_like(src)
 for y,x in np.argwhere(mask('target07-boot-owner.png')):
  sx,sy=bm[y,x];boot[y,x]=donor[sy,sx]
 assert np.array_equal(boot,rgba(R/'parts/07-boot-translated-minus4-minus1.png'))
 assert not np.any(mask('target07-boot-owner.png')&prot&(boot[:,:,3]>0))
 composite=source_over(boot,out);active=mask('target07-boot-owner.png')&~prot&(boot[:,:,3]>0);out[active]=composite[active];out[prot]=src[prot];out[out[:,:,3]==0]=0
 assert np.array_equal(out,rgba(R/'frames/06.png'))
 checks=[]
 for i in range(8):
  frame=out if i==6 else rgba(R/'inputs/control'/f'{i:02}.png');p=outdir/'source-frames'/f'{i:02}.png';png(frame,p);target=R/'frames'/f'{i:02}.png'
  assert np.array_equal(frame,rgba(target));assert p.read_bytes()==target.read_bytes()
  checks.append({'phase':i,'png_sha256':sha(p),'RGBA_sha256':hashlib.sha256(frame.tobytes()).hexdigest(),'target_PNG_exact':True,'target_RGBA_exact':True})
 assert np.array_equal(src[prot],out[prot])
 # Literal actual witnesses bind every mapped boot/cloth texel, including
 # source-over underpaint, with no inferred anatomy or unlisted join colors.
 records=load_json((R/'maps/source-RGBA-witnesses.json').read_text())
 for v in records:
  x,y=v['target'];sx,sy=v['source_xy'];assert donor[sy,sx].tolist()==v['source_rgba'];assert out[y,x].tolist()==v['final_rgba']
 return checks

def make_initial():
 palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
 for i in range(8):
  indices=[]
  for c in Image.open(R/'inputs/control'/f'{i:02}.png').convert('RGBA').get_flattened_data():
   if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
   indices.append(lookup[c])
  key=f'brann-ne-{i:02}';cels[key]={'layer_id':'paint','pixels':indices};frames.append({'id':key,'duration_ticks':9,'cels':{'paint':key},'landmarks':{'pivot':[64,112]}})
 p={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen Brann NE source bank; bounded complete-Q-donor06 import','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[f'brann-ne-{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'source_authority':'inputs/control/00..07.png','candidate_authority':'frames/06.png','source_construction':'maps/source-map.npz + masks + recipe.json','model_calls':0,'scope':'Only06 complete-visible07 Q donor at[-4,-1], projected visible gray cloth underpaint, actual06 P/upper/sash protected','ambiguous_tail':'All six original-source tail witnesses retained; no erasure','status':'Parent authorized retained exact06 trial after frozen critic comparison; no whole-cycle score inherited'}}
 validate_project(p);return p

def reject_atomic(project,tx,label):
 h=History(project);before=project_hash(h.project);cursor=h.cursor
 try:h.apply(tx)
 except EditError as e:
  assert project_hash(h.project)==before and h.cursor==cursor and h.project==project
  return {'rejected':True,'atomic_project_and_history_exact':True,'error':str(e),'guard':label}
 raise AssertionError('Guard accepted: '+label)

def guard_checks(initial,final,tx):
 result={};bad=copy.deepcopy(tx);bad['expected_project_sha256']='0'*64;result['stale_project']=reject_atomic(final,bad,'stale project')
 bad=copy.deepcopy(tx)
 for op in bad['operations']:
  if op['op']=='candidate_patch':op['expected_cel_sha256']='0'*64
 result['stale_cel']=reject_atomic(initial,bad,'stale cel with correct project')
 bad=copy.deepcopy(tx)
 for op in bad['operations']:
  if op['op']=='candidate_patch':
   assert [0,0]not in op['mask'];live=initial['cels']['brann-ne-06']['pixels'][0];op['candidate_pixels'][0]=1 if live!=1 else 0
 result['outside_owner_apply']=reject_atomic(initial,bad,'candidate pixel outside literal owner')
 # Separate public import rejection proves no quiet crop/clamp when the image
 # itself has an unowned modification; palette/history remain unchanged.
 h=History(final);before=project_hash(h.project);badimg=Image.open(R/'frames/06.png').convert('RGBA');badimg.putpixel((0,0),(1,2,3,255));coords=next(op['mask']for op in tx['operations']if op['op']=='candidate_patch')
 try:candidate_transaction(h.project,'brann-ne-06',badimg,coords,reason='Outside-owner rejection probe only')
 except EditError as e:
  assert project_hash(h.project)==before and h.project==final and h.cursor==0;result['outside_owner_import']={'rejected':True,'atomic_project_and_history_exact':True,'error':str(e)}
 else:raise AssertionError('Outside-owner image import accepted')
 return result

def create_editor(outdir):
 initial=make_initial();a=rgba(R/'inputs/control/06.png');b=rgba(R/'frames/06.png');coords=[[int(x),int(y)]for y,x in np.argwhere(np.any(a!=b,axis=2))];h=History(initial)
 tx=candidate_transaction(h.project,'brann-ne-06',Image.open(R/'frames/06.png').convert('RGBA'),coords,reason='Import exact inspected e2e664 donor07 recovery: whole visible Q cuff/boot[-4,-1] plus declared projected gray cloth, preserving06 P/upper/sash and other7; ambiguous tail retained')
 h.apply(tx);final=copy.deepcopy(h.project);journal=h.journal();assert len(journal['receipts'])==1
 for name,obj in [('initial',initial),('final',final),('journal',journal),('transaction',tx)]:save(outdir/'projects'/f'{name}.json',obj)
 return initial,final,journal,tx

def replay_editor(outdir,initial,final,journal,tx):
 h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(final);checks=[]
 for i in range(8):
  key=f'brann-ne-{i:02}';im=render_frame(h.project,key);p=outdir/'editor-frames'/f'{i:02}.png';p.parent.mkdir(exist_ok=True);im.save(p);target=R/'frames'/f'{i:02}.png'
  assert im.tobytes()==Image.open(target).convert('RGBA').tobytes();assert p.read_bytes()==target.read_bytes();checks.append({'phase':i,'RGBA_exact':True,'PNG_exact':True,'PNG_sha256':sha(p)})
 before=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial)
 undo=[]
 for i in range(8):
  p=outdir/'undo-frames'/f'{i:02}.png';p.parent.mkdir(exist_ok=True);render_frame(h.project,f'brann-ne-{i:02}').save(p);assert p.read_bytes()==(R/'inputs/control'/f'{i:02}.png').read_bytes();undo.append({'phase':i,'original_PNG_exact':True})
 h.redo();assert project_hash(h.project)==before
 for i in range(8):assert render_frame(h.project,f'brann-ne-{i:02}').tobytes()==Image.open(R/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
 guards=guard_checks(initial,final,tx)
 return {'actual_guarded_transactions':1,'actual_changed_RGBA_coordinates':len(next(op['mask']for op in tx['operations']if op['op']=='candidate_patch')),'all8_editor_exports':checks,'undo_original8':undo,'redo_final8_RGBA_exact':True,'guards':guards,'initial_project_sha256':project_hash(initial),'final_project_sha256':project_hash(final),'initial06_cel_sha256':cel_hash(initial,'brann-ne-06'),'final06_cel_sha256':cel_hash(final,'brann-ne-06')}

parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--create-editor',action='store_true');args=parser.parse_args();O=Path(args.out).resolve()
if O.exists():raise SystemExit('Fresh output directory required; refusing to overwrite '+str(O))
O.mkdir(parents=True);source=reconstruct(O)
if args.create_editor:initial,final,journal,tx=create_editor(O)
else:
 initial,final,journal,tx=[load_json((R/'projects'/f'{n}.json').read_text())for n in ['initial','final','journal','transaction']]
editor=replay_editor(O,initial,final,journal,tx)
receipt={'status':'exact-source and independent guarded-editor mechanics verified; no new paint or visual rating','python':platform.python_version(),'pillow':pillow_version,'numpy':np.__version__,'source_over':'Independent rational integer straight-alpha formula; all actual samples exact to frozen Pillow-produced target','full8_source_exports':source,'editor':editor,'all_other7_original_PNG_bytes_exact':all((R/'frames'/f'{i:02}.png').read_bytes()==(R/'inputs/control'/f'{i:02}.png').read_bytes()for i in range(8)if i!=6),'candidate06_sha256':sha(R/'frames/06.png'),'hold':[9,160],'total':[9,20],'model_calls':0,'canonical_writes':0}
save(O/'REPLAY-RECEIPT.json',receipt);print(json.dumps({'source8_PNG_exact':True,'editor8_PNG_exact':True,'undo8_PNG_exact':True,'redo8_RGBA_exact':True,'transaction_count':1,'changed_pixels':editor['actual_changed_RGBA_coordinates'],'guards':{k:v['rejected']for k,v in editor['guards'].items()},'candidate06':receipt['candidate06_sha256']},indent=2))
