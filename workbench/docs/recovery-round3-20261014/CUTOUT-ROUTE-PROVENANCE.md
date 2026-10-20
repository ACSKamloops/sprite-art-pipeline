# Cutout route provenance and recovered local selector

**A source-exact local manual selector is available; an automatic PixelLab cutout implementation is still unknown.** The recovered Pixelorama host contains a complete scanline flood selector and componentwise RGBA comparison. Neither is called by the inspected PixelLab removal/animation request paths. This pass executes those recovered host methods unchanged, verifies four relevant extracted files against the shipped PCK, and keeps public endpoint observations separate.

No API/provider calls, credentials, browser/profile access, runtime edits or research writes were made. Sources were read from `/home/astra/projects/pixellab-local-test-20261011`; new files belong to this isolated worktree only. Previous [initial](../recovery-next-20261014/CUTOUT-FINDINGS.md) and [corrected](../recovery-next-20261014/CUTOUT-CONNECTIVITY-FINDINGS.md) endpoint measurements remain unchanged.

## Which code selects the route and policy?

The [28-anchor ledger](CUTOUT-PROVENANCE-LEDGER.json) records exact file/slice hashes, lines, minified offsets and OpenAPI pointers. It also retains existing REA record IDs/limitations; static or inferred graph observations are not execution proof. No new live REA/browser attachment was used.

| Layer | Recovered behavior | Boundary |
| --- | --- | --- |
| Godot `RemoveBackground.gd:69–120` | Maps selector index to `remove_simple_background` / `remove_complex_background`; text null for Simple, optional for Complex; captures image/dimensions, tool URL `remove-background`. | No background-color picker, flood threshold or local segmentation here. `flat_generation_cost` returns 1.0; this is client source, not a guarantee of future server pricing. |
| `ToolBase.gd:368–386` → `Main.gd:563–583` | Builds/validates payload and dispatches through migrated-endpoint map. `remove-background` is migrated; default base URL is `https://api.pixellab.ai/`. | Recovered client uses legacy service interface, not necessarily public `/v2` behavior. |
| `background_generation.gd:73–103` | Courier submits `remove-background/background`; completed images later reach ordinary image placement. | Remote job/response processing; no foreground estimator. Response blit is not segmentation. |
| Lua `generate-remove-background.lua:69–95` | Same task names; Simple omits text; Complex may retain it; remote `remove-background` request. | No local cutout estimator. |
| Website `create-677791a6e206dafa.js` | Builder forwards `backgroundRemovalTask`, defaulting Simple; includes text if prompt is provided. UI shows “Subject to keep” for Complex. | The builder itself does not gate text by mode, unlike the inspected Lua/Godot wrapper. No claim that every browser state sends identical fields. |
| Website helper 6848, export FX | Draws uploaded image to canvas and serializes browser RGBA. | Decode/canvas conversion, not source-foreground inference. Browser normalization may differ from direct PNG uploads. |
| PixMiniMax Godot/Lua | First/last-frame/caption/frame-count/seed and `no_background`; route `animate-minimax-h3`. Godot dispatch uses WS since this route is absent from the migrated map. | No `background_removal_task` argument or call to the standalone removal tool in these paths. Internal animation cutout remains remote/unknown. |

The retained public OpenAPI declares `RemoveBackgroundRequest` task modes and optional subject text, and says animation `no_background=true` cuts out an opaque first frame before animating. It does not disclose how the internal operation is implemented, which mode it uses, or whether it reuses `/remove-background`. The five captured public requests measure `/v2/remove-background`; shared words are not proof of shared code with legacy client routes or animation workers.

A bounded literal scan across 126 extension Godot scripts, 112 Lua scripts, 105 website chunks and one shipped editor bundle found no `FloodFillObject`, `ColorSelect.gdshader`, `ColorReplace.gdshader`, flood-fill, color-to-alpha or chroma-key name. This supports the traced separation but is not proof against obfuscated, differently named or private methods.

## Actual local utilities in the shipped host

| Utility | Actual method | Coverage this pass |
| --- | --- | --- |
| `src/Classes/FloodFillObject.gd` | Scanline spans around a user seed; adjacent-row traversal; optional selection bounds; source color similarity controls eligibility. | Entire recovered file executed unchanged, selection-bounds branch disabled by fixture. |
| `DrawingAlgos.gd:752 similar_colors` | Approx-equal Color shortcut, then componentwise absolute RGBA difference ≤ normalized tolerance; tol 0 otherwise rejects. | Original function text executed unchanged. |
| MagicWand / Bucket / Gradient | Actual callers of host flood selector. MagicWand default tolerance 0.003, slider value/255; Bucket can fill returned spans using user's color. | Call sites statically traced; no full editor/undo/tilemap execution. |
| `ColorSelect.gdshader` | Global per-pixel RGBA tolerance selection; add/subtract/intersect operations. | Original PCK membership verified; shader inspected, not GPU-executed. |
| `ColorReplace.gdshader` | Replaces globally matching RGBA with user-supplied new color/pattern inside selection alpha. Transparent new color can support manual color removal. | Original PCK membership verified; source inspected, not GPU-executed. This is not automatic foreground extraction. |
| SmartSlicer `RegionUnpacker.gd` | Floods existing alpha>0 islands into bounding rectangles. | Static inventory; it consumes an alpha mask and does not discover a background from RGB. |
| Transparency/checker, blur, palette shaders | Display/compositing/effects. | Not reclassified as foreground estimators because they mention alpha. |

