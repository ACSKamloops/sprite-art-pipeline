import sys
from pathlib import Path
ROOT=Path('/home/astra/artifacts/emberwake-brann-se-three-pose-v1')
OUT=Path('/home/astra/artifacts/emberwake-brann-three-pose-independent-replay-v1')
sys.dont_write_bytecode=True
sys.pycache_prefix=str(OUT/'unused-isolated-pycache')
sys.path.insert(0,str(ROOT/'toolkit'))
import copy,json,hashlib,platform,subprocess,time,datetime,os
import numpy as np
import PIL
from PIL import Image,ImageDraw
from sprite_lab import History,render_frame,project_hash

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p))>0
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0

def save(n,d):(OUT/n).write_text(json.dumps(d,indent=2)+'\n')
# Re-execute the exact retained script with old package bytecode bypassed.
command=[sys.executable,'-B','-X',f'pycache_prefix={OUT / "unused-isolated-pycache"}',str(ROOT/'scripts/replay.py'),'--output',str(OUT/'retained-source-only-run')]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
p=subprocess.run(command,cwd=OUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
(OUT/'SOURCE-ONLY-STDOUT.txt').write_text(p.stdout);(OUT/'SOURCE-ONLY-STDERR.txt').write_text(p.stderr)
save('SOURCE-ONLY-RUN.json',{'command':command,'started_utc':started,'elapsed_seconds':time.monotonic()-tick,'exit_code':p.returncode,'stdout_file':'SOURCE-ONLY-STDOUT.txt','stderr_file':'SOURCE-ONLY-STDERR.txt','old_package_bytecode_bypassed':True})
assert p.returncode==0,p.stderr
initial=load(ROOT/'initial-project.json');target=load(ROOT/'project.json');journal=load(ROOT/'journal.json');recipe=load(ROOT/'RECIPE.json');guide=load(ROOT/'inputs/guide04-recipe.json')
source=[arr(ROOT/'inputs/v5-frames'/f'{i:02}.png')for i in range(8)]
h=History.replay(initial,journal);initial_hash=project_hash(initial);final_hash=project_hash(h.project)
assert final_hash==project_hash(target)
frames=[]
for i in range(8):
 expected=arr(ROOT/'frames'/f'{i:02}.png');replayed=arr(OUT/'retained-script-run'/f'{i:02}.png');sourceonly=arr(OUT/'retained-source-only-run'/f'{i:02}.png');editor=np.array(render_frame(h.project,f'f{i}'))
 assert np.array_equal(expected,replayed) and np.array_equal(expected,sourceonly) and np.array_equal(expected,editor)
 assert sha(ROOT/'frames'/f'{i:02}.png')==sha(OUT/'retained-script-run'/f'{i:02}.png')==sha(OUT/'retained-source-only-run'/f'{i:02}.png')
 if i in [3,4,5]:
  upper=mask(ROOT/'masks'/f'{i:02}-whole-upper.png');assert np.array_equal(expected[upper],source[i][upper])
 else:assert sha(ROOT/'frames'/f'{i:02}.png')==sha(ROOT/'inputs/v5-frames'/f'{i:02}.png')
 assert np.array_equal(np.array(render_frame(initial,f'f{i}')),source[i])
 frames.append({'phase':i,'PNG_sha256':sha(ROOT/'frames'/f'{i:02}.png'),'decoded_RGBA_sha256':hashlib.sha256(expected.tobytes()).hexdigest(),'RGBA_exact':True,'PNG_bytes_exact':True})
for _ in journal['receipts']:h.undo()
assert project_hash(h.project)==initial_hash
for _ in journal['receipts']:h.redo()
assert project_hash(h.project)==final_hash

def rejection(name,action,project=None):
 before=project_hash(project)if project is not None else None
 try:action()
 except Exception as e:
  unchanged=project_hash(project)==before if project is not None else True
  assert unchanged
  return {'name':name,'rejected':True,'exception':type(e).__name__,'message':str(e),'input_or_history_state_unchanged':unchanged}
 raise AssertionError(name+' unexpectedly accepted')
negative=[]
bad=copy.deepcopy(journal);bad['initial_project_sha256']='0'*64
negative.append(rejection('stale initial journal',lambda:History.replay(initial,bad),initial))
h0=History(initial);badtx=copy.deepcopy(journal['receipts'][0]['transaction']);badtx['expected_project_sha256']='0'*64
negative.append(rejection('stale transaction expected project hash',lambda:h0.apply(badtx),h0.project));assert h0.cursor==0 and not h0.records
badtx=copy.deepcopy(journal['receipts'][0]['transaction']);badtx['operations'][0]['points'][0][0:2]=[0,0]
assert [0,0]not in badtx['operations'][0]['mask']
negative.append(rejection('paint point outside actual operation mask',lambda:h0.apply(badtx),h0.project));assert h0.cursor==0 and not h0.records
# Replay receipt comparison is a further guard, distinct from paint masks.
bad=copy.deepcopy(journal);bad['receipts'][0]['after_sha256']='0'*64
negative.append(rejection('tampered journal receipt',lambda:History.replay(initial,bad),initial))
operations=[]
for receipt in journal['receipts']:
 for op in receipt['transaction']['operations']:
  assert op['op']=='paint';i=int(op['cel_id'][-1]);upper=mask(ROOT/'masks'/f'{i:02}-whole-upper.png');allowed=set(map(tuple,op['mask']))
  assert all((x,y)in allowed and not upper[y,x]for x,y,_ in op['points'])
  assert all(not upper[y,x]for x,y in allowed)
  operations.append({'cel_id':op['cel_id'],'op':op['op'],'points':len(op['points']),'mask_points':len(allowed),'upper_excluded':True})
# Verify retained full source arrays and source-owner witnesses as well as replayed maps.
mapchecks=[];witnesses=[]
for i in [3,4,5]:
 r=guide if i==4 else recipe['frames'][f'{i:02}'];boots=r['boot_sources']if i==4 else r['parts_in_back_to_front_order'];ws=r['literal_trouser_source_witnesses']if i==4 else r['literal_cloth_witnesses']
 for w in ws:
  x,y=w['source'];sp=w.get('source_phase',0);assert source[sp][y,x].tolist()==w['RGBA']
 witnesses.append({'phase':i,'literal_witness_count':len(ws),'all_source_RGBA_exact':True})
 for b in boots:
  with np.load(ROOT/'maps'/f'{i:02}-{b["id"]}.npz',allow_pickle=False)as data:
   assert np.array_equal(data['source_rgba'],source[b['source_phase']])
   if 'source_owner'in data:assert np.array_equal(data['source_owner'],poly(b['polygon']))
   if 'source_owner_translation'in data:assert data['source_owner_translation'].tolist()==b['translation']
   mapchecks.append({'phase':i,'part':b['id'],'source_phase':b['source_phase'],'source_RGBA_exact':True,'source_owner_or_translation_exact':True,'source_XY_shape':list(data['source_xy'].shape)})
occlusion=[]
for item in load(ROOT/'OCCLUSION.json'):
 i=item['phase'];part=item['part'];placed=arr(ROOT/'layers'/f'editor-{i:02}-{item["part_layer"]}.png')[:,:,3]>0;opaque=np.zeros((128,128),bool);partial=opaque.copy()
 for name in item['later_owners']:
  alpha=arr(ROOT/'layers'/f'editor-{i:02}-{name}.png')[:,:,3];opaque|=alpha==255;partial|=(alpha>0)&(alpha<255)
 visible=placed&~opaque
 computed={'positive_after_upper_occlusion':int(placed.sum()),'fully_occluded_by_later_part_pixels':int((placed&opaque).sum()),'positive_final_contribution_pixels':int(visible.sum()),'partially_overlaid_pixels':int((placed&partial&~opaque).sum())}
 assert all(item[k]==v for k,v in computed.items())
 assert np.array_equal(visible,mask(ROOT/'masks'/f'{i:02}-{part}-target-visible.png'))
 assert np.array_equal(placed&opaque,mask(ROOT/'masks'/f'{i:02}-{part}-opaque-later-occlusion.png'))
 occlusion.append({'phase':i,'part':part,'counts_and_masks_exact':True,**computed})
assert all(f['duration_ticks']==9 for f in target['frames'])and target['animations'][0]['fps']==160
checks={'status':'PASS mechanical reproduction with explicit qualifications; no art rating','python':platform.python_version(),'Pillow':PIL.__version__,'NumPy':np.__version__,'initial_project_sha256':initial_hash,'final_project_sha256':final_hash,'all8':frames,'journal_transactions':len(journal['receipts']),'undo_all_3_exact':True,'redo_all_3_exact':True,'negative_guard_checks':negative,'actual_journal_operations':operations,'guard_qualification':'Actual paint transactions use project-hash preconditions and per-operation coordinate masks. There are no candidate_patch cel-hash guards or intrinsic whole-upper layer locks; the recorded masks exclude upper and the final replay checks upper pixels.','maps':mapchecks,'literal_source_witnesses':witnesses,'occlusion':occlusion,'occlusion_qualification':'Source contribution means alpha algebra under declared later layers; not perceptual visibility or anatomy.','clock':'8 exposures x 9/160 s = 0.45 s','bytecode_bypass':'Retained source-only replay and these checks redirect cache lookup to nonexistent audit-local prefix; -B prevents bytecode writes.','toolkit_module_sources':{k:v.__file__ for k,v in sys.modules.copy().items()if k=='sprite_lab'or k.startswith('sprite_lab.')}}
save('INDEPENDENT-CHECKS.json',checks)
print('PASS independent all8 RGBA/PNG, source-only retained replay, 3 undo/redo, 4 negative guards, 6 map witnesses, 6 occlusion records.')
