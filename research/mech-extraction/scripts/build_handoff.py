#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build a mech-only Blender handoff from the lossless native extraction."""
import collections
import hashlib
import io
import json
import math
import os
import re
import struct
from pathlib import Path, PurePosixPath

from PIL import Image

from erf import read_erf
from extract_mechs import write_entry
from mw4 import Archive

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def blender_vector(vector):
    x, y, z = vector
    return x, -z, y


def write_obj(path, lod, textures):
    path.parent.mkdir(parents=True, exist_ok=True)
    materials = []
    lines = ["# MW4 highest-detail mesh part; Blender Z-up coordinates (x, -z, y)",
             "# Local coordinates: assemble using the accompanying joint hierarchy.",
             "mtllib " + path.with_suffix(".mtl").name]
    vbase = uvbase = nbase = 1
    for index, mesh in enumerate(lod["meshes"]):
        material = "surface_" + str(index)
        lines.extend(["o mesh_" + str(index), "usemtl " + material])
        for vector in mesh["vertices"]:
            lines.append("v " + " ".join(f"{v:.9g}" for v in blender_vector(vector)))
        for u, v in mesh["uvs"]:
            lines.append(f"vt {u:.9g} {1-v:.9g}")
        for normal in mesh["normals"]:
            lines.append("vn " + " ".join(f"v{v}" if not math.isfinite(v) else f"{v:.9g}" for v in blender_vector(normal)))
        has_uv = len(mesh["uvs"]) == len(mesh["vertices"])
        has_normals = len(mesh["normals"]) == len(mesh["vertices"])
        for face in mesh["faces"]:
            corners = []
            for vertex in face:
                ref = str(vertex + vbase)
                if has_uv or has_normals:
                    ref += "/" + (str(vertex + uvbase) if has_uv else "")
                    if has_normals:
                        ref += "/" + str(vertex + nbase)
                corners.append(ref)
            lines.append("f " + " ".join(corners))
        vbase += len(mesh["vertices"])
        uvbase += len(mesh["uvs"])
        nbase += len(mesh["normals"])
        materials.extend(["newmtl " + material, "Kd 0.8 0.8 0.8", "Ks 0.1 0.1 0.1", "Ns 20"])
        texture = textures.get((mesh["texture"] or "").lower())
        if texture:
            rel = os.path.relpath(OUT / texture["png"], path.parent).replace(os.sep, "/")
            materials.append("map_Kd " + rel)
        materials.append("")
    path.write_text("\n".join(lines) + "\n")
    path.with_suffix(".mtl").write_text("\n".join(materials) + "\n")


def armature_records(file, data, core_ids):
    if (len(data)-2) % 280:
        raise ValueError("Unsupported armature record layout")
    match = re.search(r"\[([^]]+)\]", file["name"])
    parent = match.group(1) if match else "__model_root__"
    records = []
    for offset in range(2, len(data), 280):
        block = data[offset:offset+280]
        if struct.unpack_from("<I", block)[0] != 280:
            raise ValueError("Unexpected armature record length")
        name = block[152:280].split(b"\0", 1)[0].decode("cp1252")
        if not re.fullmatch(r"[A-Za-z0-9_ .-]+", name):
            raise ValueError("Unexpected joint name")
        matrix = struct.unpack_from("<12f", block, 28)
        if not all(math.isfinite(v) for v in matrix):
            raise ValueError("Nonfinite joint transform")
        archive, ident = struct.unpack_from("<HH", block, 84)
        child_archive, child_id = struct.unpack_from("<HH", block, 148)
        data_ref = core_ids.get(ident) if archive == 1 else None
        records.append({
            "parent": parent, "name": name,
            "local_matrix_game_row_major_3x4": list(matrix),
            "data_reference": {"archive_number": archive, "id": ident,
                               "name": data_ref.name if data_ref else None},
            "child_armature_reference": {"archive_number": child_archive, "id": child_id},
            "source": file["output"], "record_offset": offset,
        })
    return records


