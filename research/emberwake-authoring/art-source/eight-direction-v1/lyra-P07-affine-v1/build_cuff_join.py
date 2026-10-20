"""One explicit small source-connected charcoal field; preserve raw affine."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;O=R/'cuff-join-v1'
assert not O.exists(),'Preserve the first bounded join result.'
(O/'proof').mkdir(parents=True)
def a(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=a(R/'inputs/current/07.png');raw=a(R/'raw/07-affine-protected.png');part=a(R/'raw/P07-affine-layer.png')
protected=np.array(Image.open(R/'masks/upper-Q-protected.png'))>0
own=np.array(Image.open(R/'masks/P07-literal-source-owner.png'))>0
cuff=np.array(Image.open(R/'masks/P07-charcoal-cuff-owner.png'))>0
field=np.zeros_like(src);mask=np.zeros((128,128),bool);mp=np.full((128,128,2),-1,np.int16);ops=[]
# Only the actual top cuff gap directly between fixed hem row83 and affine
# cuff row86. The larger left arm/leg clearance is deliberately not filled.
rows={84:{'target_x0':69,'source_x':[66,67,68,69,70,71,72,76,77,78]},
      85:{'target_x0':70,'source_x':[66,67,68,69,70,71,77,77,78]}}
for y,rule in rows.items():
 for j,sx in enumerate(rule['source_x']):
  x=rule['target_x0']+j;sy=y
  assert raw[y,x,3]==0 and not protected[y,x] and own[y,x] and cuff[sy,sx]
  field[y,x]=src[sy,sx];mask[y,x]=True;mp[y,x]=[sx,sy]
  ops.append({'destination':[x,y],'before_raw_RGBA':raw[y,x].tolist(),'source_xy':[sx,sy],'source_RGBA':src[sy,sx].tolist(),
   'actual_original_destination_RGBA':src[y,x].tolist(),'material':'visible source07 charcoal cuff and terminal outline',
   'authored_paint_assignment':'source-connected cuff field, not recovered hidden anatomy',
   'depth':'behind the existing fixed hem/upper and affine P boot; outside Q; fills only actual proximal gap'})
out=raw.copy();out[mask]=field[mask]
assert np.array_equal(out[protected],src[protected]);assert np.array_equal(out[~mask],raw[~mask])
assert np.all(out[mask,3]==255) and not np.any((part[:,:,3]>0)&mask)
Image.fromarray(field).save(O/'charcoal-cuff-join-layer.png');Image.fromarray(mask.astype('uint8')*255).save(O/'charcoal-cuff-join-owner.png');Image.fromarray(out).save(O/'07.png')
np.savez_compressed(O/'charcoal-cuff-join-map.npz',source_xy=mp,owner=mask,source_RGBA=src)
receipt={'status':'one joined affine hypothesis for parent inspection; no art selection',
 'raw_affine_preserved_sha256':sha(R/'raw/07-affine-protected.png'),'raw_source_layer_preserved_sha256':sha(R/'raw/P07-affine-layer.png'),
 'join_pixels':len(ops),'new_RGB_colors':0,'join_RGBA_literal_source_samples':True,'field_is_authored_shape':True,
 'why_needed':'Raw part starts at row86, leaving a two-row open cut beneath current hem row83. This field connects only the authored P cuff projection at69..78/70..78; left clearance remains open.',
 'literal_target_rows':{84:[[69,78]],85:[[70,78]]},'negative_clearance_kept':{'84':[[66,68]],'85':[[66,69]],'86':[[65,69]],'87':[[65,69]],'88':[[63,68]]},
 'no_contour_cleanup_or_alpha_dilation':True,'no_rigid_boot_claim':True,'no_hidden_anatomy_claim':True,
 'upper_and_Q_RGBA_exact':True,'outside_join_vs_raw_RGBA_exact':True,'fixed_registration':True,'original06_and00_PNG_unchanged':True,
 'clock':{'original8holds':[9,160],'total':[9,20],'change':False},
 'candidate_sha256':sha(O/'07.png'),'changed_vs_original07_RGBA':int(np.any(out!=src,axis=2).sum()),'operations':ops}
(O/'JOIN-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k]for k in ['join_pixels','candidate_sha256','changed_vs_original07_RGBA','raw_affine_preserved_sha256']},indent=2))
