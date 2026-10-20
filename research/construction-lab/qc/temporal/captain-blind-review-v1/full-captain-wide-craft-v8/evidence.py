from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import subprocess,re,json
out=Path(__file__).parent;src=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-wide-craft-v8/native256')
def grid(items,name,size=256):
 for page in range((len(items)+19)//20):
  canvas=Image.new('RGB',(5*size,4*(size+22)),(35,40,45));d=ImageDraw.Draw(canvas)
  for j,(im,label) in enumerate(items[page*20:page*20+20]):
   im=im.convert('RGBA').resize((size,size),Image.Resampling.NEAREST);b=Image.new('RGBA',im.size,(35,40,45,255));b.alpha_composite(im);x=j%5*size;y=j//5*(size+22);canvas.paste(b.convert('RGB'),(x,y));d.text((x,y+size),label,fill='white')
  canvas.save(out/f'{name}-p{page}.png')
def decode(p,size):
 b=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','rawvideo','-pix_fmt','rgb24','-'],check=True,capture_output=True).stdout;return [Image.frombytes('RGB',(size,size),b[i:i+size*size*3]) for i in range(0,len(b),size*size*3)]
frames=sorted(p for p in src.glob('frame-*.png') if re.fullmatch(r'frame-\d{3}.png',p.name));grid([(Image.open(p),f'{i}: {i/60:.3f}s') for i,p in enumerate(frames)],'source')
receipt=[]
for fn,size,fps in [('full-captain-1x-normal.mp4',256,60),('full-captain-2x-normal.mp4',512,60),('full-captain-1x-half-speed.mp4',256,30)]:
 dec=decode(src/fn,size);inds=list(range(68))+list(range(127,133))+list(range(191,195));grid([(dec[i],f'packet{i} f{i%65} {i/fps:.3f}s') for i in inds],fn[:-4],size);receipt.append({'file':fn,'decoded':len(dec),'view_selected':inds,'fps':fps})
sil=out/'silhouette-input';sil.mkdir(exist_ok=True)
for i,p in enumerate(frames):
 a=Image.open(p).convert('RGBA');b=Image.new('RGB',a.size,(35,40,45));b.paste((0,0,0),(0,0,*a.size),a.getchannel('A'));b.save(sil/f'{i:03}.png')
subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',str(sil/'%03d.png'),'-c:v','libx264','-crf','10','-pix_fmt','yuv420p',str(out/'silhouette.mp4')],check=True);ds=decode(out/'silhouette.mp4',256);grid([(im,f'f{i} {i/60:.3f}s') for i,im in enumerate(ds)],'silhouette');grid([(ds[i],f'wrap f{i}') for i in [61,62,63,64,0,1,2,3]],'silhouette-wrap',512)
grid([(Image.open(src/n),n) for n in ['frame-064.png','loop-endpoint.png','frame-000.png','frame-001.png']],'endpoint',512)
a=Image.open(src/'frame-000.png').convert('RGBA');b=Image.open(src/'loop-endpoint.png').convert('RGBA');pa=list(a.getdata());pb=list(b.getdata());changed=sum(x!=y for x,y in zip(pa,pb));maximum=max(abs(v-w) for x,y in zip(pa,pb) for v,w in zip(x,y));receipt.append({'endpoint_RGBA_changed_pixels':changed,'max_channel_delta':maximum});(out/'decode-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(changed,maximum)
