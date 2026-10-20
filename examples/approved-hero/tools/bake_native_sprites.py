#!/usr/bin/env python3
"""Offline video -> native sampled sprites. Only --output is ever written."""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json,subprocess,sys
import numpy as np
from PIL import Image

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def pair(v):return [v.numerator,v.denominator]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def integer(v):return type(v) is int

def validate_recipe(r):
 specs={'schema':None,'source':{'sha256','canvas','frame_count','first_pts','uniform_hold','duration'},'sampling':{'canvas','stride','offset','filter'},'matte':{'rule','green_min','green_minus_red_min','green_minus_blue_min','preserve_rgb_under_alpha0'},'selection':{'start','count','step','loop','mode'},'despill':{'rule','expected_changed_pixels'},'decode':{'pixel_format','threads'}}
 need(type(r) is dict and set(r)==set(specs),'Unknown/missing recipe fields')
 for k,keys in specs.items():
  if keys is not None:need(type(r[k]) is dict and set(r[k])==keys,'Unknown/missing '+k+' contract fields')
 need(r['schema']=='native-sprite-bake-v1','Unsupported/stale recipe schema')
 s=r['source'];h=s['sha256'];need(type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h),'Invalid SHA256')
 for key in ['canvas']:
  v=s[key];need(type(v) is list and len(v)==2 and all(integer(x) and x>0 for x in v),'Invalid source geometry')
 need(integer(s['frame_count']) and s['frame_count']>0,'Invalid source frame count')
 for key in ['first_pts','uniform_hold','duration']:
  v=s[key];need(type(v) is list and len(v)==2 and all(integer(x) for x in v) and v[1]>0,'Invalid rational '+key)
  need(key=='first_pts' or v[0]>0,'Nonpositive rational '+key)
 a=r['sampling']
 for key in ['canvas','stride','offset']:
  v=a[key];need(type(v) is list and len(v)==2 and all(integer(x) and x>=(0 if key=='offset' else 1) for x in v),'Invalid sampling '+key)
 need(a['filter']=='fixed-whole-canvas-point-sample','Unsupported sampling filter')
 need(all(a['canvas'][i]*a['stride'][i]==s['canvas'][i] and 0<=a['offset'][i]<a['stride'][i] for i in range(2)),'Sampling is not fixed whole-canvas integer stride')
 m=r['matte'];need(m['rule']=='alpha0-iff-green-threshold-and-two-differences' and m['preserve_rgb_under_alpha0'] is True,'Unsupported/stale matte rule')
 need(all(integer(m[k]) and 0<=m[k]<=255 for k in ['green_min','green_minus_red_min','green_minus_blue_min']),'Invalid matte thresholds')
 q=r['selection'];need(all(integer(q[k]) for k in ['start','count','step']) and q['start']>=0 and q['count']>0 and q['step']==1,'Invalid selection range/native order');need(q['start']+q['count']<=s['frame_count'],'Selection outside source range');need(type(q['loop']) is bool and q['mode']=='explicit-native-order','Invalid loop/selection contract')
 d=r['despill'];need(d['rule']=='opaque-green-dominant-set-green-max-red-blue' and integer(d['expected_changed_pixels']) and d['expected_changed_pixels']>=0,'Unsupported/stale despill contract')
 need(r['decode']=={'pixel_format':'rgb24','threads':4},'Decoder contract must be bounded RGB24 / four threads')

