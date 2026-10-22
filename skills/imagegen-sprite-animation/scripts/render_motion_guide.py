#!/usr/bin/env python3
"""Render a supplied keyed humanoid GLB as one-camera pose geometry.

Run inside Blender 4.5 (tested), not ordinary Python. No downloads, model calls,
repository imports, Pillow, or external Python packages. Input licenses are
caller-supplied metadata. Square stages and one armature/mesh are intentional.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys
import zlib
from fractions import Fraction

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def fraction(value):
    return [value.numerator, value.denominator]


def curve_list(action):
    if hasattr(action, 'layers') and len(action.layers):
        result = []
        for layer in action.layers:
            for strip in layer.strips:
                require(hasattr(strip, 'channelbags'), 'Unsupported action strip; expected keyed channelbags')
                for bag in strip.channelbags:
                    result.extend(bag.fcurves)
        return result
    return list(action.fcurves)


def curve_state(curve):
    return {
        'path': curve.data_path, 'index': curve.array_index,
        'keys': [[*p.co, *p.handle_left, *p.handle_right, p.interpolation,
                  p.handle_left_type, p.handle_right_type] for p in curve.keyframe_points],
        'sampled': [list(p.co) for p in curve.sampled_points],
        'extrapolation': curve.extrapolation,
    }


def action_hash(action):
    return hashlib.sha256(json.dumps([curve_state(f) for f in curve_list(action)], sort_keys=True).encode()).hexdigest()


def bind_action(rig, action):
    rig.animation_data_create()
    rig.animation_data.action = action
    if hasattr(action, 'slots') and len(action.slots):
        rig.animation_data.action_slot = action.slots[0]


def glb_clock(path, action_name):
    """Read actual float time samples, rather than inventing source capture FPS."""
    raw = Path(path).read_bytes()
    require(raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 4)[0] == 2, 'Expected GLB v2')
    at, document, binary = 12, None, None
    while at < len(raw):
        length, kind = struct.unpack_from('<II', raw, at)
        payload = raw[at + 8:at + 8 + length]
        if kind == 0x4e4f534a:
            document = json.loads(payload)
        elif kind == 0x004e4942:
            binary = payload
        at += 8 + length
    require(document is not None and binary is not None, 'Expected embedded GLB JSON/BIN')
    matches = [a for a in document.get('animations', []) if a.get('name') == action_name]
    require(len(matches) == 1, 'Exact source GLB animation name not unique/present')
    action = matches[0]
    arrays = []
    for index in sorted({s['input'] for s in action['samplers']}):
        accessor = document['accessors'][index]
        require(accessor['type'] == 'SCALAR' and accessor['componentType'] == 5126 and 'sparse' not in accessor,
                'This bounded reader requires nonsparse float SCALAR time accessors')
        view = document['bufferViews'][accessor['bufferView']]
        require(view.get('buffer', 0) == 0, 'External time buffer unsupported')
        offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        stride = view.get('byteStride', 4)
        times = [struct.unpack_from('<f', binary, offset + i * stride)[0] for i in range(accessor['count'])]
        arrays.append({'accessor': index, 'times_seconds': times})
    nodes = sorted({c['target']['node'] for c in action['channels']})
    return {'animation': action_name, 'channel_count': len(action['channels']),
            'target_nodes': [document['nodes'][i].get('name') for i in nodes],
            'interpolations': sorted({s.get('interpolation', 'LINEAR') for s in action['samplers']}),
            'time_arrays': arrays, 'note': 'glTF stores seconds; configured sample_fps is a rendering/sample convention.'}


# Small lossless PNG reader/writer for the helper's own RGBA8 Blender renders.
# This keeps standalone Blender execution independent of Pillow.
def png_chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def read_rgba_png(path):
    raw = Path(path).read_bytes()
    require(raw[:8] == b'\x89PNG\r\n\x1a\n', 'Not PNG')
    at, packed, header = 8, bytearray(), None
    while at < len(raw):
        n = struct.unpack_from('>I', raw, at)[0]
        kind, data = raw[at + 4:at + 8], raw[at + 8:at + 8 + n]
        crc = struct.unpack_from('>I', raw, at + 8 + n)[0]
        require(crc == zlib.crc32(kind + data) & 0xffffffff, 'PNG CRC mismatch')
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', data)
        elif kind == b'IDAT':
            packed.extend(data)
        at += n + 12
    require(header is not None, 'Missing PNG header')
    w, h, depth, color, compression, filt, interlace = header
    require((depth, color, compression, filt, interlace) == (8, 6, 0, 0, 0), 'Expected noninterlaced RGBA8 PNG')
    scan = zlib.decompress(packed)
    row_bytes = w * 4
    require(len(scan) == h * (row_bytes + 1), 'PNG scanline length mismatch')
    result, prior = bytearray(), bytearray(row_bytes)
    for y in range(h):
        mode = scan[y * (row_bytes + 1)]
        row = bytearray(scan[y * (row_bytes + 1) + 1:(y + 1) * (row_bytes + 1)])
        require(mode in range(5), 'Unsupported PNG row filter')
        for x in range(row_bytes):
            left = row[x - 4] if x >= 4 else 0
            above, upper_left = prior[x], prior[x - 4] if x >= 4 else 0
            if mode == 1:
                predictor = left
            elif mode == 2:
                predictor = above
            elif mode == 3:
                predictor = (left + above) // 2
            elif mode == 4:
                p = left + above - upper_left
                pa, pb, pc = abs(p - left), abs(p - above), abs(p - upper_left)
                predictor = left if pa <= pb and pa <= pc else above if pb <= pc else upper_left
            else:
                predictor = 0
            row[x] = (row[x] + predictor) & 255
        result.extend(row)
        prior = row
    return w, h, bytes(result)


def write_rgba_png(path, w, h, rgba):
    require(len(rgba) == w * h * 4, 'RGBA byte count mismatch')
    scan = b''.join(b'\0' + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))
    raw = b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    raw += png_chunk(b'IDAT', zlib.compress(scan, 6)) + png_chunk(b'IEND', b'')
    Path(path).write_bytes(raw)


def resize_nearest(w, h, rgba, scale):
    rows = []
    for y in range(h):
        row = rgba[y * w * 4:(y + 1) * w * 4]
        enlarged = b''.join(row[x:x + 4] * scale for x in range(0, len(row), 4))
        rows.extend([enlarged] * scale)
    return w * scale, h * scale, b''.join(rows)


def blit(dst, dw, src, sw, sh, ox, oy):
    for y in range(sh):
        start = ((oy + y) * dw + ox) * 4
        dst[start:start + sw * 4] = src[y * sw * 4:(y + 1) * sw * 4]


def matte_rgba(rgba, matte):
    result = bytearray(len(rgba))
    for p in range(0, len(rgba), 4):
        a = rgba[p + 3]
        for c in range(3):
            result[p + c] = (rgba[p + c] * a + matte[c] * (255 - a) + 127) // 255
        result[p + 3] = 255
    return bytes(result)


FONT = {
    '0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'],
    '2': ['111', '001', '111', '100', '111'], '3': ['111', '001', '111', '001', '111'],
    '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '111', '001', '111'],
    '6': ['111', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'],
    '8': ['111', '101', '111', '101', '111'], '9': ['111', '101', '111', '001', '111'],
    'f': ['011', '010', '111', '010', '010'], 's': ['011', '100', '010', '001', '110'],
    '.': ['000', '000', '000', '000', '010'], '-': ['000', '000', '111', '000', '000'],
}


def label(dst, width, text, ox, oy):
    for char in text:
        for y, row in enumerate(FONT.get(char, ['000'] * 5)):
            for x, bit in enumerate(row):
                if bit == '1':
                    at = ((oy + y) * width + ox + x) * 4
                    dst[at:at + 4] = bytes((15, 25, 30, 255))
        ox += 4


def alpha_report(w, h, rgba):
    positions = [p // 4 for p in range(3, len(rgba), 4) if rgba[p]]
    require(positions, 'Empty rendered actor')
    xs, ys = [p % w for p in positions], [p // w for p in positions]
    return {'alpha_nonzero_bbox_half_open': [min(xs), min(ys), max(xs) + 1, max(ys) + 1],
            'alpha_touches_canvas_edge': min(xs) == 0 or min(ys) == 0 or max(xs) == w - 1 or max(ys) == h - 1}


def run(config_path, output):
    config_path = config_path.resolve()
    cfg = json.loads(config_path.read_text())
    require(cfg.get('schema') == 'motion-guide-config/v1', 'Wrong config schema')
    require(not output.exists() and not output.is_symlink(), 'Output must be a fresh nonexistent directory; retained outputs are never overwritten')
    require(output.parent.is_dir(), 'Output parent must already exist')
    source = (config_path.parent / cfg['source_glb']).resolve()
    require(source.is_file() and source.suffix.lower() == '.glb', 'Supply an existing GLB')
    license_meta = dict(cfg['source_license'])
    require(bool(license_meta.get('label')), 'Supply explicit source-license metadata; helper does not infer licensing')
    license_file = (config_path.parent / license_meta['path']).resolve() if license_meta.get('path') else None
    require(license_file is None or license_file.is_file(), 'Supplied license file missing')
    width, height = cfg['stage']
    require(type(width) is int and type(height) is int and width == height and width > 0, 'Bounded helper supports positive square native stages')
    fps = cfg['sample_fps']
    require(type(fps) is int and fps > 0, 'sample_fps must be a positive integer')
    if 'frames' in cfg:
        frames = cfg['frames']
    else:
        fr = cfg['frame_range']
        require(fr.get('step', 1) > 0, 'Frame range step must be positive')
        frames = list(range(fr['start'], fr['end'] + 1, fr.get('step', 1)))
    require(frames and all(type(f) is int for f in frames) and frames == sorted(set(frames)), 'Frames must be unique increasing integers')
    standing_frame = cfg['standing_frame']
    require(standing_frame in frames, 'Standing frame must be in measured/rendered frames')
    sheet_cfg = cfg.get('selected_sheet')
    if sheet_cfg:
        require(all(type(sheet_cfg[n]) is int and sheet_cfg[n] > 0 for n in ['columns', 'rows']),
                'Sheet columns and rows must be positive integers')
        require(sheet_cfg['columns'] * sheet_cfg['rows'] == len(sheet_cfg['frames']), 'Sheet grid must exactly match selected frame count')
        require(all(f in frames for f in sheet_cfg['frames']), 'Selected sheet frames must be measured/rendered')
        require(type(sheet_cfg['scale']) is int and sheet_cfg['scale'] > 0, 'Sheet nearest scale must be positive integer')
    contacts = cfg.get('contact_frames', frames)
    require(isinstance(contacts, list) and bool(contacts), 'Contact frames must be a nonempty list')
    require(all(type(f) is int and f in frames for f in contacts), 'Contact frames must be rendered integers')
    render = cfg.get('render', {})
    contact_scale = render.get('contact_scale', 3)
    require(type(contact_scale) is int and contact_scale > 0, 'Contact scale must be a positive integer')
    allow_extrapolation = cfg.get('allow_extrapolation', False)
    require(type(allow_extrapolation) is bool, 'allow_extrapolation must be an explicit boolean')
    source_hash, config_hash = sha(source), sha(config_path)
    actual_clock = glb_clock(source, cfg['action'])
    actual_times = sorted({t for array in actual_clock['time_arrays'] for t in array['times_seconds']})
    require(bool(actual_times), 'Selected source animation has no stored times')
    source_interval = [min(actual_times), max(actual_times)]
    time_epsilon = 1e-6
    extrapolated_frames = [f for f in frames if f / fps < source_interval[0] - time_epsilon
                           or f / fps > source_interval[1] + time_epsilon]
    require(allow_extrapolation or not extrapolated_frames,
            'Requested frames outside actual GLB action time interval; explicit allow_extrapolation:true required')

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = fps
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    bpy.ops.import_scene.gltf(filepath=str(source))
    rig, mesh = scene.objects.get(cfg['armature']), scene.objects.get(cfg['mesh'])
    require(rig is not None and rig.type == 'ARMATURE', 'Configured armature not found')
    require(mesh is not None and mesh.type == 'MESH', 'Configured mesh not found')
    matches = [a for a in bpy.data.actions if a.name == cfg['action']]
    require(len(matches) == 1, 'Exact imported action missing/ambiguous: ' + cfg['action'])
    source_action = matches[0]
    for obj in scene.objects:
        if obj.animation_data:
            obj.animation_data_clear()
        if obj.type == 'MESH' and obj != mesh:
            obj.hide_render = True
    head_cfg = cfg.get('head_scale')
    head_name = head_cfg['bone'] if head_cfg else None
    factor = float(head_cfg['multiplier']) if head_cfg else 1.0
    require(math.isfinite(factor) and factor > 0, 'Head factor must be finite and positive')
    if head_name:
        require(head_name in rig.pose.bones, 'Named scale bone missing')
        require(not rig.pose.bones[head_name].children, 'Tested Head-only invariant requires a leaf scale bone; this is not a general retargeter')
    source_action_hash = action_hash(source_action)
    authored = source_action.copy()
    authored.name = cfg['action'] + '_GUIDE_COPY'
    scale_path = 'pose.bones[' + json.dumps(head_name) + '].scale' if head_name else None
    changes = []
    if head_cfg and factor != 1:
        for curve in curve_list(authored):
            if curve.data_path == scale_path:
                before = curve_state(curve)
                for point in curve.keyframe_points:
                    point.co.y *= factor
                    point.handle_left.y *= factor
                    point.handle_right.y *= factor
                for point in curve.sampled_points:
                    point.co.y *= factor
                changes.append({'before': before, 'after': curve_state(curve)})
        require(len(changes) == 3 and {c['before']['index'] for c in changes} == {0, 1, 2}, 'Requested scale bone needs exactly3 keyed scale channels')
    original_curves, copied_curves = curve_list(source_action), curve_list(authored)
    require(len(original_curves) == len(copied_curves), 'Copied action channel count changed')
    unchanged = 0
    for before, after in zip(original_curves, copied_curves):
        if before.data_path != scale_path or factor == 1:
            require(curve_state(before) == curve_state(after), 'Unexpected channel change')
            unchanged += 1
    for role, mapping in cfg['joint_roles'].items():
        require(mapping['bone'] in rig.pose.bones and mapping['point'] in ['head', 'tail'], 'Invalid role mapping: ' + role)

    bpy.ops.object.camera_add(location=cfg['camera']['location'])
    camera = bpy.context.object
    camera.name = 'one_measured_motion_guide_camera'
    look = Vector(cfg['camera']['target']) - camera.location
    require(look.length > 0, 'Camera target equals camera location')
    camera.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    scene.camera = camera
    bpy.context.view_layer.update()
    right = camera.matrix_world.to_quaternion() @ Vector((1, 0, 0))
    up = camera.matrix_world.to_quaternion() @ Vector((0, 1, 0))
    depsgraph = bpy.context.evaluated_depsgraph_get()
    threshold = float(head_cfg.get('owner_weight_threshold', .5)) if head_cfg else .5
    head_group = mesh.vertex_groups.get(head_name) if head_name else None
    head_ids = [v.index for v in mesh.data.vertices if head_group and any(g.group == head_group.index and g.weight > threshold for g in v.groups)]
    foot_groups = []
    for name in cfg['foot_owner_bones']:
        require(mesh.vertex_groups.get(name) is not None, 'Foot owner vertex group missing: ' + name)
        foot_groups.append(mesh.vertex_groups[name].index)
    foot_ids = [v.index for v in mesh.data.vertices if sum(g.weight for g in v.groups if g.group in foot_groups) > .5]
    require(foot_ids, 'No vertices in declared foot owner')
    require(not head_cfg or head_ids, 'No vertices in declared Head owner')

    def bounds(points):
        return {'right': [min(v.dot(right) for v in points), max(v.dot(right) for v in points)],
                'up': [min(v.dot(up) for v in points), max(v.dot(up) for v in points)]}

    samples, max_joint_error = [], 0.0
    for frame in frames:
        bind_action(rig, source_action)
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        before = {n: rig.matrix_world @ p.head for n, p in rig.pose.bones.items() if n != head_name}
        before_head_rotation = list(rig.pose.bones[head_name].rotation_quaternion) if head_name else None
        before_head_scale = list(rig.pose.bones[head_name].scale) if head_name else None
        bind_action(rig, authored)
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        max_joint_error = max(max_joint_error, max((rig.matrix_world @ rig.pose.bones[n].head - pos).length for n, pos in before.items()))
        if head_name:
            head = rig.pose.bones[head_name]
            require(list(head.rotation_quaternion) == before_head_rotation, 'Source scale-bone pitch changed')
            require(all(abs(head.scale[i] - before_head_scale[i] * factor) < 1e-5 for i in range(3)), 'Evaluated keyed scale mismatch')
        evaluated = mesh.evaluated_get(depsgraph)
        evaluated_mesh = evaluated.to_mesh()
        require(len(evaluated_mesh.vertices) == len(mesh.data.vertices), 'Topology-changing modifier unsupported by weight-owner bboxes')
        points = [evaluated.matrix_world @ v.co for v in evaluated_mesh.vertices]
        joint_points = {n: {'head_world': list(rig.matrix_world @ rig.pose.bones[n].head),
                            'tail_world': list(rig.matrix_world @ rig.pose.bones[n].tail)}
                        for n in {m['bone'] for m in cfg['joint_roles'].values()}}
        nominal = Fraction(frame, fps)
        nearest_time = min(actual_times, key=lambda time: abs(time - float(nominal)))
        samples.append({'source_frame': frame, 'source_time_nominal': fraction(nominal),
                        'nearest_stored_gltf_time': nearest_time,
                        'outside_stored_source_interval': frame in extrapolated_frames,
                        'nearest_source_time_error_seconds': abs(nearest_time - float(nominal)),
                        'sample_is_source_key_within_1e_6': abs(nearest_time - float(nominal)) < 1e-6,
                        'geometry_bounds': bounds(points),
                        'head_weight_owner_bounds': bounds([points[i] for i in head_ids]) if head_ids else None,
                        'foot_weight_owner_bounds': bounds([points[i] for i in foot_ids]),
                        'bones': joint_points,
                        'evaluated_head_scale': list(rig.pose.bones[head_name].scale) if head_name else None})
        evaluated.to_mesh_clear()
    require(max_joint_error < 1e-6, 'Non-Head joint positions changed')
    require(action_hash(source_action) == source_action_hash, 'Original action changed')

    stand = samples[frames.index(standing_frame)]
    sole_up = stand['foot_weight_owner_bounds']['up'][0]
    standing_height = stand['geometry_bounds']['up'][1] - sole_up
    require(standing_height > 0, 'Degenerate standing geometry')
    target_height, sole_y = float(cfg['standing_target_height']), float(cfg['standing_sole_y'])
    origin_x, margin = float(cfg.get('horizontal_origin_x', cfg['pivot'][0])), float(cfg['camera'].get('margin', 1))
    min_r = min(s['geometry_bounds']['right'][0] for s in samples)
    max_r = max(s['geometry_bounds']['right'][1] for s in samples)
    min_u = min(s['geometry_bounds']['up'][0] for s in samples)
    max_u = max(s['geometry_bounds']['up'][1] for s in samples)
    constraints = {'standing_height_target': target_height / standing_height,
                   'left_margin': (origin_x - margin) / -min_r if min_r < 0 else 1e99,
                   'right_margin': (width - margin - origin_x) / max_r if max_r > 0 else 1e99,
                   'top_margin': (sole_y - margin) / (max_u - sole_up),
                   'bottom_margin': (height - margin - sole_y) / (sole_up - min_u) if min_u < sole_up else 1e99}
    scale = min(constraints.values())
    require(scale > 0 and math.isfinite(scale), 'Camera/anchor constraints give no positive fit')
    origin_y = sole_y + scale * sole_up
    camera.data.ortho_scale = width / scale
    bpy.context.view_layer.update()
    uv = world_to_camera_view(scene, camera, Vector((0, 0, 0)))
    camera.data.shift_x += uv.x - origin_x / width
    camera.data.shift_y += uv.y - (1 - origin_y / height)
    bpy.context.view_layer.update()
    uv = world_to_camera_view(scene, camera, Vector((0, 0, 0)))
    require(abs(uv.x * width - origin_x) < 1e-3 and abs((1 - uv.y) * height - origin_y) < 1e-3, 'Shared camera registration failed')

    def project(point):
        v = Vector(point)
        return [origin_x + scale * v.dot(right), origin_y - scale * v.dot(up)]

    def projected_box(b):
        return [origin_x + scale * b['right'][0], origin_y - scale * b['up'][1],
                origin_x + scale * b['right'][1], origin_y - scale * b['up'][0]]

    for sample in samples:
        sample['projected_geometry_bbox'] = projected_box(sample['geometry_bounds'])
        sample['projected_head_weight_owner_bbox'] = projected_box(sample['head_weight_owner_bounds']) if head_ids else None
        box = sample['projected_geometry_bbox']
        sample['geometry_clips'] = box[0] < 0 or box[1] < 0 or box[2] >= width or box[3] >= height
        for value in sample['bones'].values():
            value['head_stage'] = project(value['head_world'])
            value['tail_stage'] = project(value['tail_world'])
        sample['joint_roles'] = {role: {'bone': mapping['bone'], 'point': mapping['point'],
                                       'world': sample['bones'][mapping['bone']][mapping['point'] + '_world'],
                                       'stage': sample['bones'][mapping['bone']][mapping['point'] + '_stage']}
                                 for role, mapping in cfg['joint_roles'].items()}
    camera_meta = {'location': list(camera.location), 'rotation_euler': list(camera.rotation_euler),
                   'ortho_scale': camera.data.ortho_scale, 'shift_x': camera.data.shift_x, 'shift_y': camera.data.shift_y,
                   'pixels_per_world_unit': scale, 'constraints': constraints,
                   'world_rig_origin_stage': [origin_x, origin_y], 'declared_2D_pivot': cfg['pivot'],
                   'standing_visual_sole_reference_y': sole_y, 'standing_target_height': target_height,
                   'standing_achieved_geometry_height': standing_height * scale,
                   'standing_head_owner_height': (stand['head_weight_owner_bounds']['up'][1] - stand['head_weight_owner_bounds']['up'][0]) * scale if head_ids else None,
                   'same_camera_all_frames': True, 'per_frame_fit': False}
    metadata = {'schema': 'motion-guide-result/v1', 'classification': 'Pose geometry; optional Head-scale edit is authored, not a full anatomical/contact retarget',
                'source_glb_sha256': source_hash, 'source_action': cfg['action'],
                'allow_extrapolation': allow_extrapolation, 'source_time_interval_seconds': source_interval,
                'source_interval_epsilon_seconds': time_epsilon, 'extrapolated_frames': extrapolated_frames,
                'source_action_curve_hash': source_action_hash, 'authored_action_curve_hash': action_hash(authored),
                'authored_action': authored.name, 'head_scale': head_cfg, 'changed_curve_count': len(changes),
                'unchanged_curve_count': unchanged, 'nonHead_joint_world_max_error': max_joint_error,
                'original_pitch_channels_exact': True, 'source_action_unchanged': True,
                'camera': camera_meta, 'samples': samples,
                'owner_note': 'Head/foot owner bboxes use declared vertex weights; palms/contacts are caller-defined bone proxies, not measured skin contacts.'}
    # No output folder is created until sources, action edits, and whole-range geometry fit have been measured.
    require(not output.exists(), 'Output appeared while preparing guide; refusing overwrite')
    output.mkdir()
    write_json(output / 'config.json', cfg)
    write_json(output / 'geometry.json', metadata)
    write_json(output / 'head-key-changes.json', changes)
    write_json(output / 'source-clock.json', actual_clock)
    if license_file:
        shutil.copyfile(license_file, output / 'source-license.txt')
    provenance = {'source_glb_path': str(source), 'source_glb_sha256': source_hash,
                  'config_path': str(config_path), 'config_sha256': config_hash,
                  'helper_sha256': sha(Path(__file__)), 'blender_version': bpy.app.version_string,
                  'source_license_supplied_metadata': license_meta,
                  'source_license_sha256': sha(license_file) if license_file else None,
                  'downloads': False, 'original_source_modified': False,
                  'raw_source_glb_copied': False, 'source_derived_assets_in_saved_blend': True,
                  'saved_blend_contents': 'Imported mesh, rig and available actions; caller must hold redistribution rights',
                  'allow_extrapolation': allow_extrapolation, 'extrapolated_frames': extrapolated_frames,
                  'source_time_interval_seconds': source_interval, 'source_interval_epsilon_seconds': time_epsilon}
    write_json(output / 'provenance.json', provenance)

    render = cfg.get('render', {})
    material = bpy.data.materials.new('diagnostic_motion_guide_clay')
    color = render.get('color', [.18, .48, .6, 1])
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = .8
    mesh.data.materials.clear()
    mesh.data.materials.append(material)
    bpy.ops.object.light_add(type='AREA', location=render.get('light_position', [-3, -4, 6]))
    bpy.context.object.data.energy = render.get('light_energy', 650)
    bpy.context.object.data.size = render.get('light_size', 5)
    scene.world = bpy.data.worlds.new('diagnostic_motion_guide_world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = render.get('world_strength', .6)
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = render.get('samples', 32)
    scene.cycles.use_denoising = False
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = render.get('threads', 4)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.view_transform = 'Standard'
    scene.render.film_transparent = True
    frame_dir, mask_dir = output / 'frames', output / 'masks'
    frame_dir.mkdir()
    mask_dir.mkdir()
    bind_action(rig, authored)
    pngs, alpha = {}, []
    for sample in samples:
        frame = sample['source_frame']
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        if head_name:
            require(all(abs(rig.pose.bones[head_name].scale[i] - sample['evaluated_head_scale'][i]) < 1e-5 for i in range(3)),
                    'Scale changed at render evaluation; manual pose override is not a substitute for keyed edits')
        path = frame_dir / f'{frame:04}.png'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        w, h, rgba = read_rgba_png(path)
        require((w, h) == (width, height), 'Wrong native PNG dimensions')
        pngs[frame] = rgba
        report = alpha_report(w, h, rgba)
        report.update({'source_frame': frame, 'source_time_nominal': sample['source_time_nominal'],
                       'file': str(path.relative_to(output)), 'png_sha256': sha(path),
                       'rgba_sha256': hashlib.sha256(rgba).hexdigest()})
        alpha.append(report)
        mask = bytes(value for i in range(0, len(rgba), 4) for value in (255, 255, 255, rgba[i + 3]))
        write_rgba_png(mask_dir / f'{frame:04}-alpha.png', width, height, mask)
    write_json(output / 'alpha-clipping.json', {'frames': alpha, 'geometry_any_clip': any(s['geometry_clips'] for s in samples),
               'alpha_any_canvas_edge': any(a['alpha_touches_canvas_edge'] for a in alpha),
               'note': 'Continuous mesh bounds and actual alpha>0 raster bounds are separate checks; edges may include filtering.'})
    if sheet_cfg:
        k, columns, rows = sheet_cfg['scale'], sheet_cfg['columns'], sheet_cfg['rows']
        sheet_w, sheet_h = width * k * columns, height * k * rows
        sheet = bytearray(sheet_w * sheet_h * 4)
        for index, frame in enumerate(sheet_cfg['frames']):
            sw, sh, scaled = resize_nearest(width, height, pngs[frame], k)
            blit(sheet, sheet_w, scaled, sw, sh, index % columns * sw, index // columns * sh)
        write_rgba_png(output / 'selected-full-cell-sheet.png', sheet_w, sheet_h, sheet)
        write_json(output / 'sheet-layout.json', {'size': [sheet_w, sheet_h], 'stage': [width, height],
                   'columns': columns, 'rows': rows, 'nearest_scale': k, 'frames': sheet_cfg['frames'],
                   'stage_per_cell': [0, 0, width * k, height * k], 'labels': False, 'margins': False, 'matte': False})
    matte = tuple(render.get('contact_matte', [184, 194, 204, 255]))
    for name, chosen in [('selected', contacts), ('all', frames)]:
        columns = min(8, len(chosen))
        rows = (len(chosen) + columns - 1) // columns
        cw, ch = columns * width, rows * (height + 12)
        contact = bytearray(bytes(matte) * (cw * ch))
        for index, frame in enumerate(chosen):
            ox, oy = index % columns * width, index // columns * (height + 12)
            label(contact, cw, f'f{frame:03} {frame / fps:.2f}s', ox + 1, oy + 2)
            blit(contact, cw, matte_rgba(pngs[frame], matte), width, height, ox, oy + 12)
        write_rgba_png(output / f'{name}-native-contact.png', cw, ch, contact)
        if name == 'selected':
            k = int(render.get('contact_scale', 3))
            sw, sh, large = resize_nearest(cw, ch, contact, k)
            write_rgba_png(output / 'selected-enlarged-contact.png', sw, sh, large)
    scene.frame_set(frames[0])
    bpy.context.view_layer.update()
    require(action_hash(source_action) == source_action_hash and sha(source) == source_hash, 'Original source changed')
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'motion-guide.blend'))
    verification = {'source_glb_hash_unchanged': True, 'source_action_hash_unchanged': True,
                    'only_declared_scale_channels_changed': True, 'changed_curve_count': len(changes),
                    'other_curve_count_exact': unchanged, 'source_pitch_retained': True,
                    'actual_frame_evaluated_scale_checked': True, 'nonHead_joint_world_max_error': max_joint_error,
                    'all_frames_measured_before_render': True, 'rendered_frames': frames,
                    'geometry_any_clip': any(s['geometry_clips'] for s in samples),
                    'actual_alpha_any_canvas_edge': any(a['alpha_touches_canvas_edge'] for a in alpha),
                    'same_camera_all_frames': True, 'per_frame_fit': False,
                    'art_or_physical_contact_approval': False, 'full_chibi_anatomical_retarget': False}
    write_json(output / 'verification.json', verification)
    write_json(output / 'SHA256.json', {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'SHA256.json'})
    print('MOTION_GUIDE_COMPLETE ' + json.dumps({'output': str(output), 'frames': len(frames), 'camera': camera_meta, 'checks': verification}))


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    run(args.config, args.output.absolute())


if __name__ == '__main__':
    main()
