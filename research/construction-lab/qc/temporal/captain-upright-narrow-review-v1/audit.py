import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;B=Path('/home/astra/projects/sprite-construction-lab-captain-techniques/pilot/captain-upright-narrow-v1/artifacts')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r={}
for f in sorted(B.glob('audition-*/report.json')):
 d=json.loads(f.read_text());name=f.parent.name;dest=O/name;dest.mkdir(exist_ok=True);rows=[]
 for v in d['variants']:
  video=f.parent/v['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_frames','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time','-of','json',str(video)]));pts=[float(x['best_effort_timestamp_time'])*1000 for x in probe['frames']];packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_packets','-show_entries','packet=pts_time,duration_time','-of','json',str(video)]))['packets'];end=max(float(x['pts_time'])+float(x.get('duration_time','0'))for x in packets)*1000
  row={'file':str(video),'sha256':sha(video),'hash_matches_report':sha(video)==v['sha256'],'end_ms':end,'expected_end_ms':v['exact_duration_ms'],'clock_pass':abs(end-v['exact_duration_ms']-1)<.01,'decoded_frames':len(pts)};rows.append(row)
  if v['zoom']==2 and (v['silhouette'] or v['slowdown']==2):continue
  targets=[(i*150+75)*v['slowdown'] for i in range(8)]
  all_dense='dense-in-place' in name and v['file']=='rgba-1x-normal.mp4'
  if all_dense:
   holds=d['source_holds_ms'];acc=0;targets=[]
   for h in holds:targets.append(acc+h/2);acc+=h
  inds=[max(j for j,t in enumerate(pts)if t<=target) for target in targets];raw=dest/'decoded'/video.stem;raw.mkdir(parents=True,exist_ok=True);expr='+'.join(f'eq(n\\,{i})'for i in sorted(set(inds)));subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f'select={expr}','-fps_mode','vfr',str(raw/'%03d.png')],check=True)
  images=dict(zip(sorted(set(inds)),sorted(raw.glob('*.png'))));size=256*v['zoom'];box=(96,80,96+size,80+size)
  if 'moving' in name:box=(32,64,352,352)if v['zoom']==1 else(16,64,640,624)
  w=box[2]-box[0];h=box[3]-box[1];nper=12 if all_dense else 4
  for start in range(0,len(inds),nper):
   count=min(nper,len(inds)-start);cols=3 if all_dense else 2;sheet=Image.new('RGB',(cols*w,((count+cols-1)//cols)*(h+24)),(38,43,49));dr=ImageDraw.Draw(sheet)
   for j in range(count):
    i=start+j;im=Image.open(images[inds[i]]).crop(box);x=j%cols*w;y=j//cols*(h+24);sheet.paste(im,(x,y));dr.text((x+3,y+h+3),f'{i}: PTS {pts[inds[i]]:.0f}ms',fill='white')
   sheet.save(dest/f'{video.stem}-page-{start//nper:02}.png')
  row['selected_pts_ms']=[pts[i]for i in inds]
 r[name]={'report_sha256':sha(f),'spec_sha256':d['spec_sha256'],'videos':rows}
for pack in ['dense','eight-key']:
 f=B/pack/'manifest.json';r[pack]={'manifest_sha256':sha(f)}
(O/'binding.json').write_text(json.dumps(r,indent=2)+'\n');print({k:all(v['clock_pass']for v in d['videos'])for k,d in r.items()if 'videos'in d})
