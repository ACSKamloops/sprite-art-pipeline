#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Create static glTF previews from the reachable MW4 joint hierarchy.

These are rigid mesh parts parented to named nodes, not animated skins.
Native ERF/armature files remain authoritative for unsupported render elements.
"""
import json
import struct
from collections import defaultdict
from pathlib import Path, PurePosixPath

import numpy as np

from erf import read_erf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"


def active_hierarchy(group):
    by_source = defaultdict(list)
    for joint in group["joints"]:
        by_source[joint["source"]].append(joint)
    roots = [source for source in by_source
             if Path(source).name.endswith("_" + group["chassis"] + ".contents")]
    if len(roots) != 1:
        raise ValueError(f"Expected one root armature: {roots}")
    sources_by_id = {int(Path(s).name.split("_", 1)[0]): s for s in by_source}
    seen_sources, seen_names, active = set(), set(), []

    def walk(source, parent):
        if source in seen_sources:
            raise ValueError("Reused or cyclic armature source: " + source)
        seen_sources.add(source)
        for joint in by_source[source]:
            if joint["parent"] != parent or joint["name"] in seen_names:
                raise ValueError("Ambiguous reachable joint: " + joint["name"])
            seen_names.add(joint["name"])
            active.append(joint)
            ref = joint["child_armature_reference"]
            if ref["archive_number"] == 1:
                walk(sources_by_id[ref["id"]], joint["name"])
            elif ref["archive_number"] != 65535:
                raise ValueError("Unsupported child archive: " + str(ref))

    walk(roots[0], "__model_root__")
    return active, sorted(set(by_source) - seen_sources)


class GLB:
    def __init__(self, name):
        self.bin = bytearray()
        self.doc = {
            "asset": {"version": "2.0", "generator": "MW4 mech-only static preview exporter"},
            "scene": 0, "scenes": [{"nodes": [0]}],
            "nodes": [{"name": name, "children": []}],
            "meshes": [], "accessors": [], "bufferViews": [],
            "materials": [], "textures": [], "images": [],
            "samplers": [{"magFilter": 9729, "minFilter": 9987,
                          "wrapS": 10497, "wrapT": 10497}],
            "extras": {"purpose": "Static rest assembly; no Blender actions or skin weights",
                       "coordinates": "Native Y-up; glTF importer converts to Blender Z-up"},
        }
        self.materials = {}

    def buffer_view(self, raw, target=None):
        self.bin.extend(b"\0" * (-len(self.bin) % 4))
        view = {"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(raw)}
        if target:
            view["target"] = target
        self.bin.extend(raw)
        self.doc["bufferViews"].append(view)
        return len(self.doc["bufferViews"]) - 1

    def accessor(self, values, component_type, kind, dtype, target):
        arr = np.asarray(values, dtype=dtype)
        accessor = {"bufferView": self.buffer_view(arr.tobytes(), target),
                    "componentType": component_type, "count": len(arr), "type": kind}
        if kind == "VEC3":
            accessor["min"] = arr.min(axis=0).tolist()
            accessor["max"] = arr.max(axis=0).tolist()
        self.doc["accessors"].append(accessor)
        return len(self.doc["accessors"]) - 1

    def material(self, texture_name, textures):
        key = (texture_name or "").lower()
        if key in self.materials:
            return self.materials[key]
        pbr = {"metallicFactor": 0.0, "roughnessFactor": 0.8}
        if key:
            record = textures[key]
            png = OUT / record["png"]
            image_id = len(self.doc["images"])
            self.doc["images"].append({"name": key, "mimeType": "image/png",
                                       "bufferView": self.buffer_view(png.read_bytes())})
            texture_id = len(self.doc["textures"])
            self.doc["textures"].append({"source": image_id, "sampler": 0})
            pbr["baseColorTexture"] = {"index": texture_id}
        ident = len(self.doc["materials"])
        self.doc["materials"].append({"name": key or "untextured", "pbrMetallicRoughness": pbr,
                                       "doubleSided": True, "alphaMode": "OPAQUE",
                                       "extras": {"note": "Simple preview material; source alpha retained in PNG"}})
        self.materials[key] = ident
        return ident

    def mesh(self, part, textures):
        erf = read_erf((OUT / part["native"]).read_bytes())
        primitives, triangles, removed = [], 0, {"repeated_index_faces": 0, "duplicate_faces": 0}
        for mesh in erf["lods"][0]["meshes"]:
            faces, seen = [], set()
            for face in mesh["faces"]:
                if len(set(face)) < 3:
                    removed["repeated_index_faces"] += 1
                    continue
                key = tuple(sorted(face))
                if key in seen:
                    removed["duplicate_faces"] += 1
                    continue
                seen.add(key)
                faces.append(face)
            if not faces:
                continue
            attributes = {"POSITION": self.accessor(mesh["vertices"], 5126, "VEC3", "<f4", 34962)}
            if len(mesh["uvs"]) == len(mesh["vertices"]):
                # glTF uses upper-left UV origin, unlike Wavefront/Blender UVs.
                attributes["TEXCOORD_0"] = self.accessor(mesh["uvs"], 5126, "VEC2", "<f4", 34962)
            if len(mesh["normals"]) == len(mesh["vertices"]):
                normals = np.asarray(mesh["normals"], dtype=float)
                lengths = np.linalg.norm(normals, axis=1)
                if (lengths > 1e-8).all():
                    normals /= lengths[:, None]
                    attributes["NORMAL"] = self.accessor(normals, 5126, "VEC3", "<f4", 34962)
            indices = np.asarray(faces, dtype="<u2").reshape(-1)
            primitives.append({"attributes": attributes,
                               "indices": self.accessor(indices, 5123, "SCALAR", "<u2", 34963),
                               "material": self.material(mesh["texture"], textures), "mode": 4})
            triangles += len(faces)
        if not primitives:
            return None, 0, removed
        ident = len(self.doc["meshes"])
        self.doc["meshes"].append({"name": PurePosixPath(part["original_path"].replace("\\", "/")).stem,
                                    "primitives": primitives, "extras": {"native_erf": part["native"]}})
        return ident, triangles, removed

    def save(self, path):
        self.doc["buffers"] = [{"byteLength": len(self.bin)}]
        raw_json = json.dumps(self.doc, separators=(",", ":"), allow_nan=False).encode()
        raw_json += b" " * (-len(raw_json) % 4)
        self.bin.extend(b"\0" * (-len(self.bin) % 4))
        raw = (struct.pack("<4sII", b"glTF", 2, 28 + len(raw_json) + len(self.bin))
               + struct.pack("<I4s", len(raw_json), b"JSON") + raw_json
               + struct.pack("<I4s", len(self.bin), b"BIN\0") + self.bin)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def main():
    textures = {Path(t["png"]).stem.split("_", 1)[1].lower(): t
                for t in json.loads((OUT / "inventory/textures.json").read_text())}
    results = []
    for path in sorted((OUT / "inventory/mechs").glob("*.json")):
        group = json.loads(path.read_text())
        active, unreachable = active_hierarchy(group)
        available = {}
        for part in group["parts"]:
            original = PurePosixPath(part["original_path"].replace("\\", "/"))
            if original.parts[1].lower() == group["chassis"] and part["kind"] == "mesh_part":
                available[original.stem.lower()] = part
        glb = GLB(group["chassis"])
        nodes = {"__model_root__": 0}
        used, missing, header_transforms, cleanup, triangles = [], [], [], [], 0
        for joint in active:
            matrix = np.eye(4)
            matrix[:3, :] = np.asarray(joint["local_matrix_game_row_major_3x4"]).reshape(3, 4)
            node = {"name": joint["name"], "matrix": matrix.T.reshape(-1).tolist(),
                    "extras": {"mw4_data_reference": joint["data_reference"]}}
            name = joint["data_reference"]["name"]
            if name and name.lower().startswith("mechs\\") and joint["name"] != "joint_cage":
                stem = PurePosixPath(name.replace("\\", "/")).stem.lower()
                part = available.get(stem)
                if part:
                    mesh_id, count, removed = glb.mesh(part, textures)
                    if mesh_id is not None:
                        node["mesh"] = mesh_id
                        used.append(part["native"])
                        triangles += count
                        if any(removed.values()):
                            cleanup.append({"native": part["native"], **removed})
                        if part["header_transform_game"] is not None:
                            header_transforms.append({"native": part["native"],
                                                      "matrix": part["header_transform_game"],
                                                      "note": "ERF header transform preserved but not applied; inspect render definition before changing placement"})
                else:
                    missing.append({"joint": joint["name"], "data_reference": name,
                                    "note": "No matching loose ERF; native render definition retained"})
            index = len(glb.doc["nodes"])
            glb.doc["nodes"].append(node)
            glb.doc["nodes"][nodes[joint["parent"]]].setdefault("children", []).append(index)
            nodes[joint["name"]] = index
        target = OUT / "assembled" / (group["chassis"] + "_rest.glb")
        glb.save(target)
        results.append({"chassis": group["chassis"], "glb": target.relative_to(OUT).as_posix(),
                        "reachable_joint_nodes": len(active), "mesh_parts": len(used),
                        "triangles": triangles, "native_parts": used,
                        "unmatched_render_definitions": missing,
                        "unapplied_erf_header_transforms": header_transforms,
                        "preview_face_cleanup": cleanup,
                        "unreachable_armature_files": unreachable,
                        "status": "Static assembly from native rest transforms; not an animated Blender rig"})
    (OUT / "inventory/assemblies.json").write_text(json.dumps(results, indent=2) + "\n")
    summary_path = OUT / "inventory/summary.json"
    summary = json.loads(summary_path.read_text())
    summary["assembled_static_glb_previews"] = len(results)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"assemblies": len(results), "triangles": sum(r["triangles"] for r in results),
                      "mesh_parts": sum(r["mesh_parts"] for r in results),
                      "unmatched_render_definitions": sum(len(r["unmatched_render_definitions"]) for r in results)}, indent=2))


if __name__ == "__main__":
    main()
