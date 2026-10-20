"""Exact rational sprite-clock MP4 preview; RGB framing and CFR verification are explicit.
No image generation, source modification, concat demuxer or silent time resampling.
"""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json,math,subprocess
import numpy as np
from PIL import Image,ImageDraw
MAX_FPS=240;MAX_KEYS=1000;MAX_OUTPUT_FRAMES=24000;MAX_SECONDS=120;MAX_PIXEL_FRAMES=1_000_000_000
PROVENANCE={'source_script_sha256':'c157168be9e6d1a06208f2fe8a5dbf93f701da8578744b2b952c3ac5f24503a5','adaptation':'Portable skill copy; historical baseline file is not a runtime dependency.'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def hold_fraction(v):
 if not isinstance(v,list) or len(v)!=2 or any(type(x)!=int for x in v) or v[0]<=0 or v[1]<=0:raise ValueError('hold must be two strictly positive integers [numerator,denominator]')
 return Fraction(*v)
def plan_clock(holds,fps=None):
 if not holds or len(holds)>MAX_KEYS:raise ValueError('key count outside1..1000')
 denom=math.lcm(*(h.denominator for h in holds))
 if denom>MAX_FPS:raise ValueError(f'Unrepresentable exact CFR clock: denominator LCM {denom} exceeds maximum240fps')
 if fps is None:
  preferred=[f for f in [60,120,200,240] if f%denom==0]
  fps=preferred[0] if preferred else math.ceil(60/denom)*denom
 if type(fps)!=int or not 1<=fps<=MAX_FPS or fps%denom:raise ValueError('fps must be integer1..240 and represent every reduced hold denominator exactly')
 repeats=[int(h*fps) for h in holds];total=sum(holds,Fraction())
 if any(n<=0 for n in repeats) or sum(repeats)>MAX_OUTPUT_FRAMES or total>MAX_SECONDS:raise ValueError('Preview frame/duration bound exceeded')
 return fps,repeats,total
# Same8px two-color checker and whole-canvas compositing as the retained baseline.
def checker(w,h):
 im=Image.new('RGBA',(w,h),(49,53,61,255));d=ImageDraw.Draw(im)
 for y in range(0,h,8):
  for x in range(0,w,8):
   if (x//8+y//8)%2:d.rectangle((x,y,x+7,y+7),fill=(64,68,77,255))
 return im

def encode(manifest,out,fps=None,scale=4,min_psnr=32.0):
 manifest=Path(manifest).resolve();out=Path(out).resolve()
 if out.exists():raise ValueError('Refuse overwrite output directory')
 if type(scale)!=int or not 1<=scale<=8:raise ValueError('scale must be integer1..8')
 doc=json.loads(manifest.read_text());rows=doc['frames'];holds=[hold_fraction(f['hold']) for f in rows];fps,repeats,total=plan_clock(holds,fps)
 canvas=doc['canvas'];w,h=canvas
 if any(type(v)!=int or not 1<=v<=2048 for v in canvas) or (w*scale)%2 or (h*scale)%2:raise ValueError('Invalid canvas or odd yuv420 output dimensions')
 if w*h*scale*scale*sum(repeats)>MAX_PIXEL_FRAMES:raise ValueError('Preview aggregate pixel bound exceeded')
 sources=[];templates=[]
 for i,f in enumerate(rows):
  src=Path(f['file']);src=src if src.is_absolute() else manifest.parent/src;digest=sha(src)
  if digest!=f.get('sha256',f.get('png_sha256')):raise ValueError('Source PNG SHA mismatch or missing')
  with Image.open(src) as image:
   rgba=image.convert('RGBA')
   if list(rgba.size)!=canvas:raise ValueError('Source canvas mismatch')
   bg=checker(w,h);bg.alpha_composite(rgba);rgb=bg.convert('RGB').resize((w*scale,h*scale),Image.Resampling.NEAREST)
  templates.append(np.array(rgb));sources.append({'source_index':i,'file':str(src),'png_sha256':digest,'hold':rows[i]['hold'],'repeated_frames':repeats[i],'rgb_template_sha256':hashlib.sha256(rgb.tobytes()).hexdigest()})
 out.mkdir(parents=True);(out/'templates').mkdir()
 for i,a in enumerate(templates):Image.fromarray(a).save(out/'templates'/f'{i:04d}.png')
 video=out/'preview-exact.mp4';cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w*scale}x{h*scale}','-framerate',str(fps),'-i','pipe:0','-an','-frames:v',str(sum(repeats)),'-fps_mode','passthrough','-c:v','libx264','-bf','0','-preset','fast','-crf','16','-pix_fmt','yuv420p','-video_track_timescale',str(fps),'-movflags','+faststart',str(video)]
 with (out/'ffmpeg.log').open('wb') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
  try:
   for a,n in zip(templates,repeats):
    raw=a.tobytes()
    for _ in range(n):proc.stdin.write(raw)
   proc.stdin.close();code=proc.wait()
  except BaseException:
   proc.kill();proc.wait();raise
 if code:raise RuntimeError('ffmpeg encode failed; see log')
 probe_cmd=['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_format','-show_frames','-of','json',str(video)];probe=json.loads(subprocess.check_output(probe_cmd));dump(out/'ffprobe.json',probe)
 stream=probe['streams'][0];frames=probe['frames'];tb=Fraction(stream['time_base']);expected=[i for i,n in enumerate(repeats) for _ in range(n)]
 if len(frames)!=len(expected):raise ValueError('ffprobe frame count differs from exact repetitions')
 timing=[]
 for i,f in enumerate(frames):
  pts=int(f.get('pts',f['best_effort_timestamp']));duration=int(f.get('duration',f.get('pkt_duration',0)));t=pts*tb;dur=duration*tb
  if t!=Fraction(i,fps) or dur!=Fraction(1,fps):raise ValueError(f'Non-exact PTS or duration at decoded frame{i}: {t},{dur}')
  timing.append({'output_index':i,'source_index':expected[i],'pts':pts,'time_base':[tb.numerator,tb.denominator],'pts_seconds':[t.numerator,t.denominator],'duration_seconds':[dur.numerator,dur.denominator]})
 actual_total=int(stream['duration_ts'])*tb
 if actual_total!=total or sum((Fraction(*f['duration_seconds']) for f in timing),Fraction())!=total:raise ValueError('Exact rational stream duration mismatch')
 # Lossy MP4 cannot prove pixel equality. Compare every decoded frame with every
 # prepared RGB source template; refuse ambiguous/misclassified distinct keys.
 decode_cmd=['ffmpeg','-v','error','-i',str(video),'-map','0:v:0','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
 decode=subprocess.Popen(decode_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);frame_bytes=w*h*scale*scale*3;classification=[];decoded_count=0;failures=[];hashes=[s['rgb_template_sha256'] for s in sources]
 template32=[a.astype(np.float32) for a in templates]
 while True:
  raw=decode.stdout.read(frame_bytes)
  if not raw:break
  if len(raw)!=frame_bytes:raise ValueError('Partial decoded RGB frame')
  if decoded_count>=len(expected):raise ValueError('Extra decoded frames')
  arr=np.frombuffer(raw,np.uint8).reshape((h*scale,w*scale,3));af=arr.astype(np.float32);mse=[float(np.mean((af-a)**2)) for a in template32];best=min(range(len(mse)),key=mse.__getitem__);target=expected[decoded_count];equivalent=[j for j,x in enumerate(hashes) if x==hashes[target]];other=[mse[j] for j in range(len(mse)) if hashes[j]!=hashes[best]];margin=min(other)-mse[best] if other else None;psnr=10*math.log10(255*255/mse[target]) if mse[target]>0 else None;accepted=best in equivalent and (margin is None or margin>0.01) and (psnr is None or psnr>=min_psnr)
  if not accepted:failures.append(decoded_count)
  classification.append({'output_index':decoded_count,'expected_source_index':target,'nearest_source_index':best,'identical_RGB_source_group':equivalent,'expected_source_MSE':mse[target],'expected_source_MAE':float(np.mean(np.abs(af-template32[target]))),'expected_source_PSNR_dB':psnr,'distinct_source_MSE_margin':margin,'classification_and_quality_pass':accepted,'source_MSE_all':mse});decoded_count+=1
 stderr=decode.stderr.read().decode();rc=decode.wait()
 if rc or decoded_count!=len(expected):raise RuntimeError(f'Decode error/count mismatch: {stderr}')
 transitions=[{'output_index':i,'time_seconds':[Fraction(i,fps).numerator,Fraction(i,fps).denominator],'from_source':expected[i-1],'to_source':expected[i]} for i in range(1,len(expected)) if expected[i]!=expected[i-1]]
 # Distinguish measured visible transitions from logical boundaries between
 # byte-identical source templates, which no decoder can visually identify.
 observed_transitions=[]
 for i in range(1,len(classification)):
  prev=classification[i-1]['nearest_source_index'];cur=classification[i]['nearest_source_index']
  if hashes[prev]!=hashes[cur]:
   observed_transitions.append({'output_index':i,'from_source':prev,'to_source':cur,'pts_seconds':timing[i]['pts_seconds']})
 visible_expected=[x['output_index'] for x in transitions if hashes[x['from_source']]!=hashes[x['to_source']]]
 if [x['output_index'] for x in observed_transitions]!=visible_expected:raise ValueError('Observed decoded visual transitions differ from declared observable transitions')
 for t in transitions:t['visually_observable']=hashes[t['from_source']]!=hashes[t['to_source']]
 receipt={'schema':'exact-rational-CFR-preview/v1','source_manifest':str(manifest),'source_manifest_sha256':sha(manifest),'source_canvas':canvas,'output_canvas':[w*scale,h*scale],'scale':scale,'matte':'Baseline8px checker RGBA compositing before whole-canvas nearest-neighbor scaling','fps':fps,'time_base':[tb.numerator,tb.denominator],'source_key_count':len(rows),'sources':sources,'frame_count':len(expected),'duration_rational':[total.numerator,total.denominator],'stream_duration_rational':[actual_total.numerator,actual_total.denominator],'format_duration_decimal':probe['format']['duration'],'format_duration_is_rounded_container_display_not_clock_authority':True,'expected_and_measured_transition_frames':transitions,'observed_decoded_visual_transitions':observed_transitions,'logical_boundaries_between_identical_templates_not_visually_provable':[x for x in transitions if not x['visually_observable']],'frame_PTS_and_duration_exact':True,'all_decoded_frames_classified_correctly_with_quality_bound':not failures,'classification_failed_output_indices':failures,'classification_rule':'Nearest prepared RGB source by MSE; identical-source groups allowed; distinct-source margin>0.01MSE; expected-template PSNR>=threshold. This is lossy nearest-template evidence, not exact source-pixel identity.','minimum_PSNR_dB_required':min_psnr,'minimum_observed_PSNR_dB':min((x['expected_source_PSNR_dB'] for x in classification if x['expected_source_PSNR_dB'] is not None),default=None),'encoder_command':cmd,'probe_command':probe_cmd,'decode_command':decode_cmd,'video_sha256':sha(video),'code_sha256':sha(__file__),'encoder_provenance':PROVENANCE,'no_concat_or_final_duplicate_or_t_resampling':True,'scope':'Exact declared preview clock only; not recovered source timing, art approval or pixel-exact video.'}
 dump(out/'frame-timing.json',timing);dump(out/'decoded-classification.json',classification);dump(out/'RECEIPT.json',receipt)
 if failures:raise ValueError(f'Lossy source classification/quality not proved at frames{failures}')
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('output',type=Path);p.add_argument('--fps',type=int);p.add_argument('--scale',type=int,default=4);p.add_argument('--min-psnr',type=float,default=32.0);a=p.parse_args();r=encode(a.manifest,a.output,a.fps,a.scale,a.min_psnr);print(json.dumps({'fps':r['fps'],'frames':r['frame_count'],'duration':r['duration_rational'],'transitions':r['expected_and_measured_transition_frames'],'minimum_PSNR_dB':r['minimum_observed_PSNR_dB'],'output':str(a.output)}))
