#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Verify rigid joint posing and render the saved Atlas Blender project."""
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"

scene = bpy.context.scene
joint = bpy.data.objects.get("joint_torsoabove")
if joint is None:
    raise RuntimeError("Named torso joint was not preserved in Blender")
descendants = [obj for obj in joint.children_recursive if obj.type == "MESH"]
before = {obj.name: obj.matrix_world.copy() for obj in descendants}
original = joint.matrix_basis.copy()
joint.rotation_mode = "XYZ"
joint.rotation_euler.z += 0.35
bpy.context.view_layer.update()
moved = [obj.name for obj in descendants
         if any(abs(obj.matrix_world[r][c] - before[obj.name][r][c]) > 1e-5
                for r in range(4) for c in range(4))]
joint.matrix_basis = original
bpy.context.view_layer.update()
if not moved:
    raise RuntimeError("Changing the torso joint did not move its mesh descendants")
if not all(name in bpy.data.texts for name in
           ["READ_ME_BLENDER_HANDOFF.md", "MECH_MANIFEST.json", "ASSEMBLY_REFERENCE.json"]):
    raise RuntimeError("Embedded model notes are missing")
previews = OUT / "previews"
previews.mkdir(exist_ok=True)
scene.render.filepath = str(previews / "atlas.png")
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
if not Path(scene.render.filepath).is_file():
    raise RuntimeError("Atlas preview was not written")
report = {"blender_version": bpy.app.version_string, "blend": "blender/atlas.blend",
          "pose_test": {"joint": joint.name, "local_rotation_radians": 0.35,
                        "mesh_descendants_moved": moved, "rest_transform_restored": True},
          "embedded_notes_verified": True, "render": "previews/atlas.png", "passed": True,
          "native_animations_converted": False}
(OUT / "inventory/blender-smoke-test.json").write_text(json.dumps(report, indent=2) + "\n")
print("MW4_BLENDER_SMOKE", json.dumps(report), flush=True)
