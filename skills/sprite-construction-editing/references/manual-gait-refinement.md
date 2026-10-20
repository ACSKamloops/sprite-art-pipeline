# Manual refinement from detailed sprite art

Use when the user wants existing pixels repaired or animated with an editor, source-owned parts and deliberate new drawings. A raster reference and readable source poses are sufficient to begin. A 3D model is not required for this route, and a hidden rig is not recovered by splitting the image.

## Establish the source and the actual defect

Freeze full-canvas RGBA, ordered poses, intended game scale, view, equipment, pivots, palette, clock and current review. Inspect native/2× colour, silhouettes and every predecessor/current pair including the wrap. Use onions and exact difference maps on the same coordinates. Independent bounding-box centering can conceal the defect and move attachments.

Classify the needed repair before drawing:

- A stray pixel, material stripe or local seam can use pencil/eraser strokes and a bounded mask.
- An orientation or equipment interruption can use an explicitly registered source part, retaining the target's posed arm/hand where needed.
- Missing contact, passing or opposite support is new pose authoring. Extra frames, RGB averaging and reordering cannot supply anatomy or a gait phase that is absent from the source.

Distinguish spatial screen-left/right from persistent near/far limb identity. Record visible cuff/sole/material witnesses separately from authored hip/knee/ankle pivots. Do not report an occluded knee as observed. Trace ownership from the art and layers, then record its colours; matching RGB alone is not an ownership classifier.

## Make bounded pixel repairs

Create a new revision from the frozen project. Use the toolkit's guarded operations and record exact coordinates, palette indices, reasons, before/after hashes and affected cels. Actual editor mouse strokes can be replayed through the same project history; keep the editor result and journal, not only a screenshot. A repeated click on an already correct colour is an operation but not a changed pixel.

For source-pixel pastes, retain the source RGBA and mask, source/target material anchor, integer translation and clipping policy. Keep the original posed arm and glove when they are the attachment authority. Check the completed composite as well as each part: a full shield can legitimately occlude a thigh without replacing that thigh's pixels. Inspect source ownership before deleting a suspicious fragment. In the retained case, gold near a repaired torso belonged to the unchanged sword pommel, not a second hand.

Verify outside-mask invariance, exact retained layers/palette where intended, full undo/redo/replay, and actual external editor save/reopen. A local repair can be accepted while the whole walk remains rejected.

## Author a missing walk rather than smoothing a shuffle

Draw the two opposing contact/loading keys and their passing/reach shapes first. Establish persistent near/far ownership and a traceable hip→knee→ankle path under the garment. Test the whole actor and flat silhouettes at game scale before making more in-betweens.

Reuse source leather, armour and cloth as drawing material. Record source-visible partitions separately from newly painted hidden thighs, cuffs and joint underlaps. If a complete boot is unavailable in the chosen still, another source pose may supply it. A source-derived upper residual may contain the full composite, including head and weapon; derive the actual body layer before moving a separately layered weapon or a second old blade can remain.

For a painted boot, separate calf/cuff and foot when ankle articulation is needed. In the tested walk, heel contact raised the toe around a source heel witness; flat loading retained the source foot; release raised the heel about the toe. The ankle placement had to follow the same pivot transform. These are authoring controls, not universal angles or a recovered walking controller.

Do not force constant projected 2D bone lengths to prove anatomy. In the retained three-quarter case, that constraint produced deeply bent support legs and a bicycling crouch. More upright loaded calves, explicitly foreshortened thigh shapes, a smaller clearing arc and deliberate knee drawings improved the result. Keep rigid boot width/volume distinct from changing projected calf length. Review the whole leg; an IK solution or connected alpha can still look wrong.

Use broad cloth planes and short knee folds where they match the source. Long parallel bright bands made the test thighs read as rods. Rounded cloth at the cuff and a known near-leg contour helped separate overlapping boots. Save exact overlap-outline strokes; they are downstream pixel edits, not evidence of hidden anatomy.

Let the pelvis, hem and chest respond to the support exchange when the art needs it. Braced gear need not swing. The case used a bounded garment tilt, small shoulder response and an upright translated face alongside newly authored load poses. Do not use more bob as a substitute for those poses. Keep the weapon grip and neck connected through every affected frame.

For a cloth deformation, forward-stamping source pixels can leave skipped rows or collisions. The retained correction used bounded inverse nearest sampling on an explicit garment area, protecting the hand/weapon. Check newly exposed edges and overlap ownership. These choices need visual review; they are not universally better than hand-drawn keys.

## Keep source edits and baked edits separate

Preserve part masters, transforms, ownership masks, pose geometry and generator snapshot as the upstream source. Keep baked pixel corrections and their guards downstream. A changed source invalidates old journals and reviews. Re-render to a fresh version rather than silently replaying stale patches.

