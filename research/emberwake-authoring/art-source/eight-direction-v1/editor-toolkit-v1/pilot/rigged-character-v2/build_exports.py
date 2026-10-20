#!/usr/bin/env python3
"""Real GPU rig bake -> fixed atlases -> SpriteFrames; no opaque image-generation pipeline."""
import argparse,hashlib,json,math,os,pathlib,shutil,subprocess,sys,time
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def engine(args,log):
 cmd=['xvfb-run','-a','godot','--display-driver','x11','--rendering-method','gl_compatibility','--audio-driver','Dummy','--path',str(ROOT),*args]
 result=subprocess.run(cmd,text=True,capture_output=True);output=result.stdout+result.stderr;log.write_text(output)
 if result.returncode or 'SCRIPT ERROR:'in output or 'Parse Error:'in output or 'ERROR:'in output:raise RuntimeError(f'Engine failed: {log} exit{result.returncode}')
 return cmd

def write_frames(manifest,dest):
 lines=['[gd_resource type="SpriteFrames" load_steps=%d format=3]'%(1+len(manifest['clips'])+sum(len(c['frames'])for c in manifest['clips'].values()))]
 for i,(name,c)in enumerate(manifest['clips'].items()):lines.append('[ext_resource type="Texture2D" path="res://generated/%s" id="atlas_%d"]'%(c['atlas'],i))
 animations=[]
 for ai,(name,c)in enumerate(manifest['clips'].items()):
  frames=[]
  for fi,f in enumerate(c['frames']):
   ident=f'cell_{ai}_{fi}';r=f['region'];lines.extend(['[sub_resource type="AtlasTexture" id="%s"]'%ident,'atlas = ExtResource("atlas_%d")'%ai,'region = Rect2(%s)'%', '.join(map(str,r))]);frames.append('{"duration": 1.0, "texture": SubResource("%s")}'%ident)
  animations.append('{"frames": [%s], "loop": %s, "name": &%s, "speed": %s}'%(', '.join(frames),'true'if c['loop']else'false',json.dumps(name),manifest['fps']))
 lines.extend(['[resource]','animations = [%s]'%',\n'.join(animations)]);(dest/'frames.tres').write_text('\n\n'.join(lines)+'\n')

