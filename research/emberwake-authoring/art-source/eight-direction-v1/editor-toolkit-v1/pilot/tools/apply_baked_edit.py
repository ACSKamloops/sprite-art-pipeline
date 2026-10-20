#!/usr/bin/env python3
"""Project journal -> isolated baked-frame candidate; never mutate reviewed exports."""
import argparse, hashlib, json, runpy, shutil, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sprite_lab import History, project_hash, render_frame
from sprite_lab.loading import load_project, load_json

def sha(data): return hashlib.sha256(data).hexdigest()
def contained(root, name):
    path = (root / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError('Asset path escapes its project: ' + name)
    return path
def apply(rig, original, edited, journal, frame_id, binding, tick, output):
    if output.exists(): raise ValueError('Use a fresh candidate project directory')
    if output.is_relative_to(rig) or rig.is_relative_to(output): raise ValueError('Candidate and source trees must not overlap')
    source = load_project(original.read_text()); candidate = load_project(edited.read_text())
    if project_hash(History.replay(source, load_json(journal.read_text())).project) != project_hash(candidate):
        raise ValueError('Edited project does not match its journal')
    generated = rig / 'generated'
    isolated_file = generated / 'isolated/manifest.json'
    isolated = json.loads(isolated_file.read_text())
    if sha(isolated_file.read_bytes()) != source['provenance']['isolation_manifest_sha256']:
        raise ValueError('Stale isolation project')
    if set(source['provenance'].get('source_bindings', {})) != {'rig.gd','bake.gd','design.json','clips.json'}:
        raise ValueError('Editable project requires all source bindings')
    for name, expected in source['provenance']['source_bindings'].items():
        if sha((rig / name).read_bytes()) != expected: raise ValueError('Stale source: ' + name)
    if candidate['provenance'] != source['provenance']: raise ValueError('Changed candidate provenance')
    if set(candidate) != set(source) or any(candidate[k] != source[k] for k in source if k not in ('palette', 'cels')):
        raise ValueError('Only pixel/palette edits are supported; timing/layer/project metadata changed')
    if set(candidate['cels']) != set(source['cels']): raise ValueError('Cel structure changed')
    for name, cel in source['cels'].items():
        if set(candidate['cels'][name]) != set(cel) or any(candidate['cels'][name][k] != cel[k] for k in cel if k != 'pixels'):
            raise ValueError('Nonpixel cel metadata changed')
    manifest = json.loads((generated / 'manifest.json').read_text())
    if 'pixel_overrides' in manifest: raise ValueError('Rebase against original exports; cumulative overrides unsupported')
    if set(manifest.get('source_bindings', {})) != {'rig.gd','bake.gd','build_exports.py','design.json','clips.json'}:
        raise ValueError('Export requires all source bindings')
    for name, expected in manifest['source_bindings'].items():
        if sha((rig / name).read_bytes()) != expected: raise ValueError('Stale rendered source: ' + name)
    for clip in manifest['clips'].values():
        for name in [clip['atlas'], *[row['png'] for row in clip['frames']]]:
            contained(generated, name); contained(output / 'generated', name)
    for row in isolated['poses']: contained(generated, row['full_png'])
    if binding not in manifest['clips']: raise ValueError('Unsupported clip/view')
    if binding in ['walk/right','run/right','walk/left','run/left']:
        raise ValueError('Locomotion pixel edits require a new measured contact cache; unsupported by this example')
    rows = manifest['clips'][binding]['frames']
    if isinstance(tick,bool) or not isinstance(tick,int) or not 0 <= tick < len(rows): raise ValueError('Invalid tick')
    sample = next((x for x in isolated['poses'] if x['id'] == frame_id),None)
    if not sample or sample['clip'] + '/' + sample['view'] != binding or sample['tick'] != tick or sample['full_pixel_sha256'] != rows[tick]['pixel_sha256']: raise ValueError('Frame does not match explicit clip/view/tick')
    frame_ids = [x['id'] for x in source['frames']]
    if [x['id'] for x in candidate['frames']] != frame_ids: raise ValueError('Changed frame structure')
    for other in frame_ids:
        if other != frame_id and render_frame(source,other).tobytes() != render_frame(candidate,other).tobytes():
            raise ValueError('Other displayed pose changed; select and review overrides separately')
    old = Image.open(generated / rows[tick]['png']).convert('RGBA')
    if render_frame(source,frame_id).tobytes() != old.tobytes(): raise ValueError('Original editable frame does not reconstruct baked pixels')
    new = render_frame(candidate,frame_id).convert('RGBA')
    if new.size != old.size: raise ValueError('Changed canvas')
    if new.getchannel('A').crop((0,170,192,192)).getbbox(): raise ValueError('Candidate penetrates declared floor')
    changed = [i for i,(a,b) in enumerate(zip(old.get_flattened_data(),new.get_flattened_data())) if a != b]
    if not changed: raise ValueError('No visible correction')
    # Copy only project sources and current exported textures/resources; omit old review/proof/isolation receipts.
    output.mkdir(parents=True)
    for path in rig.iterdir():
        if path.is_file() and path.suffix in ['.gd','.json','.tscn','.godot','.py']: shutil.copy2(path,output/path.name)
    (output/'generated').mkdir()
    # Actual exports may use a different atlas subfolder; copy only referenced files.
    for clip in manifest['clips'].values():
        for name in [clip['atlas'], *[f['png'] for f in clip['frames']]]:
            dst=output/'generated'/name;dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists(): shutil.copy2(generated/name,dst)
    cp=output/'contact-proof';cp.mkdir();shutil.copy2(rig/'contact-proof/held-sole-cache.json',cp/'held-sole-cache.json')
    row=rows[tick];new.save(output/'generated'/row['png']);row['pixel_sha256']=sha(new.tobytes())
    c=manifest['clips'][binding];atlas=Image.open(output/'generated'/c['atlas']).convert('RGBA')
    x,y,w,h=row['region'];atlas.paste(new,(x,y));atlas.save(output/'generated'/c['atlas']);c['atlas_pixel_sha256']=sha(atlas.tobytes())
    manifest['pixel_overrides']=[{'binding':binding,'tick':tick,'frame_id':frame_id,'original_pixel_sha256':sha(old.tobytes()),'candidate_pixel_sha256':sha(new.tobytes()),'editable_project_sha256':project_hash(candidate),'journal_sha256':sha(journal.read_bytes()),'art_approved':False}]
    (output/'generated/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    runpy.run_path(str(rig/'build_exports.py'))['write_frames'](manifest,output/'generated')
    (output/'generated/build-receipt.json').write_text(json.dumps({'schema':'baked-edit-build/v1', 'manifest_sha256':sha((output/'generated/manifest.json').read_bytes()), 'frames_tres_sha256':sha((output/'generated/frames.tres').read_bytes()), 'source_bindings':manifest['source_bindings'], 'art_approved':False},indent=2)+'\n')
    verify=runpy.run_path(str(rig/'verify_exports.py'))['verify'](output/'generated')
    if not verify['passed']: raise ValueError('Candidate atlas/resource verification failed')
    (output/'generated/export-validation.json').write_text(json.dumps(verify,indent=2)+'\n')
    report={'schema':'baked-pixel-edit-proof/v1','passed':True,'binding':binding,'tick':tick,'changed_coordinates':[[i%192,i//192] for i in changed], 'source_manifest_sha256':sha((generated/'manifest.json').read_bytes()),'candidate_manifest_sha256':sha((output/'generated/manifest.json').read_bytes()),'candidate_project_sha256':project_hash(candidate),'candidate_rgba_sha256':sha(new.tobytes()),'unchanged_frames':sum(len(c['frames']) for c in manifest['clips'].values())-1,'art_approved':False,'limits':['One explicit pose/tick override; no automatic painting across motion','Old body-rig pixel oracle intentionally differs at corrected tick; use dedicated candidate GPU check','Locomotion overrides require remeasured contact evidence','Candidate requires fresh temporal art review']}
    (output/'generated/pixel-edit-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('rig',type=Path);p.add_argument('original',type=Path);p.add_argument('edited',type=Path);p.add_argument('journal',type=Path);p.add_argument('--frame',required=True);p.add_argument('--binding',required=True);p.add_argument('--tick',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=apply(a.rig.resolve(),a.original,a.edited,a.journal,a.frame,a.binding,a.tick,a.output.resolve())
    print(json.dumps({k:report[k] for k in ['passed','binding','tick','changed_coordinates','unchanged_frames']}))
if __name__=='__main__': main()
