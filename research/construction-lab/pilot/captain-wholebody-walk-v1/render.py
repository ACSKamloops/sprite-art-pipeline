"""Independent wholebody eight-key source-part trial. No old pose/cadence reuse."""
from pathlib import Path
import json,math,hashlib,importlib.util,argparse,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sub(a,b):return[a[i]-b[i]for i in range(2)]
def angle(v):return math.atan2(v[1],v[0])
def rotate(v,a):return[v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a)]
def transform(im,p,t,a):
 c,s=math.cos(a),math.sin(a)
 return im.transform((256,256),Image.Transform.AFFINE,(c,s,p[0]-c*t[0]-s*t[1],-s,c,p[1]+s*t[0]-c*t[1]),Image.Resampling.NEAREST,fillcolor=(0,0,0,0))
def knee(h,a,l):
 v=sub(a,h);d=math.hypot(*v);assert d<sum(l),(h,a,d,l)
 x=(l[0]**2-l[1]**2+d*d)/(2*d);y=math.sqrt(max(0,l[0]**2-x*x));return[h[0]+x*v[0]/d-y*v[1]/d,h[1]+x*v[1]/d+y*v[0]/d]
def sample(keys,q):
 q=q%1
 for a,b in zip(keys,keys[1:]):
  if a['phase']<=q<=b['phase']:
   t=(q-a['phase'])/(b['phase']-a['phase']);out={}
   for name in ['pelvis','right_sole','left_sole']:out[name]=[a[name][i]+(b[name][i]-a[name][i])*t for i in range(2)]
   for name in ['lean','chest_counter']:out[name]=a[name]+(b[name]-a[name])*t
   out['support']='right'if q<.5 else'left';return out
 raise ValueError(q)
