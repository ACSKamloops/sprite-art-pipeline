#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Run with Blender --background --python this_file -- --handoff PATH.

Import every assembled preview, pack textures, embed handoff notes, save .blend
files, and reopen them to verify their geometry, transforms, and packed images.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def mesh_stats(scene):
    objects = [obj for obj in scene.objects if obj.type == "MESH"]
    return {"mesh_objects": len(objects),
            "triangles": sum(sum(len(poly.vertices)-2 for poly in obj.data.polygons) for obj in objects),
            "vertices": sum(len(obj.data.vertices) for obj in objects)}


def world_bounds(scene):
    # Transform actual vertices. Transforming the eight local AABB corners
    # overestimates world bounds when a source joint is rotated.
    points = [obj.matrix_world @ vertex.co for obj in scene.objects
              if obj.type == "MESH" for vertex in obj.data.vertices]
    if not points:
        raise RuntimeError("No mesh objects")
    return [[min(p[axis] for p in points) for axis in range(3)],
            [max(p[axis] for p in points) for axis in range(3)]]


def preview_studio(scene, bounds):
    lower, upper = map(Vector, bounds)
    center = (lower + upper) * 0.5
    span = max((upper-lower))
    studio = bpy.data.collections.new("Preview Studio")
    scene.collection.children.link(studio)

    camera_data = bpy.data.cameras.new("Preview Camera")
    camera = bpy.data.objects.new("Preview Camera", camera_data)
    studio.objects.link(camera)
    camera.location = center + Vector((1.35, -1.8, 0.85)) * span
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = span * 1.35
    camera_data.clip_start = max(span * 0.0001, 0.001)
    camera_data.clip_end = max(span * 50, 100)
    scene.camera = camera
    for name, direction, factor, color in [
        ("Key", (1.0, -1.2, 1.4), 110, (1.0, 0.94, 0.85)),
        ("Fill", (-1.1, -0.6, 0.6), 45, (0.76, 0.86, 1.0)),
        ("Rim", (0.3, 1.1, 1.0), 130, (1.0, 1.0, 1.0)),
    ]:
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy = factor * span * span
        light_data.shape = "DISK"
        light_data.size = span * 0.8
        light_data.color = color
        light = bpy.data.objects.new(name, light_data)
        studio.objects.link(light)
        light.location = center + Vector(direction) * span
        light.rotation_euler = (center-light.location).to_track_quat("-Z", "Y").to_euler()
    world = bpy.data.worlds.new("Preview World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.045, 0.065, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                region = area.spaces.active.region_3d
                region.view_location = center
                region.view_distance = span * 1.7
                region.view_rotation = camera.rotation_euler.to_quaternion()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    root = args.handoff.resolve()
    assemblies = json.loads((root / "inventory/assemblies.json").read_text())
    output = root / "blender"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for assembly in assemblies:
        name = assembly["chassis"]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        status = bpy.ops.import_scene.gltf(filepath=str(root / assembly["glb"]))
        if status != {"FINISHED"}:
            raise RuntimeError(f"Import failed: {name}: {status}")
        scene = bpy.context.scene
        scene.name = "MW4 " + name
        bpy.context.view_layer.update()
        stats = mesh_stats(scene)
        if stats["triangles"] != assembly["triangles"] or stats["mesh_objects"] != assembly["mesh_parts"]:
            raise RuntimeError(f"Imported geometry mismatch: {name}: {stats}")
        bounds = world_bounds(scene)
        native_bounds = assembly["validated_bounds_game_y_up"]
        expected = [[native_bounds[0][0], -native_bounds[1][2], native_bounds[0][1]],
                    [native_bounds[1][0], -native_bounds[0][2], native_bounds[1][1]]]
        if any(abs(actual-wanted) > 0.0002 for row, desired in zip(bounds, expected)
               for actual, wanted in zip(row, desired)):
            raise RuntimeError(f"Blender coordinate/bounds mismatch: {name}: {bounds} vs {expected}")
        span = max(Vector(bounds[1])-Vector(bounds[0]))
        for obj in scene.objects:
            if obj.type == "EMPTY":
                obj.empty_display_type = "PLAIN_AXES"
                obj.empty_display_size = max(span * 0.01, 0.01)
                obj["MW4_usage"] = "Rigid joint control; local transform from native armature. Native actions not converted."
        preview_studio(scene, bounds)
        scene["MW4_chassis"] = name
        scene["MW4_source_manifest"] = "inventory/mechs/" + name + ".json"
        scene["MW4_animation_status"] = "Static rest hierarchy. Native clips retained; no converted actions."
        scene["MW4_assembly_notes"] = json.dumps({key: assembly[key] for key in
            ("unmatched_render_definitions", "unapplied_erf_header_transforms", "unreachable_armature_files", "preview_face_cleanup")})
        for source, label in [
            (root / "BLENDER_HANDOFF.md", "READ_ME_BLENDER_HANDOFF.md"),
            (root / "inventory/mechs" / (name + ".json"), "MECH_MANIFEST.json"),
            (root / "inventory/assemblies.json", "ASSEMBLY_REFERENCE.json"),
        ]:
            text = bpy.data.texts.new(label)
            text.write(source.read_text())
        bpy.ops.file.pack_all()
        images = [im for im in bpy.data.images if im.type == "IMAGE" and im.size[0] > 0]
        if any(not im.packed_file for im in images):
            raise RuntimeError("Unpacked texture image: " + name)
        scene.render.filepath = "//renders/" + name + ".png"
        bpy.context.preferences.filepaths.save_version = 0
        target = output / (name + ".blend")
        bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
        records.append({"chassis": name, "blend": target.relative_to(root).as_posix(),
                        "geometry": stats, "packed_texture_images": len(images),
                        "bounds_blender_z_up": bounds, "native_animation_actions": 0})
        print("MW4_BLEND_SAVED", name, json.dumps(stats), flush=True)

    # Reopen the serialized files, checking data after saving rather than only
    # trusting in-memory imports. Texture data must be self-contained.
    for record in records:
        bpy.ops.wm.open_mainfile(filepath=str(root / record["blend"]))
        scene = bpy.context.scene
        if mesh_stats(scene) != record["geometry"]:
            raise RuntimeError("Saved Blender geometry mismatch: " + record["chassis"])
        if any(not math.isfinite(v) for obj in scene.objects for row in obj.matrix_world for v in row):
            raise RuntimeError("Nonfinite Blender transform: " + record["chassis"])
        images = [im for im in bpy.data.images if im.type == "IMAGE" and im.size[0] > 0]
        if len(images) != record["packed_texture_images"] or any(not im.packed_file for im in images):
            raise RuntimeError("Saved packed texture mismatch: " + record["chassis"])
        record["save_reopen_passed"] = True
    report = {"blender_version": bpy.app.version_string, "files": len(records),
              "all_imported_saved_and_reopened": True, "failures": [], "results": records,
              "animation_actions_converted": False}
    (root / "inventory/blender-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print("MW4_BLENDER_VALIDATION", json.dumps({k:v for k,v in report.items() if k != "results"}), flush=True)


if __name__ == "__main__":
    main()
