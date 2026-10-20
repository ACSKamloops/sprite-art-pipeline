#!/usr/bin/env python3
"""Write source/candidate dodge triptychs and exact rational-clock proofs."""
from pathlib import Path
import json,struct,zlib,subprocess
from fractions import Fraction
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
HOLDS=[Fraction(9,200),Fraction(21,200),Fraction(11,200),Fraction(11,400),Fraction(11,400)]
BG=(35,39,47,255)
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
def apng(frames,path,plays=1):
 w,h=frames[0].size;b=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'acTL',struct.pack('>II',len(frames),plays));seq=0
 for i,(im,hold) in enumerate(zip(frames,HOLDS)):
  b+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,h,0,0,hold.numerator,hold.denominator,0,0));seq+=1
  arr=np.array(im.convert('RGBA'));data=zlib.compress(b''.join(b'\0'+row.tobytes() for row in arr),9)
  if i==0:b+=chunk(b'IDAT',data)
  else:b+=chunk(b'fdAT',struct.pack('>I',seq)+data);seq+=1
 b+=chunk(b'IEND',b'');path.write_bytes(b)
 with Image.open(path) as im:
  assert im.n_frames==5
  for i,f in enumerate(frames):im.seek(i);assert np.array_equal(np.array(im.convert('RGBA')),np.array(f.convert('RGBA')))
def getcell(atlas,i):return Image.fromarray(atlas[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128])
def main():
 p=R/'previews';p.mkdir(exist_ok=True);atlas=np.array(Image.open(R/'inputs'/'atlas.png'));manifest=json.loads((R/'inputs'/'animations.json').read_text());jobs=json.loads((R/'frozen-plan.json').read_text())['jobs'];metrics=[]
 neck=Image.new('RGBA',(4*330,4*150),BG);dn=ImageDraw.Draw(neck)
 for row,job in enumerate(jobs):
  view=job['view'];ids=manifest['animations'][view+'_dodge']['frames'];assert len(ids)==5 and ids[3]==job['source_frame'];assert manifest['animations'][view+'_dodge']['holds']==[float(x) for x in HOLDS]
  aa=[getcell(atlas,i) for i in ids];bb=aa.copy();bb[3]=Image.open(R/'candidates'/f'{view}.png').convert('RGBA')
  trip=Image.new('RGBA',(3*128,2*150),BG);dt=ImageDraw.Draw(trip)
  heads=Image.new('RGBA',(3*170,2*160),BG);dh=ImageDraw.Draw(heads)
  for rr,frames in enumerate((aa,bb)):
   for col,phase in enumerate((2,3,4)):
    im=frames[phase];label=f'{"A" if rr==0 else "B"}: '+(f'recovery f{ids[phase]}' if col==0 else ('source settle' if rr==0 and col==1 else 'shifted head' if col==1 else f'neutral f{ids[phase]}'))
    trip.alpha_composite(im,(col*128,rr*150+20));dt.text((col*128+3,rr*150+3),label,fill='white')
    heads.alpha_composite(im.crop((22,8,105,75)).resize((166,134),Image.Resampling.NEAREST),(col*170,rr*160+23));dh.text((col*170+3,rr*160+3),label,fill='white')
  trip.convert('RGB').save(p/f'{view}-triptych-native.png');trip.resize((trip.width*2,trip.height*2),Image.Resampling.NEAREST).convert('RGB').save(p/f'{view}-triptych-2x.png');heads.convert('RGB').save(p/f'{view}-head-triptych-2x.png')
  source=np.array(aa[3]);candidate=np.array(bb[3]);changed=np.any(source!=candidate,axis=2);old=np.array(Image.open(R/'replay-verified'/'witnesses'/view/'old-head-owner.png'))>0;new=np.array(Image.open(R/'replay-verified'/'witnesses'/view/'shifted-nonzero-foreground.png'))>0
  diff=candidate.copy();diff[changed]=[255,65,85,255];over=candidate.copy();bodytouch=(~old)&(source[:,:,3]>0)&changed;over[bodytouch]=[255,165,30,255]
  for col,arr in enumerate((source,candidate,diff,over)):
   crop=Image.fromarray(arr).crop((25,42,105,68)).resize((320,104),Image.Resampling.NEAREST);neck.alpha_composite(crop,(col*330,row*150+30));dn.text((col*330,row*150+5),f'{view}: '+('old neck','candidate neck','actual changes','covered body')[col],fill='white')
  apng(aa,p/f'{view}-A-source-native.apng');apng(bb,p/f'{view}-B-head-candidate-native.apng')
  compare=[]
  for phase in range(5):
   im=Image.new('RGBA',(512,288),BG);draw=ImageDraw.Draw(im)
   for col,frames in enumerate((aa,bb)):
    im.alpha_composite(frames[phase].resize((256,256),Image.Resampling.NEAREST),(col*256,26));draw.text((col*256+8,5),f'{view} {"A source" if col==0 else "B lower head"} slot {phase}',fill='white')
   compare.append(im)
  apng(compare,p/f'{view}-AB-dodge-2x-once.apng');apng(compare,p/f'{view}-AB-dodge-2x-repeat.apng',0)
  mp=p/f'{view}-AB-dodge-exact-260ms.mp4';counts=[int(x*400) for x in HOLDS];assert counts==[18,42,22,11,11]
  raw=b''.join(np.array(f).tobytes()*count for f,count in zip(compare,counts))
  subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-video_size','512x288','-framerate','400','-i','pipe:0','-frames:v','104','-c:v','libx264','-crf','0','-preset','fast','-pix_fmt','yuv444p','-video_track_timescale','400',str(mp)],input=raw,check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(mp)]));stream=probe['streams'][0];assert stream['nb_frames']=='104' and stream['duration']=='0.260000'
  tops={}
  for name,frames in (('A',aa),('B',bb)):
   tops[name]={}
   for threshold in (1,128,255):
    tops[name][f'alpha_ge_{threshold}']=[int(np.where(np.array(frames[i])[:65,:,3]>=threshold)[0].min()) for i in (2,3,4)]
  metrics.append({'view':view,'source_frames':ids,'replacement_slot':3,'holds_rational':[[f.numerator,f.denominator] for f in HOLDS],'loop':False,'total_seconds_rational':[13,50],'mp4_fps':400,'mp4_repeated_frames_per_slot':counts,'mp4_duration_seconds':stream['duration'],'head_top_recovery_settle_neutral':tops,'repeat_preview_note':'repeat APNG is labeled review convenience; manifest dodge remains nonlooping'})
 neck.convert('RGB').save(p/'all-views-neck-joins-4x.png');(p/'CLOCK-AND-HEAD-TOPS.json').write_text(json.dumps(metrics,indent=2)+'\n');print('four views: native/2x triptychs, head detail, neck joins, exact APNG and 260ms MP4')
if __name__=='__main__':main()
