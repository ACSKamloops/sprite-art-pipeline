# Detailed humanoid animation from a flat reference

Use this route when the approved art is a detailed raster character and no 3D model exists. A source image supplies visible surfaces, not a recovered skeleton or hidden anatomy. Keep the approved image immutable; author missing thighs, cuffs, greaves or soles as distinct referenced masters. Record their prompts, references, matte and source/native anchor registration. Generate semantic construction assets once, then animate and repair those authoritative parts rather than redrawing every frame independently.

The local Captain case lives in `/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/`. It uses the approved 256px image, independently authored complete legs and a convex greave/low foot master, exact upper-body ownership, bone-chain poses and deterministic pixel transforms. It is a particular humanoid example, not a universal armour template or a complete action library.

## Construction ownership

Recompose visible source partitions exactly before motion. Give each knee, cuff, boot and attachment one authoritative owner. A replacement shin must replace the legacy source, not cover a second moving plate. Retained parent registrations are historical provenance; explicitly distinguish them from the renderer's current source registration.

Keep hard armour volume with rigid transforms and localized authored shape keys. A circular camera-facing kneepad over a swinging greave can remain mechanically connected yet look wrong. Author loaded/passing face projection and seating/overlap; a source-palette shadow may join the cap to the shell. Avoid fixing a leg's mass by uniformly widening its boot or scaling its kneepad. Preserve source-attached ankles and sole material identities.

Use one fixed actor canvas, pivot and camera convention. Split upper torso/shoulder motion from waist loading where the silhouette needs a distinct settle/release; steady head clusters and equipment grips through those keys. More whole-body bob or a longer stride cannot substitute for missing anatomical poses. Secondary cape/kit lag follows their declared attachments.

Source-palette transforms are not automatically good pixel craft. The tested Scale2x-three-pass, 8x nearest rotation approximation preserves palette and exact rest identity; it is not full RotSprite and does not repair anatomy. Inspect native clusters, silhouettes and all affected adjacencies.

## Precise edits and exchange

Keep upstream master/rig edits separate from downstream baked-cel changes. A changed source invalidates stale project hashes and journals. In the full Captain layered project, one masked head-pixel edit changed only its coordinate in two shared frame bindings; actual canvas readback, exact undo/redo and journal replay were checked. Shared cels deliberately affect every binding.

The editor supports unrestricted RGBA palettes; palette size, image count and animation timebase are separate. Millisecond ticks at fps1000 encode 12–21ms holds without implying 1000 distinct poses per second. Preserve the original timing/events in the sidecar.

ASE/GIF exports must round cumulative boundaries, not each hold. Seventy-two independently rounded 17ms holds incorrectly total1224ms; cumulative ASE rounding preserves the1200ms cycle with16/17ms holds. GIF's10ms clock has a different preview quantization. Reopen/save/render in actual LibreSprite and compare every composite and duration. A small RGBA .aseprite file is often more practical for desktop editing than a large full-canvas indexed JSON project; retain both when programmable edits are needed.

## Reproduction and quality

Historical `upper-body-rig-v1/build.py::construct()` writes derived parts. Use an isolated source snapshot for reproduction, never assume that importing a builder is read-only. The local `pilot/captain-rebuild-v18-receipt/` proved all72 final frames and648 layers plus full manifest bytes reproducible without changing root files.

Use the companion animation skill's contact and temporal review workflow. Source equality, bounds and lossless exchange confer no art points. In this case v18 remained visually unapproved by one reviewer at8.85 despite another at9.155 and successful engine/material proofs. Consult the current source-bound review/handoff before using any candidate as an approved example; never infer acceptance from the newest version number.


## Historical reviewer acceptance, subsequently rejected

Captain v20 added bounded chest/shoulder compression and counterrotation around a source-owned waist, source-attached equipment response and a mostly steady head. The frozen actor manifest is `82cc443fc6b5f05e806a60788a01602c4f683376f1a6ff303abb5cdb43a6da86`. Two independent reviews of every pose/adjacency/wrap plus timed native/nearest2× playback rated it **9.025/10 and 9.17/10**, no critical defects. Those ratings did not establish usable walk quality and were superseded by user rejection. No Captain walking view is currently approved. Root handoff links the exact evidence; local delivery is `/home/astra/artifacts/space-marine-captain-walk/`.

