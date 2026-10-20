"""Explicit supplied-part scenes. Local policy, not a PixelLab skeletal renderer."""
from __future__ import annotations

import json
import math
from fractions import Fraction

import numpy as np

from .core import (MAX_FRAMES, MAX_PIXELS, ValidationError, UnsupportedCapability,
                   canonical_json, load_sequence, save_sequence)

MAX_WORK_PIXELS = 64_000_000
NODE_FIELDS = {'id', 'parent', 'raster', 'mask', 'ownership', 'position', 'anchor',
               'rotation_degrees', 'scale', 'visible', 'z', 'composite'}
OVERRIDES = NODE_FIELDS - {'id', 'parent'}


def _keys(value, allowed, label):
    if not isinstance(value, dict):
        raise ValidationError(f'{label} must be an object')
    extra = value.keys() - allowed
    if extra:
        raise UnsupportedCapability(label, f'Unsupported fields: {sorted(extra)}')


def _point(value, label):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValidationError(f'{label} requires two coordinates')
    if any(type(v) not in (int, float) or abs(v) > 1e6 or not math.isfinite(v) for v in value):
        raise ValidationError(f'{label} requires bounded finite numbers')
    return np.array(value, dtype=np.float64)


def _duration(value):
    if not isinstance(value, list) or len(value) != 2 or any(type(v) != int for v in value):
        raise ValidationError('Scene duration must be integer [numerator,denominator] seconds')
    try:
        d = Fraction(*value)
    except (ValueError, ZeroDivisionError) as e:
        raise ValidationError('Invalid scene duration') from e
    if not 0 < d <= 3600:
        raise ValidationError('Duration must be positive and <=3600seconds')
    return d


def _local(node):
    p = _point(node.get('position', [0, 0]), 'position')
    a = _point(node.get('anchor', [0, 0]), 'anchor')
    s = _point(node.get('scale', [1, 1]), 'scale')
    if np.any(np.abs(s) < 1e-6) or np.any(np.abs(s) > 64):
        raise ValidationError('Scale magnitude must be1e-6..64')
    angle = node.get('rotation_degrees', 0)
    if type(angle) not in (int, float) or abs(angle) > 1e12 or not math.isfinite(angle):
        raise ValidationError('Rotation must be a finite degree value')
    rad = math.radians(angle % 360)
    c, t = math.cos(rad), math.sin(rad)
    # Exact cardinal coefficients avoid float-boundary artifacts.
    c = round(c) if abs(c - round(c)) < 1e-12 else c
    t = round(t) if abs(t - round(t)) < 1e-12 else t
    linear = np.array([[c * s[0], -t * s[1]], [t * s[0], c * s[1]]])
    m = np.eye(3)
    m[:2, :2] = linear
    m[:2, 2] = p + a - linear @ a
    return m


def _owned(store, node, source_masks, coverage):
    raster = store.get_raster(node['raster'])
    if node.get('mask') is None:
        raise ValidationError(f"Raster node {node['id']} requires an explicit owned mask")
    mask = store.get_raster(node['mask'])
    if mask.shape != raster.shape or np.any((mask[..., 3] != 0) & (mask[..., 3] != 255)):
        raise ValidationError('Ownership mask must match raster dimensions and have binary alpha')
    owned = mask[..., 3] == 255
    ownership = node.get('ownership')
    if ownership is not None:
        _keys(ownership, {'source', 'origin'}, 'ownership')
        source = store.get_raster(ownership.get('source'))
        origin = ownership.get('origin', [0, 0])
        if not isinstance(origin, list) or len(origin) != 2 or any(type(v) != int or v < 0 for v in origin):
            raise ValidationError('Source origin must be two nonnegative integer pixels')
        x, y = origin; h, w = raster.shape[:2]
        if x + w > source.shape[1] or y + h > source.shape[0]:
            raise ValidationError('Source ownership rectangle lies outside source')
        if not np.array_equal(raster, source[y:y+h, x:x+w]):
            raise ValidationError('Raster does not exactly match bound source rectangle, including hiddenRGB')
        sid = ownership['source']
        previous = source_masks.setdefault(sid, np.zeros(source.shape[:2], dtype=bool))
        region = previous[y:y+h, x:x+w]
        if not coverage['allow_overlap'] and np.any(region & owned):
            raise ValidationError('Two nodes claim the same source pixel ownership')
        region |= owned
        coverage['sources'][sid] = source
    elif coverage['require']:
        raise ValidationError('Source coverage requires ownership bindings on every raster node')
    return raster, owned


