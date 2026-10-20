from pathlib import Path
import os,json,subprocess
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]));order=['00','01','02','03','04','04.5','05','06','07'];holds=[18,18,18,18,9,9,18,18,18]
arts={n:Image.open(P/'candidate'/f'{n}.png').convert('RGBA') for n in order};bg=(29,34,43)
for sz,name in [(128,'native'),(84,'game')]:
 trip=Image.new('RGBA',(3*sz,sz+20),(*bg,255));d=ImageDraw.Draw(trip)
 for j,n in enumerate(['04','04.5','05']):trip.alpha_composite(arts[n].resize((sz,sz),Image.Resampling.NEAREST),(j*sz,20));d.text((j*sz+3,2),n,fill='white')
 trip.save(P/'proof'/f'04-mid-05-{name}.png')
 if sz==128:trip.resize((trip.width*4,trip.height*4),Image.Resampling.NEAREST).save(P/'proof/04-mid-05-4x.png')
 sheet=Image.new('RGBA',(9*sz,2*(sz+20)),(*bg,255));dd=ImageDraw.Draw(sheet)
 for row in range(2):
  for j,n in enumerate(order):
   pose=('04' if n=='04.5' else n) if row==0 else n;im=arts[pose].resize((sz,sz),Image.Resampling.NEAREST);sheet.alpha_composite(im,(j*sz,row*(sz+20)+20));dd.text((j*sz+3,row*(sz+20)+2),f'{"control" if row==0 else "midtrial"} {pose}',fill='white')
 sheet.save(P/'proof'/f'full9-{name}.png')
 if sz==128:sheet.resize((sheet.width*2,sheet.height*2),Image.Resampling.NEAREST).save(P/'proof/full9-2x.png')
 size=(2*sz+32,sz+36);exposures=[]
 for n,hold in zip(order,holds):
  im=Image.new('RGB',size,bg);dd=ImageDraw.Draw(im)
  for j,pose in enumerate([('04' if n=='04.5' else n),n]):
   z=arts[pose].resize((sz,sz),Image.Resampling.NEAREST);im.paste(z,(j*(sz+16)+8,24),z);dd.text((j*(sz+16)+8,5),f'{"control" if j==0 else "midtrial"} {pose}',fill='white')
  exposures.append((im,hold))
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-threads','3','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','320','-i','-','-an','-c:v','libx264','-threads','3','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'proof'/f'paired-{name}.mp4')],stdin=subprocess.PIPE)
 for cycle in range(8):
  for im,hold in exposures:
   for _ in range(hold):proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated;max-width:100%}</style><h1>One projected-surface midpoint04.5</h1><p>Unselected no-generation trial. Both exact original04/05 and all other original keys remain unchanged.04hold splits9/320+9/320; original key starts and .45s total preserved. No crossfade or double boot. Only actual visible owned surface colors; authored projected deformation.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['04-mid-05-native','04-mid-05-game','full9-native','full9-game'])+''.join(f'<p>{s}, paired full cycle exact normal clock</p><video controls loop autoplay muted src="paired-{s}.mp4"></video>' for s in ['native','game']))
print('proof complete')
