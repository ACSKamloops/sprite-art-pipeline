#!/usr/bin/env python3
from pathlib import Path
import json,struct,zlib,subprocess
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
MODES=('source','held-contact-pass-control','trial-a-down','trial-b-boot-preserved')
COLORS=(35,39,47,255)
def chunks(p):
 b=p.read_bytes();i=8
 while i<len(b):
  n=int.from_bytes(b[i:i+4],'big');t=b[i+4:i+8];d=b[i+8:i+8+n];yield t,d;i+=12+n

def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
def apng(frames,p):
 w,h=frames[0].size;b=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(frames),0));seq=0
 for i,im in enumerate(frames):
  b+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,h,0,0,9,160,0,0));seq+=1
  raw=np.array(im.convert('RGBA'));payload=zlib.compress(b''.join(b'\0'+row.tobytes() for row in raw),9)
  if i==0:b+=chunk(b'IDAT',payload)
  else:b+=chunk(b'fdAT',struct.pack('>I',seq)+payload);seq+=1
 b+=chunk(b'IEND',b'');p.write_bytes(b)
 durations=[struct.unpack('>IIIIIHHBB',d)[5:7] for t,d in chunks(p) if t==b'fcTL'];assert durations==[(9,160)]*8
 with Image.open(p) as im:
  assert im.n_frames==8
  for i,f in enumerate(frames):im.seek(i);assert np.array_equal(np.array(im.convert('RGBA')),np.array(f.convert('RGBA')))
def get(actor,view,mode):
 base=R/'inputs'/actor if mode in ('source','held-contact-pass-control') else R/mode/actor
 atlas=Image.open(base/'atlas.png').convert('RGBA');m=json.loads((base/'animations.json').read_text());ids=m['animations'][view+'_walk']['frames'];ids=[ids[x] for x in (0,0,0,3,4,4,4,7)] if mode=='held-contact-pass-control' else ids
 return [atlas.crop(((i%8)*128,(i//8)*128,(i%8+1)*128,(i//8+1)*128)) for i in ids],ids

def main():
 out=R/'previews';out.mkdir(exist_ok=True);(out/'mp4-frames').mkdir(exist_ok=True);receipts=[]
 for actor in ('lyra','brann'):
  for view in ('south','north'):
   allsets={mode:get(actor,view,mode) for mode in MODES}
   full=Image.new('RGBA',(9*140,4*240),COLORS);d=ImageDraw.Draw(full)
   legs=Image.new('RGBA',(9*100,4*110),COLORS);dl=ImageDraw.Draw(legs)
   native=Image.new('RGBA',(9*128,4*148),COLORS);dn=ImageDraw.Draw(native)
   pair=Image.new('RGBA',(8*180,4*110),COLORS);dp=ImageDraw.Draw(pair)
   for row,mode in enumerate(MODES):
    frames,ids=allsets[mode]
    for pidx in range(9):
     phase=pidx%8;frame=frames[phase];col=pidx*140;y=row*240
     full.alpha_composite(frame.crop((32,16,96,121)).resize((128,210),Image.Resampling.NEAREST),(col,y+25));d.text((col+2,y+5),f'{mode[:7]} p{phase} cel{ids[phase]}',fill='white')
     legs.alpha_composite(frame.crop((43,82,86,121)).resize((86,78),Image.Resampling.NEAREST),(pidx*100,row*110+25));dl.text((pidx*100,row*110+5),f'{mode[:7]} p{phase}',fill='white')
     native.alpha_composite(frame,(pidx*128,row*148+20));dn.text((pidx*128,row*148),f'{mode[:7]} p{phase}',fill='white')
    # Every adjacent pair, including 7->0, at exact 2x.
    for phase in range(8):
     for side,pidx in enumerate((phase,(phase+1)%8)):
      pair.alpha_composite(frames[pidx].crop((43,82,86,121)).resize((86,78),Image.Resampling.NEAREST),(phase*180+side*88,row*110+25))
     dp.text((phase*180,row*110+5),f'{mode[:7]} {phase}->{(phase+1)%8}',fill='white')
    # Individual alpha-preserving native APNG, no millisecond quantization.
    apng(frames,out/f'{actor}-{view}-{mode}-native.apng')
   full.convert('RGB').save(out/f'{actor}-{view}-gaits-2x-wrap.png');legs.convert('RGB').save(out/f'{actor}-{view}-thigh-ankle-2x-wrap.png');native.convert('RGB').save(out/f'{actor}-{view}-gaits-native-wrap.png');native.resize((native.width*2,native.height*2),Image.Resampling.NEAREST).convert('RGB').save(out/f'{actor}-{view}-fullstage-2x-wrap.png');pair.convert('RGB').save(out/f'{actor}-{view}-adjacent-contact-pairs-2x.png')
   comps=[]
   for phase in range(8):
    f=Image.new('RGBA',(4*256,288),COLORS);draw=ImageDraw.Draw(f)
    for col,mode in enumerate(MODES):
     f.alpha_composite(allsets[mode][0][phase].resize((256,256),Image.Resampling.NEAREST),(col*256,24));draw.text((col*256+8,6),f'{mode}  p{phase}',fill='white')
    comps.append(f)
   apng(comps,out/f'{actor}-{view}-comparison-2x.apng')
   fd=out/'mp4-frames'/f'{actor}-{view}';fd.mkdir(exist_ok=True)
   for i,f in enumerate(comps):f.convert('RGB').save(fd/f'{i:02d}.png')
   cmd=['ffmpeg','-v','error','-y','-framerate','160/9','-i',str(fd/'%02d.png'),'-vf','fps=160:round=near','-frames:v','72','-c:v','libx264','-crf','0','-preset','fast','-pix_fmt','yuv444p','-video_track_timescale','160',str(out/f'{actor}-{view}-comparison-exact-450ms.mp4')]
   subprocess.run(cmd,check=True)
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_frames','-of','json',str(out/f'{actor}-{view}-comparison-exact-450ms.mp4')]))
   assert probe['streams'][0]['nb_frames']=='72';assert probe['streams'][0]['duration']=='0.450000'
   receipts.append({'actor':actor,'view':view,'apng_delay':[9,160],'apng_frames':8,'loop_seconds':'9/20','mp4_frames':72,'mp4_rate':160,'mp4_duration':probe['streams'][0]['duration'],'control':'source frames 0,0,0,3,4,4,4,7 at the same eight exact holds; original phase bodies retained in actual source/candidates','mp4_note':'lossless H264 RGB conversion to YUV444; APNG is the exact RGBA authority'})
 (out/'CLOCK-VALIDATION.json').write_text(json.dumps(receipts,indent=2)+'\n')
 print('wrote full gait/wrap, adjacent pairs, thighs/ankles, exact APNG and MP4 for four walk clips')
if __name__=='__main__':main()
