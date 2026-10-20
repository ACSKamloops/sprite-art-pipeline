"""Actual matched controls for the UV trials; no approximate camera reuse."""
import argparse
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
SOURCE = Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-wide-accommodation-v1/full-captain-wide-cape-camera12-packed.blend')
parser = argparse.ArgumentParser()
parser.add_argument('--resolution', type=int, choices=(256,384), required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out = HERE / 'matched-controls' / f'native{args.resolution}'
out.mkdir(parents=True, exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
scene.render.resolution_x = scene.render.resolution_y = args.resolution
scene.render.resolution_percentage = 100
scene.render.threads_mode = 'FIXED'
scene.render.threads = 6
for frame in (1,33,103):
    scene.frame_set(frame)
    scene.render.filepath = str(out / f'original-source{frame:03}.png')
    bpy.ops.render.render(write_still=True)
