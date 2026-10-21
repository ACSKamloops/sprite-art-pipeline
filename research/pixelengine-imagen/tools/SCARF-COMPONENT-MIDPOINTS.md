# Independent scarf-tail midpoint experiment

`compose-tail-midpoints.py` takes one layered eight-key,8Hz looping project
and an external literal ownership/paint plan. It keeps the original body keys
at8Hz and introduces tail-only half-step states at16Hz. Total time remains one
second. These narrow input bounds reject retiming/events that this experiment
does not implement.

```bash
.venv/bin/python research/pixelengine-imagen/tools/compose-tail-midpoints.py \
  --project /absolute/external/layered-source/project.json \
  --plan /absolute/external/literal-tail-plan.json \
  --output /absolute/external/fresh-scarf-experiment \
  --native-editor /absolute/path/to/existing/libresprite
```

The plan is external because its masks and source maps contain artwork-specific
information. It has `schema: "owned-tail-midpoints/v1"`, a source project file
SHA-256, `tail_source_layer`, eight `keys` and a `midpoints` list. Each key pins
its rendered RGBA SHA-256 and supplies a unique explicit `owner_mask` of `[x,y]`
coordinates. Own only visible rear flap paint and its outline. Keep the neck
bib, hair/face and shoulder occlusion seam in their original foreground layers.

Every midpoint entry contains:

```json
{
  "state": 5,
  "attachment": {
    "root_anchor": [32, 30],
    "layer_order": "behind the original shoulder"
  },
  "reason": "Explain the newly authored cloth contour and source donors",
  "source_texel_map": [[26, 32, 3, 24, 33]]
}
```

Only odd states0–15 may be edited; state5 is halfway between original keys2
and3. Every source map entry is `[target_x,target_y,source_key,source_x,source_y]`.
Donor pixels must belong to that source's explicitly owned visible tail.
Targets are literal authored paint, not recovered hidden cloth. Source color
origin does not prove the new outline, fold or volume. If geometry was used
to propose the map, the frozen integer map is the exact replay authority.

The runner splits the visible tail from its original source layer, places it
behind the untouched foreground layers and requires exact source reassembly.
This is a visible-paint decomposition; no missing body/underpaint is inferred.
It creates a16-state duplicate-exposure control before editing the odd tail
cels with guarded toolkit transactions. Tail cels are unique even when their
source pixels repeat, so changing one midpoint cannot change its even key.
Original foreground body/head/bib cels stay shared at8Hz and locked.

Changes must stay inside old/new tail-mask unions. Every original even key
must reproduce exactly, and all visible non-tail original pixels must remain
exact. New cloth is occluded by the unchanged foreground layers, including
the shoulder and neck bib. Per-state witnesses record the actual hidden tail
pixels; an anchor declaration alone does not verify a visually good join.

The existing `union_component_clocks.py` unions the pinned body8Hz and tail16Hz
tracks. Every rational boundary, source position and one-second period is
verified. A16-state clock does not mean16 new drawings: the result explicitly
counts actual changed visible midpoints and distinct tail rasters, including
hidden/duplicate exposures. No FPS-only motion-improvement claim follows.

Outputs retain the original eight-key control,16-state duplicate control,
candidate, layered editable JSON, ASE/sidecar, PNGs, atlas, exact APNG, input
project, construction spec, masks/source witnesses, journal and receipts.
The optional actual LibreSprite check compares each rendered frame with the
native horizontal sheet independently of the atlas's row layout. Native
millisecond quantization remains separate from authoritative rational holds.

Inspect complete actors at native scale, the isolated tail, all16 adjacent
pairs and15→0 wrap, then actual timed playback. Pay particular attention to
first reveal, fold/hem volume, attachment, shoulder occlusion, body-key catches
and disappearance. A thinner exposed strip can result from correct occlusion
while still looking bad in motion. Keep failed drawings and tooling evidence,
qualify actual viewing conditions, and assign no art score from these checks.