def render(out):
 if out.exists():raise ValueError('Refuse old output')
 out.mkdir(parents=True);snapshot=out/'upper-source';shutil.copytree(ROOT/'source/upper',snapshot,ignore=shutil.ignore_patterns('parts','__pycache__','upper-rest.png','partition-proof.json'));cfg=json.loads((ROOT/'motion.json').read_text());spec=importlib.util.spec_from_file_location('upper_trial',ROOT/'source/upper/build.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u);u.ROOT=snapshot;design,upper=u.construct();design['rotation_method']='scale2x8-approximation';design['motion_profile']='weighted'
 parts={p.stem:Image.open(p).convert('RGBA')for p in(ROOT/'source/parts').glob('*.png')};(out/'frames').mkdir();(out/'layers').mkdir();frames=[];order=['cape','legs','joint_backing','arm_sword','torso_pack','head','tabard','near_shin_foreground','shield'];palette=set()
 for im in parts.values():palette.update(im.get_flattened_data())
 palette.update(Image.open(ROOT/'source/upper/source/approved-256.png').convert('RGBA').get_flattened_data());palette.update([(0,0,0,0),(34,17,22,255),(32,20,24,255),(58,18,24,255),(24,25,31,255)])
 for i in range(72):
  q=i/72;pose=sample(cfg['keys'],q);leglayers={};marks={};nearfore=None
  for side in ['right','left']:
   hip=[pose['pelvis'][j]+rotate(cfg['hips_local'][side],math.radians(pose['lean']))[j]for j in range(2)];sole=pose[side+'_sole'];ankle=sub(sole,cfg['boot_sole_offsets'][side]);kn=knee(hip,ankle,cfg['lengths'][side]);resthip=[112,145]if side=='right'else[147,160];restknee=[100,169]if side=='right'else[158,184];restankle=cfg['boot_ankles'][side];ta=angle(sub(kn,hip))-angle(sub(restknee,resthip));sa=angle(sub(ankle,kn))-angle(sub(restankle,restknee));thigh=transform(parts[side+'-thigh'],resthip,hip,ta);boot=transform(parts[side+'-boot'],restankle,ankle,0)
   if side=='right':shin=transform(parts['right-shin'],restknee,kn,sa)
   else:
    # Fixed source-space convex shell retains bulk; cap has partial joint follow.
    shell=parts['left-shell'];axis=sub(restankle,restknee);n=math.hypot(*axis);ax=[v/n for v in axis];tr=[-ax[1],ax[0]];f=1.28;aa=ax[0]**2+tr[0]**2/f;bb=ax[0]*ax[1]+tr[0]*tr[1]/f;dd=ax[1]**2+tr[1]**2/f;x,y=restknee;shell=shell.transform((256,256),Image.Transform.AFFINE,(aa,bb,x-aa*x-bb*y,bb,dd,y-bb*x-dd*y),Image.Resampling.NEAREST)
    shin=transform(shell,restknee,kn,sa);shin.alpha_composite(transform(parts['left-cap'],restknee,kn,.2*ta+.5*sa));nearfore=shin.copy()
   layer=thigh.copy();layer.alpha_composite(boot);layer.alpha_composite(shin);leglayers[side]=layer
   marks[side]={'hip':hip,'knee':kn,'ankle':ankle,'sole_source_attached_target':sole,'support':pose['support']==side,'swing_clearance':(224 if side=='right'else 242)-sole[1],'reach_distance':math.dist(hip,ankle),'maximum_chain':sum(cfg['lengths'][side]),'thigh_rotation_degrees':math.degrees(ta),'shin_rotation_degrees':math.degrees(sa),'boot_angle_degrees':0}
  u.load_state=lambda _d,_q:(abs(pose['chest_counter'])/1.5,pose['chest_counter']/1.5)
  layers,um=u.render_parts(design,upper,q,pose['pelvis'],pose['lean']);layers['legs']=leglayers['right'].copy();layers['legs'].alpha_composite(leglayers['left']);layers['near_shin_foreground']=nearfore
  whole=Image.new('RGBA',(256,256))
  for name in order:layers[name].save(out/'layers'/f'{i:02}-{name}.png');whole.alpha_composite(layers[name])
  assert set(whole.getchannel('A').get_flattened_data())<={0,255};assert set(whole.get_flattened_data())<=palette
  box=whole.getbbox();assert box[0]>0 and box[1]>0 and box[2]<256 and box[3]<256
  whole.save(out/'frames'/f'{i:02}.png');frames.append({'frame':i,'phase':q,'duration_ms':1200/72,'pose':pose,'legs':marks,'upper':um,'physical_root':[v*q for v in cfg['root_stride']],'png':f'frames/{i:02}.png','sha256':sha(out/'frames'/f'{i:02}.png')})
 sheet=Image.new('RGB',(4*256,2*280),(35,38,44));d=ImageDraw.Draw(sheet)
 for j,i in enumerate([0,9,18,27,36,45,54,63]):
  im=Image.open(out/'frames'/f'{i:02}.png');xy=(j%4*256,j//4*280);sheet.paste(im,xy,im);d.text((xy[0]+4,xy[1]+258),cfg['keys'][j]['name'],fill='white')
 sheet.save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png')
 movie=[]
 for f in frames:
  im=Image.new('RGBA',(256,256),(35,38,44,255));im.alpha_composite(Image.open(out/f['png']));movie.append(im.convert('RGB'))
 holds=[round((i+1)*120/72)*10-round(i*120/72)*10 for i in range(72)];movie[0].save(out/'loop.gif',save_all=True,append_images=movie[1:],duration=holds,loop=0,disposal=2)
 (out/'manifest.json').write_text(json.dumps({'status':'UNAPPROVED_NEW_WHOLEBODY_MOTION_TRIAL','canvas':[256,256],'cycle_ms':1200,'frames':frames,'source_hashes':{str(p.relative_to(ROOT)):sha(p)for p in (ROOT/'source').rglob('*')if p.is_file()and '__pycache__'not in str(p)and not any(n in p.parts for n in ['__pycache__']) and p.name not in ['upper-rest.png','partition-proof.json'] and not ('upper' in p.parts and 'parts' in p.parts)},'motion_sha256':sha(ROOT/'motion.json'),'renderer_sha256':sha(Path(__file__)),'layer_order':order,'limitations':['Boots intentionally flat throughout support; this does not implement heel/toe roll.','No movingworld material-plant GPU certificate.','Single three-quarter source view.','Rigid source armor turns are limited viewpoint approximations; no new anatomy is inferred.','Hard contact phase transitions and linearly authored keys require temporal review.']},indent=2)+'\n')
 print(out)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/trial-v1');render(p.parse_args().output.resolve())
