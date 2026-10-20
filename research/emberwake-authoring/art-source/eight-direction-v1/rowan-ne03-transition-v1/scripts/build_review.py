from pathlib import Path
import argparse, binascii, hashlib, json, struct, subprocess, zlib
from PIL import Image, ImageDraw

P=Path(__file__).resolve().parents[1]

def chunk(tag,body):
    return struct.pack('>I',len(body))+tag+body+struct.pack('>I',binascii.crc32(tag+body)&0xffffffff)

def apng(path,frames):
    width,height=frames[0].size
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'acTL',struct.pack('>II',len(frames),0))
    seq=0
    for i,im in enumerate(frames):
        data+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,width,height,0,0,9,160,0,0));seq+=1
        raw=im.tobytes();row=width*3
        packed=zlib.compress(b''.join(b'\0'+raw[y*row:(y+1)*row]for y in range(height)),9)
        if i==0:data+=chunk(b'IDAT',packed)
        else:data+=chunk(b'fdAT',struct.pack('>I',seq)+packed);seq+=1
    path.write_bytes(data+chunk(b'IEND',b''))

def main(out,video):
    assert out.is_absolute()and not out.exists();out.mkdir()
    originals=[Image.open(P/f'inputs/current/{i:02}.png').convert('RGBA')for i in range(8)]
    trial=list(originals);trial[3]=Image.open(P/'final/03.png').convert('RGBA')
    grounds={'light':(224,221,211),'dark':(24,28,32),'game':(52,62,48)}
    media=[]
    for name,g in grounds.items():
        ink='black'if name=='light'else'white'
        for size in [128,256,84]:
            sheet=Image.new('RGB',(size*8,size*2+48),g);d=ImageDraw.Draw(sheet)
            for row,bank in enumerate([originals,trial]):
                d.text((4,row*(size+24)+4),'CURRENT control'if row==0 else'ONE 03 TRANSITION; other seven exact',fill=ink)
                for i,im in enumerate(bank):
                    bg=Image.new('RGBA',(size,size),g+(255,));bg=Image.alpha_composite(bg,im.resize((size,size),Image.Resampling.NEAREST));sheet.paste(bg.convert('RGB'),(i*size,row*(size+24)+24))
            sheet.save(out/f'whole8-{size}-{name}.png')
        for size in [128,84]:
            frames=[]
            for i in range(8):
                frame=Image.new('RGB',(size*2+16,size+32),g);d=ImageDraw.Draw(frame)
                for col,im in enumerate([originals[i],trial[i]]):
                    bg=Image.new('RGBA',(size,size),g+(255,));bg=Image.alpha_composite(bg,im.resize((size,size),Image.Resampling.NEAREST));frame.paste(bg.convert('RGB'),(col*(size+16),24))
                    d.text((col*(size+16)+3,5),('CURRENT'if col==0 else'TEST')+f' {i:02}',fill=ink)
                frames.append(frame)
            fn=f'paired-whole8-{size}-{name}.apng';apng(out/fn,frames)
            check=Image.open(out/fn);assert check.n_frames==8
            for i,frame in enumerate(frames):
                check.seek(i);assert check.convert('RGB').tobytes()==frame.tobytes();assert abs(check.info['duration']-56.25)<1e-9
            media.append({'path':fn,'frames':8,'hold':[9,160],'cycle':[9,20],'RGB_frames_exact':True})
            if video and name=='game':
                seqdir=out/f'paired-{size}-video-frames';seqdir.mkdir()
                for i,im in enumerate(frames):im.save(seqdir/f'{i:02}.png')
                dest=out/f'paired-whole8-{size}-game.mp4'
                command=['ffmpeg','-v','error','-stream_loop','11','-framerate','160/9','-i',str(seqdir/'%02d.png'),'-an','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-r','160/9','-video_track_timescale','160','-movflags','+faststart',str(dest)]
                subprocess.run(command,check=True)
                probed=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration,time_base,r_frame_rate','-of','json',str(dest)]))
                st=probed['streams'][0];assert st['nb_frames']=='96'and st['r_frame_rate']=='160/9'and abs(float(st['duration'])-5.4)<1e-9
                media.append({'path':dest.name,'command':command,'ffprobe':probed,'limitation':'MP4 display derivative uses YUV420, not RGBA fidelity evidence;12 identical0.45s cycles. APNG is exact RGB/hold reference.'})
    (out/'MEDIA-RECEIPT.json').write_text(json.dumps({'scope':'Whole8 comparison; only03 replaced; no gameplay/root/contact test','media':media},indent=2)+'\n')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rowan NE03 transition</title><style>body{background:#343e30;color:#eee;font:16px sans-serif}img,video{image-rendering:pixelated}video{display:block;margin:1em 0}</style><h1>Rowan NE03 one transition test</h1><p>Current left, one03 replacement right. Eight unchanged9/160s holds, .45s loop. No score or selection.</p><img src="whole8-84-game.png"><video controls loop autoplay muted src="paired-whole8-128-game.mp4"></video><img src="paired-whole8-84-game.apng"><p>MP4 uses YUV420 display conversion; APNG retains exact RGB and rational timing.</p>')
    print('Review outputs',len(list(out.rglob('*'))))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--video',action='store_true');a=ap.parse_args();main(a.output,a.video)
