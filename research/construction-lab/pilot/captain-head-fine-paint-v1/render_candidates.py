"""Bake bounded source-paint trials from an unchanged assembled rig in Blender."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-wide-accommodation-v1/full-captain-wide-cape-camera12-packed.blend')
EXPECTED = '9d9e2387496e4b46d148da7e274d080cc09d90714c6a034946f53609d52ef84c'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mesh_fingerprint():
    digest = hashlib.sha256()
    for obj in sorted(bpy.context.scene.objects, key=lambda x: x.name):
        if obj.type != 'MESH':
            continue
        digest.update(obj.name.encode())
        for vertex in obj.data.vertices:
            digest.update(np.asarray(vertex.co, dtype='<f4').tobytes())
            for group in vertex.groups:
                digest.update(np.asarray([group.group, group.weight], dtype='<f8').tobytes())
        for polygon in obj.data.polygons:
            digest.update(np.asarray(polygon.vertices, dtype='<i4').tobytes())
        for layer in obj.data.uv_layers:
            digest.update(np.asarray([loop.uv[:] for loop in layer.data], dtype='<f4').tobytes())
        if obj.data.shape_keys:
            for block in obj.data.shape_keys.key_blocks:
                digest.update(np.asarray([v.co[:] for v in block.data], dtype='<f4').tobytes())
    return digest.hexdigest()


def evaluated_pose_fingerprint():
    scene = bpy.context.scene
    digest = hashlib.sha256()
    objects = sorted(scene.objects, key=lambda x: x.name)
    for index in range(521):
        frame = 1 + index / 4
        scene.frame_set(math.floor(frame), subframe=frame % 1)
        bpy.context.view_layer.update()
        for obj in objects:
            digest.update(np.asarray(obj.matrix_world, dtype='<f4').tobytes())
            if obj.type == 'ARMATURE':
                for bone in obj.pose.bones:
                    digest.update(np.asarray(bone.matrix, dtype='<f4').tobytes())
            if obj.type == 'MESH' and obj.data.shape_keys:
                digest.update(np.asarray([b.value for b in obj.data.shape_keys.key_blocks], dtype='<f4').tobytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resolution', type=int, choices=(256, 384), required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    assert sha(SOURCE) == EXPECTED
    out = HERE / 'renders' / f'native{args.resolution}'
    if out.exists():
        raise FileExistsError('Preserve previous renders')
    out.mkdir(parents=True)
    results = []
    for name in ('detail-sharpen', 'authored-temple-plate'):
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
        scene = bpy.context.scene
        geometry_before = mesh_fingerprint()
        pose_before = evaluated_pose_fingerprint()
        texture = HERE / 'candidates' / f'{name}.png'
        image = bpy.data.images.load(str(texture), check_existing=False)
        image.colorspace_settings.name = 'sRGB'
        image.pack()
        bindings = []
        for material in bpy.data.materials:
            if not material.use_nodes:
                continue
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image and node.image.name.startswith('Material_0-side-polish-UV'):
                    bindings.append({'material': material.name, 'node': node.name, 'filter': node.interpolation})
                    node.image = image
        assert len(bindings) == 3, bindings
        assert mesh_fingerprint() == geometry_before
        assert evaluated_pose_fingerprint() == pose_before
        scene.render.resolution_x = scene.render.resolution_y = args.resolution
        scene.render.resolution_percentage = 100
        scene.render.threads_mode = 'FIXED'
        scene.render.threads = 6
        records = []
        for frame in (1, 33, 103):
            scene.frame_set(frame)
            path = out / f'{name}-source{frame:03}.png'
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            records.append({'source_frame': frame, 'file': path.name, 'SHA256': sha(path)})
        if args.resolution == 384:
            scene.frame_set(33)
            scene.render.filepath = str(out / f'{name}-source033.png')
            packed = out / f'{name}.blend'
            bpy.ops.wm.save_as_mainfile(filepath=str(packed))
            bpy.ops.wm.open_mainfile(filepath=str(packed))
            reopened = out / f'{name}-reopened-source033.png'
            bpy.context.scene.render.filepath = str(reopened)
            bpy.ops.render.render(write_still=True)
        results.append({'name': name, 'texture_SHA256': sha(texture), 'bindings': bindings,
                        'geometry_UV_weights_shapes_SHA256': geometry_before,
                        'all521_evaluated_pose_object_shape_values_SHA256': pose_before,
                        'geometry_pose_unchanged': True, 'renders': records})
    assert sha(SOURCE) == EXPECTED
    (out / 'receipt.json').write_text(json.dumps({'state': 'BOUNDED_HEAD_PAINT_RENDER_NOT_ART_APPROVAL',
        'source_SHA256': EXPECTED, 'script_SHA256': sha(__file__), 'native_resolution': args.resolution,
        'results': results, 'limits': ['Shader image binding changed only; no geometry or action authored',
        '521 evaluated key times, not a continuum proof', 'Head-only raster mask still requires actual nonhead leakage review']}, indent=2) + '\n')
    print('HEAD_PAINT_RENDER', args.resolution)


if __name__ == '__main__':
    main()
