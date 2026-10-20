from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,math,hashlib
O=Path(__file__).resolve().parent
S=Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v11/bake/rowan/southeast')
# A = source00 screen-right elongated white thigh/boot; B = source00 screen-left tucked leg.
# Hidden hip/knee locations are authored construction hypotheses, never source observations.
phase=['A contact / B trailing','A loading / B toe-off','A support / B passing','A heel-rise / B reach','B contact / A trailing','B loading / A toe-off','B support / A passing','B heel-rise / A reach']
pelvis=[[64,80],[65,81.5],[64,79.5],[63,78.5],[63,80],[62.5,81.5],[63,79.5],[64,78.5]]
A=[[[70,80],[71,87],[71,92],[67,107],[80,110]],[[71,81.5],[70,89],[68.5,95],[65,105],[78,108]],[[70,79.5],[68,88],[66,93],[62,102],[75,105]],[[69,78.5],[66,87],[63,91],[59,99],[72,102]],[[69,80],[67,85],[63,89],[59,95],[67,98]],[[68.5,81.5],[66,87],[63,90],[60,94],[68,96]],[[69,79.5],[72,86],[68,89],[64,91],[72,94]],[[70,78.5],[76,85],[74,91],[70,100],[81,103]]]
B=[[[55,79],[51,85],[47,89],[43,95],[51,98]],[[56,80.5],[51,87],[47,90],[44,94],[52,96]],[[55,78.5],[58,86],[53,89],[49,91],[57,94]],[[54,77.5],[61,85],[58,91],[54,99],[65,102]],[[54,79],[57,88],[57,94],[53,108],[66,111]],[[53.5,80.5],[55,90],[54.5,96],[50,106],[63,109]],[[54,78.5],[53,88],[52,93],[47,103],[60,106]],[[55,77.5],[51,87],[49,91],[44,100],[57,103]]]
shouldA=[[80,61],[81,62.5],[80,60.5],[79,59.5],[79,60],[78.5,61.5],[79,59.5],[80,59.5]]
shouldB=[[48,60],[49,61.5],[48,59.5],[47,58.5],[47,61],[46.5,62.5],[47,60.5],[48,59.5]]
handA=[[84,73],[85,75],[84,77],[83,79],[83,81],[82.5,82],[83,78],[84,75]]
handB=[[43,82],[44,82.5],[43,78],[42,75],[42,73],[41.5,75],[42,78],[43,81]]
frames=[]
for i in range(8):
 p=pelvis[i];dy=p[1]-80;dx=p[0]-64
 def leg(q):return dict(zip(['hip','knee','cuff','heel','toe'],q))
 def arm(s,h):return {'shoulder':s,'elbow':[(s[0]+h[0])/2,(s[1]+h[1])/2+1],'glove_center':h}
 frames.append({'frame':i,'start_seconds':i*.05625,'hold_seconds':.05625,'phase':phase[i],'pelvis_center':p,'belt_center':[64+dx,75+dy],'neck':[67+dx*.65,56+dy*.75],'head_translation':[dx*.65,dy*.75],'head_turn_degrees':0,'torso_countertwist_hint_degrees':[2,1,0,-1,-2,-1,0,1][i],'leg_A':leg(A[i]),'leg_B':leg(B[i]),'arm_A':arm(shouldA[i],handA[i]),'arm_B':arm(shouldB[i],handB[i]),'leg_frontmost':['A','A','A','B','B','B','B','A'][i]})
doc={'status':'PROPOSED DIRECTOR MOTION GUIDE, NOT FINISHED ART OR QUALITY ACCEPTANCE','coordinate_convention':{'canvas':[128,128],'origin':'top left','axes':'x right, y down','render_pivot':[64,112],'units':'original native pixels; fractional points retained','A':'leg/arm on source00 screen-right, initially elongated forward boot','B':'leg/arm on source00 screen-left, initially tucked boot','identity_note':'A/B labels avoid claiming hidden anatomical left/right ownership'},'clock':{'loop_seconds':'9/20','hold_seconds':'9/160','frames':8,'loop_frame_8':'exact frame00 construction after completing 07→00 foot lowering and opposite toe-off'},'source_measurements':{'frame00_alpha_bbox':[35,16,91,112],'painted_head_band_bbox':[37,16,91,55],'approx_visible_neck':[67,56],'approx_belt_center':[64,75],'approx_hip_origin_band':[52,78,74,83],'approx_cream_thigh_width_range':[10,15],'approx_supported_boot_shaft_width':11,'approx_projected_full_boot_length':19,'note':'Band bounds are measured alpha; named landmarks/volumes are visual estimates. Hidden joints below clothing are authored assumptions.'},'volume_contract':{'thigh_radius_px':{'A':6,'B':5.5},'knee_radius_px':{'A':5.7,'B':5.2},'boot_cuff_halfwidth_px':{'A':5.5,'B':5},'glove_radius_px':4.3,'upper_arm_halfwidth_px':3.7,'head_and_torso':'reuse source00 paint in guide only; newly visible side planes and changed upper overlap need final paint','whole_boot':'cuff, heel and toe define one filled shaft+foot volume; do not move toe pixels independently of shaft/sole'},'frames':frames,'wrap_note':'07 is an approach pose, never a copied contact. A foot lowers into00 while B leaves its trailing toe; pelvis rises at07 then settles into00/01. Evaluate07→00 and03→04 at full0.45s.'}
(O/'ROWAN-SE-POSE-BLUEPRINT.json').write_text(json.dumps(doc,indent=2))

