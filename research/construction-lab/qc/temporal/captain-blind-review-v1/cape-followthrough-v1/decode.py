from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw
r=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-followthrough-gpu-audition-v1');o=Path(__file__).parent;receipts=[]
for variant in ['baseline','followthrough']:
 for rate in ['normal','half']:
  p=r/variant/(rate+'.mp4');raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','rawvideo','-pix_fmt','rgb24','-']);n=len(raw)//(384*384*3);sel=list(range(68));prefix=variant+'-'+rate
  for pg in range(4):
   inds=sel[pg*17:(pg+1)*17];sheet=Image.new('RGB',(4*384,5*404),(30,34,38));d=ImageDraw.Draw(sheet)
   for i,idx in enumerate(inds):
    im=Image.frombytes('RGB',(384,384),raw[idx*384*384*3:(idx+1)*384*384*3]);x=(i%4)*384;y=(i//4)*404;sheet.paste(im,(x,y));d.text((x+4,y+386),f'{prefix} packet{idx} cel{idx%65} source{2*(idx%65)+1}',fill='white')
   sheet.save(o/f'{prefix}-p{pg}.png')
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(p)]));receipts.append({'video':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded':n,'visually_selected':sel,'probe':probe})
(o/'actual-decode-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
