from pathlib import Path
import json,hashlib,importlib.util
from PIL import Image
ROOT=Path(__file__).resolve().parent
p=ROOT/'artifacts/trial-final';r=ROOT/'artifacts/repeat-final';m=json.loads((p/'manifest.json').read_text());n=json.loads((r/'manifest.json').read_text());assert m['frames']==n['frames'];checks=0
for f in m['frames']:
 for name in [f['png']]+[f"layers/{f['frame']:02}-{layer}.png"for layer in m['layer_order']]:
  assert Image.open(p/name).convert('RGBA').tobytes()==Image.open(r/name).convert('RGBA').tobytes();checks+=1
 for side,leg in f['legs'].items():assert leg['reach_distance']<leg['maximum_chain'];checks+=1
movie=Image.open(p/'loop.gif');duration=0
for i in range(movie.n_frames):movie.seek(i);duration+=movie.info['duration']
assert duration==1200
spec=importlib.util.spec_from_file_location('motion',ROOT/'render.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);cfg=json.loads((ROOT/'motion.json').read_text());assert mod.sample(cfg['keys'],0)==mod.sample(cfg['keys'],1)
stance={}
for side in ['right','left']:
 points=[[f['legs'][side]['sole_source_attached_target'][j]+f['physical_root'][j]for j in range(2)]for f in m['frames']if f['legs'][side]['support']]
 spreads=[max(v[j]for v in points)-min(v[j]for v in points)for j in range(2)];assert max(spreads)<1e-10
 support=[f['legs'][side]for f in m['frames']if f['legs'][side]['support']];stance[side]={'analytic_world_contact_range_xy':spreads,'support_chain_extension_ratio_range':[min(x['reach_distance']/x['maximum_chain']for x in support),max(x['reach_distance']/x['maximum_chain']for x in support)],'maximum_swing_clearance_px':max(f['legs'][side]['swing_clearance']for f in m['frames'])}
report={'status':'TECHNICAL_COMPARATOR_NOT_ART_APPROVAL','visual_status':'REJECTED_STILL_CROUCHED_RIGID_POSTER_SILHOUETTE_AND_FLAT_NOISY_NEAR_GREAVE','repeat_frame_and_layer_RGBA_checks':checks,'timed_GIF_cycle_ms':duration,'source_keys':8,'actual_dense_frames':72,'canvas_fixed':[256,256],'source_keys_loop_endpoint_equal':True,'fixed_hips_all_reachable_no_adaptation':True,'stance':stance,'renderer_sha256':hashlib.sha256((ROOT/'render.py').read_bytes()).hexdigest(),'motion_sha256':hashlib.sha256((ROOT/'motion.json').read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest(),'limits':['Analytic source-attached target stationarity is NOT actual wholeboot pixel/GPU/material stationarity.','No heel/toe roll implemented; boot pitch zero.','Single source viewpoint and rigid armor still constrain believable volume.','New posture/keys require independent actual timed review; previous scores not inherited.']}
(ROOT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
