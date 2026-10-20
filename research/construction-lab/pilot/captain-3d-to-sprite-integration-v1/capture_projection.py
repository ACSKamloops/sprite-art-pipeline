"""Read-only Blender camera witness for a frozen assembled sprite source.

Run inside Blender, passing --input <blend> --output <new directory> after --.
Render resolution changes are unsaved; no source pixels or geometry are edited.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.output.exists():
        raise FileExistsError('Preserve previous projection evidence')
    source_hash = hashlib.sha256(args.input.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(args.input.resolve()))
    scene = bpy.context.scene
    scene.frame_set(1)
    rows = []
    for size in (256, 384):
        scene.render.resolution_x = size
        scene.render.resolution_y = size
        scene.render.resolution_percentage = 100
        scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
        points = []
        for world in ((0, 0, -1), (.25, 0, -1), (0, .25, -1),
                      (0, 0, 0), (1, -2, -1), (-1, .5, .7)):
            projected = world_to_camera_view(scene, scene.camera, Vector(world))
            points.append({'world': world, 'actual_blender_pixel':
                           [float(projected.x * size), float((1 - projected.y) * size)]})
        rows.append({'resolution': size, 'camera_matrix':
                     [list(row) for row in scene.camera.matrix_world],
                     'ortho_scale': float(scene.camera.data.ortho_scale), 'points': points})
    assert hashlib.sha256(args.input.read_bytes()).hexdigest() == source_hash
    args.output.mkdir(parents=True)
    receipt = {'state': 'CAMERA_PROJECTION_WITNESS_NOT_ART_APPROVAL',
               'input_blend': str(args.input.resolve()), 'input_SHA256': source_hash,
               'script_SHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'method': 'bpy_extras.object_utils.world_to_camera_view',
               'witnesses': rows, 'source_file_unchanged': True}
    (args.output / 'witness.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('PROJECTION_WITNESS', args.output)


if __name__ == '__main__':
    main()
