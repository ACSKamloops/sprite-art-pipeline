"""A timed 60Hz viewing clip; lossless PNG/layer files remain authoritative."""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile
from PIL import Image,ImageDraw


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Keep prior motion previews frozen')
    a.output.mkdir(parents=True)
    manifest_path=a.candidate/'manifest.json';m=json.loads(manifest_path.read_text())
    assert abs(m['cycle_ms']-1200)<1e-7
    ends=[];elapsed=0.;images=[]
    for f in m['frames']:
        path=a.candidate/f['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256']
        images.append(Image.open(path).convert('RGBA'));elapsed+=f['duration_ms'];ends.append(round(elapsed*1e6))
    samples=[]
    with tempfile.TemporaryDirectory(prefix='captain-preview-')as td:
        td=Path(td)
        for i in range(288):
            time=i/60*1000;local=round((time%m['cycle_ms'])*1e6)
            index=next(n for n,end in enumerate(ends)if local<end)
            zoom=1 if i<144 else 2
            canvas=Image.new('RGBA',(512,544),(38,43,49,255));draw=ImageDraw.Draw(canvas)
            draw.text((10,10),f'Captain combat-ready walk | {"Native 1x"if zoom==1 else"Nearest 2x"}',fill='white')
            image=images[index].resize((256*zoom,256*zoom),Image.Resampling.NEAREST)
            at=(128,160)if zoom==1 else(0,32);canvas.alpha_composite(image,at)
            canvas.convert('RGB').save(td/f'{i:04}.png')
            samples.append({'video_frame':i,'time_ms':time,'source_pose':index,'scale':zoom})
        video=a.output/'captain-walk.mp4'
        r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate','60','-i',str(td/'%04d.png'),
                          '-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],capture_output=True,text=True)
        (a.output/'encode.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr[:1000]
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],capture_output=True,text=True)
    assert probe.returncode==0;info=json.loads(probe.stdout);stream=info['streams'][0]
    assert int(stream['nb_frames'])==288 and abs(float(info['format']['duration'])-4.8)<1e-6
    receipt={'candidate_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
             'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'frames':288,'fps':60,'duration_ms':4800,
             'samples':samples,'scope':'Four timed loops, two native then two nearest2x; source poses sampled at60Hz. MP4 is a lossy viewing artifact, not all-pose pixel/material evidence.'}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'video':str(video),'fps':60,'duration_ms':4800,'source_sha256':receipt['candidate_manifest_sha256']}))


if __name__=='__main__':main()
