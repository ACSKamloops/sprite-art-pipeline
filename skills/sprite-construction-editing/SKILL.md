---
name: sprite-construction-editing
description: Construct layered raster sprites from source images, make precise replayable pixel edits, exchange editable sprites with LibreSprite, and verify construction against game captures and Godot rendering. Use for fine sprite editing and animation refinement beyond generating whole images.
---

# Sprite Construction and Fine Editing

Use the bundled [toolkit](assets/toolkit/CONTRACT.md) for deterministic pixel work when the user requests programmatic construction/editor workflows. It supports modern RGBA art with unrestricted palette size. For semantic image generation use the available image tool; a generated image is a candidate until reviewed.

## Freeze inputs

Record source-image hashes, canvas/game scale, view, actor/equipment identity, palette/material regions, render and ground anchors, layer ownership, action/direction coverage, pose landmarks and motion brief. Missing anatomy/views stay missing. A fused image supplies one paint layer; splitting it does not prove hidden limb geometry. A 2D cutout route needs editable parts/anchors; articulated 3D rendering needs an actual model/rig.

For generated front/back/side banks, protected-body passing-leg edits and explicit whole-cel origin repairs, read the ImageGen companion's [directional-character-banks.md](../imagegen-sprite-animation/references/directional-character-banks.md). Its selected direct composites and rejected rigid-boot/warped-thigh trial separate pixel preservation from believable anatomy; its same-side rear-weapon repair is new full-pose paint, not an exact-body edit. Use the animation companion's [top-down Godot workflow](../sprite-animation-pipeline/references/topdown-godot-demo.md) for in-game visibility, input and export checks.

For extraction, retain decoded table/stream order, aliasing and unknown commands, plus consecutive runtime captures of inputs, pixels and relevant state. Distinguish selected pose from presented pose. Independent raw-source fidelity must not share the producer renderer. Read [the real-game case and demonstrated failures](references/case-study.md) when using native evidence.

## Animate reusable parts

For a source-bound diagonal leg-proportion repair, read [lyra-leg-repair.md](references/lyra-leg-repair.md). It records cleaner generated paint versus actual passing-leg correction, portable painted-part replay and why timed acceptance remains separate.

For complete generated arm keys under a protected native body, bounded wrist-path edits, source-shaded fine painting and mixed independent reviews, read [masked-arm-paint-and-motion.md](references/masked-arm-paint-and-motion.md). It also records why fixed soles, fragment rigs and a whole-arm affine were rejected.

For static full-body keys, actual local pencil/eraser refinement and equal-clock drawing controls, read [pose-specific-cel-refinement.md](references/pose-specific-cel-refinement.md). The demonstrated route meets a scoped character-consistency target while remaining below the video baseline for motion; it also records failed whole-body meshes, retained old-part pixels and verified editor replay.

When substituting static generated artwork and manual editing for a video provider, read [hybrid-painted-masters.md](references/hybrid-painted-masters.md). It covers complete masters versus visible cuts, coherent replacement drawings, wrist calibration, non-collapsing joint interpolation, guarded hidden-paint/cel repairs and an independent frozen-affine replay helper. The tested hero alternatives remain below the accepted video baseline; their mechanical verification is not quality parity.

For modular bodies, swappable equipment, hidden-paint completion and rig-to-sprite experiments, read [modular-parts-and-attachments.md](references/modular-parts-and-attachments.md). It separates baked-body equipment tracks, hybrid painted rigs and full cutout rigs, with source-ownership and actual-raster checks.

For fixed whole-clip sampling, source-coordinate witnesses and explicit action timing repairs, use the companion animation skill's `references/approved-character-action-experiments.md`. Newly generated backgrounds, pose scale and held extremes require fresh checks; previous matte or timing recipes do not establish their correctness.

When learning from shipped motion templates or testing model-generated pose paint, read [recovered-pose-and-generated-paint.md](references/recovered-pose-and-generated-paint.md). It distinguishes actual client controls, body calibration, painted-part anchors and generated pose compliance; correct joint math alone did not pass the independent motion review.

For manual refinement of existing detailed sprites, read [manual-gait-refinement.md](references/manual-gait-refinement.md). It covers source-owned copy/paste, real pencil/eraser journals, missing opposing gait poses, articulated boots, projected anatomy and a reproducible 96px walk with independent 8/10 and 7/10 judgments. Its art settings are case-specific; neither the scores nor the original seven-pose defects establish approval for another character.

For a source-colored triangular part warp, read [nearest-part-warp.md](references/nearest-part-warp.md). Its standalone CLI uses explicit owners, inverse nearest samples and source-texel witnesses; it does not infer underpaint, occlusion or a complete rig. Validate the combined animation separately.

For detailed humanoids built from an approved flat sprite without a 3D model, read [detailed-humanoid-parts.md](references/detailed-humanoid-parts.md). It covers newly authored missing anatomy, single-owner armour/joint shape keys, isolated reproduction, source-attached precise edits and actual lossless layered-tool exchange. Art approval remains source-bound and separate.

For a repeatable 2D rig→sprite bake with source-track editing and a real Godot comparison lab, read [rig-bake-workflow.md](references/rig-bake-workflow.md). The toolkit retains the original two-view baseline and supplies a V2 biped with authored front/back, mirrored left, persistent equipment, contact compensation and separate VFX. For the current build/test/review commands, read [four-view-workflow.md](references/four-view-workflow.md). For source-attached painting and one complete animation per editable project, read [source-paint-and-clip-editing.md](references/source-paint-and-clip-editing.md). These are prototype capabilities; each final export needs its own visual acceptance. Read [recent-ai-workflows.md](references/recent-ai-workflows.md) when comparing AI proposals with deterministic animation; dated primary sources and actual renderer tests are distinguished from vendor claims.

