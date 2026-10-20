#!/usr/bin/env python3
"""Fixed-canvas source-bound pair sheets. Metrics flag change; they do not grade art."""
from pathlib import Path
import hashlib,json,argparse
from PIL import Image,ImageDraw,ImageChops

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('pack',type=Path);a.add_argument('output',type=Path);args=a.parse_args();p=args.pack;o=args.output;o.mkdir(parents=True,exist_ok=True)
 m=json.loads((p/'manifest.json').read_text());assert m['source_fps']==24 and m['cycle_seconds']==1.25 and m['canvas']==[160,160]
 frames=[];pairs=[];sheets=[]
 for view in ['front','right','back','left']:
  ims=[]
  for i,f in enumerate(m['views'][view]):
   q=p/f['png'];assert sha(q)==f['sha256'];im=Image.open(q).convert('RGBA');assert im.size==(160,160);ims.append(im)
   frames.append({'view':view,'sample':i,'file_sha256':sha(q),'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'source_frame':f['source_frame'],'seconds':f['seconds']})
  assert len(ims)==12
  for i,im in enumerate(ims):
   k=(i+1)%12;diff=ImageChops.difference(im,ims[k]);mask=diff.convert('RGBA');count=sum(any(v) for v in mask.get_flattened_data())
   pairs.append({'view':view,'from':i,'to':k,'kind':'loop_wrap' if k==0 else 'adjacent','changed_pixels':count,'difference_bounds':diff.getbbox(alpha_only=False)})
  for start in range(0,12,3):
   sheet=Image.new('RGB',(960,180),'#263440');d=ImageDraw.Draw(sheet)
   for j in range(3):
    i=start+j;k=(i+1)%12;x=j*320;d.text((x+2,2),f'{view} {i} -> {k}'+(' LOOP' if k==0 else ''),fill='white')
    for off,q in [(0,i),(160,k)]:sheet.paste(ims[q],(x+off,20),ims[q])
   for scale in [1,2]:
    f=o/f'{view}-{start:02}-{scale}x.png';sheet.resize((960*scale,180*scale),Image.Resampling.NEAREST).save(f);sheets.append({'file':f.name,'sha256':sha(f),'pairs':[[i,(i+1)%12] for i in range(start,start+3)],'view':view,'scale':scale})
 receipt={'schema':'sprite.source_bound_static_pairs.v1','manifest_path':str(p/'manifest.json'),'manifest_sha256':sha(p/'manifest.json'),'clock':{'source_fps':24,'cycle_seconds':1.25,'pose_seconds':1.25/12},'source_inputs_declared':m['source_sha256'],'packed_blend_sha256':sha(p/'ranger-walk-render.blend') if (p/'ranger-walk-render.blend').exists() else None,'frames':frames,'pairs':pairs,'sheets':sheets,'algorithm_scope':'48 sourcePNG/hash/dimension checks;44 ordinary adjacent pairs+4 wraps; no recentering; raw change metrics are not art grades','visual_viewing_scope':'Set by separate reviewer receipt; generation alone proves no viewing.'};(o/'static-inputs.json').write_text(json.dumps(receipt,indent=2)+'\n');print('48 verified images;48 pairs;32 fixed-canvas sheets')
if __name__=='__main__':main()
