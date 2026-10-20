#!/usr/bin/env python3
"""Record current declared pilot rules; does not derive thresholds from passing art."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    study=ROOT/'study/layered-cutout';p=json.loads((study/'project.json').read_text());observations=json.loads((study/'observations.json').read_text());obs={o['id']:o for o in observations};hashes={}
    def entry(path):
        rel=path.relative_to(ROOT).as_posix();digest=hashlib.sha256(path.read_bytes()).hexdigest();hashes[rel]=digest;return {'path':rel,'sha256':digest}
    for path in [study/'project.json',study/'observations.json',study/'assets/rig.json',study/'cutout_rig.gd']:entry(path)
    order=['rear_thigh','rear_shin','rear_foot','rear_arm','torso','head','front_thigh','front_shin','front_foot','front_arm','front_forearm'];frames={}
    for frame in p['frames']:
        fid=frame['id'];joints=[]
        for side in ['front','rear']:
            for name,a,b,key in [('knee',side+'_thigh',side+'_shin',side+'_shin'),('ankle',side+'_shin',side+'_foot',side+'_foot')]:
                x,y=obs[fid]['snapshot']['parts'][key]['position'];joints.append({'name':side+'_'+name,'a':a,'b':b,'roi':[int(x)-8,int(y)-8,int(x)+9,int(y)+9],'annotation_basis':'Rig places these named parts at this joint; overlap/gap is evidence, not anatomical acceptance'})
        frames[fid]={'landmarks':{name:[round(v)for v in data['position']]for name,data in obs[fid]['snapshot']['parts'].items()},'duration_ticks':5,'composite':entry(study/'rendered'/f'{fid}-composite.png'),'layers':{l['id']:entry(study/'rendered'/f"{fid}-{l['id']}.png")for l in p['layers']},'joints':joints}
    actions=[]
    for anim in p['animations']:
        walk=anim['id']=='walk';contacts=[]
        for side in ['front','rear']:
            stance=[f for i,f in enumerate(anim['frames'])if not walk or(i/12+(.5 if side=='rear'else 0))%1<.5]
            contacts.append({'layer':side+'_foot','stance_frames':stance,'ground_row':139,'max_ground_error_px':0,'max_boundary_slip_px':0.01,'max_hold_slip_px':0.5})
        actions.append({'id':anim['id'],'sequence':anim['frames'],'fps':anim['fps'],'loop':anim['loop'],'root_speed_px_s':48 if walk else 0,'world_motion':'continuous','contacts':contacts,'basis':'Rig stance p<0.5; specified 48px/s walk, zero stationary attack; ground boundary140 means opaque row139. Hold slip0.5px is an explicit QC requirement, not a measurement fitted to this fixture.'})
    ann={'schema':'sprite-pixel-motion-annotations/v1','canvas':p['canvas'],'layer_order':order,'palette_sha256':hashlib.sha256(json.dumps(p['palette'],separators=(',',':')).encode()).hexdigest(),'alpha_threshold':128,'edge_margin':1,'frames':frames,'actions':actions,'source_hashes':hashes,'unresolved':['No anatomical/material seam acceptance thresholds: joint ROIs only evidence.','Spriteworld motion continuous is explicit; a stepped-root policy produces different intra-hold results.','Attack windup/contact/recovery are authored and not native gameplay events.']}
    target=Path(__file__).parent/'study-annotations.json';target.write_text(json.dumps(ann,indent=2)+'\n')
    material={'schema':'sprite-material-annotations/v1','review_source':'native/authoring-review/localized-knee-review.json','samples':[{'xy':list(xy),'label':'reviewer identified blue trouser cloth','criterion':'blue_exceeds_red','source_observation':list(__import__('PIL.Image',fromlist=['Image']).open(ROOT/'study/ai-local-edit/source.png').convert('RGBA').getpixel(xy))}for xy in [(61,98),(60,99),(59,100)]],'scope':'Not a global color classifier; exact independently reviewed coordinates only.'}
    (Path(__file__).parent/'material-annotations.json').write_text(json.dumps(material,indent=2)+'\n')
if __name__=='__main__':main()
