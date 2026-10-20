import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;result={}
for name in ['old','upright']:
 base=Path(f'/home/astra/artifacts/captain-key-comparison-{name}-source-v1');f=base/'rgba-1x-normal.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(f)]));pts=[float(x['best_effort_timestamp_time'])*1000 for x in probe['frames']]
 source=[np.array(Image.open(base/'source-frames'/f'{i:02}.png').convert('RGBA')) for i in range(8)]
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(f),'-vf','crop=256:256:120:88','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
 rows=[]
 for t in pts:
  raw=proc.stdout.read(256*256*3)
  if len(raw)!=256*256*3:raise RuntimeError('short decode')
  a=np.frombuffer(raw,dtype=np.uint8).reshape((256,256,3)).astype(np.int16)
  errs=[float(np.abs(a-s[:,:,:3].astype(np.int16))[s[:,:,3]>=250].mean())for s in source]
  expected=int((t%1200)//150);nearest=int(np.argmin(errs));rows.append({'pts_ms':t,'expected':expected,'nearest':nearest,'expected_opaque_RGB_MAE':errs[expected]})
 proc.wait();result[name]={'decoded_count':len(rows),'wrong_nearest_pose':[x for x in rows if x['expected']!=x['nearest']],'mean_expected_opaque_RGB_MAE':float(np.mean([x['expected_opaque_RGB_MAE']for x in rows])),'rows':rows}
 im=Image.new('RGB',(1024,536),(38,43,49))
 for j,i in enumerate([7,0]):
  frame=Image.open(p/name/'decoded'/'rgba-2x-normal'/f'{i+1:02}.png').crop((120,88,632,600));im.paste(frame,(j*512,0))
 im.save(p/name/'actual-wrap-2x.png')
(p/'source-sequence-check.json').write_text(json.dumps(result,indent=2)+'\n');print({k:{x:y for x,y in v.items()if x!='rows'}for k,v in result.items()})