def expand_animation_defines(data):
    text = data.decode("cp1252")
    macros = dict(re.findall(r"^!([^=\s]+)\s*=\s*([^\r\n]*)", text, re.MULTILINE))
    for _ in range(32):
        changed = False
        for name, value in list(macros.items()):
            new = re.sub(r"\$\(([^)]+)\)", lambda m: macros.get(m.group(1), m.group(0)), value)
            if new != value:
                macros[name] = new
                changed = True
        if not changed:
            break
    dependencies = set()
    for value in macros.values():
        match = re.search(r"(?:content[\\/])?mechs[\\/]([^\\/]+)[\\/]animation", value, re.I)
        if match:
            dependencies.add(match.group(1).lower())
    return macros, sorted(dependencies)


def main():
    extraction = json.loads((ROOT / "reports/mech-extraction.json").read_text())
    if extraction["failures"]:
        raise RuntimeError("Resolve native extraction failures before building the handoff")
    files = extraction["files"]
    mesh_files = [f for f in files if f["name"].lower().endswith(".erf")]
    parsed = {}
    texture_names = set()
    for file in mesh_files:
        model = read_erf((OUT / file["output"]).read_bytes())
        parsed[file["output"]] = model
        for lod in model["lods"]:
            texture_names.update(m["texture"] for m in lod["meshes"] if m["texture"])

    texture_archive = Archive(ROOT / "sources/game/RESOURCE/textures.mw4")
    wanted = {name.lower() + ".tga" for name in texture_names}
    # Preserve the original mip families as well as the full-resolution material.
    for name in texture_names:
        if name.endswith("0"):
            wanted.update(name[:-1].lower() + str(level) + ".tga" for level in range(6))
    textures = {}
    texture_files = []
    for entry in texture_archive.entries:
        if entry.path.name.lower() not in wanted:
            continue
        record = write_entry(texture_archive, entry, role="mech_texture_dependency")
        data = (OUT / record["output"]).read_bytes()
        image = Image.open(io.BytesIO(data))
        image.load()
        image = image.convert("RGBA")
        path = OUT / "textures" / f"{entry.id:05d}_{entry.path.stem}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        record.update({"png": path.relative_to(OUT).as_posix(),
                       "width": image.width, "height": image.height, "mode": "RGBA"})
        texture_files.append(record)
        textures[entry.path.stem.lower()] = record
    missing = sorted(name for name in texture_names if name.lower() not in textures)
    if missing:
        raise RuntimeError("Missing material textures: " + repr(missing))
    save_json(OUT / "inventory/textures.json", texture_files)

    library = {}
    for file in mesh_files:
        parts = PurePosixPath(file["name"].replace("\\", "/")).parts
        variant = parts[1].lower()
        chassis = variant.removesuffix("_destroyed")
        model = parsed[file["output"]]
        stem = Path(file["output"]).stem
        obj = OUT / "models" / chassis / variant / (stem + "_lod0.obj")
        write_obj(obj, model["lods"][0], textures)
        kind = "cockpit" if "cage" in stem.lower() else "damaged_part" if "_dam" in stem.lower() else "mesh_part"
        if variant.endswith("_destroyed"):
            kind = "wreck_part"
        lods = [{"index": lod["index"], "min_distance_squared": lod["min_distance_squared"],
                 "max_distance_squared": lod["max_distance_squared"],
                 "vertices": sum(len(m["vertices"]) for m in lod["meshes"]),
                 "triangles": sum(len(m["faces"]) for m in lod["meshes"]),
                 "textures": sorted({m["texture"] for m in lod["meshes"] if m["texture"]})}
                for lod in model["lods"]]
        info = {"native": file["output"], "archive": file["archive"], "id": file["id"],
                "original_path": file["name"], "kind": kind,
                "obj": obj.relative_to(OUT).as_posix(), "version": model["version"],
                "bounding_sphere_game": model["bounding_sphere"],
                "header_transform_game": model["header_transform"],
                "lods": lods, "source_size_warnings": model["warnings"],
                "export": {"lod": 0, "coordinates": "x,-z,y", "uv": "u,1-v",
                           "placement": "local; use joint hierarchy"}}
        save_json(obj.with_suffix(".json"), info)
        group = library.setdefault(chassis, {"chassis": chassis, "parts": [], "joints": [],
                                            "animations": [], "animation_scripts": [], "notes": []})
        group["parts"].append(info)

    core_archive = Archive(ROOT / "sources/game/RESOURCE/core.mw4")
    core_ids = {entry.id: entry for entry in core_archive.entries}
    armature_errors = []
    animations = []
    for file in files:
        path = PurePosixPath(file["name"].replace("\\", "/"))
        variant = path.parts[1].lower()
        chassis = variant.removesuffix("_destroyed")
        group = library.get(chassis)
        suffix = path.suffix.lower()
        if group and file["archive"] == "RESOURCE/core.mw4" and (
            suffix == ".contents" or file["name"].lower().endswith("{armature}")
        ):
            try:
                group["joints"].extend(armature_records(file, (OUT / file["output"]).read_bytes(), core_ids))
            except ValueError as error:
                armature_errors.append({"file": file["output"], "error": str(error)})
        if suffix in (".animscript", ".animskript") and group:
            definitions, dependencies = expand_animation_defines((OUT / file["output"]).read_bytes())
            group["animation_scripts"].append({"native": file["output"], "definitions": definitions,
                                               "animation_chassis_dependencies": dependencies})
        if suffix == ".mw4anim":
            data = (OUT / file["output"]).read_bytes()
            duration = struct.unpack_from("<f", data, 13)[0] if len(data) >= 45 else None
            header_ok = len(data) >= 45 and struct.unpack_from("<I", data, 17)[0] == len(data)-1
            info = {"native": file["output"], "original_path": file["name"],
                    "source_chassis": chassis, "id": file["id"],
                    "pose_named": "pose" in path.stem.lower(),
                    "header_duration_seconds": duration if header_ok and math.isfinite(duration) else None,
                    "header_length_matches": header_ok,
                    "conversion_status": "native_only; not a Blender action"}
            animations.append(info)
            if group:
                group["animations"].append(info)

    for group in library.values():
        dependencies = sorted({dep for script in group["animation_scripts"]
                               for dep in script["animation_chassis_dependencies"]})
        group["animation_chassis_dependencies"] = dependencies
        if not group["animations"]:
            group["notes"].append("No animations stored under this chassis name. Inspect shared references; do not invent missing actions.")
        save_json(OUT / "inventory/mechs" / (group["chassis"] + ".json"), group)
    save_json(OUT / "inventory/animations.json", animations)
    save_json(OUT / "inventory/native-files.json", files + texture_files)
    save_json(OUT / "inventory/armature-issues.json", armature_errors)
    save_json(OUT / "inventory/library.json", [{
        "chassis": g["chassis"], "manifest": "inventory/mechs/" + g["chassis"] + ".json",
        "mesh_parts": len(g["parts"]), "joint_records": len(g["joints"]),
        "native_animation_files": len(g["animations"]),
        "animation_chassis_dependencies": g["animation_chassis_dependencies"],
    } for _, g in sorted(library.items())])
    summary = {"chassis_groups": len(library), "erf_files": len(mesh_files),
               "obj_mesh_parts": len(mesh_files), "native_animation_files": len(animations),
               "pose_named_native_files": sum(a["pose_named"] for a in animations),
               "textures_with_mips": len(texture_files), "direct_material_textures": len(texture_names),
               "all_native_files": len(files) + len(texture_files),
               "lods_preserved_in_native_erf": sum(len(m["lods"]) for m in parsed.values()),
               "armature_issues": len(armature_errors),
               "native_extraction_errors": len(extraction["failures"]),
               "animations_converted_to_blender_actions": False}
    save_json(OUT / "inventory/summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
