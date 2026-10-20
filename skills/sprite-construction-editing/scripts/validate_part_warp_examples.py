#!/usr/bin/env python3
"""Independent artifact validation; never import or execute the frozen producer."""
from pathlib import Path
from PIL import Image
import argparse,copy,hashlib,json,subprocess,sys
import numpy as np

HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
def invoke(spec,out,success=True):
 p=subprocess.run([sys.executable,str(HERE/'warp_part.py'),str(spec),'--out',str(out)],capture_output=True,text=True)
 if success:assert p.returncode==0,(p.stdout,p.stderr)
 else:assert p.returncode==2,p;assert not out.exists()
 return {'returncode':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--evidence-root',type=Path,required=True,help='read-only game-ready-v6 folder');args=parser.parse_args();O=args.out.absolute();O.mkdir(exist_ok=False);B=args.evidence_root.resolve();M=B/'half-torso-AGAGAG';pins={};real=[]
 frozen=json.loads((M/'FROZEN-SHA256.json').read_text());frozen=frozen.get('files',frozen);pins[str(M/'FROZEN-SHA256.json')]=sha(M/'FROZEN-SHA256.json')
 def pin(p):
  p=p.resolve();digest=sha(p);pins[str(p)]=digest
  if p.is_relative_to(M):
   rel=str(p.relative_to(M));expected=frozen.get(rel);assert expected is not None,rel
   # Frozen inventories may store simple hashes or structured entries.
   if isinstance(expected,dict):expected=expected.get('sha256')
   assert digest==expected,(rel,digest,expected)
  return digest
 for phase,part in [('3p5','torso'),('6p5','source6-visible-far-arm')]:
  P=M/phase;ctl=P/'TRANSFORMS-AND-COVERAGE.json';data=json.loads(ctl.read_text());pin(ctl);entry=data['torso'] if part=='torso' else next(e for e in data['other_parts'] if e['part']==part);donor=P/'torso-donor.png';owner=P/('source-torso-owner.png' if part=='torso' else 'source6-far-arm-owner.png');spec={'schema':'nearest-part-warp/v1','canvas':[96,96],'donor':{'path':str(donor),'sha256':pin(donor)},'owner_mask':{'path':str(owner),'sha256':pin(owner)},'source_vertices':entry['source_points'],'target_vertices':entry['target_points'],'triangles':entry['triangles'],'alpha_mode':'copy-owned'};specpath=O/f'{phase}-{part}-request.json';dump(specpath,spec);dest=O/f'{phase}-{part}';call=invoke(specpath,dest)
  layer=np.array(Image.open(dest/'layer.png'));own=np.array(Image.open(dest/'owner-mask.png'))>0;xy=np.load(dest/'source-xy.npy',allow_pickle=False);tmap=np.load(dest/'triangle-index.npy',allow_pickle=False);src=np.array(Image.open(donor));assert np.array_equal(layer[own],src[xy[own,1],xy[own,0]])
  known=P/('torso-new-owner.png' if part=='torso' else 'new-far-arm-owner.png');pin(known);visible=np.array(Image.open(known))>0
  if part=='torso':
   flare=P/'new-flare-owner.png';pin(flare);visible &= ~(np.array(Image.open(flare))>0)
  final=P/'composite.png';pin(final);a=np.array(Image.open(final));assert np.all(~visible|own);assert np.array_equal(layer[visible],a[visible]);journal=P/'PIXEL-JOURNAL.json';pin(journal);samples=[j for j in json.loads(journal.read_text()) if j.get('source_sample',{}).get('part')==part];assert samples
  for j in samples:
   x,y=j['xy'];w=j['source_sample'];assert xy[y,x].tolist()==w['source_xy'];assert layer[y,x].tolist()==j['after']==w['rgba']
  real.append({'phase':phase,'part':part,'spec':str(specpath),'call':call,'actual_frozen_visible_RGBA_samples_exact':int(visible.sum()),'actual_frozen_journal_sourceXY_and_RGBA_exact':len(samples),'all_owned_output_RGBA_equal_actual_source_at_witness_map':True,'no_producer_import_or_execution':True,'comparison_limit':'Known visible layer samples only; no claim of full-body compositor equivalence, hidden underpaint or art quality.'})
 # Independent known-answer arbitrary4x3 RGBA fixture: unique RGB, partial alpha,
 # owned alpha0 with nonzero RGB, and integer translation against array slicing.
 tiny=O/'tiny';tiny.mkdir();a=np.arange(48,dtype=np.uint8).reshape(3,4,4)*5;a[:,:,3]=255;a[1,1,3]=93;a[2,2,3]=0;Image.fromarray(a).save(tiny/'donor.png');Image.fromarray(np.full((3,4),255,np.uint8)).save(tiny/'owner.png');base={'schema':'nearest-part-warp/v1','canvas':[4,3],'donor':{'path':str(tiny/'donor.png'),'sha256':sha(tiny/'donor.png')},'owner_mask':{'path':str(tiny/'owner.png'),'sha256':sha(tiny/'owner.png')},'source_vertices':[[0,0],[3,0],[3,2],[0,2]],'target_vertices':[[0,0],[3,0],[3,2],[0,2]],'triangles':[[0,1,2],[0,2,3]],'alpha_mode':'copy-owned'}
 dump(tiny/'identity.json',base);invoke(tiny/'identity.json',tiny/'identity');r=np.array(Image.open(tiny/'identity/layer.png'));assert np.array_equal(r,a);assert np.all(np.array(Image.open(tiny/'identity/owner-mask.png'))==255)
 shifted=copy.deepcopy(base);shifted['target_vertices']=[[x+1,y] for x,y in shifted['target_vertices']];dump(tiny/'translation.json',shifted);invoke(tiny/'translation.json',tiny/'translation');expected=np.zeros_like(a);expected[:,1:]=a[:,:-1];assert np.array_equal(np.array(Image.open(tiny/'translation/layer.png')),expected)
 nonzero=copy.deepcopy(base);nonzero['alpha_mode']='nonzero-only';dump(tiny/'nonzero.json',nonzero);invoke(tiny/'nonzero.json',tiny/'nonzero');r=np.array(Image.open(tiny/'nonzero/layer.png'));expect=a.copy();expect[2,2]=0;assert np.array_equal(r,expect);assert np.array(Image.open(tiny/'nonzero/owner-mask.png'))[2,2]==0
 # Known source-coordinate clipping case; log counts must observe rejected samples.
 sourceclip=copy.deepcopy(base);sourceclip['source_vertices']=[[x-1,y] for x,y in sourceclip['source_vertices']];dump(tiny/'source-clip.json',sourceclip);invoke(tiny/'source-clip.json',tiny/'source-clip');assert np.array_equal(np.array(Image.open(tiny/'source-clip/layer.png')),expected);clipreceipt=json.loads((tiny/'source-clip/receipt.json').read_text());assert sum(t['source_outside_canvas_samples'] for t in clipreceipt['triangle_statistics'])>0
 # Explicit overlap order: two target triangles sample different source locations.
 overlap=copy.deepcopy(base);overlap['source_vertices']=[[0,0],[1,0],[0,1],[2,1],[3,1],[2,2]];overlap['target_vertices']=[[0,0],[1,0],[0,1],[0,0],[1,0],[0,1]];overlap['triangles']=[[0,1,2],[3,4,5]];dump(tiny/'overlap.json',overlap);invoke(tiny/'overlap.json',tiny/'overlap');r=np.array(Image.open(tiny/'overlap/layer.png'));xy=np.load(tiny/'overlap/source-xy.npy',allow_pickle=False);assert r[0,0].tolist()==a[1,2].tolist();assert xy[0,0].tolist()==[2,1]
 # Contract failures, not a mirror suite of implementation internals.
 bad=[]
 for name,mutate in [
 ('stalehash',lambda q:q['donor'].update(sha256='0'*64)),
 ('badindex',lambda q:q.update(triangles=[[0,1,99]])),
 ('degenerate',lambda q:q.update(triangles=[[0,1,1]])),
 ('fold',lambda q:q.update(target_vertices=[[0,0],[0,2],[3,0],[3,2]])),
 ('nan',lambda q:q['source_vertices'][0].__setitem__(0,float('nan'))),
 ('canvas',lambda q:q.update(canvas=[5,3]))]:
  q=copy.deepcopy(base);mutate(q);p=tiny/f'bad-{name}.json';dump(p,q);call=invoke(p,tiny/f'refused-{name}',False);bad.append({'case':name,**call,'no_output_created':True})
 existing=tiny/'already-exists';existing.mkdir();sentinel=existing/'sentinel';sentinel.write_text('preserve\n');p=subprocess.run([sys.executable,str(HERE/'warp_part.py'),str(tiny/'identity.json'),'--out',str(existing)],capture_output=True,text=True);assert p.returncode==2;assert list(existing.iterdir())==[sentinel] and sentinel.read_text()=='preserve\n';bad.append({'case':'existing output','returncode':p.returncode,'stderr':p.stderr.strip(),'existing_sentinel_unchanged':True})
 # Nonbinary mask rejection binds its real hash so it reaches mask validation.
 badmask=np.full((3,4),255,np.uint8);badmask[0,0]=127;Image.fromarray(badmask).save(tiny/'nonbinary.png');q=copy.deepcopy(base);q['owner_mask']={'path':str(tiny/'nonbinary.png'),'sha256':sha(tiny/'nonbinary.png')};dump(tiny/'bad-owner.json',q);bad.append({'case':'nonbinary owner',**invoke(tiny/'bad-owner.json',tiny/'refused-owner',False),'no_output_created':True})
 assert all(sha(Path(p))==h for p,h in pins.items());dump(O/'SOURCE-PINS.json',pins);dump(O/'VALIDATION.json',{'actual_frozen_evidence':real,'tiny_known_answer':{'canvas':[4,3],'identity_all_RGBA_including_hidden_RGB_and_partial_alpha_exact':True,'integer_translation_clipped_exact':True,'source_outside_canvas_samples_logged_and_skipped':True,'nonzero_alpha_mode_partial_alpha_exact_alpha0_skipped':True,'last_valid_owned_triangle_wins_with_sourceXY_exact':True},'contract_rejections':bad,'all_read_only_sources_unchanged':True,'source_code_under_test_sha256':sha(HERE/'warp_part.py'),'tool_versions':{'Python':sys.version,'NumPy':np.__version__,'Pillow':Image.__version__}});print(json.dumps({'real_samples':[(r['part'],r['actual_frozen_visible_RGBA_samples_exact'],r['actual_frozen_journal_sourceXY_and_RGBA_exact']) for r in real],'tiny_checks':5,'reject_cases':len(bad)}))

if __name__=='__main__':main()
