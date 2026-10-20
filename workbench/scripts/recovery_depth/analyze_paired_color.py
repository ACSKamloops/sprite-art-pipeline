#!/usr/bin/env python3
"""Bounded read-only capture scan and measurements. New private output dir only."""
import argparse,base64,hashlib,json
from pathlib import Path
from io import BytesIO
from collections import Counter,defaultdict
import numpy as np
from PIL import Image
R=Path('/home/astra/projects/pixellab-local-test-20261011')
ROOTS=[R/'runtime/probes',R/'runtime/captures',R/'depth-round2',Path('/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014')]
DENY=['credential','cookie','token','secret','profile','auth','balance']
INTEREST={'original_images','original_image','quantized_images','quantized_image','drift_threshold'}
def sha(b):return hashlib.sha256(b).hexdigest()
def ptr(k):return str(k).replace('~','~0').replace('/','~1')
def walk(x,p='',parsed=0):
 if isinstance(x,dict):
  yield p,x
  for k,v in x.items():
   if k in ['headers','cookies','base64','authorization']:continue
   yield from walk(v,p+'/'+ptr(k),parsed)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,p+'/'+str(i),parsed)
 elif isinstance(x,str) and parsed<2 and x[:1] in ['{','[']:
  try:y=json.loads(x)
  except ValueError:return
  yield from walk(y,p+'::<JSON>',parsed+1)
def arr(x):return x if isinstance(x,list) else [x]
def decode(d):
 if not isinstance(d,dict) or 'base64' not in d:raise ValueError('No typed base64 descriptor')
 b=base64.b64decode(d['base64'].split(',')[-1],validate=True)
 with Image.open(BytesIO(b)) as im:
  if im.format!='PNG':raise ValueError('Only retained PNGs decoded')
  return b,np.array(im.convert('RGBA'))
def lab(rgb):
 s=np.asarray(rgb,dtype=float)/255;s=np.where(s<=.04045,s/12.92,((s+.055)/1.055)**2.4)
 l=np.cbrt(s@np.array([[.4122214708,.5363325363,.0514459929],[.2119034982,.6806995451,.1073969566],[.0883024619,.2817188376,.6299787005]]).T)
 return l@np.array([[.2104542553,.7936177850,-.0040720468],[1.9779984951,-2.4285922050,.4505937099],[.0259040371,.7827717662,-.8086757660]]).T
def colorstats(x):
 flat=x.reshape(-1,4);v=flat[flat[:,3]>0]
 return {'rgba_colors_all':len(np.unique(flat,axis=0)),'rgb_colors_alpha_positive':len(np.unique(v[:,:3],axis=0)),'alpha_values':np.unique(flat[:,3]).tolist(),'visible_pixels':len(v)}
def affine(x,y):
 if not len(x):return None
 a=np.column_stack([x,np.ones(len(x))]);coef,_,rank,_=np.linalg.lstsq(a,y,rcond=None);pred=a@coef
 return {'least_squares_RGB_3x3_plus_bias':coef.tolist(),'design_rank':int(rank),'per_channel_rmse':np.sqrt(np.mean((pred-y)**2,axis=0)).tolist(),'max_abs_channel_residual':float(np.max(np.abs(pred-y))),'rounded_clipped_exact_fraction':float(np.mean(np.all(np.clip(np.rint(pred),0,255)==y,axis=1))),'boundary':'Descriptive fit on observed co-located visible pixels; not a recovered transform or independent heldout validation'}