Use `upper-body-rig-v2/build_preview.py --output /absolute/fresh` from the local pipeline repository to reproduce `weighted/`. A private constructor copy protects frozen inputs; all72 composites and648 layers reproduce exactly. Actual LibreSprite exchange, masked-pixel edit/readback/undo/replay, source browser and standalone Godot integration are separate proofs. A published skill reference points to this local example; it does not silently bundle or invent its art masters.


## Superseding Captain video rejection

The user rejected Captain v20 after viewing the delivered video. Its9.025/9.17 ratings are historical failed aesthetic judgments, not accepted example art. Root inspected consecutive decoded native and2× loops: the gait stayed crouched, contact/passing/extension silhouettes were weak, the upper combat illustration dominated, and deformed armour clusters were busy. Precise partitions, contact tests and small chest motion did not produce a believable walk. See local `pilot/space-marine-captain/video-rejection-review.md` and `user-rejection-v20.json` for source-bound evidence.

The MP4 omitted the tested root/floor/stance-correction presentation and quantized variable source holds at60Hz (66of72poses percycle). Compare the actual final deliverable against its declared presentation policy, not only a separate engine lab. Inspect motion silhouette and whole-cycle support/load/push-off at intended speed before expanding/interpolating the pose count. Technical reproducibility stays useful; user rejection supersedes reviewer art acceptance even when every hash still matches. No template should inherit the rejected example's visual approval.


## Evidence from the upright rebuild

The upright master improves construction space, but a more upright drawing alone is not a gait. Source-owned rigid parts preserved identity while independent reviews rejected the first whole loops for missing advancing extension, outward hinged kneecap motion and weak weight transfer. Narrower foot tracks improved passing placement but caused overlapping leg columns and did not repair shell perspective or all ankle gaps. These are rejected controls, not accepted production templates.

Pose-specific generated lower-body drawings give more rounded shells and visible incoming soles. Their named phases were still wrong in reading order, and supporting boots changed position, scale and ornament proportions. Preserve the raw atlas and document any explicit reordered sequence; do not use phase labels as an oracle. Registration requires source anchor ownership and common anatomy dimensions. A crop or offset does not certify the result.

A 2D cutout rotates its painted surfaces in the image plane. Constant projected bone lengths are not proof of correct 3D anatomy: a limb turning into depth must foreshorten. A genuinely authored 3D skeleton and fixed camera can supply canonical projected hips, knees, ankles and heel/toe trajectories. It supplies pose geometry only; it does not recover unseen armour surfaces from one raster drawing. Alternate depth-specific shell drawings or a constructed volume are still required. Verify those drawn surfaces against the geometry, both support phases and the whole actor at native size before interpolating or broadening the action library.

## Bind visible material, then test complete joints

A marker on a transparent texel is not a material witness. Four guessed
heel/toe points in a rejected leg trial all had alpha0, despite effectively
zero projected anchor error. Bind soles to observed source material and
retain source UV, triangle ownership and the posed mesh transform. Mark
unseen rear/underside surface shape and texture as authored, including
nearest-source-edge extrusion; never describe it as recovered art.

Source-visible partitions are not complete articulated parts. A later
closed greave kept its shape but source-only thighs ended4–6px before the
kneecap. Author a fixed femur-owned underlap behind the original paint;
verify the actual thigh/cap/shin/boot masks through every pose and review
exposed contours. Do not stretch a cap, move a bone, or add per-frame patches
to conceal incomplete construction. Mask connection establishes coverage,
not good anatomical shape or convincing armour volume.

Keep UV/local mesh bindings fixed across gait comparisons. Different pose
packets require fresh rasters and hashes, not rewritten receipts. Distinguish
source-palette equality, independent alpha agreement, full-composite exact
reconstruction and numerical UV sampling ambiguity. An independent raster
can agree in alpha while differing at a floating-point integer texel edge;
report the exact disagreements instead of claiming byte equality.
