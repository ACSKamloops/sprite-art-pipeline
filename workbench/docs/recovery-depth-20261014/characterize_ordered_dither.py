"""Bounded OFFLINE candidate comparison; inferred algorithms, not recovered source."""
from pathlib import Path
import hashlib,json,itertools,base64,subprocess
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
R1=Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014')
R2=Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014-phase2')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roots=[(R1/'fixed-2x2',5),(R2/'bw-2x2-ten',10)]
sources=[np.array(Image.open(R1/'inputs'/n).convert('RGBA')) for n in ['rgb-cube-gray.png','rgba-stripes.png']]
targets=[[np.array(Image.open(d/f'output-{i:02d}.png').convert('RGBA'))for i in range(2)] for d,_ in roots]
pal=Image.new('P',(2,1));pal.putpalette([0,0,0,255,255,255]);pal.putdata([0,1])

def predict(source, strength, params):
 b=np.array([[0,2],[3,1]],dtype=float)
 if params['transpose']:b=b.T
 y,x=np.indices(source.shape[:2]);noise=((b[y%2,x%2]+params['offset'])/4-.5)*strength*params['factor']
 rgb=np.clip(source[:,:,:3].astype(float)+noise[:,:,None],0,255)
 if params['rounding']=='round':rgb=np.rint(rgb)
 elif params['rounding']=='floor':rgb=np.floor(rgb)
 rgb=rgb.astype(np.uint8)
 if params['mapper']=='rgb-nearest':
  white=np.sum(rgb.astype(float),axis=2)>382.5;result=np.repeat((white.astype(np.uint8)*255)[:,:,None],3,axis=2)
 elif params['mapper']=='pillow-fixed':
  result=np.array(Image.fromarray(rgb).quantize(palette=pal,dither=Image.Dither.NONE).convert('RGB'))
 else:
  # Original GIF cache's packed565 first-hit mechanism, but deliberately authored
  # candidate (not original source). Squared RGB distance picks white iff sum>382.5.
  flat=rgb.reshape(-1,3);cache={};result=np.empty_like(flat)
  for i,(r,g,bv) in enumerate(flat):
   key=((int(r)>>3)<<11)|((int(g)>>2)<<5)|(int(bv)>>3)
   if key not in cache:cache[key]=255 if int(r)+int(g)+int(bv)>382.5 else 0
   result[i]=cache[key]
  result=result.reshape(rgb.shape)
 return np.concatenate([result,source[:,:,3:4]],axis=2)

def score(result,target):
 bad=np.any(result!=target,axis=2)
 ys,xs=np.where(bad)
 examples=[dict(x=int(x),y=int(y),predicted=result[y,x].tolist(),actual=target[y,x].tolist())for y,x in zip(ys[:4],xs[:4])]
 return dict(rgba_mismatches=int(bad.sum()),cube_mismatches=int(bad[:16].sum()),gray_mismatches=int(bad[16:].sum()),alpha_mismatches=int(np.count_nonzero(result[:,:,3]!=target[:,:,3])),counterexamples=examples)
rows=[]
for mapper,transpose,offset,factor,rounding in itertools.product(['rgb-nearest','pillow-fixed','gif565-cache'],[False,True],[0,.5,1],[1,2,3,3.2,4,5,8],['trunc','round','floor']):
 p=dict(mapper=mapper,transpose=transpose,offset=offset,factor=factor,rounding=rounding)
 scores=[]
 for case,(_,strength) in enumerate(roots):
  for i,s in enumerate(sources):scores.append(dict(case=roots[case][0].name,frame=i,**score(predict(s,strength,p),targets[case][i])))
 rows.append(dict(params=p,scores=scores,total_rgba_mismatches=sum(s['rgba_mismatches']for s in scores)))
rows.sort(key=lambda r:r['total_rgba_mismatches'])
best=rows[:12]
compact_rows=[dict(params=r['params'],total_rgba_mismatches=r['total_rgba_mismatches'],scores=[{k:v for k,v in score.items() if k!='counterexamples'}for score in r['scores']])for r in rows]
controls=[]
for i in range(2):
    a=R1/'fixed-none'/f'output-{i:02d}.png'
    b=R2/'bw-2x2-zero'/f'output-{i:02d}.png'
    controls.append(dict(frame=i,none_path=str(a),none_sha256=sha(a),zero_path=str(b),zero_sha256=sha(b),png_bytes_equal=a.read_bytes()==b.read_bytes(),rgba_equal=np.array_equal(np.array(Image.open(a)),np.array(Image.open(b)))))
request_bindings=[]
for d,strength in roots:
    req=json.loads((d/'request.json').read_text())
    entries=[]
    for i,image in enumerate(req['images']):
        value=image['base64'];raw=base64.b64decode(value.split(',',1)[-1] if value.startswith('data:') else value)
        source=R1/'inputs'/['rgb-cube-gray.png','rgba-stripes.png'][i]
        entries.append(dict(frame=i,request_png_sha256=hashlib.sha256(raw).hexdigest(),retained_source_png_sha256=sha(source),bytes_equal=raw==source.read_bytes()))
        assert raw==source.read_bytes()
    request_bindings.append(dict(case=d.name,declared_strength=req['dithering_strength'],declared_dithering=req['dithering'],images=entries))
thresholds=[]
for c,(d,strength) in enumerate(roots):
    a=targets[c][0];table=[]
    for y in [16,17]:
        row=[]
        for parity in [0,1]:
            xs=np.arange(parity,256,2);row.append(int(xs[a[y,xs,0]==255][0]))
        table.append(row)
    thresholds.append(dict(case=d.name,strength=strength,first_white_x_by_row_and_x_parity=table))
