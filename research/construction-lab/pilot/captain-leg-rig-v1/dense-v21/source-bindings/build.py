"""Authored Captain full-leg parts and fixed-origin heavy-walk candidate."""
from pathlib import Path
import json,math,hashlib,argparse
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def transform(im,srcpivot,dstpivot,angle,scale=1):
 c=math.cos(angle)/scale;s=math.sin(angle)/scale;px,py=srcpivot;dx,dy=dstpivot
 return im.transform((256,256),Image.Transform.AFFINE,(c,s,px-c*dx-s*dy,-s,c,py+s*dx-c*dy),Image.Resampling.NEAREST,fillcolor=(0,0,0,0))
def angle(v):return math.atan2(v[1],v[0])
def sub(a,b):return[a[0]-b[0],a[1]-b[1]]
def norm(v):return math.hypot(*v)
def rotate(v,a):return[v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a)]
def ik(hip,ankle,l1,l2,bend):
 v=sub(ankle,hip);d=norm(v);reach=max(0,d-l1-l2);d=max(.001,min(d,l1+l2-.001));u=[v[0]/norm(v),v[1]/norm(v)];a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a))
 return[hip[0]+a*u[0]-bend*h*u[1],hip[1]+a*u[1]+bend*h*u[0]],reach

def sample_keys(keys,phase):
 for a,b in zip(keys,keys[1:]):
  if a[0]<=phase<=b[0]:
   t=(phase-a[0])/(b[0]-a[0]);return a[1]+(b[1]-a[1])*t
 return keys[-1][1]

