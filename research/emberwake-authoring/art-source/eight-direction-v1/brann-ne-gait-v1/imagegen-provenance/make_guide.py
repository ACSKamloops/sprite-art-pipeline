from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).resolve().parent
# Authored filled silhouette geometry. Magenta = viewer-left hip leg; cyan = viewer-right hip leg.
# Positions are on the fixed 128 stage, never fitted from individual pose bounds.
poses=[
 dict(name='00-contact-right-forward',upper=0,bob=0,
  left={'hip':[56,77],'knee':[51,92],'cuff':[49,104],'sole':[49,114],'trouser':[(50,76),(61,78),(58,91),(54,105),(44,106),(46,93)],'boot':[(44,101),(54,102),(56,109),(53,114),(44,114),(40,110),(41,106)]},
  right={'hip':[69,76],'knee':[73,88],'cuff':[77,94],'sole':[77,103],'trouser':[(63,76),(74,75),(79,87),(81,96),(71,99),(67,90)],'boot':[(71,92),(80,91),(85,97),(82,102),(74,104),(69,100)]}),
 dict(name='02-left-passing',upper=2,bob=-1,
  left={'hip':[56,76],'knee':[54,86],'cuff':[55,93],'sole':[55,102],'trouser':[(50,75),(61,77),(60,86),(60,95),(49,97),(47,87)],'boot':[(49,91),(58,91),(63,97),(61,101),(53,103),(47,99),(46,96)]},
  right={'hip':[69,75],'knee':[70,94],'cuff':[71,105],'sole':[71,114],'trouser':[(63,75),(74,75),(77,93),(77,106),(65,108),(64,94)],'boot':[(65,102),(75,103),(80,109),(77,114),(68,115),(62,111),(62,107)]}),
 dict(name='04-contact-left-forward',upper=4,bob=0,
  left={'hip':[56,77],'knee':[58,88],'cuff':[60,94],'sole':[61,103],'trouser':[(50,76),(61,77),(64,85),(65,96),(56,99),(53,91)],'boot':[(54,91),(63,91),(70,96),(68,101),(59,104),(53,100)]},
  right={'hip':[69,76],'knee':[71,93],'cuff':[72,105],'sole':[72,115],'trouser':[(63,76),(74,75),(78,92),(78,108),(67,108),(66,93)],'boot':[(67,103),(77,103),(81,109),(78,115),(69,116),(64,111),(64,107)]}),
 dict(name='06-right-passing',upper=6,bob=-1,
  left={'hip':[56,76],'knee':[54,94],'cuff':[53,105],'sole':[53,114],'trouser':[(50,75),(61,77),(61,93),(59,107),(47,108),(47,94)],'boot':[(47,103),(57,103),(62,109),(60,114),(50,116),(44,111),(44,107)]},
  right={'hip':[69,75],'knee':[74,86],'cuff':[75,93],'sole':[76,102],'trouser':[(63,75),(74,75),(80,85),(80,96),(69,98),(67,88)],'boot':[(69,91),(78,90),(84,96),(82,101),(74,103),(68,99)]})]
colors={'left':((147,59,107,255),(240,95,178,255),(255,175,218,255)),'right':((23,122,143,255),(61,208,226,255),(156,247,255,255))}
sheet=Image.new('RGBA',(256,256),(0,0,0,0))
for i,p in enumerate(poses):
 im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im)
 # Draw rear before front according to visual occlusion, including complete boots.
 for leg in (['right','left'] if i==2 else ['left','right']):
  a=p[leg];tr,boot,light=colors[leg]
  d.polygon(a['trouser'],fill=tr)
  d.polygon(a['boot'],fill=boot)
  cx,cy=a['cuff'];d.line([(cx-4,cy),(cx+4,cy-1)],fill=light,width=2)
  sx,sy=a['sole'];d.line([(sx-4,sy),(sx+3,sy-1)],fill=light,width=2)
 # Existing NE paint supplies view/identity placement only, not final limb art.
 upper=Image.open(root/'inputs/current'/f"{p['upper']:02}.png").convert('RGBA')
 upper.putalpha(upper.getchannel('A').point(lambda x:x))
 upper.paste((0,0,0,0),(0,78,128,128))
 im.alpha_composite(upper,(0,p['bob']))
 sheet.alpha_composite(im,((i%2)*128,(i//2)*128))
 im.save(root/'inputs'/f'guide-{i*2:02}.png')
sheet.resize((1024,1024),Image.Resampling.NEAREST).save(root/'inputs'/'four-key-filled-guide.png')
(root/'pose-guide.json').write_text(json.dumps({'stage':[128,128],'pivot':[64,112],'layout':'2x2 row-major 00,02,04,06','leg_colors':'magenta viewer-left hip; cyan viewer-right hip; labels are guide only','poses':poses},indent=2)+'\n')
# Current contact reference enlarged without changing its native clusters.
Image.open(root/'inputs/current/00.png').resize((512,512),Image.Resampling.NEAREST).save(root/'inputs'/'northeast-view-reference.png')
