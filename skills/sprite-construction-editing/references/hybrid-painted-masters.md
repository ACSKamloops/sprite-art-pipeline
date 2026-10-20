# Painted masters, articulated bridges and replacement poses

Use this route when a video provider is unavailable and static image generation, manual raster work and a2D rig are being compared. It is an alternative construction method, not evidence of a vendor's private implementation. A high-quality still is an art input, not an animation approval.

## Freeze the drawing system first

Keep appearance, actual game scale, camera/view, costume construction, material palette, collar/hip/cuff anchors and paint source hashes explicit. Distinguish three assets:

- A visible source cut, which contains no hidden anatomy.
- A complete articulating master with concealed overlaps and a real hinge.
- A replacement drawing for a changed projection, such as a frontal coat becoming a side/back coat.

Do not rotate one frontal torso to represent a turn. Conversely, replacing the torso with a differently built coat can create a worse animation even when the extreme pose is individually better. Validate neutral, guard, intermediate turn, strike and recovery together before expanding an action library. Treat a newly built neutral as a separate design if it differs from the accepted character; matching first/last candidate frames does not establish a match to the approved ready.

Normalize static masters once at design scale, then register actual anatomical openings. Keep raw generations and literal prompts/references. This differs from independently fitting or recentering each exported animation frame. Historical video poses can be useful explicit guides; disclose that dependency rather than calling the resulting route motion discovery without references.

## Rig and edit deliberately

1. Make ownership masks at native resolution. Inspect dark metal edges, glove highlights and cloth separately. Colour thresholds confused all three in the demonstrated test. Explicit row spans or hand-painted masks permit precise correction; a coarse polygon may retain glove paint on the coat or move a blue coat flap with an arm.
2. Paint newly exposed biceps, cloth and joint overlaps. Save an exact before/after coordinate journal with source palette/donor coordinates. Do not fill missing anatomy through an arbitrary whole-body warp.
3. Calibrate the actual elbow and wrist/cuff. A proxy placed inside the fist changed forearm scale and glove proportions. Keep a closed fist rigid as a separate part when the forearm stretches; add hand replacement drawings when the required projection changes.
4. Preserve transverse limb width. For opposite bone orientations, linear interpolation of elbow/wrist positions can collapse the bone through zero length. Interpolate angle and length separately, or author a better joint path. Joint math does not prove believable motion.
5. Use replacement visibility/order keys for genuine perspective changes. Inspect the adjacent switches for shoulder mass, trim thickness, coat length, wrist positions and silhouette. An intermediate bent-elbow pose serves a different purpose from compressing a straight arm.
6. Bake into a fixed stage using an explicit sampling convention, retain master/affine/visibility/order controls, and inspect every resulting pose. Inverse nearest sampling preserves source texels but can create serrations and isolated fragments after rotation.
7. Make downstream pixel repairs on the baked cels when needed. Freeze the parent layer hashes, use literal changed coordinates and before/after RGBA, verify undo/replay and outside-region equality, and keep the override separate from upstream rig edits. Removing detached flecks does not repair a bad silhouette or missing pose.

## Replay contract

`scripts/replay_affine_layers.py INPUT_FOLDER FRESH_OUTPUT_FOLDER` independently rerenders a frozen affine rig. It requires Python3, NumPy and Pillow. Input files:

- `manifest.json`: `canvas:[w,h]`, ordered `frames` with relative `file` and `sha256`.
- `MASTER-BAKE-PROOF.json`: ordered `draw_order` and `masters` mapping layer ids to PNG SHA256s.
- `masters/<layer>.png`: full-stage RGBA masters, all the declared canvas size.
- `CONTROLS.json`: one record per frame with `layer_affines[layer].A` (2x2), `.b` (2-vector), and optional `active_layers`.
- Existing `layers/000/<layer>.png` and final frame PNGs to compare against.

The convention is `destination=A*source+b`; inverse nearest uses `floor(source+.5)` and transparent out-of-stage samples. The helper imports no producer code and checks every layer and composite. It reproduces retained paint/controls, not a stochastic image request or physical/anatomical truth. A downstream cel-edited clip must replay its parent rig and then its edit journal; do not claim final edited pixels are unmodified master samples.

For the named humanoid pairs `near_forearm:near_hand` and `far_forearm:far_hand`, run `scripts/check_raster_joins.py INPUT_FOLDER FRESH_REPORT.json`. It checks actual 8-neighbour alpha contact and records visible top-layer witnesses on every articulated pose. Whole replacement drawings are outside that separate-part test. Adapt the pair names for a different rig. This caught an actual pose7 wrist gap despite coincident joint targets; two source-owned cuff-underlap pixels repaired it. The negative case returns exit1. The repaired case checked36 joints, minimum4 adjacent hand pixels in layer rasters and minimum1 visible contact pixel, with zero failures. Those counts are this fixture's evidence, not generic quality thresholds. Visible adjacency still does not prove good anatomy.

Snapshot producing code when freezing a candidate. A shared authoring filename advanced during the experiment while the old source bytes were retained under `history/`; an adversarial review correctly found the current filename no longer matched the old hash. `BUILD-CODE-INDEX.json` resolves the recorded producer hashes to immutable content-addressed files. A saved hash without a retrievable source version is an incomplete reproducibility pointer.

Resolve the declared parent path and compare its actual hash. A parameterized edge-edit helper retained two old path strings while recording new parent hashes; the negative lineage check rejected it. The corrected successor preserved all frame/layer/APNG bytes and rational timing, so its visual assessment could carry forward only after independent equality and corrected-lineage verification. Keep that metadata repair separate from any claim of improved art.

## Require separate evidence

Verify source palette/donor claims, guarded master edits, affine replay, rational timing, actual lossless animation decode, real external sprite-editor save/reopen, browser playback and actual engine pixels. Independently inspect all affected frames/pairs at native/2x over contrasting backgrounds and timed motion. Automated clock/canvas checks and timed browser captures do not equal a human's uninterrupted motion judgment.

For pixel-sensitive A/B playback, prefer the verified lossless APNG when a combined lossy preview fails the source-template transition check. In the demonstrated side-by-side, the default MP4 did fail that check; it was quarantined rather than approved by lowering the fidelity gate. The separate action MP4s passed. The comparison APNG preserves all96 frames and1/24s delays, and five actual browser image captures matched source RGB exactly. Record any screenshot bounding-box crop explicitly; no rescaling is needed to exclude an extra margin row.

The source-bound RPG experiment is `/home/astra/projects/rpg-hero-animation/work/hybrid-rig-v1/README.md`. A cutout pickup received4.8/10; completed-part punch5.8; source-painted full arm6.8; calibrated separate fist and body load7.1. A stronger side-strike replacement reduced the full-clip score to6.4 because construction changed at switches. These are local independent judgments, not transferable skill scores. Later coherent-body and per-cel repairs have their own frozen reviews in that folder. No9/10 or H3 parity follows from those tests. Three static ImageGen calls and zero new H3 calls were made for that experiment; existing H3 poses supplied disclosed motion references. This was the available OpenAI ImageGen tool, not Google Imagen.

Official mechanism references: [Spine meshes](https://esotericsoftware.com/spine-meshes), [attachment keys](https://esotericsoftware.com/spine-keys), [Godot2D skeletons](https://docs.godotengine.org/en/stable/tutorials/animation/2d_skeletons.html). The demonstrated implementation is an offline affine baker consumed as Godot SpriteFrames, not a tested Spine or Skeleton2D skinning integration.
