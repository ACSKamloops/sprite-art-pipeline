from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,hashlib
out=Path(__file__).parent;src=Path('/home/astra/artifacts/captain-articulated-v7-world-native384'); inds=list(range(0,130,2))+list(range(130,138,2))
receipt=[]
for kind in ['colour','silhouette']:
 p=src/f'continuous-1x-{kind}.mp4'
 expr='+'.join(f'eq(n,{i})' for i in inds)
 b=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-vf',f"select='{expr}',crop=530:530:500:60",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],check=True,capture_output=True).stdout
 ims=[Image.frombytes('RGB',(530,530),b[i:i+530*530*3]) for i in range(0,len(b),530*530*3)]
 for page in range((len(ims)+11)//12):
  c=Image.new('RGB',(1590,2208),(35,40,45));d=ImageDraw.Draw(c)
  for j,im in enumerate(ims[page*12:page*12+12]):
   idx=page*12+j;x=j%3*530;y=j//3*552;c.paste(im,(x,y));d.text((x,y+530),f'actual packet {inds[idx]} cel {inds[idx]//2%65} {inds[idx]/120:.3f}s',fill='white')
  c.save(out/f'world-{kind}-p{page}.png')
 receipt.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'selected_packets':inds,'crop_fixed_xywh':[500,60,530,530],'decoded_selected_count':len(ims)})
(out/'world-decode-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
