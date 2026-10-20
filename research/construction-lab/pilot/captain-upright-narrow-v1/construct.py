from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def mask(poly):
 im=Image.new('L',(256,256));ImageDraw.Draw(im).polygon(poly,fill=255);return im
def owned(src,m):
 im=src.copy();im.putalpha(ImageChops.multiply(src.getchannel('A'),m));im.putdata([p if p[3] else(0,0,0,0)for p in im.get_flattened_data()]);return im
def construct(out):
 cfg=json.loads((ROOT/'design.json').read_text());assert sha(ROOT/cfg['source'])==cfg['source_sha256'],'Source SHA precondition failed';src=Image.open(ROOT/cfg['source']).convert('RGBA');used=Image.new('L',src.size);pieces={}
 for name in cfg['source_ownership_priority']:
  poly=cfg['legs'][name.split('_')[0]]['polygon']if name.endswith('_leg')else cfg['polygons'][name]
  m=ImageChops.subtract(mask(poly),used);used=ImageChops.lighter(used,m);pieces[name]=owned(src,m)
 pieces['torso']=owned(src,ImageChops.invert(used));rest=Image.new('RGBA',src.size)
 for im in pieces.values():rest.alpha_composite(im)
 assert rest.tobytes()==src.tobytes()
 out.mkdir(parents=True,exist_ok=True);(out/'source-owned').mkdir(exist_ok=True);(out/'complete').mkdir(exist_ok=True)
 for n,im in pieces.items():im.save(out/'source-owned'/f'{n}.png')
 colors={n:src.getpixel(tuple(p))for n,p in cfg['hidden_palette_sample_points'].items()};assert all(c[3]==255 for c in colors.values());parts={n:p for n,p in pieces.items()if not n.endswith('_leg')};joint_records=[]
 arm=parts.pop('arm_sword');am=mask(cfg['sword_upper_arm_polygon']);parts['sword_upper_arm']=owned(arm,am);parts['sword_forearm']=owned(arm,ImageChops.invert(am));check=parts['sword_upper_arm'].copy();check.alpha_composite(parts['sword_forearm']);assert check.tobytes()==arm.tobytes()
 cm=Image.new('L',src.size);ImageDraw.Draw(cm).rectangle((0,0,255,104),fill=255);torso=parts.pop('torso');parts['chest']=owned(torso,cm);parts['waist']=owned(torso,ImageChops.invert(cm))
 for leg,d in cfg['legs'].items():
  legsrc=pieces[leg+'_leg'];hip=d['hip'];kn=d['knee'];an=d['ankle']
  for name,lo,hi in [('thigh',0,d['thigh_shin_cut_y']),('shin',d['thigh_shin_cut_y']+1,d['shin_boot_cut_y']),('boot',d['shin_boot_cut_y']+1,255)]:
   m=Image.new('L',src.size);ImageDraw.Draw(m).rectangle((0,lo,255,hi),fill=255);source=owned(legsrc,m);back=Image.new('RGBA',src.size);draw=ImageDraw.Draw(back)
   if name=='thigh':
    # Complete concealed hip-to-knee tube, deliberately conservative underlap.
    import math
    vx,vy=kn[0]-hip[0],kn[1]-hip[1];length=math.hypot(vx,vy);nx,ny=-vy/length,vx/length;w=d['thigh_width'];poly=[(hip[0]+nx*w,hip[1]+ny*w),(hip[0]-nx*w,hip[1]-ny*w),(kn[0]-nx*7,kn[1]-ny*7),(kn[0]+nx*7,kn[1]+ny*7)];draw.polygon(poly,fill=colors['dark_red']);draw.line((hip[0]+nx*w,hip[1]+ny*w,kn[0]+nx*7,kn[1]+ny*7),fill=colors['edge'],width=2)
   if name=='shin':
    # New declared distal flex/cuff underlap; constant source-space geometry.
    import math
    vx,vy=an[0]-kn[0],an[1]-kn[1];ln=math.hypot(vx,vy);ux,uy=vx/ln,vy/ln;nx,ny=-uy,ux;w=9 if leg=='far'else 8
    distal=[(an[0]+ux*t+nx*sw,an[1]+uy*t+ny*sw)for t,sw in [(-15,-w),(-15,w),(6,w-2),(6,-w+2)]];draw.polygon(distal,fill=colors['joint'])
    draw.polygon([(kn[0]-6,kn[1]-10),(kn[0]+6,kn[1]-10),(kn[0]+6,kn[1]+5),(kn[0]-6,kn[1]+5)],fill=colors['joint'])
   if name=='boot':draw.polygon([(an[0]-6,an[1]-12),(an[0]+6,an[1]-12),(an[0]+7,an[1]+3),(an[0]-7,an[1]+3)],fill=colors['joint'])
   back.alpha_composite(source);parts[leg+'_'+name]=back;source.save(out/'source-owned'/f'{leg}_{name}.png');parts[leg+'_'+name+'_source']=source;joint_records.append({'part':leg+'_'+name,'new_hidden_pixels':sum(a[3]>0 and b[3]==0 for a,b in zip(back.get_flattened_data(),source.get_flattened_data()))})
 for n,im in parts.items():im.save(out/'complete'/f'{n}.png')
 rest.save(out/'source-rest.png');report={'source_sha256':sha(ROOT/cfg['source']),'design_sha256':sha(ROOT/'design.json'),'source_only_rest_recomposition_RGBA_exact':True,'source_owned_masks_disjoint':True,'hidden_pixels_declared':joint_records,'hidden_colors':colors,'anchors_inspected_from_new_master_not_inherited':True};(out/'construction-receipt.json').write_text(json.dumps(report,indent=2)+'\n');return cfg,parts,report
if __name__=='__main__':construct(ROOT/'artifacts/parts-v1')
