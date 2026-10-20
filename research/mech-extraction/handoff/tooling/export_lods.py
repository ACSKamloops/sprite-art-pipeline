#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Export any retained native LOD as Blender-coordinate OBJ from a manifest."""
import argparse
import json
from pathlib import Path

from erf import read_erf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chassis", help="Chassis directory name, e.g. atlas")
    parser.add_argument("--lod", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True, help="Separate output directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.lod < 0 or Path(args.chassis).name != args.chassis:
        parser.error("Use a chassis name and a nonnegative LOD index")
    manifest = root / "inventory/mechs" / (args.chassis + ".json")
    group = json.loads(manifest.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    exported = 0
    for part in group["parts"]:
        model = read_erf((root / part["native"]).read_bytes())
        if args.lod >= len(model["lods"]):
            continue
        # This utility exports geometry and UVs; use existing LOD0 MTLs as the
        # material reference when constructing a full Blender importer.
        lines = ["# MW4 local mesh part, Blender Z-up (x, -z, y)"]
        vertex_base = uv_base = 1
        for index, mesh in enumerate(model["lods"][args.lod]["meshes"]):
            lines.append("o surface_" + str(index))
            lines.extend(f"v {x:.9g} {-z:.9g} {y:.9g}" for x, y, z in mesh["vertices"])
            lines.extend(f"vt {u:.9g} {1-v:.9g}" for u, v in mesh["uvs"])
            uv = len(mesh["uvs"]) == len(mesh["vertices"])
            for face in mesh["faces"]:
                lines.append("f " + " ".join(
                    f"{i+vertex_base}/{i+uv_base}" if uv else str(i+vertex_base) for i in face))
            vertex_base += len(mesh["vertices"])
            uv_base += len(mesh["uvs"])
        original = Path(part["obj"])
        directory = args.output / original.parent.name
        directory.mkdir(parents=True, exist_ok=True)
        name = original.name.removesuffix("_lod0.obj") + f"_lod{args.lod}.obj"
        (directory / name).write_text("\n".join(lines) + "\n")
        exported += 1
    print(f"Exported {exported} parts at LOD {args.lod} to {args.output}")


if __name__ == "__main__":
    main()
