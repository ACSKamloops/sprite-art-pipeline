#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
ART=Path('/home/astra/artifacts')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={'schema':'captain.whole_key_video_audit.v1','candidates':{}}
for name in ['old','upright']:
 base=ART/f'captain-key-comparison-{name}-source-v1';report=json.loads((base/'report.json').read_text()); dest=OUT/name;dest.mkdir(exist_ok=True);decoded=dest/'decoded';decoded.mkdir(exist_ok=True)
 candidate={'report_sha256':sha(base/'report.json'),'spec_sha256':report['spec_sha256'],'variants':[]}
 for v in report['variants']:
  file=base/v['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_frames','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time','-of','json',str(file)]));pts=[float(f['best_effort_timestamp_time'])*1000 for f in probe['frames']]; selected=[min(range(len(pts)),key=lambda j:abs(pts[j]-(i*150+75)*v['slowdown'])) for i in range(8)]
  tag=file.stem; target=decoded/tag;target.mkdir(exist_ok=True); expr='+'.join(f'eq(n\\,{i})' for i in selected)
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(file),'-vf',f'select={expr}','-fps_mode','vfr',str(target/'%02d.png')],check=True)
  size=256*v['zoom']; sheet=Image.new('RGB',(size*4,(size+24)*2),(38,43,49));dr=ImageDraw.Draw(sheet)
  for i,p in enumerate(sorted(target.glob('*.png'))):
   im=Image.open(p).convert('RGB');crop=im.crop((120,88,120+size,88+size));x=(i%4)*size;y=(i//4)*(size+24);sheet.paste(crop,(x,y));dr.text((x+3,y+size+4),f'{i}: decoded PTS {pts[selected[i]]:.0f}ms',fill='white')
  sheet.save(dest/f'{tag}-eight.png')
  expected_duration=1200*3*v['slowdown'];end=pts[-1]+float(probe['frames'][-1].get('pkt_duration_time','0'))*1000
  candidate['variants'].append({'file':str(file),'sha256':sha(file),'matches_exporter_hash':sha(file)==v['sha256'],'decoded_frame_count':len(pts),'first_pts_ms':pts[0],'end_ms':end,'expected_end_ms':expected_duration,'end_exact':abs(end-expected_duration)<.01,'selected_indices':selected,'selected_pts_ms':[pts[j] for j in selected],'selected_source_pose':[int((pts[j]/v['slowdown'])%1200//150) for j in selected],'sheet':str(dest/f'{tag}-eight.png')})
 result['candidates'][name]=candidate
(OUT/'video-binding.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:{'variants':len(v['variants']),'clock_pass':all(x['end_exact'] for x in v['variants'])}for k,v in result['candidates'].items()})
