"""Read-only, bounded CPU/CUDA renderer audition; never saves preferences."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
import bpy

SOURCE=Path('/home/astra/projects/sprite-construction-lab/pilot/captain-fine-edit-assembly-v1/preview/captain-combined-head-sole04.blend')
EXPECTED='0a9b4f0926eec5b3ad0a56a2cf0304695392bfb4dcdf282c6733b086e972831d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);assert sha(SOURCE)==EXPECTED
gpu_state=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
parts=gpu_state.split(',');assert len(parts)==4 and float(parts[1])-float(parts[2])>16000,'Leave at least16GB GPU memory free before bounded probe'
args.output.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
devices=[{'name':d.name,'id':d.id,'type':d.type}for d in prefs.devices]
selected=[d for d in prefs.devices if d.type=='CUDA' and '5090'in d.name]
assert len(selected)==1,('Expectedactual5090CUDAdevice',devices)
for d in prefs.devices:d.use=d==selected[0]
s.render.resolution_x=s.render.resolution_y=384;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=128;s.cycles.seed=19;s.cycles.use_denoising=False
records=[]
for backend in ('CPU','GPU'):
    s.cycles.device=backend
    for frame in (33,103):
        s.frame_set(frame);path=args.output/f'{backend.lower()}-source{frame:03}.png';s.render.filepath=str(path)
        started=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-started
        records.append({'backend':backend,'compute_device_type':'CUDA'if backend=='GPU'else'CPU','source':frame,'elapsed_seconds_including_save':elapsed,'file':path.name,'sha256':sha(path)})
assert sha(SOURCE)==EXPECTED
(args.output/'receipt.json').write_text(json.dumps({'state':'RENDERER_BENCHMARK_NOT_ART_APPROVAL','source_sha256':EXPECTED,'script_sha256':sha(Path(__file__)),'blender_version':bpy.app.version_string,'gpu_state_before':gpu_state,'enumerated_devices':devices,'selected_GPU':selected[0].name,'preferences_saved':False,'source_scene_saved':False,'native':384,'samples':128,'seed':19,'denoise':False,'CPU_threads':6,'records':records,'limits':['Two phases only; firstGPUrenderincludesinitialization','GPU/CPU equality and visual comparison pending','No GodotRTXrendererclaim; Godot remains llvmpipe','No geometry, action or material authoring']},indent=2)+'\n')
print('RENDERER_PROBE_READY',flush=True)
