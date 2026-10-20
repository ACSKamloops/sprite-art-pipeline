"""Portable, source-only body-weight construction and guarded native editor replay.
No external artifact/canonical reads. No geometry choices or new pixels.
"""
from pathlib import Path
from fractions import Fraction
import argparse,copy,hashlib,json,sys,platform
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,__version__ as pillow_version
from sprite_lab import History,EditError,candidate_transaction,project_hash,cel_hash,render_frame,validate_project,load_json,export_aseprite,import_aseprite
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def save(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,separators=(',',':'))+'\n')
def png(p,z):p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(z.astype('uint8')).save(p)
def mask(p):return np.array(Image.open(p).convert('L'))>0
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
def fraction_over(s,d):
 sa=Fraction(int(s[3]),255);da=Fraction(int(d[3]),255);oa=sa+da*(1-sa)
 def rnd(q):return (2*q.numerator+q.denominator)//(2*q.denominator)
 return [rnd((int(s[c])*sa+int(d[c])*da*(1-sa))/oa)for c in range(3)]+[rnd(oa*255)]if oa else[0,0,0,0]
def independent_over(s,d,out):
 n=0
 for y,x in np.argwhere((s[:,:,3]>0)|(d[:,:,3]>0)):
  assert out[y,x].tolist()==fraction_over(s[y,x],d[y,x]);n+=1
 return n