def build(out,samples=None):
 if out.exists():raise ValueError('Existing output')
 design=json.loads((ROOT/'design.json').read_text());out.mkdir(parents=True);(out/'parts').mkdir();(out/'frames').mkdir();(out/'boot-isolates').mkdir();(out/'leg-isolates').mkdir()
 parts={};info={}
 for leg,d in design['legs'].items():
  src=Image.open(ROOT/d['source']).convert('RGBA');parts[leg]={};info[leg]={}
  for name in ['thigh','shin','boot']:
   cfg=d['parts'][name];im=src.copy();alpha=im.getchannel('A');mask=Image.new('L',im.size);ImageDraw.Draw(mask).rectangle((0,cfg['source_y'][0],im.width-1,cfg['source_y'][1]),fill=255)
   from PIL import ImageChops
   im.putalpha(ImageChops.multiply(alpha,mask));sp=d['source_anchors'][cfg['pivot']];np=d['native_anchors'][cfg['pivot']]
   sv=sub(d['source_anchors'][cfg['end']],sp);nv=sub(d['native_anchors'][cfg['end']],np);scale=norm(nv)/norm(sv);a=angle(nv)-angle(sv)
   if name=='boot'and 'boot_source'in d:
    im=Image.open(ROOT/d['boot_source']).convert('RGBA');sp=d['boot_source_pivot'];a=0;scale=d['boot_source_scale']
   native=transform(im,sp,np,a,scale)
   if name=='boot'and d.get('boot_lateral_factor',1)!=1:
    factor=d['boot_lateral_factor'];native=native.transform((256,256),Image.Transform.AFFINE,(1/factor,0,np[0]*(1-1/factor),0,1,0),Image.Resampling.NEAREST,fillcolor=(0,0,0,0))
   if name in ['thigh','shin']:
    # Authored hidden dark cuff behind native art, not extracted anatomy.
    end=d['native_anchors'][cfg['end']];v=sub(end,np);u=[x/norm(v)for x in v];n=[-u[1],u[0]];center=end if name=='thigh'else np
    polygon=[(center[0]+u[0]*t+n[0]*w,center[1]+u[1]*t+n[1]*w)for t,w in [(-8,-5),(-8,5),(7,4),(7,-4)]]
    cuff=Image.new('RGBA',(256,256));ImageDraw.Draw(cuff).polygon(polygon,fill=tuple(design['hidden_cuff_rgba']));cuff.alpha_composite(native);native=cuff
   native.save(out/'parts'/f'{leg}-{name}.png');parts[leg][name]=native
   info[leg][name]={'pivot':np,'axis':nv,'native_scale':scale,'initial_registration_radians':a,'authored_hidden_cuff':name!='boot','RGBA_sha256':hashlib.sha256(native.tobytes()).hexdigest()}
  # Find visible boot ground witness at rest. Same fixed shape retained.
  boot=parts[leg]['boot'];p=boot.load();box=boot.getchannel('A').getbbox();y=box[3]-1;xs=[x for x in range(256)if p[x,y][3]>0];sole=[min(xs),y]
  d['source_registered_sole']=sole;d['rest_sole']=d.get('gait_rest_sole',sole);d['sole_offset']=sub(sole,d['native_anchors']['ankle'])
 frames=[];clips=json.loads((ROOT/'clips.json').read_text());base_y=clips['walk'].get('pelvis_base_y',143);stride=clips['walk']['root_stride'];stance=clips['walk']['stance_fraction'];timing=clips['walk']['duration_ticks'];count=samples or len(clips['walk']['keypose_phases'])
 for i in range(count):
  phase=i/count if samples else clips['walk']['keypose_phases'][i];hold=1/count if samples else(clips['walk']['keypose_phases'][i+1]if i+1<count else 1)-phase;root=[x*phase for x in stride];bob=sample_keys(clips['walk']['pelvis_bob_keys'],phase);sway=-math.sin(phase*2*math.pi)*clips['walk']['sway_amplitude'];lean=-math.sin(phase*2*math.pi)*clips['walk']['lean_amplitude_degrees'];canvas=Image.new('RGBA',(256,256));meta={'key':i,'phase':phase,'duration_ticks':timing*hold,'physical_root':root,'pelvis':{'origin':[130+sway,base_y+bob],'bob':bob,'lean_degrees':lean},'legs':{}}
  rendered={}
  for leg,d in design['legs'].items():
   local=(phase+d['phase_offset'])%1;rotated_hip=rotate(sub(d['native_anchors']['hip'],[130,143]),math.radians(lean));hip=[130+sway+rotated_hip[0],base_y+bob+rotated_hip[1]]
   # Stance cancels physical root; swing returns foot along a lifted arc.
   if local<stance:
    travel=.5*stance-local;lift=0;pitch=clips['walk']['heel_pitch']*(1-local/.10)if local<.10 else(clips['walk']['pushoff_pitch']*((local-.5)/.1)if local>.5 else 0)
   else:
    u=(local-stance)/(1-stance);travel=-.5*stance+stance*u;lift=clips['walk']['swing_lift']*math.sin(math.pi*u)**2;pitch=sample_keys(clips['walk']['swing_pitch_keys'],u)
   sole=[d['rest_sole'][0]+stride[0]*travel,d['rest_sole'][1]+stride[1]*travel-lift]
   if local>=stance:sole[0]-=d.get('forward_passing_shift',0)*math.sin(math.pi*u)**2
   a=math.radians(pitch);offset=rotate(d['sole_offset'],a);ankle=sub(sole,offset)
   boot=transform(parts[leg]['boot'],d['native_anchors']['ankle'],ankle,a)
   # No raster feedback: source-attached solepoint defines a smooth chain.
   pre_distance=norm(sub(ankle,hip));max_length=sum(d['bone_lengths']);hip_adjust=[0,0]
   if clips['walk'].get('adaptive_hip_compression',True) and pre_distance>max_length-clips['walk']['extension_margin']:
    hip_adjust=[x/pre_distance*(pre_distance-max_length+clips['walk']['extension_margin'])for x in sub(ankle,hip)];hip=[hip[j]+hip_adjust[j]for j in range(2)]
   knee,reach=ik(hip,ankle,d['bone_lengths'][0],d['bone_lengths'][1],d['bend_sign'])
   thighangle=angle(sub(knee,hip))-angle(info[leg]['thigh']['axis']);shinangle=angle(sub(ankle,knee))-angle(info[leg]['shin']['axis'])
   layer=Image.new('RGBA',(256,256));layer.alpha_composite(transform(parts[leg]['thigh'],d['native_anchors']['hip'],hip,thighangle));layer.alpha_composite(boot);layer.alpha_composite(transform(parts[leg]['shin'],d['native_anchors']['knee'],knee,shinangle));rendered[leg]=layer;layer.save(out/'leg-isolates'/f'{leg}-{i:02}.png');boot.save(out/'boot-isolates'/f'{leg}-{i:02}.png')
   box=boot.getchannel('A').getbbox();y=box[3]-1;xs=[x for x in range(256)if boot.getpixel((x,y))[3]>0]
   meta['legs'][leg]={'hip':hip,'knee':knee,'ankle':ankle,'contact':local<stance,'local_phase':local,'toe_pitch_degrees':pitch,'swing_lift':lift,'requested_sole':sole,'material_sole_source_pixel':d['source_registered_sole'],'material_sole_native_RGBA':list(parts[leg]['boot'].getpixel(tuple(d['source_registered_sole']))),'boot_material_RGBA_sha256':hashlib.sha256(boot.tobytes()).hexdigest(),'actual_sole':[min(xs),y],'reach_excess':reach,'hip_compression_adjustment':hip_adjust,'joint_angles_degrees':[math.degrees(thighangle),math.degrees(shinangle)]}
  for leg in ['right','left']:canvas.alpha_composite(rendered[leg])
  canvas.save(out/'frames'/f'{i:02}.png');meta['png']=f'frames/{i:02}.png';meta['png_sha256']=sha(out/meta['png']);frames.append(meta)
 columns=6 if count>12 else 4
 sheet=Image.new('RGB',(columns*512,math.ceil(count/columns)*538),(31,34,41));draw=ImageDraw.Draw(sheet)
 for i,m in enumerate(frames):
  im=Image.open(out/m['png']).resize((512,512),Image.Resampling.NEAREST);x=(i%columns)*512;y=(i//columns)*538;sheet.paste(im,(x,y+26),im);draw.text((x+8,y+6),f"walk{i:02} phase{m['phase']:.3f}",fill='white')
 sheet.save(out/'contact-2x.png')
 native=[Image.open(out/m['png']).convert('RGBA')for m in frames];background=[]
 for im in native:
  bg=Image.new('RGBA',im.size,(31,34,41,255));bg.alpha_composite(im);background.append(bg.convert('RGB'))
 background[0].save(out/'walk.gif',save_all=True,append_images=background[1:],duration=[round(sum(v['duration_ticks']for v in frames[:i+1])/60*1000/10)*10-round(sum(v['duration_ticks']for v in frames[:i])/60*1000/10)*10 for i in range(len(frames))],loop=0,disposal=2)
 atlas=Image.new('RGBA',(3*256,2*256))
 for i,(leg,name)in enumerate([(l,n)for l in ['right','left']for n in ['thigh','shin','boot']]):atlas.alpha_composite(parts[leg][name],((i%3)*256,(i//3)*256))
 atlas.save(out/'source-parts-atlas.png')
 manifest={'schema':'captain-authored-leg-walk/v1','canvas':[256,256],'fps':60,'duration_ticks':timing,'root_stride':stride,'ground_policy':'planar stagger perleg; physicalroot projectedXY, opaque sole witness independent','source_hashes':{p:sha(ROOT/p)for d in design['legs'].values()for p in [d['source']]+([d['boot_source']]if'boot_source'in d else[])},'renderer_sha256':sha(Path(__file__)),'design_sha256':sha(ROOT/'design.json'),'clips_sha256':sha(ROOT/'clips.json'),'part_registration':info,'registered_design':design,'frames':frames,'dense_samples':samples,'scope':'Authored conservativecomplete legparts and firstheavywalkcandidate; no art/contact approval.12 authoredkeys with fractionalholds and exact0.6stance, fractionalphysicalroot requires explicitcontactlocking.'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');archive=out/'source-bindings';archive.mkdir()
 for name in ['build.py','design.json','clips.json']:(archive/name).write_bytes((ROOT/name).read_bytes())
 print('rendered',count,'candidate frames')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'candidate-v1');p.add_argument('--samples',type=int);a=p.parse_args();build(a.output,a.samples)