### PCK provenance

[Godot membership proof](PCK-MEMBER-PROOF.json): mounted `evidence/pixelorama_pixellab.pck` read-only, without launching packaged scenes or autoloads, and compared four allowlisted resource byte arrays to extracted files. PCK SHA256: `ebf9812ea474bddb84faa22183a1ec0178983cdc285674a4d0177c606e8a4a3f`.

- Compiled `FloodFillObject.gdc`: `0ee165629964a97e45e137916339feb30eb3eaaa29dbaf67032a59b38ab3801c`.
- Compiled `DrawingAlgos.gdc`: `94c363fed83c79f26338d29ddbc671b32c696ba403c56c01a858ceb8aec0456c`.
- `ColorSelect.gdshader`: `27f8c50cfd9517fff45c8fd8171530b2b301e5acd6d5ace93687e151641378f2`.
- `ColorReplace.gdshader`: `b46064050032d39b28a4ac62d09808c463ea55506bbfffcb2380dc71a8cda81c`.

Membership proves extraction identity, not lossless decompilation equivalence. The replay executes recovered source, not original compiled GDC. Recovered FloodFill source SHA256 is `63f7320fbb151e1959265a8e1331c341cefaf6511c1975e69df1ccf515c15cb7`; recovered DrawingAlgos source SHA256 is `6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9`.

### Unchanged recovered-method replay

[Receipt](HOST-FLOOD-REPLAY.json) covers 12 runs: three source PNGs × tolerances 0/1/8/32 divided by 255, seed (0,0), no active selection. The whole recovered FloodFill file is preserved byte-for-byte as a prefix; local Project/SelectionMap stubs and dependency declaration are appended. Original `similar_colors` is extracted without translating its body. Local callback merely fills original emitted spans into a mask. Host state/undo, arbitrary active selections, tilemaps and shaders are not exercised.

Two assertions check the RGBA-alpha comparison and approximate-equality shortcut. The latter accepts a tiny float-channel difference even at tolerance 0; this does not make distinct ordinary RGBA8 colors identical.

On the initial source, 6538 pixels are selected, matching all captured masks at all tested tolerances. Comparing that selection to endpoint RGBA requires an **explicitly local** wrapper that clears selected pixels and makes retained alpha 255; the source selector itself does not implement that alpha restoration. On the corrected source:

| Requested tolerance | Host-selected pixels | Simple mask mismatches | Complex mask mismatches |
| --- | --- | --- | --- |
|0/255 |5697 |282 |193 |
|1/255 |5761 |218 |129 |
|8/255 |5761 |218 |129 |
|32/255 |5889 |90 |1 |

The host method still fails the corrected service outputs, including Complex's `(20,48)` counterexample. No exception patch is added.

**Reproducible precision boundary:** at the red-distance 8 strip, the decoded Color-channel difference is `0.0313725546002388`; requested 8/255 is `0.0313725490196078`. Original `similar_colors` rejects that comparison. Therefore source-exact host tolerance 8 does not behave like an integer RGB-distance≤8 Python candidate. This is measured source behavior, not a newly invented tolerance rule or evidence that the server uses it.

## What can be reused and the next useful test

A local manual editing channel can truthfully expose the recovered host seed/tolerance selection method with source hashes, explicit user seed, original normalized RGBA tolerance semantics and declared host-selection limits. It must be named/labeled a **Pixelorama host selector**, not automatic PixelLab cutout, server parity or private animation cleanup. The choice to clear selected pixels is a separate editing operation/wrapper; silently forcing source alpha 255 would be misleading.

The next useful offline step is a reusable bounded PNG→mask CLI around these same unchanged methods, preserving seed/tolerance and mask provenance. A later exact GPU replay can verify original global ColorSelect/ColorReplace behavior before exposing those shader tools. If further public service trials are separately authorized, orientation/translation of the one-pixel `(20,48)` boundary is a narrow discriminator; this report authorizes or performs no extra calls. Do not patch a special pixel or fit an arbitrary global mask to erase the current counterexample.

Reproduce with root Python environment:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python scripts/recovery_round3/replay_host_flood.py
python3 scripts/recovery_round3/verify_pck_members.py
python3 scripts/recovery_round3/build_cutout_ledger.py
```
