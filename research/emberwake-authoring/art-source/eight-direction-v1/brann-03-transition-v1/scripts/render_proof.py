from pathlib import Path
import os,subprocess
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]));bg=(233,233,222)
for sz,name in [(128,'native'),(84,'game'),(256,'2x')]:
 for label,seq in [('02-03-04',[2,3,4]),('full8',list(range(8)))]:
  can=Image.new('RGBA',(len(seq)*sz,2*(sz+18)),(*bg,255));d=ImageDraw.Draw(can)
  for row,folder in enumerate(['inputs/control','frames']):
   for j,i in enumerate(seq):
    im=Image.open(P/folder/f'{i:02}.png').convert('RGBA').resize((sz,sz),Image.Resampling.NEAREST);can.alpha_composite(im,(j*sz,row*(sz+18)+18));d.text((j*sz+3,row*(sz+18)+2),f'{"base" if row==0 else "trial"} {i:02}',fill='black')
  can.save(P/'proof'/f'{label}-{name}.png')
  if label=='02-03-04' and sz==128:can.resize((can.width*4,can.height*4),Image.Resampling.NEAREST).save(P/'proof/02-03-04-4x.png')
 if sz==256:continue
 size=(2*sz+32,sz+36);ex=[]
 for i in range(8):
  im=Image.new('RGB',size,bg);d=ImageDraw.Draw(im)
  for j,folder in enumerate(['inputs/control','frames']):
   z=Image.open(P/folder/f'{i:02}.png').convert('RGBA').resize((sz,sz),Image.Resampling.NEAREST);im.paste(z,(j*(sz+16)+8,24),z);d.text((j*(sz+16)+8,5),f'{"base" if j==0 else "trial"} {i:02}',fill='black')
  ex.append(im)
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-threads','3','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','160','-i','-','-an','-c:v','libx264','-threads','3','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'proof'/f'paired-{name}.mp4')],stdin=subprocess.PIPE)
 for cycle in range(8):
  for im in ex:
   for _ in range(9):proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#e9e9de;color:#111;font:16px sans-serif}img,video{image-rendering:pixelated;max-width:100%}</style><h1>Brann SE03 lower transition trial</h1><p>Unselected no-generation test. Only03 lower changes. Other7PNGs, actual03upper and full.45s clock exact. Q uses an authored projected actual00/04boot surface; P retreating source layer unchanged. No hidden anatomy claim.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['02-03-04-native','02-03-04-game','full8-native','full8-game'])+''.join(f'<p>{n}normal-clock base/trial</p><video controls loop autoplay muted src="paired-{n}.mp4"></video>' for n in ['native','game']))
print('proof ready')
