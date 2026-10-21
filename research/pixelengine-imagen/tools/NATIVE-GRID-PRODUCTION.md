# Genuine native-grid production experiment

`native-grid-production.py` crops explicitly pinned raw sheet cells and invokes
the actual `offline-pixelengine.cjs` shared-frame path. It does not replace the
processor, infer an output size, resample artwork or call a generation/network
service. Wrapper/WASM files remain external and must satisfy the adapter's
hard-coded complete-file hashes; see [README.md](README.md).

```bash
.venv/bin/python research/pixelengine-imagen/tools/native-grid-production.py \
  --plan /absolute/external/production-plan.json \
  --wrapper /absolute/external/retained-wrapper.js \
  --wasm /absolute/external/retained-pixel-tools.wasm \
  --output /absolute/external/fresh-experiment \
  --reference-eight /absolute/external/prior-eight-experiment \
  --native-editor /absolute/path/to/existing/libresprite
```

Add `--verify-replay` only for an eight-source exact replay. The reference
directory uses `inputs/`, `wasm/`, `STAGING.json`, `timing.json` and
`clips/native-grid/`. A replay must match all eight prepared-input PNG hashes,
native PNG bytes/RGBA,80px exported PNG bytes/RGBA, actual grid, global offset,
per-frame source bounds, exact metadata, palette/artifact bindings and clock.
Path-bearing receipt/project provenance can differ and is not presented as
byte-identical. A larger batch records differences instead of claiming exact
preservation of its eight original sources.

Keep the case-specific plan outside Git. Its shape is:

```json
{
  "schema": "native-grid-production/v1",
  "sheets": {
    "keys": {"file": "/external/raw-sheet.png", "sha256": "HASH", "cell_edge": 418}
  },
  "palette_results": {"file": "/external/palette-results.json", "sha256": "HASH"},
  "clip_id": "native-grid",
  "frames": [
    {"id": "pose-00", "sheet": "keys", "cell": 0, "hold": [1, 8]}
  ]
}
```

Each source sheet is an exact3x3 layout. Cell indices are row-major0–8; no
automatic bounds fitting occurs. Supply the whole ordered clip and positive
rational holds totaling one second. The pinned palette-results file must
contain the actual52 opaque `palette_rgba` entries, in their original order.
No palette is fitted again by this runner; genuine processor palette/grid
inference can still change which requested colors appear and every output key.

Alpha preparation explicitly sets positive alpha1–7 to transparent black and
separately zeros hidden RGB at alpha0. This distinction matters for raw sheets
that contain nonzero invisible RGB. Every RGBA value at alpha>=8 must remain
exact. Raw sheet bytes, exact crop rectangles, unmodified crop PNG/RGBA pins,
prepared inputs and affected-pixel counts are retained. The actual adapter's
runtime metadata string and complete receipt remain authoritative.

If the real grid exceeds80px, any frame is empty or one global staging offset
clips visible paint, the runner records the invalid condition and stops before
inventing a scale. Otherwise it uses one integer translation for the entire
clip: grid integer-center anchor maps to x40, and the maximum observed alpha
bottom maps to y72. Raw native rasters remain preserved; no pose is fitted or
recentered independently. In an odd-width grid, the integer-center convention
is explicit rather than a fractional resample.

The existing constructor/exporter supplies one editable whole-body raster
layer, exact tick durations, atlas, PNGs, ASE/sidecar and rational APNG. Optional
actual LibreSprite save/reopen checks rendered frame pixels and the full
imported project. Emitted engine-input files do not establish gameplay tests.

Compare complete native/2x actors, each adjacent pair and wrap, the original
eight-source native-grid run and an immutable original control. Inspect both
cluster clarity and temporal identity/volume; crisp edges alone cannot repair
an inconsistent body drawing. Preserve raw new-batch key differences, actual
viewing conditions and failures. No art score or motion superiority follows
from successful conversion, a larger frame count or exact export mechanics.
