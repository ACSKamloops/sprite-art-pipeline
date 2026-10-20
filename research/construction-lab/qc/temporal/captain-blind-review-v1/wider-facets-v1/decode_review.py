import json,pathlib,subprocess,hashlib
from PIL import Image,ImageDraw
BASE=pathlib.Path('/home/astra/artifacts/captain-wider-facets-v1'); OUT=pathlib.Path(__file__).parent
report=json.loads((BASE/'report.json').read_text()); receipt=[]
for v in report['variants']:
 file=BASE/v['file']; zoom=v['zoom']; slow=v['slowdown']
 show=(not v['silhouette'] and slow==1) or (v['silhouette'] and zoom==2 and slow==2)
 if zoom==1:height=560; vf='crop=512:560:200:70'
 else:height=416; vf='scale=512:416:force_original_aspect_ratio=decrease:flags=neighbor,pad=512:416:0:0:color=0x23272d'
 cmd=['ffmpeg','-v','error','-i',str(file),'-vf',vf,'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-']
 raw=subprocess.check_output(cmd,stderr=subprocess.DEVNULL); size=512*height*3; count=len(raw)//size;obs=v['observations']; assert count==len(obs)
 seen=set(); selected=[]
 for i,o in enumerate(obs):
  k=(o['cycle'],o['frame'])
  if k not in seen and (o['cycle']==0 or o['frame'] in [0,71]):selected.append(i);seen.add(k)
 if show:
  for page,start in enumerate(range(0,len(selected),18)):
   ids=selected[start:start+18]; cols=3; rows=(len(ids)+cols-1)//cols;sheet=Image.new('RGB',(1536,(height+20)*rows),(35,39,45));d=ImageDraw.Draw(sheet)
   for k,i in enumerate(ids):
    img=Image.frombytes('RGB',(512,height),raw[i*size:(i+1)*size]);x=k%cols*512;y=k//cols*(height+20);sheet.paste(img,(x,y));o=obs[i];d.text((x+2,y+height+2),f"t={o['output_ms']}ms source={o['source_elapsed_ms']} f={o['frame']}",fill='white')
   sheet.save(OUT/(file.stem+f'-p{page}.png'))
 receipt.append({'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'all_consecutive_decoded_frames':count,'visually_inspected':show,'selected_indexes':selected if show else [],'normalization':vf,'continuous_video_ingestion':False})
(OUT/'decoded-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('decoded',len(receipt),'videos')