Nearest sampling preserves a palette but does not ensure good clusters. Scale2× edge refinement before rotation is not full RotSprite and is not an anatomy repair. An unchanged unit-scale part should use an exact integer source translation where intended; repeated resampling can alter the detail unnecessarily. Record the raster snapping convention separately from authored float anchors.

Deliver one complete editable clip rather than thousands of unrelated cels in one document. Include full-canvas PNGs, atlas, layer project, external-editor source and required metadata sidecar, construction snapshot, pose plan, guarded pixel edits and current reviews. For actual-clock MP4 and engine evidence, use the companion animation skill's [manual-sprite-delivery.md](../../sprite-animation-pipeline/references/manual-sprite-delivery.md).

## Source-bound local case

Read `/home/astra/artifacts/pixellab-hybrid-walk-20261015/gait-v5/README.md` for the retained implementation and `HANDOFF.md` for continuation. This is local example art, not bundled with this skill. The frozen builder must stay in its original layout, or be adapted in a copy: it reads sibling `manual-v4/draft1/project.json`, the parent's `toolkit/sprite_lab`, and `gait-v5/leg-source/` inputs. Its Python dependencies include Pillow and NumPy. Copying only `candidate-7/` is insufficient for construction replay. Its upper residual is also a provenance hash input even though the torso is derived from separate body cels.

The candidate manifest retains its creation-time "pending review" boundary. Current status is in the source-bound review receipts, `CURRENT.json` and `FINAL-VERIFY.json`; do not rewrite the frozen reviewed manifest merely to update that status.

Useful case files:

- Source partitions and missing-anatomy notes: `leg-source/OWNERSHIP.md`, `extract.py`, `manifest.json`, material anchors and row masks.
- Actual pencil/paste work before the rebuild: sibling `manual-v4/edits/browser-boot-result.json`, `draft1/journal.json` and `masks/APPLY-PLAN.json`. Ten operations replayed, undid and redid; only frames 3, 4 and 6 changed.
- Final authored source: `candidate-7/project.json`, `parts/`, `poses.json`, `occlusion-pixel-edits.json`, `AUTHORING.json` and `build_snapshot.py`.
- Frozen builder reproduces the source project, manifest, sixteen PNGs, pose data and contour edits: twenty authoritative files byte-identical in `root/REPRODUCTION.json`.
- Final canonical project hash: `b5113dd7d0696cf43844f8dfa98f236753c2226a4383b19bb6d436453bdaa561`.
- Current scope: one guarded walk, one direction, sixteen 96×96 poses, 50 ms each, authored 800 ms cycle replacing the older 750 ms sequence. No new image generation/API calls in this manual pass.
- Reviewer A: 8/10, scoped pilot acceptance. Independent reviewer B: 7/10, usable prototype with weight/overlap polish remaining. Both reviewed all sixteen poses/pairs/wrap and all 48 actual decoded preview frames; B also reviewed all 32 moving-scene frames. Neither observed continuous real-time playback through the interface. Keep the disagreement and coverage limits.

The copied art dimensions, angles, offsets, cadence and scores are specific to that case. Do not use them as defaults for a new actor, a different view, another action or service-parity claims. User playback judgment can supersede these reviews, as it did in older rejected Captain examples.

## Subsequent quality trials

The continuation is in the same trial's `game-ready-v6/` folder. It keeps every failed revision and its source-bound independent review. Loading-only knee shading, small hip/hem warps, wider foot lanes and whole-upper-body settling yielded small gains; they did not solve complete passing-leg construction. Freshly drawn closed cuff/calf shapes improved volume locally. A shorter stride increased merged-foot/shuffle problems; more lift alone did not fix the anatomical drawing. Do not repeat parameter sweeps after evidence identifies a full-pose construction defect.

Built-in ImageGen produced stronger rounded thigh/cuff/boot drawing references. A shared full-sheet registration, hard alpha threshold and source-palette mapping were explicitly recorded, with no per-frame bbox fitting. The generated four- and eight-pose sheets nevertheless repeated similar lead arrangements. A color-coded persistent-leg guide did not guarantee the model followed that identity. Exact preserved upper layers and a better individual boot did not make the hybrid a valid alternating walk. Check actual hip-to-knee-to-ankle ownership and temporal lead exchange; labels and recoloring alone cannot prove it.

Retargeting rich generated leg parts to a coherent authored ankle trajectory fixed material planting but introduced donor-shape hitches at the compact-passing to reaching change. A single painted boot master, split into independently articulated calf and rigid foot, substantially reduced those substitutions. Independent whole-actor reviews still rated it only7.1/7.3: broad shafts crowded the small space beneath the tunic and hid passing-knee direction. A stable master is a consistency control, not proof that its proportions or poses are good. Test a few representative full-actor keys when changing garment length or boot taper; preserve toe/heel material separately if the defect is in the shaft. Do not regenerate a complete bank for every unjudged design variation.