def reconstruct(outdir):
 C=load_json((R/'construction/CONSTRUCTION.json').read_text());S=load_json((R/'construction/four-pixel-stage/FOUR-PIXEL-RECIPE.json').read_text());sources=[rgba(R/'inputs/original8'/f'{i:02}.png')for i in range(8)];records=[];pin_count=under27=seam4=sourceovers=map_delta_count=owner_delta_count=0
 for i in range(8):
  src=sources[i];rec=C['records'][i];m=np.load(R/'construction/maps'/f'{i:02}.npz');upper=mask(R/'construction/masks'/f'{i:02}-current-upper-owner.png');clothowner=mask(R/'construction/masks'/f'{i:02}-literal-cloth-owner.png');fixed=src.copy();fixed[upper|clothowner]=0
  body=np.zeros_like(src);cloth=np.zeros_like(src);under=np.zeros_like(src)
  for key,dst in [('body_source_xy',body),('cloth_source_xy',cloth)]:
   xy=m[key]
   for y,x in np.argwhere(xy[:,:,0]>=0):
    sx,sy=[int(v)for v in xy[y,x]];dst[y,x]=src[sy,sx]
    if key=='body_source_xy':assert upper[sy,sx]and[x-sx,y-sy]==rec['body_xy']
    else:assert clothowner[sy,sx]
  u=m['authored_undercoat_source_phase_xy']
  for y,x in np.argwhere(u[:,:,0]>=0):di,sx,sy=[int(v)for v in u[y,x]];under[y,x]=sources[di][sy,sx];under27+=1
  for q in rec['authored_undercoat']:
   x,y=q['target'];di=q['donor_phase'];sx,sy=q['donor'];assert sources[di][sy,sx].tolist()==q['donor_RGBA'];assert under[y,x].tolist()==q['donor_RGBA']
  for q in rec['explicit_pins']:
   x,y=q['target'];sx,sy=q['source'];assert m['cloth_source_xy'][y,x].tolist()==[sx,sy];assert src[sy,sx].tolist()==q['source_RGBA'];pin_count+=1
  # Every map/owner correction has its literal initial-failure source witness.
  prior=R/'archive/initial-failed-single-curve-v1';oldmap=np.load(prior/'maps'/f'{i:02}.npz')['cloth_source_xy'];delta=np.any(oldmap!=m['cloth_source_xy'],axis=2);assert int(delta.sum())==len(rec['map_deltas']);map_delta_count+=int(delta.sum())
  for q in rec['map_deltas']:
   x,y=q['target'];assert oldmap[y,x].tolist()==q['old_source'];assert m['cloth_source_xy'][y,x].tolist()==q['new_source']
   if q['new_source'][0]>=0:sx,sy=q['new_source'];assert src[sy,sx].tolist()==q['source_RGBA']
  oldupper=mask(prior/'masks'/f'{i:02}-current-upper-owner.png');oc=oldupper!=upper;assert int(oc.sum())==len(rec['owner_changes']);owner_delta_count+=int(oc.sum())
  for q in rec['owner_changes']:
   x,y=q['xy'];assert bool(oldupper[y,x])==q['was_upper']and bool(upper[y,x])==q['now_upper'];assert src[y,x].tolist()==q['source_RGBA']
  oldcloth=mask(prior/'masks'/f'{i:02}-literal-cloth-owner.png');oldfixed=src.copy();oldfixed[oldupper|oldcloth]=0
  fc=np.any(oldfixed!=fixed,axis=2);assert int(fc.sum())==len(rec['fixed_lower_delta_vs_bad_initial_partition'])
  for q in rec['fixed_lower_delta_vs_bad_initial_partition']:
   x,y=q['xy'];assert oldfixed[y,x].tolist()==q['old']and fixed[y,x].tolist()==q['corrected']
  # Full visible boots/other retained lower paint remain in this exact source
  # layer at identity. This does not assert hidden whole boots or full final
  # visibility when moved upper naturally occludes some current lower pixels.
  assert np.array_equal(fixed,rgba(R/'construction/layers'/f'{i:02}-fixed-lower.png'))
  p1=over(cloth,under);sourceovers+=independent_over(cloth,under,p1);p2=over(fixed,p1);sourceovers+=independent_over(fixed,p1,p2);out=over(body,p2);sourceovers+=independent_over(body,p2,out);out[out[:,:,3]==0]=0
  pre=out.copy();prepath=outdir/'before-four-frames'/f'{i:02}.png';png(prepath,pre);assert prepath.read_bytes()==(R/'inputs/corrected-before-four'/f'{i:02}.png').read_bytes()
  four=np.load(R/'construction/four-pixel-stage/maps'/f'{i:02}.npz')['source_phase_xy'];layer=np.zeros_like(src);owner=np.zeros((128,128),bool)
  for y,x in np.argwhere(four[:,:,0]>=0):di,sx,sy=[int(v)for v in four[y,x]];layer[y,x]=sources[di][sy,sx];owner[y,x]=True;seam4+=1
  final=over(pre,layer);sourceovers+=independent_over(pre,layer,final);final[final[:,:,3]==0]=0;assert np.array_equal(np.any(final!=pre,axis=2),owner);assert np.array_equal(final[~owner],pre[~owner])
  for q in S['records'][i]['witnesses']:
   x,y=q['target'];sx,sy=q['donor'];assert sources[i][sy,sx].tolist()==q['source_RGBA'];assert final[y,x].tolist()==q['new_target_RGBA']
  p=outdir/'source-frames'/f'{i:02}.png';png(p,final);assert p.read_bytes()==(R/'frames'/f'{i:02}.png').read_bytes();assert np.array_equal(final,rgba(R/'frames'/f'{i:02}.png'))
  if i not in[2,6]:assert p.read_bytes()==prepath.read_bytes()
  if i==6:assert final[83,50,3]==0 and final[84,50,3]==0
  for role,z in [('current-body-source',np.where(upper[:,:,None],src,0)),('mapped-body',body),('fixed-current-lower',fixed),('mapped-charcoal',cloth),('authored-undercoat27',under),('authored-seam4',layer)]:png(outdir/'source-layers'/f'{i:02}-{role}.png',z)
  occlusion=(fixed[:,:,3]>0)&(body[:,:,3]>0);expected={tuple(q)for q in rec['new_upper_over_fixedlower']};actual={(int(x),int(y))for y,x in np.argwhere(occlusion)};assert actual==expected
  records.append({'phase':i,'PNG_sha256':sha(p),'RGBA_sha256':hashlib.sha256(final.tobytes()).hexdigest(),'source_and_PNG_exact':True,'current_upper_rigid_xy_exact':rec['body_xy'],'fixed_current_lower_layer_RGBA_exact':True,'natural_upper_over_fixedlower_samples':len(actual),'four_seam_changes':int(owner.sum()),'outside_four_RGBA_exact':True})
 assert(pin_count,under27,seam4)==(34,27,4)
 return {'all8_final_PNG_RGBA_exact':True,'all8_before_four_PNG_exact':True,'explicit_pins_verified':pin_count,'authored_undercoat27_verified':under27,'authored_seam4_verified':seam4,'all_map_delta_witnesses':map_delta_count,'all_upper_owner_delta_witnesses':owner_delta_count,'independent_fraction_composite_samples':sourceovers,'no_hidden_anatomy_claim':True,'records':records}

