# Source-owned component track experiment

`compose-owned-track.py` tests one explicitly masked source component attached
to manually declared per-frame anchors. It retains the entire original motion
and an exact control. It can also use a separately pinned donor of the same
stage/clock, retaining that complete donor as another control.

This is an authored component rig. A stable drawing reused through a fixed
view can reduce facial/hair variation, but can also look stiff or mismatch the
body's palette/shading. It does not recover hidden anatomy or prove that one
view suits every original pose. Inspect the source first and retain failures.

```bash
.venv/bin/python research/pixelengine-imagen/tools/compose-owned-track.py \
  --source /absolute/external/source-clip \
  --plan /absolute/external/ownership-plan.json \
  --output /absolute/external/fresh-component-test \
  --native-editor /absolute/path/to/existing/libresprite
```

Add `--donor /absolute/external/donor-clip` only with the plan's matching
`external_donor` pins. This flag makes no model/provider request.

The external plan contains artwork-specific masks and anchor choices:

```json
{
  "schema": "owned-source-component-track/v1",
  "source_project_file_sha256": "SOURCE_PROJECT_FILE_HASH",
  "animation": "walk",
  "component": "head",
  "master_frame_index": 0,
  "master_anchor": [40, 28],
  "forbid_body_occlusion": true,
  "frames": [{
    "frame_id": "pose-00",
    "png_sha256": "SOURCE_FRAME_HASH",
    "attachment_anchor": [40, 28],
    "owner_mask": [[34, 9], [35, 9]],
    "underpaint": [],
    "reason": "Explain this manually chosen owner and attachment"
  }]
}
```

Provide every frame in the animation's original order and every owned visible
coordinate. The tiny example mask is schematic. Source files use the existing
delivery layout: `project.json` and `frames/0000.png`, etc. Masks must follow
the actual component, excluding collar/scarf/neck regions that remain body.
Avoid rectangular copy/paste across the attachment.

For a separately supplied donor, the plan additionally includes:

```json
{
  "external_donor": {
    "project_file_sha256": "DONOR_PROJECT_FILE_HASH",
    "frames_sha256": ["DONOR_FRAME_HASH"],
    "frame_index": 0,
    "owner_layer_id": "owner",
    "owner_mask": [[34, 9], [35, 9]],
    "anchor": [40, 28]
  }
}
```

All donor frames must be pinned. Donor and target canvas/pivots/animation clock
must match. The full donor is exported unchanged as `donor-control/`.
When `owner_layer_id` is declared, the mask must exactly equal that layer's
visible cel raster, and every sampled donor pixel must equal the owner's
unoccluded composite paint. This prevents a stale hand mask from silently
sampling another component. Without the optional field, the explicit mask
remains the authority for fused donor artwork.

The runner first uses the existing constructor to split each original frame
into a locked body, empty join-underpaint layer and explicit component owner.
The complete composite must reproduce the source exactly. Guarded candidate
transactions then erase the old owner and place literal master source texels
at `destination_anchor - master_anchor`. Only integer translation is supported;
there is no rotation, scale, automatic fitting or whole-pose recentering.

If old ownership exposes a small join hole, declare each authored underpaint
pixel as `{"at":[x,y],"source_pixel":[frame_index,sx,sy],"reason":"..."}`.
It must lie inside old ownership, outside the replacement owner. This is new
paint sampled from a declared source-color witness, not recovered underpaint.
Former outer-silhouette pixels may deliberately expose background; record and
review them instead of treating every removal as an internal hole.

Each frame records old/target/union masks, exact source-texel witnesses,
anchors/translation, exposed-background coordinates, source body pixels
occluded by the new owner and underpaint declarations. Body cel arrays remain
unchanged. An unchanged body layer does **not** imply every original body pixel
remains visible: inspect the occlusion list, especially at the collar/scarf.
Set `forbid_body_occlusion` to true when every protected body pixel must remain
visible. The runner rejects overlap before applying the component transaction.
Do not broaden old ownership merely to pass this guard: inspect and rebase the
actual visible head, hair fringe, jaw outline and collar boundaries separately
for every new raster grid. A donor mask may stay exact while target ownership
and attachment anchors need fresh measurement.

For a native-grid body/crisp-head experiment, keep the new grid's complete
control, define target masks from that grid, and sample the donor's existing
owned head layer. Measure anchors at the first neck-shadow baseline after the
jaw and document any variation. Inspect all exposed-background coordinates;
outer fringe removals differ from join holes that need literal underpaint.
Freeze case-specific masks, colors, anchor witnesses and source hashes in the
external artifact plan. Keep those private artwork coordinates outside Git.

The recipe checks source and donor pins, exact decomposition, outside-mask
pixel preservation, locked body/cloth cel preservation, exact frame/clock/pivot
metadata, and complete journal replay/undo/redo. Export uses the existing
project/APNG/ASE tooling. Optional actual LibreSprite save/reopen verifies the
entire imported project and raster sheet. Engine files emitted by the exporter
are inputs for later tests, not evidence of engine acceptance.

Review complete native-scale actors first, then every predecessor/current pair
and wrap. Inspect attachment joins, unchanged scarf follow-through, head bob,
identity/material consistency, stiffness from reuse and donor style mismatch.
Exact mechanics and clearer faces do not establish a higher art score or human
timed-motion acceptance.
