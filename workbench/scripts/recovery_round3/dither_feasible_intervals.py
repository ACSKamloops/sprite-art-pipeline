#!/usr/bin/env python3
"""Offline few-hypothesis interval tests, not a PixelLab method or service client."""
import base64,hashlib,json,math
from pathlib import Path
from io import BytesIO
import numpy as np
from PIL import Image
OLD=Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014')
NEW=Path('/home/astra/artifacts/pixellab-dither-followup-20261014')
CASES=[(OLD/'fixed-2x2',5,2,False),(Path(str(OLD)+'-phase2')/'bw-2x2-ten',10,2,False),(NEW/'gray-context-2x2',5,2,True),(NEW/'epsilon-2x2',.000001,2,False),(NEW/'cube-4x4',5,4,False)]
B2=np.array([[0,2],[3,1]])
B4=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
def sha(b):return hashlib.sha256(b).hexdigest()
def decode(v):
 raw=base64.b64decode(v['base64'].split(',')[-1],validate=True)
 with Image.open(BytesIO(raw)) as im:return raw,np.array(im.convert('RGBA'))
def inputs():
 records=[];cols={k:[] for k in ['rgb','white','strength','rank','side','gray','old','case','x','y']}
 for index,(p,strength,side,gray_only) in enumerate(CASES):
  qb=(p/'request.json').read_bytes();rb=(p/'response.json').read_bytes();q=json.loads(qb);r=json.loads(rb)
  if q['dithering_strength']!=strength or q['dithering']!=f'{side}x{side}':raise ValueError('Controls differ')
  raw,a=decode(q['images'][0]);ret,b=decode(r['images'][0]);raw2,a2=decode(q['images'][1]);ret2,b2=decode(r['images'][1]);palraw,pal=decode(q['palette_image'])
  if pal.reshape(-1,4).tolist()!=[[0,0,0,255],[255,255,255,255]]:raise ValueError('Palette differs')
  if ret!=(p/'output-00.png').read_bytes() or ret2!=(p/'output-01.png').read_bytes():raise ValueError('Return byte binding differs')
  if a.shape!=b.shape or a2.shape!=b2.shape:raise ValueError('Canvas differs')
  if not np.array_equal(a[:,:,:3],a2[:,:,:3]) or not np.array_equal(b[:,:,:3],b2[:,:,:3]):raise ValueError('Alpha-repeat RGB differs')
  if not np.array_equal(a[:,:,3],b[:,:,3]) or not np.array_equal(a2[:,:,3],b2[:,:,3]):raise ValueError('Alpha differs')
  if np.any(~np.isin(b[:,:,:3],[0,255])) or not np.array_equal(b[:,:,0],b[:,:,1]) or not np.array_equal(b[:,:,0],b[:,:,2]):raise ValueError('Non-BW result')
  y,x=np.indices(a.shape[:2]);B=B2 if side==2 else B4;n=a.shape[0]*a.shape[1]
  for k,v in {'rgb':a[:,:,:3].reshape(-1,3).astype(float),'white':b[:,:,0].reshape(-1)>0,'strength':np.full(n,strength),'rank':B[y%side,x%side].reshape(-1),'side':np.full(n,side),'gray':np.ones(n,dtype=bool) if gray_only else y.reshape(-1)>=16,'old':np.full(n,index<2),'case':np.full(n,index),'x':x.reshape(-1),'y':y.reshape(-1)}.items():cols[k].append(v)
  records.append({'path':str(p),'request_sha256':sha(qb),'response_sha256':sha(rb),'source_pointer':'/images/0/base64','returned_pointer':'/images/0/base64','source_png_sha256':sha(raw),'returned_png_sha256':sha(ret),'alpha_repeat_source_sha256':sha(raw2),'alpha_repeat_returned_sha256':sha(ret2),'palette_png_sha256':sha(palraw),'first_frame_observations':n,'both_frames_alpha_exact':True,'both_frames_RGB_equal':True})
 return records,{k:np.concatenate(v) for k,v in cols.items()}
def example(i,data,records):
 return {'case':Path(records[int(data['case'][i])]['path']).name,'x':int(data['x'][i]),'y':int(data['y'][i]),'RGB':data['rgb'][i].astype(int).tolist(),'white':bool(data['white'][i]),'strength':float(data['strength'][i]),'rank':int(data['rank'][i]),'side':int(data['side'][i])}
