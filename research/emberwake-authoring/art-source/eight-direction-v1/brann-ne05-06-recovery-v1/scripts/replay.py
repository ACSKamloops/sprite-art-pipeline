"""Portable exact05 source reconstruction and one guarded editor transaction.
All local source layers/maps are frozen. No geometry decisions or new painting.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys,platform
sys.dont_write_bytecode=True
from fractions import Fraction
import numpy as np
from PIL import Image,ImageDraw,__version__ as pillow_version
from sprite_lab import History,EditError,candidate_transaction,project_hash,cel_hash,render_frame,validate_project,load_json
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,separators=(',',':'))+'\n')
def mask(n):return np.array(Image.open(R/'masks'/n).convert('L'))>0
def png(a,p):p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a.astype('uint8')).save(p)
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
def fraction_over(s,d):
 sa=Fraction(int(s[3]),255);da=Fraction(int(d[3]),255);a=sa+da*(1-sa)
 def round_half_up(v):return (2*v.numerator+v.denominator)//(2*v.denominator)
 if a==0:return [0,0,0,0]
 return [round_half_up((int(s[c])*sa+int(d[c])*da*(1-sa))/a)for c in range(3)]+[round_half_up(a*255)]
def reconstruct(outdir):
 src=rgba(R/'inputs/control/05.png');d=rgba(R/'inputs/control/07.png');reg=rgba(R/'inputs/provenance/registered00.png');under=rgba(R/'inputs/provenance/original05-underpaint.png');mp=np.load(R/'maps/05.npz');P=np.zeros_like(src)
 for y,x in np.argwhere(mask('P-complete-layer-owner.png')):
  sx,sy=mp['complete_P_source_xy'][y,x];P[y,x]=reg[sy,sx]
 assert np.array_equal(P,rgba(R/'parts/complete-P-source-layer-UNCHANGED.png'));Pcomp=over(P,under);out=src.copy();remove=mask('old-Q-complete-removal-owner.png');out[remove]=0;reveal=mask('P-source-revealed-after-oldQ-removal.png');out[reveal]=Pcomp[reveal]
 pm=Image.new('L',(128,128));ImageDraw.Draw(pm).polygon([(50,76),(65,76),(62,90),(50,92)],fill=255);allowed=np.array(Image.open(R/'inputs/provenance/05-allowed.png').convert('L'))>0;ur=remove&(np.array(pm)>0)&allowed&(out[:,:,3]==0);out[ur]=under[ur]
 assert np.array_equal(out,rgba(R/'parts/05-after-complete-oldQ-removal-P-reveal.png'))
 for y,x in np.argwhere(mask('shaded-proximal-cloth-owner.png')):
  sx,sy=mp['cloth_source_xy'][y,x];out[y,x]=d[sy,sx]
 assert np.array_equal(out,rgba(R/'parts/05-before-Q-source-over.png'));before_Q=out.copy();boot=np.zeros_like(src)
 for y,x in np.argwhere(mask('Q-new-complete-target-owner.png')):
  sx,sy=mp['new_Q_source_xy'][y,x];boot[y,x]=d[sy,sx]
 assert np.array_equal(boot,rgba(R/'parts/source07-boot-translated-minus7-0.png'));active=boot[:,:,3]>0;composite=over(boot,out)
 for y,x in np.argwhere(active):assert composite[y,x].tolist()==fraction_over(boot[y,x],out[y,x])
 out[active]=composite[active];protected=mask('upper-sash-protected.png');out[protected]=src[protected];out[out[:,:,3]==0]=0
 assert np.array_equal(out,rgba(R/'frames/05.png'));Pvis=mask('P-current-visible-owner.png');occluded=mask('Q-over-current-visible-P-nine.png');assert int(occluded.sum())==9;assert np.array_equal(out[Pvis&~occluded],src[Pvis&~occluded]);assert np.array_equal(out[protected],src[protected])
 for v in load_json((R/'maps/NINE-P-OCCLUSION-WITNESSES.json').read_text()):
  x,y=v['target'];sx,sy=v['source07_Q_xy'];px,py=v['retained_P_layer_registered00_xy'];assert d[sy,sx].tolist()==v['source07_Q_RGBA'];assert reg[py,px].tolist()==v['retained_P_layer_RGBA'];assert src[y,x].tolist()==v['original05_visible_P_RGBA'];assert before_Q[y,x].tolist()==v['source_over_under_RGBA'];assert out[y,x].tolist()==v['final_RGBA']
 for v in load_json((R/'maps/ALL-Q-SOURCE-WITNESSES.json').read_text()):
  x,y=v['target'];sx,sy=v['source07_xy'];assert d[sy,sx].tolist()==v['source07_RGBA'];assert out[y,x].tolist()==v['final_RGBA']
 checks=[]
 for i in range(8):
  frame=out if i==5 else rgba(R/'inputs/control'/f'{i:02}.png');p=outdir/'source-frames'/f'{i:02}.png';png(frame,p);target=R/'frames'/f'{i:02}.png';assert p.read_bytes()==target.read_bytes();assert np.array_equal(frame,rgba(target));checks.append({'phase':i,'PNG_sha256':sha(p),'RGBA_sha256':hashlib.sha256(frame.tobytes()).hexdigest(),'target_PNG_exact':True,'target_RGBA_exact':True})
 return checks,{'complete_P_layer_RGBA_exact':True,'P_current_visible_exact_except_nine_Q_occlusions':True,'upper_sash_exact':True,'frozen06_exact':True,'fraction_source_over_samples_exact':int(active.sum()),'no_hidden_anatomy_claim':True}

def make_initial():
 palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
 for i in range(8):
  indices=[]
  for c in Image.open(R/'inputs/control'/f'{i:02}.png').convert('RGBA').get_flattened_data():
   if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
   indices.append(lookup[c])
  key=f'brann-ne-{i:02}';cels[key]={'layer_id':'paint','pixels':indices};frames.append({'id':key,'duration_ticks':9,'cels':{'paint':key},'landmarks':{'pivot':[64,112]}})
 p={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Frozen Brann NE source bank; bounded complete-Q-donor05 import','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[f'brann-ne-{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'source_authority':'inputs/control/00..07.png','candidate_authority':'frames/05.png','source_construction':'maps/05.npz + masks + RECIPE.json','model_calls':0,'scope':'Only05 complete-visible07 Q donor at[-7,0], bounded projected gray cloth, complete original registered00 P layer retained at its unchanged05 map with9 visible P-Q occlusions; frozen06 retained exact','ambiguous_tail':'All six original-source tail witnesses retained; no erasure','status':'Parent authorized retained exact05 on the frozen06 bank after critic comparison; no whole-cycle score inherited'}}
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
   assert [0,0]not in op['mask'];live=initial['cels']['brann-ne-05']['pixels'][0];op['candidate_pixels'][0]=1 if live!=1 else 0
 result['outside_owner_apply']=reject_atomic(initial,bad,'candidate pixel outside literal owner')
 # Separate public import rejection proves no quiet crop/clamp when the image
 # itself has an unowned modification; palette/history remain unchanged.
 h=History(final);before=project_hash(h.project);badimg=Image.open(R/'frames/05.png').convert('RGBA');badimg.putpixel((0,0),(1,2,3,255));coords=next(op['mask']for op in tx['operations']if op['op']=='candidate_patch')
 try:candidate_transaction(h.project,'brann-ne-05',badimg,coords,reason='Outside-owner rejection probe only')
 except EditError as e:
  assert project_hash(h.project)==before and h.project==final and h.cursor==0;result['outside_owner_import']={'rejected':True,'atomic_project_and_history_exact':True,'error':str(e)}
 else:raise AssertionError('Outside-owner image import accepted')
 return result

def create_editor(outdir):
 initial=make_initial();a=rgba(R/'inputs/control/05.png');b=rgba(R/'frames/05.png');coords=[[int(x),int(y)]for y,x in np.argwhere(np.any(a!=b,axis=2))];h=History(initial)
 tx=candidate_transaction(h.project,'brann-ne-05',Image.open(R/'frames/05.png').convert('RGBA'),coords,reason='Import exact inspected d162cf05: whole visible07 Q cuff/boot[-7,0] plus bounded shaded cloth; complete registered00 P layer stays at its old05 map,9 visible P texels naturally occluded; upper/sash and other7 including frozen06 exact')
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
 return {'actual_guarded_transactions':1,'actual_changed_RGBA_coordinates':len(next(op['mask']for op in tx['operations']if op['op']=='candidate_patch')),'all8_editor_exports':checks,'undo_original8':undo,'redo_final8_RGBA_exact':True,'guards':guards,'initial_project_sha256':project_hash(initial),'final_project_sha256':project_hash(final),'initial05_cel_sha256':cel_hash(initial,'brann-ne-05'),'final05_cel_sha256':cel_hash(final,'brann-ne-05')}

parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--create-editor',action='store_true');args=parser.parse_args();O=Path(args.out).resolve()
if O.exists():raise SystemExit('Fresh output directory required; refusing to overwrite '+str(O))
O.mkdir(parents=True);source,qualified=reconstruct(O)
if args.create_editor:initial,final,journal,tx=create_editor(O)
else:initial,final,journal,tx=[load_json((R/'projects'/f'{n}.json').read_text())for n in ['initial','final','journal','transaction']]
editor=replay_editor(O,initial,final,journal,tx)
receipt={'status':'Exact retained05+06 source and independent guarded-editor mechanics; no new paint or public acceptance','python':platform.python_version(),'pillow':pillow_version,'numpy':np.__version__,'full8_source_exports':source,'qualified_P_and_source_over':qualified,'editor':editor,'all_other7_original_PNG_bytes_exact':all((R/'frames'/f'{i:02}.png').read_bytes()==(R/'inputs/control'/f'{i:02}.png').read_bytes()for i in range(8)if i!=5),'candidate05_sha256':sha(R/'frames/05.png'),'frozen06_sha256':sha(R/'frames/06.png'),'hold':[9,160],'total':[9,20],'model_calls':0,'canonical_writes':0}
save(O/'REPLAY-RECEIPT.json',receipt);print(json.dumps({'source8_PNG_exact':True,'editor8_PNG_exact':True,'undo8_PNG_exact':True,'redo8_RGBA_exact':True,'transaction_count':1,'changed_pixels':editor['actual_changed_RGBA_coordinates'],'guards':{k:v['rejected']for k,v in editor['guards'].items()},'qualified_P_layer':qualified,'candidate05':receipt['candidate05_sha256'],'frozen06':receipt['frozen06_sha256']},indent=2))
