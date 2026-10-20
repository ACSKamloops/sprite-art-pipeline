# Helper code attribution

`erf.py` interprets the public MechWarrior 4 ERF editor source by Scanner (2003), published at [RivvidGunner/Mechwarrior-4-ERFEditor](https://github.com/RivvidGunner/Mechwarrior-4-ERFEditor). The upstream repository supplies a GPL version 3 license. Its original Pascal units and license are included here under `upstream/`.

The Python adaptation and the associated extraction/export scripts are supplied under GPL-3.0-only. Changes include Python porting, bounds checks, complete-file validation, support for untextured surfaces with render flags, JSON inventories, and OBJ/GLB exports. The GPL applies to helper code, not to the extracted game assets.

`mw4.py` is a Python archive reader informed by the public MW4 VBD and animation-archive descriptions mirrored at:

- https://mirror.aluigi.org/bms/xentax_cs/MW4_VBD.bms
- https://mirror.aluigi.org/bms/xentax_cs/Mechwarrior_4_Merc_MW4.bms

The portable readers use the Python standard library. Workspace exports use Pillow, NumPy, and trimesh; GLB validation uses the official Khronos `gltf-validator` package. These dependencies are not bundled in this package.

For an additional retained level of detail, run:

```bash
python tooling/export_lods.py atlas --lod 1 --output /path/to/new/lod_exports
```

This optional exporter writes local geometry and UVs only. The existing LOD0 exports also include normals and MTL texture links.
