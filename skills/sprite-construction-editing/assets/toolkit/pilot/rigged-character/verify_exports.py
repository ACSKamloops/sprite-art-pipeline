#!/usr/bin/env python3
"""Validate actual exported RGBA/atlas rows and source freshness independently of Godot producer."""
import argparse,hashlib,json,pathlib
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent

def pixelsha(image):return hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
def verify(dest):
 m=json.loads((dest/'manifest.json').read_text());checks=[];clipping=[]
 def check(label,ok):checks.append({'label':label,'passed':bool(ok)})
 for name,digest in m['source_bindings'].items():check('source freshness '+name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest)
 for name,c in m['clips'].items():
  atlas=Image.open(dest/c['atlas']).convert('RGBA');check(name+' atlas <=4096',max(atlas.size)<=4096);check(name+' atlas RGBA',pixelsha(atlas)==c['atlas_pixel_sha256']);check(name+' count',len(c['frames'])==c['duration_ticks'])
  for tick,f in enumerate(c['frames']):
   image=Image.open(dest/f['png']).convert('RGBA');x,y,w,h=f['region'];cell=atlas.crop((x,y,x+w,y+h));check(name+f' tick{tick} image/atlas/order/hold',image.size==(192,192)and pixelsha(image)==f['pixel_sha256']and cell.tobytes()==image.tobytes()and f['tick']==tick and f['duration_ticks']==1)
   alpha=image.getchannel('A');box=alpha.getbbox()
   if box and(box[0]<=0 or box[1]<=0 or box[2]>=192 or box[3]>=192):clipping.append({'clip':name,'tick':tick,'bounds':box})
  check(name+' no edge clipping',not any(x['clip']==name for x in clipping))
 check('positive authored clock',m['fps']==60)
 return {'schema':'copper-scout-export-validation/v1','passed':all(c['passed']for c in checks),'manifest_sha256':hashlib.sha256((dest/'manifest.json').read_bytes()).hexdigest(),'frames_tres_sha256':hashlib.sha256((dest/'frames.tres').read_bytes()).hexdigest(),'checks':checks,'edge_clipping':clipping,'limits':['Pixel hash and clipping checks do not approve anatomy, contacts or temporal art quality.','No per-frame recentering or resampling.']}

def main():
 p=argparse.ArgumentParser();p.add_argument('exports',type=pathlib.Path);a=p.parse_args();r=verify(a.exports);(a.exports/'export-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'checks':len(r['checks']),'clipped_frames':len(r['edge_clipping'])}));raise SystemExit(0 if r['passed']else 2)
if __name__=='__main__':main()
