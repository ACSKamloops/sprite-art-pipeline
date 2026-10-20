# Reusable offline host manual selector

[host_flood_mask.py](../../scripts/recovery_round3/host_flood_mask.py) accepts a supplied PNG, an explicit seed and normalized RGBA tolerance, and writes **only a selection mask and receipt**. It executes the pinned recovered Pixelorama host FloodFillObject file and original DrawingAlgos.similar_colors function without rewriting either algorithm. It is not automatic PixelLab background removal or private animation cleanup. [Provenance and boundaries](CUTOUT-ROUTE-PROVENANCE.md).

Example command; choose a fresh output directory:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python scripts/recovery_round3/host_flood_mask.py \
  --image /home/astra/artifacts/pixellab-cutout-connectivity-20261014/inputs/connectivity-rgba.png \
  --seed-x 0 --seed-y 0 \
  --tolerance 0.03137254901960784 \
  --output-dir /home/astra/artifacts/my-host-manual-selection
```

`--tolerance` is the original normalized componentwise RGBA comparison tolerance 0..1, **not** an integer byte-distance or perceptual threshold. Source alpha participates. Approximate Color equality is the original helper's early shortcut. A user-selected seed supplies the color; this wrapper does not infer a background color or decide which foreground object to retain.

`mask.png` is RGBA: selected pixels `[255,255,255,255]`, unselected pixels `[255,255,255,0]` (transparent white). Consume its alpha channel as selection; its RGB channels alone are not a selection bitmap. The input is never cleared, recolored or forced opaque. Any later editing operation applying this mask belongs to a separate, explicit editing step. `receipt.json` records source PNG hash, source method hashes, seed/tolerance, original segment count, selected-pixel count, mask hash, decoder format, engine, wrapper hash and all fixture boundaries.

The source pins are:

- Recovered `FloodFillObject.gd`: `63f7320fbb151e1959265a8e1331c341cefaf6511c1975e69df1ccf515c15cb7`.
- Recovered `DrawingAlgos.gd`: `6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9`.

The whole recovered FloodFill file is used unchanged, with local Project/SelectionMap declarations appended. Project size comes from the PNG; `has_selection=false`; active selection bounds and tilemap/undo branches are not exercised. DrawingAlgos is a local instance containing only the unchanged extracted original similar_colors method. A local callback converts emitted original spans to a mask. The receipt explicitly lists these stubs and wrapper operations. This is recovered-source replay, not a proof of equivalence to original compiled GDC; PCK membership evidence is retained separately.

## Bounds and demonstrated checks

Input must have a PNG signature/IHDR, at most 4MiB and dimensions 1..512 on each side (262144 pixels maximum). Dimensions are checked from the verified byte snapshot before decoding. Seed must lie inside the image; tolerance must be finite and 0..1. Recovered source hashes must match. Output directory must be fresh; an existing directory is rejected. Verified input bytes are snapshotted locally, decoded by Godot and converted to RGBA8 if needed; that conversion is declared in the receipt. The subprocess has a 60-second timeout, and a temporary isolated Godot project/data directory is removed afterward. No network, provider, credential resolver or packaged-app startup exists in this CLI.

[Targeted checks](HOST-SELECTOR-CLI-CHECKS.json) passed for NaN tolerance, out-of-bounds seed, 513×1 input, non-PNG input and existing output directory. Each returned exit 2; new output directories were not created, and existing receipt bytes were unchanged. Actual timeout and source-pin mutation failures were not induced; those guards are inspected code paths. Recheck these guards with:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python scripts/recovery_round3/check_host_selector_guards.py
```

## Two retained source-method masks

Both examples use the corrected 96px fixture, seed (0,0), and unchanged original methods. Their receipts bind the exact source PNG and CLI hash.

| Example | Tolerance | Selected pixels | Mask PNG SHA256 |
| --- | --- | --- | --- |
| [mask at 8/255](manual-selector-examples/tolerance8/mask.png), [receipt](manual-selector-examples/tolerance8/receipt.json) | `0.03137254901960784` | 5761 | `8d5c66ecbbdcee0c85ba0c0dd994894b43b893781be078bc8e516f340b824579` |
| [mask at 32/255](manual-selector-examples/tolerance32/mask.png), [receipt](manual-selector-examples/tolerance32/receipt.json) | `0.12549019607843137` | 5889 | `d46178aa2e071504bd68d7bb26fa377dbeeb79868258979706830aca51c11fc3` |

The first is a repeatable precision counterexample: the distance 8 strip is excluded. Its decoded normalized red difference `0.0313725546002388` exceeds supplied 8/255 `0.0313725490196078`. Therefore a mathematical integer tolerance≤8 would select 5825 pixels while this original host implementation selects 5761. Do not clamp/round that difference away and still claim source-exact host behavior. The second mask still differs from the captured public Complex cutout at one pixel, so it must not be offered as an exact service substitute.

This concrete channel is ready for a caller to consume as **manual host selection**. Full editor integration and original GPU global-color shader execution remain separate work. Zero provider calls were made to build or check it.

The first example receipts mislabeled unselected pixels as transparent black. Independent review decoded the PNGs and found transparent white. Original masks/receipts are preserved; [the correction and fresh replay receipts](MASK-CONVENTION-CORRECTION.json) record the corrected metadata and unchanged PNG hashes. The recovered method and mask construction were not altered.