def measure(a,b):
 if a.shape!=b.shape:return {'same_shape':False,'a_shape':a.shape,'b_shape':b.shape}
 f=a.reshape(-1,4);g=b.reshape(-1,4);vis=(f[:,3]>0)&(g[:,3]>0);x=f[vis,:3];y=g[vis,:3]
 pairs=np.unique(np.column_stack([x,y]),axis=0);counts=Counter(map(tuple,pairs[:,:3]));palette=np.unique(y,axis=0)
 mism=0;unweighted=0;srgb=0
 if len(palette) and len(palette)<=1024:
  pl=lab(palette)
  for start in range(0,len(x),4096):
   d=lab(x[start:start+4096])[:,None,:]-pl[None,:,:];idx=np.argmin(np.sum(d*d*np.array([.25,1,1]),axis=2),axis=1)
   mism+=int(np.count_nonzero(np.any(palette[idx]!=y[start:start+4096],axis=1)))
   ui=np.argmin(np.sum(d*d,axis=2),axis=1);unweighted+=int(np.count_nonzero(np.any(palette[ui]!=y[start:start+4096],axis=1)))
   raw=x[start:start+4096].astype(float)[:,None,:]-palette[None,:,:].astype(float)
   si=np.argmin(np.sum(raw*raw,axis=2),axis=1);srgb+=int(np.count_nonzero(np.any(palette[si]!=y[start:start+4096],axis=1)))
 else:mism=None;unweighted=None;srgb=None
 return {'same_shape':True,'size':[a.shape[1],a.shape[0]],'rgba_exact':bool(np.array_equal(a,b)),'alpha_mismatches':int(np.count_nonzero(f[:,3]!=g[:,3])),'alpha_positive_support_mismatches':int(np.count_nonzero((f[:,3]>0)!=(g[:,3]>0))),'RGB_mismatches_all':int(np.count_nonzero(np.any(f[:,:3]!=g[:,:3],axis=1))),'co_visible_pixels':len(x),'RGB_mismatches_co_visible':int(np.count_nonzero(np.any(x!=y,axis=1))),'changed_hidden_RGB_alpha0_both':int(np.count_nonzero((f[:,3]==0)&(g[:,3]==0)&np.any(f[:,:3]!=g[:,:3],axis=1))),'main':colorstats(a),'processed':colorstats(b),'same_main_RGB_multiple_processed_RGB_count':sum(n>1 for n in counts.values()),'visible_unique_RGB_pair_count':len(pairs),'weighted_Oklab_nearest_observed_output_palette_mismatches':mism,'unweighted_Oklab_nearest_observed_output_palette_mismatches':unweighted,'sRGB_nearest_observed_output_palette_mismatches':srgb,'palette_candidate_boundary':'Observed output palette reused as candidate only; no supplied-palette/private-reducer identity or independent prediction','affine_visible':affine(x.astype(float),y.astype(float))},pairs

