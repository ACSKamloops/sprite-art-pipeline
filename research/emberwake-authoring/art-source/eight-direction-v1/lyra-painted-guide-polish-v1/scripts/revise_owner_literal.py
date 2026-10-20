"""Root-authorized POST-CALL literal16-sample nearleg owner revision.
Strict401 remains unchanged. No model, resampling change, fitting or hand paint.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'owner-revision-v1'
assert not D.exists(),'Fresh revision required';D.mkdir();(D/'proof').mkdir()
def a(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=a(R/'inputs/base128.png');raw=a(R/'raw/whole-canvas-native128-BOX.png');owner=m(R/'masks/whole-leg-owner.png');upper=m(R/'masks/protected-upper.png');other=m(R/'masks/protected-otherleg.png');oldfoot=m(R/'masks/protected-distal136.png');oldstrict=a(R/'strict-owner-composite-PROVISIONAL.png');strictsha=sha(R/'strict-owner-composite-PROVISIONAL.png');assert strictsha=='a7721a7b3a66e433c627761692874d194d7cd7fd7dca61a04a6d643449f78090'
groups=[('brown boot dark heel/toe outer contour',[[55,101],[55,102],[55,103],[54,104]],'contiguous dark leather outer edge of the generated foreground boot; retains actual complete new boot contour rather than clipping its outline'),('charcoal knee lower/side outline',[[61,90],[60,91]],'dark outer charcoal knee silhouette directly adjacent to the same visible generated thigh; preserves rounded complete knee mass'),('charcoal proximal thigh under original hem',[[58,82],[59,82],[60,82],[60,83],[61,83],[62,83],[61,84],[62,84]],'actual gray/dark trouser surface under the current hem; closes scope-created knee-root clearance using generated leg paint only'),('brown upper calf/cuff contour',[[46,87],[47,87]],'two contiguous brown upper-side calf/cuff edge samples on the new folded boot shaft; isolated from the higher generated glove variation')]
rev=owner.copy();added=[]
for material,coords,reason in groups:
 for x,y in coords:
  assert not owner[y,x]and not upper[y,x]and not other[y,x];assert raw[y,x,3]>=128
  rev[y,x]=True;added.append({'xy':[x,y],'raw_RGBA':raw[y,x].tolist(),'old_base_RGBA':base[y,x].tolist(),'strict401_RGBA':oldstrict[y,x].tolist(),'material':material,'reason_this_is_leg':reason,'source_native':'raw/whole-canvas-native128-BOX.png','raw_original_area_bounds':[x*1254/128,y*1254/128,(x+1)*1254/128,(y+1)*1254/128]})
assert int(owner.sum())==401 and int(rev.sum())==417;assert len(added)==16;assert not np.any(rev&(upper|other))
out=base.copy();out[rev]=raw[rev];assert np.array_equal(out[~rev],base[~rev]);assert np.array_equal(out[upper|other],base[upper|other]);assert np.all(np.any(out!=oldstrict,axis=2)==(rev&~owner))
Image.fromarray(rev.astype('uint8')*255).save(D/'revised-owner417.png');Image.fromarray((rev&~owner).astype('uint8')*255).save(D/'literal-added16.png');Image.fromarray(out).save(D/'composite06.png');changed=np.any(out!=base,axis=2);Image.fromarray(changed.astype('uint8')*255).save(D/'actual-changed-pixels.png')
# Actual generated gold hem is not classified as leg to force a closed joint.
# These original transparent positions remain transparent; both exact RGBA
# witnesses disclose the residual current-upper interface qualification.
excluded_hem=[]
for x,y in[(61,82),(62,82)]:
 assert not rev[y,x];excluded_hem.append({'xy':[x,y],'raw_RGBA':raw[y,x].tolist(),'old_base_RGBA':base[y,x].tolist(),'final_RGBA':out[y,x].tolist(),'material':'new generated gold tunic hem, not foreground trouser/boot paint','decision':'not imported under wholeleg-only revision; preserves current upper/otherleg scope; residual original two-pixel clearance remains explicit'})
# Original otherleg ownership stays front where raw near-thigh shadow touches it.
other_witnesses=[]
for x,y in[(62,86),(63,86),(62,87),(63,87),(61,88),(62,88),(61,89)]:
 assert other[y,x]and not rev[y,x];other_witnesses.append({'xy':[x,y],'current_RGBA':base[y,x].tolist(),'raw_RGBA':raw[y,x].tolist(),'final_RGBA':out[y,x].tolist(),'decision':'literal existing other visible leg owner protected; no overwritten anatomy claim'})
rec={'status':'frozen literal post-call owner revision for root/critic inspection; unselected art','post_call_revision_explicit':True,'original_pre_call_owner_file':'masks/whole-leg-owner.png','original_pre_call_owner_sha256':sha(R/'masks/whole-leg-owner.png'),'original_owner_count':401,'revised_owner_file':'owner-revision-v1/revised-owner417.png','revised_owner_count':417,'literal_added16':added,'no_dilation_no_fitting_no_new_model_or_paint':True,'strict401_PNG_unchanged_sha256':strictsha,'raw_original_sha256':sha(R/'raw/imagegen-return.png'),'raw_normalized_BOX_sha256':sha(R/'raw/whole-canvas-native128-BOX.png'),'normalization_unchanged':'actual1254square to128square, one full-canvas PillowBOX; translation0,0; nearest diagnostic retained separately','protected_upper_otherleg_RGBA_exact':True,'all_outside417_RGBA_exact':True,'distal136_old_constraint_dropped_no_old_toe_paste':True,'old_distal136_changed_pixels':int((changed&oldfoot).sum()),'actual_changed_RGBA_coordinates':[{'xy':[int(x),int(y)],'before':base[y,x].tolist(),'after':out[y,x].tolist()}for y,x in np.argwhere(changed)],'excluded_generated_gold_hem_samples':excluded_hem,'protected_otherleg_interface_witnesses':other_witnesses,'new_wholeleg_paint':'new generated image content, not source palette recovery or recovered anatomy','final_PNG_sha256':sha(D/'composite06.png'),'final_RGBA_sha256':hashlib.sha256(out.tobytes()).hexdigest(),'model_calls_total':1,'editor':False,'fullbank':False,'no_quality_score_claim':True}
(D/'REVISION.json').write_text(json.dumps(rec,indent=2)+'\n')
# Original/revised masks over exact painted art, and literal16 delta only.
board=Image.new('RGB',(3*384,384),(231,227,214))
for j,mask in enumerate([owner,rev,rev&~owner]):
 bg=Image.new('RGBA',(128,128),(231,227,214,255));bg.alpha_composite(Image.fromarray(out));ov=np.zeros_like(out);ov[mask]=[30,180,210,110]if j<2 else[240,45,100,200];bg.alpha_composite(Image.fromarray(ov));board.paste(bg.resize((384,384),Image.Resampling.NEAREST).convert('RGB'),(j*384,0))
board.save(D/'proof/original401-revised417-added16-3x.png')
for size in[128,256,84]:
 for name,col in [('light',(231,227,214,255)),('dark',(34,37,43,255)),('game',(39,57,47,255))]:
  board=Image.new('RGB',(size*3,size+24),col[:3]);d=ImageDraw.Draw(board)
  for j,(label,z)in enumerate([('RAW BOX',raw),('strict401',oldstrict),('revised417',out)]):
   bg=Image.new('RGBA',(128,128),col);bg.alpha_composite(Image.fromarray(z));board.paste(bg.resize((size,size),Image.Resampling.NEAREST).convert('RGB'),(j*size,24));d.text((j*size+2,3),label,fill='black'if name=='light'else'white')
  board.save(D/'proof'/f'raw-strict-revised-{size}-{name}.png')
box=(32,76,68,108);board=Image.new('RGB',(3*432,408),(231,227,214));d=ImageDraw.Draw(board)
for j,(label,z)in enumerate([('RAW BOX; no protection',raw),('strict401; retained unchanged',oldstrict),('postcall revised417',out)]):
 bg=Image.new('RGBA',(128,128),(231,227,214,255));bg.alpha_composite(Image.fromarray(z));board.paste(bg.crop(box).resize((432,384),Image.Resampling.NEAREST).convert('RGB'),(j*432,24));d.text((j*432+3,3),label,fill='black')
board.save(D/'proof/raw-strict-revised-joints-12x.png')
assert sha(R/'strict-owner-composite-PROVISIONAL.png')==strictsha
print(json.dumps({'final_file':str(D/'composite06.png'),'final_SHA256':rec['final_PNG_sha256'],'changed_from_base':int(changed.sum()),'owner417':True,'literal_additions':16,'source_upper_otherleg_outside417_exact':True,'strict401_unchanged':True,'excluded_gold_hem_samples':excluded_hem},indent=2))
