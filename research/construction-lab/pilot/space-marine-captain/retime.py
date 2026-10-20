"""Freeze a load/release timing trial without changing a single source pixel.

Physical displacement follows source pose phase, not a newly invented linear
time phase. The player interpolates declared physical_root between these poses.
"""
from pathlib import Path
import argparse, hashlib, json, math, shutil
from PIL import Image


def holds(count, cycle_ms, amplitude, load_phase):
    assert 0 <= amplitude < .5 and cycle_ms == round(cycle_ms)
    weights = [1 + amplitude * math.cos(4 * math.pi * (i/count-load_phase))
               for i in range(count)]
    total=sum(weights); boundary=0; elapsed=0.; durations=[]
    for weight in weights:
        elapsed += weight
        following=round(cycle_ms*elapsed/total)
        durations.append(following-boundary); boundary=following
    assert min(durations)>0 and sum(durations)==cycle_ms
    return durations


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--amplitude',type=float,default=.24)
    p.add_argument('--load-phase',type=float,default=.1)
    a=p.parse_args()
    if a.output.exists(): raise FileExistsError('Keep timing trials frozen')
    path=a.candidate/'manifest.json'; manifest=json.loads(path.read_text())
    delays=holds(len(manifest['frames']),round(manifest['cycle_ms']),a.amplitude,a.load_phase)
    shutil.copytree(a.candidate,a.output)
    original_manifest_sha=hashlib.sha256(path.read_bytes()).hexdigest()
    for record,delay in zip(manifest['frames'],delays):
        record['source_duration_ms']=record['duration_ms']
        record['duration_ms']=delay
        assert hashlib.sha256((a.output/record['file']).read_bytes()).hexdigest()==record['sha256']
    manifest['timing_trial']={
        'source_manifest_sha256':original_manifest_sha,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'amplitude':a.amplitude,'loaded_pose_phase':a.load_phase,
        'method':'Two smooth load holds per cycle, faster release; cumulative integer millisecond boundaries',
        'physical_clock':'Interpolate declared source physical_root per pose interval, then add cycle stride',
        'art_pixels_changed':False,'approval':'Independent fresh art reviews required'}
    images=[]; elapsed=0; previous=0; gif_delays=[]
    for record in manifest['frames']:
        image=Image.open(a.output/record['file']).convert('RGBA')
        bg=Image.new('RGBA',image.size,(38,43,49,255));bg.alpha_composite(image)
        images.append(bg.convert('RGB').resize((512,512),Image.Resampling.NEAREST))
        elapsed+=record['duration_ms']; following=round(elapsed/10)*10
        gif_delays.append(following-previous); previous=following
    assert min(gif_delays)>=10
    images[0].save(a.output/'walk-preview.gif',save_all=True,append_images=images[1:],
                   duration=gif_delays,loop=0,disposal=2)
    manifest['preview_gif']={'clock_quantum_ms':10,'duration_ms':previous,
                            'holds_ms':gif_delays,'method':'cumulative boundary quantization'}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'output':str(a.output),'cycle_ms':sum(delays),'holds_range_ms':[min(delays),max(delays)],'pixels_unchanged':True}))


if __name__=='__main__':main()
