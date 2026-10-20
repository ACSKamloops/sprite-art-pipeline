#!/usr/bin/env python3
"""Measure actual full source foot material in GPU readbacks, not only anchors.
Requires each flat contact annotation to include foot_mask (relative to contact JSON).
Reports movement within held poses and changed world material across source poses.
Does not equate artistic foot deformation with collision failure.
"""
import json,pathlib
import numpy as np
from PIL import Image
p=pathlib.Path(__file__).resolve().parent
config=json.loads((p/'runtime-config.json').read_text()); cp=p/config['contacts'].replace('res://','');m=json.loads((p/'selected/manifest.json').read_text())
r=json.loads((p/'CONTACT-CAPTURE-RECORDS.json').read_text());out=[];previous={};groups={}
for row in r['records']:
 c=row['contact']
 if not c.get('flat'):continue
 maskpath=cp.parent/c['foot_mask'];maskim=np.array(Image.open(maskpath).convert('RGBA'));visibleim=np.array(Image.open(cp.parent/c['visible_foot_mask']).convert('RGBA'));src=np.array(Image.open(p/'selected'/m['frames'][row['pose']]['file']).convert('RGBA'))
 foot_opaque=maskim[:,:,3]==255
 visible_foot=visibleim[:,:,3]==255
 assert np.all(foot_opaque[visible_foot]), 'visible ownership exceeds full foot'
 assert np.array_equal(visibleim[visible_foot],src[visible_foot]), 'explicit visible foot material disagrees with composite source'
 hidden_foot_texels=int((foot_opaque&~visible_foot).sum())
 assert int(foot_opaque.sum())==c['ownership']['full_pixels']
 assert int(visible_foot.sum())==c['ownership']['visible_pixels']
 assert hidden_foot_texels==c['ownership']['occluded_pixels']
 partial_alpha_texels=int(((maskim[:,:,3]>0)&(maskim[:,:,3]<255)).sum())
 mask=visible_foot
 scale=int(row['scale']);mask=np.repeat(np.repeat(mask,scale,0),scale,1);expanded=np.repeat(np.repeat(src,scale,0),scale,1)
 # Rendering nearest CanvasItem translation uses nearest texel placement. Check
 # candidate raster roots around the fractional physical+draw position against
 # every selected material pixel, then retain actual matched GPU pixels.
 origin=[row['root'][i]+row['correction'][i]-row['pivot'][i]*scale for i in range(2)]
 im=np.array(Image.open(p/row['file'].replace('res://','')).convert('RGBA'));yy,xx=np.nonzero(mask)
 best=None
 for ox in {int(np.floor(origin[0])),int(np.ceil(origin[0]))}:
  for oy in {int(np.floor(origin[1])),int(np.ceil(origin[1]))}:
   wx,wy=xx+ox,yy+oy;inside=(wx>=0)&(wy>=0)&(wx<im.shape[1])&(wy<im.shape[0])
   if not inside.all():continue
   matches=np.all(im[wy,wx,:3]==expanded[yy,xx,:3],axis=1);ratio=float(matches.mean()) if len(matches) else 0
   if best is None or ratio>best[0]:best=(ratio,wx,wy,im[wy,wx,:3])
 assert best is not None and len(xx)>0
 ratio,wx,wy,rgb=best;material={(int(x),int(y),*map(int,col)) for x,y,col in zip(wx,wy,rgb)}
 key=(row['mode'],row['loop'],row['pose']);groups.setdefault(key,[]).append(material)
 ep=(row['mode'],row['loop'],str(c['episode']));prev=previous.get(ep)
 changed=None if prev is None else len(material.symmetric_difference(prev));previous[ep]=material
 out.append({'sample':row['sample'],'mode':row['mode'],'pose':row['pose'],'fraction':row['fraction'],'opaque_foot_texels':len(xx),'occluded_source_foot_texels':hidden_foot_texels,'partial_alpha_source_foot_texels':partial_alpha_texels,'source_material_rgb_match_ratio':ratio,'changed_world_material_pixels_from_previous_episode_sample':changed,'correction':row['correction']})
summary=[]
for key,sets in groups.items():summary.append({'mode':key[0],'loop':key[1],'pose':key[2],'max_changed_material_pixels_within_held_pose':max(len(s.symmetric_difference(sets[0])) for s in sets)})
report={'scope':'All visible isolated opaque FOOT material world-coordinate GPU samples; explicit known-layer ownership masks select visible pixels; source material RGB is asserted after ownership selection and never infers visibility. Fractional-hold movement and across-pose material changes reported independently. No calf/cuff, target-only or collision-anatomy claim. Transparent/partial-alpha foot pixels excluded and counted separately by mask design.','samples':out,'held_pose_summary':summary,'all_foot_source_rgb_matched':all(x['source_material_rgb_match_ratio']==1 for x in out)}
(p/'CONTACT-MATERIAL-MEASUREMENTS.json').write_text(json.dumps(report,indent=2));print('measured',len(out),'flat-foot samples; source RGB exact',report['all_foot_source_rgb_matched']);assert report['all_foot_source_rgb_matched']
