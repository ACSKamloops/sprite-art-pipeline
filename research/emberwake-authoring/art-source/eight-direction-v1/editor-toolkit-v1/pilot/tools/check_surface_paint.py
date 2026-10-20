#!/usr/bin/env python3
"""Independent pixel-centre UV and material checks of actual Godot readbacks."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path

from PIL import Image


def local_point(pixel, frame):
    dx = pixel[0] + .5 - frame['origin'][0]
    dy = pixel[1] + .5 - frame['origin'][1]
    c, s = math.cos(frame['angle']), math.sin(frame['angle'])
    return ((dx*c + dy*s)/frame['uv_scale'][0],
            (-dx*s + dy*c)/frame['uv_scale'][1])


def inside(point, polygon):
    x, y = point
    hit = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = a[0] + (y-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if x < crossing:
                hit = not hit
    return hit


def expected(point, frame, strokes, palette):
    mask = frame['mask']
    if not any(inside(point, p) for p in mask['include']):
        return None
    if any(inside(point, p) for p in mask['exclude']):
        return None
    color = None
    for stroke in strokes:
        x, y = stroke['at']; size = stroke['size']
        if x <= point[0] < x+size and y <= point[1] < y+size:
            color = tuple(bytes.fromhex(palette[stroke['color']])) + (255,)
    return color


def check(report_path, design_path, samples_per_binding=8):
    report = json.loads(report_path.read_text())
    raw = design_path.read_bytes(); design = json.loads(raw)
    if hashlib.sha256(raw).hexdigest() != report['source_bindings']['design.json']:
        raise ValueError('Design differs from rendered source binding')
    failures, coverage = [], collections.defaultdict(lambda: {'samples':0,'visible_samples':0,'surface_pixels':0})
    for name in ['rig.gd','rig_side.gd','design.json','clips.json']:
        if hashlib.sha256((design_path.parent/name).read_bytes()).hexdigest()!=report['source_bindings'].get(name):
            raise ValueError('Source differs from rendered binding: '+name)
    clips=json.loads((design_path.parent/'clips.json').read_text())['clips']
    required={(name,view) for name in clips for view in ['right','left','front','back']}
    seen=collections.defaultdict(list)
    for row in report['samples']:seen[(row['clip'],row['view'])].append(row['phase'])
    if set(seen)!=required:
        failures.append({'reason':'Missing or unexpected action/view bindings'})
    for binding in required:
        phases=sorted(seen.get(binding,[])); loop=clips[binding[0]]['loop']
        wanted=[i/(samples_per_binding if loop else max(samples_per_binding-1,1)) for i in range(samples_per_binding)]
        if len(phases)!=samples_per_binding or any(abs(a-b)>1e-12 for a,b in zip(phases,wanted)):
            failures.append({'reason':'Missing, duplicate or incorrect phase samples','binding':binding})
    for row in report['samples']:
        prefix = row['prefix']; frame = row['surface_frame']
        strokes = design.get('paint_layers',{}).get(row['view'],{}).get('torso',[])
        coverage_key = row['clip']+'/'+row['view']
        coverage[coverage_key]['samples'] += 1
        coverage[coverage_key]['visible_samples'] += bool(row['visible_changed_coordinates'])
        coverage[coverage_key]['surface_pixels'] += len(row['surface_changed_coordinates'])
        after = Image.open(report_path.parent/(prefix+'-surface-after.png')).convert('RGBA')
        before = Image.open(report_path.parent/(prefix+'-surface-before.png')).convert('RGBA')
        full_after = Image.open(report_path.parent/(prefix+'-after.png')).convert('RGBA')
        full_before = Image.open(report_path.parent/(prefix+'-before.png')).convert('RGBA')
        if (hashlib.sha256(full_before.tobytes()).hexdigest() != row['before_sha256'] or
                hashlib.sha256(full_after.tobytes()).hexdigest() != row['after_sha256']):
            failures.append({'prefix':prefix,'reason':'Saved full render differs from bound RGBA hashes'})
        actual = [(x,y) for y in range(192) for x in range(192) if before.getpixel((x,y)) != after.getpixel((x,y))]
        full_actual = {(x,y) for y in range(192) for x in range(192) if full_before.getpixel((x,y)) != full_after.getpixel((x,y))}
        if (full_actual != {tuple(p) for p in row['visible_changed_coordinates']} or
                not full_actual.issubset(set(actual))):
            failures.append({'prefix':prefix,'reason':'Full render has unreported or off-surface changes'})
        if (before.getchannel('A').tobytes() != after.getchannel('A').tobytes() or
                full_before.getchannel('A').tobytes() != full_after.getchannel('A').tobytes()):
            failures.append({'prefix':prefix,'reason':'Paint changed alpha coverage'})
        if set(actual) != {tuple(p) for p in row['surface_changed_coordinates']}:
            failures.append({'prefix':prefix,'reason':'Saved pixels disagree with reported change coordinates'})
        for pixel in actual:
            uv = local_point(pixel, frame)
            color = expected(uv, frame, strokes, design['palette'])
            if color is None or after.getpixel(pixel) != color:
                failures.append({'prefix':prefix,'pixel':pixel,'uv':uv,'reason':'Changed pixel outside authored UV stroke/mask or wrong material','expected':color,'actual':after.getpixel(pixel)})
    return {'schema':'independent-surface-paint-check/v1',
            'passed':report['passed'] and not failures,
            'source_bindings':report['source_bindings'],
            'tester_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'samples':len(report['samples']),'coverage':dict(coverage),'failures':failures,
            'scope':'Independent inverse-transform pixel-centre UV, polygon mask and palette checks; readback change ledger recomputed. Foreground occlusion may hide valid stitches. Rigid torso painting only; no art approval.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('report',type=Path); p.add_argument('design',type=Path); p.add_argument('--output',type=Path,required=True); p.add_argument('--samples-per-binding',type=int,default=8)
    args = p.parse_args()
    if args.samples_per_binding<1:raise ValueError('A positive explicit sample count is required')
    result = check(args.report,args.design,args.samples_per_binding)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'samples':result['samples'],'failures':len(result['failures']),'output':str(args.output)}))
    raise SystemExit(0 if result['passed'] else 2)
