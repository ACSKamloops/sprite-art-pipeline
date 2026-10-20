"""Depth-guided painted planes. Authored source binding; no full3D armor claim."""
from pathlib import Path
import json,math,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent;R=P.parent/'captain-upright-rig-v1';sys.path.insert(0,str(R));import construct
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CFG={'far':{'hip':[49,10],'knee':[44,43],'ankle':[43,104],'heel':[58,118],'toe':[20,121],'cuts':[37,90]},'near':{'hip':[82,10],'knee':[89,46],'ankle':[104,103],'heel':[112,107],'toe':[99,118],'cuts':[40,89]}}
def warp(im,M,origin,target):
 inv=np.linalg.inv(M);offset=np.asarray(origin)-inv@np.asarray(target);coef=tuple(inv[0])+tuple([offset[0]])+tuple(inv[1])+tuple([offset[1]])
 return im.transform((256,256),Image.Transform.AFFINE,coef,Image.Resampling.NEAREST)
def unit(v):return np.asarray(v)/np.linalg.norm(v)
def make_parts(out):
 src=Image.open(P/'source/leg-master-128.png').convert('RGBA');mask=Image.new('L',src.size);ImageDraw.Draw(mask).polygon([(0,0),(62,0),(64,40),(68,128),(0,128)],fill=255);masks={'far':mask,'near':ImageChops.invert(mask)};parts={};recomposed=Image.new('RGBA',src.size);(out/'parts').mkdir()
 for n,c in CFG.items():
  leg=src.copy();leg.putalpha(ImageChops.multiply(src.getchannel('A'),masks[n]));recomposed.alpha_composite(leg)
  a,b=c['cuts']
  for part,lo,hi in [('thigh',0,a),('shin',a+1,b),('boot',b+1,127)]:
   selection=Image.new('L',src.size);ImageDraw.Draw(selection).rectangle((0,lo,127,hi),fill=255);im=leg.copy();im.putalpha(ImageChops.multiply(leg.getchannel('A'),selection));im.putdata([x if x[3] else(0,0,0,0)for x in im.get_flattened_data()]);im.save(out/'parts'/f'{n}_{part}-visible.png')
   # Declared joint underlaps authored separately from the exact source partitions.
   if part!='boot':
    hidden=Image.new('RGBA',src.size);d=ImageDraw.Draw(hidden);k=c['knee']if part=='thigh'else c['ankle'];d.rectangle((k[0]-5,k[1]-8,k[0]+5,k[1]+5),fill=(30,30,32,255));hidden.alpha_composite(im);im=hidden
   parts[n+'_'+part]=im
 assert recomposed.getchannel('A').tobytes()==src.getchannel('A').tobytes()
 return parts

def bone_matrix(s,e,w0,w1,cam,transverse):
 v=np.asarray(e)-np.asarray(s);sourceB=np.column_stack(([v[1],-v[0]],v))/np.linalg.norm(v);bone=np.asarray(w1)-w0;U=unit(transverse-unit(bone)*np.dot(transverse,unit(bone)));U=-U if (cam@U)[0]<0 else U;projectedU=cam@U
 # One bind calibration for each projected plane width. No per-frame pixel fitting.
 A=np.column_stack((projectedU/.8,(cam@bone)/np.linalg.norm(v)));return A@np.linalg.inv(sourceB)
