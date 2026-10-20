# Supplied-art geometry, export and review

These modules implement a **local deterministic subset**, not PixelLab's private body authoring, model, hidden-surface, frame-ranking or wrapper algorithms. They require supplied pixel parts and explicit poses. F02/F10 tests use asymmetric mechanical markers; artistic quality is unreviewed. Source authority remains the versioned reconstruction contracts and source reviews, including the differing Lua/Godot coordinate and depth paths. This module does not merge those projections into an invented common rig.

## Python integration

```python
from sprite_workbench.scene import render_scene
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.review import review_sequence

sequence_id = render_scene(store, scene)
report = export_sequence(store, sequence_id, output_directory,
    formats=['png', 'manifest', 'sheet', 'apng', 'gif', 'editable', 'godot', 'review'])
report = review_sequence(store, sequence_id, review_directory)
same_id = import_editable(other_store, output_directory + '/editable')
```

No function publishes a named head. Call `Store.set_head` only after admission/validation, using the caller's expected previous head. Failed scene guards may leave immutable orphan layer candidates, but never replace a publication. Outputs are staged and renamed only into absent/empty nonsymlink directories. Existing artifacts are refused and preserved. Reports distinguish written formats from unsupported formats; a requested unsupported GIF/APNG is **not** a passed export.

## Scene v1 schema

```json
{
  "canvas": [64,64], "name": "supplied-pose", "loop": false, "play_count": 1,
  "require_source_coverage": true, "allow_source_overlap": false,
  "clip_policy": "report",
  "nodes": [
    {"id":"root","position":[3,4]},
    {"id":"arm","parent":"root","raster":"<RGBA artifact ID>",
     "mask":"<RGBA binary ownership-mask ID>",
     "ownership":{"source":"<source RGBA artifact ID>","origin":[0,0]},
     "anchor":[12.5,17.5],"position":[0,0],"rotation_degrees":0,
     "scale":[1,1],"visible":true,"z":2,"composite":"source_over"}
  ],
  "frames":[
    {"duration":[1,12],"pivot":[32,48],"direction":"south",
     "nodes":{"arm":{"rotation_degrees":15}}}
  ]
}
```

Artifact IDs are complete Store content identities, never filesystem paths. A raster node requires a same-sized mask whose alpha is **0 or255**. Mask RGB is irrelevant. Art alpha, including partial alpha and nonzero hidden RGB, is separate. Group nodes omit raster/mask. Unknown fields, duplicate IDs, missing parents, cycles and missing-mask/raster branches fail explicitly. Per-frame overrides can change raster/mask/ownership, position/anchor/rotation/scale/visibility/z/composite; parent identity remains fixed. Every frame requires an integer rational duration in seconds; poses are discrete, with no undocumented interpolation/easing or anatomy synthesis.

`ownership.source` binds a full source raster and `origin` binds the source crop in integer pixels. The complete raster rectangle, including hidden RGB outside the owned mask, must match that source crop. Source-pixel ownership is disjoint across nodes by default, even when a node is hidden. `allow_source_overlap=true` is an explicit local duplication policy, not an automatic repair. With coverage required, every raster node must bind a source and the union of its source-space masks must cover all **visible** source pixels. Hidden RGB can be owned explicitly and remains in editable inputs.

Coordinate policy is local and explicit: x right/y down, positive degrees clockwise, pixel centers at `(x+.5,y+.5)`. Local matrix is `T(position) T(anchor) R(rotation) S(scale) T(-anchor)`; world matrix is `parent_world × local`. Negative scale mirrors. Rasters sample inverse-mapped output centers by source cell floor (exact ties toward the positive source axis). Cardinal coefficients snap within1e-12; source-cell boundaries snap within1e-10 to avoid numerical epsilon artifacts. No per-frame recentering occurs. Noncardinal nearest sampling can lose or duplicate source cells; the oblique test intentionally witnesses this aliasing, not an aesthetic success.

Visibility is inherited; z is a **global integer draw order** with node-list order breaking ties, not inherited parent depth. `source_over` uses straight RGBA with nearest-integer rounding for partial-alpha mixtures. Opaque source and source over a zero-alpha destination copy exact RGBA; source-alpha0 over nonzero-alpha destination leaves destination unchanged. At an empty destination, an owned alpha0 source copies its hidden RGB. `replace` copies all owned RGBA, including alpha0 clears. These are local policies, not inferred vendor paint semantics.

Canvas clipping does not alter source artifacts. Each layer records inverse sample support and the count of forward transformed owned source **centers** outside the canvas. That center count is a geometric diagnostic, not a count of all rasterized edge loss. `clip_policy=reject` makes any such center a validation failure; default `report` allows bounded clipping with retained audit data. Numerical composition is bounded (world coefficients<=1e9, minimum singular value1e-8, condition<=1e8). Canvas/frame/work budgets are enforced.

