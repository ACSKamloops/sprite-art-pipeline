# Copper Scout V2 — authored four-view candidate

`design.json` and `clips.json` are authoritative editable sources. There is no bootstrap/rebuild script that overwrites them. `rig.gd` extends the preserved side rig engine in `rig_side.gd`; front/back replace shapes, anchors, IK bend direction, depth-facing pose tracks and draw order. Left remains a mirror of the right view. All original durations/events remain intact.

Current final export: 96 bindings / 6000 held frames. The complete dense review is `../../qc/temporal/repaired96-review.md`, source-bound to manifest5543790d. Thrust guard recovery is repaired and approved for prototype use only; depth foreshortening and production polish remain open. Earlier candidate snapshots below remain historical evidence. Current actual world/cache and contact evidence is linked from `../HANDOFF.md`.

Run actual GPU review locally:

```
xvfb-run -a godot --path pilot/rigged-character-v2 --audio-driver Dummy --rendering-method gl_compatibility --script res://render_first.gd
```

`configure(design, clips)` and `pose(clip, normalized_phase, view)` retain the V1 API. One-shot phase1 is an endpoint; loops wrap. `visible_layers` selects actual named draw layers. Metadata exposes structured landmarks, reach errors, contacts, draw order and `surface_frames`.

Rigid paint uses `design.paint_layers[view][layer]` arrays of `{at:[x,y], color:palette_name, size:integer}`; each cell is clipped to its actual local material silhouette, conservatively excluded at other-material cutouts. Supported layers: torso (body origin/lean, cloth only), head (head origin/angle, hood only), shoulder_armor (front shoulder/lean), equipment (front hand/weapon angle, guard or panel). Left applies global mirror after identical local UV coordinates. `surface_frames` gives origin, angle, UV reflection and local masks. Deforming sleeve/trouser paint is unsupported; editable `details` seam paths follow their continuous strips.

The first GPU snapshots and source hashes live in `candidate-first/receipt.json`; those images are evidence for a candidate, not a quality score. New candidates must use a new output directory to preserve previous-frame comparisons.

## Persistent equipment contract

Default `configure` clears selection and renders clip-declared equipment **for inspection only**. Functional playback must call `set_equipment("none"|"sword"|"blaster")` as an explicit equip/stow action, then retain selection through locomotion and matching attacks. `can_play(clip)` and `pose` reject mismatches: slash/thrust/charge need sword; shoot needs blaster; two-hand cast needs none. No implicit equipment change occurs when an attack is requested. The controller owns action interruption/menu permission; changing gear is an explicit state change. `clear_equipment_selection()` returns to inspection mode. Metadata reports `declared_clip_equipment`, `effective_equipment`, `equipment_selection` and its mode.

Additional baked bindings are idle/walk/run/hurt/knockdown/recover with sword or blaster, each in four views (48). Base 48 bindings are inspection clips; they do not imply every pair is a valid gameplay transition. Expected live transitions keep the selected sword/blaster across movement/action/recovery; casting requires explicit stow. Original timing/event tracks are unchanged.

Front/back locomotion uses orthographic planar XY: world root moves vertically ±8px/walk or ±12px/run cycle; planted local foot Y counters it. Metadata declares `contact_basis: planar_xy` and the view-dependent projection. There is no perspective scale change and no universal opaque row169 foot gate in those moving views. Actual world-raster contact is independently checked by the consumer. Standing knockdown/recovery use the action ground boundary170; authored scarf folding and palm targets prevent penetration.

New review renders use `--script res://render_candidate.gd -- UNIQUE_OUTPUT_NAME`; existing evidence directories are rejected. The sampled GIFs are abbreviated phase reviews, not the full per-tick playback that the exporter/reviewer must inspect.
