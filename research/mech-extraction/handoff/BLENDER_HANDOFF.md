# MechWarrior 4 mech library for Blender

This is a local extraction of the MyAbandonware **MekTek version** of MechWarrior 4: Mercenaries. The intended workflow is mech animation, texture updates, and short films. Maps, buildings, vehicles, infantry, and battle armor are excluded from this handoff.

## Start here

1. Open `blender/atlas.blend` in Blender. It contains assembled rigid mesh parts, named joint nodes, packed original textures, a preview camera, and lights. Try `blender/madcat.blend` for another familiar example. For a clean interchange import, use `assembled/atlas_rest.glb` through **File > Import > glTF 2.0**.
2. Read `inventory/mechs/atlas.json` and `inventory/assemblies.json` for the original part references, hierarchy, transforms, and assembly limitations.
3. Save your working `.blend` separately. Create new materials and texture copies while retaining the original UVs and named parts.
4. For native motions, inspect the `.mw4anim` files and animation scripts before creating Blender actions. The binary keyframes have **not** been decoded or converted.

Every chassis group has a `.blend` file and a static GLB preview. These contain parented objects and empties, not Blender armature bones, skin weights, or animation actions. Rigid parenting provides a useful starting point for posing a mech; the next agent can animate the joint objects or create a control rig. Open the hierarchy in the Outliner and select a named joint object to rotate its attached parts. The native rest transforms remain the reference for resetting a pose.

The `.blend` files include this guide, the individual mech manifest, and the assembly reference as Blender Text data blocks. Source notes therefore travel with each model. The preview camera/lights are grouped in `Preview Studio`; materials retain original color maps. Save edits as a new file and use Render Image for a first visual check.

## What is included

| Asset | Count | Location |
| --- | ---: | --- |
| Chassis directory groups | 113 | `inventory/library.json` |
| Blender projects with packed textures | 113 | `blender/` |
| Assembled static GLB previews | 113 | `assembled/` |
| Highest-detail OBJ mesh parts | 3,905 | `models/<chassis>/<variant>/` |
| Native ERF levels of detail | 18,008 | `native/` |
| Native animation files | 3,724 | `native/props/mechs/` |
| Native files with “pose” in their name | 364 | `inventory/animations.json` |
| PNG textures including mip families | 710 | `textures/` |
| Distinct directly referenced material textures | 125 | `inventory/textures.json` |
| Native files with source hashes | 22,423 | `inventory/native-files.json` |

**113 groups does not mean 113 distinct playable mechs.** This includes original and MekTek chassis, variants, prototypes, and a `standard` placeholder. Destroyed variants are grouped with their chassis. OBJ files include damaged parts, wrecks, cockpit cages, and extra parts; they are not separate complete mechs. Original names and archive IDs are preserved so another agent can identify these correctly.

The 364 pose-named files are a searchable subset of the native animation files. They are not 364 verified Blender poses. Some chassis borrow animation families from other mechs; the expanded script dependencies are recorded in each chassis manifest. A chassis with no clips under its own directory may still use shared motions.

## Folder map

- `assembled/`: static, highest-detail exterior previews with embedded PNGs.
- `blender/`: Blender 4.5 LTS projects with packed images, joint hierarchy, embedded notes, and a preview studio.
- `models/`: individual OBJ/MTL parts and adjacent JSON metadata, including other variants and cockpit meshes.
- `textures/`: lossless RGBA PNG conversions. Original TGA bytes are retained under `native/textures/textures/`.
- `native/`: original extracted ERF geometry, armatures, scripts, animations, render definitions, and related mech metadata.
- `inventory/`: file hashes, model catalog, per-chassis manifests, animation index, dependencies, and validation reports.
- `tooling/`: Python format readers, an optional LOD exporter, source attribution, and GPL license text for the helper code.
- `provenance/`: source download metadata and extraction/ERF parse reports.

## Geometry, coordinates, and materials

The GLBs use native Y-up coordinates, which a conforming Blender glTF importer converts to Blender Z-up. The OBJ vertices and normals are already converted to Blender coordinates with `(x, -z, y)`. OBJ UVs use `(u, 1-v)`; GLB UVs retain the native upper-left image convention. Do not apply the coordinate conversion twice. The original units are retained; physical dimensions have not been normalized across MekTek assets.

Each OBJ is a **local mesh part**. Its neighboring JSON records the source path, version, bounding sphere, optional header transform, and all LOD counts. Use the named joint hierarchy to place parts. The GLB assembly follows the root `.contents` file and its archive-ID child references; unused armature files are not added to the scene. This prevents stale duplicate joint definitions from being assembled twice.

