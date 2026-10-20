from pathlib import Path
import json,struct,zlib,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BG={'light':(230,228,217,255),'dark':(27,30,39,255),'ground':(94,96,63,255)}
control=[Image.open(ROOT/'inputs'/'control'/f'{i:02}.png').convert('RGBA')for i in range(8)]
frames=[Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA')for i in range(8)]
def composite(im,s,c):
    b=Image.new('RGBA',(s,s),c);b.alpha_composite(im.resize((s,s),Image.Resampling.NEAREST));return b
for name,s in [('native',128),('066',84),('2x',256)]:
    compare=Image.new('RGBA',(9*s,2*(s+18)),BG['light']);d=ImageDraw.Draw(compare)
    chrono=Image.new('RGBA',(9*s,3*(s+18)));cd=ImageDraw.Draw(chrono)
    pairs=Image.new('RGBA',(8*(2*s+8),3*(s+18)));pd=ImageDraw.Draw(pairs)
    for row,ims in enumerate([control,frames]):
        for col,im in enumerate(ims+[ims[0]]):
            compare.paste(composite(im,s,BG['light']),(col*s,row*(s+18)+18));d.text((col*s+2,row*(s+18)+1),f'{"control"if row==0 else"swing"} {col%8:02}',fill='black')
    for row,(label,color) in enumerate(BG.items()):
        y=row*(s+18);cd.rectangle((0,y,chrono.width,y+18),fill='white');pd.rectangle((0,y,pairs.width,y+18),fill='white')
        for col,im in enumerate(frames+[frames[0]]):chrono.paste(composite(im,s,color),(col*s,y+18));cd.text((col*s+2,y+1),f'{col%8:02} {label}',fill='black')
        for i in range(8):
            x=i*(2*s+8);pairs.paste(composite(frames[i],s,color),(x,y+18));pairs.paste(composite(frames[(i+1)%8],s,color),(x+s,y+18));pd.text((x+2,y+1),f'{i:02}>{(i+1)%8:02} {label}',fill='black')
    compare.save(ROOT/'proof'/f'before-after-{name}.png');chrono.save(ROOT/'proof'/f'chronology-{name}.png');pairs.save(ROOT/'proof'/f'every-pair-{name}.png')
sh=Image.new('RGBA',(75*5,38*2),BG['light'])
for row,ims in enumerate([control,frames]):
    for j,i in enumerate([2,3,4,5,6]):sh.alpha_composite(ims[i].crop((28,53,103,91)),(75*j,38*row))
sh.resize((1500,304),Image.Resampling.NEAREST).save(ROOT/'proof'/'joints-before-after-4x.png')
# Literal eight-pixel join correction: reconstruct the prior body without
# those explicit witnesses, retaining the same final arm/fixed layers.
import numpy as np
underpaint=json.loads((ROOT/'UNDERPAINT.json').read_text());closed=json.loads((ROOT/'inputs'/'closed-slit-source-witnesses.json').read_text())
joins=Image.new('RGBA',(144,64),BG['light'])
for col,i in enumerate([3,7]):
    a=np.array(control[i]);fixed=np.array(Image.open(ROOT/'masks'/f'{i:02}-fixed-head-pauldron.png'))>0;old=np.array(Image.open(ROOT/'masks'/f'{i:02}-old-visible-arm.png'))>0
    a[fixed|old]=0
    for w in underpaint[i]['literal_body_underpaint_before_arms']:
        x,y=w['destination'];a[y,x]=w['rgba']
    for w in closed[i]['literal_source_witnesses']:
        x,y=w['destination']
        if not fixed[y,x]:a[y,x]=np.array(control[i])[y,x]
    prior=Image.fromarray(a)
    for layer in ['far','near','fixed']:prior.alpha_composite(Image.open(ROOT/'layers'/f'{i:02}-{layer}.png').convert('RGBA'))
    for row,im in enumerate([prior,frames[i]]):joins.alpha_composite(im.crop((26,58,98,90)),(72*col,32*row))
joins.resize((1728,768),Image.Resampling.NEAREST).save(ROOT/'proof'/'joins-literal-shadow-12x.png')
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
apng([ROOT/'frames'/f'{i:02}.png'for i in range(8)],ROOT/'counter-swing.apng')
apng([ROOT/'inputs'/'control'/f'{i:02}.png'for i in range(8)],ROOT/'closed-slit-control.apng')
holds=[];im=Image.open(ROOT/'counter-swing.apng')
for i in range(8):im.seek(i);holds.append(im.info['duration']);assert im.convert('RGBA').tobytes()==frames[i].tobytes()
assert holds==[56.25]*8
proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgba','-video_size','256x128','-framerate','160','-i','pipe:0','-c:v','libx264','-pix_fmt','yuv420p',str(ROOT/'control-vs-swing-4loops.mp4')],stdin=subprocess.PIPE)
for tick in range(288):
    i=(tick//9)%8;sh=Image.new('RGBA',(256,128),BG['ground']);sh.paste(composite(control[i],128,BG['ground']),(0,0));sh.paste(composite(frames[i],128,BG['ground']),(128,0));proc.stdin.write(sh.tobytes())
proc.stdin.close();assert proc.wait()==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=r_frame_rate,nb_frames,duration','-of','json',str(ROOT/'control-vs-swing-4loops.mp4')]))
assert probe['streams'][0]['nb_frames']=='288'and probe['streams'][0]['duration']=='1.800000'
(ROOT/'MEDIA-RECEIPT.json').write_text(json.dumps({'APNG_RGBA_exact':True,'APNG_holds_ms':holds,'mp4':probe,'mp4_lossy_preview':True,'control_and_experiment_clock_equal':True,'human_continuous_playback_and_engine_planting_unverified':True},indent=2)+'\n')
print('Full eight-key and cyclic-pair native/.66/2x sheets, exact-clock APNGs and equal-clock comparison MP4.')
