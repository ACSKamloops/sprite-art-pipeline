"""New source-owned upright rig; source joints, no old crouched-pose metadata."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,json,hashlib,argparse
import construct,pixel_affine
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sub(a,b):return[a[i]-b[i]for i in range(2)]
def rotate(v,a):
 a=math.radians(a);return[v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a)]
def point(p,o,t,a):return[t[i]+rotate(sub(p,o),a)[i]for i in range(2)]
def angle(v):return math.degrees(math.atan2(v[1],v[0]))
def knee(h,a,l):
 v=sub(a,h);dist=math.hypot(*v);assert dist<sum(l),(h,a,dist,l)
 z=(l[0]**2-l[1]**2+dist**2)/(2*dist);p=math.sqrt(max(0,l[0]**2-z*z));return[h[0]+z*v[0]/dist-p*v[1]/dist,h[1]+z*v[1]/dist+p*v[0]/dist]
def sample(keys,q):
 q%=1
 for a,b in zip(keys,keys[1:]):
  if a['phase']<=q<=b['phase']:
   t=(q-a['phase'])/(b['phase']-a['phase']);p={}
   for name in ['pelvis','far_sole','near_sole']:p[name]=[a[name][j]+(b[name][j]-a[name][j])*t for j in range(2)]
   for name in ['lean','chest_counter','chest_drop','forearm_carry','far_pitch','near_pitch']:p[name]=a[name]+(b[name]-a[name])*t
   p['support']='far'if q<.5 else'near';return p
 raise ValueError(q)
def rigid(im,o,t,a):return pixel_affine.affine(im,o,t,a)
def pose(cfg,parts,motion,q):
 p=sample(motion['keys'],q);pelvis=p['pelvis'];lean=p['lean'];layers={};meta={'pelvis':pelvis,'support':p['support'],'physical_root':[q*x for x in motion['root_stride']],'legs':{},'upper':{}}
 for leg,d in cfg['legs'].items():
  hip=point(d['hip'],cfg['pelvis_rest'],pelvis,lean);sole=p[leg+'_sole'];source_contact=cfg['boot_contact_source_points'][leg];offset=rotate(sub(source_contact,d['ankle']),p[leg+'_pitch']);ankle=sub(sole,offset);lengths=[math.dist(d['hip'],d['knee']),math.dist(d['knee'],d['ankle'])];kn=knee(hip,ankle,lengths);ta=angle(sub(kn,hip))-angle(sub(d['knee'],d['hip']));sa=angle(sub(ankle,kn))-angle(sub(d['ankle'],d['knee']))
  layers[leg+'_thigh']=rigid(parts[leg+'_thigh'],d['hip'],hip,ta);layers[leg+'_shin']=rigid(parts[leg+'_shin'],d['knee'],kn,sa);layers[leg+'_boot']=rigid(parts[leg+'_boot'],d['ankle'],ankle,p[leg+'_pitch'])
  if leg=='near':layers['near_shin_foreground']=rigid(parts['near_shin_source'],d['knee'],kn,sa)
  cosine=(lengths[0]**2+lengths[1]**2-math.dist(hip,ankle)**2)/(2*lengths[0]*lengths[1]);flex=180-math.degrees(math.acos(max(-1,min(1,cosine))))
  meta['legs'][leg]={'hip':hip,'knee':kn,'ankle':ankle,'bone_lengths':lengths,'reach_distance':math.dist(hip,ankle),'knee_flex_degrees':flex,'sole_source_point':source_contact,'sole_world_target':[sole[j]+meta['physical_root'][j]for j in range(2)],'sole_local_target':sole,'stance':p['support']==leg,'swing_clearance':source_contact[1]-sole[1],'boot_angle':p[leg+'_pitch'],'shin_angle':sa,'thigh_angle':ta,'no_adaptive_hip_shift':True}
 waist_pivot=cfg['pelvis_rest'];hinge=cfg['chest_hinge'];chesttarget=point(hinge,waist_pivot,pelvis,lean);chesttarget[1]+=p['chest_drop'];chestangle=lean+p['chest_counter'];layers['waist']=rigid(parts['waist'],waist_pivot,pelvis,lean);layers['chest']=rigid(parts['chest'],hinge,chesttarget,chestangle)
 backing=Image.new('RGBA',(256,256));d=ImageDraw.Draw(backing);src=Image.open(ROOT/cfg['source']);col=src.getpixel(tuple(cfg['hidden_palette_sample_points']['dark_red']));d.polygon([(124,65),(149,65),(152,82),(122,82)],fill=col);d.polygon([(106,88),(115,88),(118,107),(103,107)],fill=col);d.polygon([(114,98),(145,98),(146,110),(113,110)],fill=col);layers['joint_backing']=rigid(backing,hinge,chesttarget,chestangle)
 shoulder=point(cfg['anchors']['sword_shoulder'],hinge,chesttarget,chestangle);upperangle=chestangle-0.6*p['forearm_carry'];elbow=point(cfg['anchors']['sword_elbow'],cfg['anchors']['sword_shoulder'],shoulder,upperangle);foreangle=upperangle+p['forearm_carry'];wrist=point(cfg['anchors']['sword_wrist'],cfg['anchors']['sword_elbow'],elbow,foreangle);layers['sword_upper_arm']=rigid(parts['sword_upper_arm'],cfg['anchors']['sword_shoulder'],shoulder,upperangle);layers['sword_forearm']=rigid(parts['sword_forearm'],cfg['anchors']['sword_elbow'],elbow,foreangle);meta['upper']['sword_arm']={'shoulder':shoulder,'elbow':elbow,'wrist':wrist,'upper_arm_angle':upperangle,'forearm_angle':foreangle,'sword_grip_is_one_source_cluster':True}
 for name in ['head','shield','cape','tabard','backpack_halo']:
  o=cfg['anchors'][name];owner_chest=name in ['head','shield','backpack_halo'];t=point(o,hinge,chesttarget,chestangle)if owner_chest else point(o,waist_pivot,pelvis,lean);a=0 if name=='head'else(chestangle if name=='backpack_halo'else chestangle-.6*p['forearm_carry']if name=='shield'else lean+(1.2 if name=='cape'else .6)*math.sin(2*math.pi*(q-.1)));layers[name]=rigid(parts[name],o,t,a);meta['upper'][name]={'pivot':t,'angle':a,'owner':'chest'if owner_chest else'waist'}
 meta['upper']['chest']={'hinge':chesttarget,'angle':chestangle,'compression':p['chest_drop']};return layers,meta
ORDER=['cape','backpack_halo','far_thigh','far_boot','far_shin','near_thigh','near_boot','near_shin','joint_backing','sword_upper_arm','sword_forearm','waist','chest','head','tabard','near_shin_foreground','shield']
def render(out,keys_only=False,motion_path=None):
 if out.exists():raise ValueError('Refuse historical outputs')
 out.mkdir(parents=True);cfg,parts,construction=construct.construct(out/'parts');motion_path=Path(motion_path or ROOT/'motion.json');motion=json.loads(motion_path.read_text());(out/'frames').mkdir();(out/'layers').mkdir();count=8 if keys_only else motion['dense_frames'];frames=[]
 for i in range(count):
  q=i/count;layers,meta=pose(cfg,parts,motion,q);canvas=Image.new('RGBA',(256,256))
  for name in ORDER:layers[name].save(out/'layers'/f'{i:02}-{name}.png');canvas.alpha_composite(layers[name])
  canvas.save(out/'frames'/f'{i:02}.png');meta.update({'frame':i,'phase':q,'file':f'frames/{i:02}.png','sha256':sha(out/'frames'/f'{i:02}.png'),'duration_ms':motion['duration_ms']/count,'bbox':canvas.getbbox()});frames.append(meta)
 selected=list(range(8))if keys_only else[0,9,18,27,36,45,54,63];sheet=Image.new('RGBA',(1024,560),(35,38,44,255));dr=ImageDraw.Draw(sheet)
 for j,i in enumerate(selected):
  im=Image.open(out/'frames'/f'{i:02}.png');xy=(j%4*256,j//4*280);sheet.alpha_composite(im,xy);dr.text((xy[0]+4,xy[1]+258),motion['keys'][j]['name'],fill='white')
 sheet.convert('RGB').save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).convert('RGB').save(out/'eight-keys-2x.png');movie=[]
 for f in frames:
  bg=Image.new('RGBA',(256,256),(35,38,44,255));bg.alpha_composite(Image.open(out/f['file']));movie.append(bg.convert('RGB'))
 holds=[round((i+1)*motion['duration_ms']/count/10)*10-round(i*motion['duration_ms']/count/10)*10 for i in range(count)];movie[0].save(out/'loop.gif',save_all=True,append_images=movie[1:],duration=holds,loop=0,disposal=2)
 manifest={'status':'UNAPPROVED_UPRIGHT_CONSTRUCTION_TRIAL','source_sha256':sha(ROOT/cfg['source']),'design_sha256':sha(ROOT/'design.json'),'motion_sha256':sha(motion_path),'renderer_sha256':sha(Path(__file__)),'construction_sha256':sha(ROOT/'construct.py'),'pixel_affine_sha256':sha(ROOT/'pixel_affine.py'),'canvas':[256,256],'cycle_ms':motion['duration_ms'],'frames':frames,'layer_order':ORDER,'construction':construction,'limitations':['One authored three-quarter view; no four-view claim.','Boots flat during stance, modest authored swing pitch; no measured heel/toe roll.','Analytic targets are not measured pixel/GPU contacts.','Occluded thigh/cuff anatomy is newly authored backing, not recovered.','Rigid greaves and split arm pieces are not skeletal skinning.']};(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(out)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/key-trial-v1');p.add_argument('--keys-only',action='store_true');p.add_argument('--motion',type=Path);a=p.parse_args();render(a.output.resolve(),a.keys_only,a.motion)