Include the actual compressed passing keys in that design gate. Contact and emerging-foot samples alone missed the unresolved construction. A source-attached shorter hem and narrowed calf improved proportions but the full cycle still received7.5. Moving the cap down added a pale band; moving the swing cuff forward made the joint overlay look more bent while normal art remained a bulge. Judge the normal actor before expanding either change.

A later targeted ImageGen edit produced useful rounded knee paint and approximately preserved whole-grid placement, yet moved the clearing shoes forward within their cells. Restoring exact original feet around its imported calf paint left an inconsistent joint-to-shoe route. An outside-mask and foot-pixel pass could not detect this semantic conflict. Trace the new knee through the actual retained ankle before importing its calf; selectively reuse paint references or redraw the connection. Do not adopt the generated body just because a still looks more finished.

Treat pixel preservation as a deliberate experiment control, not an unrequested constraint on new art. The preserved foot partition in this case included a broad two-row ankle neck; later manual knee/calf repairs had only a few exposed pixels before meeting it, and remained rejected. If the inherited shoe proportions or partition prevent a coherent drawing, test a newly authored consistent shoe master and editable neck separately. This invalidates old foot-material, contact-witness and planting receipts; adapt the heel/toe pivots and measure the new art rather than inheriting those claims.

When a rotated part creates a spur, trace the actual target pixels to source pixels before choosing an edit mask. The case's `game-ready-v6/art/trace_prong.py` carries source IDs through Scale2x's original-color branch decisions and nearest sampling. It identified upper-cuff rows74/75 among an apparent extra toe; trimming only the lower ankle could not remove that shape. Unique-ID colors must not replace the original RGB when deciding Scale2x branches, or the diagnostic changes the sampling it is meant to trace. Source material centers, authored guides and recovered anatomical joints are distinct; misplacing a part's source origin can displace its visible volume even when the target guide is correct.

Palette remaps must select masks from an immutable input. The continuation's in-place depth loop could map one source color onto another source color and then darken it again later in the loop. Reproducing the actual far-calf exports confirmed13 affected pixels in each of two examined poses. Check one-application lookup against an independent source array and reverse/shuffle color iteration; the output should be order-independent. Source-pixel fidelity to that faulty producer was not proof of a correct depth policy. Preserve rejected exports and re-review the corrected source.

Label hashes by representation. The toolkit's canonical normalized-project hash and the SHA256 of the JSON file including its final newline can differ legitimately. Review receipts should bind exact files; name a canonical hash separately rather than calling both the project-file hash.

For game consumption, the companion animation skill now documents finite source-bound start/stop banks, post-shading explicit material ownership masks and actual input-driven Godot captures in `references/locomotion-runtime-and-contact.md`. The continuation's current reviews remain authoritative; the user's 9/10 target is not an achieved status merely because the engine tests pass.

## Direct corrective paint after a rig bake

An Emberwake Rowan trial passed literal layer/map replay while its assembled
06/07 cels had four exposed background strips between trousers and boots.
An independent critic located the breaks in native pixels. The repair kept
that failed raster locked and added a separate editable correction layer:
125 changed pixels across02/04/05/06/07, recorded through105 real local-editor
pencil transactions. Actual source-palette witnesses distinguish sampled
edge restoration from newly authored cuff geometry. Do not refuse required
new paint merely to retain a source-only claim.

Inspect the real material and volume at each join. The repaired cuffs have
opaque cross-sections of9–11 native pixels and each boot connects to the
body; those checks support the demonstrated gap repair, not universal anatomy
rules. Occlusion may legitimately conceal other joints. The actual toolkit
undo/redo and journal replay preserve the locked source, and external
LibreSprite save/reopen retains the editable project and rendered RGBA.

The repaired whole walk ties the original in a fresh review:8 overall but
7.5 motion, with chronology-only uncertainty. This does not meet an8 motion
request or establish a whole-cycle improvement. Keep the simpler accepted
control until a visible gain or human playback preference is established.
The exact case is `/home/astra/artifacts/emberwake-rowan-phase-rig-repair-v1`;
its review is `emberwake-rowan-repaired-cold-review-v1` under the same root.

For a separate full-key/source-part case that reaches a scoped8 motion
judgment, read the ImageGen companion's
[painted-part rigs and replay fixture](../../imagegen-sprite-animation/references/painted-part-rigs-and-contact.md).
Its8 NE cels and conditional mirrors do not certify this Rowan walk.
