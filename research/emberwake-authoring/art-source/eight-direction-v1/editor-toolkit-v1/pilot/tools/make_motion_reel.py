#!/usr/bin/env python3
"""Assemble source-bound native sprite ticks into a local four-view video."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


def sha(raw):return hashlib.sha256(raw).hexdigest()


def make(pack, output, groups=None, scale=2):
    pack=pack.resolve(); output=output.resolve()
    if output.exists():raise ValueError('Preserve prior reels; output must be fresh')
    raw=(pack/'manifest.json').read_bytes(); manifest=json.loads(raw)
    for name,digest in manifest['source_bindings'].items():
        if sha((pack.parent/name).read_bytes())!=digest:raise ValueError('Stale reel source: '+name)
    if manifest['fps']!=60:raise ValueError('This reel uses the tested 60Hz clock')
    views=manifest['views']
    groups=groups or sorted({b.split('/')[0] for b in manifest['clips']})
    width=192*len(views)*scale; height=192*scale+48
    output.mkdir(parents=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{width}x{height}',
         '-framerate','60','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','15','-pix_fmt','yuv420p',str(output/'animation-reel.mp4')]
    rows=[];video_tick=0
    with (output/'ffmpeg.log').open('wb') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for group in groups:
                clips=[manifest['clips'][group+'/'+v] for v in views]
                count=clips[0]['duration_ticks']
                if any(c['duration_ticks']!=count or c['loop']!=clips[0]['loop'] for c in clips):raise ValueError('Direction clocks disagree')
                begin=video_tick
                for repeat in range(2 if clips[0]['loop'] else 1):
                    for tick in range(count):
                        canvas=Image.new('RGB',(width,height),(31,43,51));draw=ImageDraw.Draw(canvas)
                        draw.text((8,6),f'Copper Scout | {group} | native tick {tick}/{count-1} | 60Hz | {scale}x nearest',fill='white')
                        for i,(view,clip) in enumerate(zip(views,clips)):
                            frame=clip['frames'][tick]
                            if frame['tick']!=tick or frame['duration_ticks']!=1:raise ValueError('Unexpected ordering/hold')
                            path=(pack/frame['png']).resolve()
                            if not path.is_relative_to(pack):raise ValueError('Frame escapes pack')
                            image=Image.open(path).convert('RGBA')
                            if image.size!=(192,192) or sha(image.tobytes())!=frame['pixel_sha256']:raise ValueError('Changed sprite pixels')
                            image=image.resize((192*scale,192*scale),Image.Resampling.NEAREST)
                            canvas.paste(image,(192*scale*i,48),image)
                            draw.text((192*scale*i+8,27),view,fill='white')
                        proc.stdin.write(canvas.tobytes());video_tick+=1
                rows.append({'group':group,'video_start_tick':begin,'video_end_tick':video_tick-1,'source_ticks':count,
                             'loop_repeats':2 if clips[0]['loop'] else 1})
                # Explicit separator: this reel is a clip review, not a gameplay transition.
                separator=Image.new('RGB',(width,height),(31,43,51));ImageDraw.Draw(separator).text((12,16),'Next independent clip; no gameplay transition implied',fill='white')
                for _ in range(21):proc.stdin.write(separator.tobytes());video_tick+=1
        finally:
            proc.stdin.close();status=proc.wait()
        if status:raise ValueError('Video encoder failed; inspect ffmpeg.log')
    if (pack/'manifest.json').read_bytes()!=raw:raise ValueError('Bake changed during reel assembly')
    receipt={'schema':'sprite-motion-reel/v1','passed':True,'bake_manifest_sha256':sha(raw),'source_bindings':manifest['source_bindings'],
             'groups':rows,'fps':60,'video_ticks':video_tick,'seconds':video_tick/60,'nearest_scale':scale,
             'video_sha256':sha((output/'animation-reel.mp4').read_bytes()),
             'scope':'Verified actual baked body PNG ticks; fixed canvas, explicit clip separators, no interpolated frames. Body-only review, not gameplay effects or continuous video inspection by AI.'}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('pack',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--groups');p.add_argument('--scale',type=int,choices=[1,2,3],default=2)
    a=p.parse_args();r=make(a.pack,a.output,a.groups.split(',')if a.groups else None,a.scale)
    print(json.dumps({'passed':r['passed'],'groups':len(r['groups']),'seconds':r['seconds'],'video':str(a.output/'animation-reel.mp4')}))
