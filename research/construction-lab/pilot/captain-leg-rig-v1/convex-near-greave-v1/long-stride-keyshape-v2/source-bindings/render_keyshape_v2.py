"""New convex source master, frozen existing chain/foot poses; no old greave underneath."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,math,hashlib,importlib.util,argparse
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('frozen',BASE/'dense-v22/source-bindings/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def render(pack,out):
 if out.exists():raise ValueError('Refuse historical output')
 cfg=json.loads((ROOT/'registration.json').read_text());master=Image.open(ROOT/cfg['source']).convert('RGBA');sv=b.sub(cfg['source_ankle'],cfg['source_knee']);nv=b.sub(cfg['native_ankle'],cfg['native_knee']);scale=b.norm(nv)/b.norm(sv);a=b.angle(nv)-b.angle(sv);native=b.transform(master,cfg['source_knee'],cfg['native_knee'],a,scale);layers={}
 for name in ['cap','shell']:
  src=master.copy();mask=Image.new('L',master.size);ImageDraw.Draw(mask).rectangle((0,cfg[name+'_source_y'][0],master.width-1,cfg[name+'_source_y'][1]),fill=255);src.putalpha(ImageChops.multiply(src.getchannel('A'),mask));layer=b.transform(src,cfg['source_knee'],cfg['native_knee'],a,scale);lp=layer.load()
  for y in range(256):
   for x in range(256):
    if not lp[x,y][3]:lp[x,y]=(0,0,0,0)
  layers[name]=layer
 out.mkdir();dirs=['frames','foreground','boot-isolates','leg-isolates','parts']
 for d in dirs:(out/d).mkdir()
 for n,im in [('left-shin-source',native),('left-cap',layers['cap']),('left-shell',layers['shell'])]:im.save(out/'parts'/f'{n}.png')
 shape=json.loads((ROOT/'keyshape-v2.json').read_text());m=json.loads((pack/'manifest.json').read_text());frames=[];d=m['registered_design']['legs']['left'];thigh=Image.open(pack/'parts/left-thigh.png').convert('RGBA');palette=set(master.get_flattened_data())|{(0,0,0,0)}
 for old in m['frames']:
  f=json.loads(json.dumps(old));key=f['key'];p=f['legs']['left'];capangle=math.radians(max(-8,min(8,sum(p['joint_angles_degrees'])*.20)));q=p['local_phase'];passing=math.sin(math.pi*(q-.6)/.4)**2 if q>=.6 else 0;down=max(0,1-abs(q-shape['down_phase'])/shape['down_width']);axis=b.sub(cfg['native_ankle'],cfg['native_knee']);length=b.norm(axis);u=[v/length for v in axis];n=[-u[1],u[0]];shaped=Image.new('RGBA',(256,256));ip=layers['shell'].load();op=shaped.load()
  for yy in range(160,245):
   for xx in range(120,205):
    rel=[xx-cfg['native_knee'][0],yy-cfg['native_knee'][1]];ss=sum(rel[j]*u[j]for j in range(2));tt=sum(rel[j]*n[j]for j in range(2));belly=math.sin(math.pi*max(0,min(1,(ss-shape['axis_profile_start'])/(length-shape['axis_profile_start']))));factor=b.sample_keys(shape['transverse_profile'],max(0,min(1,ss/length)))+(shape['down_expansion']*down-shape['passing_foreshortening']*passing)*belly;skew=shape['passing_return_plane_skew']*passing*belly;st=(tt-skew)/factor;sx=round(cfg['native_knee'][0]+u[0]*ss+n[0]*st);sy=round(cfg['native_knee'][1]+u[1]*ss+n[1]*st);op[xx,yy]=ip[sx,sy]
  shin=b.transform(shaped,cfg['native_knee'],p['knee'],math.radians(p['joint_angles_degrees'][1]));shin.alpha_composite(b.transform(layers['cap'],cfg['native_knee'],p['knee'],capangle))
  collar=shaped.copy();ca=collar.getchannel('A');cp=ca.load()
  for yy in range(256):
   for xx in range(256):
    ss=(xx-cfg['native_knee'][0])*u[0]+(yy-cfg['native_knee'][1])*u[1]
    if not(shape['collar_source_axis_range'][0]<=ss<=shape['collar_source_axis_range'][1]):cp[xx,yy]=0
  collar.putalpha(ca);lp=collar.load()
  for yy in range(256):
   for xx in range(256):
    if not lp[xx,yy][3]:lp[xx,yy]=(0,0,0,0)
  shin.alpha_composite(b.transform(collar,cfg['native_knee'],p['knee'],math.radians(p['joint_angles_degrees'][1])));assert set(shin.get_flattened_data())<=palette;assert set(shin.getchannel('A').get_flattened_data())<={0,255};shin.save(out/'foreground'/f'{key:02}.png')
  # Preserve authored hidden joint backing behind source armor only in completeleg.
  cuff=Image.new('RGBA',(256,256));kn=p['knee'];an=p['ankle'];u=[v/b.norm(b.sub(an,kn))for v in b.sub(an,kn)];n=[-u[1],u[0]];poly=[(kn[0]+u[0]*t+n[0]*w,kn[1]+u[1]*t+n[1]*w)for t,w in [(-8,-5),(-8,5),(7,4),(7,-4)]];ImageDraw.Draw(cuff).polygon(poly,fill=(24,25,31,255));cuff.alpha_composite(shin)
  boot=Image.open(pack/'boot-isolates'/f'left-{key:02}.png').convert('RGBA');near=b.transform(thigh,d['native_anchors']['hip'],p['hip'],math.radians(p['joint_angles_degrees'][0]));near.alpha_composite(boot);near.alpha_composite(cuff);near.save(out/'leg-isolates'/f'left-{key:02}.png');far=Image.open(pack/'leg-isolates'/f'right-{key:02}.png').convert('RGBA');far.save(out/'leg-isolates'/f'right-{key:02}.png');full=far.copy();full.alpha_composite(near);full.save(out/'frames'/f'{key:02}.png')
  for leg in ['left','right']:Image.open(pack/'boot-isolates'/f'{leg}-{key:02}.png').save(out/'boot-isolates'/f'{leg}-{key:02}.png')
  f['png_sha256']=sha(out/f['png']);f['foreground']={'png':f'foreground/{key:02}.png','png_sha256':sha(out/'foreground'/f'{key:02}.png'),'cap_angle_degrees':math.degrees(capangle),'shell_keyshape':{'passing':passing,'down':down},'source_palette_only':True,'binary_alpha':True};frames.append(f)
 samples=[0,7,18,24,36,54];sheet=Image.new('RGBA',(1536,1080),(31,34,41,255));dr=ImageDraw.Draw(sheet)
 for k,i in enumerate(samples):
  im=Image.open(out/'frames'/f'{i:02}.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST);x=k%3*512;y=k//3*540;sheet.alpha_composite(im,(x,y+20));dr.text((x+8,y+8),f'newconvexgreave key{i:02}',fill='white')
 sheet.save(out/'representative-2x.png');m['frames']=frames;m['parent_pose_manifest_sha256']=sha(pack/'manifest.json');m['source_hashes'][cfg['source']]=sha(ROOT/cfg['source']);m['renderer_sha256']=sha(Path(__file__));m['design_sha256']=sha(ROOT/'registration.json');m['keyshape_descriptor_sha256']=sha(ROOT/'keyshape-v2.json');m['source_registration']={'scale':scale,'angle_radians':a,'configuration':cfg,'native_RGBA_sha256':hashlib.sha256(native.tobytes()).hexdigest()};m['scope']='Newauthored convexneargreave MASTER replacesoldshin completely, separatecamera-facingcap andauthored localizeddown/pass barrel shell, frozenparentposechain/boots/timing; no artapproval. Foregroundexcludeshidden cuff. No newperframeart.';(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');sb=out/'source-bindings';sb.mkdir()
 for n in ['render_keyshape_v2.py','registration.json','keyshape-v2.json']:(sb/n).write_bytes((ROOT/n).read_bytes())
 print('rendered72 newconvexgreave, parentbones/boots unchanged')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,default=BASE/'stride-pose-probe/dense-mean149');p.add_argument('--output',type=Path,default=ROOT/'long-stride-keyshape-v2');args=p.parse_args();render(args.pack,args.output)
