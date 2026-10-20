"""Authored 2.5D near-greave probe, frozen bone anchors/boot gait untouched."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,math,hashlib,importlib.util
R=Path(__file__).resolve().parent;B=R.parent;P=B/'dense-v22'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('frozen',P/'source-bindings/build.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
D=json.loads((P/'source-bindings/design.json').read_text())['legs']['left'];K=D['native_anchors']['knee'];A=D['native_anchors']['ankle'];V=b.sub(A,K);L=b.norm(V);U=[x/L for x in V];N=[-U[1],U[0]]
def xy(s,t):return[K[j]+U[j]*s+N[j]*t for j in range(2)]
def run():
 if (R/'frames').exists():raise ValueError('Refuse existing probe')
 (R/'frames').mkdir();src=Image.open(B/'foreground-shin-v22/native-source-before-cuff.png').convert('RGBA');capmask=Image.new('L',src.size);ImageDraw.Draw(capmask).polygon([(144,177),(160,173),(173,180),(176,190),(169,198),(155,198),(144,188)],fill=255)
 from PIL import ImageChops
 cap=src.copy();cap.putalpha(ImageChops.multiply(src.getchannel('A'),capmask));shell=src.copy();alpha=shell.getchannel('A');ap=alpha.load()
 for y in range(256):
  for x in range(256):
   s=(x-K[0])*U[0]+(y-K[1])*U[1]
   if s<8 or s>41:ap[x,y]=0
 shell.putalpha(alpha)
 for layer in [cap,shell]:
  lp=layer.load()
  for y in range(256):
   for x in range(256):
    if lp[x,y][3]==0:lp[x,y]=(0,0,0,0)
 cap.save(R/'native-cap.png');shell.save(R/'native-shell.png');sourcepal=set(src.get_flattened_data())|{(0,0,0,0)};m=json.loads((P/'manifest.json').read_text());rows=[];samples=[0,7,18,24,36,54];sheet=Image.new('RGBA',(1536,1560),(31,34,41,255));draw=ImageDraw.Draw(sheet)
 for f in m['frames']:
  pose=f['legs']['left'];q=pose['local_phase'];passing=max(0,math.sin(math.pi*(q-.6)/.4))if q>=.6 else 0;down=max(0,1-abs(q-.1)/.12);width=1+.1*down-.12*passing;skew=1.7*passing
  # Authored inverse surface warp; exact longitudinal axis retained, barrel contour.
  shaped=Image.new('RGBA',(256,256));pixels=shaped.load();ip=shell.load()
  for y in range(170,235):
   for x in range(125,205):
    s=(x-K[0])*U[0]+(y-K[1])*U[1];t=(x-K[0])*N[0]+(y-K[1])*N[1];belly=math.sin(math.pi*max(0,min(1,(s-8)/33)));factor=width*(1+.08*belly);sourcet=(t-skew*belly)/factor;p=xy(s,sourcet);sx,sy=round(p[0]),round(p[1]);pixels[x,y]=ip[sx,sy]
  angle=math.radians(pose['joint_angles_degrees'][1]);posed=b.transform(shaped,K,pose['knee'],angle)
  # A round armored cap faces the camera, rather than rotating the full red panel.
  capangle=math.radians(max(-8,min(8,(pose['joint_angles_degrees'][0]+pose['joint_angles_degrees'][1])*.20)));posed.alpha_composite(b.transform(cap,K,pose['knee'],capangle));path=R/'frames'/f"{f['key']:02}.png";posed.save(path);assert set(posed.get_flattened_data())<=sourcepal;assert set(posed.getchannel('A').get_flattened_data())<={0,255}
  rows.append({'key':f['key'],'phase':f['phase'],'png':str(path.relative_to(R)),'png_sha256':sha(path),'knee':pose['knee'],'ankle':pose['ankle'],'passing':passing,'down':down,'barrel_scale':width,'surface_skew':skew,'cap_angle_degrees':math.degrees(capangle)})
  if f['key']in samples:
   i=samples.index(f['key']);x=i%3*512;y=i//3*780;old=Image.open(B/'foreground-shin-v22/frames'/f"{f['key']:02}.png").convert('RGBA');oldcrop=old.crop((120,160,200,245)).resize((240,255),Image.Resampling.NEAREST);newcrop=posed.crop((120,160,200,245)).resize((240,255),Image.Resampling.NEAREST);sheet.alpha_composite(oldcrop,(x,y+25));sheet.alpha_composite(newcrop,(x+255,y+25));draw.text((x+8,y+8),f"{f['key']:02} old / cap+shell probe",fill='white');sheet.alpha_composite(posed.resize((512,512),Image.Resampling.NEAREST),(x,y+268))
 sheet.save(R/'comparison-2x.png');report={'schema':'captain-near-volume-probe/v1','art_status':'unapproved experiment','source_manifest_sha256':sha(P/'manifest.json'),'source_before_cuff_sha256':sha(B/'foreground-shin-v22/native-source-before-cuff.png'),'renderer_sha256':sha(Path(__file__)),'canvas':[256,256],'bones_contacts_unchanged':True,'scope':'Sourcecap polygon separated from greave. Capcamera-facing averagedjoint20percent/clamped8deg. Greaveauthored down/pass transversebarrel/skew whilelongitudinaljointaxisfixed. Palettepreserved/binaryalpha; no newcolors/AI. Native source art remains unchanged. This 2.5D approximation is NOT recovered3Dvolume; temporal/composite/art review required.','frames':rows};(R/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('72 sourcepalette volumeprobe layers')
if __name__=='__main__':run()
