"""One conservative current-source NE06 charcoal knee/cuff repair; no boot move."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
for name in ['raw','final']:(R/name).mkdir(exist_ok=True)
def a(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=a(R/'inputs/current/06.png');donor=a(R/'inputs/current/07.png');z=np.load(R/'inputs/source/source-map06.npz')
# Literal locations, inspected in the actual current source grid. These13
# samples all belong to the previous projected charcoal field, not boot paint.
shade=[((60,85),(70,84)),((61,85),(71,84)),((60,86),(71,84)),((61,86),(72,84)),
 ((60,87),(70,85)),((61,87),(71,85)),((62,87),(72,85)),((60,88),(72,86)),
 ((61,88),(73,86)),((62,88),(72,86)),((60,89),(71,86)),((61,89),(72,86)),((62,89),(71,87))]
# Five bounded charcoal contour placements round the existing inward step.
# These are authored cuff coverage in previously transparent cells; the open
# channel to the donor Q boot continues below/beside them, not filled globally.
under=[((59,87),(69,86)),((59,88),(69,87)),((60,90),(70,87)),((61,90),(69,87)),((61,91),(69,87))]
owner=np.zeros((128,128),bool);underowner=np.zeros_like(owner);layer=np.zeros_like(base);mp=np.full((128,128,2),-1,np.int16);ops=[]
for role,plan in [('existing projected cloth plane',shade),('authored small charcoal cuff underpaint',under)]:
 for (x,y),(sx,sy)in plan:
  assert not owner[y,x];assert 59<=x<=66 and 84<=y<=95
  if role.startswith('existing'):assert int(z['source_id'][y,x])==7 and base[y,x,3]==255
  else:assert base[y,x].tolist()==[0,0,0,0] and int(z['source_id'][y,x])==-1;underowner[y,x]=True
  assert donor[sy,sx,3]==255
  owner[y,x]=True;layer[y,x]=donor[sy,sx];mp[y,x]=[sx,sy]
  ops.append({'destination':[x,y],'actual_before_RGBA':base[y,x].tolist(),'retained_before_source_id':int(z['source_id'][y,x]),'retained_before_source_xy':z['source_xy'][y,x].tolist(),
   'new_source_file':'inputs/current/07.png','new_source_xy':[sx,sy],'literal_source_RGBA':donor[sy,sx].tolist(),'new_RGBA':donor[sy,sx].tolist(),
   'material':'charcoal trouser/cuff shaded surface','role':role,'authored_shape_or_shading':True,
   'depth':'local cloth/cuff plane beside and above fixed positive P leather and fixed Q donor boot; no brown boot sample is replaced',
   'anatomy_limit':'Source-colored authored knee/cuff interpretation, not recovery of a hidden joint.'})
raw=base.copy();out=base.copy();out[owner]=layer[owner]
# No boot, otherleg, sash or upper texel is displaced, erased or recolored.
powner=np.array(Image.open(R/'inputs/source/P-owner06.png'))>0
Ppositive=powner&(base[:,:,3]>0)
Qpositive=(a(R/'inputs/source/Q-boot06.png')[:,:,3]>0)
upper=(a(R/'inputs/source/upper06.png')[:,:,3]>0)|(np.array(Image.open(R/'inputs/source/sash06.png'))>0)
assert not np.any(owner&Ppositive);assert not np.any(owner&Qpositive);assert not np.any(owner&upper)
assert np.array_equal(out[Ppositive],base[Ppositive]);assert np.array_equal(out[Qpositive],base[Qpositive]);assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[~owner],base[~owner])
assert np.array_equal(np.any(out!=base,axis=2),owner)
for path,data in [('raw/06.png',raw),('raw/charcoal-repair-layer.png',layer),('final/06.png',out)]:Image.fromarray(data).save(R/path)
assert (R/'raw/06.png').read_bytes()==(R/'inputs/current/06.png').read_bytes()
for path,mask in [('masks/literal-edit-owner.png',owner),('masks/new-charcoal-coverage.png',underowner),('masks/retained-positive-P-boot.png',Ppositive),('masks/retained-positive-Q-boot.png',Qpositive),('masks/upper-sash-protected.png',upper)]:Image.fromarray(mask.astype('uint8')*255).save(R/path)
np.savez_compressed(R/'maps/literal-cuff-repair.npz',source_xy=mp,owner=owner,underpaint_owner=underowner,source_RGBA=donor,original06_RGBA=base)
receipt={'status':'ONE unselected conservative cuff repair for root inspection; no fullcycle/editor/rating',
 'source06_sha256':sha(R/'inputs/current/06.png'),'source07_sha256':sha(R/'inputs/current/07.png'),'candidate06_sha256':sha(R/'final/06.png'),
 'changed_RGBA_samples':len(ops),'existing_cloth_shading_samples':len(shade),'authored_charcoal_underpaint_samples':len(under),
 'new_palette_colors':0,'brown_boot_samples_moved_erased_or_recolored':0,'P_positive_boot_RGBA_exact':True,'Q_positive_boot_RGBA_exact':True,'upper_sash_RGBA_exact':True,
 'outside18_exact':True,'otherleg_geometry_unchanged':True,'actual_boot_geometry_unchanged':True,
 'alpha_change':'only five declared previously transparent cuff cells become sourceopaque charcoal; all other alpha exact',
 'large_negative_channel_retained':True,'ambiguous_tail_coordinates_unchanged':[[63,100],[63,101],[64,101],[62,102],[63,102],[64,102]],
 'gray_side_projection':'legitimate existing cloth untouched, not blanket-erased',
 'view_registration':'original128stage/pivot64,112; no fitting, warps, translation or reflections',
 'clock':{'original_equal_hold':[9,160],'cycle':[9,20],'change':False},'models':0,'canonical_edits':0,'operations':ops}
(R/'CUFF-RECIPE.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k]for k in ['candidate06_sha256','changed_RGBA_samples','existing_cloth_shading_samples','authored_charcoal_underpaint_samples','P_positive_boot_RGBA_exact','Q_positive_boot_RGBA_exact','upper_sash_RGBA_exact']},indent=2))