def run(out):
 out.mkdir(parents=True,exist_ok=False);inventory=[];hits=[];controls=[];snapshots=[];errors=[]
 for root in ROOTS:
  for p in sorted(root.rglob('*')):
   if not p.is_file() or p.suffix not in ['.json','.har','.jsonl'] or any(t in '/'.join(p.relative_to(root).parts).lower() for t in DENY) or 'openapi' in p.name.lower():continue
   raw=p.read_bytes();inventory.append({'path':str(p),'sha256':sha(raw),'bytes':len(raw)})
   try:values=[(f'/line/{i+1}',json.loads(l)) for i,l in enumerate(raw.splitlines()) if l] if p.suffix=='.jsonl' else [('',json.loads(raw))]
   except ValueError:errors.append({'path':str(p),'reason':'JSON parse failure'});continue
   for prefix,value in values:
    for pointer,d in walk(value,prefix):
     for key in d:
      if key=='drift_threshold' or 'palette' in key.lower():
       controls.append({'path':str(p),'file_sha256':sha(raw),'pointer':pointer+'/'+ptr(key),'type':type(d[key]).__name__,'value':d[key] if isinstance(d[key],(int,float,bool)) else None})
     found=INTEREST&d.keys()
     if found:hits.append({'path':str(p),'sha256':sha(raw),'pointer':pointer,'variant_keys':sorted(found),'counts':{k:len(arr(d[k])) for k in found if k!='drift_threshold'}})
     for first,second in [('images','quantized_images'),('image','quantized_image'),('original_images','images'),('original_image','image')]:
      if first not in d or second not in d:continue
      aa,bb=arr(d[first]),arr(d[second])
      if not aa or len(aa)!=len(bb):errors.append({'path':str(p),'pointer':pointer,'reason':'Pair count unequal/empty'});continue
      try:decoded=[(decode(a),decode(b)) for a,b in zip(aa,bb)]
      except (ValueError,OSError):errors.append({'path':str(p),'pointer':pointer,'reason':'Pair descriptors not decoded as PNG'});continue
      # Same returned arrays may recur in progress and completed polls.
      fingerprint=sha(json.dumps([[sha(a[0]),sha(b[0])] for a,b in decoded]).encode())
      snapshots.append({'path':str(p),'file_sha256':sha(raw),'pointer':pointer,'first_key':first,'second_key':second,'job_id':value.get('id') if isinstance(value,dict) else None,'status':value.get('status') if isinstance(value,dict) else None,'fingerprint':fingerprint,'decoded':decoded,'reported_color_counts':{k:d[k] for k in ['original_image_n_colors','quantized_image_n_colors'] if k in d},'metadata':{k:d[k] for k in ['generation_model','frame_count','number_of_frames','frame_index'] if k in d}})
 grouped=defaultdict(list)
 for s in snapshots:grouped[s['fingerprint']].append(s)
 results=[]
 for i,(_,ss) in enumerate(sorted(grouped.items(),key=lambda pair:pair[1][-1]['path'])):
  s=max(ss,key=lambda x:(x['path'].endswith('-response.json'),x['path']));folder=out/f'pair-{i:02}';folder.mkdir();frames=[];globalpairs=[]
  for j,(a,b) in enumerate(s['decoded']):
   for label,item in [('main',a),('processed',b)]:
    path=folder/f'{label}-{j:02}.png';path.write_bytes(item[0])
   measured=measure(a[1],b[1])
   if isinstance(measured,tuple):m,pairs=measured;globalpairs.extend((tuple(x[:3]),tuple(x[3:]),j) for x in pairs)
   else:m=measured
   frames.append({'index':j,'main_pointer':s['pointer']+'/'+s['first_key']+(('/'+str(j)) if s['first_key'].endswith('s') else ''),'processed_pointer':s['pointer']+'/'+s['second_key']+(('/'+str(j)) if s['second_key'].endswith('s') else ''),'main_png_sha256':sha(a[0]),'processed_png_sha256':sha(b[0]),'PNG_bytes_exact':a[0]==b[0],'measurements':m})
  colors=defaultdict(lambda:defaultdict(set))
  for x,y,j in globalpairs:colors[x][j].add(y)
  shared={x:fs for x,fs in colors.items() if len(fs)>1}
  conflict=sum(len(set().union(*fs.values()))>1 for fs in shared.values())
  canonical=Path(s['path']);request=canonical.parent/'request.json';accept=canonical.parent/'001-response.json'
  job_binding={}
  if request.exists() and accept.exists():
   rb=request.read_bytes();ab=accept.read_bytes();rq=json.loads(rb);accepted=json.loads(ab)
   ids=accepted.get('background_job_ids',[accepted.get('background_job_id')]);ids=list(ids.values()) if isinstance(ids,dict) else ids
   job_binding={'request_path':str(request),'request_sha256':sha(rb),'request_endpoint':rq.get('endpoint'),'request_body_fields':list(rq.get('body',{})),'drift_threshold_explicit':'drift_threshold' in rq.get('body',{}),'acceptance_path':str(accept),'acceptance_sha256':sha(ab),'job_id_matches_acceptance':s['job_id'] in ids}
  (folder/'RGB-PAIRS.json').write_text(json.dumps([{'main_RGB':list(map(int,x)),'processed_RGB':list(map(int,y)),'frame':j} for x,y,j in globalpairs],indent=2)+'\n')
  mainunion=set();processedunion=set()
  for a,b in s['decoded']:
   for image,union in [(a[1],mainunion),(b[1],processedunion)]:
    f=image.reshape(-1,4);union.update(map(tuple,np.unique(f[f[:,3]>0,:3],axis=0).tolist()))
  results.append({k:v for k,v in s.items() if k!='decoded'}|{'retained_same_arrays_snapshots':[{k:x[k] for k in ['path','file_sha256','pointer','job_id','status']} for x in ss],'private_extraction':str(folder),'job_binding':job_binding,'RGB_pairs_sha256':sha((folder/'RGB-PAIRS.json').read_bytes()),'frames':frames,'sequence':{'frame_count':len(frames),'union_main_visible_RGB_colors':len(mainunion),'union_processed_visible_RGB_colors':len(processedunion),'shared_main_RGB_across_frames':len(shared),'shared_main_RGB_with_differing_processed_RGB_across_frames':conflict,'boundary':'Index pairing is declared-array order and co-location, not a proved internal processing stage, native source timeline or foreground correspondence across moving frames.'}})
 ledger={'version':1,'scope_roots':list(map(str,ROOTS)),'excluded_name_substrings':DENY,'excluded_formats':'All non-json/har/jsonl; openapi snapshots; no profile/session-history/credential store scan','script_sha256':sha(Path(__file__).read_bytes()),'scanned_files':len(inventory),'scanned_bytes':sum(x['bytes'] for x in inventory),'parse_or_decode_qualifications':errors,'variant_field_hits':hits,'palette_or_drift_fields':controls,'unique_paired_array_snapshots':len(results),'pairs':results,'private_inventory':str(out/'INVENTORY.json'),'model_or_provider_calls':0,'private_deflicker_recovered':False}
 (out/'INVENTORY.json').write_text(json.dumps(inventory,indent=2)+'\n');(out/'MEASUREMENTS.json').write_text(json.dumps(ledger,indent=2)+'\n');return ledger
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args();d=run(args.output)
 print(json.dumps({'scanned_files':d['scanned_files'],'pairs':d['unique_paired_array_snapshots'],'qualifications':d['parse_or_decode_qualifications'],'pairs_metadata':[{'path':x['path'],'frame_count':len(x['frames']),'alpha_mismatches':[f['measurements'].get('alpha_mismatches') for f in x['frames']],'RGB_mismatches':[f['measurements'].get('RGB_mismatches_co_visible') for f in x['frames']],'conflicts':x['sequence']['shared_main_RGB_with_differing_processed_RGB_across_frames']} for x in d['pairs']]}))
