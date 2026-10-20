"""Independent mechanical pixel/attachment/timing checks; never an art rating."""
from pathlib import Path
from PIL import Image
import json,math,hashlib,tempfile,argparse
import build
ROOT=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--pack',type=Path,default=ROOT/'dense-v20');parser.add_argument('--contact-report',type=Path,default=ROOT/'contact-proof-v20/report.json');parser.add_argument('--output',type=Path,default=ROOT/'verification-v20.json');args=parser.parse_args();PACK=args.pack;m=json.loads((PACK/'manifest.json').read_text());checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(label,result):checks.append({'label':label,'passed':bool(result)})
check('72 actualone-tick60fps poses',len(m['frames'])==72 and m['fps']==60 and all(f['duration_ticks']==1 for f in m['frames']))
check('Nativecycle1.2seconds',sum(f['duration_ticks']for f in m['frames'])/m['fps']==1.2)
for name,key in [('build.py','renderer_sha256'),('design.json','design_sha256'),('clips.json','clips_sha256')]:check('Frozen source '+name,sha(ROOT/name)==sha(PACK/'source-bindings'/name)==m[key])
for file,digest in m['source_hashes'].items():check('Sourceart '+file,sha(ROOT/file)==digest)
for f in m['frames']:
 im=Image.open(PACK/f['png']).convert('RGBA');box=im.getchannel('A').getbbox();check(f"Frame{f['key']} hash/256/unclipped",sha(PACK/f['png'])==f['png_sha256']and im.size==(256,256)and box[0]>0 and box[1]>0 and box[2]<256 and box[3]<256)
 for leg,l in f['legs'].items():
  lengths=m['registered_design']['legs'][leg]['bone_lengths'];check(f"Frame{f['key']} {leg} actualdeclaredchain lengths",abs(math.dist(l['hip'],l['knee'])-lengths[0])<1e-6 and abs(math.dist(l['knee'],l['ankle'])-lengths[1])<1e-6 and l['reach_excess']==0)
  layer=Image.open(PACK/'leg-isolates'/f"{leg}-{f['key']:02}.png").convert('RGBA');alpha=layer.getchannel('A')
  for joint in ['hip','knee','ankle']:
   x,y=l[joint];tile=alpha.crop((round(x)-2,round(y)-2,round(x)+3,round(y)+3));check(f"Frame{f['key']} {leg}/{joint} nonempty5px attachment neighborhood",tile.getbbox()is not None)
with tempfile.TemporaryDirectory()as td:
 out=Path(td)/'fresh';build.build(out,72)
 for p in (PACK/'frames').glob('*.png'):check('FreshactualrenderRGBA '+p.name,Image.open(p).convert('RGBA').tobytes()==Image.open(out/'frames'/p.name).convert('RGBA').tobytes())
physics=json.loads(args.contact_report.read_text());check('Physicalcontinuousheldnegativecontrol fails',physics['physical_pass']is False);check('Sharedglobalactualsolepixel0.5gate passes',physics['global_contact_lock_pass']is True);check('AllplantedbootRGBA material stable',physics['global_whole_boot_material_pass']is True)
with Image.open(PACK/'walk.gif')as gif:
 durations=[]
 for i in range(gif.n_frames):gif.seek(i);durations.append(gif.info['duration'])
 check('ActualGIF72poses1.2sec',gif.n_frames==72 and sum(durations)==1200)
r={'schema':'captain-complete-leg-mechanical-checks/v1','passed':all(c['passed']for c in checks),'checks':checks,'manifest_sha256':sha(PACK/'manifest.json'),'scope':'Source/frame hashes, independent chain length geometry, actualalphaattachment neighborhoods, freshactualrendererRGBA repeatability, clipbounds, and finiteCPU actualsole readback. Doesnotestablish knee anatomy, jointmaterial quality, heelreaction, engineGPU or9/10 artapproval.'}
args.output.write_text(json.dumps(r,indent=2)+'\n');print('passed',r['passed'],'checks',len(checks))
if not r['passed']:raise SystemExit(2)