def probe_source(video,r):
 need(video.is_file(),'Video missing');need(sha(video)==r['source']['sha256'],'Source SHA256 mismatch')
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_frames','-of','json',str(video)]))
 need(len(data.get('streams',[]))==1,'No unique selected video stream');s=data['streams'][0];frames=data.get('frames',[]);c=r['source'];need([s['width'],s['height']]==c['canvas'],'Source geometry mismatch');need(len(frames)==c['frame_count'],'Source frame count mismatch');tb=Fraction(s['time_base']);pts=[int(f['best_effort_timestamp'])*tb for f in frames];need(pts[0]==Fraction(*c['first_pts']),'Source initial PTS mismatch');holds=[b-a for a,b in zip(pts,pts[1:])];last=frames[-1];tail=last.get('duration',last.get('pkt_duration'))
 if tail is not None and int(tail)>0:tail=int(tail)*tb
 elif 'duration_ts' in s:tail=(int(s.get('start_pts',0))+int(s['duration_ts']))*tb-pts[-1]
 else:raise ValueError('Missing actual final frame duration')
 holds.append(tail);need(all(v>0 for v in holds),'Nonpositive native hold');need(all(v==Fraction(*c['uniform_hold']) for v in holds),'Source timing mismatch');need(sum(holds)==Fraction(*c['duration']),'Source duration mismatch')
 if 'duration_ts' in s:need(int(s['duration_ts'])*tb==Fraction(*c['duration']),'Stream duration mismatch')
 need(Fraction(s['r_frame_rate'])==1/Fraction(*c['uniform_hold']) and Fraction(s['avg_frame_rate'])==1/Fraction(*c['uniform_hold']),'Source stream rate mismatch')
 return {'canvas':c['canvas'],'frame_count':len(frames),'time_base':pair(tb),'r_frame_rate':s['r_frame_rate'],'avg_frame_rate':s['avg_frame_rate'],'duration':pair(sum(holds)),'frames':[{'index':i,'native_pts_integer':int(f['best_effort_timestamp']),'pts':pair(pts[i]),'playback_pts':pair(pts[i]-pts[0]),'hold':pair(holds[i])} for i,f in enumerate(frames)]}

def read_exact(pipe,size):
 chunks=[];left=size
 while left:
  b=pipe.read(left)
  if not b:raise RuntimeError('Unexpected short RGB decode stream')
  chunks.append(b);left-=len(b)
 return b''.join(chunks)

