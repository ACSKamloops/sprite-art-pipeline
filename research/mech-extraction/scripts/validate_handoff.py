#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Independently load exports and compare their contents with the native assets."""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"


def main():
    report = {"checks": {}, "failures": [],
              "blender_runtime_tested": False,
              "note": "Independent trimesh loading and pixel/hash checks; animation keyframes are not decoded"}
    failures = report["failures"]
    native = json.loads((OUT / "inventory/native-files.json").read_text())
    for record in native:
        path = OUT / record["output"]
        data = path.read_bytes()
        if len(data) != record["output_bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            failures.append({"native": record["output"], "error": "size or SHA-256 mismatch"})
    report["checks"]["native_hashes"] = len(native)
    print("Native hashes checked:", len(native), flush=True)

    texture_count = 0
    for record in json.loads((OUT / "inventory/textures.json").read_text()):
        with Image.open(OUT / record["output"]) as source, Image.open(OUT / record["png"]) as export:
            source_rgba = source.convert("RGBA")
            export_rgba = export.convert("RGBA")
            if source_rgba.size != export_rgba.size or source_rgba.tobytes() != export_rgba.tobytes():
                failures.append({"png": record["png"], "error": "pixel mismatch"})
        texture_count += 1
    report["checks"]["png_pixel_round_trips"] = texture_count
    print("PNG pixel round trips:", texture_count, flush=True)

    part_count = triangle_count = textured_surfaces = 0
    for manifest in sorted((OUT / "inventory/mechs").glob("*.json")):
        group = json.loads(manifest.read_text())
        for part in group["parts"]:
            obj = OUT / part["obj"]
            # MTL paths intentionally share textures in the handoff root.
            resolver = trimesh.resolvers.FilePathResolver(obj.parent, allow_anywhere=True)
            scene = trimesh.load_scene(obj, process=False, group_material=False, resolver=resolver)
            triangles = sum(len(mesh.faces) for mesh in scene.geometry.values())
            if triangles != part["lods"][0]["triangles"]:
                failures.append({"obj": part["obj"], "error": "triangle count mismatch",
                                 "actual": triangles, "expected": part["lods"][0]["triangles"]})
            for mesh in scene.geometry.values():
                if not np.isfinite(mesh.vertices).all():
                    failures.append({"obj": part["obj"], "error": "nonfinite vertex"})
                if hasattr(mesh.visual, "uv") and mesh.visual.uv is not None and not np.isfinite(mesh.visual.uv).all():
                    failures.append({"obj": part["obj"], "error": "nonfinite UV"})
                material = getattr(mesh.visual, "material", None)
                image = getattr(material, "image", None)
                if image is not None:
                    image.load()
                    textured_surfaces += 1
            # Verify every MTL material's texture reference separately, including
            # materials which a loader might merge or omit for empty surfaces.
            for line in obj.with_suffix(".mtl").read_text().splitlines():
                if line.startswith("map_Kd "):
                    target = (obj.parent / line[7:]).resolve()
                    if not target.is_relative_to(OUT.resolve()) or not target.is_file():
                        failures.append({"obj": part["obj"], "error": "invalid texture path"})
            part_count += 1
            triangle_count += triangles
    report["checks"].update({"obj_parts_loaded": part_count, "obj_triangles": triangle_count,
                              "obj_textured_surfaces_loaded": textured_surfaces})
    print("OBJ files independently loaded:", part_count, flush=True)

    previews = json.loads((OUT / "inventory/assemblies.json").read_text())
    for assembly in previews:
        scene = trimesh.load_scene(OUT / assembly["glb"], process=False)
        triangles = sum(len(mesh.faces) for mesh in scene.geometry.values())
        if triangles != assembly["triangles"] or scene.bounds is None or not np.isfinite(scene.bounds).all():
            failures.append({"glb": assembly["glb"], "error": "triangle count or bounds mismatch"})
        assembly["validated_bounds_game_y_up"] = scene.bounds.tolist()
        assembly["validated_trimesh_surfaces"] = len(scene.geometry)
    (OUT / "inventory/assemblies.json").write_text(json.dumps(previews, indent=2) + "\n")
    report["checks"]["glb_previews_loaded"] = len(previews)
    report["passed"] = not failures
    (OUT / "inventory/validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
