#!/usr/bin/env python3
"""Bind actual browser screenshot clock ranges without inventing exact pose labels."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,argparse

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('capture',type=Path);a.add_argument('output',type=Path);a.add_argument('--manifest',required=True);args=a.parse_args();d=json.loads(args.capture.read_text());assert d['manifest_sha256']==args.manifest;o=args.output;o.mkdir(parents=True,exist_ok=True);sheets=[]
 for mode in d['modes']:
  scale=mode['scale'];assert mode['stopped']['seconds']>=3.75 and mode['stopped']['seconds']==mode['after_pause']['seconds'];rows=4 if scale==1 else 2;w=676 if scale==1 else 1316;ht=196 if scale==1 else 356
  for start in range(0,len(mode['entries']),rows):
   es=mode['entries'][start:start+rows];out=Image.new('RGB',(w,(ht+24)*len(es)),'#263440');dr=ImageDraw.Draw(out)
   for j,e in enumerate(es):
    f=Path(e['path']);assert sha(f)==e['screenshot_sha256'];im=Image.open(f);out.paste(im.crop((0,0,w,ht)),(0,j*(ht+24)+24));b=e['before'];a=e['after'];assert b['manifest_sha256']==a['manifest_sha256']==args.manifest;dr.text((2,j*(ht+24)+3),f'{start+j:02} t={b["seconds"]:.3f}..{a["seconds"]:.3f} pose={b["pose"]}..{a["pose"]} (clock range, not exact snapshot label)',fill='white')
   q=o/f'chronological-{scale}x-{start:02}.png';out.save(q);sheets.append({'file':q.name,'sha256':sha(q),'entries':list(range(start,start+len(es))),'scale':scale})
 for start in range(0,len(d['paused']),3):
  es=d['paused'][start:start+3];out=Image.new('RGB',(1316,380*len(es)),'#263440');dr=ImageDraw.Draw(out)
  for j,e in enumerate(es):
   f=Path(e['path']);assert sha(f)==e['screenshot_sha256'];assert e['state']['pose']==start+j and not e['state']['playing'];im=Image.open(f);out.paste(im.crop((0,0,1316,356)),(0,j*380+24));dr.text((2,j*380+3),f'PAUSED pose{start+j} t={e["state"]["seconds"]:.6f}',fill='white')
  q=o/f'paused-{start:02}.png';out.save(q);sheets.append({'file':q.name,'sha256':sha(q),'paused_poses':list(range(start,start+len(es)))})
 r={'capture_path':str(args.capture),'capture_sha256':sha(args.capture),'manifest_sha256':d['manifest_sha256'],'chronological_screenshots':sum(len(m['entries']) for m in d['modes']),'paused_screenshots':len(d['paused']),'sheets':sheets,'stopped':[{k:m[k] for k in ['scale','stopped','after_pause']} for m in d['modes']],'screenshot_source_hashes':{Path(e['path']).name:e['screenshot_sha256'] for m in d['modes'] for e in m['entries']}|{Path(e['path']).name:e['screenshot_sha256'] for e in d['paused']},'continuous_video_ingested':False,'visual_viewing_scope':'Generation alone proves no image viewing; separate reviewer receipt required.'};(o/'capture-binding.json').write_text(json.dumps(r,indent=2)+'\n');print('Screenshot sourcehashes andclock verified; sheets',len(sheets))
if __name__=='__main__':main()
