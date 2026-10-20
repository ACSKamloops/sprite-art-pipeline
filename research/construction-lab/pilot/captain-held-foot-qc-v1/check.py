"""Actual opaque sole-patch motion in a held cel, not target contact inference."""
from pathlib import Path
import json,hashlib,subprocess,bisect
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;S=Path('/home/astra/projects/sprite-construction-lab/pilot/captain-guided-key-art-v1/artifacts/trial-v2');V=Path('/home/astra/artifacts/captain-guided-key-art-v1');report=json.loads((V/'report.json').read_text());spec=json.loads((S/'audition-physical.json').read_text());video=V/'rgba-1x-normal.mp4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(video)==report['variants'][0]['sha256'];assert sha(S/'audition-physical.json')==report['spec_sha256']
# Manually selected visible LEFT-image boot rubber sole on key1. Source guide calls far support flat at pose9; anatomy is not recovered from generated art.
source=Image.open(S/'frames/001.png').convert('RGBA');a=np.array(source);xy=(102,241);box=(97,235,108,242);patch=a[box[1]:box[3],box[0]:box[2]];mask=patch[:,:,3]==255;assert a[xy[1],xy[0],3]==255;assert mask.sum()>40
source.crop((85,215,120,249)).resize((280,272),Image.Resampling.NEAREST).save(P/'sole-template.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]));ts=[round(float(f['best_effort_timestamp_time'])*1000)for f in probe['frames']];stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height','-of','json',str(video)]))['streams'][0];w,h=stream['width'],stream['height'];targets=[150,170,204,238,272,289,1350,1489,0,1200];ids={max(0,bisect.bisect_right(ts,t)-1)for t in targets};proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-vsync','0','-enc_time_base','1:1000','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE);ims={}
for i,t in enumerate(ts):
 raw=proc.stdout.read(w*h*3)
 if i in ids:ims[t]=np.frombuffer(raw,dtype=np.uint8).reshape(h,w,3).copy()
assert proc.wait()==0
rows=[];panels=[]
for target in targets:
 t=ts[max(0,bisect.bisect_right(ts,target)-1)];im=ims[t];candidates=[]
 cel=0 if target in [0,1200] else 1
 assert int((t%1200)//150)==cel
 obs=max((o for o in report['variants'][0]['observations']if o['output_ms']<=t),key=lambda o:o['output_ms']);assert obs['frame']==cel
 aa=np.array(Image.open(S/f'frames/{cel:03}.png').convert('RGBA'));patch=aa[box[1]:box[3],box[0]:box[2]];mask=patch[:,:,3]==255;assert aa[xy[1],xy[0],3]==255
 # Independent pixel search, broad absolute screen bounds. No root/cel origin is supplied to matcher.
 for y in range(305,370):
  for x in range(400,530):
   sub=im[y:y+patch.shape[0],x:x+patch.shape[1]];err=np.abs(sub.astype(int)-patch[:,:,:3].astype(int))[mask];e=int(err.max());mean=float(err.mean())
   if e<=2:candidates.append((mean,x,y,e))
 assert len(candidates)==1,(t,candidates[:10]);mean,x,y,e=candidates[0];point=[x+xy[0]-box[0],y+xy[1]-box[1]]
 rows.append({'requested_ms':target,'actual_pts_ms':t,'same_cel':cel,'unique_patch_matches':len(candidates),'opaque_template_texels':int(mask.sum()),'max_RGB_error':e,'witness_screen_xy':point,'patch_screen_top_left':[x,y]})
 panel=Image.fromarray(im).crop((400,285,570,365)).resize((680,320),Image.Resampling.NEAREST);d=ImageDraw.Draw(panel);px=(point[0]-400)*4;py=(point[1]-285)*4;d.rectangle((px-6,py-6,px+6,py+6),outline='cyan',width=2);d.text((8,8),f'actualPTS {t}ms sole {point}',fill='white');panels.append(panel)
sheet=Image.new('RGB',(1360,1600));
for i,p in enumerate(panels):sheet.paste(p,((i%2)*680,(i//2)*320))
sheet.save(P/'actual-held-sole.png')
first=rows[0]['witness_screen_xy'];last=rows[5]['witness_screen_xy'];delta=[last[i]-first[i]for i in range(2)];assert abs(delta[0])>1,delta
negative={'claim':'stationary rendered sole within key1 hold (<=1px)','measured_shift':delta,'result':'FAIL','method':'same visible alpha255 rubber-sole texels uniquely matched in decoded actualMP4; fixed camera'}
guide=json.loads((P.parent/'captain-upper-loading-v1/source/poses.json').read_text());g9=guide['frames'][9]['legs']['far']['foot']['sole_world'];g17=guide['frames'][17]['legs']['far']['foot']['sole_world'];gd=max(abs(b-a)for p9,p17 in zip(g9,g17)for a,b in zip(p9,p17));assert gd<1e-10
out={'schema':'captain.rendered_hold_drift.v1','decision':'rendered_stationary_stance_claim_fails','source_spec_sha256':sha(S/'audition-physical.json'),'source_construction_sha256':sha(S/'construction.json'),'source_key1_sha256':sha(S/'frames/001.png'),'source_key0_sha256':sha(S/'frames/000.png'),'actual_video_sha256':sha(video),'export_report_sha256':sha(V/'report.json'),'code_sha256':sha(Path(__file__)),'manual_witness':{'key':1,'source_xy':xy,'source_rgba':a[xy[1],xy[0]].tolist(),'source_patch_box':box,'ownership':'Visible left-image boot dark rubber sole, manually selected. Guide far flat at pose9; generated-art limb/material identity across other keys unproved. No invisible marker.'},'rows':rows,'within_hold_delta_screen_pixels':delta,'analytic_full_hold_root_delta':[-8.25,3.3991869381244157],'plant_negative_test':negative,'actual_key0_repeat_across_wrap_delta':[rows[9]['witness_screen_xy'][i]-rows[8]['witness_screen_xy'][i]for i in range(2)],'wrap_same_cel_cycle_delta':[rows[6]['witness_screen_xy'][i]-first[i]for i in range(2)],'limits':['No heel/toe reaction or force model','No global ground-plane world reconstruction from pixels','One opaque witness in one guide-designated support hold; not all8foot contact certification','No continuousvideo ingestion; selected actual decoded states personally inspected','No generated-leg style approval'],'guide_target_check':{'source_packet_sha256':sha(P.parent/'captain-upper-loading-v1/source/poses.json'),'far_flat_sole_world_displacement_pose9_to17':gd,'meaning':'Frozen guide flat support worldpoints fixed; the AI sole witness is not bound to that guide material.'},'diagnosis':'Frozen whole cel follows continuous root; all visible materials translate together within hold. Guide plant validity cannot transfer to this held artwork.'};(P/'report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