def bake(video,recipe_path,output):
 # Complete preflight before any output creation. Existing paths (including symlinks) are refused.
 need(not output.exists() and not output.is_symlink(),'Output already exists; refusing all writes')
 r=json.loads(recipe_path.read_text());validate_recipe(r);actual=probe_source(video,r)
 need(output.parent.is_dir(),'Output parent must exist');output.mkdir() # no exist_ok; races refuse.
 for name in ['raw128','matte','selected']:(output/name).mkdir()
 dump(output/'recipe.json',r);dump(output/'actual-source.json',actual)
 W,H=r['source']['canvas'];w,h=r['sampling']['canvas'];sx,sy=r['sampling']['stride'];ox,oy=r['sampling']['offset'];yy,xx=np.indices((h,w));xy=np.stack([xx*sx+ox,yy*sy+oy],-1).astype(np.int16);np.save(output/'source-xy.npy',xy,allow_pickle=False)
 cmd=['ffmpeg','-v','error','-threads','4','-i',str(video),'-map','0:v:0','-fps_mode','passthrough','-an','-threads','4','-f','rawvideo','-pix_fmt','rgb24','pipe:1'];proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);records=[];selected=[];journal=[];replay_ok=undo_ok=True;changed_total=0
 try:
  for frame in actual['frames']:
   i=frame['index'];native=np.frombuffer(read_exact(proc.stdout,W*H*3),np.uint8).reshape(H,W,3);rgb=native[xy[:,:,1],xy[:,:,0]].copy();raw=output/'raw128'/f'{i:04}.png';Image.fromarray(rgb).save(raw);v=rgb.astype(np.int16);m=r['matte'];green=(v[:,:,1]>=m['green_min'])&(v[:,:,1]-v[:,:,0]>=m['green_minus_red_min'])&(v[:,:,1]-v[:,:,2]>=m['green_minus_blue_min']);a=np.dstack([rgb,np.where(green,0,255).astype(np.uint8)]);matte=output/'matte'/f'{i:04}.png';Image.fromarray(a).save(matte)
   rec={**frame,'raw_file':raw.relative_to(output).as_posix(),'raw_sha256':sha(raw),'matte_file':matte.relative_to(output).as_posix(),'matte_sha256':sha(matte),'native_rgb_array_sha256':hashlib.sha256(native.tobytes()).hexdigest(),'sampled_rgb_array_sha256':hashlib.sha256(rgb.tobytes()).hexdigest(),'matte_rgba_array_sha256':hashlib.sha256(a.tobytes()).hexdigest()};records.append(rec)
   q=r['selection']
   if q['start']<=i<q['start']+q['count']:
    b=a.copy();mask=(a[:,:,3]>0)&(a[:,:,1]>np.maximum(a[:,:,0],a[:,:,2]));b[:,:,1][mask]=np.maximum(a[:,:,0],a[:,:,2])[mask];need(np.array_equal(a[:,:,[0,2,3]],b[:,:,[0,2,3]]) and np.array_equal(a[~mask],b[~mask]),'Despill preservation guard failed');changes=[]
    for y,x in zip(*np.where(mask)):changes.append({'xy':[int(x),int(y)],'native_source_xy':xy[y,x].tolist(),'before':a[y,x].tolist(),'after':b[y,x].tolist()})
    replay=a.copy();undo=b.copy()
    for e in changes:x,y=e['xy'];replay[y,x]=e['after'];undo[y,x]=e['before']
    replay_ok &= np.array_equal(replay,b);undo_ok &= np.array_equal(undo,a);changed_total+=len(changes);j=i-q['start'];dest=output/'selected'/f'{j:02}.png';Image.fromarray(b).save(dest);selected.append({'index':j,'source_index':i,'file':dest.relative_to(output).as_posix(),'sha256':sha(dest),'source_native_pts':frame['pts'],'playback_pts':pair(Fraction(j)*Fraction(*r['source']['uniform_hold'])),'hold':frame['hold'],'matte_source_file':rec['matte_file'],'matte_source_sha256':rec['matte_sha256']});journal.append({'index':j,'source_index':i,'changed_pixels':len(changes),'changes':changes})
  need(proc.stdout.read(1)==b'','Extra decoded frames beyond source contract');stderr=proc.stderr.read().decode(errors='replace');need(proc.wait()==0,'ffmpeg decode failed: '+stderr)
 except BaseException:
  proc.kill();proc.wait();raise
 need(changed_total==r['despill']['expected_changed_pixels'],'Despill pixel count contract mismatch');need(replay_ok and undo_ok,'Journal replay/undo failed');need(len(selected)==r['selection']['count'],'Selected count mismatch')
 source={'video_name':video.name,'sha256':r['source']['sha256'],'recipe_file':'recipe.json','recipe_sha256':sha(output/'recipe.json'),'tested_code_sha256':sha(Path(__file__)),'source_xy':'source-xy.npy','source_xy_sha256':sha(output/'source-xy.npy')}
 dump(output/'all-native-manifest.json',{'schema':'native-bake-frames-v1','source':source,'canvas':[w,h],'source_canvas':[W,H],'frame_count':len(records),'duration':actual['duration'],'sampling':r['sampling'],'matte':r['matte'],'frames':records})
 dump(output/'manifest.json',{'schema':'native-selected-sprites-v1','source':source,'canvas':[w,h],'loop':r['selection']['loop'],'selection':r['selection'],'duration':pair(sum(Fraction(*f['hold']) for f in selected)),'clock_hz':Fraction(*r['source']['uniform_hold']).denominator,'scope':'Explicit native-order selection; no automatic loop detection or seamlessness claim','frames':selected})
 dump(output/'despill-journal.json',{'rule':r['despill']['rule'],'changed_pixel_count':changed_total,'source_xy':'source-xy.npy','frames':journal})
 dump(output/'receipt.json',{'status':'OFFLINE_BAKE_COMPLETE','source':source,'native_frames':len(records),'selected_frames':len(selected),'despill_changed_pixels':changed_total,'actual_native_pts_and_positive_rational_holds_verified':True,'all_sampled_rgb_preserved_under_hard_matte':True,'despill_alpha_red_blue_unaffected_and_hidden_rgba_exact':True,'journal_actual_replay_exact':bool(replay_ok),'journal_actual_undo_exact':bool(undo_ok),'decoder_threads':4,'no_fitting_reorder_or_automatic_loop_detection':True})
 return output/'receipt.json'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--video',required=True,type=Path);p.add_argument('--recipe',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 try:print(bake(a.video,a.recipe,a.output))
 except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError,subprocess.CalledProcessError) as e:p.exit(2,'Bake rejected: '+str(e)+'\n')
if __name__=='__main__':main()
