"""Decode the delivered video, compare every sprite crop, and make chronological sheets."""
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
from PIL import Image, ImageDraw

p = Path(__file__).parent
video = Path('/home/astra/artifacts/space-marine-captain-walk/captain-walk.mp4')
source = Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assembled-v20')
(p/'decoded').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),str(p/'decoded/%03d.png')],check=True)
probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
(p/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
m = json.loads((source/'manifest.json').read_text())
images = [Image.open(source/f['file']).convert('RGBA') for f in m['frames']]
for f in m['frames']:
    assert hashlib.sha256((source/f['file']).read_bytes()).hexdigest() == f['sha256']
ends = np.cumsum([f['duration_ms'] for f in m['frames']])
expected = {}
for scale in [1,2]:
    expected[scale] = []
    for image in images:
        plate = Image.new('RGBA',(256*scale,256*scale),(38,43,49,255))
        plate.alpha_composite(image.resize(plate.size,Image.Resampling.NEAREST))
        expected[scale].append(np.asarray(plate.convert('RGB'),dtype=np.int16))
rows = []
for i in range(288):
    scale = 1 if i < 144 else 2
    box = (128,160,384,416) if scale == 1 else (0,32,512,544)
    array = np.asarray(Image.open(p/'decoded'/f'{i+1:03d}.png').convert('RGB').crop(box),dtype=np.int16)
    errors = [float(np.abs(array-x).mean()) for x in expected[scale]]
    best = int(np.argmin(errors))
    wanted = int(np.searchsorted(ends,(i/60*1000)%1200,side='right'))
    rows.append({'frame':i,'time_seconds':i/60,'scale':scale,'best_pose':best,'clock_pose':wanted,'mae':errors[best],'clock_pose_mae':errors[wanted]})
result = {'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),'decoded_frames':288,'expected_clock_matches':sum(r['best_pose']==r['clock_pose'] for r in rows),'different_nearest_pose':[r for r in rows if r['best_pose']!=r['clock_pose']],'max_expected_rgb_mae':max(r['clock_pose_mae'] for r in rows),'mean_expected_rgb_mae':sum(r['clock_pose_mae'] for r in rows)/288,'unique_presented_per_cycle':[len({r['best_pose'] for r in rows[j:j+72]}) for j in [0,72,144,216]],'rows':rows,'limits':'Lossy H264 nearest-source comparison, not byte-exact RGBA; title excluded.'}
(p/'sequence-check.json').write_text(json.dumps(result,indent=2)+'\n')
for scale, first, count, columns, width, height in [(1,0,12,4,256,280),(2,144,4,2,512,540)]:
    for start in range(first,first+72,count):
        sheet = Image.new('RGB',(columns*width,(count//columns)*height),(38,43,49))
        draw = ImageDraw.Draw(sheet)
        for j in range(count):
            r = rows[start+j]
            image = Image.open(p/'decoded'/f'{start+j+1:03d}.png')
            box = (128,160,384,416) if scale == 1 else (0,32,512,544)
            x,y = (j%columns)*width,(j//columns)*height
            sheet.paste(image.crop(box),(x,y+24))
            draw.text((x+3,y+3),f"{r['time_seconds']:.3f}s pose{r['best_pose']:02}",fill='white')
        name = f'native-consecutive-{start:02}.png' if scale == 1 else f'twice-consecutive-{start:03}.png'
        sheet.save(p/name)
print({k:v for k,v in result.items() if k not in ['rows','different_nearest_pose']})
