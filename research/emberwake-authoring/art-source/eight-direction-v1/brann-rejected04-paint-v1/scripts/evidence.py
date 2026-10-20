from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=arr(ROOT/'raw/untouched.png');h,w=raw.shape[:2];yy,xx=np.mgrid[:128,:128];sx=((2*xx+1)*w//256).astype('int16');sy=((2*yy+1)*h//256).astype('int16');native=raw[sy,sx];Image.fromarray(native).save(ROOT/'raw-fixed-stage-native.png');np.savez_compressed(ROOT/'raw/full-stage-source-map.npz',raw_source_xy=np.stack([sx,sy],axis=-1))
base=arr(ROOT/'inputs/02-v5-current04-context-native.png');upper=np.array(Image.open(ROOT/'inputs/whole-upper-protection.png'))>0
im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon([(47,84),(79,84),(83,89),(94,102),(96,117),(31,117),(31,94),(43,88)],fill=255);roi=(np.array(im)>0)&~upper
candidate=base.copy();candidate[roi]=native[roi];assert np.array_equal(candidate[~roi],base[~roi]);assert np.array_equal(candidate[upper],base[upper]);Image.fromarray(candidate).save(ROOT/'composite-04-REJECTED.png');Image.fromarray((roi*255).astype('uint8')).save(ROOT/'masks/bounded04-lower-owner.png')
guide=Image.open(ROOT/'inputs/01-guide-primary-pose-native.png').convert('RGBA');BG=(230,228,217,255)
for name,s in [('native',128),('066',84),('2x',256)]:
    items=[('actual guide',guide),('raw fixed stage',Image.fromarray(native)),('v5 current04',Image.fromarray(base)),('REJECTED composite',Image.fromarray(candidate))];sh=Image.new('RGBA',(4*s,s+20),BG);d=ImageDraw.Draw(sh)
    for col,(label,im)in enumerate(items):sh.alpha_composite(im.resize((s,s),Image.Resampling.NEAREST),(s*col,20));d.text((s*col+2,2),label,fill='black')
    sh.save(ROOT/'proof'/f'guide-raw-composite-{name}.png')
    context=Image.new('RGBA',(5*s,2*(s+20)),BG);cd=ImageDraw.Draw(context)
    for row in range(2):
        for col,i in enumerate([0,3,4,5,6]):
            im=Image.fromarray(candidate)if row==1 and i==4 else Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA');context.alpha_composite(im.resize((s,s),Image.Resampling.NEAREST),(s*col,row*(s+20)+20));cd.text((s*col+2,row*(s+20)+2),f'{"REJECTED04"if row==1 and i==4 else"v5"} {i:02}',fill='black')
    context.save(ROOT/'proof'/f'00-03-new04-05-06-{name}.png')
sh=Image.new('RGBA',(72*3,42),BG)
for col,im in enumerate([guide,Image.fromarray(native),Image.fromarray(candidate)]):sh.alpha_composite(im.crop((28,76,100,118)),(72*col,0))
sh.resize((864,168),Image.Resampling.NEAREST).save(ROOT/'proof/lower-guide-raw-rejected-4x.png')
receipt={'status':'REJECTED for reverted support role; no accepted replacement','built_in_ImageGen_calls':1,'raw':'raw/untouched.png','raw_sha256':sha(ROOT/'raw/untouched.png'),'raw_dimensions':[w,h],'registration':{'method':'single full-stage center-sampled nearest mapping only','native_canvas':[128,128],'scale_x_rational':[128,w],'scale_y_rational':[128,h],'translation':[0,0],'bbox_fit':False,'recenter':False,'limb_fit':False},'failure':'Raw places screen-right boot lower/forward and screen-left boot tucked/rear, opposite the actual primary guide. No source shift or label change repairs this.','composite':'composite-04-REJECTED.png','composite_sha256':sha(ROOT/'composite-04-REJECTED.png'),'bounded_owner':'masks/bounded04-lower-owner.png','actual_v5_upper_and_outside_owner_RGBA_exact':True,'baseline_frames_unchanged':True,'further_calls':0,'editor_package':'not produced for rejected art'}
(ROOT/'ROLE-REJECTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='SHA256SUMS')
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n'for p in files))
print('Frozen compact rejected-call evidence; raw/guide/composite and requested native/.66 context retained. Role-rejection SHA256 '+sha(ROOT/'ROLE-REJECTION.json'))
