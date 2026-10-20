"""ONE actual generated whole-leg return; exact pre-call owner only.
No per-pose fit, source-toe paste, palette remap, alpha threshold or reroll.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def a(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
rawim=Image.open(R/'raw/imagegen-return.png').convert('RGBA');rawim.resize((128,128),Image.Resampling.NEAREST).save(R/'raw/whole-canvas-native128-NEAREST-DIAGNOSTIC.png')
base=a(R/'inputs/base128.png');gen=a(R/'raw/whole-canvas-native128-BOX.png');nn=a(R/'raw/whole-canvas-native128-NEAREST-DIAGNOSTIC.png');owner=m(R/'masks/whole-leg-owner.png');upper=m(R/'masks/protected-upper.png');other=m(R/'masks/protected-otherleg.png');oldfoot=m(R/'masks/protected-distal136.png')
assert not np.any(owner&(upper|other));out=base.copy();out[owner]=gen[owner];assert np.array_equal(out[~owner],base[~owner]);assert np.array_equal(out[upper|other],base[upper|other]);Image.fromarray(out).save(R/'strict-owner-composite-PROVISIONAL.png')
selected=np.zeros_like(base);selected[owner]=gen[owner];Image.fromarray(selected).save(R/'raw/wholeleg-selected-under-predeclared-owner.png');changed=np.any(out!=base,axis=2);Image.fromarray(changed.astype('uint8')*255).save(R/'masks/actual-changed-pixels.png')
# Literal off-owner material is reported, not hidden by a newer mask. Body/
# glove/tunic drift belongs to the protected upper and is not reusable leg paint.
flag=json.loads((R/'raw/OWNER-FIT-DIAGNOSTIC.json').read_text())['source_RGBA_at_flagged'];bootedge=[[55,101],[55,102],[55,103],[54,104]];kneeedge=[[61,90],[60,91]];hipedge=[[58,82],[60,83],[61,84],[62,84]];cuffedge=[[46,87],[47,87]]
classification=[]
for q in flag:
 x,y=q['xy'];role='protected upper/glove/hem variation outside authorized wholeleg mask'
 if[x,y]in bootedge:role='generated boot dark outer edge clipped by strict pre-call owner; fit limitation'
 elif[x,y]in kneeedge:role='generated knee dark outer edge clipped by strict pre-call owner; fit limitation'
 elif[x,y]in hipedge:role='generated proximal gray/hem interface outside owner; source hem restored, inspect join'
 elif[x,y]in cuffedge:role='generated calf upper-side brown edge outside owner; strict clip, inspect contour'
 classification.append(q|{'classification':role,'base_RGBA':base[y,x].tolist(),'strict_composite_RGBA':out[y,x].tolist()})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rec={'status':'unselected provisional strict-owner composite for root visual inspection; not final art','actual_model_calls':1,'source':'raw/imagegen-return.png','raw_sha256':sha(R/'raw/imagegen-return.png'),'actual_raw_dimensions':list(rawim.size),'native_normalization':{'whole_canvas_only':True,'source_dimensions':list(rawim.size),'target':[128,128],'translation':[0,0],'chosen_filter':'Pillow BOX; averaged painted-stage transport, not nearest or byte-preserving','reason':'actual return has enlarged painterly/pixel clusters not aligned to input8x grid; one global area reduction retains whole-stage framing and reduces arbitrary single-sample cluster aliasing','diagnostic_filter':'NEAREST retained separately, no candidate fitted to it'},'owner_file':'masks/whole-leg-owner.png','owner_sha256':sha(R/'masks/whole-leg-owner.png'),'owner_before_call_unchanged':True,'owner_count':int(owner.sum()),'no_clipping_hidden':classification,'new_leg_broad_pose_assessment':'raw new charcoal knee/calf/ankle/boot is connected, with a shallower, more conventional diagonal step than rejected source; exact oldH/K/A/toe no longer requirements','manual_raw_shape_landmark_estimates_native_not_bones':{'hem_attachment':[58,83],'charcoal_knee_lower_center':[54,90],'leather_ankle_transition':[48,98],'forefoot_lower_mass':[50,102],'estimate_uncertainty_px':2},'actual_changed_RGBA_coordinates':[{'xy':[int(x),int(y)],'before':base[y,x].tolist(),'after':out[y,x].tolist()}for y,x in np.argwhere(changed)],'outside401_RGBA_exact':True,'current_upper_otherleg_RGBA_exact':True,'old_distal136_not_protected_or_pasted':True,'old_distal_changed_coordinates':[[int(x),int(y)]for y,x in np.argwhere(changed&oldfoot)],'whole_leg_generated_paint_new_not_recovered_anatomy':True,'composite_sha256':sha(R/'strict-owner-composite-PROVISIONAL.png'),'limitations':['Strict pre-call owner removes several generated dark outer boot/knee/calf edge samples and clips part of raw proximal interface. See explicit off-owner witnesses and join crops.','BOX is a declared average reduction; nearest diagnostic retained. No palette/source-texel fidelity claimed for generated paint.','Broad step is less sharply bent; one-pose visual comparison required.','No fullbank, editor, score or causal comparison conclusion from one sample.']}
(R/'STRICT-COMPOSITE-RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
for size in[128,256,84]:
 for name,col in [('light',(231,227,214,255)),('dark',(34,37,43,255)),('game',(39,57,47,255))]:
  can=Image.new('RGB',(size*4,size+24),col[:3]);d=ImageDraw.Draw(can)
  for j,(label,z)in enumerate([('input',base),('RAW BOX',gen),('RAW nearest',nn),('strict401 BOX',out)]):
   bg=Image.new('RGBA',(128,128),col);bg.alpha_composite(Image.fromarray(z));can.paste(bg.resize((size,size),Image.Resampling.NEAREST).convert('RGB'),(j*size,24));d.text((j*size+2,3),label,fill='black'if name=='light'else'white')
  can.save(R/'proof'/f'full-pose-comparison-{size}-{name}.png')
box=(32,76,68,108);scale=12;can=Image.new('RGB',(4*36*scale,32*scale+24),(231,227,214));d=ImageDraw.Draw(can)
for j,(label,z)in enumerate([('SOURCE input',base),('RAW BOX - no restore',gen),('RAW nearest diagnostic',nn),('STRICT401 BOX - provisional',out)]):
 bg=Image.new('RGBA',(128,128),(231,227,214,255));bg.alpha_composite(Image.fromarray(z));can.paste(bg.crop(box).resize((36*scale,32*scale),Image.Resampling.NEAREST).convert('RGB'),(j*36*scale,24));d.text((j*36*scale+3,3),label,fill='black')
can.save(R/'proof/join-and-toe-comparison-12x.png')
print(json.dumps({'provisional_composite_sha256':rec['composite_sha256'],'changed_pixels':int(changed.sum()),'old_distal136_changed':int((changed&oldfoot).sum()),'strict401_outside_exact':True,'raw_edge_fit_limitations_reported':True,'model_calls':1},indent=2))
