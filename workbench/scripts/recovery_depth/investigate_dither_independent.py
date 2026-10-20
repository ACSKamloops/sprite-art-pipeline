#!/usr/bin/env python3
"""Bounded offline dither cache/bin hypotheses; no provider imports or art claims."""
from pathlib import Path
from io import BytesIO
import base64,hashlib,json
from collections import defaultdict
import numpy as np
from PIL import Image
from scipy.optimize import linprog
import scipy
R=Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014')
CASES=[(R/'fixed-2x2',5),(Path(str(R)+'-phase2')/'bw-2x2-ten',10)]
def sha(b):return hashlib.sha256(b).hexdigest()
def decode(v):
 b=base64.b64decode(v['base64'].split(',')[-1],validate=True)
 return b,np.array(Image.open(BytesIO(b)).convert('RGBA'))
def load():
 cases=[]
 for p,strength in CASES:
  rb=(p/'request.json').read_bytes();d=json.loads(rb);sources=[];targets=[];pins=[]
  response=json.loads((p/'response.json').read_bytes())
  if d['dithering']!='2x2' or d['dithering_strength']!=strength:raise ValueError('Prior dither controls differ')
  palette_raw,palette=decode(d['palette_image'])
  if palette.reshape(-1,4).tolist()!=[[0,0,0,255],[255,255,255,255]]:raise ValueError('Prior palette differs')
  for i in range(2):
   raw,a=decode(d['images'][i]);ret,b=decode(response['images'][i]);out=(p/f'output-{i:02}.png').read_bytes()
   if ret!=out:raise ValueError('Output bytes differ')
   sources.append(a);targets.append(b);pins.append({'frame':i,'source_png_sha256':sha(raw),'returned_png_sha256':sha(ret)})
  cases.append({'path':str(p),'strength':strength,'request_sha256':sha(rb),'palette_png_sha256':sha(palette_raw),'response_sha256':sha((p/'response.json').read_bytes()),'pins':pins,'sources':sources,'targets':targets})
 return cases

def predict(source,strength,offset,rounding,bits,mapper):
 yy,xx=np.indices(source.shape[:2]);rank=np.array([[0,2],[3,1]])[yy%2,xx%2]
 v=np.clip(source[:,:,:3].astype(float)+((rank+offset)/4-.5)[:,:,None]*strength*3,0,255)
 if rounding=='trunc':v=np.floor(v)
 elif rounding=='round':v=np.rint(v)
 shape=v.shape;f=v.reshape(-1,3)
 if mapper.startswith('pre-'):
  step=np.array([2**(8-n) for n in bits]);keys=np.floor(source[:,:,:3]/step)
  rep=mapper[4:]
  pre=keys*step+step/2 if rep=='center' else keys*step if rep=='lower' else keys*255/(2**np.array(bits)-1)
  moved=np.clip(pre+((rank+offset)/4-.5)[:,:,None]*strength*3,0,255)
  if rounding=='trunc':moved=np.floor(moved)
  elif rounding=='round':moved=np.rint(moved)
  return moved.reshape(-1,3).sum(1)>382.5
 if mapper=='exact':return f.sum(1)>382.5
 step=np.array([2**(8-n) for n in bits]);keys=np.floor(f/step).astype(int)
 if mapper in ['center','lower','rescale']:
  representative=keys*step+step/2 if mapper=='center' else keys*step if mapper=='lower' else keys*255/(2**np.array(bits)-1)
  return representative.sum(1)>382.5
 # First-hit variants explicitly model cache state; no original GIF code imported.
 cache={};output=[];phase=(yy%2*2+xx%2).reshape(-1)
 for i,(key,color) in enumerate(zip(keys,f)):
  k=tuple(key) if mapper=='first-global' else (int(phase[i]),*np.floor(source[:,:,:3].reshape(-1,3)[i]/step).astype(int)) if mapper=='first-source-phase' else (int(phase[i]),*key)
  if k not in cache:cache[k]=color.sum()>382.5
  output.append(cache[k])
 return np.array(output)