def _sample(raster, owned, matrix, width, height):
    """Inverse sample canvas pixel centers; floor selects source cells, ties toward +axis."""
    yy, xx = np.mgrid[:height, :width]
    dest = np.stack((xx.ravel() + .5, yy.ravel() + .5, np.ones(width * height)))
    q = np.linalg.solve(matrix, dest)[:2]
    near = np.rint(q)
    q = np.where(np.abs(q - near) < 1e-10, near, q)
    sx, sy = np.floor(q).astype(np.int64)
    inside = (sx >= 0) & (sy >= 0) & (sx < raster.shape[1]) & (sy < raster.shape[0])
    index = np.flatnonzero(inside)
    index = index[owned[sy[index], sx[index]]]
    support = np.zeros(width * height, dtype=bool)
    support[index] = True
    layer = np.zeros((height * width, 4), dtype=np.uint8)
    layer[index] = raster[sy[index], sx[index]]
    return layer.reshape(height, width, 4), support.reshape(height, width)


def _over(canvas, layer, support, mode):
    if mode == 'replace':
        canvas[support] = layer[support]
        return
    if mode != 'source_over':
        raise UnsupportedCapability('composite', mode)
    src, dst = layer[support].astype(np.uint32), canvas[support].astype(np.uint32)
    sa, da = src[:, 3], dst[:, 3]
    result = dst.copy()
    direct = (da == 0) | (sa == 255)
    result[direct] = src[direct]
    mix = (sa > 0) & (sa < 255) & (da > 0)
    if np.any(mix):
        s, d = src[mix], dst[mix]; a, b = s[:, 3], d[:, 3]
        denominator = a * 255 + b * (255 - a)
        numerator = s[:, :3] * (a * 255)[:, None] + d[:, :3] * (b * (255 - a))[:, None]
        result[mix, :3] = (numerator + denominator[:, None] // 2) // denominator[:, None]
        result[mix, 3] = (denominator + 127) // 255
    canvas[support] = result.astype(np.uint8)


def _guard(store, scene, arrays):
    guards = scene.get('guards', {})
    _keys(guards, {'reference_sequence', 'frozen_frames', 'protected', 'palette_reference'}, 'guards')
    frozen = guards.get('frozen_frames', [])
    protected = guards.get('protected', [])
    if not isinstance(frozen, list) or not isinstance(protected, list):
        raise ValidationError('Guard frame/region lists required')
    if frozen or protected:
        _, refs = load_sequence(store, guards.get('reference_sequence'))
        if len(refs) != len(arrays) or any(a.shape != b.shape for a,b in zip(arrays,refs)):
            raise ValidationError('Guard reference sequence must match canvas and ordered frame count')
        for i in frozen:
            if type(i) != int or not 0 <= i < len(arrays):
                raise ValidationError('Frozen frame index outside sequence')
            if not np.array_equal(arrays[i], refs[i]):
                raise ValidationError(f'Frozen frame {i} changed')
        for entry in protected:
            _keys(entry, {'frame', 'mask'}, 'protected region')
            i = entry.get('frame')
            if type(i) != int or not 0 <= i < len(arrays):
                raise ValidationError('Protected frame index outside sequence')
            mask = store.get_raster(entry.get('mask'))
            if mask.shape != arrays[i].shape or np.any((mask[...,3] != 0) & (mask[...,3] != 255)):
                raise ValidationError('Protected mask must match canvas and have binary alpha')
            region = mask[...,3] == 255
            if not np.array_equal(arrays[i][region], refs[i][region]):
                raise ValidationError(f'Protected frame {i} pixels changed')
    if 'palette_reference' in guards:
        ref = store.get_raster(guards['palette_reference'])
        palette = {tuple(c) for c in ref[ref[...,3] > 0, :3]}
        for i, a in enumerate(arrays):
            if not {tuple(c) for c in a[a[...,3] > 0, :3]} <= palette:
                raise ValidationError(f'Visible RGB palette guard failed in frame {i}')


def render_scene(store, scene):
    """Render supplied discrete poses and preserve a source-bound editable layered document."""
    scene = json.loads(canonical_json(scene))
    _keys(scene, {'canvas', 'nodes', 'frames', 'loop', 'name', 'metadata', 'guards',
                  'require_source_coverage', 'allow_source_overlap', 'clip_policy', 'play_count'}, 'scene')
    size = scene.get('canvas')
    if not isinstance(size, list) or len(size) != 2 or any(type(v) != int or v < 1 for v in size) or math.prod(size) > MAX_PIXELS:
        raise ValidationError('Canvas must be two positive bounded integer dimensions')
    width, height = size
    clip_policy = scene.get('clip_policy','report')
    if clip_policy not in ['report','reject']:
        raise ValidationError('clip_policy must be report or reject')
    count = scene.get('play_count',0 if scene.get('loop',False) else 1)
    if type(count) != int or not 0 <= count <= 65536 or scene.get('loop',False) != (count == 0):
        raise ValidationError('play_count must be0..65536 and consistent with infinite loop flag')
    nodes, frames = scene.get('nodes'), scene.get('frames')
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 128:
        raise ValidationError('Scene requires1..128 nodes')
    if not isinstance(frames, list) or not 1 <= len(frames) <= MAX_FRAMES:
        raise ValidationError('Scene requires1..512 ordered frames')
    if width * height * len(nodes) * len(frames) > MAX_WORK_PIXELS:
        raise ValidationError('Scene exceeds local sampling work budget')
    for key in ['loop', 'require_source_coverage', 'allow_source_overlap']:
        if key in scene and type(scene[key]) != bool:
            raise ValidationError(f'{key} must be boolean')
    by_id = {}
    for node in nodes:
        _keys(node, NODE_FIELDS, 'node')
        ident = node.get('id')
        if not isinstance(ident, str) or not ident or len(ident) > 128 or ident in by_id:
            raise ValidationError('Node IDs must be unique bounded nonempty strings')
        by_id[ident] = node
    order, visiting, visited = [], set(), set()
    def visit(ident):
        if ident in visited:
            return
        if ident in visiting:
            raise ValidationError('Parent graph contains a cycle')
        visiting.add(ident)
        parent = by_id[ident].get('parent')
        if parent is not None:
            if not isinstance(parent,str) or parent not in by_id:
                raise ValidationError('Unknown parent node')
            visit(parent)
        visiting.remove(ident); visited.add(ident); order.append(ident)
    for ident in by_id:
        visit(ident)
    arrays, holds, pivots, directions, layered = [], [], [], [], []
    source_ids = set()
    for fi, frame in enumerate(frames):
        _keys(frame, {'duration','nodes','pivot','direction','label'}, 'frame')
        hold = _duration(frame.get('duration'))
        pivot = _point(frame.get('pivot',[0,0]), 'frame pivot')
        direction = frame.get('direction','unspecified')
        if not isinstance(direction,str) or not direction:
            raise ValidationError('Frame direction must be nonempty text')
        overrides = frame.get('nodes', {})
        if not isinstance(overrides,dict) or overrides.keys() - by_id.keys():
            raise ValidationError('Frame overrides reference unknown nodes')
        effective = {}
        for ident, node in by_id.items():
            override = overrides.get(ident,{})
            _keys(override, OVERRIDES, 'node override')
            effective[ident] = node | override
        matrices, visibility = {}, {}
        for ident in order:
            node = effective[ident]; parent = node.get('parent')
            if type(node.get('visible',True)) != bool or type(node.get('z',0)) != int:
                raise ValidationError('Node visible/z must be boolean/integer')
            matrices[ident] = (matrices[parent] if parent else np.eye(3)) @ _local(node)
            matrix = matrices[ident]
            singular = np.linalg.svd(matrix[:2,:2],compute_uv=False)
            if not np.all(np.isfinite(matrix)) or np.max(np.abs(matrix)) > 1e9 or singular[-1] < 1e-8 or singular[0]/singular[-1] > 1e8:
                raise ValidationError('World transform exceeds local numerical bounds')
            visibility[ident] = node.get('visible',True) and (visibility[parent] if parent else True)
        # Validate ownership even for hidden nodes; visibility does not change ownership.
        sources, coverage = {}, {'sources': {}, 'require':scene.get('require_source_coverage',False),
                                 'allow_overlap':scene.get('allow_source_overlap',False)}
        assets = {}
        for ident,node in effective.items():
            if 'raster' in node:
                assets[ident] = _owned(store,node,sources,coverage)
                source_ids.update([node['raster'],node['mask']])
                if node.get('ownership'):
                    source_ids.add(node['ownership']['source'])
            elif any(k in node for k in ['mask','ownership']):
                raise ValidationError('Group nodes cannot have a mask or ownership without a raster')
        if coverage['require']:
            for sid,source in coverage['sources'].items():
                if np.any((source[...,3] > 0) & ~sources[sid]):
                    raise ValidationError('Owned parts do not cover all visible source pixels')
        canvas = np.zeros((height,width,4),dtype=np.uint8)
        records = []
        for ident in sorted(effective,key=lambda k:(effective[k].get('z',0), list(by_id).index(k))):
            node = effective[ident]
            if ident not in assets:
                continue
            raster,owned = assets[ident]
            oy,ox = np.nonzero(owned)
            centers = matrices[ident] @ np.stack((ox+.5,oy+.5,np.ones(len(ox))))
            outside = int(((centers[0]<0)|(centers[0]>=width)|(centers[1]<0)|(centers[1]>=height)).sum())
            if outside and clip_policy == 'reject':
                raise ValidationError(f'Owned source centers outside canvas in node {ident}, frame {fi}')
            layer,support = _sample(raster,owned,matrices[ident],width,height)
            mode = node.get('composite','source_over')
            if mode not in ['replace','source_over']:
                raise UnsupportedCapability('composite',mode)
            if visibility[ident]:
                _over(canvas,layer,support,mode)
            mask = np.zeros_like(layer); mask[...,3] = support.astype(np.uint8)*255
            records.append({'node':ident,'raster':node['raster'],'mask':node['mask'],
                            'world_matrix':matrices[ident].tolist(),'visible':visibility[ident],
                            'z':node.get('z',0),'composite':mode,
                            'transformed_raster':store.put_raster(layer),'transformed_mask':store.put_raster(mask),
                            'owned_source_centers_outside_canvas':outside,
                            'sampled_owned_canvas_pixels':int(support.sum())})
        arrays.append(canvas); holds.append(hold); pivots.append(pivot.tolist()); directions.append(direction)
        layered.append({'index':fi,'layers':records})
    _guard(store,scene,arrays)
    scene_id = store.put_json({'kind':'layered-scene','version':1,'scene':scene,
                               'source_ids':sorted(source_ids),'frame_layers':layered,
                               'policy':'local-nearest-inverse-pixel-center-v1; no hidden-surface inference'})
    ident = save_sequence(store,arrays,holds,pivots,scene.get('loop',False),directions,
                         {'scene_id':scene_id,'source_ids':sorted(source_ids),'name':scene.get('name','supplied-scene'),
                          'method':'local-supplied-part-scene-v1','scene_metadata':scene.get('metadata',{})},play_count=count)
    return ident
