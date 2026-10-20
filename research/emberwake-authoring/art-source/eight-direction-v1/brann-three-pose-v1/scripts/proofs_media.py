from pathlib import Path
import json,struct,zlib,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BG={'light':(233,233,222,255),'dark':(27,30,39,255),'ground':(94,96,63,255)}
control=[Image.open(ROOT/'inputs/v5-frames'/f'{i:02}.png').convert('RGBA')for i in range(8)];frames=[Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA')for i in range(8)]
def composite(im,s,c):
 b=Image.new('RGBA',(s,s),c);b.alpha_composite(im.resize((s,s),Image.Resampling.NEAREST));return b
for name,s in [('native',128),('066',84),('2x',256)]:
 chrono=Image.new('RGBA',(9*s,3*(s+18)));cd=ImageDraw.Draw(chrono);pairs=Image.new('RGBA',(8*(2*s+8),3*(s+18)));pd=ImageDraw.Draw(pairs)
 for row,(label,color)in enumerate(BG.items()):
  y=row*(s+18);cd.rectangle((0,y,chrono.width,y+18),fill='white');pd.rectangle((0,y,pairs.width,y+18),fill='white')
  for col,im in enumerate(frames+[frames[0]]):chrono.paste(composite(im,s,color),(col*s,y+18));cd.text((col*s+2,y+1),f'{col%8:02} {label}',fill='black')
  for i in range(8):
   x=i*(2*s+8);pairs.paste(composite(frames[i],s,color),(x,y+18));pairs.paste(composite(frames[(i+1)%8],s,color),(x+s,y+18));pd.text((x+2,y+1),f'{i:02}>{(i+1)%8:02} {label}',fill='black')
 chrono.save(ROOT/'proof'/f'chronology-{name}.png');pairs.save(ROOT/'proof'/f'every-pair-{name}.png')
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
def chunks(data):
 p=8
 while p<len(data):
  n=struct.unpack('>I',data[p:p+4])[0];yield data[p+4:p+8],data[p+8:p+8+n];p+=12+n
def apng(files,path):
 parts=[list(chunks(p.read_bytes()))for p in files];ihdr=next(d for k,d in parts[0]if k==b'IHDR');w,h=struct.unpack('>II',ihdr[:8]);seq=0;out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ihdr)+chunk(b'acTL',struct.pack('>II',8,0))
 for i,cs in enumerate(parts):
  out+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,h,0,0,9,160,0,0));seq+=1
  for k,d in cs:
   if k!=b'IDAT':continue
   if i==0:out+=chunk(k,d)
   else:out+=chunk(b'fdAT',struct.pack('>I',seq)+d);seq+=1
 path.write_bytes(out+chunk(b'IEND',b''))
apng([ROOT/'frames'/f'{i:02}.png'for i in range(8)],ROOT/'three-pose.apng');apng([ROOT/'inputs/v5-frames'/f'{i:02}.png'for i in range(8)],ROOT/'v5-control.apng')
holds=[];im=Image.open(ROOT/'three-pose.apng')
for i in range(8):im.seek(i);holds.append(im.info['duration']);assert im.convert('RGBA').tobytes()==frames[i].tobytes()
assert holds==[56.25]*8
proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgba','-video_size','512x256','-framerate','160','-i','pipe:0','-c:v','libx264','-pix_fmt','yuv420p',str(ROOT/'normal-clock-v5-vs-trial-8loops.mp4')],stdin=subprocess.PIPE)
for tick in range(576):
 i=(tick//9)%8;sh=Image.new('RGBA',(512,256),BG['ground']);sh.paste(composite(control[i],256,BG['ground']),(0,0));sh.paste(composite(frames[i],256,BG['ground']),(256,0));proc.stdin.write(sh.tobytes())
proc.stdin.close();assert proc.wait()==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=r_frame_rate,nb_frames,duration','-of','json',str(ROOT/'normal-clock-v5-vs-trial-8loops.mp4')]))
assert probe['streams'][0]['nb_frames']=='576'and probe['streams'][0]['duration']=='3.600000'
(ROOT/'MEDIA-RECEIPT.json').write_text(json.dumps({'APNG8_RGBA_exact':True,'APNG_holds_ms':holds,'mp4':probe,'mp4_side_by_side':'v5 left, candidate right; whole-stage2x nearest display','mp4_lossy_preview':True,'control_and_candidate_clock_equal':True,'human_continuous_playback_and_engine_physical_contact_unverified':True},indent=2)+'\n')
print('Full8+wrap and everypair native/.66/2x, exact56.25ms APNG holds, v5/candidate normal-clock8loops comparison.')