def feasible(z,c,white,mask,data,records,tie_white=False):
 # Prediction is z+c*A>0 (or >=0 for bin boundary); A>=0.
 lower=0.;upper=math.inf;lo_open=False;hi_open=False;lo_i=hi_i=None;constant=[]
 for i in np.flatnonzero(mask):
  zz=float(z[i]);cc=float(c[i]);w=bool(white[i])
  if cc==0:
   pred=zz>=0 if tie_white else zz>0
   if pred!=w and len(constant)<2:constant.append(example(i,data,records)|{'margin':zz,'amplitude_coefficient':cc})
   continue
  boundary=-zz/cc
  is_lower=(w and cc>0) or (not w and cc<0)
  is_open=(w and not tie_white) or (not w and tie_white)
  if is_lower and (boundary>lower or boundary==lower and is_open and not lo_open):lower=boundary;lo_open=is_open;lo_i=i
  if not is_lower and (boundary<upper or boundary==upper and is_open and not hi_open):upper=boundary;hi_open=is_open;hi_i=i
 possible=not constant and (lower<upper or lower==upper and not(lo_open or hi_open))
 result={'feasible':bool(possible),'amplitude_lower':lower,'lower_open':lo_open,'amplitude_upper':upper if math.isfinite(upper) else None,'upper_open':hi_open,'lower_witness':None if lo_i is None else example(lo_i,data,records)|{'z':float(z[lo_i]),'c':float(c[lo_i])},'upper_witness':None if hi_i is None else example(hi_i,data,records)|{'z':float(z[hi_i]),'c':float(c[hi_i])},'constant_contradictions':constant,'observations':int(mask.sum())}
 if possible:
  chosen=(lower+upper)/2 if math.isfinite(upper) else lower+1
  pred=z+c*chosen>=0 if tie_white else z+c*chosen>0
  result.update({'example_amplitude':chosen,'replay_mismatches_in_scope':int(np.count_nonzero((pred!=white)&mask))})
 return result

def bin_transition(rgb,bits):
 # Exact integer noise at first white center-bin result. Monotone in equal RGB shift.
 step=2**(8-np.array(bits));lo=np.full(len(rgb),-256,dtype=int);hi=np.full(len(rgb),256,dtype=int)
 for _ in range(9):
  mid=(lo+hi)//2;v=np.clip(rgb+mid[:,None],0,255);representative=np.floor(v/step)*step+step/2
  white=representative.sum(1)>382.5;hi=np.where(white,mid,hi);lo=np.where(white,lo,mid)
 return hi.astype(float)
