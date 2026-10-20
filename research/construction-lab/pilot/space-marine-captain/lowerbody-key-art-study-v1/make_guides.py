from pathlib import Path
from PIL import Image, ImageDraw
import importlib.util,json,sys
P=Path(__file__).resolve().parent;R=P.parents[1]/'captain-upright-rig-v1';sys.path.insert(0,str(R));import construct
cfg,parts,report=construct.construct(P/'reference-parts')
source=Image.new('RGBA',(256,256));source.alpha_composite(Image.open(P/'reference-parts/source-owned/far_leg.png'));source.alpha_composite(Image.open(P/'reference-parts/source-owned/near_leg.png'));source.crop((76,120,192,248)).resize((464,512),Image.Resampling.NEAREST).save(P/'source-leg-art.png')
# These are authored projected landmarks, not a measured skeleton or recovered animation.
soles=[((103,235),(151,241)),((109,233),(149,234)),((115,231),(139,225)),((121,229),(128,233)),((127,227),(127,241)),((132,223),(133,239)),((119,216),(139,237)),((107,227),(145,235))]
knees=[((105,173),(145,175)),((110,175),(144,170)),((114,174),(132,171)),((118,172),(122,174)),((120,174),(126,174)),((126,167),(132,176)),((115,165),(138,174)),((104,171),(144,172))]
canvas=Image.new('RGB',(1024,544),(34,37,44));d=ImageDraw.Draw(canvas); rows=[]
for i,(fs,ns) in enumerate(soles):
 x,y=i%4*256,i//4*272;d.rectangle((x+75,y+90,x+183,y+247),outline=(90,92,98));d.polygon([(x+105,y+120),(x+151,y+120),(x+149,y+142),(x+109,y+138)],fill=(85,86,94))
 for leg,(sole,knee,hip,color) in enumerate(zip((fs,ns),knees[i],((113,134),(146,140)),((195,145,58),(190,46,50)))):
  an=(sole[0]+(6 if leg==0 else 1),sole[1]-24);points=[(x+hip[0],y+hip[1]),(x+knee[0],y+knee[1]),(x+an[0],y+an[1])];d.line(points,fill=color,width=16);d.polygon([(x+an[0]-7,y+an[1]),(x+an[0]+8,y+an[1]),(x+sole[0]+8,y+sole[1]),(x+sole[0]-13,y+sole[1]),(x+sole[0]-15,y+sole[1]-5)],fill=color)
  for px,py in points:d.ellipse((px-2,py-2,px+2,py+2),fill='white')
 d.text((x+5,y+251),f'{i}: '+['far contact','far load/near release','near passing','near incoming','near contact','near load/far release','far passing','far incoming'][i],fill='white');rows.append({'key':i,'far_sole':fs,'near_sole':ns,'far_knee':knees[i][0],'near_knee':knees[i][1]})
canvas.resize((2048,1088),Image.Resampling.NEAREST).save(P/'guide-eight-keys.png');(P/'guide.json').write_text(json.dumps({'scope':'Authored projected silhouette constraints only; not validated bone lengths or simulation','canvas':[256,256],'keys':rows},indent=2)+'\n')
