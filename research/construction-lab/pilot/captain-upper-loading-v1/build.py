from pathlib import Path
import json,hashlib,sys,importlib.util,argparse
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
import loading
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',default=str(P.parent/'captain-full-volume-auditions-v1/artifacts/longstride-cloth-v1'));ap.add_argument('--output',default=str(P/'artifacts/loading-v1'));a=ap.parse_args();baseline=Path(a.baseline);out=Path(a.output);assert not out.exists(),'Fresh output required';src=P/'source';packet=json.loads((src/'poses.json').read_text());cfg=json.loads((src/'design.json').read_text());binding=json.loads((baseline/'construction.json').read_text());spec=json.loads((baseline/'audition-physical.json').read_text());assert binding['pose_packet_sha256']==sha(src/'poses.json')
 sources={n:Image.open(src/'upper'/f'{n}.png').convert('RGBA')for n in list(loading.CARRIED)+['head','cape']};cs=importlib.util.spec_from_file_location('frozen_cloth',src/'cloth.py');cloth=importlib.util.module_from_spec(cs);cs.loader.exec_module(cloth);adapted=loading.cloth_packet(packet,cfg);palette=set(tuple(c)for im in sources.values()for c in np.array(im).reshape(-1,4)if c[3]);out.mkdir(parents=True);(out/'frames').mkdir();(out/'layers').mkdir();records=[];frames=[];comparisons=[];checks=[]
 for i,(f,b,s)in enumerate(zip(packet['frames'],binding['records'],spec['frames'],strict=True)):
  assert b['index']==f['index']==s['index']==i;layers={}
  for n,rec in b['layers'].items():
   path=baseline/rec['file'];assert sha(path)==rec['sha256'];layers[n]=Image.open(path).convert('RGBA')
  replacements,data=loading.render(sources,packet,i,cfg,cloth,adapted);layers.update(replacements);im=Image.new('RGBA',(256,256));layer_meta={}
  for n in binding['layer_order']:
   path=out/'layers'/f'{i:03}-{n}.png';layers[n].save(path);layer_meta[n]={'file':str(path.relative_to(out)),'sha256':sha(path),'replaced':n in replacements};im.alpha_composite(layers[n])
  path=out/'frames'/f'{i:03}.png';im.save(path);frames.append(dict(s,file=str(path.relative_to(out)),sha256=sha(path)));records.append({'index':i,'transform':data,'layers':layer_meta});old=Image.open(baseline/s['file']).convert('RGBA');comparisons.append((old,im));newcolors=sum(tuple(c)not in palette for name,layer in replacements.items()for c in np.unique(np.array(layer).reshape(-1,4),axis=0)if c[3]);neck=np.array(data['head_neck_target']);head=np.array(layers['head'])[:,:,3]>0;chest=np.array(layers['chest'])[:,:,3]>0;yy,xx=np.indices(head.shape);region=(xx+.5-neck[0])**2+(yy+.5-neck[1])**2<=64;local_head=head&region;seam_distance=float(distance_transform_edt(~chest)[local_head].min())if local_head.any()else 999;checks.append({'head_chest_near_neck_distance_px':seam_distance,'index':i,'new_palette_colors':newcolors,'head_chest_overlap_within8px':int(np.sum(head&chest&region)),'leg_layer_hashes_unchanged':all(layer_meta[n]['sha256']==b['layers'][n]['sha256']for n in b['layers']if n.startswith(('far_','near_')))})
 # Continuously periodic parent math, independent of held last→first pixel difference.
 from copy import deepcopy
 wrap=deepcopy(packet);wrap['frames'].append(deepcopy(packet['frames'][0]));wrap['frames'][-1]['phase']=1.0
 r0,p0,t0,m0=loading.transform(packet,0,cfg);r1,p1,t1,m1=loading.transform(wrap,72,cfg);assert np.allclose(r0,r1)and np.allclose(t0,t1)
 for c in checks:assert c['new_palette_colors']==0 and c['leg_layer_hashes_unchanged'] and c['head_chest_near_neck_distance_px']<=1.5
 for j in range(2):
  sheet=Image.new('RGBA',(1024,560),(35,40,46,255));draw=ImageDraw.Draw(sheet)
  for k,i in enumerate(range(j*36,(j+1)*36,9)):
   x=(k%2)*512;y=(k//2)*280
   sheet.alpha_composite(comparisons[i][0],(x,y));sheet.alpha_composite(comparisons[i][1],(x+256,y));draw.text((x+3,y+260),f'{i}: baseline / loading experiment',fill='white')
  sheet.save(out/f'comparison-{j}.png')
 spec.update(name='UNAPPROVED optional carried torso parent: negative3deg roll /2.25px upper settle',stage=[1024,832],origin=[416,80],frames=frames)
 (out/'audition-physical.json').write_text(json.dumps(spec,indent=2)+'\n')
 receipt={'schema':'captain.optional_upper_loading.v1','state':'UNAPPROVED_EXPERIMENT','source_pose_sha256':sha(src/'poses.json'),'baseline_construction_sha256':sha(baseline/'construction.json'),'module_sha256':sha(P/'loading.py'),'builder_sha256':sha(__file__),'source_files':[{'file':str(x.relative_to(P)),'sha256':sha(x)}for x in [src/'poses.json',src/'design.json',src/'cloth.py']+list((src/'upper').glob('*.png'))],'fixed_head_neck_source':[133,72],'layer_order':binding['layer_order'],'records':records,'checks':checks,'periodic_parent_exact_within1e-12':True,'head_chest_near_neck_max_distance_px':max(c['head_chest_near_neck_distance_px']for c in checks),'limits':['Rigid source torso/armor image roll remains an authored2D approximation.','Head position follows source neck anchor; its gaze remains imageangle0.','Mask overlap/palette/periodicity checks do not grant art approval.','Leg pixels and physical root remain baseline; no new contact/biomechanics proof.']};(out/'construction.json').write_text(json.dumps(receipt,indent=2)+'\n');print({'frames':len(frames),'head_neck_overlap_min':min(c['head_chest_overlap_within8px']for c in checks),'out':str(out)})
if __name__=='__main__':main()