Optional `guards` has `reference_sequence`, `frozen_frames:[zero_based_indices]`, `protected:[{"frame":i,"mask":id}]` and `palette_reference:RGBA_ID`. Reference frame count/canvas must match. Frozen and protected comparisons are full RGBA, including hidden RGB. Masks have binary alpha. Palette checks compare visible RGB sets against the reference's visible RGB; they do not award artistic acceptance. Guards are local admission rules, not a claim that PixelLab ignored its own failed candidate checks.

The sequence metadata binds `scene_id`. Its immutable `kind=layered-scene` document retains the original scene, source IDs, per-frame input layer IDs/masks, world matrices, transformed layer/mask IDs, visibility/order and sampling diagnostics. `editable/` carries the whole content-addressed closure; import verifies hashes, dimensions/timeline and closure inventory. Missing anatomy/occluded paint is not inferred.

## Clocks, formats and limits

All ordered entries and held duplicates remain in `frames/`, sheet cells and rational manifest. Duration is `[numerator,denominator]` seconds; starts/ends are exact accumulated fractions. `play_count=0` means infinite,1 one-shot, N positive total plays; `loop` is true **only** for infinite playback. A finite animation does not become an infinite SpriteFrames loop. `total` is one-cycle duration, `play_total` is the complete finite duration or null for infinite.

PNG and sheet exports preserve exact decoded RGBA, including hidden RGB. Sheets use fixed full-canvas cells, no trim/recenter, transparent-zero padding, zero offsets and original per-frame pivots. Rectangles use x/y/width/height pixels and ordered indices are zero-based. PNGs and manifest are always authoritative and are written even if preview containers are unsupported.

APNG uses full-frame SOURCE blend/NONE disposal, every supplied entry, exact unsigned16-bit rational hold fields and the source total-play count. There is no separate poster/default image: the first PNG image is animation frame0. A rational field overflow is refused, not silently rounded.

GIF preserves every entry using a shared palette with <=255 visible RGB colors plus transparent index0. Partial alpha and excess colors are refused. Hidden RGB is unrepresentable. Holds round to nearest centisecond (ties up; minimum1) and every individual/cumulative error is reported. Finite GIF repeats equal `play_count-1`; one-shot omits the loop extension, infinite encodes0. Too many repeats/oversized holds are refused. Palette preparation or partial-alpha flattening must be a separately declared operation. The Pillow GIF framing helper is exercised by independent Pillow decode tests; no universal decoder/browser behavior is promised.

Godot export is a standalone local project with SpriteFrames/AtlasTexture resource, fixed sheet, rational JSON manifest and Node2D driver. Speed1 and float-second frame weights avoid double-dividing FPS. Texture alpha-border repair, premultiplication and mipmaps are disabled in importer defaults; nearest CanvasItem filtering is explicit. The driver applies per-frame `offset=-pivot`, `centered=false`, handles finite play counts through completion/restart, and exposes `restart()` to clear completion state. Exact rational storage remains authoritative; Godot holds are floating-point. There is no inferred gameplay hit/collision event.

Review HTML includes every ordered frame, every adjacent pair and the final→first loop/replay seam. One performance timestamp maps through the same rational timeline; it does not use a guessed8fps clock. Finite plays hold the final pose, duplicates retain their durations, and integer1x/2x/4x display scales are explicit. Exact/visible/alpha/hidden-only differences, alpha support and palette counts are diagnostics. A generated player/contact packet is not proof of continuous viewing or9/10 motion. JavaScript uses an eight-ULP boundary tolerance to avoid modulo roundoff at repeated-cycle boundaries; its performance clock is floating-point, while the stored timeline is exact. The generated program is tested in an inert Node VM for finite-cycle/end/seek selection, not claimed to have been visually viewed in a browser. No numeric aesthetic score is assigned.

## Verification

```bash
mkdir -p .test-tmp
python3 -m pytest -q tests/test_geometry_flows.py --basetemp .test-tmp/geometry
```

F02 traverses supplied-art→owned scene→guarded immutable sequence→publication→editable export→fresh-store import→identical rerender. Goldens enumerate asymmetric source destinations independently. Discriminators include hidden RGB source mismatch, ownership overlap, graph cycle/missing parent, partial ownership alpha, missing-pose request, mirror/cardinal/oblique behavior, inherited visibility, clipping report/reject, frozen/protected/palette violations and partial-alpha compositing.

F10 traverses exact frames→sheet/manifest→APNG/GIF decode→review→Godot import→SpriteFrames save/reload→real AnimatedSprite2D clock/restart/held pose. Three fresh headless cases exercise one-shot/infinite/finite3 plays. Actual imported AtlasTexture crops match complete expected RGBA, including hidden RGB. Engine timing uses a declared30ms-per-cycle tolerance and retains raw event timestamps. This is texture readback and actual headless scheduling, **not GPU raster output, browser viewing, target PixelLab runtime, neural-model parity or artistic acceptance**. If Godot is unavailable the engine cases explicitly skip; no verification is invented.
