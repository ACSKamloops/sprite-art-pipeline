from pathlib import Path
from PIL import Image
import json,hashlib,shutil,argparse
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def export(pack,out):
 if out.exists():raise ValueError('Refuse historical foreground output')
 m=json.loads((pack/'manifest.json').read_text());out.mkdir();(out/'frames').mkdir();rows=[];source=ROOT/'source/near-greave-convex-matte.png';palette=set(Image.open(source).convert('RGBA').get_flattened_data())|{(0,0,0,0)}
 for f in m['frames']:
  p=pack/f['foreground']['png'];assert sha(p)==f['foreground']['png_sha256'];im=Image.open(p).convert('RGBA');assert set(im.get_flattened_data())<=palette;assert set(im.getchannel('A').get_flattened_data())<={0,255};d=out/'frames'/f"{f['key']:02}.png";shutil.copy2(p,d);rows.append({'key':f['key'],'phase':f['phase'],'png':str(d.relative_to(out)),'png_sha256':sha(d),'RGBA_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'knee':f['legs']['left']['knee'],'shin_angle_degrees':f['legs']['left']['joint_angles_degrees'][1],'cap_angle_degrees':f['foreground']['cap_angle_degrees'],'cap_face_projection':f['foreground']['cap_face_projection'],'seat_shadow_ownership':f['foreground']['seat_shadow_ownership'],'source_palette_only':True,'binary_alpha':True})
 r={'schema':'captain-source-foreground-shin/v1','source_manifest_sha256':sha(pack/'manifest.json'),'source_pose_manifest_sha256':m['parent_pose_manifest_sha256'],'source_renderer_sha256':m['renderer_sha256'],'source_art_sha256':sha(source),'exporter_sha256':sha(Path(__file__)),'canvas':[256,256],'origin_policy':'Exactfulllegpackorigin/pose, nofit/recenter','source_ownership':m['source_ownership'],'scope':'Replacementconvexmastercap/shell withauthored sourcepalette-sampled shallowseatshadow clippedtoshell. No hidden cuff/thigh/boot/oldgreave. SameactualRGBA asfulllegpackforeground; no recovery/artapprovalclaim.','frames':rows};(out/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');sb=out/'source-bindings';sb.mkdir()
 for p in (pack/'source-bindings').iterdir():shutil.copy2(p,sb/p.name)
 print('72matching cuff-freeforegrounds')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,default=ROOT/'long-stride-keyshape-v3');p.add_argument('--output',type=Path,default=ROOT/'foreground-long-stride-keyshape-v3-owned');a=p.parse_args();export(a.pack,a.output)