GLB materials use the original color maps and simple opaque preview shading. Texture alpha is preserved in PNGs. The old game's shader flags, team-color behavior, emissive behavior, and transparency have not been recreated. Normal, roughness, metallic, and other modern texture maps have not been generated. Inspect the source material definitions before assigning new PBR behavior.

Full-resolution source textures are commonly named with a trailing `0`; the adjacent `1` through `5` files are mipmaps, not alternate skins. Use `inventory/textures.json` to check pixel dimensions and original names. Texture references may be shared across parts and chassis; copy or deliberately share updated materials accordingly.

## Assembly limits to inspect

- Masakari's `joint_specialone` references a native render definition without a matching loose ERF. Its source files are preserved, but this element is absent from the static preview. It is not a missing extraction file.
- Fourteen assembled parts across ten chassis have an additional ERF header transform. These transforms are recorded in `inventory/assemblies.json` but have not been applied automatically, because their relationship to the native render transform still needs verification. Check affected parts before treating a preview as an exact in-game assembly.
- Cockpit cages, damaged variants, wrecks, and unmatched extras remain available as OBJ and native files; the static previews assemble exterior parts with matching joint data names.
- Six ERFs contain inconsistent declared LOD block lengths. Their actual geometry was parsed to the end of the file and exported successfully. The original discrepancies remain recorded in each part's `source_size_warnings`.
- Static GLB/Blender previews omit 23 faces with repeated vertex indices and 672 duplicate faces which Blender may reject or remove during import. Preview materials are double-sided. Original ERFs and the full OBJ exports retain all source faces; per-part cleanup counts are recorded in `inventory/assemblies.json`.

## Native motions and armatures

The per-chassis manifest contains raw joint record interpretations:

- `name` and `parent` preserve the original joint names.
- `local_matrix_game_row_major_3x4` is the native local transform with translation in the fourth column.
- `data_reference` and `child_armature_reference` preserve the source archive number and ID.
- `source` and `record_offset` identify the exact native bytes.

The animation index records filenames, source chassis, pose-name classification, and a header duration where the header length matches. A duration is **not** a decoded animation. Preserve all raw bytes until keyframe channels, rotation conventions, timing, and shared references have been verified. Validate one known stand pose and one walk cycle on Atlas before converting the whole library. Avoid assuming a humanoid skeleton or discarding helper joints.

Some MekTek `.subsystems` files use a `mektek` wrapper. They are retained with `.mektek` appended and labeled opaque gameplay metadata. They have not been decrypted; this did not block geometry, texture, or animation extraction.

## Validation completed

- All 520 source `.mw4` archive indexes scanned without index errors.
- Mech extraction completed without failures.
- All 3,905 ERFs parsed, preserving 18,008 LODs.
- All 22,423 extracted native files match their recorded sizes and SHA-256 hashes.
- All 710 PNG conversions match the RGBA pixels decoded from the original TGA files.
- All 3,905 OBJs independently loaded with trimesh and matched the source LOD0 triangle counts; referenced texture paths were checked.
- All 113 GLBs independently loaded and matched expected triangle counts and finite bounds.
- The official Khronos glTF Validator reported zero errors and zero warnings across all 113 GLBs.
- All 113 projects passed Blender 4.5.9 LTS import, save, reopen, packed-image, geometry-count, and coordinate checks, recorded in `inventory/blender-validation.json`.
- Atlas passed a joint-rotation test: rotating `joint_torsoabove` moved its attached mesh descendants, and the rest transform was restored. Embedded notes were checked and a textured render was produced at `previews/atlas.png`; details are in `inventory/blender-smoke-test.json`.

Details are in `inventory/validation.json`, `inventory/gltf-validation.json`, and `inventory/blender-validation.json`. Portable Blender 4.5.9 LTS is retained in the workspace and checked against the official download checksum. Visual comparison against the game and native animation decoding remain work for the next stage.

## Suggested next-agent task

> Read BLENDER_HANDOFF.md and the inventory files. Build a Blender workflow for the complete mech library, starting with Atlas to validate import, original UVs, material assignment, joint hierarchy, and scale. Keep the original extraction intact and save edited assets separately. Create a rigid mech control rig using the source joint names. Inspect and decode the native pose/animation format before claiming any motion has been recovered; verify shared animation references. Update textures using the original UV layouts, then prepare scenes for short films. Expand the validated workflow to every mech chassis group, including variants, and report unsupported render elements or motions explicitly.

Source and helper-code attribution is recorded in `provenance/README.md` and `tooling/THIRD_PARTY.md`.
