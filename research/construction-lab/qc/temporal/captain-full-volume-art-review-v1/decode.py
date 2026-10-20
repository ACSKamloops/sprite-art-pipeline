import json,hashlib,subprocess,bisect,sys
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent
receipt=json.loads((O/'decode-receipt.json').read_text()) if (O/'decode-receipt.json').exists() else {}
for name in (['longstride-v2'] if '--longstride-v2' in sys.argv else ['canonical','longstride']):
 p=Path('/home/astra/artifacts/captain-original-volume-'+ ('longstride-v2' if name=='longstride-v2' else name+'-v1'));report=json.loads((p/'report.json').read_text());receipt[name]={'report_sha256':hashlib.sha256((p/'report.json').read_bytes()).hexdigest(),'spec_sha256':report['spec_sha256'],'videos':{}}
 for filename in ['rgba-1x-normal.mp4','rgba-2x-normal.mp4','silhouette-1x-normal.mp4','rgba-1x-half-speed.mp4']:
  v=next(v for v in report['variants'] if v['file']==filename);f=p/filename;assert hashlib.sha256(f.read_bytes()).hexdigest()==v['sha256']
  meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(f)]));times=[round(float(x['best_effort_timestamp_time'])*1000) for x in meta['frames']]
  normal=filename=='rgba-1x-normal.mp4';targets=[sum(report['source_holds_ms'][:i]) for i in (range(72) if normal else range(0,72,9))]
  targets=[t*v['slowdown'] for t in targets];targets += [1190*v['slowdown'],1200*v['slowdown'],1217*v['slowdown']]
  indices=sorted(set(max(0,bisect.bisect_right(times,t)-1) for t in targets));selected={};zoom=v['zoom'];stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height','-of','json',str(f)]))['streams'][0];w,h=stream['width'],stream['height']
  proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(f),'-vsync','0','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
  for j in range(len(times)):
   raw=proc.stdout.read(w*h*3)
   if j in indices:
    im=Image.frombytes('RGB',(w,h),raw);box=(300,70,700,390) if zoom==1 else (270,65,1020,625);selected[j]=im.crop(box)
  assert proc.wait()==0
  views=[(t,selected[max(0,bisect.bisect_right(times,t)-1)]) for t in targets]
  size=12 if normal else len(views)
  sheets=[]
  for start in range(0,len(views),size):
   chunk=views[start:start+size];cw,ch=chunk[0][1].size;cols=3 if normal else 2;rows=(len(chunk)+cols-1)//cols;sheet=Image.new('RGB',(cw*cols,(ch+22)*rows),(35,39,43));d=ImageDraw.Draw(sheet)
   for k,(t,im) in enumerate(chunk):
    x=k%cols*cw;y=k//cols*(ch+22);sheet.paste(im,(x,y));d.text((x+4,y+ch+3),f'{name} {filename} decoded t={t}ms',fill='white')
   out=O/f'{name}-{filename[:-4]}-{start//size:02}.png';sheet.save(out);sheets.append(out.name)
  receipt[name]['videos'][filename]={'sha256':v['sha256'],'decoded_frames':len(times),'selected_requested_ms':targets,'selected_actual_ms':[times[max(0,bisect.bisect_right(times,t)-1)]for t in targets],'sheets':sheets,'crop_fixed_screen':box}
(O/'decode-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