# Baseline: no added noise, independent of requested strength.
baselines=[]
for mapper in ['rgb-nearest','pillow-fixed','gif565-cache']:
 p=dict(mapper=mapper,transpose=False,offset=.5,factor=0,rounding='trunc')
 baselines.append(dict(params=p,scores=[dict(case=roots[c][0].name,frame=i,**score(predict(s,0,p),targets[c][i]))for c in range(2)for i,s in enumerate(sources)]))
pins=[]
for r in [R1,R2]:
 for f in sorted((r/'inputs').glob('*.png')):pins.append(dict(path=str(f),sha256=sha(f)))
for d,_ in roots:
 for f in [d/'request.json',d/'response.json',d/'network.har',d/'output-00.png',d/'output-01.png']:pins.append(dict(path=str(f),sha256=sha(f)))
# Cross-check the modeled GIF cache on the best such candidate using the unchanged
# shipped module. This validates the local cache model only, not server parity.
gif_best=next(r for r in rows if r['params']['mapper']=='gif565-cache')
node_payload=[]
for c,(_,strength) in enumerate(roots):
    for source in sources:
        y,x=np.indices(source.shape[:2]);b=np.array([[0,2],[3,1]],dtype=float)
        noise=((b[y%2,x%2]+gif_best['params']['offset'])/4-.5)*strength*gif_best['params']['factor']
        rgb=np.clip(source[:,:,:3].astype(float)+noise[:,:,None],0,255).astype(np.uint8)
        node_payload.append(np.concatenate([rgb,source[:,:,3:4]],axis=2).reshape(-1).tolist())
node_code=r"""
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const p='/home/astra/projects/pixellab-local-test-20261011/website-art-bundles/4354-3a62375cb4c03823.js';
const raw=fs.readFileSync(p),hash=crypto.createHash('sha256').update(raw).digest('hex');
if(hash!=='cc7e87ddeb584f550ab863bc10792addab01469be1143ede0cded67a096284de')throw Error('source pin changed');
const ctx=vm.createContext({self:{},Uint8Array,Uint8ClampedArray,Uint32Array,Int32Array,Float64Array,ArrayBuffer});
vm.runInContext(raw.toString(),ctx,{timeout:1000});
const f=ctx.self.webpackChunk_N_E.flatMap(x=>Object.entries(x[1])).find(x=>x[0]==='5958')[1];
const api={};f({exports:api},api);
const inputs=JSON.parse(fs.readFileSync(0,'utf8'));
console.log(JSON.stringify({sha256:hash,indices:inputs.map(a=>Array.from(api.applyPalette(new Uint8Array(a),[[0,0,0],[255,255,255]],'rgb565')))}));
"""
gif_observed=json.loads(subprocess.run(['node','-e',node_code],input=json.dumps(node_payload),capture_output=True,text=True,check=True,timeout=10).stdout)
gif_diff=[]
for c,(_,strength) in enumerate(roots):
    for i,source in enumerate(sources):
        expected=predict(source,strength,gif_best['params'])[:,:,0].reshape(-1)
        actual=np.array(gif_observed['indices'][c*2+i],dtype=np.uint8)*255
        gif_diff.append(int(np.count_nonzero(expected!=actual)))
assert gif_diff==[0,0,0,0]
source_cache_check=dict(source_sha256=gif_observed['sha256'],module=5958,method='applyPalette format rgb565',candidate_params=gif_best['params'],pixels_compared=32768,authored_cache_vs_original_mismatches=gif_diff,boundary='Original GIF mapping matches cache candidate for these perturbed inputs; server mismatch remains538.')
alpha_observations=[dict(case=d.name,source_alpha_matches_output=bool(np.array_equal(sources[1][:,:,3],targets[c][1][:,:,3])),rgb_outputs_independent_of_alpha_on_same_rgb_fixture=bool(np.array_equal(targets[c][0][:,:,:3],targets[c][1][:,:,:3])),alpha_zero_white_rgb_pixels=int(np.count_nonzero((targets[c][1][:,:,3]==0)&(targets[c][1][:,:,0]==255))))for c,(d,_)in enumerate(roots)]
result=dict(classification='bounded-offline-candidate-characterization-not-server-source-recovery',pillow=Image.__version__,grid=dict(mappers=['rgb-nearest','pillow-fixed','gif565-cache'],transpose=[False,True],offset=[0,.5,1],factor=[1,2,3,3.2,4,5,8],rounding=['trunc','round','floor'],formula='clip(RGB + (((Bayer+offset)/4)-0.5) * request_strength * factor,0,255); cast uint8 after rounding option; map to fixed black/white; preserve original alpha'),candidates=len(rows),pins=pins,source_cache_check=source_cache_check,alpha_observations=alpha_observations,controls=controls,request_bindings=request_bindings,gray_phase_thresholds=thresholds,best=best,exact_candidates=[r['params']for r in rows if r['total_rgba_mismatches']==0],baselines=baselines,all_candidates=compact_rows,coverage='2 cases strengths5/10, 2 frames each,8192 RGBA pixels/frame,32768 comparisons/candidate, including alpha0/64/128/255; no heldout or non-BW dither case')
(OUT/'DITHER-CHARACTERIZATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(candidates=len(rows),best_params=rows[0]['params'],best_mismatches=rows[0]['total_rgba_mismatches'],exact=result['exact_candidates'],controls=controls,gray_phase_thresholds=thresholds),indent=2))
