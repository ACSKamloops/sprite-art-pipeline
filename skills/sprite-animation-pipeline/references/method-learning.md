# Original game behavior → authored sprite pipeline

Use when extraction must teach how a real game selects, constructs and animates
sprites. The toolchain is evidence collection; do not treat a decompile, atlas or
viewer as a complete behavior model.

## Build a causal case, then expand coverage

Freeze artifact hashes and a case tuple: actor, view, equipment, action/level,
status, target, map/start checkpoint and exact input sequence. Separate requested
action coverage, allocated table bindings, reachable branches, unique poses and
observed displayed ticks. Unknown names and unvisited branches remain unknown.

Use available REA operations directly for supported targets. If a loader rejects
the actual target format, retain its error and use an already available
format-aware disassembler/emulator adapter. Do not relabel host-emulator code as
game code or repeatedly repair configuration for an unsupported format.

Trace selector → script/control/waits → pose/part assembly → palette/effect
state → displayed frames → gameplay events/cleanup. Preserve each edge's type:
static instruction/data reference, executed watchpoint, correlated observation,
controlled intervention or unresolved. Nearby execution is not a causal call
graph. CPU register meanings vary by routine; only assign actor ownership where
the local calling contract establishes it. Report selective trace drops.

Capture consecutive source/video ticks and raw render state. A selected pose can
lead the displayed frame. Preserve palette flicker, object order, world/render
anchors, equipment/entity ownership and final cleanup. Independently reconstruct
raw pixels without importing the producer decoder. Reject shifted tick order,
holds, clocks, events, flips and unsupported ownership.

Use a minimal counterfactual in a derived artifact or controlled state/input,
keeping originals and all other conditions fixed. Predict the effect before
interpreting it. Confirm selection, displayed pixels and completion, plus an
unchanged control. One branch's delay formula does not prove all wait/status
paths. Unsupported commands and external callbacks remain resumable gaps.

For variable-width CPUs such as65816, bind entryM/X widths to actual processor
status where observed. A successful disassembler command does not prove correct
width, all bytes decoded or complete function boundaries. Report undecoded gaps
and exclude instructions extending outside the captured byte range.

## Transfer behavior into construction

Freeze references at intended scale and view. Additional views, occluded anatomy,
extreme deformation and transformed identities need new key poses or geometry.
A2D rig needs real separate parts and anchors; Blender needs an actual model/rig.
Do not ask an image generator for independent finished frames and assume identity
or temporal consistency. Use it for proposals, then redraw/fine-edit where needed.

Build body poses, equipment, root motion, projectiles/effects, palette state and
gameplay events as explicit components. Charge and status waits depend on state;
projectile return and death persistence are not fixed body-GIF holds. A single
HP transition proves an event, not a complete hit window. Restore neutral recovery
and test transitions, cancellation and cleanup in the intended engine.

Measure rendered contact throughout held frames, fractional time and wrap. A
passing IK target or pose boundary can conceal foot sliding as the root moves.
Report continuous physics, raster snapping and camera policy separately. Denser
frames may improve slipping while still failing the same threshold. Connected
alpha does not prove a convincing knee seam or material ownership.

## Automate and audit

Create a searchable frame index preserving selected state and displayed signatures
separately. Attach methods by trace source and tick; unknown actor ownership and
missing traces stay explicit. Methods×cases heatmaps show coverage, not causality.
Use bounded summaries and query by actor/action/state instead of loading giant
catalogs into model context.

The bundled `scripts/method_learning_queue.py` supports generic source-bound case
registration, atomic claims, finish and owner-token release. It checks evidence
paths/hashes and named purposes, not scientific truth. Require an adapter verifier
and an independent current review before accepting a causal conclusion. It is a
discovery queue; the existing leased animation_queue.py handles artwork stages.

```bash
python3 scripts/method_learning_queue.py --db /work/cases.sqlite register cases.json
python3 scripts/method_learning_queue.py --db /work/cases.sqlite claim --worker worker-a
python3 scripts/method_learning_queue.py --db /work/cases.sqlite status
```

Each registered case has `id` plus a frozen JSON brief. Finish requires the claim's
input fingerprint, `scope_status` observed_partial/verified_bounded/unresolved,
nonempty evidence and limits. Causal receipts name four evidence IDs matching
purposes static_analysis/executed_trace/controlled_intervention/displayed_frame_check.
Arbitrary booleans reject; correctly labelled but irrelevant evidence can still
pass provenance gating. Never autoapprove methods or artwork from queue acceptance.

The local worked case is `/home/astra/projects/sprite-construction-lab/learning/`:
one sword control-byte intervention changes5/5/5 displayed holds to10/5/5 under
identical input; independent review caught and corrected a65816M-width error.
The broader corpus has85 native routes/28123 observed video ticks, not a complete
game. The companion construction lab measures4/1/0pixel slipping for old raster,
dense raster and continuous rig respectively; both raster clips remain rejected
under their0.5pixel rule. Native controller timing and editor pause/resume repairs
have separate current tests. Use these as failure recipes, not universal counts,
styles, clock constants or production-art approval.