def main():
 records,d=inputs();rgb=d['rgb'];mean=rgb.mean(1);a=np.sqrt(np.sum(rgb**2,axis=1));b=np.sqrt(np.sum((255-rgb)**2,axis=1));variance=np.mean((rgb-mean[:,None])**2,axis=1)
 metrics={'RGB_mean_equiv_squared_distance_difference':mean,'euclidean_distance_ratio':255*a/(a+b),'squared_distance_ratio':255*a*a/(a*a+b*b),'euclidean_distance_difference':127.5+(a-b)/(2*np.sqrt(3)),'channel_variance_normalized_mean':127.5+(mean-127.5)/(1+variance/(255**2/4))}
 scopes={'all_five_cases':np.ones(len(rgb),dtype=bool),'prior_strength5_gray':(d['case']==0)&d['gray'],'prior_strength10_gray':(d['case']==1)&d['gray'],'both_prior_gray':d['old']&d['gray'],'all_gray':d['gray'],'prior_cube':d['old']&~d['gray']}
 rows=[]
 for convention in ['centered','offset1','rank0']:
  phase=(d['rank']+({'centered':.5,'offset1':1,'rank0':0}[convention]))/d['side']**2-.5;c=d['strength']*phase
  for name,score in metrics.items():
   rows.append({'hypothesis':name,'Bayer_convention':convention,'formula':'score(RGB)-127.5 + A*strength*((rank+offset)/side²-0.5) > 0','free_parameters':['one nonnegative amplitude A, shared across cases'],'scopes':{scope:feasible(score-127.5,c,d['white'],mask,d,records) for scope,mask in scopes.items()}})
 bins=[];c=d['strength']*((d['rank']+.5)/d['side']**2-.5)
 for bits in [(5,5,5),(5,6,5),(6,6,6)]:
  threshold=bin_transition(rgb,bits)
  step=2**(8-np.array(bits))
  def direct(noise,rounding):
   values=np.clip(rgb+noise[:,None],0,255)
   values=np.rint(values) if rounding else np.floor(values)
   return (np.floor(values/step)*step+step/2).sum(1)>382.5
  if np.any(direct(threshold-1,False)) or not np.all(direct(threshold,False)):raise ValueError('Integer bin transition boundary differs')
  if np.any(direct(threshold-.5000001,True)) or not np.all(direct(threshold-.5,True)):raise ValueError('Nearest-even bin transition boundary differs')
  for rounding in ['truncate','nearest_even']:
   q=threshold if rounding=='truncate' else threshold-.5
   bins.append({'bits':bits,'rounding_before_bins':rounding,'representative':'fixed midpoint','Bayer_convention':'centered','transition_formula':'clip RGB+noise, uint8 rounding, floor into bins, bin-center RGB nearest black/white; white at noise>=integerTransition (minus0.5 for nearest-even)','scopes':{scope:feasible(-q,c,d['white'],mask,d,records,True) for scope,mask in scopes.items()}})
 # A pure input-bin-and-phase lookup cannot distinguish these two observed pixels.
 collisions=[]
 for bits in [(4,4,4),(5,5,5),(5,6,5),(6,6,6)]:
  step=2**(8-np.array(bits));seen={};found=None
  for i in np.flatnonzero(d['case']==0):
   key=(*np.floor(rgb[i]/step).astype(int),int(d['rank'][i]))
   if key in seen and d['white'][seen[key]]!=d['white'][i]:found=[example(seen[key],d,records),example(i,d,records)];break
   seen[key]=i
  collisions.append({'bits':bits,'same_input_bin_and_phase_opposite_outputs':found,'boundary':'Rejects a deterministic lookup using only this unperturbed bin+phase; not all post-noise bins, caches, exact-RGB adaptive maps or context.'})
 proofs={'phase_linear_strength':{'white_witness':{'case':'fixed-2x2','x':129,'y':17,'gray':129,'strength':5},'black_witness':{'case':'bw-2x2-ten','x':131,'y':17,'gray':131,'strength':10},'assumption':'white iff gray-127.5 + strength*n >0, same phase coefficient n across strengths','n_lower_strict':'-3/10','n_upper_closed':'-7/20','conclusion':'empty interval, lower exceeds upper by1/20; not a rounding/tie equality'},'centered_single_strength':{'white_low_gray':122,'white_high_gray':129,'strength':5,'rank_low_gray':3,'rank_high_gray':1,'A_lower_strict':'44/15','A_upper_strict':'12/5','conclusion':'empty interval, lower exceeds upper by8/15'}}
 for case,x,y,w in [(0,129,17,True),(1,131,17,False),(0,122,17,True)]:
  ids=np.flatnonzero((d['case']==case)&(d['x']==x)&(d['y']==y))
  if len(ids)!=1 or bool(d['white'][ids[0]])!=w or d['rgb'][ids[0]].tolist()!=[x,x,x]:raise ValueError('Exact witness differs')
 result={'version':1,'exact_gray_counterexamples':proofs,'classification':'few-hypothesis offline interval falsification, not private source recovery','script_sha256':sha(Path(__file__).read_bytes()),'bindings':records,'fit_observations':len(rgb),'alpha_repeated_frames_used_for_fit':False,'float_boundary_policy':'Double precision, reported endpoints as computed; exact rational gray counterexample derived separately in report; no numerical infeasibility promoted to general uniqueness proof','pointwise_hypotheses':rows,'post_noise_bin_hypotheses':bins,'post_noise_bin_boundaries_checked_against_direct_processing':True,'unperturbed_bin_collisions':collisions,'exact_global_fit_candidates':[{k:v for k,v in r.items() if k!='scopes'} for r in rows+bins if r['scopes']['all_five_cases']['feasible']],'provider_calls':0,'credentials_loaded':False,'private_method_recovered':False}
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
