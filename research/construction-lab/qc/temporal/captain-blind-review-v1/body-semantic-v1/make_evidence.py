from pathlib import Path
from PIL import Image, ImageDraw
import subprocess
out=Path(__file__).parent
src=Path('/home/astra/projects/captain-3d-rig-lab/render/body-semantic-v1')
def grid(items,name,size=256,cols=5):
 for page in range((len(items)+19)//20):
  chunk=items[page*20:page*20+20]; canvas=Image.new('RGB',(cols*size,4*(size+23)),(35,40,45));d=ImageDraw.Draw(canvas)
  for j,(p,label) in enumerate(chunk):
   im=Image.open(p).convert('RGBA');im=im.resize((size,size),Image.Resampling.NEAREST); tile=Image.new('RGBA',im.size,(35,40,45,255));tile.alpha_composite(im); x=j%cols*size;y=j//cols*(size+23);canvas.paste(tile.convert('RGB'),(x,y));d.text((x+3,y+size+3),label,fill='white')
  canvas.save(out/f'{name}-p{page}.png')
frames=sorted(src.glob('frame-*.png'));grid([(p,f'{i}: {i/60:.3f}s CMU{88+i*2}') for i,p in enumerate(frames)],'source')
dec=sorted((out/'decoded').glob('*.png'));grid([(p,f'decoded {i}: {i/60:.3f}s') for i,p in enumerate(dec)],'actual-native');grid([(p,f'decoded {i}: {i/60:.3f}s') for i,p in enumerate(dec)],'actual-nearest2x',512)
# Three-cycle instrumental silhouette export from actual source alpha, same canvas/timing; not art changes.
sil=out/'silhouette-input';sil.mkdir(exist_ok=True)
for i,p in enumerate(frames):
 im=Image.open(p).convert('RGBA'); bg=Image.new('RGB',(256,256),(35,40,45));bg.paste((0,0,0),(0,0,256,256),im.getchannel('A'));bg.save(sil/f'{i:03}.png')
subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',str(sil/'%03d.png'),'-c:v','libx264','-crf','10','-pix_fmt','yuv420p',str(out/'silhouette.mp4')],check=True)
sd=out/'silhouette-decoded';sd.mkdir(exist_ok=True);subprocess.run(['ffmpeg','-v','error','-i',str(out/'silhouette.mp4'),'-vsync','0',str(sd/'%03d.png')],check=True)
grid([(p,f'silhouette decoded {i}: {i/60:.3f}s') for i,p in enumerate(sorted(sd.glob('*.png')))],'actual-silhouette')
grid([(dec[i],f'wrap f{i}') for i in [60,61,62,63,64,0,1,2,3,4]],'wrap',512)
ref=Path('/home/astra/projects/captain-3d-rig-lab/motion/cmu07/official-preview');grid([(p,p.name) for p in sorted(ref.glob('*.png'))],'official-control')
print(len(frames),len(dec))
