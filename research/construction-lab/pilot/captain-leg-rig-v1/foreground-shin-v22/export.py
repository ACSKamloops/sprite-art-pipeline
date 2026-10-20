"""Foreground near source armor only; exact frozen v22 registration/poses, no cuffs."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import json,math,hashlib,importlib.util
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;PACK=BASE/'dense-v22'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 out=ROOT/'frames'
 if out.exists():raise ValueError('Refuse existing export')
 manifest=json.loads((PACK/'manifest.json').read_text());design=json.loads((PACK/'source-bindings/design.json').read_text());d=design['legs']['left'];cfg=d['parts']['shin'];source=BASE/d['source'];assert sha(source)==manifest['source_hashes'][d['source']]
 spec=importlib.util.spec_from_file_location('frozen_v22',PACK/'source-bindings/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 im=Image.open(source).convert('RGBA');mask=Image.new('L',im.size);ImageDraw.Draw(mask).rectangle((0,cfg['source_y'][0],im.width-1,cfg['source_y'][1]),fill=255);im.putalpha(ImageChops.multiply(im.getchannel('A'),mask));sp=d['source_anchors'][cfg['pivot']];np=d['native_anchors'][cfg['pivot']];sv=b.sub(d['source_anchors'][cfg['end']],sp);nv=b.sub(d['native_anchors'][cfg['end']],np);scale=b.norm(nv)/b.norm(sv);angle=b.angle(nv)-b.angle(sv);native=b.transform(im,sp,np,angle,scale)
 factor=d.get('shin_lateral_factor',1);u=[v/b.norm(nv)for v in nv];n=[-u[1],u[0]];aa=u[0]**2+n[0]**2/factor;bb=u[0]*u[1]+n[0]*n[1]/factor;dd=u[1]**2+n[1]**2/factor;native=native.transform((256,256),Image.Transform.AFFINE,(aa,bb,np[0]-aa*np[0]-bb*np[1],bb,dd,np[1]-bb*np[0]-dd*np[1]),Image.Resampling.NEAREST,fillcolor=(0,0,0,0))
 native.save(ROOT/'native-source-before-cuff.png');palette=set(native.get_flattened_data());source_palette=set(im.get_flattened_data())|{(0,0,0,0)};assert palette<=source_palette
 out.mkdir();rows=[];sheet=Image.new('RGBA',(2048,1080),(31,34,41,255));select=[0,7,18,22,28,36,54,71]
 for f in manifest['frames']:
  pose=f['legs']['left'];layer=b.transform(native,np,pose['knee'],math.radians(pose['joint_angles_degrees'][1]));path=out/f"{f['key']:02}.png";layer.save(path);colors=set(layer.get_flattened_data());assert colors<=palette|{(0,0,0,0)};assert set(layer.getchannel('A').get_flattened_data())<={0,255};rows.append({'key':f['key'],'phase':f['phase'],'png':str(path.relative_to(ROOT)),'png_sha256':sha(path),'RGBA_sha256':hashlib.sha256(layer.tobytes()).hexdigest(),'knee':pose['knee'],'shin_angle_degrees':pose['joint_angles_degrees'][1],'source_palette_only':True,'binary_alpha':True})
  if f['key']in select:
   i=select.index(f['key']);x=i%4*512;y=i//4*540;sheet.alpha_composite(layer.resize((512,512),Image.Resampling.NEAREST),(x,y+20));ImageDraw.Draw(sheet).text((x+8,y+8),f"source-only near shin pose{f['key']:02}",fill='white')
 sheet.save(ROOT/'contact-2x.png');r={'schema':'captain-source-foreground-shin/v1','source_manifest_sha256':sha(PACK/'manifest.json'),'source_renderer_sha256':sha(PACK/'source-bindings/build.py'),'source_design_sha256':sha(PACK/'source-bindings/design.json'),'source_clips_sha256':sha(PACK/'source-bindings/clips.json'),'source_art':d['source'],'source_art_sha256':sha(source),'exporter_sha256':sha(Path(__file__)),'native_before_cuff_png_sha256':sha(ROOT/'native-source-before-cuff.png'),'native_RGBA_sha256':hashlib.sha256(native.tobytes()).hexdigest(),'source_slice_y':cfg['source_y'],'transverse_factor':factor,'canvas':[256,256],'origin_policy':'Unchanged v22 origin; no crop/recenter/perpose fit','scope':'Actual near shin SOURCE pixels after initialregistration and1.12 width but BEFORE authored cuff. Frozenv22 knee/angle applied unchanged. No thigh/boot/cuff included; source darkpixels remain legitimate. All72 frames palette-preserving/binaryalpha. Foregrounddepthtrial requires root composition/visualreview, no artapproval.','frames':rows};(ROOT/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print('72 source-only layers, palette/binaryalpha PASS')
if __name__=='__main__':run()
