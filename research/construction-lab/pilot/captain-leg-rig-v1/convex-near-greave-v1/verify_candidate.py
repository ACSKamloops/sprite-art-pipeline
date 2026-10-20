"""Fresh actual change-isolation checks; never an art score."""
from pathlib import Path
from PIL import Image
import json,hashlib,importlib.util,tempfile,argparse,shutil
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(pack,parent,renderer):
 m=json.loads((pack/'manifest.json').read_text());old=json.loads((parent/'manifest.json').read_text());checks={};checks['producer_SHA_exact']=sha(renderer)==m['renderer_sha256'];checks['parent_manifest_exact']=sha(parent/'manifest.json')==m['parent_pose_manifest_sha256'];checks['72pose_chain_hip_root_timing_exact']=all(f['legs']==o['legs']and f['pelvis']==o['pelvis']and f['physical_root']==o['physical_root']and f['duration_ticks']==o['duration_ticks']for f,o in zip(m['frames'],old['frames']));checks['144boot_RGBA_exact']=all(Image.open(pack/'boot-isolates'/f'{l}-{i:02}.png').convert('RGBA').tobytes()==Image.open(parent/'boot-isolates'/f'{l}-{i:02}.png').convert('RGBA').tobytes()for l in ['left','right']for i in range(72));checks['72far_leg_RGBA_exact']=all(Image.open(pack/'leg-isolates'/f'right-{i:02}.png').convert('RGBA').tobytes()==Image.open(parent/'leg-isolates'/f'right-{i:02}.png').convert('RGBA').tobytes()for i in range(72));checks['72actualRGBA_unclipped']=all((lambda b:b[0]>0 and b[1]>0 and b[2]<256 and b[3]<256)(Image.open(pack/f['png']).getchannel('A').getbbox())for f in m['frames']);spec=importlib.util.spec_from_file_location('candidate',renderer);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 with tempfile.TemporaryDirectory()as td:
  out=Path(td)/'fresh';mod.render(parent,out);checks['all72fresh_actualRGBA_repeat']=all(Image.open(pack/f['png']).convert('RGBA').tobytes()==Image.open(out/f['png']).convert('RGBA').tobytes()for f in m['frames']);checks['all72fresh_foregroundRGBA_repeat']=all(Image.open(pack/f['foreground']['png']).convert('RGBA').tobytes()==Image.open(out/f['foreground']['png']).convert('RGBA').tobytes()for f in m['frames'])
 for n in ['build.py','design.json','clips.json']:shutil.copy2(parent/'source-bindings'/n,pack/'source-bindings'/('parent-'+n))
 ims=[]
 for f in m['frames']:
  im=Image.open(pack/f['png']).convert('RGBA');bg=Image.new('RGBA',im.size,(31,34,41,255));bg.alpha_composite(im);ims.append(bg.convert('RGB'))
 ims[0].save(pack/'walk.gif',save_all=True,append_images=ims[1:],duration=[round((i+1)*1000/60/10)*10-round(i*1000/60/10)*10 for i in range(72)],loop=0,disposal=2)
 report={'manifest_sha256':sha(pack/'manifest.json'),'checks':checks,'passed':all(checks.values()),'scope':'Actualsource/pose/boot/farleg/pixelbounds/repeatability only. Palette/binaryforeground producerassertions. Notart/volume/3D/anatomyapproval.'};(pack/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('passed',report['passed'],checks)
 if not report['passed']:raise ValueError('Rejected mechanical candidate')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True);p.add_argument('--parent',type=Path,default=ROOT.parent/'stride-pose-probe/dense-mean149');p.add_argument('--renderer',type=Path,required=True);a=p.parse_args();verify(a.pack,a.parent,a.renderer)
