from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
for i in range(8):
 src=P/'inputs/A'/f'{i:02}.png'
 if i==4:src=P/'inputs/new04.png'
 if i==7:src=P/'inputs/generated07.png'
 shutil.copy2(src,P/'preview/control-frames'/f'{i:02}.png')
 if i==7:shutil.copy2(P/'proposal/07.png',P/'preview/frames/07.png')
 else:shutil.copy2(src,P/'preview/frames'/f'{i:02}.png')
def sheet(ids,size,prefix):
 can=Image.new('RGBA',(len(ids)*size,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,bank in enumerate(['preview/control-frames','preview/frames']):
  for k,i in enumerate(ids):
   im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.alpha_composite(im,(k*size,row*(size+18)+18));d.text((k*size+3,row*(size+18)+2),f'{"generated" if row==0 else "hybrid"} {i:02}',fill='white')
 can.save(P/f'proof/{prefix}.png');return can
for ids,prefix in [(list(range(8)),'full8'),([6,7,0],'06-07-00')]:
 im=sheet(ids,128,prefix+'-native');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(P/f'proof/{prefix}-3x.png');sheet(ids,84,prefix+'-game')
media=[]
for prefix,ids in [('paired',list(range(8))),('focused',[6,7,0])]:
 for size,scale in [(128,'native'),(84,'game')]:
  frames=[];folder=P/f'proof/{prefix}-{scale}-stages';folder.mkdir(exist_ok=True)
  for k,i in enumerate(ids):
   can=Image.new('RGB',(2*size+32,size+36),(29,34,43));d=ImageDraw.Draw(can)
   for col,bank in enumerate(['preview/control-frames','preview/frames']):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*(size+16)+8,24),im);d.text((col*(size+16)+8,5),f'{"generated" if col==0 else "hybrid"} {i:02}',fill='white')
   can.save(folder/f'{k:02}.png');frames.append(can.tobytes())
  reps=8 if prefix=='paired' else 12;video=P/f'proof/{prefix}-{scale}.mp4';proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{2*size+32}x{size+36}','-framerate','160','-i','pipe:0','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
  for tick in range(len(ids)*9*reps):proc.stdin.write(frames[(tick//9)%len(ids)])
  proc.stdin.close();assert proc.wait()==0
  info=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,duration,nb_frames','-of','json',str(video)],check=True,capture_output=True,text=True).stdout)['streams'][0]
  assert info['r_frame_rate']=='160/1' and int(info['nb_frames'])==len(ids)*9*reps
  media.append({'file':str(video.relative_to(P)),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'stream':info,'hold':[9,160]})
can=Image.new('RGBA',(384,4*146));d=ImageDraw.Draw(can)
for row,bg in enumerate([(29,34,43,255),(235,230,215,255),(64,111,80,255),(105,76,122,255)]):
 d.rectangle((0,row*146,384,(row+1)*146),fill=bg)
 for col,phase in enumerate([6,7,0]):can.alpha_composite(Image.open(P/'preview/frames'/f'{phase:02}.png').convert('RGBA'),(128*col,146*row+18));d.text((128*col+3,146*row+2),f'hybrid {phase:02}',fill='white' if row!=1 else 'black')
can.save(P/'proof/06-07-00-contrasting-grounds-native.png')
# Inspect literal owner coordinates rather than treating a whole-stage half-plane as anatomy.
Y,X=np.indices((128,128));measure={}
for name,path in [('old07','inputs/A/07.png'),('generated07','inputs/generated07.png'),('hybrid07','proposal/07.png')]:
 a=np.array(Image.open(P/path).convert('RGBA'));measure[name]={}
 for side,region in [('screen-left',(X<64)&(Y>=92)),('screen-right',(X>=64)&(Y>=92))]:
  for threshold in [0,128]:
   yy,xx=np.where((a[...,3]>threshold)&region);measure[name][side+f'-alpha>{threshold}']={'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]}
(P/'proof/MEDIA-RECEIPT.json').write_text(json.dumps({'status':'UNSELECTED07 source-boot hybrid preview; no art approval or runtime claim','media':media,'projected_lower_bounds':measure,'notes':['Target strong-alpha sole positions remain108(screen-right)/102(screen-left).','Complete original source alpha fringe may extend one row below the strong-alpha sole.','Both fullcycle banks contain new04 and original03;03 model failure is excluded.']},indent=2)+'\n')
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><title>07 source-boot hybrid</title><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>No-generation07 boot-only hybrid</h1><p>Generated07 control left, source-boot hybrid right. Original03 and new04 in both banks. Every stage9/160s.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" autoplay loop muted controls></video>' for n in ['paired-native','paired-game','focused-native','focused-game'])+'<p>All8</p><img src="full8-native.png"><p>06→07→00</p><img src="06-07-00-native.png"><p>Old07,generated07,boot-hybrid07</p><img src="old-new-hybrid-native.png">')
print(json.dumps({'media_count':len(media),'bounds':measure},indent=2))
