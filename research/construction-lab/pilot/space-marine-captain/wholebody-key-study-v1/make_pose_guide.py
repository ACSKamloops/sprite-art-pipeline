"""Pose guide only: newly authored coordinates; not delivered sprite artwork."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
HERE=Path(__file__).resolve().parent
# Ordered contact/down/passing/up, then opposite support side.
# Fixed camera, leftward progression; x/y perspective distinguishes near/far ground.
near=[[(142,145),(125,188),(107,229)],[(139,150),(126,191),(119,225)],[(140,145),(142,188),(140,218)],[(143,142),(154,180),(159,214)],[(142,145),(164,180),(179,207)],[(145,150),(162,181),(157,203)],[(144,145),(128,177),(124,207)],[(141,142),(113,180),(106,216)]]
far=[[(125,139),(145,175),(166,203)],[(128,144),(143,176),(145,198)],[(128,139),(120,172),(113,200)],[(125,136),(106,174),(100,211)],[(125,139),(108,182),(97,216)],[(122,144),(110,185),(112,212)],[(124,139),(126,181),(132,209)],[(127,136),(137,177),(146,205)]]
labels=['A CONTACT','A DOWN','A PASS','A UP','B CONTACT','B DOWN','B PASS','B UP']
canvas=Image.new('RGB',(2048,1024),'#20252b');draw=ImageDraw.Draw(canvas)
records=[]
for i in range(8):
 ox=i%4*512;oy=i//4*512;bob=[0,5,0,-3,0,5,0,-3][i];lean=[-2,-4,-1,1,2,0,-3,-1][i]
 def pt(p):return(ox+p[0]*2,oy+p[1]*2)
 draw.rectangle((ox,oy,ox+511,oy+511),outline='#66717f',width=2)
 draw.text((ox+16,oy+12),f'{i} {labels[i]} 150ms | NEAR=orange FAR=blue',fill='white')
 # torso/head/pelvis: scaffold for readable full-body locomotion, not a static combat photo.
 body=[(132+lean,70+bob),(130+lean,104+bob),(134,145+bob)]
 draw.line([pt(p)for p in body],fill='#e7e0c7',width=15)
 draw.ellipse((pt((121+lean,55+bob))+pt((142+lean,78+bob))),outline='#e7e0c7',width=6)
 draw.line([pt((105+lean,101+bob)),pt((156+lean,98+bob))],fill='#e7e0c7',width=12)
 draw.line([pt(near[i][0]),pt(far[i][0])],fill='#e7e0c7',width=10)
 for side,coords,color in [('far',far[i],'#63adff'),('near',near[i],'#ffb263')]:
  draw.line([pt(p)for p in coords],fill=color,width=14)
  for p in coords:draw.ellipse((pt((p[0]-3,p[1]-3))+pt((p[0]+3,p[1]+3))),fill=color)
  ax,ay=coords[-1];draw.line([pt((ax-13,ay+5)),pt((ax+3,ay+5))],fill=color,width=12)
 # restrained equipment, sword carried raised but arm isn't permanently straight.
 arm=[(105+lean,101+bob),(97+lean,122+bob),(83+lean,110+bob)]
 draw.line([pt(p)for p in arm],fill='#e7e0c7',width=10)
 draw.line([pt(arm[-1]),pt((45+lean,78+bob))],fill='#aebcca',width=5)
 draw.polygon([pt(p)for p in [(157+lean,110+bob),(182+lean,120+bob),(182+lean,165+bob),(161+lean,179+bob),(151+lean,145+bob)]],outline='#aebcca',width=5)
 draw.text((ox+16,oy+474),'Same 3/4 view. Extended support leg; lifted passing foot.',fill='white')
 records.append({'frame':i,'phase':labels[i],'duration_ms':150,'near':near[i],'far':far[i],'pelvis_bob':bob,'torso_lean':lean})
canvas.save(HERE/'guide.png');(HERE/'pose-guide.json').write_text(json.dumps({'scope':'Authoring guide, no final pixels','frames':records},indent=2)+'\n')
