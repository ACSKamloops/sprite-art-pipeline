import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np
P=Path(__file__).resolve().parent;R=Path('/home/astra/projects/sprite-construction-lab/pilot');S=R/'captain-depth-projected-art-v1/artifacts/trial-v3-volume';B=R/'captain-boot-volume-binding-v1/artifacts/proxy-v2';r=json.loads((P/'report.json').read_text());sheet=Image.new('RGBA',(1024,1120),(38,43,49,255));draw=ImageDraw.Draw(sheet)
for j,i in enumerate(range(0,72,9)):
 actual=Image.open(S/'frames'/f'{i:03}.png');m=Image.new('RGBA',(256,256))
 for n,c in [('far_thigh',(210,140,40,255)),('far_shin',(210,140,40,255)),('far_boot',(170,100,20,255)),('near_thigh',(180,60,210,255)),('near_shin',(180,60,210,255)),('near_boot',(130,20,170,255))]:
  a=Image.open(P/'layers'/f'{i:03}-{n}.png').getchannel('A');colored=Image.new('RGBA',(256,256),c);colored.putalpha(a);m.alpha_composite(colored)
 for g in r['joint_neighborhoods']:
  if g['frame']==i:
   x,y=g['source_point'];ImageDraw.Draw(m).ellipse((x-2,y-2,x+2,y+2),outline=(0,255,100,255))
 x=(j%2)*512;y=(j//2)*280;sheet.alpha_composite(actual,(x,y));sheet.alpha_composite(m,(x+256,y));draw.text((x+3,y+259),f'{i}: actual composite / reconstructed lower layers + joint anchors',fill='white')
sheet.convert('RGB').save(P/'joint-evidence.png')
a=Image.open(B/'layers/000-far.png').convert('RGBA');shift=Image.new('RGBA',(256,256));shift.paste(a,(0,10));diff=ImageChops.difference(a,shift);b=Image.new('RGBA',(624,264),(38,43,49,255));crop=(72,190,176,256)
for j,im in enumerate([a,shift,diff]):b.alpha_composite(im.crop(crop).resize((208,132),Image.Resampling.NEAREST),(j*208,0))
ImageDraw.Draw(b).text((3,140),'Original / deliberate10px yshift / RGBA difference',fill='white');b.convert('RGB').save(P/'negative-boot-shift.png');r['negative_cases']['boot_shift_y_10_alpha_changed_pixels']=int(np.sum(np.array(a)[:,:,3]!=np.array(shift)[:,:,3]));r['negative_cases']['shift_rejected_by_exact_alpha_mask_comparison']=not np.array_equal(np.array(a)[:,:,3],np.array(shift)[:,:,3]);assert r['negative_cases']['shift_rejected_by_exact_alpha_mask_comparison']
blob=subprocess.check_output(['git','-C','/home/astra/projects/sprite-construction-lab','show','bc8fee9:pilot/captain-depth-projected-art-v1/render-volume.py']);r['inputs']['frozen_renderer_git_revision']='bc8fee9';r['inputs']['frozen_renderer_blob_sha256']=hashlib.sha256(blob).hexdigest();r['inputs']['renderer_sha256_scope']='Current file may contain later optionalcloth branches; frozenv3 producing default source is independently pinned bygitblob.'
files=list((S/'parts').glob('*.png'))+list((S/'upper-parts/complete').glob('*.png'));r['inputs']['source_piece_files']=[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in files];r['summary']={'fullsprite_exact_RGBA_frames':sum(x['changed_pixels']==0 for x in r['full_sprite_comparisons']),'boot_layers':len(r['boot_raster_comparisons']),'boot_changed_RGBA_pixels':sum(x['changed_pixels']for x in r['boot_raster_comparisons']),'boot_changed_alpha_pixels':sum(c['alpha_changed']for x in r['boot_raster_comparisons']for c in x['cases']),'all_boot_color_discrepancies_integer_UV_neighbor_texels':all(c['distance_to_integer_boundary']<1e-9 and c['actual_color_in_neighbor_texel']for x in r['boot_raster_comparisons']for c in x['cases']),'joint_checks':len(r['joint_neighborhoods']),'joint_overlap_zero_count':sum(not x['mask_overlap_pixels_within_8px']for x in r['joint_neighborhoods']),'contact_boundary_tolerance_px':1.5,'contact_witnesses_over_tolerance':sum((x['max_contact_vertex_to_opaque_pixel_center_px']or 0)>1.5 for x in r['contact_witnesses'])};# A support witness must reject actual displaced opaque material, independently of metadata.
poses=json.loads((R/'captain-depth-projected-art-v1/source/authored-poses-final.json').read_text())
boots=json.loads((B/'manifest.json').read_text());foot=boots['records'][0]['feet']['far']
world=np.array(foot['vertices_world']);xy=np.array(foot['vertices_pixels']);support=np.flatnonzero(abs(world[:,2])<1e-6)
yy,xx=np.nonzero(np.array(shift)[:,:,3]>0)
dist=[float(np.min(np.hypot(xx+.5-xy[j,0],yy+.5-xy[j,1]))) for j in support]
r['negative_cases']['shifted_support_max_distance_px']=max(dist)
r['negative_cases']['shift_rejected_by_1p5px_support_witness']=max(dist)>1.5
# Down-shifted bulk may still cover an old support point: this is a real limitation.
up=Image.new('RGBA',(256,256));up.paste(a,(0,-10));uy,ux=np.nonzero(np.array(up)[:,:,3]>0)
udist=[float(np.min(np.hypot(ux+.5-xy[j,0],uy+.5-xy[j,1]))) for j in support]
r['negative_cases']['upshift_10_support_max_distance_px']=max(udist)
r['negative_cases']['upshift_rejected_by_1p5px_support_witness']=max(udist)>1.5
assert r['negative_cases']['upshift_rejected_by_1p5px_support_witness']
r['limits'].append('Opaque proximity alone can miss a downward boot translation when shifted bulk still covers old support vertices; exact raster/hash comparison detects it.')
assert r['summary']['fullsprite_exact_RGBA_frames']==72
assert r['summary']['boot_changed_alpha_pixels']==0
assert r['summary']['joint_overlap_zero_count']==0
assert r['summary']['contact_witnesses_over_tolerance']==0
r['reviewer']='independent temporal-review agent'
r['review_date']='2026-10-08'
r['engineering_decision']='bounded_checks_pass_with_85_UV_color_boundary_discrepancies'
r['visual_inspection']={'frames':[0,9,18,27,36,45,54,63], 'evidence':'joint-evidence.png', 'scope':'Eight fixed-canvas actual composites and colored reconstructed joint masks personally inspected; no complete temporal/art review.', 'observations':['No detached visible boot or open ankle hole apparent in these eight composites.', 'Far knee silhouette becomes a narrow angular plate near frames36/45; mask overlap cannot prove persuasive armor depth.', 'Near knee and upper shin remain substantially concealed by hanging gear/shield in some poses; concealed anchor overlap does not establish exposed joint craft.']}
r['held_source_world_plant_proven']=False
r['art_approval']=False
(P/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(r['summary']);print(r['negative_cases'])
