# Owned head repair of retained painted bridges

`replace-bridge-heads.py` tests whether a stable source-owned head salvages two
already painted full-body bridge drawings. No image/model/provider call is made.
It is deliberately bounded to one eight-key8Hz loop, bridge2.5 after key2 and
bridge3.5 after key3, with source layers `body`, `join-underpaint`, `owner`.

```bash
.venv/bin/python research/pixelengine-imagen/tools/replace-bridge-heads.py \
  --project /absolute/external/layered-source/project.json \
  --bridges /absolute/external/retained-painted-bridges \
  --plan /absolute/external/literal-head-plan.json \
  --output /absolute/external/fresh-test \
  --native-editor /absolute/path/to/existing/libresprite
```

The external plan contains source/art-specific hashes, ownership and anchors:

```json
{
  "schema": "painted-bridge-head-test/v1",
  "source_project_file_sha256": "SOURCE_PROJECT_FILE_HASH",
  "donor_frame_id": "pose-00",
  "donor_anchor": [40, 28],
  "bridges": [{
    "after_key": 2,
    "file": "00.png",
    "file_sha256": "BRIDGE_FILE_HASH",
    "frame_id": "bridge-2p5",
    "anchor": [40, 28],
    "owner_mask": [[34, 8], [35, 8]],
    "underpaint": [],
    "reason": "Explain the actual visible head owner and declared join"
  }]
}
```

The abbreviated mask is schematic. Supply both bridge entries in order and
every owned visible head/neck-shadow pixel. Old owner masks follow actual
hair/face boundaries; never use a rectangle across scarf or torso. The new
head comes from the source's existing `owner` cel, preserving its exact RGBA
and alpha, with integer translation by the declared attachment anchor only.
There is no head resizing, hidden-paint recovery or whole-pose registration.

For an exposed join pixel, declare
`{"at":[x,y],"source_bridge_pixel":[sx,sy],"reason":"..."}` under that bridge.
The target must lie inside the removed old owner and outside the new head.
It becomes explicitly authored underpaint sampled from that bridge, not a
claim of recovered anatomy or costume. A replacement jaw can also cover a
few original collar pixels; the runner records every such coordinate and
does not claim that all original bridge pixels remain visible.

The existing constructor builds an exact before control from the retained
bridge bodies and their removed head owners. Original source keys retain
their original layer images. The ten-frame clock is16Hz with tick holds
`[2,2,1,1,1,1,2,2,2,2]`: source keys2 and3 split their original125ms exposure
into62.5ms source plus62.5ms bridge. All eight source-key onsets remain at
their original eighth-second boundaries; the complete cycle remains1second.

Guarded toolkit transactions edit only the two new owned-head cels and any
declared join underpaint. Body cels stay locked. Verification requires exact
source head pixels at their anchors, outside-mask preservation, every source
key/onset unchanged, and exact journal replay/undo/redo. Output includes the
original control, painted-before sequence, repaired sequence, layered editable
JSON/ASE/sidecars, PNG/atlas/APNG, masks, source maps and receipts. Optional
actual LibreSprite save/reopen checks the full project and rendered frame
sheet; rational source clocks remain authoritative over tool milliseconds.

Inspect native actors,2x/4x neighboring frames, every adjacency and wrap. A
clearer face can leave torso/cuff/buckle/boot shading or shape changes intact.
Keep those generated-body differences visible in before/after controls; head
pixel fidelity alone cannot establish animation parity, better motion or a
new art score. Record whether actual timed motion was perceived.