def make_initial():
 palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
 for i in range(8):
  pixels=[]
  for col in Image.open(R/'inputs/original8'/f'{i:02}.png').convert('RGBA').get_flattened_data():
   if col not in lookup:lookup[col]=len(palette);palette.append(list(col))
   pixels.append(lookup[col])
  key=f'brann-se-{i:02}';cels[key]={'layer_id':'paint','pixels':pixels};frames.append({'id':key,'duration_ticks':9,'cels':{'paint':key},'landmarks':{'pivot':[64,112]}})
 project={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Exact primary flattened RGBA; upstream source layers and maps retained separately','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[f'brann-se-{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'source_authority':'inputs/original8/00..07.png','construction':'construction/CONSTRUCTION.json + literal maps/masks + four-pixel-stage','representation':'One flattened exact RGBA paint cel per phase, not a claim of hidden anatomy or native independent parts. Full upstream layers retained separately.','curve':'Authored XY body motion after fixed128 registration; no per-pose fitting','fixed_lower':'Complete current visible boot/cuff and retained lower layer at identity; upper foreground occlusions declared in source construction','authored_paint':'27+4 literal existing-source-colour undercoat placements, not recovered hidden anatomy','status':'Root preferred body-weight hypothesis; seam followup separate; unfinished art, no new rating or acceptance inherited','model_calls':0}}
 validate_project(project);return project

def body_transaction(initial):
 lookup={tuple(c):i for i,c in reversed(list(enumerate(initial['palette'])))};nextidx=len(initial['palette']);add=[];patch=[];counts=[]
 for i in range(8):
  old=rgba(R/'inputs/original8'/f'{i:02}.png');new=rgba(R/'inputs/corrected-before-four'/f'{i:02}.png');coords=[[int(x),int(y)]for y,x in np.argwhere(np.any(old!=new,axis=2))];pixels=list(initial['cels'][f'brann-se-{i:02}']['pixels'])
  for x,y in coords:
   col=tuple(int(v)for v in new[y,x])
   if col not in lookup:lookup[col]=nextidx;nextidx+=1;add.append({'op':'palette_add','rgba':list(col)})
   pixels[y*128+x]=lookup[col]
  patch.append({'op':'candidate_patch','cel_id':f'brann-se-{i:02}','mask':coords,'candidate_pixels':pixels,'expected_cel_sha256':cel_hash(initial,f'brann-se-{i:02}')});counts.append(len(coords))
 tx={'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(initial),'reason':'Import exact inspected corrected body-weight construction: same authored XY curve, corrected literal current material owners,34 source-map pins,27 authored source-shaded undercoat placements; full current visible boot layers stay at identity with declared foreground body occlusions. No pose fitting.','operations':add+patch};return tx,counts

def seam_transaction(project):
 recipe=load_json((R/'construction/four-pixel-stage/FOUR-PIXEL-RECIPE.json').read_text());lookup={tuple(c):i for i,c in reversed(list(enumerate(project['palette'])))};ops=[]
 for i in[2,6]:
  points=[];coords=[]
  for w in recipe['records'][i]['witnesses']:
   x,y=w['target'];col=tuple(w['new_target_RGBA']);assert col in lookup;points.append([x,y,lookup[col]]);coords.append([x,y])
  ops.append({'op':'paint','cel_id':f'brann-se-{i:02}','points':points,'mask':coords})
 return {'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(project),'reason':'Four explicitly authored local charcoal continuation texels only:02[50,83]/[50,84],06[80,79]/[80,80], literal donor/source-over witnesses retained. Behind fixed existing paint, no recovered anatomy;06[50,83]/[50,84] stays transparent.','operations':ops}

def create_editor(outdir):
 initial=make_initial();hist=History(initial);tx1,counts=body_transaction(initial);hist.apply(tx1);middle=copy.deepcopy(hist.project);tx2=seam_transaction(middle);hist.apply(tx2);final=copy.deepcopy(hist.project);journal=hist.journal();assert len(journal['receipts'])==2
 for name,obj in [('initial',initial),('corrected-before-four',middle),('final',final),('body-transaction',tx1),('four-seam-transaction',tx2),('journal',journal)]:save(outdir/'projects'/f'{name}.json',obj)
 return initial,middle,final,tx1,tx2,journal,counts

def reject_atomic(project,tx,label):
 hist=History(project);before=project_hash(hist.project);cursor=hist.cursor;records=copy.deepcopy(hist.records)
 try:hist.apply(tx)
 except EditError as e:
  assert project_hash(hist.project)==before and hist.project==project and hist.cursor==cursor and hist.records==records
  return{'guard':label,'rejected':True,'project_history_cursor_atomic_exact':True,'error':str(e)}
 raise AssertionError('Guard accepted: '+label)

def guards(initial,middle,final,tx1,tx2):
 out={}
 for n,project,tx in [('body',initial,tx1),('seam',middle,tx2)]:
  bad=copy.deepcopy(tx);bad['expected_project_sha256']='0'*64;out[n+'_stale_project']=reject_atomic(project,bad,n+' stale project')
 bad=copy.deepcopy(tx1);[q for q in bad['operations']if q['op']=='candidate_patch'][-1]['expected_cel_sha256']='0'*64;out['stale_last_cel_after_earlier_ops']=reject_atomic(initial,bad,'stale final cel after earlier body edits in isolated copy')
 bad=copy.deepcopy(tx1);q=next(q for q in bad['operations']if q['op']=='candidate_patch');assert[0,0]not in q['mask'];q['candidate_pixels'][0]=1 if initial['cels'][q['cel_id']]['pixels'][0]!=1 else 0;out['body_outside_owner_apply']=reject_atomic(initial,bad,'outside body import owner')
 bad=copy.deepcopy(tx2);bad['operations'][-1]['points'].append([0,0,1]);out['seam_outside_owner_apply']=reject_atomic(middle,bad,'outside four-seam owner after first seam op')
 for label,project,cel,img,coords in [('body',initial,'brann-se-00',R/'inputs/corrected-before-four/00.png',next(q['mask']for q in tx1['operations']if q.get('cel_id')=='brann-se-00')),('seam',middle,'brann-se-02',R/'frames/02.png',tx2['operations'][0]['mask'])]:
  hist=History(project);before=project_hash(hist.project);badimg=Image.open(img).convert('RGBA');badimg.putpixel((0,0),(1,2,3,255))
  try:candidate_transaction(hist.project,cel,badimg,coords,reason='Outside-owner rejection probe only')
  except EditError as e:assert hist.project==project and project_hash(hist.project)==before and hist.cursor==0;out[label+'_outside_owner_import']={'rejected':True,'project_history_cursor_atomic_exact':True,'error':str(e)}
  else:raise AssertionError('Unowned candidate accepted')
 return out

def check_export(project,folder,targets):
 checks=[]
 for i in range(8):
  p=folder/f'{i:02}.png';p.parent.mkdir(parents=True,exist_ok=True);im=render_frame(project,f'brann-se-{i:02}');im.save(p);ref=targets/f'{i:02}.png';assert p.read_bytes()==ref.read_bytes();assert im.tobytes()==Image.open(ref).convert('RGBA').tobytes();checks.append({'phase':i,'PNG_exact':True,'RGBA_exact':True,'PNG_sha256':sha(p)})
 return checks

def verify_editor(outdir,initial,middle,final,tx1,tx2,journal,counts):
 h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(final);exports=check_export(h.project,outdir/'editor-frames',R/'frames');h.undo();assert project_hash(h.project)==project_hash(middle);undo_seam=check_export(h.project,outdir/'undo-seam-frames',R/'inputs/corrected-before-four');h.undo();assert project_hash(h.project)==project_hash(initial);undo_all=check_export(h.project,outdir/'undo-all-frames',R/'inputs/original8');h.redo();assert project_hash(h.project)==project_hash(middle);redo_body=check_export(h.project,outdir/'redo-body-frames',R/'inputs/corrected-before-four');h.redo();assert project_hash(h.project)==project_hash(final);redo_final=check_export(h.project,outdir/'redo-final-frames',R/'frames');guard=guards(initial,middle,final,tx1,tx2)
 return{'actual_transactions':2,'body_import_changed_RGBA_counts':counts,'seam_paint_changed_RGBA_count':4,'all8_editor_exports':exports,'undo_seam8_PNG_RGBA_exact':undo_seam,'undo_all8_original_PNG_RGBA_exact':undo_all,'redo_body8_PNG_RGBA_exact':redo_body,'redo_final8_PNG_RGBA_exact':redo_final,'atomic_guards':guard,'initial_project_sha256':project_hash(initial),'middle_project_sha256':project_hash(middle),'final_project_sha256':project_hash(final)}

p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--create-editor',action='store_true');args=p.parse_args();O=Path(args.out).resolve()
if O.exists():raise SystemExit('Fresh output directory required: '+str(O))
O.mkdir(parents=True);source=reconstruct(O)
if args.create_editor:initial,middle,final,tx1,tx2,journal,counts=create_editor(O)
else:
 initial,middle,final,tx1,tx2,journal=[load_json((R/'projects'/f'{n}.json').read_text())for n in ['initial','corrected-before-four','final','body-transaction','four-seam-transaction','journal']];counts=[len(q['mask'])for q in tx1['operations']if q['op']=='candidate_patch']
editor=verify_editor(O,initial,middle,final,tx1,tx2,journal,counts)
# Exact primary native exchange: deliberately ONE flattened RGBA layer. The
# upstream source/body/cloth/undercoat/lower layers are retained, not falsely
# asserted to compose identically in an external editor with different rounding.
ase=O/'native/Brann-SE-weight.aseprite';ase.parent.mkdir(parents=True,exist_ok=True);ase_export=export_aseprite(final,ase,'walk');native_import=import_aseprite(ase);assert project_hash(native_import)==project_hash(final);check_export(native_import,O/'native-adapter-frames',R/'frames')
receipt={'status':'Exact preferred unfinished candidate mechanics; no new art rating/acceptance','dependencies':{'python':platform.python_version(),'pillow':pillow_version,'numpy':np.__version__},'source':source,'editor':editor,'native_adapter':{'one_flat_RGBA_layer':True,'export':ase_export,'exact_full_project_reimport':True,'actual_LibreSprite_separate_receipt':'native/LIBRESPRITE-RECEIPT.json after external save/reopen'},'timing':{'holds':[[9,160]]*8,'total':[9,20],'native_ms_are_quantized_preview':True},'model_calls':0,'canonical_writes':0}
save(O/'REPLAY-RECEIPT.json',receipt);print(json.dumps({'source8_PNG_RGBA':True,'editor8_PNG_RGBA':True,'undo_redo8_PNG_RGBA':True,'transactions':2,'pins':source['explicit_pins_verified'],'undercoat':source['authored_undercoat27_verified']+source['authored_seam4_verified'],'guards':{k:v['rejected']for k,v in editor['atomic_guards'].items()},'native_flat_adapter_full_project_exact':True,'receipt':str(O/'REPLAY-RECEIPT.json')},indent=2))
