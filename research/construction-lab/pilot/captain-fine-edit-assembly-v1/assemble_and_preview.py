"""Bounded combined head/sole source preview, retaining the .4 sole shader."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
HEAD = HERE.parent / 'captain-head-fine-paint-v1'
SOURCE = Path('/home/astra/projects/captain-rig-carry-art-v8/experiments/captain-sole-fill-v1/captain-sole-fill04.blend')
SOURCE_SHA = 'fba9042c9e293fd083806e78625ea99d41e6969a76f23047d2fec15859cfc803'
PAINT = HEAD / 'combined-candidate/combined-body-paint.png'
PAINT_SHA = 'ceb0108276bb3be3f2d6c31367acb01c57818af2184e1f67e878d9fc97d9c4e8'
sys.path.insert(0, str(HEAD))
from render_candidates import mesh_fingerprint, evaluated_pose_fingerprint


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normal_signature():
    digest = hashlib.sha256()
    for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
        if obj.type != 'MESH':
            continue
        digest.update(obj.name.encode())
        digest.update(np.asarray([n.vector[:] for n in obj.data.corner_normals], dtype='<f4').tobytes())
        for attribute in obj.data.attributes:
            if 'normal' in attribute.name:
                digest.update(attribute.name.encode())
                digest.update(str([tuple(x.value) if hasattr(x.value, '__len__') else x.value
                                   for x in attribute.data]).encode())
    return digest.hexdigest()


def material_signature():
    """All node structure/defaults/filter inputs, excluding image identity."""
    rows = []
    for material in sorted(bpy.data.materials, key=lambda m: m.name):
        if not material.use_nodes:
            continue
        nodes = []
        for node in sorted(material.node_tree.nodes, key=lambda n: n.name):
            inputs = []
            for socket in node.inputs:
                if hasattr(socket, 'default_value'):
                    value = socket.default_value
                    inputs.append((socket.name, list(value) if hasattr(value, '__len__') and not isinstance(value, str) else value))
            nodes.append((node.name, node.type, getattr(node, 'interpolation', None),
                          getattr(node, 'extension', None), getattr(node, 'operation', None), inputs))
        links = sorted((x.from_node.name, x.from_socket.name, x.to_node.name, x.to_socket.name)
                       for x in material.node_tree.links)
        rows.append((material.name, nodes, links))
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def signatures():
    return {'mesh_UV_weights_shapes': mesh_fingerprint(),
            'all521_bone_object_shape_values': evaluated_pose_fingerprint(),
            'stored_corner_normals': normal_signature(),
            'material_nodes_defaults_links_filters': material_signature()}


assert sha(SOURCE) == SOURCE_SHA
assert sha(PAINT) == PAINT_SHA
OUT = HERE / 'preview'
OUT.mkdir(parents=True, exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
protected = signatures()
scene.render.resolution_x = scene.render.resolution_y = 384
scene.render.resolution_percentage = 100
scene.render.threads_mode = 'FIXED'
scene.render.threads = 6
scene.cycles.device = 'CPU'
records = []
for frame in (1, 33, 103):
    scene.frame_set(frame)
    path = OUT / f'control-source{frame:03}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    records.append({'kind': 'sole04-control', 'source': frame, 'file': path.name, 'sha256': sha(path)})

image = bpy.data.images.load(str(PAINT), check_existing=False)
image.name = 'CaptainCombinedHeadSolePaint_v1'
image.colorspace_settings.name = 'sRGB'
image.pack()
bindings = []
for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image and node.image.name == 'OwnedSoleTread_refined_v1':
            bindings.append({'material': material.name, 'node': node.name,
                             'filter': node.interpolation, 'extension': node.extension})
            node.image = image
assert len(bindings) == 3
assert protected == signatures(), 'Fine edit changed protected scene data'
for frame in (1, 33, 103):
    scene.frame_set(frame)
    path = OUT / f'combined-source{frame:03}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    records.append({'kind': 'combined', 'source': frame, 'file': path.name, 'sha256': sha(path)})
scene.frame_set(33)
packed = OUT / 'captain-combined-head-sole04.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(packed))
bpy.ops.wm.open_mainfile(filepath=str(packed))
path = OUT / 'combined-reopened-source033.png'
bpy.context.scene.render.filepath = str(path)
bpy.ops.render.render(write_still=True)
assert sha(SOURCE) == SOURCE_SHA and sha(PAINT) == PAINT_SHA
(OUT / 'receipt.json').write_text(json.dumps({
    'state': 'BOUNDED_COMBINED_SOURCE_PREVIEW_NOT_FULL_ART_APPROVAL',
    'source_sha256': SOURCE_SHA, 'combined_paint_sha256': PAINT_SHA,
    'script_sha256': sha(Path(__file__)), 'packed_sha256': sha(packed),
    'protected_signatures_before_after_exact': protected, 'bindings': bindings,
    'sole_shader_policy': 'original refined mask and local .4 emission retained exactly',
    'native_resolution': 384, 'source_frames': [1, 33, 103], 'renders': records,
    'limits': ['No new motion or geometry', 'No full65 cycle or art score',
               'Reopen pixel comparison performed separately',
               'Owned UV edits can change indirect lighting outside the head']
}, indent=2) + '\n')
print('COMBINED_PREVIEW_READY', flush=True)
