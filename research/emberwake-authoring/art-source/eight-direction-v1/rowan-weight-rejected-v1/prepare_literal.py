from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
Q=Path(__file__).resolve().parent
# These native-coordinate outlines were read against all eight retained
# 10x joint grids. They trace visible cream cloth, excluding the leather.
POLYS={
0:{'left':[(47,79),(51,80),(57,83),(62,82),(61,87),(57,90),(52,90),(48,87),(47,83)],'right':[(62,79),(66,77),(69,78),(72,81),(76,79),(77,82),(77,91),(74,92),(68,92),(64,90),(62,85)]},
1:{'left':[(47,79),(51,79),(58,82),(62,81),(62,86),(58,90),(52,90),(48,88),(46,84)],'right':[(62,79),(66,77),(69,79),(73,80),(77,79),(78,83),(78,91),(75,92),(67,92),(63,89)]},
2:{'left':[(47,80),(52,82),(57,84),(61,83),(62,84),(60,87),(55,88),(50,87),(47,85)],'right':[(62,80),(66,78),(70,79),(72,82),(77,80),(78,84),(78,94),(75,97),(71,97),(67,94),(65,89),(62,86)]},
3:{'left':[(48,79),(53,81),(59,83),(63,81),(63,88),(61,93),(57,96),(51,96),(48,93),(48,87)],'right':[(63,80),(67,78),(71,80),(74,80),(76,78),(77,82),(77,89),(73,90),(66,90),(64,87)]},
4:{'left':[(48,80),(53,82),(59,84),(64,82),(64,90),(62,96),(55,96),(50,95),(48,91)],'right':[(64,80),(68,79),(71,82),(75,82),(77,80),(79,81),(80,84),(78,87),(75,88),(71,86),(68,86)]},
5:{'left':[(48,82),(53,83),(58,84),(63,84),(63,88),(61,92),(58,95),(54,95),(51,92),(50,88)],'right':[(66,83),(70,82),(73,81),(75,78),(77,78),(77,81),(79,82),(81,85),(81,89),(78,92),(73,92),(69,90),(67,87)]},
6:{'left':[(48,82),(53,83),(58,84),(63,83),(63,87),(60,91),(56,93),(51,92),(48,89),(47,86)],'right':[(72,75),(76,73),(81,73),(85,76),(85,82),(83,86),(80,88),(76,88),(72,85),(70,81)]},
7:{'left':[(47,80),(52,83),(58,84),(62,83),(62,86),(59,88),(54,89),(50,88),(47,85)],'right':[(63,79),(66,76),(68,77),(71,80),(73,80),(77,78),(80,80),(82,83),(82,87),(79,90),(75,90),(71,88),(67,85)]}}

def polygon(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
rows={};summary=[]
for i in range(8):
 a=np.array(Image.open(Q/f'inputs/current/{i:02}.png').convert('RGBA'))
 body=np.array(Image.open(Q/f'masks/{i:02}-proposed-body.png'))>0
 Y,X=np.indices((128,128));add=(a[...,3]>0)&(Y<=75)
 if i==6:add &=~polygon([(70,72),(82,71),(87,75),(87,87),(70,87)])
 if i==7:add &=~polygon([(64,74),(70,74),(73,79),(63,82)])
 body|=add
 union=np.zeros((128,128),bool);parts={}
 for name,poly in POLYS[i].items():
  core=polygon(poly)&(a[...,3]>0)&~body&~union;union|=core
  parts[name]={'literal_row_runs':{str(y):[[int(v[0]),int(v[-1])] for v in np.split(np.where(core[y])[0],np.where(np.diff(np.where(core[y])[0])>1)[0]+1) if len(v)]for y in range(128) if core[y].any()},'outline_guide':poly}
  Image.fromarray(core.astype('uint8')*255).save(Q/f'masks/{i:02}-{name}-literal-cloth.png')
 Image.fromarray(body.astype('uint8')*255).save(Q/f'masks/{i:02}-body-source-owner.png')
 fixed=a.copy();fixed[body|union]=0;Image.fromarray(fixed).save(Q/f'layers/{i:02}-fixed-source.png')
 rows[str(i)]=parts
 overlay=np.zeros_like(a);overlay[body]=[0,255,255,90];overlay[union]=[255,0,255,90];im=Image.new('RGBA',(128,128),'#e9e4d7');im.alpha_composite(Image.fromarray(a));im.alpha_composite(Image.fromarray(overlay));im.crop((28,70,96,116)).resize((680,460),Image.Resampling.NEAREST).convert('RGB').save(Q/f'inspection/{i:02}-literal-owner-overlay.png')
 summary.append({'phase':i,'body':int(body.sum()),'cloth':int(union.sum()),'fixed':int((fixed[...,3]>0).sum())})
(Q/'LITERAL-CLOTH-ROWS.json').write_text(json.dumps({'parts':rows,'inspection':'Native coordinate grids inspected; literal rows are authoritative, no RGB segmentation','curve':[1,0,-1,0]*2,'correction':[1,-1,-2,0]*2},indent=2)+'\n')
print(summary)
# Current fixed layer only exposes the source material excluded from motion.
b=Image.new('RGBA',(8*272,184),'#e9e4d7')
for i in range(8):b.alpha_composite(Image.open(Q/f'layers/{i:02}-fixed-source.png').crop((28,70,96,116)).resize((272,184),Image.Resampling.NEAREST),(i*272,0))
b.convert('RGB').save(Q/'inspection/fixed-lower-layer-4x.png')
