"""Decode actual exported presentation states into fixed-screen review sheets."""
from pathlib import Path
import json,subprocess,bisect,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;V=P/'artifacts/audition-v1';O=P/'artifacts/video-review-v1';O.mkdir(exist_ok=True);r=json.loads((V/'report.json').read_text());receipt={}
for v in r['variants']:
 path=V/v['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==v['sha256'];data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(path)]));times=[round(float(f['best_effort_timestamp_time'])*1000)for f in data['frames']];st=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height','-of','json',str(path)]))['streams'][0];w,h=st['width'],st['height'];native=v['zoom']==1 and not v['silhouette'];phases=list(range(72))if native else list(range(0,72,9));targets=[sum(r['source_holds_ms'][:i])for i in phases]+[1190,1200,1217];indices={max(0,bisect.bisect_right(times,t)-1)for t in targets};proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-vsync','0','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE);ims={};crop=(300,70,700,390)if v['zoom']==1 else(270,65,1020,625)
 for i in range(len(times)):
  b=proc.stdout.read(w*h*3)
  if i in indices:ims[i]=Image.frombytes('RGB',(w,h),b).crop(crop)
 assert proc.wait()==0
 selected=[ims[max(0,bisect.bisect_right(times,t)-1)]for t in targets];pages=[];chunk_size=12 if native else len(targets)
 for start in range(0,len(targets),chunk_size):
  chunk=selected[start:start+chunk_size];cw,ch=chunk[0].size;cols=3 if native else 2;rows=(len(chunk)+cols-1)//cols;sheet=Image.new('RGB',(cols*cw,rows*(ch+22)),(35,40,45));draw=ImageDraw.Draw(sheet)
  for j,im in enumerate(chunk):
   x=j%cols*cw;y=j//cols*(ch+22);sheet.paste(im,(x,y));draw.text((x+4,y+ch+2),f"{v['file']} actualPTS {targets[start+j]}ms",fill='white')
  f=O/f"{v['file'][:-4]}-{start//chunk_size:02}.png";sheet.save(f);pages.append(f.name)
 receipt[v['file']]={'sha256':v['sha256'],'decoded_count':len(times),'targets_ms':targets,'actual_selected_pts_ms':[times[max(0,bisect.bisect_right(times,t)-1)]for t in targets],'fixed_screen_crop':crop,'pages':pages}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(list(receipt))