# Transparent flat-volume guide with source head/torso paint retained for scale/identity.
# These deliberately plain mattes are a renderer aid. They are not replacement sprite paint.
source=Image.open(S/'00.png').convert('RGBA')
def masked(poly):
 m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(poly,fill=255);r=source.copy();r.putalpha(ImageChops.multiply(source.getchannel('A'),m));return r
head=masked([(36,16),(92,16),(92,53),(76,58),(56,58),(37,49)])
torso=masked([(52,56),(76,55),(81,64),(80,74),(75,82),(53,82),(47,74),(48,64)])
def capsule(d,a,b,r,fill,outline=None):
 dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy) or 1;nx=-dy/L*r;ny=dx/L*r
 d.polygon([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)],fill=fill)
 for q in [a,b]:d.ellipse((q[0]-r,q[1]-r,q[0]+r,q[1]+r),fill=fill)
def limb_volume(d,q,name):
 h,k,c,he,to=[q[n] for n in ['hip','knee','cuff','heel','toe']];r=6 if name=='A' else 5.5
 cream=(220,211,184,255) if name=='A' else (193,181,151,255)
 capsule(d,h,k,r,cream);capsule(d,k,c,r-.5,cream)
 # Shaft and complete closed foot, with consistent boot width and no dangling toe-only patch.
 bh=5.5 if name=='A' else 5
 ankle=[he[0]+3,he[1]-3]
 boot=(123,66,34,255) if name=='A' else (98,48,25,255)
 capsule(d,c,ankle,bh+.5,(59,35,25,255));capsule(d,c,ankle,bh-.5,boot)
 capsule(d,[he[0]+1,he[1]-2],[to[0]-1,to[1]-2],4,(59,35,25,255));capsule(d,[he[0]+1,he[1]-2],[to[0]-1,to[1]-2],3,boot)
 d.line([tuple(he),tuple(to)],fill=(59,35,25,255),width=2)
 d.line([(c[0]-bh,c[1]),(c[0]+bh,c[1])],fill=(169,99,44,255),width=2)
def armvol(d,q):
 s,e,h=q['shoulder'],q['elbow'],q['glove_center'];capsule(d,s,e,3.7,(152,158,166,255));capsule(d,e,h,3.7,(125,68,32,255));d.ellipse((s[0]-6,s[1]-5,s[0]+6,s[1]+5),fill=(173,180,185,255));d.ellipse((h[0]-4.3,h[1]-4.5,h[0]+4.3,h[1]+4.5),fill=(123,64,31,255))
G=O/'guide';G.mkdir(exist_ok=True)
for f in frames:
 im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im)
 front=f['leg_frontmost'];back='B' if front=='A' else 'A';limb_volume(d,f['leg_'+back],back);limb_volume(d,f['leg_'+front],front)
 armvol(d,f['arm_A']);armvol(d,f['arm_B'])
 dx=f['pelvis_center'][0]-64;dy=f['pelvis_center'][1]-80
 im.alpha_composite(torso,(round(dx),round(dy)))
 im.alpha_composite(head,tuple(round(v) for v in f['head_translation']))
 im.save(G/f"{f['frame']:02}.png")
# Contact sheets: original source, volume guide, silhouette overlay.
for sc in [84,128,256]:
 cw=sc+8;ch=sc+26;sheet=Image.new('RGB',(cw*8+140,ch*3+30),(36,41,48));d=ImageDraw.Draw(sheet)
 for row,title in enumerate(['CURRENT SOURCE','PROPOSED VOLUME','CYAN source / ROSE guide']):
  d.text((5,30+row*ch+sc//2),title.replace(' / ','\n'),fill='white')
  for f in frames:
   i=f['frame'];src=Image.open(S/f'{i:02}.png').convert('RGBA');gui=Image.open(G/f'{i:02}.png').convert('RGBA');im=src if row==0 else gui
   if row==2:
    im=Image.new('RGBA',(128,128));sa=src.getchannel('A').point(lambda x:125 if x else 0);ga=gui.getchannel('A').point(lambda x:135 if x else 0)
    a=Image.new('RGBA',(128,128),(0,225,235,0));a.putalpha(sa);b=Image.new('RGBA',(128,128),(255,80,135,0));b.putalpha(ga);im=Image.alpha_composite(a,b)
   im=im.resize((sc,sc),Image.Resampling.NEAREST);x=140+i*cw;y=30+row*ch;sheet.paste(im,(x,y),im);d.text((x,y+sc+2),f'{i:02} {f["start_seconds"]*1000:g}ms',fill='white')
 sheet.save(O/f'ROWAN-SE-SOURCE-GUIDE-{sc}.png')
# A native-space trajectory drawing, spatially honest rather than anatomical proof.
pathim=Image.new('RGB',(768,768),(36,41,48));pd=ImageDraw.Draw(pathim)
for leg,color in [('A',(255,150,65)),('B',(80,205,255))]:
 for landmark in ['hip','knee','cuff','heel','toe']:
  pts=[tuple(6*v for v in f['leg_'+leg][landmark]) for f in frames];pd.line(pts+[pts[0]],fill=color,width=2)
  for i,p in enumerate(pts):pd.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=color);pd.text((p[0]+4,p[1]-7),f'{leg}{i}',fill=color)
pd.text((10,10),'Proposed native128 paths x6. Orange=A; cyan=B.\nHidden joint positions are design hypotheses. See JSON per landmark.',fill='white');pathim.save(O/'ROWAN-SE-PATHS.png')
print(O/'ROWAN-SE-POSE-BLUEPRINT.json')
