from pathlib import Path
import struct,zlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BG={'light':(225,225,215,255),'dark':(25,29,36,255),'ground':(77,103,60,255)}
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
def chunks(data):
 p=8
 while p<len(data):
  n=struct.unpack('>I',data[p:p+4])[0];yield data[p+4:p+8],data[p+8:p+8+n];p+=12+n
def apng(files,out):
 parts=[list(chunks(p.read_bytes())) for p in files];seq=0
 ihdr=next(d for k,d in parts[0] if k==b'IHDR');w,h=struct.unpack('>II',ihdr[:8])
 result=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ihdr)+chunk(b'acTL',struct.pack('>II',len(files),0))
 for i,part in enumerate(parts):
  result+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,h,0,0,9,160,0,0));seq+=1
  for k,d in part:
   if k==b'IDAT':
    if i==0:result+=chunk(k,d)
    else:result+=chunk(b'fdAT',struct.pack('>I',seq)+d);seq+=1
 result+=chunk(b'IEND',b'');out.write_bytes(result)
for view in ['se','ne']:
 files=[ROOT/view/'frames'/f'{i:02}.png' for i in range(8)];frames=[Image.open(p).convert('RGBA') for p in files]
 for label,factor in [('native',1),('2x',2),('066',.66)]:
  size=round(128*factor);sh=Image.new('RGBA',(size*9,size*3+18*3),(255,255,255,255));d=ImageDraw.Draw(sh)
  for r,(name,color) in enumerate(BG.items()):
   y=r*(size+18);d.text((2,y),f'{view} {name} {label} : 00 01 02 03 04 05 06 07 00 wrap',fill='black')
   for c,im in enumerate(frames+[frames[0]]):
    bg=Image.new('RGBA',(size,size),color);bg.alpha_composite(im.resize((size,size),Image.Resampling.NEAREST));sh.paste(bg,(c*size,y+18))
  sh.save(ROOT/'diagnostics'/f'{view}-{label}-three-backgrounds.png')
 apng(files,ROOT/view/'walk.apng')
 # A 4x lower-only chronological sheet for joint inspection.
 sh=Image.new('RGBA',(72*9,56),(225,225,215,255))
 for i,im in enumerate(frames+[frames[0]]):sh.alpha_composite(im.crop((28,72,100,128)),(72*i,0))
 sh.resize((2592,224),Image.Resampling.NEAREST).save(ROOT/'diagnostics'/f'{view}-lower-4x.png')
 # Video contains four exact loops at the original 160fps clock.
 d=ROOT/view/'video-frames';d.mkdir(exist_ok=True)
 for tick in range(288):
  bg=Image.new('RGBA',(128,128),BG['ground']);bg.alpha_composite(frames[(tick//9)%8]);bg.convert('RGB').save(d/f'{tick:03}.png')
json.dump({'native_stage':[128,128],'pivot':[64,112],'frames':list(range(8)),'fps':160,'ticks_per_frame':9,'duration_per_frame':'9/160','loop_duration':'9/20','apng_delay_num':9,'apng_delay_den':160,'0.66_proxy_dimensions':[84,84],'no_world_translation_or_engine_acceptance':True},open(ROOT/'TIMING.json','w'),indent=2)
print('Exact rational APNG and chronological native/2x/.66 diagnostics written.')
