#!/usr/bin/env python3
"""Bridge the licensed-rig fixture to the installed portable clip contract, losslessly."""
import argparse,hashlib,json,math
from fractions import Fraction
from pathlib import Path
from PIL import Image

def sha(data):return hashlib.sha256(data).hexdigest()
def export(path,out):
 path=Path(path).resolve();out=Path(out).resolve()
 if out.exists():raise ValueError('Refuse overwriting a prior atlas revision')
 m=json.loads(path.read_text());landmarks_path=path.parent/'landmarks.json';lm=json.loads(landmarks_path.read_text())
 if lm['manifest_sha256']!=sha(path.read_bytes()):raise ValueError('Stale landmark source')
 views={'front':'down','right':'right','back':'up','left':'left'}
 if set(m['views'])!=set(views):raise ValueError('Explicit four-view adapter required')
 w,h=m['canvas'];n=m['samples_per_view'];fps=Fraction(str(m['source_fps']));period=Fraction(str(m['source_action_frames'][1]))-Fraction(str(m['source_action_frames'][0]))
 interval=period/n/fps;rate=interval.denominator;hold=interval.numerator;images={};clips=[];checks=[]
 for view,direction in views.items():
  rows=m['views'][view]
  if len(rows)!=n:raise ValueError('Missing pose')
  seq=[]
  for i,row in enumerate(rows):
   p=(path.parent/row['png']).resolve()
   if not p.is_relative_to(path.parent)or sha(p.read_bytes())!=row['sha256']:raise ValueError('Unsafe or stale frame')
   if row['sample']!=i or not math.isclose(row['seconds'],float(i*interval),abs_tol=1e-10):raise ValueError('Nonuniform source clock')
   im=Image.open(p).convert('RGBA')
   if im.size!=(w,h):raise ValueError('Canvas mismatch')
   seq.append(im)
  images[view]=seq
 # Preflight all sources before creating output. No masking, trimming, rescaling or resampling.
 out.mkdir(parents=True)
 for view,direction in views.items():
  seq=images[view];sheet=Image.new('RGBA',(n*w,h));frames=[]
  for i,im in enumerate(seq):
   sheet.paste(im,(i*w,0));frames.append({'atlas_index':i,'duration_video_frames':hold,'duration_seconds':float(interval),'pixel_sha256':sha(im.tobytes())})
  filename=f'{view}.png';sheet.save(out/filename);loaded=Image.open(out/filename).convert('RGBA')
  for i,im in enumerate(seq):
   assert loaded.crop((i*w,0,(i+1)*w,h)).tobytes()==im.tobytes();checks.append({'view':view,'sample':i,'exact_rgba':True})
  pivot=lm['views'][view][0]['projected_world_origin']
  clips.append({'actor':'ranger','name':'walk_'+view,'action':'walk','direction':direction,'sheet':filename,'frame_size':[w,h],'sheet_columns':n,'pivot_pixels':pivot,'ground_pivot_pixels':pivot,'loop':True,'frames':frames})
 portable={'video_fps':rate,'clips':clips,'source_manifest_sha256':sha(path.read_bytes()),'scope':'Only the four-view bow-carry walk. Pivot is world-origin projection, not certified sole contact.','gameplay_bindings':{'ranger':{'walk':{d:'walk_'+v for v,d in views.items()}}}}
 (out/'clips.json').write_text(json.dumps(portable,indent=2)+'\n')
 report={'source_manifest_sha256':sha(path.read_bytes()),'landmarks_sha256':sha(landmarks_path.read_bytes()),'adapter_sha256':sha(Path(__file__).read_bytes()),'portable_manifest_sha256':sha((out/'clips.json').read_bytes()),'rational_hold':[hold,rate],'cycle_seconds':float(period/fps),'exact_rgba_checks':checks,'art_approved_by_adapter':False}
 (out/'bridge-proof.json').write_text(json.dumps(report,indent=2)+'\n');return {'exact_cells':len(checks),'hold':f'{hold}/{rate}s','output':str(out)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('output');a=p.parse_args();print(json.dumps(export(a.manifest,a.output)))
