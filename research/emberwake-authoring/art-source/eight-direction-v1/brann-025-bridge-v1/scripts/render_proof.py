from pathlib import Path
import os,json,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]));t=json.loads((R/'TIMING.json').read_text());order=t['order'];holds=t['hold_ticks'];bg=(233,233,222)
def im(n):return Image.open(R/'frames'/f'{n}.png').convert('RGBA')
for sz,name in [(128,'native'),(256,'2x'),(84,'game')]:
 can=Image.new('RGBA',(3*sz,sz+20),(*bg,255));d=ImageDraw.Draw(can)
 for j,n in enumerate(['02','02.5','03']):can.alpha_composite(im(n).resize((sz,sz),Image.Resampling.NEAREST),(j*sz,20));d.text((j*sz+3,2),f'{n}'+(' GUIDE' if n=='02.5' else ' exact'),fill='black')
 can.save(R/'proof'/f'02-mid-03-{name}.png')
 if sz==128:can.resize((can.width*4,can.height*4),Image.Resampling.NEAREST).save(R/'proof/02-mid-03-4x.png')
 if sz==256:continue
 full=Image.new('RGBA',(9*sz,2*(sz+20)),(*bg,255));d=ImageDraw.Draw(full)
 for row in range(2):
  for j,n in enumerate(order):
   k='02' if row==0 and n=='02.5' else n;full.alpha_composite(im(k).resize((sz,sz),Image.Resampling.NEAREST),(j*sz,row*(sz+20)+20));d.text((j*sz+3,row*(sz+20)+2),f'{"control"if row==0 else"guide"} {k}',fill='black')
 full.save(R/'proof'/f'full9-{name}.png')
 size=(2*sz+32,sz+36);ex=[]
 for n,hold in zip(order,holds):
  z=Image.new('RGB',size,bg);dd=ImageDraw.Draw(z)
  for j,k in enumerate([('02' if n=='02.5' else n),n]):
   a=im(k).resize((sz,sz),Image.Resampling.NEAREST);z.paste(a,(j*(sz+16)+8,24),a);dd.text((j*(sz+16)+8,5),f'{"control"if j==0 else"guide"} {k}',fill='black')
  ex.append((z,hold))
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-threads','3','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','320','-i','-','-an','-c:v','libx264','-threads','3','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'proof'/f'paired-{name}.mp4')],stdin=subprocess.PIPE)
 for _ in range(8):
  for z,hold in ex:
   for __ in range(hold):proc.stdin.write(z.tobytes())
 proc.stdin.close();assert proc.wait()==0
(R/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#e9e9de;color:#111;font:16px sans-serif}img,video{image-rendering:pixelated;max-width:100%}</style><h1>Brann SE02.5 source-pixel guide only</h1><p>No generation or art acceptance. Exact02 upper. Only one new drawing; original8PNGs and key starts fixed. Split02hold into9/320+9/320;9exposures total.45s. Visible03Q surfaces use separatecloth/cuff/heel/toe projection;02P retracts1pixel. No hidden anatomy/contact claim.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['02-mid-03-native','02-mid-03-2x','02-mid-03-game','full9-native','full9-game'])+''.join(f'<p>{n}exactnormalclock</p><video controls autoplay muted loop src="paired-{n}.mp4"></video>' for n in ['native','game']))
print('GUIDE proof ready')
