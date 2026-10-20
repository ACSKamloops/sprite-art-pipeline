# Lyra southeast03/04 contact repair — frozen candidate

The root-inspected exact candidate cels are `candidate/03.png` (`3aa39d61d900e563555f2e6dfd99bf24478ac2535e185ca59ba5dd903664de32`) and `candidate/04.png` (`af8109e3810036d90f476658bc52c2f5cf7ef8011fd4c6409b86dbae17d83eac`). No pixels changed after preview approval. This is a candidate for independent review, with no inherited quality score.

Only03/04 change. Each original cel's full upper body, white hair, green/gold hem and whole visible gloves remain exact. Other six PNGs remain byte-identical, including05's existing overlap. No southeast endpoint, rear view or other hero was changed. The canonical source cycle was read only.

## Authored pose and visible paint

04 uses actual06's useful screen-left support leg as the newly low/forward opposite contact. Its charcoal thigh and cuff move continuously into the visible whole leather boot; distal boot rows94 onward translate(+4,+4). The upper cuff shares the explicit proximal leg mesh rather than being forced to a rigid identical front boot. Actual06's distinct bent screen-right leg/boot shifts(-3,+2) into a higher rear position, preserving that toe projection.

03 bridges actual02 into new04. The source02 screen-left leg descends; its whole visible boot moves approximately(+3,+6), with a bounded forefoot shear opening the toe by at most2 native pixels. The source02 first-support boot retreats with distal translation(-2,-5), joined by its mapped charcoal knee/cuff. No toe reflection, whole-pose fitting or recentering is applied. Different real same-view boot projections remain distinct.

These are authored projected support/swing roles, not verified anatomical left/right. `POSE-ROLES.json` binds declared hip/knee/cuff/heel/toe landmarks to actual source-map witnesses; an occluded/unsampled source anchor remains labeled unavailable. `maps/control-meshes.json` stores all source/target controls and fixed nonfolded triangles. `source-parts/` holds actual visible owners and mapped paint. Visible cutouts are not complete hidden anatomy, and no missing rig or hidden limb surface is recovered.

Each repaired cel has138 bounded actual02 charcoal hip-underpaint pixels behind the mapped legs. Five partial-alpha joins in03 use declared integer source-over to retain real underlying paint;04 has no such overlap. Literal source coordinates and layer order are retained. Transparent donor space never clears valid underpaint. Original lower paint is cleared before placing the new parts, and the exact original upper/hem/gloves overlay last.

The boot inventory is used only for source witness/status. `inputs/VISIBLE-DONOR-STATUS.json` retains the relevant LyraSE records, source hashes, limitations and local witness copies. The00 screen-left donor is explicitly partial-reference-only and is not used as a new complete leg. Source-exact cutouts do not establish hidden anatomical completeness, persistent limb identity or drawing quality.

## Inspect actual chronology

`proof/02-03-04-05-06-native.png`, its3x inspection board and84px proxy show the whole contact exchange. `proof/full8-native.png` and `full8-game.png` show every cel and loop context. Contrasting dark/light/green/purple grounds are retained. `proof/index.html` links native128 and84px normal-speed focused/full-cycle videos. Every phase holds9/160s; the8-frame cycle is9/20s. The focused excerpt's06→02 reset is not treated as walk-loop evidence. MP4 is review transport; PNG RGBA remains authoritative. Actual160fps stream counts and hashes are in `proof/MEDIA-RECEIPT.json`.

## Rebuild without generation

Requires Python3, Pillow and NumPy; toolkit modules are retained locally. Choose a fresh nonexistent output folder:

```bash
python3 scripts/rebuild.py --output /absolute/path/to/fresh-replay
```

This independently reconstructs per-leg layers from actual retained source texels, composes hips/legs with a scalar implementation of the declared alpha rule, verifies all8 source-map PNG bytes, and independently replays the actual guarded editor journal. Completed `verification/full-replay-v1/` and `REPLAY-RECEIPT.json` prove all8 RGBA and PNG bytes, exact other-six/upper/hem/glove preservation, and two-step undo/redo.

`projects/initial.json` contains the original eight-cel cycle. Two actual guarded transactions import03 then04 through each explicit lower owner, excluding the original upper/hem/opaque gloves. Project and cel preconditions are retained. A deliberately changed outside-mask candidate and stale precondition were actually rejected atomically. `projects/final.json` and `journal.json` are editable complete raster-cel artifacts; separate source parts/maps retain the construction. No external GUI editor, engine renderer or physical-contact behavior was tested.

There were zero model calls. `INTAKE.json`, `SOURCE-INTEGRITY-RECEIPT.json`, `CANDIDATE-RECEIPT.json`, `PACKAGE-STATUS.json`, `TIMING.json` and `SHA256SUMS` bind the exact source, authored geometry, ownership, timing and scope.
