"""Replay the987-texel compact socket edit from the unchanged body texture."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/body-side-polish-v2/Material_0-side-polish-UV.png')
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='3f4db5046bda0e20194b2a8dbf5364176a9712bb2cc4e6ff9cd533a120a2f5d3'
args.output.mkdir(parents=True,exist_ok=False)
original=Image.open(SOURCE).convert('RGBA');before=np.asarray(original).copy()
mask_path=HERE/'candidates/owned-head-edit-mask.png'
mask=np.asarray(Image.open(mask_path))>0
image=original.copy();draw=ImageDraw.Draw(image)
polygon=[(29,1798),(51,1799),(61,1810),(61,1828),(53,1838),(32,1836),(23,1824),(23,1807)]
draw.polygon(polygon,fill=(77,88,103,255));draw.line(polygon+[polygon[0]],fill=(132,146,160,255),width=2)
draw.line([(54,1808),(50,1830),(34,1834)],fill=(39,47,59,255),width=2)
draw.ellipse((26,1803,49,1828),fill=(143,157,171,255));draw.ellipse((30,1807,45,1824),fill=(19,25,35,255))
draw.ellipse((33,1810,43,1821),fill=(206,38,30,255));draw.ellipse((35,1811,41,1816),fill=(247,76,42,255));draw.point((36,1812),fill=(255,176,114,255))
result=before.copy();result[mask]=np.asarray(image)[mask];result[:,:,3]=before[:,:,3]
assert np.array_equal(result[~mask],before[~mask])
assert np.array_equal(result[:,:,3],before[:,:,3])
changed=np.any(result!=before,axis=2)
Image.fromarray(result).save(args.output/'compact-steel-socket.png')
Image.fromarray(changed.astype('uint8')*255).save(args.output/'changed-mask.png')
recipe={'state':'UNAPPROVED_COMPACT_SOCKET_TRIAL','polygon':polygon,'edit_count':int(changed.sum()),'outside_owned_exact':True,'alpha_exact':True,'source_SHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'mask_SHA256':hashlib.sha256(mask_path.read_bytes()).hexdigest(),'script_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'texture_SHA256':hashlib.sha256((args.output/'compact-steel-socket.png').read_bytes()).hexdigest(),'reason':'Restore originaltemple/cheek/hair; concentrate steelrim/darksocket/redlens besideeye'}
(args.output/'recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
print('COMPACT_EDIT_REPLAY',recipe['edit_count'])
