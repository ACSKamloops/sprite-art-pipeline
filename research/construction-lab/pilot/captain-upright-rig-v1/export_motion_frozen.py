#!/usr/bin/env python3
"""Export fixed-origin, hash-bound motion auditions; never rate or alter art."""
import argparse, bisect, hashlib, html, json, math, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or int(value) != value or value < minimum:
        raise ValueError(f'{name}: expected integral finite >= {minimum}')
    return int(value)
def point(value, name):
    if not isinstance(value,list) or len(value)!=2 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in value):
        raise ValueError(f'{name}: expected finite XY')
    return value

def round_away(x): return math.floor(x+.5) if x>=0 else math.ceil(x-.5)


class Motion:
    def __init__(self, spec_path):
        self.path=Path(spec_path).resolve(); self.spec=json.loads(self.path.read_text())
        s=self.spec
        if s.get('schema')!='motion-audition/v1': raise ValueError('Wrong schema')
        self.canvas=[integer(x,'canvas',1) for x in point(s['canvas'],'canvas')]
        self.stage=[integer(x,'stage',1) for x in point(s['stage'],'stage')]
        self.origin=point(s['origin'],'origin'); self.stride=point(s.get('root_stride',[0,0]),'root_stride')
        self.policy=s.get('root_policy','in_place')
        if self.policy not in ['in_place','physical','shared_episode_target']: raise ValueError('Unknown root policy')
        self.camera=s.get('camera','fixed')
        if self.camera not in ['fixed','follow_physical']: raise ValueError('Unknown camera policy')
        self.frames=[];self.boundaries=[0];self.images=[]
        for i,f in enumerate(s['frames']):
            if integer(f['index'],'index')!=i: raise ValueError('Unordered frame')
            duration=integer(f['duration_ms'],'duration_ms',1)
            if not isinstance(f.get('phase_label'),str) or not f['phase_label']: raise ValueError('Every pose needs authored phase_label')
            path=(self.path.parent/f['file']).resolve()
            if not path.is_relative_to(self.path.parent): raise ValueError('Source image escapes input folder')
            if sha(path)!=f['sha256']: raise ValueError(f'Source PNG SHA mismatch: {i}')
            image=Image.open(path).convert('RGBA')
            if list(image.size)!=self.canvas: raise ValueError('Mixed/fitted canvas unsupported')
            point(f.get('physical_root',[0,0]),'physical_root')
            if self.policy=='shared_episode_target':
                for side in f.get('support_order',['right','left']):
                    support=f.get('supports',{}).get(side)
                    if support is not None:
                        point(support['world_target'],'world_target');point(support['material_sole'],'material_sole')
            self.frames.append(f);self.images.append(image);self.boundaries.append(self.boundaries[-1]+duration)
        if not self.frames: raise ValueError('No frames')
        self.cycle=self.boundaries[-1]
        if integer(s['cycle_ms'],'cycle_ms',1)!=self.cycle: raise ValueError('Hold sum mismatch')

    def state(self, elapsed_ms):
        cycle,local=divmod(elapsed_ms,self.cycle)
        i=bisect.bisect_right(self.boundaries,local)-1
        fraction=(local-self.boundaries[i])/self.frames[i]['duration_ms']
        a=self.frames[i].get('physical_root',[0,0]);b=self.frames[i+1].get('physical_root',[0,0]) if i+1<len(self.frames) else self.stride
        physical=[a[k]+(b[k]-a[k])*fraction+self.stride[k]*cycle for k in range(2)]
        if self.policy=='in_place': physical=[0,0]
        draw_root=physical[:];support_side=None
        if self.policy=='shared_episode_target':
            f=self.frames[i]
            for side in f.get('support_order',['right','left']):
                support=f.get('supports',{}).get(side)
                if support is not None:
                    draw_root=[support['world_target'][k]-support['material_sole'][k]+self.stride[k]*cycle for k in range(2)]
                    support_side=side;break
        camera=physical[:] if self.camera=='follow_physical' else [0,0]
        return {'frame':i,'cycle':cycle,'progress':fraction,'physical_root':physical,'draw_root':draw_root,'camera':camera,'selected_support':support_side}

    def render(self, elapsed_ms, zoom=1, silhouette=False):
        state=self.state(elapsed_ms);s=self.spec
        image=Image.new('RGBA',self.stage,tuple(s.get('background',[43,50,56,255])))
        draw=ImageDraw.Draw(image)
        spacing=integer(s.get('grid_spacing',16),'grid_spacing',1)
        grid=tuple(s.get('grid_color',[62,71,77,255]))
        shift=[self.origin[k]-state['camera'][k]*zoom for k in range(2)]
        # Same fixed-world grid and physical camera as the frame consumer.
        for x in range(math.floor(-shift[0]/(spacing*zoom)),math.ceil((self.stage[0]-shift[0])/(spacing*zoom))+1):
            px=round_away(shift[0]+x*spacing*zoom);draw.line((px,70,px,self.stage[1]),fill=grid)
        for y in range(math.floor((70-shift[1])/(spacing*zoom)),math.ceil((self.stage[1]-shift[1])/(spacing*zoom))+1):
            py=round_away(shift[1]+y*spacing*zoom);draw.line((0,py,self.stage[0],py),fill=grid)
        source=self.images[state['frame']]
        if silhouette:
            source=Image.new('RGBA',source.size,(232,236,240,0));source.putalpha(self.images[state['frame']].getchannel('A'))
        source=source.resize((source.width*zoom,source.height*zoom),Image.Resampling.NEAREST)
        origin=[round_away(self.origin[k]+(state['draw_root'][k]-state['camera'][k])*zoom) for k in range(2)]
        bbox=source.getbbox()
        clipped=bool(bbox and (origin[0]+bbox[0]<0 or origin[1]+bbox[1]<0 or origin[0]+bbox[2]>image.width or origin[1]+bbox[3]>image.height))
        image.alpha_composite(source,tuple(origin))
        draw=ImageDraw.Draw(image)
        draw.text((10,8),f"{s.get('name','UNRATED')} | {state['frame']:02d} {self.frames[state['frame']]['phase_label']} | {elapsed_ms:g}ms | {zoom}x",fill='white')
        draw.text((10,26),f"{self.policy} / camera:{self.camera} | silhouette:{silhouette} | source pose held, one actor translation",fill='white')
        return image.convert('RGB'),{**state,'draw_origin':origin,'clipped':clipped}


