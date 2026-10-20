"""Fresh-process CUDA replay of the actual two-phase benchmark."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import bpy
SOURCE=Path('/home/astra/projects/sprite-construction-lab/pilot/captain-fine-edit-assembly-v1/preview/captain-combined-head-sole04.blend')
SHA='0a9b4f0926eec5b3ad0a56a2cf0304695392bfb4dcdf282c6733b086e972831d'
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA;a.output.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
selected=[d for d in p.devices if d.type=='CUDA'and '5090'in d.name];assert len(selected)==1
for d in p.devices:d.use=d==selected[0]
s.cycles.device='GPU';s.cycles.samples=128;s.cycles.seed=19;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=s.render.resolution_y=384;s.render.resolution_percentage=100
rows=[]
for i,f in enumerate((33,103,33)):
    s.frame_set(f);out=a.output/f'gpu-{i}-source{f:03}.png';s.render.filepath=str(out);t=time.perf_counter();bpy.ops.render.render(write_still=True);rows.append({'sequence':i,'source':f,'file':out.name,'elapsed_seconds':time.perf_counter()-t,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
(a.output/'receipt.json').write_text(json.dumps({'state':'GPU_REPLAY_PIXELS_REQUIRE_SEPARATE_CHECK','source_sha256':SHA,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'device':selected[0].name,'compute':'CUDA','records':rows,'preferences_saved':False,'source_saved':False},indent=2)+'\n')
print('CUDA_REPLAY_READY',flush=True)
