from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];media=[]
for prefix,ids in [('paired',list(range(8))),('focused',[2,3,4,5,6])]:
 for size,scale in [(128,'native'),(84,'game')]:
  frames=[];folder=P/f'proof/{prefix}-{scale}-stages';folder.mkdir(exist_ok=True)
  for k,i in enumerate(ids):
   can=Image.new('RGB',(2*size+32,size+36),(29,34,43));d=ImageDraw.Draw(can)
   for col,bank in enumerate(['inputs/A','candidate']):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*(size+16)+8,24),im);d.text((col*(size+16)+8,5),f'{"current" if col==0 else "source"} {i:02}',fill='white')
   can.save(folder/f'{k:02}.png');frames.append(can.tobytes())
  reps=8;dest=P/f'proof/{prefix}-{scale}.mp4';proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{2*size+32}x{size+36}','-framerate','160','-i','pipe:0','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
  for tick in range(len(ids)*9*reps):proc.stdin.write(frames[(tick//9)%len(ids)])
  proc.stdin.close();assert proc.wait()==0
  stream=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,duration,nb_frames','-of','json',str(dest)],capture_output=True,text=True,check=True).stdout)['streams'][0];assert stream['r_frame_rate']=='160/1' and int(stream['nb_frames'])==len(ids)*9*reps
  media.append({'file':str(dest.relative_to(P)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'stream':stream,'hold':[9,160],'focused_reset_is_excerpt_not_cycle':prefix=='focused'})
can=Image.new('RGBA',(640,584));d=ImageDraw.Draw(can)
for row,bg in enumerate([(29,34,43,255),(235,230,215,255),(64,111,80,255),(105,76,122,255)]):
 d.rectangle((0,row*146,640,(row+1)*146),fill=bg)
 for col,i in enumerate([2,3,4,5,6]):can.alpha_composite(Image.open(P/'candidate'/f'{i:02}.png').convert('RGBA'),(col*128,row*146+18));d.text((col*128+3,row*146+2),f'source {i:02}',fill='black' if row==1 else 'white')
can.save(P/'proof/02-03-04-05-06-contrasting-grounds-native.png')
(P/'proof/MEDIA-RECEIPT.json').write_text(json.dumps({'media':media,'stage':[128,128],'game_proxy':[84,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'no_game_runtime_or_quality_claim':True},indent=2)+'\n')
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Lyra SE03/04 source repair</title><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>Lyra SE03/04 source-painted repair</h1><p>Current left, candidate right. Original upper/hem/full visible gloves and other6cels exact. Each stage9/160s. Focused reset is an excerpt, not whole-cycle evidence.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" autoplay loop muted controls></video>' for n in ['paired-native','paired-game','focused-native','focused-game'])+'<p>02→03→04→05→06</p><img src="02-03-04-05-06-native.png"><p>All8</p><img src="full8-native.png">')
print(json.dumps({'normal_speed_media':len(media),'full8_cycles':[9,20]},indent=2))
