from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;R=Q/'sourcefield-probe-v1';O=Q/'literal31-completion-v1'
def a(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
V=O/'verification';V.mkdir(exist_ok=False);(V/'replay').mkdir()
journal=json.loads((O/'LITERAL-UNDERCOAT-JOURNAL.json').read_text());base=json.loads((R/'CONSTRUCTION-RECEIPT.json').read_text());guide=json.loads((Q/'generation-guide-v1/INPUT-ROLES.json').read_text());rows=[];pins=[]
for i in range(8):
 source=a(Q/f'inputs/current/{i:02}.png');before=a(R/f'frames/{i:02}.png');expected=a(O/f'frames/{i:02}.png');undercoat=np.zeros_like(source);coords=[]
 for edit in journal['edits']:
  if edit['phase']!=i:continue
  x,y=edit['at'];sx,sy=edit['donor']['at'];assert before[y,x].tolist()==edit['before_rgba']==[0,0,0,0];assert sha(Q/f'inputs/current/{i:02}.png')==edit['donor']['sha256'];assert source[sy,sx].tolist()==edit['new_rgba'];undercoat[y,x]=source[sy,sx];coords.append([x,y])
 assert np.array_equal(undercoat,a(O/f'layers/{i:02}-new-authored-undercoat.png'))
 result=undercoat.copy()
 for name in ['fixed-lower','left-mapped-cloth','right-mapped-cloth','body-rigid']:
  p=R/f'layers/{i:02}-{name}.png';layer=a(p);use=layer[...,3]>0;result[use]=layer[use];pins.append({'phase':i,'role':name,'file':str(p.relative_to(Q)),'sha256':sha(p),'unchanged_sourcefield_component':True})
 assert np.array_equal(result,expected);assert np.array_equal(expected[before[...,3]>0],before[before[...,3]>0]);assert np.array_equal(expected[99:],source[99:])
 output=V/f'replay/{i:02}.png';Image.fromarray(result).save(output);assert sha(output)==sha(O/f'frames/{i:02}.png')
 changed=np.any(before!=expected,axis=2);assert int(changed.sum())==len(coords)
 if i not in [2,6]:assert sha(O/f'frames/{i:02}.png')==sha(R/f'frames/{i:02}.png')
 cloth_losses=[v for v in base['phases'][i]['new_clear_y76plus']if v['old_owner']=='cloth'and expected[v['at'][1],v['at'][0],3]==0]
 residual_amber=[]
 for spec in guide['masks']:
  if spec['phase']==i and spec['role']=='uncertain-waist-or-ownership':
   for x,y in spec['coordinates']:
    if expected[y,x,3]==0:residual_amber.append([x,y])
 rows.append({'phase':i,'changed_pixels':int(changed.sum()),'all_existing_positive_probe_pixels_exact':True,'fixed_components_replay_exact':True,'rows99plus_equal_selected_source':True,'other6_probe_PNG_bytes_exact':True if i not in [2,6]else None,'remaining_original_mutable_cloth_loss_witnesses':cloth_losses,'remaining_amber_clear_coordinates':residual_amber,'replay_RGBA_and_PNG_bytes_exact':True,'output_sha256':sha(output)})
assert sum(v['changed_pixels']for v in rows)==31
(V/'EXISTING-COMPONENT-LAYERS.json').write_text(json.dumps(pins,indent=2)+'\n')
(V/'RESULT.json').write_text(json.dumps({'status':'REJECTED after31pixel seam completion; green coverage solved but unapproved amber/cloth losses remain','all31_approved_green_targets_now_positive':True,'new_paint_pixels':31,'curve_unchanged_from_rejected_raw':True,'no_existing_positive_pixel_overwritten':True,'semantic_complete_boot_owner_certificate':False,'fixed_component_and_visible_probe_boot_paint_preserved':'All32 retained body/lower/cloth layers replay unchanged and every existing positive probe pixel remains exact; original complete anatomical boot ownership was not resolved.','phases':rows},indent=2)+'\n')
print(json.dumps({'authored':31,'all8_replay_exact':True,'remaining_amber':[len(v['remaining_amber_clear_coordinates'])for v in rows],'remaining_mutable_cloth_losses':[len(v['remaining_original_mutable_cloth_loss_witnesses'])for v in rows]},indent=2))
