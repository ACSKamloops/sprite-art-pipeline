from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
out=Path(__file__).parent;master=Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/upright-master-v1/native-256.png');src=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-articulated-craft-v7/native384');records=[]
cases={'head':[(master,(120,42,150,76),'master256 head',6)]+[(src/f'frame-{f:03}.png',(169,88,210,135),f'v7 true384 cel{f} head',4)for f in [0,16,49]],'ankle':[(master,(84,177,129,242),'master256 skull ankle',4),(src/'frame-016.png',(113,257,181,345),'v7 true384 cel16 collar sole',3),(src/'frame-016.png',(115,301,181,346),'v7 true384 cel16 sole',3)]}
for region,items in cases.items():
 c=Image.new('RGB',(len(items)*250,330),(35,40,45));d=ImageDraw.Draw(c)
 for i,(p,roi,label,z) in enumerate(items):
  a=Image.open(p).convert('RGBA').crop(roi);a=a.resize((a.width*z,a.height*z),Image.Resampling.NEAREST);b=Image.new('RGBA',a.size,(35,40,45,255));b.alpha_composite(a);c.paste(b.convert('RGB'),(i*250,0));d.text((i*250,285),label,fill='white');d.text((i*250,303),f'ROI{roi} nearest{z}x',fill='white');records.append({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'region':region,'roi_xyxy':roi,'nearest_scale':z})
 c.save(out/f'{region}-comparison.png')
(out/'crop-receipt.json').write_text(json.dumps(records,indent=2)+'\n')