def review_artifacts(manifest,dest):
 out=dest/'review';out.mkdir(exist_ok=True)
 for name,c in manifest['clips'].items():
  frames=[Image.open(dest/f['png']).convert('RGBA')for f in c['frames']]
  # Exact source samples with no recentering; transparent alpha retains authored placement.
  sample_indices=sorted(set([0,len(frames)//4,len(frames)//2,3*len(frames)//4,len(frames)-1]))
  sheet=Image.new('RGBA',(192*len(sample_indices),218),(30,36,45,255));d=ImageDraw.Draw(sheet)
  for i,n in enumerate(sample_indices):sheet.alpha_composite(frames[n],(i*192,0));d.text((i*192+8,196),f'{name} tick {n}',fill=(225,230,235,255))
  sheet.save(out/(name.replace('/','-')+'-contact.png'))
  for scale in [1,2]:
   images=[]
   for f in frames:
    bg=Image.new('RGBA',(192,192),(30,36,45,255));bg.alpha_composite(f);images.append(bg.convert('RGB').resize((192*scale,192*scale),Image.Resampling.NEAREST))
   # GIF only supports10ms intervals: cumulative nearest10ms error diffusion.
   boundaries=[round(i*100/manifest['fps'])*10 for i in range(len(images)+1)];durations=[max(10,b-a)for a,b in zip(boundaries,boundaries[1:])]
   images[0].save(out/(name.replace('/','-')+f'-{scale}x.gif'),save_all=True,append_images=images[1:],duration=durations,disposal=2,**({'loop':0}if c['loop']else{}))

def main():
 p=argparse.ArgumentParser();p.add_argument('--private-output',type=pathlib.Path,required=True);p.add_argument('--select');p.add_argument('--views',default='right,left,front,back');p.add_argument('--duplicate',action='store_true');p.add_argument('--reuse-render',action='store_true');p.add_argument('--web',action='store_true');a=p.parse_args();private=a.private_output.resolve()
 if private.exists()and not a.reuse_render:raise ValueError('Private output must be fresh; never replace a previous bake')
 private.mkdir(parents=True,exist_ok=a.reuse_render);out=private/'first';args=['--script','bake.gd','--','--output',str(out),'--isolate','--views',a.views]
 if a.select:args+=['--select',a.select]
 commands=[]if a.reuse_render else[engine(['--editor','--import'],private/'preimport.log'),engine(args,private/'bake.log')]
 manifest=json.loads((out/'manifest.json').read_text());
 for name,digest in manifest['source_bindings'].items():
  if sha(ROOT/name)!=digest:raise ValueError('Stale rendered source '+name)
 manifest['source_bindings']['build_exports.py']=sha(pathlib.Path(__file__).resolve());manifest['sampling_policy']='Loop:tick/N; one-shot:tick/(N-1), endpoint held for final source tick; completion atN.'
 for name,c in manifest['clips'].items():
  seen=set()
  for e in c['events']:
   if isinstance(e['tick'],bool)or not isinstance(e['tick'],(int,float))or not math.isfinite(e['tick'])or e['tick']!=int(e['tick'])or not 0<=e['tick']<=c['duration_ticks']or not isinstance(e['type'],str):raise ValueError('Invalid authored event')
   e['tick']=int(e['tick']);key=(e['tick'],e['type'])
   if key in seen:raise ValueError('Duplicate authored event')
   seen.add(key)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');write_frames(manifest,out);review_artifacts(manifest,out)
 dest=ROOT/'generated'
 if dest.exists():
  # Preserve old exports privately before replacing this worker-owned derived folder.
  shutil.copytree(dest,private/'previous-generated')
  shutil.rmtree(dest)
 shutil.copytree(out,dest)
 commands.append(engine(['--editor','--import'],private/'import.log'))
 if a.duplicate:
  duplicate=private/'duplicate';dup_args=['--script','bake.gd','--','--output',str(duplicate),'--views',a.views]
  if a.select:dup_args+=['--select',a.select]
  commands.append(engine(dup_args,private/'duplicate.log'))
  repeated=json.loads((duplicate/'manifest.json').read_text());checks=[]
  for name,c in manifest['clips'].items():
   for tick in sorted(set([0,len(c['frames'])//4,len(c['frames'])//2,len(c['frames'])-1])):
    first=Image.open(out/c['frames'][tick]['png']).convert('RGBA').tobytes();second=Image.open(duplicate/repeated['clips'][name]['frames'][tick]['png']).convert('RGBA').tobytes();checks.append({'clip':name,'tick':tick,'pixel_sha256':hashlib.sha256(first).hexdigest(),'passed':first==second})
  report={'passed':all(c['passed']for c in checks),'scope':'Actual repeated engine RGBA in same renderer; no cross-renderer PNG-byte determinism claim','checks':checks};(dest/'repeat-render-report.json').write_text(json.dumps(report,indent=2)+'\n')
  if not report['passed']:raise ValueError('Actual duplicate render pixels differ')
 subprocess.run([sys.executable,str(ROOT/'verify_exports.py'),str(dest)],check=True)
 if a.web:
  (dest/'web').mkdir(exist_ok=True);commands.append(engine(['--headless','--export-release','Web',str(dest/'web/index.html')],private/'web-export.log'))
 (dest/'build-receipt.json').write_text(json.dumps({'schema':'copper-scout-build/v2','source_bindings':manifest['source_bindings'],'manifest_sha256':sha(dest/'manifest.json'),'frames_tres_sha256':sha(dest/'frames.tres'),'commands':commands,'private_output':str(private),'built_at_unix':time.time()},indent=2)+'\n')
 print(json.dumps({'bindings':len(manifest['clips']),'frames':sum(len(c['frames'])for c in manifest['clips'].values()),'output':str(dest)}))
if __name__=='__main__':main()