## Construct and edit

Copy assets/toolkit to an isolated work folder; requires Python3 and Pillow. Read [editing-contract](assets/toolkit/docs/editing-contract.md) for transactions and tool exchange, and examples/construction/spec.json for source placements. From that folder:

```sh
python3 scripts/sprite_construct.py examples/construction/spec.json output/project.json
python3 scripts/sprite_edit.py validate output/project.json
python3 scripts/sprite_edit.py apply source.json edit.json --output edited.json --receipt receipt.json
python3 scripts/sprite_edit.py replay source.json journal.json replayed.json
python3 scripts/sprite_edit.py export edited.json exports
python3 -m http.server 8140 --bind 127.0.0.1
```

Open /editor/ and load the project. Pencil/eraser, masks/recoloring, layer/frame/palette selection, onion skins, guides/diff, undo/replay and exact clock playback are available. Every edit has an expected project hash and reason; candidate imports additionally bind the cel hash and exact mask. Verify changed coordinates and outside-region invariants. A shared cel deliberately changes every referencing frame; global palette edits can change many cels. Preserve locks and explicit translation clipping policy. Partial-alpha editable RGBA is authoritative; browser Canvas2D can round premultiplied translucent colors.

Keep upstream textures/rig/anchors and downstream cel journals separate. Rerendering changes the project hash and invalidates old journals; repair upstream where appropriate or explicitly rebase and review downstream overrides. Never silently reuse an old receipt.

For source-attached UV/material edits on a textured 3D rig, use the companion animation skill's `references/textured-model-sprites.md`. It includes a licensed editable example and explains why source geometry/rig/action, equipment context and fixed camera/light conventions must be frozen. Verify a fine edit in every affected view and representative motion phase; a shared UV can paint unintended body areas, and global illumination can change pixels beyond the edited feature.

## Verify quality in layers

1. Validate source placement, visible RGBA, timing, pivots, exact undo/replay and rejected-edit atomicity. Use portable load_json/load_project for JSON numeric boundaries. Run the meaningful bundled tests with python3 -m unittest discover -s tests -v.
2. Exchange selected animations using ase-export/ase-import plus the required sidecar; verify actual external LibreSprite save/reopen and rendered pixels. Quantized tool milliseconds are a preview; native tick clock stays authoritative. ORA editors may strip embedded metadata; unsupported transforms/order/timing reject.
3. Test the actual Godot renderer: SpriteFrames save/reload and durations/loops when using that architecture, or the custom atlas schema/loader/clocks when using one. Verify GPU pixels, real animation playback and game-specific movement/attack/interruption/events. Sprite appearance alone cannot establish hit windows. Use the sprite-animation-pipeline skill for its tested import/driver helpers or its top-down demo reference for the custom Emberwake route; do not force a second unused renderer.
4. Measure actual rendered boot/attachment pixels with declared contact phases and root world displacement, including fractional samples throughout held frames. An IK target, alpha centroid, pose boundary or shadow bottom is not a whole-timeline sole check. Include complete loop wrap and recovery; record the ground boundary/pixel-row convention, raster/camera snapping and continuous-root model separately.
5. Independently view affected frames and adjacent poses at intended scale and in timed motion. Check identity/material boundaries, anatomy, joint seams, silhouette, equipment attachment, anticipation/contact/recovery and weight. Bind review to exact source/project/export hashes and covered clips. Mechanics passing does not create art approval; defects require targeted repair and fresh review.

For AI candidates, save prompt/references/model/master. Check dimension drift, alpha/silhouette and outside-mask changes. Explicitly record any candidate registration; never independently recenter animation poses. Localizing a patch proves preservation only. Reject material leakage or weakened pose landmarks even when all pixel invariants pass. Do not claim Google Imagen was tested when the available tool is a different model.

## Scale and deliver

When delivering many actions from a shared hero, use the animation skill's `references/common-rpg-library.md` for fixed registration, dependency endpoints and complete primary source-pointer checks. Validate local unregistered originals, raw/matte samples and exact source hashes before rebinding a repaired manifest to its editor/APNG receipts.


Use separate worktrees/output folders per authorized worker. The sprite-animation-pipeline queue provides claim-next, lease heartbeat, stage receipts and revision; read its references/review-and-queue.md before advancing stages. Keep mechanics, native fidelity and art acceptance separate. Never promote a changes_requested review to approved.

Deliver editable sources/spec, journals/receipts, portable exports, reproduction commands, hash ledger, current reviews and remaining action/view/behavior gaps. The calibrated sample is a tool fixture; the real-game control is original-game art; neither establishes original production art; the rigged character is an original prototype.

## Blocking visual quality

Use the companion animation skill's `references/visual-quality-gates.md`. The former Copper Scout V2 prototype art approval was superseded by user rejection. Its mechanical checks remain useful, but its anatomy, directional volume and motion were insufficient. Do not inherit that aesthetic acceptance. Require a strong native-size design, authored directional anatomy, believable key-pose progression and actual timed visual review before expanding a library. Richer AI-generated sheets also remain unapproved when gait phase, material shape or registration drifts.
