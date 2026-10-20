"""Onlythefrozenreview'sseven alpha0 cuffslit pixels; literalactual03charcoal underpaint."""
from pathlib import Path
from fractions import Fraction
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=np.array(Image.open(R/'inputs/original-bank/02.5.png').convert('RGBA'));source=np.array(Image.open(R/'inputs/original-bank/03.png').convert('RGBA'))
# Fixedmaterialwitnesses: continueactual03charcoalgradient, thenactualdarkcuffattachmentshadow.
placements=[([53,90],[54,90],'uppercharcoalcontinuation'),([54,90],[55,90],'uppercharcoalcontinuation'),([55,90],[56,90],'uppercharcoalcontinuation'),([53,91],[57,91],'cuffattachmentshadow'),([54,91],[57,92],'cuffattachmentshadow'),([55,91],[58,92],'cuffattachmentshadow'),([56,91],[59,92],'cuffattachmentshadow')]
expected={(53,90),(54,90),(55,90),(53,91),(54,91),(55,91),(56,91)};assert {tuple(x) for x,_s,_r in placements}==expected
out=base.copy();owner=np.zeros((128,128),np.uint8);underlayer=np.zeros_like(base);ops=[]
def halfup(f):return (f.numerator*2+f.denominator)//(2*f.denominator)
for (x,y),(sx,sy),role in placements:
 f=base[y,x].astype(np.int64);u=source[sy,sx].astype(np.int64);assert f.tolist()==[0,0,0,0];assert int(u[3])==255;assert max(map(int,u[:3]))-min(map(int,u[:3]))<=2
 fa,ua=int(f[3]),int(u[3]);den=fa*255+ua*(255-fa);result=[int((int(f[k])*fa*255+int(u[k])*ua*(255-fa)+den//2)//den) for k in range(3)]+[(den+127)//255]
 # Independentexactrationalmath andPillow one-pixel alpha-composite mustagree.
 af,au=Fraction(fa,255),Fraction(ua,255);ao=af+au*(1-af);rgb=[halfup((Fraction(int(f[k]))*af+Fraction(int(u[k]))*au*(1-af))/ao) for k in range(3)];rational=rgb+[halfup(ao*255)];pil=list(Image.alpha_composite(Image.new('RGBA',(1,1),tuple(map(int,u))),Image.new('RGBA',(1,1),tuple(map(int,f)))).getpixel((0,0)))
 assert result==rational==pil==u.tolist();out[y,x]=result;owner[y,x]=255;underlayer[y,x]=u;ops.append({'destination':[x,y],'expected_front_RGBA':f.tolist(),'underpaint_source_file':'inputs/original-bank/03.png','underpaint_source_xy':[sx,sy],'underpaint_source_RGBA':u.tolist(),'material_role':role,'source_over_result_RGBA':result,'independent_rational_alpha_over_exact':True,'independent_Pillow_alpha_over_exact':True})
changed=np.any(out!=base,axis=-1);assert changed.sum()==7;assert {tuple([int(x),int(y)]) for y,x in np.argwhere(changed)}==expected;assert np.array_equal(out[~changed],base[~changed]);Image.fromarray(out).save(R/'candidate/02.5.png');Image.fromarray(owner).save(R/'masks/seven-pixel-cuff-owner.png');Image.fromarray(underlayer).save(R/'layers-underpaint.png')
np.savez_compressed(R/'maps/seven-pixel-underpaint.npz',destination=np.array([o['destination'] for o in ops],np.int16),front_RGBA=np.array([o['expected_front_RGBA'] for o in ops],np.uint8),source_phase=np.full(7,3,np.int8),source_xy=np.array([o['underpaint_source_xy'] for o in ops],np.int16),under_RGBA=np.array([o['underpaint_source_RGBA'] for o in ops],np.uint8),result_RGBA=np.array([o['source_over_result_RGBA'] for o in ops],np.uint8))
report=Path('/home/astra/artifacts/emberwake-brann-025-followup-review-v1/review/report.md');journal={'status':'Onlyactualdemonstrated7pixelcuffslit repair; parentcropinspectionbeforeeditorpackage','frozen_report_readonly':str(report),'frozen_report_sha256':sha(report),'original_midpoint_sha256':sha(R/'inputs/original-bank/02.5.png'),'source03_sha256':sha(R/'inputs/original-bank/03.png'),'result_midpoint_sha256':sha(R/'candidate/02.5.png'),'composition':'Existingfront overliteralactualsourcecharcoalunderpaint; integer source-over, exactrationalreference andPillow agree independently. All7originalfrontA0, thereforeeachresult equalsitsactualsourceRGBA.','operations':ops,'actual_changed_RGBA_coords':[o['destination'] for o in ops],'changed_count':7,'all_other_mid_RGBA_exact':True,'larger_leg_clearance_RGBA_exact':True,'original8_PNG_bytes_exact':True,'clock_unchanged':True,'new_authored_hidden_anatomy_claim':False,'model_calls':0};(R/'UNDERPAINT-JOURNAL.json').write_text(json.dumps(journal,indent=2)+'\n')
for n in ['00','01','02','03','04','05','06','07']:assert (R/'candidate'/f'{n}.png').read_bytes()==(R/'inputs/original-bank'/f'{n}.png').read_bytes()
# Light/dark/green diagnosticcrop, exactnativecoordinates; outlines areproofonly.
crop=(48,84,69,99);scale=16;cw,ch=21*scale,15*scale;can=Image.new('RGB',(2*cw+48,3*(ch+34)+70),(233,233,222));d=ImageDraw.Draw(can)
for row,(bg,label) in enumerate([((233,233,222,255),'light'),((29,34,43,255),'dark'),((40,145,80,255),'green')]):
 for col,(name,ar) in enumerate([('Original frozen mid',base),('Only7 charcoal underpaint',out)]):
  z=Image.new('RGBA',(21,15),bg);z.alpha_composite(Image.fromarray(ar).crop(crop));z=z.convert('RGB').resize((cw,ch),Image.Resampling.NEAREST);ox=12+col*(cw+24);oy=22+row*(ch+34);can.paste(z,(ox,oy));d.text((ox,oy-17),name+' / '+label,fill='black')
  for x,y in expected:
   x0=ox+(x-crop[0])*scale;y0=oy+(y-crop[1])*scale;d.rectangle((x0,y0,x0+scale-1,y0+scale-1),outline=(240,190,10),width=1)
d.text((12,3*(ch+34)+1),'Exact pixels:53-55 atY90;53-56 atY91. Crop x48..68,y84..98.',fill='black');d.text((12,3*(ch+34)+20),'Original8PNGs, foot/cuff outlines and larger leg clearance remain exact.',fill='black');d.text((12,3*(ch+34)+39),'Actual03charcoal surface/shadow donors; all7front alpha0 -> sourceRGBA, alpha255.',fill='black');can.save(R/'proof/before-after-seven-pixel-crop.png')
# Unmarkedfullbodycomparisonatnativeand2x keepsactualsilhouetteassessmentavailable.
for size,label in [(128,'native'),(256,'2x'),(84,'game')]:
 c=Image.new('RGBA',(size*2,size+20),(233,233,222,255));dd=ImageDraw.Draw(c)
 for j,(n,ar) in enumerate([('original02.5',base),('7pixel repair',out)]):c.alpha_composite(Image.fromarray(ar).resize((size,size),Image.Resampling.NEAREST),(j*size,20));dd.text((j*size+3,2),n,fill='black')
 c.save(R/'proof'/f'full-mid-before-after-{label}.png')
print(json.dumps({'new_midpoint_sha256':journal['result_midpoint_sha256'],'changed_count':7,'source03_RGBA_witnesses':[o['underpaint_source_RGBA'] for o in ops],'independent_alpha_over_methods':['integer','exact rational','Pillow'],'frozen_report_sha256':journal['frozen_report_sha256'],'proof':str(R/'proof/before-after-seven-pixel-crop.png')},indent=2))