def followup():
 root=Path('/home/astra/artifacts/pixellab-dither-followup-20261014');pb=(root/'PLAN.json').read_bytes()
 if sha(pb)!='771d4dfccafe8ddbaf7728a64682f5744a90ef5b8c0efd97b3008afb6f3daad4':raise ValueError('Followup PLAN identity differs')
 plan=json.loads(pb);cases=[]
 for name in ['gray-context-2x2','epsilon-2x2','cube-4x4']:
  p=root/name;qb=(p/'request.json').read_bytes();q=json.loads(qb);row=next(r for r in plan['requests'] if r['variant']==name)
  hb=(p/'network.har').read_bytes();h=json.loads(hb)['log']['entries'];response=json.loads((p/'response.json').read_bytes())
  if len(h)!=1 or sha(qb)!=row['request_sha256']:raise ValueError('Followup request/count differs')
  wire=h[0]['request']['postData']['text'].encode()
  if sha(wire)!=row['wire_sha256'] or json.loads(wire)!=q:raise ValueError('Wire binding differs')
  if h[0]['request']['method']!='POST' or h[0]['request']['url']!='https://api.pixellab.ai/v2/reduce-colors':raise ValueError('Captured endpoint differs')
  if json.loads(h[0]['response']['content']['text'])!=response or h[0]['response']['status']!=200:raise ValueError('Followup response differs')
  palette_raw,palette=decode(q['palette_image'])
  if palette.reshape(-1,4).tolist()!=[[0,0,0,255],[255,255,255,255]]:raise ValueError('Followup palette differs')
  sources=[];targets=[];pins=[]
  for i in range(2):
   sb,a=decode(q['images'][i]);tb,b=decode(response['images'][i])
   if tb!=(p/f'output-{i:02}.png').read_bytes():raise ValueError('Followup output bytes differ')
   sources.append(a);targets.append(b);pins.append({'frame':i,'source_png_sha256':sha(sb),'output_png_sha256':sha(tb),'alpha_exact':bool(np.array_equal(a[:,:,3],b[:,:,3]))})
  rea=None
  if (p/'REA-EVIDENCE.json').exists():
   rr=json.loads((p/'REA-EVIDENCE.json').read_bytes())
   if rr['subject']['digest']['sha256']!=sha(hb):raise ValueError('REA subject differs')
   if rr['normalized_result']['total_records']!=1 or rr['normalized_result']['records'][0]['reported']!=h[0]:raise ValueError('REA normalized full reported record differs')
   rea={'evidence_id':rr['evidence_id'],'authority':rr['authority'],'file_sha256':sha((p/'REA-EVIDENCE.json').read_bytes())}
  cases.append({'path':str(p),'strength':q['dithering_strength'],'matrix':q['dithering'],'palette_png_sha256':sha(palette_raw),'request_sha256':sha(qb),'wire_sha256':sha(wire),'response_sha256':sha((p/'response.json').read_bytes()),'har_sha256':sha(hb),'pins':pins,'rea':rea,'sources':sources,'targets':targets})
 return cases,sha(pb)

def distance_ratio_candidates(old,new):
 rows=[]
 B2=np.array([[0,2],[3,1]]);B4=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
 for metric in ['mean','euclid-ratio','euclid-difference','squared-ratio','Linf-ratio']:
  for factor in [1.5,2,3,3.2,4,5,6]:
   for offset in [0,.5,1]:
    scores=[]
    for c in old+new:
     B=B4 if c.get('matrix')=='4x4' else B2
     for i,(a,b) in enumerate(zip(c['sources'],c['targets'])):
      v=a[:,:,:3].astype(float);d0=np.sqrt(np.sum(v*v,axis=2));d1=np.sqrt(np.sum((255-v)**2,axis=2))
      value=v.mean(2) if metric=='mean' else 255*d0/(d0+d1) if metric=='euclid-ratio' else 127.5+(d0-d1)/(2*np.sqrt(3)) if metric=='euclid-difference' else 255*d0*d0/(d0*d0+d1*d1) if metric=='squared-ratio' else 255*v.max(2)/(v.max(2)+(255-v).max(2))
      y,x=np.indices(value.shape);noise=((B[y%len(B),x%len(B)]+offset)/B.size-.5)*c['strength']*factor
      bad=(value+noise>127.5)!=(b[:,:,0]>0)
      scores.append({'case':Path(c['path']).name,'frame':i,'mismatches':int(bad.sum()),'first16_rows_mismatches':int(bad[:16].sum()),'last16_rows_mismatches':int(bad[16:].sum()),'exact_scalar_boundary_ties':int(np.count_nonzero(value+noise==127.5))})
    rows.append({'metric':metric,'factor':factor,'offset':offset,'prior_two_cases_mismatches':sum(s['mismatches'] for s in scores[:4]),'new_three_cases_mismatches':sum(s['mismatches'] for s in scores[4:]),'scores':scores})
 rows.sort(key=lambda r:r['prior_two_cases_mismatches']);return rows