def schedule(motion, loops, slowdown, sampling_ms):
    end=motion.cycle*loops*slowdown
    boundaries={i*motion.cycle*slowdown+t*slowdown for i in range(loops) for t in motion.boundaries}
    times=sorted(boundaries|set(range(0,end,sampling_ms))|{end})
    return times


def export_variant(motion,out,zoom,slowdown,silhouette,loops,sampling_ms):
    name=f"{'silhouette' if silhouette else 'rgba'}-{zoom}x-{'normal' if slowdown==1 else 'half-speed'}"
    times=schedule(motion,loops,slowdown,sampling_ms);rows=[]
    with tempfile.TemporaryDirectory(prefix='motion-audition-') as temp:
        temp=Path(temp);lines=['ffconcat version 1.0']
        for n,t in enumerate(times):
            image,state=motion.render(t/slowdown,zoom,silhouette)
            path=temp/f'{n:06d}.png';image.save(path)
            lines.extend([f"file '{path}'",'option framerate 1000'])
            if n+1<len(times):lines.append(f'duration {(times[n+1]-t)/1000:.3f}')
            rows.append({'output_ms':t,'source_elapsed_ms':t/slowdown,**state})
        listing=temp/'frames.ffconcat';listing.write_text('\n'.join(lines)+'\n')
        target=out/f'{name}.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-safe','0','-f','concat','-i',str(listing),'-fps_mode','vfr','-c:v','libx264','-preset','fast','-crf','0','-pix_fmt','yuv444p','-video_track_timescale','1000','-enc_time_base','1:1000',str(target)],check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(target)]))
        observed=[round(float(f['best_effort_timestamp_time'])*1000)for f in probe['frames']]
        if observed!=times: raise AssertionError(f'Encoded timestamps differ: {name}')
        # Actual decode of first output verifies generated canvas survives lossless RGB→YUV conversion within1LSB.
        decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(target),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
        expected=motion.render(0,zoom,silhouette)[0].tobytes()
        error=max(abs(a-b)for a,b in zip(decoded,expected));assert len(decoded)==len(expected) and error<=2
        return {'file':target.name,'sha256':sha(target),'zoom':zoom,'slowdown':slowdown,'silhouette':silhouette,'loop_count':loops,'exact_duration_ms':times[-1],'last_endpoint_packet_ms':1,'encoded_timestamps_exact':True,'decoded_first_max_RGB_error':error,'clipped_sample_count':sum(x['clipped']for x in rows),'observations':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--loops',type=int,default=3);p.add_argument('--sampling-ms',type=int,default=17);a=p.parse_args()
    if a.output.exists(): raise FileExistsError('Preserve previous outputs')
    if not 1<=a.loops<=5 or not 1<=a.sampling_ms<=100:raise ValueError('Bound loops1..5 / sample1..100ms')
    motion=Motion(a.spec);a.output.mkdir(parents=True)
    (a.output/'source-frames').mkdir()
    for i,f in enumerate(motion.frames):
        target=a.output/'source-frames'/f'{i:02d}.png';shutil.copyfile(motion.path.parent/f['file'],target)
        assert sha(target)==f['sha256']
    variants=[export_variant(motion,a.output,zoom,slow,mask,a.loops,a.sampling_ms)for zoom in [1,2]for slow in [1,2]for mask in [False,True]]
    # SourceRGBA key sheets: no per-frame recentering, silhouettes are separate.
    columns=min(4,len(motion.frames));cell=motion.canvas;sheet=Image.new('RGBA',(columns*cell[0],math.ceil(len(motion.frames)/columns)*(cell[1]+24)),(43,50,56,255));d=ImageDraw.Draw(sheet)
    for i,im in enumerate(motion.images):
        x=(i%columns)*cell[0];y=(i//columns)*(cell[1]+24);sheet.alpha_composite(im,(x,y));d.text((x+4,y+cell[1]+3),f"{i}: {motion.frames[i]['phase_label']} {motion.frames[i]['duration_ms']}ms",fill='white')
    sheet.save(a.output/'source-keys.png')
    summary={'schema':'motion-audition-export/v1','spec_sha256':sha(a.spec),'source_sha256':[f['sha256']for f in motion.frames],'code_sha256':sha(__file__),'root_policy':motion.policy,'camera':motion.camera,'cycle_ms':motion.cycle,'source_holds_ms':[f['duration_ms']for f in motion.frames],'variants':variants,'art_verdict':'NOT_REVIEWED','limits':['VFR video contains a1ms endpoint packet; exact source-loop interval ends at declared duration','Lossless YUV444 video RGB conversion may differ by≤2LSB; PNG keys retain exact sourceRGBA','Shared support metadata is declared input, not a new anatomical/material proof','Fixed canvas/origin, no per-pose fitting; all clipped samples reported','No inherited art approval or requested score']}
    (a.output/'report.json').write_text(json.dumps(summary,indent=2)+'\n')
    options=''.join(f'<option value="{html.escape(v["file"])}">{html.escape(v["file"])}</option>'for v in variants)
    page=f"""<!doctype html><meta charset=utf-8><title>Unrated full-cycle motion audition</title>
<style>body{{background:#20272d;color:#eee;font:16px sans-serif;margin:18px}}video{{display:block;image-rendering:pixelated;margin-top:12px}}button,select{{padding:8px}}img{{image-rendering:pixelated}}p{{max-width:950px}}</style>
<h1>Unrated motion audition</h1><p>{html.escape(motion.spec.get('name','Unnamed'))}. One fixed origin, declared integer holds. Art verdict pending. No inherited approval. Source cycle{motion.cycle}ms; {html.escape(motion.policy)} / {html.escape(motion.camera)}. Encoded endpoint packet extends the last loop by1ms; full source loops end at declared interval.</p>
<select id=variant>{options}</select> <button id=restart>Restart</button><span id=clock></span>
<video id=player controls loop playsinline width={motion.stage[0]} height={motion.stage[1]} src={variants[0]['file']}></video>
<h2>Readable native keys (separate from motion judgment)</h2><img src=source-keys.png><p><a href=report.json>Hash-bound export/time/policy report</a>; exact original PNGs in source-frames/.</p>
<script>const v=document.querySelector('#player');document.querySelector('#variant').onchange=e=>{{v.src=e.target.value;v.load()}};document.querySelector('#restart').onclick=()=>{{v.currentTime=0;v.play()}};setInterval(()=>document.querySelector('#clock').textContent=` ${{v.currentTime.toFixed(3)}}s / ${{v.duration.toFixed(3)}}s`,100);window.MotionAudition={{state:()=>({{source:v.currentSrc,seconds:v.currentTime,paused:v.paused,duration:v.duration}})}};</script>"""
    (a.output/'index.html').write_text(page)
    print(json.dumps({'output':str(a.output),'variants':len(variants),'clipped_samples':sum(x['clipped_sample_count']for x in variants)}))

if __name__=='__main__':main()
