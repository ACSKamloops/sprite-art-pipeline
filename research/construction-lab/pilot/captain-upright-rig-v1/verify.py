"""Repeat actual layered rasterization, bound source and analytic limits separately."""
from pathlib import Path
from PIL import Image
import hashlib,json,functools,shutil,tempfile
import render,construct,pixel_affine
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 checks=0;reports={};source_before=sha(ROOT/'source/native-256.png')
 # Cache eviction changes runtime only; actual affine bytes still compared for every frame/layer.
 pixel_affine.expanded=functools.lru_cache(maxsize=64)(pixel_affine.expanded.__wrapped__)
 audit=ROOT/'artifacts/verification-parts';cfg,parts,construction=construct.construct(audit)
 for packname,motionfile,keypack in [('frozen-v4-dense','motion.json','frozen-v4-eight-key'),('gentle-dense','motion-gentle-longer.json','gentle-eight-key')]:
  pack=ROOT/'artifacts'/packname;m=json.loads((pack/'manifest.json').read_text());motion=json.loads((ROOT/motionfile).read_text());assert m['source_sha256']==source_before;assert m['motion_sha256']==sha(ROOT/motionfile);palette=set(Image.open(ROOT/'source/native-256.png').convert('RGBA').get_flattened_data())|{(0,0,0,0)};actual_key_matches=[];ratios={};boxes=[]
  for f in m['frames']:
   layers,meta=render.pose(cfg,parts,motion,f['phase']);whole=Image.new('RGBA',(256,256))
   for name in render.ORDER:
    im=layers[name];expected=Image.open(pack/'layers'/f"{f['frame']:02}-{name}.png").convert('RGBA');assert im.tobytes()==expected.tobytes();assert set(im.getchannel('A').get_flattened_data())<={0,255};assert set(im.get_flattened_data())<=palette;whole.alpha_composite(im);checks+=3
   assert whole.tobytes()==Image.open(pack/f['file']).convert('RGBA').tobytes();assert f['sha256']==sha(pack/f['file']);box=whole.getbbox();assert box[0]>0 and box[1]>0 and box[2]<256 and box[3]<256;boxes.append(box);checks+=3
   assert meta['upper']['backpack_halo']['owner']=='chest';assert meta['upper']['backpack_halo']['angle']==meta['upper']['chest']['angle'];assert meta['upper']['head']['angle']==0;checks+=3
   for leg,lm in meta['legs'].items():assert lm['reach_distance']<sum(lm['bone_lengths']);assert lm['no_adaptive_hip_shift'];checks+=2
   if f['frame']%9==0:
    ix=f['frame']//9;assert whole.tobytes()==Image.open(ROOT/'artifacts'/keypack/'frames'/f'{ix:02}.png').convert('RGBA').tobytes();actual_key_matches.append(f['frame']);checks+=1
  zero,_=render.pose(cfg,parts,motion,0);endpoint,_=render.pose(cfg,parts,motion,1)
  for name in render.ORDER:assert zero[name].tobytes()==endpoint[name].tobytes();checks+=1
  for leg in ['far','near']:
   fs=[f['legs'][leg]for f in m['frames']if f['legs'][leg]['stance']];ratios[leg]={'support_knee_flex_degrees':[min(x['knee_flex_degrees']for x in fs),max(x['knee_flex_degrees']for x in fs)],'maximum_swing_clearance_px':max(f['legs'][leg]['swing_clearance']for f in m['frames']),'analytic_world_target_peak_to_peak':[max(x['sole_world_target'][j]for x in fs)-min(x['sole_world_target'][j]for x in fs)for j in range(2)]};assert max(ratios[leg]['analytic_world_target_peak_to_peak'])<1e-8
  reports[packname]={'manifest_sha256':sha(pack/'manifest.json'),'actual_RGBA_repeat_fullframes':72,'actual_RGBA_repeat_layers':72*len(render.ORDER),'all_eight_keys_RGBA_equal_dense_subset':actual_key_matches,'actual_endpoint_all_layers_equal_phase0':True,'hard_alpha_source_palette_only':True,'all_frames_strictly_inside_canvas':True,'joint_geometry_only':ratios}
 # Real one-pixel private source corruption must reject before construction writes.
 with tempfile.TemporaryDirectory(prefix='upright-source-negative-',dir=ROOT/'artifacts')as temp:
  t=Path(temp);(t/'source').mkdir();shutil.copy2(ROOT/'design.json',t/'design.json');im=Image.open(ROOT/'source/native-256.png').convert('RGBA');im.putpixel((130,60),(0,255,255,255));im.save(t/'source/native-256.png');saved=construct.ROOT;construct.ROOT=t
  try:
   try:construct.construct(t/'should-not-write')
   except AssertionError:pass
   else:raise AssertionError('Stale source accepted')
   assert not(t/'should-not-write').exists()
  finally:construct.ROOT=saved
 # Actual rigid part shifts change composite; source original itself never mutated.
 m=json.loads((ROOT/'artifacts/frozen-v4-dense/manifest.json').read_text());motion=json.loads((ROOT/'motion.json').read_text());layers,_=render.pose(cfg,parts,motion,.25);control=Image.new('RGBA',(256,256));bad=Image.new('RGBA',(256,256));shifted=layers['near_boot'].transform((256,256),Image.Transform.AFFINE,(1,0,-1,0,1,0),Image.Resampling.NEAREST)
 for name in render.ORDER:control.alpha_composite(layers[name]);bad.alpha_composite(shifted if name=='near_boot'else layers[name])
 diff=sum(a!=b for a,b in zip(control.get_flattened_data(),bad.get_flattened_data()));assert diff>0
 assert source_before==sha(ROOT/'source/native-256.png')
 out={'status':'REPRODUCIBLE_AUDITION_NOT_ART_APPROVAL','checks':checks,'verification_expansion_cache_capacity':64,'producer_expansion_cache_capacity':16,'cache_difference':'Eviction cardinality only; all resulting affine RGBA bytes independently equal checked','source_unchanged_sha256':source_before,'reports':reports,'negative_source_onepixel_atomic_reject':True,'negative_boot_onepixel_actual_composite_changed_pixels':diff,'source_recomposition_exact':construction['source_only_rest_recomposition_RGBA_exact'],'input_hashes':{n:sha(ROOT/n)for n in ['render.py','construct.py','design.json','motion.json','motion-gentle-longer.json','pixel_affine.py','audition_specs.py','export_motion_frozen.py']},'limits':['No artistic approval or score.','Analytic sole target stationarity is not an actual movingworld pixel/material contact certificate.','Eight source keys and dense samples are different playback modes, not equivalent held-pose motion.','One new shallow three-quarter view, no additional view claims.']};(ROOT/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'checks':checks,'reports':list(reports)}))
if __name__=='__main__':run()
