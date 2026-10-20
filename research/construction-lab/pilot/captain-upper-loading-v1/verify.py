from pathlib import Path
import json,hashlib,sys,copy,importlib.util
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
import loading
P=Path(__file__).resolve().parent;S=P/'source';O=P/'artifacts/loading-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();packet=json.loads((S/'poses.json').read_text());cfg=json.loads((S/'design.json').read_text());receipt=json.loads((O/'construction.json').read_text());assert receipt['module_sha256']==sha(P/'loading.py')and receipt['builder_sha256']==sha(P/'build.py')
checks=[];anchors=cfg['anchors'];max_rigid_error=0;max_head_old_error=0
for i,f in enumerate(packet['frames']):
 rot,pivot,target,m=loading.transform(packet,i,cfg)
 transformed={n:target+rot@(np.array(a)-pivot)for n,a in anchors.items()}
 for aa,bb in [('sword_shoulder','sword_wrist'),('shield','sword_wrist'),('backpack_halo','sword_shoulder')]:
  err=abs(np.linalg.norm(transformed[aa]-transformed[bb])-np.linalg.norm(np.array(anchors[aa])-anchors[bb]));max_rigid_error=max(max_rigid_error,float(err))
 # Counterexample: static positional head translating with pelvis misses articulated neck.
 bad=target+loading.HEAD_NECK-pivot;max_head_old_error=max(max_head_old_error,float(np.linalg.norm(bad-np.array(m['head_neck_target']))))
for rec in receipt['records']:
 for layer in rec['layers'].values():assert sha(O/layer['file'])==layer['sha256']
assert max_rigid_error<1e-12
# Translation equivariance: physical world advance moves actor root and parents together.
cs=importlib.util.spec_from_file_location('frozen_cloth',S/'cloth.py');cloth=importlib.util.module_from_spec(cs);cs.loader.exec_module(cloth);sources={n:Image.open(S/'upper'/f'{n}.png').convert('RGBA')for n in list(loading.CARRIED)+['head','cape']};a=loading.cloth_packet(packet,cfg);shifted=copy.deepcopy(packet);stride=np.array(packet['camera']['matrix_2x3'])@packet['dimensions']['stride_world']
for f in shifted['frames']:
 f['physical_root_pixels']=(np.array(f['physical_root_pixels'])+stride).tolist()
 for n,v in f['upper_pixels'].items():f['upper_pixels'][n]=(np.array(v)+stride).tolist()
b=loading.cloth_packet(shifted,cfg);normal,_=loading.render(sources,packet,0,cfg,cloth,a);advanced,_=loading.render(sources,shifted,0,cfg,cloth,b)
assert all(normal[n].tobytes()==advanced[n].tobytes()for n in normal)
wrong=copy.deepcopy(packet);wrong['frames'][18]['phase']+=.25;r,p,t,m=loading.transform(packet,18,cfg);rr,pp,tt,mm=loading.transform(wrong,18,cfg);assert not np.allclose(r,rr),'wrong phase must alter parent'
report={'schema':'captain.upper_loading_checks.v1','module_sha256':sha(P/'loading.py'),'construction_sha256':sha(O/'construction.json'),'max_carried_rigid_anchor_distance_error_px':max_rigid_error,'static_positional_head_counterexample_max_neck_error_px':max_head_old_error,'head_neck_mask_adjacency_max_px':receipt['head_chest_near_neck_max_distance_px'],'world_stride_translation_all7replacement_layers_exact_RGBA':True,'wrong_phase_parent_rejected':True,'leg_layer_hashes_unchanged_all72':all(c['leg_layer_hashes_unchanged']for c in receipt['checks']),'source_palette_no_new_colors_all72':all(c['new_palette_colors']==0 for c in receipt['checks']),'art_approval':False}
(O/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
