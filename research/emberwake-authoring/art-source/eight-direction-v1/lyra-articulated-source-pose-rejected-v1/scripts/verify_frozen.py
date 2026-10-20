"""Independent exact-source/map/layer check of the frozen single06 proposal.
Writes proof receipt and verification render only, never candidate art.
"""
from pathlib import Path
from fractions import Fraction
import hashlib,json,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def a(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def over(s,d):
 o=np.zeros_like(s)
 def rnd(q):return(2*q.numerator+q.denominator)//(2*q.denominator)
 for y,x in np.argwhere((s[:,:,3]>0)|(d[:,:,3]>0)):
  sa=Fraction(int(s[y,x,3]),255);da=Fraction(int(d[y,x,3]),255);oa=sa+da*(1-sa)
  if not oa:continue
  o[y,x,3]=rnd(oa*255)
  for c in range(3):o[y,x,c]=rnd((int(s[y,x,c])*sa+int(d[y,x,c])*da*(1-sa))/oa)
 return o
src=a(R/'inputs/source04.png');cur=a(R/'inputs/current06.png');recipe=json.loads((R/'RECIPE.json').read_text());upper=mask(R/'inputs/guide/protected-current06-upper-owner.png');oldq=mask(R/'inputs/current06-old-Q-owner.png');other=(cur[:,:,3]>0)&~oldq&~upper;distmask=mask(R/'inputs/guide/protected-distal-target-owner.png');parts={};counts={}
for item in recipe['parts']:
 name=item['part'];m=np.load(R/'maps'/f'{name}.npz');sm=m['source_xy'];owner=mask(R/item['source_owner']);part=np.zeros_like(src);n=0
 for y,x in np.argwhere(sm[:,:,0]>=0):
  sx,sy=sm[y,x];assert owner[sy,sx];p=np.linalg.inv(m['affine'])@(np.array([x,y])-m['offset']);assert np.floor(p+.5).astype(int).tolist()==[int(sx),int(sy)];part[y,x]=src[sy,sx];n+=1
 assert np.array_equal(part,a(R/'layers'/f'{name}-mapped-raw.png'));parts[name]=part;counts[name]=n
for q in recipe['part_visibility_contour_erasures']:
 name=q['part'];x,y=q['target'];sx,sy=q['source04'];assert parts[name][y,x].tolist()==q['source_RGBA'];assert src[sy,sx].tolist()==q['source_RGBA'];assert not(upper[y,x]or other[y,x]or distmask[y,x]);parts[name][y,x]=0
for name,p in parts.items():assert np.array_equal(p,a(R/'layers'/f'{name}-visible-after-contour.png'))
# Exact upper spatial owner clips underlying new parts before normal composition
# including one partial-alpha edge[55,82]. This is a declared material/depth cut,
# not restoration of a wrong new body or new hidden anatomy.
upper_underlaps=[]
for name in parts:
 for y,x in np.argwhere((parts[name][:,:,3]>0)&upper):upper_underlaps.append({'part':name,'target':[int(x),int(y)],'mapped_RGBA':parts[name][y,x].tolist(),'upper_RGBA':cur[y,x].tolist(),'reason':'full current upper spatial ownership; hidden part sample excluded before foreground composition'})
 parts[name][upper]=0
base=cur.copy();base[oldq|upper|other]=0;body=np.zeros_like(src);body[upper]=cur[upper];leg=np.zeros_like(src);leg[other]=cur[other]
distal=np.zeros_like(src);samples=json.loads((R/'inputs/guide/DISTAL-TARGET-WITNESSES.json').read_text());assert len(samples)==136
for q in samples:
 sx,sy=q['source04'];x,y=q['target06'];assert[x-sx,y-sy]==[-12,-12];assert src[sy,sx].tolist()==q['RGBA'];distal[y,x]=src[sy,sx];assert int(src[sy,sx,3])==255
joint=np.zeros_like(src)
for q in recipe['joint_paint']:
 x,y=q['target'];sx,sy=q['source04'];assert src[sy,sx].tolist()==q['donor_RGBA'];joint[y,x]=src[sy,sx]
# Plain declared source-over composition, no post-hoc protectedRGBA restoration.
out=over(parts['shaft'],base);out=over(distal,out);out=over(parts['thigh'],out);out=over(joint,out);out=over(leg,out);out=over(body,out);out[out[:,:,3]==0]=0
frozen=a(R/'candidate06.png');assert np.array_equal(out,frozen);assert np.array_equal(out[upper],cur[upper]);assert np.array_equal(out[other],cur[other]);assert np.array_equal(out[distmask],distal[distmask]);p=R/'proof/independent-layer-replay06.png';Image.fromarray(out).save(p);assert p.read_bytes()==(R/'candidate06.png').read_bytes()
receipt={'status':'PASS frozen single-pose source construction mechanics; physical plausibility pending independent one-pose review','candidate_PNG_sha256':sha(R/'candidate06.png'),'candidate_RGBA_sha256':hashlib.sha256(out.tobytes()).hexdigest(),'source04_sha256':sha(R/'inputs/source04.png'),'current06_sha256':sha(R/'inputs/current06.png'),'separate_affine_samples':counts,'shaft_cross_section_projection':.5,'source_controls_not_anatomical_measurements':{'source_H':[58,85],'source_K':[57,96],'source_A':[55,105],'target_H':[58,83],'target_K':[52,92],'target_A':[43,93]},'source_contour_erasures':recipe['part_visibility_contour_erasures'],'authored_local_joint_pixels':recipe['joint_paint'],'upper_spatial_owner_underlap_witnesses':upper_underlaps,'whole_current_upper_RGBA_exact':True,'whole_current_other_visible_leg_RGBA_exact':True,'distal136_RGBA_exact':True,'distal_translation':[-12,-12],'separate_plain_source_over_replay_RGBA_PNG_exact':True,'body_restoration_after_composition':False,'depth':['current retained residual','separate mapped shaft','opaque protected distal136','separate mapped thigh','one explicit leather joint pixel','retained current other visible leg foreground where7 overlaps','complete current upper; incoming part samples excluded from its literal spatial owner'],'new_paint_is_authored_source_colour_not_recovered_anatomy':True,'rejected_unit_cross_section_trial_retained':'rejected-unit-cross-section','quality_limits':['Calf/ankle remains compressed; rounded thigh meets a tall protected distal neck with sharp underside/side transitions.','Source04 leather is an irregular visible U-wrap, not a full hidden calf master.','Source row104/105 is an authored paint-owner cut; it is not a proven anatomical ankle.','One pose only; no timing/action/contact/motion-quality claim.'],'model_calls':0,'editor':False,'canonical_writes':0}
(R/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'exact_candidate_png_sha256':receipt['candidate_PNG_sha256'],'source_parts_map_exact':True,'normal_source_over_replay_exact':True,'upper_otherleg_distal_exact':True,'contour_erasures':len(receipt['source_contour_erasures']),'authored_joint_pixels':len(recipe['joint_paint'])},indent=2))
