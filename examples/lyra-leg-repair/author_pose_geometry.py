"""Authored projected gait, stable painted parts, explicit inverse pixel witnesses."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parent
import argparse
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
D=args.output.absolute();assert not D.exists(),'Fresh output required';D.mkdir(parents=True);(D/'parts').mkdir();(D/'layers').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={'P':np.array(Image.open(R/'candidate-v1/04.png').convert('RGBA')),'Q':np.array(Image.open(R/'candidate-v1/00.png').convert('RGBA'))}
polys={
'P-cloth':[(53,81),(64,81),(67,85),(66,91),(63,94),(53,93),(51,87)],
'P-calf':[(53,90),(66,90),(68,96),(66,104),(52,104),(51,96)],
'P-foot':[(53,101),(58,99),(64,100),(69,104),(70,109),(66,113),(55,113),(51,109),(51,104)],
'Q-cloth':[(65,81),(77,81),(81,86),(81,91),(77,95),(67,94),(64,88)],
'Q-calf':[(65,90),(81,90),(83,98),(83,107),(65,107),(64,98)],
'Q-foot':[(66,103),(76,101),(85,104),(91,109),(91,114),(86,117),(72,117),(65,113),(64,106)]}
parts={}
for name,poly in polys.items():
 mask=Image.new('L',(128,128));ImageDraw.Draw(mask).polygon(poly,fill=255);mask=np.array(mask)>0;src=sources[name[0]].copy();src[~mask]=0
 parts[name]=(src,mask);Image.fromarray(src).save(D/'parts'/(name+'.png'));Image.fromarray(mask.astype('uint8')*255).save(D/'parts'/(name+'-owner.png'))
# Foot anchor paths are authored screen projections, not recovered joints/world contacts.
soles={'P':[[54,106],[55,103],[58,104],[61,109],[62,112],[60,111],[58,109],[56,108]],'Q':[[79,115],[77,113],[75,111],[72,108],[70,105],[72,103],[75,105],[78,111]]}
cuffs={'P':[[53,91],[55,88],[60,87],[62,91],[61,94],[59,93],[56,92],[54,91]],'Q':[[74,94],[73,93],[71,92],[71,89],[74,87],[75,85],[76,87],[77,91]]}
pitches={'P':[7,-3,-4,-5,-4,0,0,3],'Q':[-4,0,0,3,7,-3,-4,-5]}
masters={'P':{'hip':[60,81],'cuff':[60,93],'ankle':[60,102],'sole':[62,111],'half':7,'cloth_y':[80,86,94],'calf_y':[90,97,104]},'Q':{'hip':[72,81],'cuff':[73,94],'ankle':[76,105],'sole':[79,115],'half':9,'cloth_y':[80,86,95],'calf_y':[90,98,108]}}
def warp(src,mask,sv,tv):
 sv=np.array(sv,float);tv=np.array(tv,float);out=np.zeros_like(src);witness=np.full((128,128,2),-1,np.int16)
 for ids in [(0,1,2),(1,3,2),(2,3,4),(3,5,4)]:
  ss=sv[list(ids)];tt=tv[list(ids)];mat=np.vstack([tt.T,np.ones(3)]);assert abs(np.linalg.det(mat))>1e-6
  inv=np.linalg.inv(mat);lo=np.maximum(0,np.floor(tt.min(0)).astype(int));hi=np.minimum(127,np.ceil(tt.max(0)).astype(int))
  for y in range(lo[1],hi[1]+1):
   for x in range(lo[0],hi[0]+1):
    b=inv@np.array([x,y,1.]);
    if b.min() < -1e-8:continue
    q=np.floor(b@ss+.5).astype(int);sx,sy=q
    if 0<=sx<128 and 0<=sy<128 and mask[sy,sx]:out[y,x]=src[sy,sx];witness[y,x]=q
 return out,witness

def cross_sections(centers,half):return [[x-half,y]if side==0 else[x+half,y]for x,y in centers for side in[0,1]]
def rotate_foot(src,mask,ankle,target,degrees):
 angle=math.radians(degrees);a=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);yy,xx=np.indices((128,128));p=np.stack([xx,yy],-1);q=((p-np.array(target))@a)/np.array([.84,.97])+np.array(ankle);q=np.floor(q+.5).astype(int);valid=(q[:,:,0]>=0)&(q[:,:,0]<128)&(q[:,:,1]>=0)&(q[:,:,1]<128);sx=q[:,:,0].clip(0,127);sy=q[:,:,1].clip(0,127);valid &= mask[sy,sx];out=np.zeros_like(src);out[valid]=src[sy[valid],sx[valid]];w=np.full((128,128,2),-1,np.int16);w[valid]=q[valid];return out,w
records=[];poses=[]
for i in range(8):
 orig=np.array(Image.open(R/f'inputs/{i:02}.png').convert('RGBA'))
 protect=np.array(Image.open(R/'inputs'/f'{i:02}-protected-region.png'))>0
 yy,xx=np.indices((128,128));edit=(yy>=78)&~protect
 layers={};pose={'frame':i,'limbs':{},'clock_seconds':[9,160]}
 for leg in ['P','Q']:
  m=masters[leg];sole=np.array(soles[leg][i],float);ankle=sole+np.array(m['ankle'])-np.array(m['sole']);cuff=np.array(cuffs[leg][i],float)+np.array([0,3]);hip=np.array([57 if leg=='P'else 70,80],float)
  # Continuous, broad cloth planes; controls are authoring hypotheses only.
  sm=[m['hip'],[(m['hip'][0]+m['cuff'][0])/2,86],m['cuff']];tm=[hip,(hip+cuff)/2+np.array([1 if leg=='P'else-1,0]),cuff]
  sv=cross_sections(sm,m['half']);tv=cross_sections(tm,m['half']-1.5);arr,w=warp(*parts[leg+'-cloth'],sv,tv);layers[leg+'-cloth']=arr;np.save(D/'layers'/f'{i:02}-{leg}-cloth-source-xy.npy',w)
  sy=m['calf_y'];center_src=[[m['cuff'][0],sy[0]],[(m['cuff'][0]+m['ankle'][0])/2,sy[1]],[m['ankle'][0],sy[2]]];top=cuff+np.array([0,sy[0]-m['cuff'][1]]);bottom=ankle+np.array([0,sy[2]-m['ankle'][1]]);center_target=[top,(top+bottom)/2,bottom]
  sv=cross_sections(center_src,m['half']);tv=[[x+(-1 if side==0 else 1)*m['half']*scale,y]for (x,y),scale in zip(center_target,[.72,.78,.82])for side in[0,1]];arr,w=warp(*parts[leg+'-calf'],sv,tv);layers[leg+'-calf']=arr;np.save(D/'layers'/f'{i:02}-{leg}-calf-source-xy.npy',w)
  arr,w=rotate_foot(*parts[leg+'-foot'],m['ankle'],ankle,pitches[leg][i]);layers[leg+'-foot']=arr;np.save(D/'layers'/f'{i:02}-{leg}-foot-source-xy.npy',w)
  pose['limbs'][leg]={'authored_hip':hip.tolist(),'authored_cuff':cuff.tolist(),'authored_ankle':ankle.tolist(),'authored_foot_anchor':sole.tolist(),'foot_pitch_degrees':pitches[leg][i],'foot_xy_scale':[.84,.97]}
 base=Image.new('RGBA',(128,128));order=sorted(['P','Q'],key=lambda k:soles[k][i][1])
 for leg in order:
  for part in ['cloth','calf','foot']:
   a=layers[leg+'-'+part];Image.fromarray(a).save(D/'layers'/f'{i:02}-{leg}-{part}.png');base.alpha_composite(Image.fromarray(a))
 arr=np.array(base);result=orig.copy();result[edit]=arr[edit]
 # Only confirmed alpha1 specks outside a2px body silhouette are cleared.
 core=Image.fromarray((result[:,:,3]>=128).astype('uint8')*255).filter(ImageFilter.MaxFilter(5));noise=(result[:,:,3]==1)&(np.array(core)==0)&edit;result[noise]=0
 assert np.array_equal(result[~edit],orig[~edit]);assert np.array_equal(result[:78],orig[:78]);Image.fromarray(result).save(D/f'{i:02}.png');Image.fromarray(edit.astype('uint8')*255).save(D/'layers'/f'{i:02}-edit-mask.png');upper=orig.copy();upper[edit]=0;Image.fromarray(upper).save(D/'layers'/f'{i:02}-upper.png')
 records.append({'pose':i,'output_sha256':sha(D/f'{i:02}.png'),'changed_pixels':int(np.any(result!=orig,axis=2).sum()),'protected_upper_exact':True,'outside_mask_exact':True,'removed_far_alpha1_specks':int(noise.sum()),'depth_order':order});poses.append(pose)
board=Image.new('RGB',(8*192,2*216),(30,36,46));d=ImageDraw.Draw(board)
for row,folder in enumerate([R/'inputs',D]):
 for i in range(8):
  bg=Image.new('RGBA',(128,128),(30,36,46,255));bg.alpha_composite(Image.open(folder/f'{i:02}.png').convert('RGBA'));board.paste(bg.resize((192,192),Image.Resampling.NEAREST).convert('RGB'),(i*192,row*216+24));d.text((i*192+5,row*216+5),('old 'if row==0 else'parts v4 ')+str(i),fill='white')
board.save(D/'comparison.png');(D/'POSES.json').write_text(json.dumps(poses,indent=2)+'\n');(D/'BUILD-RECEIPT.json').write_text(json.dumps({'method':'Clearer raised opposite foot at second contact and tapered calf; longer trouser exposure, narrower leather with fixed .84/.97 foot projection; consistent painted foot/calf/cloth masters with authored projected trajectories and explicit source-texel maps. No inferred anatomy or physical contact claim.','donors':{'P':'candidate-v1/04.png','Q':'candidate-v1/00.png'},'portable_input_protection':'inputs/NN-protected-region.png; explicit preserved-region mask, not inferred anatomy','records':records},indent=2)+'\n');print('Built v4 complete eight-frame source-part walk with fixed upper and clock')
