#!/usr/bin/env python3
"""Build one full, source-bound animation into the lossless fine editor."""
import argparse
import hashlib
import json
import runpy
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sprite_lab import canonical_json
from sprite_lab.core import render_frames


def sha(raw):return hashlib.sha256(raw).hexdigest()


def build(source, isolation, output):
    source=source.resolve(); isolation=isolation.resolve(); output=output.resolve()
    if output.exists():raise ValueError('Use a fresh editor project directory')
    raw=(isolation/'isolation.json').read_bytes(); report=json.loads(raw)
    if report['schema']not in ['editable-full-clip-isolation/v1','editable-full-clip-isolation/v2']:raise ValueError('Unsupported isolation')
    manifest_path=source/'generated/manifest.json'; manifest=json.loads(manifest_path.read_text())
    if sha(manifest_path.read_bytes())!=report['bake_manifest_sha256']:raise ValueError('Bake changed after isolation')
    if manifest['source_bindings']!=report['source_bindings']:raise ValueError('Source binding mismatch')
    for name, digest in report['source_bindings'].items():
        if sha((source/name).read_bytes())!=digest:raise ValueError('Stale source: '+name)
    clip=manifest['clips'][report['binding']]
    header={'name':clip['name'],'base_clip':clip.get('base_clip',clip['name']),
            'equipment_selection':clip.get('equipment_selection',''),'view':clip['view'],
            'duration_ticks':clip['duration_ticks'],'loop':clip['loop'],'events':clip['events']}
    expected=clip if report['schema'].endswith('/v1')else header
    if expected!=report['clip'] or len(report['poses'])!=len(clip['frames']):raise ValueError('Incomplete or mismatched clip')
    def contained(name):
        p=(isolation/name).resolve()
        if Path(name).is_absolute() or not p.is_relative_to(isolation):raise ValueError('Escaping asset')
        return p
    records=[];frames=[];order=report['layer_order']
    for pose, baked in zip(report['poses'],clip['frames']):
        if pose['tick']!=baked['tick'] or pose['duration_ticks']!=baked['duration_ticks']:raise ValueError('Tick or hold mismatch')
        if [x['id'] for x in pose['layers']]!=order:raise ValueError('Layer order mismatch')
        images=[{'png':pose['full_png'],'pixel_sha256':baked['pixel_sha256']},*pose['layers']]
        for image in images:
            p=contained(image['png']); actual=Image.open(p).convert('RGBA').tobytes()
            if sha(actual)!=image['pixel_sha256']:raise ValueError('Changed rendered pixels: '+image['png'])
            records.append((p,image['png']))
        frames.append({'id':pose['id'],'duration_ticks':pose['duration_ticks'],
                       'cels':{x['id']:{'image':x['png'],'at':[0,0]} for x in pose['layers']}})
    output.mkdir(parents=True)
    for p,name in records:shutil.copy2(p,output/name)
    spec={'schema':'sprite-construction-spec/v1','canvas':{'width':192,'height':192,'render_pivot':[96,96],'ground_pivot':[96,170]},
          'layers':[{'id':x,'name':x.replace('_',' ').title(),'locked':False} for x in order],
          'frames':frames,'animations':[{'id':report['binding'].replace('/','-'),'frames':[f['id'] for f in frames],
                                        'fps':report['fps'],'loop':clip['loop'],
                                        'events':[{'at_tick':e['tick'],'name':e['type']} for e in clip['events']]}],
          'provenance':{'source_bindings':report['source_bindings'],'bake_manifest_sha256':report['bake_manifest_sha256'],
                        'isolation_sha256':sha(raw),'binding':report['binding'],'quality_approved':False,
                        'ground_convention':clip['frames'][0]['pose'].get('ground_projection','side-view boundary170'),
                        'scope':'Complete single clip/view. Edits to cels remain baked overrides; reusable edits belong in source paint.'}}
    path=output/'construction.json';path.write_text(json.dumps(spec,indent=2)+'\n')
    construct=runpy.run_path(str(ROOT/'scripts/sprite_construct.py'))['construct']
    project=construct(path)
    checks=[]
    # The complete immutable project is validated once per batch. Revalidating
    # every cel for every frame made a 66-frame chunk scan ~1.9B pixel entries.
    composites=render_frames(project,[row['id']for row in report['poses']])
    for row,image in zip(report['poses'],composites):
        pixels=image.tobytes()
        checks.append({'tick':row['tick'],'composite_equals_gpu':sha(pixels)==row['full_pixel_sha256']})
    if not all(x['composite_equals_gpu'] for x in checks):raise ValueError('Isolated draw layers do not exactly reconstruct GPU clip')
    (output/'project.json').write_text(canonical_json(project)+'\n')
    proof={'schema':'editable-full-clip-proof/v1','passed':True,'binding':report['binding'],'frames':len(frames),
           'layers':len(order),'checks':checks,'source_bindings':report['source_bindings'],'isolation_sha256':sha(raw),
           'scope':'Every frame reconstructs actual GPU pixels. Art and animation quality require independent review.'}
    (output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('isolation',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=build(a.source,a.isolation,a.output);print(json.dumps({k:r[k] for k in ['passed','binding','frames','layers']}))