def separator_margin(rgb,white):
 s=np.where(white,1.,-1.);a=np.column_stack([-s[:,None]*rgb/255,s,np.ones(len(s))])
 fit=linprog([0,0,0,0,-1],A_ub=a,b_ub=np.zeros(len(a)),A_eq=[[1,1,1,0,0]],b_eq=[1],bounds=[(0,None)]*3+[(None,None)]*2,method='highs')
 return {'solver_success':bool(fit.success),'max_normalized_margin':float(fit.x[-1]) if fit.success else None,'weights':fit.x[:3].tolist() if fit.success else None,'boundary':'Feasibility diagnostic for a single nonnegative RGB linear separator with sum weights1 and free intercept; not a server fit.'}

def run():
 cases=load();new,plan_sha=followup();structures=[]
 for c in cases:
  a=c['sources'][0];b=c['targets'][0];groups=defaultdict(set)
  for y in range(a.shape[0]):
   for x in range(a.shape[1]):groups[(*map(int,a[y,x,:3]),x%2,y%2)].add(int(b[y,x,0]))
  table=[]
  for yp in range(2):
   for xp in range(2):
    vals=b[16+yp,xp::2,0];xs=np.arange(xp,256,2);changes=np.where(vals[1:]!=vals[:-1])[0]+1
    cube=a[yp:16:2,xp::2,:3].reshape(-1,3).astype(int);white=b[yp:16:2,xp::2,0].reshape(-1)>0;total=cube.sum(1)
    interior=np.all((cube>=34)&(cube<=221),axis=1)
    table.append({'phase':[yp,xp],'gray_transition_x':xs[changes].tolist(),'max_black_input_sum':int(total[~white].max()),'min_white_input_sum':int(total[white].min()),'interior_max_black_sum':int(total[interior&~white].max()),'interior_min_white_sum':int(total[interior&white].min()),'cube_linear_separator':separator_margin(cube,white),'interior_linear_separator':separator_margin(cube[interior],white[interior])})
  structures.append({'case':c['path'],'same_RGB_and_2x2_phase_output_conflicts':sum(len(v)>1 for v in groups.values()),'gray_rows_repeat_every_two':bool(np.array_equal(b[16:30,:,:3],b[18:32,:,:3])),'alpha_exact_frames':[bool(np.array_equal(src[:,:,3],dst[:,:,3])) for src,dst in zip(c['sources'],c['targets'])],'RGB_outputs_same_opaque_and_alpha_frames':bool(np.array_equal(b[:,:,:3],c['targets'][1][:,:,:3])),'phase_constraints':table})
 rows=[]
 for offset in [.5,1.]:
  for rounding in ['float','trunc','round']:
   for bits,mapper in [(None,'exact')]+[(bits,mapper) for bits in [(4,4,4),(5,5,5),(5,6,5),(6,6,6)] for mapper in ['center','lower','rescale','first-global','first-phase','pre-center','pre-lower','pre-rescale','first-source-phase']]:
    scores=[]
    for c in cases:
     for i,(a,b) in enumerate(zip(c['sources'],c['targets'])):
      pred=predict(a,c['strength'],offset,rounding,bits,mapper).reshape(a.shape[:2]);bad=pred!=(b[:,:,0]>0)
      scores.append({'case':Path(c['path']).name,'frame':i,'mismatches':int(bad.sum()),'cube_mismatches':int(bad[:16].sum()),'gray_mismatches':int(bad[16:].sum())})
    rows.append({'offset':offset,'factor':3,'rounding':rounding,'bits':bits,'mapper':mapper,'mismatches':sum(s['mismatches'] for s in scores),'scores':scores})
 rows.sort(key=lambda r:r['mismatches'])
 gray=new[0];epsilon=new[1];four=new[2]
 context=[];epsilon_stats=[]
 for i in range(2):
  same=gray['targets'][i][:16]==cases[0]['targets'][i][16:]
  context.append({'frame':i,'phase_aligned_pixels':4096,'RGBA_mismatches':int(np.count_nonzero(np.any(~same,axis=2))),'gray_rows_repeat2':bool(np.array_equal(gray['targets'][i][:-2],gray['targets'][i][2:]))})
  none=np.array(Image.open(R/'fixed-none'/f'output-{i:02}.png').convert('RGBA'));a=epsilon['sources'][i];b=epsilon['targets'][i]
  baseline=(a[:,:,:3].astype(int).sum(2)>382.5)*255
  epsilon_stats.append({'frame':i,'RGB_nearest_mismatches':int(np.count_nonzero(np.any(b[:,:,:3]!=baseline[:,:,None],axis=2))),'none_png_sha256':sha((R/'fixed-none'/f'output-{i:02}.png').read_bytes()),'none_RGBA_mismatches':int(np.count_nonzero(np.any(b!=none,axis=2))),'alpha_exact':bool(np.array_equal(a[:,:,3],b[:,:,3]))})
 four_phase=[];b=four['targets'][0]
 for y in range(4):
  line=[]
  for x in range(4):
   values=b[16+y,x::4,0];xx=np.arange(x,256,4);changes=np.where(values[1:]!=values[:-1])[0]+1
   line.append({'phase':[y,x],'gray_transitions_x':xx[changes].tolist()})
  four_phase.append(line)
 ratio=distance_ratio_candidates(cases,new)
 gif=Path('/home/astra/projects/pixellab-local-test-20261011/website-art-bundles/4354-3a62375cb4c03823.js');gb=gif.read_bytes();gs=gb.index(b'function p(e,t,r="rgb565")');ge=gb.index(b'function g(',gs)
 gif_pin={'path':str(gif),'sha256':sha(gb),'function_UTF8_bytes_half_open':[gs,ge],'function_sha256':sha(gb[gs:ge]),'authority':'Original shipped GIF applyPalette helper; source retrace only in this pass, no server identity implied'}
 source=Path('/home/astra/artifacts/pixellab-recovery-web-20261014/pixelorama-shader-extracted/addons/gdgifexporter/lookup_similar.gdshader')
 return {'version':1,'script_sha256':sha(Path(__file__).read_bytes()),'scope':'Offline hypotheses on two already-retained strength5/10 black/white fixtures; not server source, heldout validation or exact processing claim','cases':[{k:v for k,v in c.items() if k not in ['sources','targets']} for c in cases],'structure':structures,'scipy_version':scipy.__version__,'candidate_count':len(rows),'formula':'Canonical Bayer((rank+offset)/4-.5)*strength*3 added equally to clipped sRGB, then rounding and exact/cache/bin mapper. Observed black/white output compared; alpha separately unchanged.','all_candidates':rows,'best':rows[0],'followup_PLAN_sha256':plan_sha,'followup_cases':[{k:v for k,v in c.items() if k not in ['sources','targets']} for c in new],'gray_context_comparison':context,'epsilon_comparison':epsilon_stats,'four_gray_phase_transitions':four_phase,'four_gray_period4':bool(np.array_equal(b[16:28],b[20:32])),'distance_ratio_candidate_count':len(ratio),'distance_ratio_candidates':ratio,'best_distance_ratio_on_prior':ratio[0],'distance_ratio_boundary':'Authored hypotheses, fitted to retained cases; new results were available during investigation. Not preregistered heldout validation or private source recovery.','GIF_helper_source':gif_pin,'shader_pin':{'path':str(source),'sha256':sha(source.read_bytes()),'lines_inclusive':[1,len(source.read_bytes().splitlines())]},'other_shader_pin':{'path':str(source.with_name('lookup_color.gdshader')),'sha256':sha(source.with_name('lookup_color.gdshader').read_bytes())},'model_or_provider_calls':0,'credentials_loaded':False}
if __name__=='__main__':print(json.dumps(run(),indent=2))
