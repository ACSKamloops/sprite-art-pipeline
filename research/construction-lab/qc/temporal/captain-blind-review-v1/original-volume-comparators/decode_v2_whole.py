import json,pathlib,subprocess,hashlib
from PIL import Image,ImageDraw
BASE=pathlib.Path('/home/astra/artifacts')
OUT=pathlib.Path(__file__).parent
receipt=[]
for name in ['captain-original-volume-longstride-v2']:
 directory=BASE/name
 if not (directory/'report.json').exists():continue
 report=json.loads((directory/'report.json').read_text())
 for v in report['variants']:
  if not ((v['silhouette'] and v['zoom']==2 and v['slowdown']==2) or (not v['silhouette'] and v['zoom']==2 and v['slowdown']==1)):continue
  file=directory/v['file']; zoom=v['zoom']; slow=v['slowdown']
  cmd=['ffmpeg','-v','error','-i',str(file),'-vf','scale=512:416:force_original_aspect_ratio=decrease:flags=neighbor,pad=512:416:0:0:color=0x23272d','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-']
  raw=subprocess.check_output(cmd,stderr=subprocess.DEVNULL); size=512*416*3; count=len(raw)//size
  obs=v['observations']; assert count==len(obs),(count,len(obs),file)
  selected=[];seen=set()
  for i,o in enumerate(obs):
   k=(o['cycle'],o['frame'])
   if k not in seen and (o['cycle']<3 or o['output_ms']==v['exact_duration_ms']):selected.append(i);seen.add(k)
  # Keep both chronological full loops for eight-key, and all first-loop frames plus wrap for dense.
  if True:selected=[i for i in selected if obs[i]['cycle']<1 or obs[i]['frame'] in [0,71]]
  per=18
  for page,start in enumerate(range(0,len(selected),per)):
   ids=selected[start:start+per];cols=3;rows=(len(ids)+cols-1)//cols
   sheet=Image.new('RGB',(512*cols,436*rows),(35,39,45));draw=ImageDraw.Draw(sheet)
   for k,i in enumerate(ids):
    img=Image.frombytes('RGB',(512,416),raw[i*size:(i+1)*size]);x=k%cols*512;y=k//cols*436
    sheet.paste(img,(x,y));o=obs[i];draw.text((x+2,y+418),f"t={o['output_ms']}ms source={o['source_elapsed_ms']} f={o['frame']}",fill='white')
   output=OUT/(name+'-'+file.stem+f'-whole-p{page}.png');sheet.save(output)
  receipt.append({'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'all_consecutive_decoded_frames':count,'contact_sheet_selected_indexes':selected,'normalization':'whole stage nearest downsample for contact grids; no pose fitting','continuous_video_ingestion':False})
(OUT/'v2-whole-stage-receipt.json').write_text(json.dumps(receipt,indent=2))
print('decoded variants',len(receipt))
