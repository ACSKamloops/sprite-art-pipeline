from pathlib import Path
import json,struct,zlib,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BACKGROUNDS={'light':(230,228,217,255),'dark':(27,30,39,255),'ground':(94,96,63,255)}
def bgimage(im,size,color):
    b=Image.new('RGBA',(size,size),color);b.alpha_composite(im.resize((size,size),Image.Resampling.NEAREST));return b
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
def chunks(data):
    p=8
    while p<len(data):
        n=struct.unpack('>I',data[p:p+4])[0];yield data[p+4:p+8],data[p+8:p+8+n];p+=12+n
def apng(files,out):
    parts=[list(chunks(p.read_bytes()))for p in files];ihdr=next(d for k,d in parts[0]if k==b'IHDR');seq=0
    w,h=struct.unpack('>II',ihdr[:8]);data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ihdr)+chunk(b'acTL',struct.pack('>II',len(files),0))
    for i,cs in enumerate(parts):
        data+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,w,h,0,0,9,160,0,0));seq+=1
        for k,d in cs:
            if k!=b'IDAT':continue
            if i==0:data+=chunk(k,d)
            else:data+=chunk(b'fdAT',struct.pack('>I',seq)+d);seq+=1
    out.write_bytes(data+chunk(b'IEND',b''))
receipt={}
for v in ['se','ne']:
    files=[ROOT/v/f'{i:02}.png'for i in range(8)];ims=[Image.open(p).convert('RGBA')for p in files]
    for scale,s in [('native',128),('066',84),('2x',256)]:
        # Every chronological key, repeated00 and each cyclic adjacent pair.
        sheet=Image.new('RGBA',(9*s,3*(s+18)));d=ImageDraw.Draw(sheet)
        pairs=Image.new('RGBA',(8*(2*s+8),3*(s+18)));pd=ImageDraw.Draw(pairs)
        for row,(name,color) in enumerate(BACKGROUNDS.items()):
            y=row*(s+18);d.rectangle((0,y,sheet.width,y+18),fill='white');pd.rectangle((0,y,pairs.width,y+18),fill='white')
            for i,im in enumerate(ims+[ims[0]]):
                sheet.paste(bgimage(im,s,color),(i*s,y+18));d.text((i*s+2,y+1),f'{v} {i%8:02} {name}',fill='black')
            for i in range(8):
                x=i*(2*s+8);pairs.paste(bgimage(ims[i],s,color),(x,y+18));pairs.paste(bgimage(ims[(i+1)%8],s,color),(x+s,y+18));pd.text((x+2,y+1),f'{i:02}>{(i+1)%8:02} {name}',fill='black')
        sheet.save(ROOT/'proof'/f'{v}-chronology-{scale}.png');pairs.save(ROOT/'proof'/f'{v}-every-pair-{scale}.png')
        # Full before/after on light, preserving stage registration.
        before=Image.new('RGBA',(8*s,2*(s+18)),BACKGROUNDS['light']);bd=ImageDraw.Draw(before)
        for i in range(8):
            for row,im in enumerate([Image.open(ROOT/'inputs'/v/f'{i:02}.png').convert('RGBA'),ims[i]]):
                before.paste(bgimage(im,s,BACKGROUNDS['light']),(i*s,row*(s+18)+18));bd.text((i*s+2,row*(s+18)+1),f'{"prior"if row==0 else"review"} {i:02}',fill='black')
        before.save(ROOT/'proof'/f'{v}-before-after-{scale}.png')
    apng(files,ROOT/v/'walk.apng')
    decoded=Image.open(ROOT/v/'walk.apng');holds=[]
    assert decoded.n_frames==8
    for i in range(8):decoded.seek(i);assert decoded.convert('RGBA').tobytes()==ims[i].tobytes();holds.append(decoded.info['duration'])
    assert holds==[56.25]*8
    # Native pinned-stage four-loop preview, decoded clock checked separately.
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgba','-video_size','128x128','-framerate','160','-i','pipe:0','-c:v','libx264','-pix_fmt','yuv420p',str(ROOT/v/'walk-4loops.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for tick in range(288):proc.stdin.write(bgimage(ims[(tick//9)%8],128,BACKGROUNDS['ground']).tobytes())
    proc.stdin.close();assert proc.wait()==0
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=r_frame_rate,nb_frames,duration','-of','json',str(ROOT/v/'walk-4loops.mp4')]))
    assert probe['streams'][0]['nb_frames']=='288'and probe['streams'][0]['duration']=='1.800000'
    receipt[v]={'apng_holds_ms':holds,'apng_RGBA_exact':True,'mp4':probe,'mp4_lossy_preview':True,'world_planting_and_engine_runtime_tested':False}
# Waist raster before/after, only the four demonstrated affected phases.
sh=Image.new('RGBA',(4*72,2*64),BACKGROUNDS['light'])
for row in range(2):
 for col,i in enumerate([1,2,3,4]):
    p=ROOT/'inputs'/'se'/f'{i:02}.png'if row==0 else ROOT/'se'/f'{i:02}.png'
    sh.alpha_composite(Image.open(p).crop((40,57,112,121)),(col*72,row*64))
sh.resize((1152,512),Image.Resampling.NEAREST).save(ROOT/'proof'/'se-waist-before-after-4x.png')
(ROOT/'MEDIA-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('All keys and cyclic pairs at native/.66/2x; exact APNG holds; four-loop MP4 previews.')
