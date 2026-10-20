from pathlib import Path
from PIL import Image,ImageDraw
import subprocess
out=Path(__file__).parent
equip=Path('/home/astra/projects/captain-3d-rig-lab/render/equipped-carry-v1');cam=Path('/home/astra/projects/captain-3d-generation-lab/camera-readability-v1/artifacts/full-minus45')
def grid(items,name,size=256):
 for page in range((len(items)+19)//20):
  ims=items[page*20:page*20+20];img=Image.new('RGB',(5*size,4*(size+22)),(35,40,45));d=ImageDraw.Draw(img)
  for j,(im,label) in enumerate(ims):
   im=im.convert('RGBA').resize((size,size),Image.Resampling.NEAREST);t=Image.new('RGBA',(size,size),(35,40,45,255));t.alpha_composite(im);x=j%5*size;y=j//5*(size+22);img.paste(t.convert('RGB'),(x,y));d.text((x,y+size),label,fill='white')
  img.save(out/f'{name}-p{page}.png')
def decode(path,size):
 p=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout;n=len(p)//(size*size*3);return [Image.frombytes('RGB',(size,size),p[i*size*size*3:(i+1)*size*size*3]) for i in range(n)]
for folder,glob,name,video,sz in [(equip,'frame-*.png','equipped',equip/'diagnostic.mp4',256),(cam,'angle-45-key-*.png','camera-minus45',cam/'walk-preview-2x.mp4',512)]:
 frames=sorted(folder.glob(glob));grid([(Image.open(p),f'{i} {i/60:.3f}s') for i,p in enumerate(frames)],name+'-source');dec=decode(video,sz);grid([(im,f'decoded {i} {i/60:.3f}s') for i,im in enumerate(dec)],name+'-actual');grid([(im,f'decoded {i}') for i,im in enumerate(dec)],name+'-actual2x',512)
 grid([(dec[i],f'wrap f{i}') for i in [61,62,63,64,0,1,2,3]],name+'-wrap',512)
 sil=out/(name+'-silhouette-input');sil.mkdir(exist_ok=True)
 for i,p in enumerate(frames):
  a=Image.open(p).convert('RGBA');bg=Image.new('RGB',a.size,(35,40,45));bg.paste((0,0,0),(0,0,*a.size),a.getchannel('A'));bg.save(sil/f'{i:03}.png')
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',str(sil/'%03d.png'),'-c:v','libx264','-crf','10','-pix_fmt','yuv420p',str(out/(name+'-silhouette.mp4'))],check=True)
 ds=decode(out/(name+'-silhouette.mp4'),256);grid([(im,f'sil f{i}') for i,im in enumerate(ds)],name+'-silhouette');print(name,len(frames),len(dec),len(ds))
