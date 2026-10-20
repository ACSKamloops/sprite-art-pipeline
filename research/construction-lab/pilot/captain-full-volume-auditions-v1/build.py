"""Frozen shell-layer integration and paired motion auditions. No art approval."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'captain-secondary-motion-v1'));import cloth
sys.path.insert(0,str(P.parent/'captain-upper-loading-v1'));import loading
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pack',required=True);ap.add_argument('--poses',required=True);ap.add_argument('--output',required=True);ap.add_argument('--cloth',action='store_true');ap.add_argument('--upper-loading',action='store_true');a=ap.parse_args();pack=Path(a.pack).resolve();poses=Path(a.poses).resolve();out=Path(a.output).resolve();assert not out.exists();m=json.loads((pack/'manifest.json').read_text());assert sha(poses)==m['poses_sha256'],'Mismatched pose/layer binding';packet=json.loads(poses.read_text());cfg=json.loads((P.parent/'captain-greave-volume-binding-v1/source/upper/design.json').read_text());adapted=loading.cloth_packet(packet,cfg)if a.upper_loading else None;upper_sources={n:Image.open(pack/'upper-parts/complete'/f'{n}.png').convert('RGBA')for n in ['chest','shield','backpack_halo','sword_upper_arm','sword_forearm','head','cape']}if a.upper_loading else {};out.mkdir(parents=True);(out/'frames').mkdir();(out/'layers').mkdir();frames=[];rows=[];ims=[]
 for f,r in zip(packet['frames'],m['records'],strict=True):
  i=f['index'];assert i==r['index'];layers={};records={}
  for name,rec in r['layers'].items():
   path=pack/rec['file'];assert sha(path)==rec['sha256'];layers[name]=Image.open(path).convert('RGBA');records[name]={'source_file':str(path),'source_sha256':sha(path)}
  if a.cloth:
   for name,parent,hinge,lag in [('cape','chest',103,.10),('tabard','pelvis',121,.075)]:
    src=pack/'upper-parts/complete'/f'{name}.png';layers[name],detail=cloth.render(Image.open(src),packet,i,cfg,parent,hinge,lag);records[name].update(authored_cloth=detail,immutable_source_sha256=sha(src))
  if a.upper_loading:
   replacements,load_meta=loading.render(upper_sources,packet,i,cfg,cloth,adapted)
   for name,image in replacements.items():
    layers[name]=image;records[name].update(authored_upper_loading=load_meta,immutable_source_sha256=sha(pack/'upper-parts/complete'/f'{name}.png'))
  im=Image.new('RGBA',(256,256))
  for name in m['layer_order']:
   path=out/'layers'/f'{i:03}-{name}.png';layers[name].save(path);records[name].update(file=str(path.relative_to(out)),sha256=sha(path));im.alpha_composite(layers[name])
  path=out/'frames'/f'{i:03}.png';im.save(path);ims.append(im);frames.append({'index':i,'file':str(path.relative_to(out)),'sha256':sha(path),'duration_ms':f['duration_ms'],'phase_label':f"pose{i}, far{f['legs']['far']['foot']['role']}, near{f['legs']['near']['foot']['role']}",'physical_root':f['physical_root_pixels']});rows.append({'index':i,'layers':records})
 sheet=Image.new('RGBA',(1024,560),(35,38,44,255));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(range(0,72,9)):
  xy=(j%4*256,j//4*280);sheet.alpha_composite(ims[i],xy);d.text((xy[0]+5,xy[1]+258),f'pose{i} / unapproved',fill='white')
 sheet.save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png')
 stride=np.array(packet['camera']['matrix_2x3'])@packet['dimensions']['stride_world']
 for policy in ['in_place','physical']:
  spec={'schema':'motion-audition/v1','name':f'UNAPPROVED original-armour volume / stride{np.linalg.norm(packet["dimensions"]["stride_world"]):.0f} / cloth{a.cloth}','canvas':[256,256],'stage':[1024,832],'origin':[416,80],'cycle_ms':1200,'root_stride':stride.tolist(),'root_policy':policy,'camera':'fixed','frames':frames};(out/f'audition-{policy}.json').write_text(json.dumps(spec,indent=2)+'\n')
 receipt={'state':'UNAPPROVED_FULL_ACTOR_COMPARATOR','source_pack_manifest_sha256':sha(pack/'manifest.json'),'pose_packet_sha256':sha(poses),'builder_sha256':sha(__file__),'cloth_source_sha256':sha(P.parent/'captain-secondary-motion-v1/cloth.py'),'upper_loading_enabled':a.upper_loading,'upper_loading_source_sha256':sha(P.parent/'captain-upper-loading-v1/loading.py'),'cloth_enabled':a.cloth,'layer_order':m['layer_order'],'records':rows,'limits':['Closed leg geometry and complete underlaps do not approve art','Single reference view; authored hidden surfaces and camera/anatomy','Chronological actual video review still required']};(out/'construction.json').write_text(json.dumps(receipt,indent=2)+'\n');print(out)
if __name__=='__main__':main()
