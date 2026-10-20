from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,hashlib,numpy as np
P=Path(__file__).resolve().parents[1];media=[]
for prefix,ids in [('paired',list(range(8))),('focused',[6,7,0])]:
 for size,scale in [(128,'native'),(84,'game')]:
  frames=[];folder=P/f'proof/{prefix}-{scale}-stages';folder.mkdir(exist_ok=True)
  for k,i in enumerate(ids):
   can=Image.new('RGB',(2*size+32,size+36),(29,34,43));d=ImageDraw.Draw(can)
   for col,bank in enumerate(['inputs/cycle','candidate']):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*(size+16)+8,24),im);d.text((col*(size+16)+8,5),f'{"current" if col==0 else "source07"} {i:02}',fill='white')
   can.save(folder/f'{k:02}.png');frames.append(can.tobytes())
  reps=8 if prefix=='paired' else 12;dest=P/f'proof/{prefix}-{scale}.mp4';proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{2*size+32}x{size+36}','-framerate','160','-i','pipe:0','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
  for tick in range(len(ids)*9*reps):proc.stdin.write(frames[(tick//9)%len(ids)])
  proc.stdin.close();assert proc.wait()==0
  stream=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,duration,nb_frames','-of','json',str(dest)],capture_output=True,text=True,check=True).stdout)['streams'][0];assert stream['r_frame_rate']=='160/1' and int(stream['nb_frames'])==len(ids)*9*reps
  media.append({'file':str(dest.relative_to(P)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'stream':stream,'hold':[9,160]})
can=Image.new('RGBA',(384,584));d=ImageDraw.Draw(can)
for row,bg in enumerate([(29,34,43,255),(235,230,215,255),(64,111,80,255),(105,76,122,255)]):
 d.rectangle((0,row*146,384,(row+1)*146),fill=bg)
 for col,i in enumerate([6,7,0]):can.alpha_composite(Image.open(P/'candidate'/f'{i:02}.png').convert('RGBA'),(col*128,row*146+18));d.text((col*128+3,row*146+2),f'source07 {i:02}',fill='black' if row==1 else 'white')
can.save(P/'proof/06-07-00-contrasting-grounds-native.png')
Y,X=np.indices((128,128));bounds={}
for bank in ['inputs/cycle','candidate']:
 a=np.array(Image.open(P/bank/'07.png').convert('RGBA'));bounds[bank]={}
 for side,region in [('screen-left',(X<64)&(Y>=92)),('screen-right',(X>=64)&(Y>=92))]:
  for threshold in [0,128]:
   yy,xx=np.where((a[...,3]>threshold)&region);bounds[bank][f'{side}-alpha>{threshold}']=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
(P/'proof/MEDIA-RECEIPT.json').write_text(json.dumps({'media':media,'projected_foot_bounds':bounds,'stage':[128,128],'pivot':[64,112],'cycle':[9,20],'actual_context':'root combined cycle-v2; direct03+hybrid04+existing05; only07 differs','runtime_claim':False},indent=2)+'\n')
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Source06-trouser07 transition</title><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>New authored07 from visible source06 paint</h1><p>Actual combined-cycle-v2 current07 left, new source-leg07 right. Other7cels exact. Every stage9/160s.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" autoplay loop muted controls></video>' for n in ['paired-native','paired-game','focused-native','focused-game'])+'<p>06→07→00</p><img src="06-07-00-native.png"><p>All8</p><img src="full8-native.png">')
print(json.dumps({'normal_speed_videos':len(media),'foot_bounds':bounds},indent=2))
