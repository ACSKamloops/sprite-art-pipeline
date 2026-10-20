#!/usr/bin/env python3
"""Replay frozen 60Hz RGBA bakes against their actual orthographic world grid.

No animation approval, contact feedback, frame fitting or material modification.
Two deliberately separate consumers: synchronized root/cel at60Hz, or120Hz
continuous physical root while each60Hz cel is held. Rational CFR timing is
preserved rather than rounding each16.666ms cel to an integer millisecond.
"""
import argparse, hashlib, json, math, subprocess
from fractions import Fraction
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rounded(x): return math.floor(x+.5) if x >= 0 else math.ceil(x-.5)


class Replay:
    def __init__(self, contract, joints):
        self.path=Path(contract).resolve(); self.contract=json.loads(self.path.read_text())
        self.joint_path=Path(joints).resolve(); self.joints=json.loads(self.joint_path.read_text())
        self.frames=self.contract['frames']; self.size=self.contract['canvas']
        if self.size not in ([256,256],[384,384]) or len(self.frames)!=65 or len(self.joints)!=131:
            raise ValueError('This adapter requires the declared65-pose60Hz /131-endpoint ledger')
        self.integrated = 'camera_fixed_matrix' not in self.contract
        if self.integrated:
            timeline=self.contract['timeline']
            if (timeline['start'],timeline['end_exclusive'],timeline['source_fps'],timeline['sample_step']) != (1,131,120,2):
                raise ValueError('Unexpected integrated source clock')
            if self.contract['root_policy'] != 'remove-captured-horizontal' or not self.contract['root_controller_baked']:
                raise ValueError('Integrated replay requires baked horizontal-only compensation')
            self.camera=np.array(self.contract['views']['threequarter'],dtype=float)
            ortho_scale=self.contract['camera_fixed_scale']
        else:
            self.camera=np.array(self.contract['camera_fixed_matrix'],dtype=float)
            ortho_scale=self.contract['ortho_scale']
        rotation=self.camera[:3,:3]
        if self.camera.shape!=(4,4) or not np.allclose(rotation.T@rotation,np.eye(3),atol=2e-6) or not math.isclose(np.linalg.det(rotation),1,abs_tol=2e-6):
            raise ValueError('Camera must be a proper orthonormal world matrix')
        self.scale=self.size[0]/float(ortho_scale); self.images=[]; self.roots=[]
        # Fixed presentation presets across the entire three-loop export. The
        # old1024 stage clipped native384 art at2x; no per-pose fitting is used.
        self.stage=(1536,1536) if self.size[0]==384 else (1024,1024)
        self.origin=np.array([640.,80.]) if self.size[0]==384 else np.array([416.,80.])
        first=np.array(self.joints[0]['root'],dtype=float)
        for i,f in enumerate(self.frames):
            frame_key='source_frame' if self.integrated else 'source_blender_frame'
            duration_key='hold_seconds' if self.integrated else 'duration_seconds'
            if f['index']!=i or f[frame_key]!=1+2*i or not math.isclose(f[duration_key],1/60,abs_tol=1e-12):
                raise ValueError('Mixed/reordered bake or altered timing')
            p=(self.path.parent/f['file']).resolve()
            if not p.is_relative_to(self.path.parent): raise ValueError('Escaping source path')
            im=Image.open(p).convert('RGBA')
            if list(im.size)!=self.size: raise ValueError('Mixed source canvas')
            delta=np.array(self.joints[2*i]['root'],dtype=float)-first
            if not np.allclose(delta,f['source_root_delta'],atol=2e-6): raise ValueError('Bake/physical root mismatch')
            if not np.allclose(f['visual_root_compensation'],[-delta[0],-delta[1],0],atol=2e-6):
                raise ValueError('Adapter requires horizontal-only declared in-place compensation')
            self.images.append(im); self.roots.append(np.array([delta[0],delta[1],0.]))
        end=np.array(self.joints[-1]['root'],dtype=float)-first
        if abs(end[2])>2e-6: raise ValueError('Vertical endpoint not closed')
        self.stride=np.array([end[0],end[1],0.]); self.roots.append(self.stride)

    def vector(self, xyz):
        """World displacement -> image displacement; screenY runs downward."""
        return self.scale*np.array([self.camera[:3,0]@xyz,-self.camera[:3,1]@xyz])

    def ground(self, xyz):
        # Same fixed camera, centre projection and actual square native viewport.
        relative=np.array(xyz)-self.camera[:3,3]
        return np.array(self.size,dtype=float)/2+self.vector(relative)

    def state(self, tick, mode):
        if mode=='coherent':
            # One sampled visual time owns both whole-actor root and cel.
            # The source120Hz trajectory is retained, not modified or cancelled.
            return self.state(tick//2,'synchronized')
        rate=60 if mode=='synchronized' else 120
        cycle,local=divmod(tick,65*(rate//60))
        i=local//(rate//60); fraction=(local%(rate//60))/(rate//60)
        root=self.roots[i]*(1-fraction)+self.roots[i+1]*fraction+self.stride*cycle
        return i,root,self.vector(root),fraction,cycle

    def render(self,tick,mode,zoom,mask):
        stage=self.stage; origin=self.origin; im=Image.new('RGB',stage,(35,42,47)); d=ImageDraw.Draw(im)
        for n in range(-48,49):
            value=n*.25; color=(79,89,93) if n%4==0 else (52,62,67)
            for ends in [[(value,-12,-1),(value,12,-1)],[(-12,value,-1),(12,value,-1)]]:
                a,b=[origin+self.ground(p)*zoom for p in ends]
                d.line((*a,*b),fill=color,width=1)
        i,root,screen,fraction,cycle=self.state(tick,mode)
        cel=self.images[i]
        if mask:
            out=Image.new('RGBA',cel.size,(232,236,240,0));out.putalpha(cel.getchannel('A'));cel=out
        cel=cel.resize((self.size[0]*zoom,self.size[1]*zoom),Image.Resampling.NEAREST)
        draw=origin+screen*zoom; xy=tuple(rounded(v) for v in draw)
        bbox=cel.getbbox(); clipped=bool(bbox and (xy[0]+bbox[0]<0 or xy[1]+bbox[1]<0 or xy[0]+bbox[2]>stage[0] or xy[1]+bbox[3]>stage[1]))
        im.paste(cel,xy,cel)
        d=ImageDraw.Draw(im);d.rectangle((0,0,stage[0],65),fill=(26,32,37))
        d.text((10,8),f'UNAPPROVED world replay | {mode} | {zoom}x | cel {i:02d} | cycle {cycle}',fill='white')
        d.text((10,28),'Fixed world grid Z=-1m; no shadows/collision proof. Root comes from retarget ledger.',fill='white')
        d.text((10,46),f'World XY {root[0]:.4f}, {root[1]:.4f}m | held cel fraction {fraction:g}',fill='white')
        return im,{'tick':tick,'cel':i,'cycle':cycle,'held_fraction':fraction,'physical_root_m':root.tolist(),'screen_root_px':screen.tolist(),'draw_xy':xy,'clipped':clipped}


def export(replay,out,mode,zoom,mask,loops):
    rate=60 if mode=='synchronized' else 120
    name=f'{mode}-{zoom}x-{"silhouette" if mask else "colour"}'
    path=out/f'{name}.mp4'; count=65*(rate//60)*loops; rows=[]
    video_size=f'{replay.stage[0]}x{replay.stage[1]}'
    process=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',video_size,'-framerate',str(rate),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','0','-pix_fmt','yuv444p','-threads','4',str(path)],stdin=subprocess.PIPE)
    try:
        for tick in range(count):
            im,row=replay.render(tick,mode,zoom,mask)
            if row['clipped']:
                raise ValueError(f'Fixed review stage clips {name} packet{tick}; preserve output and enlarge the fixed stage')
            process.stdin.write(im.tobytes()); rows.append(row)
    finally: process.stdin.close()
    if process.wait()!=0: raise RuntimeError('Encoding failed')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(path)]))
    pts=[float(f['best_effort_timestamp_time']) for f in probe['frames']]
    if len(pts)!=count or any(abs(t-i/rate)>1e-6 for i,t in enumerate(pts)): raise AssertionError('CFR packet timing mismatch')
    decoded=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(path),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    maxerror=0; panels=[]; length=replay.stage[0]*replay.stage[1]*3
    for tick in range(count):
        raw=bytearray()
        while len(raw)<length:
            chunk=decoded.stdout.read(length-len(raw))
            if not chunk: raise AssertionError('Truncated decoded frame')
            raw.extend(chunk)
        expected,_=replay.render(tick,mode,zoom,mask)
        error=int(np.max(np.abs(np.frombuffer(raw,dtype=np.uint8).astype(np.int16)-np.frombuffer(expected.tobytes(),dtype=np.uint8))))
        maxerror=max(maxerror,error)
        # Compact chronological witnesses every cel in first cycle; no claim continuous viewing.
        if tick<65*(rate//60) and tick%(rate//60)==0:
            actual=Image.frombytes('RGB',replay.stage,bytes(raw)); row=rows[tick];x,y=row['draw_xy']
            # FIXED stage crop, not per-cel recenter. Whole actor + travel envelope.
            if replay.stage==(1024,1024):
                panel=actual.crop((192,64,960,896)).resize((384,416),Image.Resampling.NEAREST)
            else:
                panel=actual.resize((384,384),Image.Resampling.NEAREST)
            panels.append(panel)
    if decoded.stdout.read(1): raise AssertionError('Unexpected extra frame')
    if decoded.wait()!=0 or maxerror>2: raise AssertionError('Decoded RGB mismatch')
    for start in range(0,len(panels),12):
        sheet=Image.new('RGB',(4*384,3*440),(26,32,37));draw=ImageDraw.Draw(sheet)
        for k,panel in enumerate(panels[start:start+12]):
            x=(k%4)*384;y=(k//4)*440;sheet.paste(panel,(x,y));draw.text((x+4,y+417),f'cel {start+k:02d}',fill='white')
        sheet.save(out/f'{name}-decoded-p{start//12}.png')
    return {'file':path.name,'sha256':sha(path),'fps':rate,'decoded_frame_count':count,'duration_seconds':str(Fraction(count,rate)),'timestamp_tolerance_seconds':1e-6,'actual_all_frames_max_rgb_error':maxerror,'clipped_count':sum(r['clipped'] for r in rows),'observations':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--joints',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--loops',type=int,default=3);a=p.parse_args()
    if a.output.exists(): raise FileExistsError('Preserve previous outputs')
    if not 1<=a.loops<=3: raise ValueError('Bound loops1..3')
    replay=Replay(a.contract,a.joints);a.output.mkdir(parents=True)
    variants=[]
    for mode in ['synchronized','continuous']:
        for zoom in [1,2]:
            for mask in [False,True]:variants.append(export(replay,a.output,mode,zoom,mask,a.loops))
    variants.append(export(replay,a.output,'coherent',1,False,a.loops))
    receipt={'state':'UNAPPROVED_PHYSICAL_ROOT_AUDITION','script_sha256':sha(__file__),'contract_sha256':sha(a.contract),'joints_sha256':sha(a.joints),'source_rgba_sha256':[sha(replay.path.parent/f['file'])for f in replay.frames],'native_canvas':replay.size,'stage_canvas':list(replay.stage),'fixed_origin_px':replay.origin.tolist(),'cycle_seconds':'65/60','camera_matrix':replay.camera.tolist(),'root_stride_m':replay.stride.tolist(),'projected_root_stride_px':replay.vector(replay.stride).tolist(),'variants':variants,'limits':['Grid is projected correctly at declared floor, but is not collision or foot-force evidence','Every cel has fixed declared native canvas; stage and origin fixed across all poses','120Hz continuous consumer holds60Hz art, exposing within-cel travel; no compensation is applied','All actual encoded frames decoded numerically; sheets are discrete witnesses, not continuous video vision','No art score or foot-contact acceptance is inferred from technical checks']}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    options=''.join(f'<option>{v["file"]}</option>'for v in variants)
    (a.output/'index.html').write_text(f'<!doctype html><meta charset=utf-8><title>Captain world replay — unapproved</title><style>body{{background:#20272d;color:white;font:16px sans-serif}}video{{display:block;image-rendering:pixelated;max-width:95vw}}button,select{{padding:8px}}</style><h1>Captain world replay — unapproved</h1><p>Actual 3D body diagnostic. Fixed projected world grid; contact and art quality remain open. Synchronized60Hz or continuous120Hz root with held60Hz cels. Each cycle65/60seconds.</p><select id=s>{options}</select><button id=slow>Half speed</button><button id=normal>Normal speed</button><video id=v controls loop width=768 src="{variants[0]["file"]}"></video><p><a href=receipt.json>Source and decoded-video evidence</a></p><script>const v=document.querySelector("#v");document.querySelector("#s").onchange=e=>{{v.src=e.target.value;v.load()}};document.querySelector("#slow").onclick=()=>v.playbackRate=.5;document.querySelector("#normal").onclick=()=>v.playbackRate=1;</script>')
    print(json.dumps({'output':str(a.output),'variants':len(variants),'clipped':sum(v['clipped_count']for v in variants),'stride_px':receipt['projected_root_stride_px']}))


if __name__=='__main__': main()
