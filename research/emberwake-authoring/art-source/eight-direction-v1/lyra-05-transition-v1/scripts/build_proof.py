from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
bgs=[('light',(235,230,215)),('dark',(29,34,43)),('green',(64,111,80))]
banks=['inputs/cycle','candidate']
for ids,prefix in [([2,3,4,5,6],'02-03-04-05-06'),(list(range(8)),'full8')]:
 for size,label in [(128,'native'),(256,'2x'),(84,'game')]:
  can=Image.new('RGB',(len(ids)*size,6*(size+18)))
  d=ImageDraw.Draw(can)
  for bgrow,(bgname,bg)in enumerate(bgs):
   for bankrow,bank in enumerate(banks):
    row=bgrow*2+bankrow;y=row*(size+18);d.rectangle((0,y,can.width,y+size+18),fill=bg)
    for col,i in enumerate(ids):
     im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*size,y+18),im);d.text((col*size+3,y+2),f'{"frozen"if bankrow==0 else"trial"} {i:02} {bgname}',fill='black'if bgrow==0 else'white')
  can.save(P/f'proof/{prefix}-{label}.png')
# Focused lower contour inspection preserves all stage coordinates; crop is diagnostic only.
can=Image.new('RGBA',(5*340,2*285),(235,230,215,255));d=ImageDraw.Draw(can)
for row,bank in enumerate(banks):
 for col,i in enumerate([2,3,4,5,6]):
  im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').crop((32,70,96,122)).resize((320,260),Image.Resampling.NEAREST);can.alpha_composite(im,(col*340+10,row*285+20));d.text((col*340+10,row*285+2),f'{"frozen"if row==0 else"trial"} {i:02}',fill='black')
can.save(P/'proof/focused-lower-5x.png')
media=[]
for size,label in [(128,'native'),(84,'game')]:
 width=size*2+32;height=(size+24)*3;frames=[]
 for i in range(8):
  can=Image.new('RGB',(width,height));d=ImageDraw.Draw(can)
  for r,(bgname,bg)in enumerate(bgs):
   y=r*(size+24);d.rectangle((0,y,width,y+size+24),fill=bg)
   for c,bank in enumerate(banks):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);x=8+c*(size+16);can.paste(im,(x,y+24),im);d.text((x,y+5),f'{"frozen"if c==0 else"trial"} {i:02}',fill='black'if r==0 else'white')
  frames.append(can.tobytes())
 dest=P/f'proof/full8-paired-{label}.mp4';p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{width}x{height}','-framerate','160','-i','pipe:0','-c:v','libx264','-threads','2','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
 for _ in range(8):
  for frame in frames:
   for __ in range(9):p.stdin.write(frame)
 p.stdin.close();assert p.wait()==0
 info=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,duration,nb_frames','-of','json',str(dest)],capture_output=True,text=True,check=True).stdout)['streams'][0];assert info['r_frame_rate']=='160/1'and int(info['nb_frames'])==576
 media.append({'file':str(dest.relative_to(P)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'stream':info,'exact_each_hold':[9,160],'loops':8})
(P/'proof/MEDIA-RECEIPT.json').write_text(json.dumps({'media':media,'native':[128,128],'game_proxy':[84,128],'clock':'9/160s each;0.45s loop','runtime_claim':False},indent=2)+'\n')
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Lyra05 source trial</title><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated;max-width:100%}</style><p>Only05 lower trial; frozen03/04 and other7 exact. No model calls. Source visible paint and authored projections; no recovered hidden anatomy. Exact9/160 holds. Candidate pending review.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" controls autoplay loop muted></video>'for n in ['full8-paired-native','full8-paired-game'])+''.join(f'<p>{n}</p><img src="{n}.png">'for n in ['02-03-04-05-06-native','02-03-04-05-06-2x','02-03-04-05-06-game','full8-native','full8-game']))
print('compact preview proof complete; 6 sheets, 1 focused lower, 2 normal-clock videos')
