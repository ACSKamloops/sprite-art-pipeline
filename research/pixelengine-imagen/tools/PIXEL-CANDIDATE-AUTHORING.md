# Literal pixel candidate recipe

`author-pixel-candidates.py` consumes an external plan and frozen delivery. It
does not generate art, run PixelEngine, fit poses, change clocks or infer anatomy.
Use it for reviewable alpha alternatives and deliberate native-coordinate pencil
repairs after examining the whole actor and all adjacent/wrap pairs.

The source currently must contain one fused `body` layer, `project.json` and
ordered `frames/0000.png`, `frames/0001.png`, etc. Source project/file and every
frame PNG are pinned. The original project and PNGs are copied byte-for-byte;
the existing constructor independently reconstructs their visible pixels.

```bash
.venv/bin/python research/pixelengine-imagen/tools/author-pixel-candidates.py \
  --source /absolute/external/frozen-delivery \
  --plan /absolute/external/literal-plan.json \
  --output /absolute/external/fresh-candidates \
  --native-editor /absolute/path/to/existing/libresprite
```

The native editor flag is optional. When supplied, actual save/reopen, complete
project reimport, PNG-sheet RGBA and clock equality are required. Without it,
the recipe makes no claim of external application acceptance.

An external plan has this shape. Replace placeholder hashes and IDs with those
of the actual frozen source; keep case-specific art and masks outside Git.

```json
{
  "schema": "literal-pixel-candidates/v1",
  "source_project_file_sha256": "SHA256_OF_PROJECT_BYTES",
  "source_project_canonical_sha256": "TOOLKIT_PROJECT_HASH",
  "source_frames_sha256": ["SHA256_FRAME_0", "SHA256_FRAME_1"],
  "animation": "walk",
  "candidates": [{
    "id": "conservative-edge-and-pencil",
    "reason": "State the observed defect and bounded intended change",
    "alpha_policy": {"mode": "cutoff", "floor": 32},
    "pencil_steps": [{
      "frame_id": "pose-00",
      "reason": "State why these actual source coordinates need pencil work",
      "pixels": [[12, 18, [80, 40, 24, 255]]]
    }]
  }]
}
```

`source_project_canonical_sha256` comes from the construction toolkit's
`project_hash(load_project(text))`; it is distinct from the file SHA-256. Each
`pixels` entry is `[x, y, [r, g, b, a]]` in the full original canvas. Coordinates
must be unique within a step. Repeated steps are deliberately ordered. Local
paint is literal, and any new costume or anatomy paint must be labeled as such
in its reason rather than described as recovered source information.

Supported alpha policies:

| Policy | Operation |
| --- | --- |
| `{"mode":"cutoff","floor":32}` | Set alpha below32 to transparent black; retain all other RGBA |
| `{"mode":"binary","threshold":128}` | Below128 transparent black; retain RGB and make the rest opaque |
| `{"mode":"coverage","floor":96,"opaque_at":224}` | Below96 transparent black; retain96–223 RGBA; make224–255 opaque |

Thresholds are explicit alternatives to inspect on light/gray/dark mattes, not
a universally correct sprite-import policy. Binary alpha may thicken weak edge
samples or cut finer contours. Source RGB is retained for alpha-only changes.

For each candidate, the runner creates masked toolkit paint/palette-add
transactions with an exact project precondition, actual before/after RGBA,
receipts and a replayable journal. It verifies exact replay/undo/redo, unchanged
canvas/pivots/frame order/ticks/events/landmarks/provenance and no composited
change outside the union of recorded masks. It rechecks source hashes at the
end. Shared source cels deliberately affect all frames that reference them.

Delivery uses the existing project exporter, exact rational APNG encoder and
ASE adapter. `control/` retains the original pixels and clock beside the
candidates. Every directory contains full-canvas PNGs, an atlas, editable JSON,
ASE plus metadata sidecar, a rational clock manifest, APNG and receipts. Adjacent
`*-journal/` directories contain the exact operations and verification evidence;
`RESULTS.json` pins outputs and the source. Godot project files emitted by the
exporter are inputs for later engine verification; their presence is not an
engine-test result.

Native-scale complete-character review, all predecessor/current pairs and loop
wrap, material/attachment continuity, secondary motion and actual timed human
playback remain separate acceptance gates. Passing this recipe cannot establish
parity with a stronger animation. Preserve unresolved pose/occlusion issues and
rejected alternatives in the handoff.
