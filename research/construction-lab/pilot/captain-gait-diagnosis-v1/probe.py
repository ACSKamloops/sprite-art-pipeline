"""One bounded fixed-track experiment; no source surface changes or art approval."""
import sys,json,hashlib,math,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
sys.argv=[__file__,'--design',str(P/'source/wider-design.json')]
s=importlib.util.spec_from_file_location('guide',P/'source/generator.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
b=json.loads((P/'source/baseline-poses.json').read_text());frames=[];margin=100;boneerror=0;minsole=100
for i in range(1441):
 f=g.pose(i/1440)
 for l in f['legs'].values():
  margin=min(margin,l['reach_margin']);minsole=min(minsole,min(v[2] for v in l['foot']['sole_world']));boneerror=max(boneerror,*[abs(v-e)for v,e in zip(l['bone_lengths'],[42,48])])
assert minsole>-1e-9 and boneerror<1e-9
for old in b['frames']:
 f=g.pose(old['phase']);f.update({k:old[k]for k in ['index','duration_ms','source_tick']});assert f['physical_root_world']==old['physical_root_world'];assert f['upper_world']==old['upper_world'];frames.append(f)
a=dict(b);a.update(frames=frames,design=g.CONFIG,scope='UNAPPROVED fixed-track pose alternative, no surface or timing edits; baseline neutral_bind intentionally retained for unchanged source registration',builder_sha256=hashlib.sha256((P/'source/generator.py').read_bytes()).hexdigest(),design_sha256=hashlib.sha256((P/'source/wider-design.json').read_bytes()).hexdigest());(P/'alternative-poses.json').write_text(json.dumps(a,indent=2)+'\n')
def metric(f):
 ls=f['legs'];r=f['physical_root_pixels'];ank={n:[v-r[i]for i,v in enumerate(l['pixels']['ankle'])]for n,l in ls.items()};knee={}
 for n,l in ls.items():
  w=l['world'];v=g.sub(w['hip'],w['knee']);z=g.sub(w['ankle'],w['knee']);knee[n]=180-math.degrees(math.acos(max(-1,min(1,g.dot(v,z)/42/48))))
 return {'ankle_pixels_in_place':ank,'ankle_x_separation':abs(ank['far'][0]-ank['near'][0]),'knee_flex_degrees':knee,'roles':{n:l['foot']['role']for n,l in ls.items()}}
rows=[{'index':i,'baseline':metric(b['frames'][i]),'alternative':metric(frames[i])}for i in range(72)]
report={'state':'UNAPPROVED_DIAGNOSTIC_PACKET','baseline_original_sha256':'878649a6b23e6c4a0a3fd3dd2c5eba76c2a623a81b4c28cda3057f4da7b24301','alternative_sha256':hashlib.sha256((P/'alternative-poses.json').read_bytes()).hexdigest(),'changes':{'foot_track_half_widening_world':6,'hip_half_widening_world':3},'unchanged':['72 durations total1200ms','physical root','upper body packet','bone lengths42/48','foot pitch and contact schedule','swing lift and forward path','source art and meshes not edited','baseline neutral_bind retained'], 'preflight':{'samples':1441,'min_reach_margin':margin,'max_bone_error':boneerror,'min_sole_z':minsole},'frames':rows,'limits':['No mass or armor collision model','No rendered material-contact proof','No full-color alternative rendered or approved','Neutral bind is deliberately baseline: renderer must not re-fit source parts to alternative pose0']};(P/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
sheet=Image.new('RGBA',(2048,1024),(35,40,45,255));dr=ImageDraw.Draw(sheet)
for j,i in enumerate(range(0,72,9)):
 # Both skeletons in same fixed canvas, baseline left, alternative right.
 for k,f in enumerate([b['frames'][i],frames[i]]):
  im=g.draw_pose(f,P/f'guide-{i:02}-{k}.png');sheet.alpha_composite(im,((j%4)*512+k*256,(j//4)*512));dr.text(((j%4)*512+k*256+3,(j//4)*512+260),f'pose{i} '+('baseline'if k==0 else 'wider fixed tracks'),fill='white')
sheet.save(P/'track-comparison.png');print(json.dumps(report['preflight']));print('f27',rows[27])
