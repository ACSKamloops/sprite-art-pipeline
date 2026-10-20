# v9 → v10 isolated art/runtime delta audit

**Verified: the runtime/art delta is confined to the intended 16 Brann SE/SW walk cells plus expected source/binding metadata.** No unexpected runtime or bake content difference was found. Whole-directory equality is false; auxiliary file differences are listed below.

Frozen snapshot: 2026-10-17T01:39:59.526933+00:00. Audited `/home/astra/artifacts/emberwake-walk-game-preview-v9/{bake,project}` and the corresponding v10 trees. All writes are confined to this audit folder. No engine/browser run, broad runtime test, canonical edit, or art rerating was performed.

## Exact atlas changes

The actual atlas files decode as PNG RGBA, with 128×128 cells and 16 columns. Rowan is 2048×2048; Lyra and Brann are 2048×2176. **Rowan and Lyra complete atlas PNG files are byte-identical across versions. Brann changes only cells 136–143 and 232–239.** All other 256 Brann cells, including padding, retain identical decoded RGBA bytes. Across all three atlas grids, 784 of 800 cells are identical.

Indices, rows, columns and pixel origins are zero-based. Every rectangle is 128×128.

| Clip/cel | Atlas index | Row, column | Pixel origin x,y | Changed RGBA pixels |
|---|---:|---|---|---:|
| Brann SE 00 | 136 | 8, 8 | 1024, 1024 | 3558 |
| Brann SE 01 | 137 | 8, 9 | 1152, 1024 | 3442 |
| Brann SE 02 | 138 | 8, 10 | 1280, 1024 | 3435 |
| Brann SE 03 | 139 | 8, 11 | 1408, 1024 | 3371 |
| Brann SE 04 | 140 | 8, 12 | 1536, 1024 | 3513 |
| Brann SE 05 | 141 | 8, 13 | 1664, 1024 | 3572 |
| Brann SE 06 | 142 | 8, 14 | 1792, 1024 | 3670 |
| Brann SE 07 | 143 | 8, 15 | 1920, 1024 | 3452 |
| Brann SW 00 | 232 | 14, 8 | 1024, 1792 | 3558 |
| Brann SW 01 | 233 | 14, 9 | 1152, 1792 | 3442 |
| Brann SW 02 | 234 | 14, 10 | 1280, 1792 | 3435 |
| Brann SW 03 | 235 | 14, 11 | 1408, 1792 | 3371 |
| Brann SW 04 | 236 | 14, 12 | 1536, 1792 | 3513 |
| Brann SW 05 | 237 | 14, 13 | 1664, 1792 | 3572 |
| Brann SW 06 | 238 | 14, 14 | 1792, 1792 | 3670 |
| Brann SW 07 | 239 | 14, 15 | 1920, 1792 | 3452 |

All 16 cells are exactly the existing `southeast_walk` and `southwest_walk` frame-index lists. SE cells bind the actual individual baked SE00–07 PNGs. SW cells exactly match their reflection about pivot x64 (flip-left-right plus one-pixel x offset). These checks cover both v9 and v10. Brann’s native SE 1024×512 strip matches its 32 individual cels; only its first eight cells change. All other baked PNG files remain byte-identical.

Brann atlas SHA-256:

| Version | PNG SHA-256 |
|---|---|
| v9 | `c4211d937aaed65936f31bab1b3814babf837d95fd9daf94a5e4ebea1df492fc` |
| v10 | `7f0e089b1ebbdae95ee775c648559d9e77d792c2d7b76d7854a259b9c0a8d4cc` |

Per-cell old/new RGBA hashes and rectangles: [atlas-cell-deltas.json](atlas-cell-deltas.json). Every recorded full-bake lineage hash was checked against its actual atlas cell.

## Manifest and runtime semantics

All **48 clips per hero / 144 total** are semantically identical: frame indices/order, holds, loops, cast-hand tracks, cast-hand locations, release index, pivot, draw scale, grid, and every other manifest value remain unchanged except `/directional_source`. That source pointer changes in each of the three baked animation manifests and their exact three project copies. Brann’s SE/SW walks keep eight holds of 0.05625 = 9/160 seconds, totaling exactly 9/20 = 0.45 seconds.

The changed metadata is bounded:

- Brann `lineage.json`: exactly 48 leaf changes, comprising each intended cell’s RGBA hash and selected source path/hash. Other fields and cells remain unchanged.
- Brann `source-ownership.json`: exactly 17 leaf changes inside SE `walk_override`: eight source paths, eight hashes, and the scope text. Other ownership records remain unchanged.
- `REPLAY.json`: exactly 22 leaf changes confined to configuration hash, the three manifest hashes, Brann atlas hash, and Brann SE selected source/scope. Its artifact hashes match the actual atlas/manifests. Selected source PNG hashes match actual baked SE PNG bytes.

The catalog’s three runtime atlas/manifests are exact copies of their corresponding bakes in both versions. The seven existing runtime GDScripts, `project.godot`, `scenes/main.tscn`, character catalog, and all other common runtime assets/configuration remain byte-identical. The four differing runtime/project files are the Brann atlas and the three source-pointer-only animation manifests. Static consumers do not reference `directional_source` or the changed auxiliary files.

Full JSON leaf differences: [json-differences.json](json-differences.json). Bake/project equality: [bake-project-bindings.json](bake-project-bindings.json). Static reference evidence: [runtime-reference-evidence.json](runtime-reference-evidence.json).

## Directory differences outside default runtime

| Tree | v9 files | v10 files | Changed | Added | Removed |
|---|---:|---:|---:|---:|---:|
| bake | 211 | 211 | 16 | 0 | 0 |
| project | 214 | 200 | 4 | 2 | 16 |
| Total | 425 | 411 | 20 | 2 | 16 |

Added offline helpers:

- `project/scripts/build_engine_walk_gallery.py`
- `project/scripts/summarize_action_traces.py`

Absent in v10:

- `project/tests/audio_teardown_probe.gd` and `project/tests/final_polish_cleanup.gd`.
- Fourteen saved evidence files under `project/docs/evidence/`: the prior checks receipt/logs and two additional system/spell receipts.

These are actual directory differences and are not represented as whole-directory equality. The Python helpers have owner UID1000 and are offline capture/report tools. The removed GDScripts are test helpers. No static reference to these added/removed auxiliary files exists in the runtime script/scene/resource/config consumers. The complete list, hashes and categories are in [file-differences.json](file-differences.json).

## Receipt, reproduction and limits

**138/138 static audit checks passed.** Audited file lists/hashes stayed stable from the initial inventory through the audit execution. Before/after ledgers bind every audited file: [inventory-start.json](inventory-start.json), [inventory-end.json](inventory-end.json). [receipt.json](receipt.json) binds the script hash and result; [checks.json](checks.json) contains each check. [SHA256SUMS](SHA256SUMS) binds the audit outputs.

Reproduce with Python 3 and Pillow, without launching Godot:

```bash
python '/home/astra/artifacts/emberwake-v10-art-delta-audit-v1/audit.py'
```

Generated `.godot`, `output`, and `.git` trees are excluded. Root-level capture media, logs and earlier acceptance reports are outside this comparison. External registration config, source-art and baker implementation files were not opened; their recorded binding strings/hashes were inspected, and the selected-source hashes were checked against actual baked SE PNGs. This audit establishes file/pixel/manifest scope only. It does not certify import success, live behavior, rendering, ground contact or game acceptance.