def main():
 out=P/'artifacts/trial-v1-replay';assert not out.exists(),'Preserve historical trials';out.mkdir(parents=True);(out/'frames').mkdir();parts=make_parts(out);cfg,upper,_=construct.construct(out/'upper-parts');packet=json.loads((P/'source/authored-poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);T=np.array(packet['camera']['transverse']);frames=[];sheet=Image.new('RGBA',(1024,560),(35,38,44,255));dr=ImageDraw.Draw(sheet)
 for i,f in enumerate(packet['frames']):
  root=np.array(f['physical_root_pixels']);layers={};anchorerrors=[]
  for n,c in CFG.items():
   leg=f['legs'][n];w=leg['world'];pix={k:np.array(v)-root for k,v in leg['pixels'].items()}
   for part,start,end in [('thigh','hip','knee'),('shin','knee','ankle')]:
    M=bone_matrix(c[start],c[end],np.array(w[start]),np.array(w[end]),cam,T);layers[n+'_'+part]=warp(parts[n+'_'+part],M,c[start],pix[start]);anchorerrors.append(float(np.linalg.norm(M@(np.array(c[end])-c[start])+pix[start]-pix[end])))
   sourceA=np.column_stack((np.array(c['heel'])-c['ankle'],np.array(c['toe'])-c['ankle']));targetA=np.column_stack((pix['heel']-pix['ankle'],pix['toe']-pix['ankle']));M=targetA@np.linalg.inv(sourceA);layers[n+'_boot']=warp(parts[n+'_boot'],M,c['ankle'],pix['ankle']);anchorerrors.extend(float(np.linalg.norm(M@(np.array(c[k])-c['ankle'])+pix['ankle']-pix[k]))for k in ['heel','toe'])
  pelvis=np.array(f['upper_pixels']['pelvis'])-root;chest=np.array(f['upper_pixels']['chest'])-root;angle=f['chest_counterrotation_degrees'];rad=math.radians(angle);rotation=np.array([[math.cos(rad),-math.sin(rad)],[math.sin(rad),math.cos(rad)]]);I=np.eye(2)
  for n in ['cape','tabard','waist']:
   o=cfg['pelvis_rest'];layers[n]=warp(upper[n],I,o,pelvis)
  for n in ['chest','head','shield','backpack_halo','sword_upper_arm','sword_forearm']:
   layers[n]=warp(upper[n],I if n=='head'else rotation,cfg['chest_hinge'],chest)
  backing=Image.new('RGBA',(256,256));draw=ImageDraw.Draw(backing);draw.rectangle((121,100,147,133),fill=(45,18,22,255));layers['joint_backing']=warp(backing,I,cfg['pelvis_rest'],pelvis)
  order=['cape','backpack_halo','far_thigh','far_shin','far_boot','near_thigh','near_shin','near_boot','joint_backing','sword_upper_arm','sword_forearm','waist','chest','head','tabard','shield'];im=Image.new('RGBA',(256,256))
  for n in order:im.alpha_composite(layers[n])
  path=out/'frames'/f'{i:03}.png';im.save(path);frames.append({'index':i,'file':f'frames/{i:03}.png','sha256':sha(path),'duration_ms':f['duration_ms'],'phase_label':f"3D guide phase {f['phase']:.4f}; far {f['legs']['far']['foot']['role']}, near {f['legs']['near']['foot']['role']}",'physical_root':list(root),'max_projected_anchor_error':max(anchorerrors)})
  if i%9==0:
   j=i//9;xy=(j%4*256,j//4*280);sheet.alpha_composite(im,xy);dr.text((xy[0]+4,xy[1]+258),f'frame{i} / source planes',fill='white')
 sheet.convert('RGB').save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).convert('RGB').save(out/'eight-keys-2x.png');spec={'schema':'motion-audition/v1','name':'UNAPPROVED depth-guided painted-plane trial','canvas':[256,256],'stage':[768,640],'origin':[96,80],'cycle_ms':1200,'root_stride':list(cam@packet['dimensions']['stride_world']),'root_policy':'in_place','camera':'fixed','frames':frames};(out/'audition.json').write_text(json.dumps(spec,indent=2)+'\n');(out/'binding.json').write_text(json.dumps({'state':'UNAPPROVED_2_5D_PAINTED_PLANES','source_leg_sha256':sha(P/'source/leg-master-128.png'),'pose_packet_sha256':sha(P/'source/authored-poses.json'),'source_anchors':CFG,'max_projected_anchor_error':max(x['max_projected_anchor_error']for x in frames),'limitations':['3D bone geometry supplies projection; painted parts are planar source images, not complete3D shells','Authored source landmarks, widths and dark underlaps have not been externally validated','Source boot images mapped to3projected guide anchors; actual pixel material contacts unmeasured','Single source view; no back surfaces or direction library','Perfect continuous anchors do not imply correct sprite joint overlap or art quality']},indent=2)+'\n');print(out)
if __name__=='__main__':main()
