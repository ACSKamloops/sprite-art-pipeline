---
name: sprite-animation-pipeline
description: Build and audit frame-based sprite animations from references, editable art, rendered models or extracted poses; preserve character consistency, encode timing and events, test Godot playback and iterate through hash-bound temporal reviews.
---

# Sprite Animation Pipeline

Use this for animated game assets and their Godot test workflow. For still-image production, use reference-art-production instead. This supports any setting, resolution or raster style; the Mana case supplies evidence, not universal art rules.

For a tested ImageGen four-direction character → complete local top-down Godot demo, read [topdown-godot-demo.md](references/topdown-godot-demo.md). It connects art contracts, gameplay/effect clocks, terrain/occlusion, combat presentation, save/input behavior, real Web exports and scoped independent reviews. Use the ImageGen companion's [directional bank recipe](../imagegen-sprite-animation/references/directional-character-banks.md) for actual front/back/side generation and repair.

## Establish coverage

For a complete declared character state set, held-pose aliases, takeoff delays,
interruptions and actual Godot/Web inspector checks, read
[character-state-contract.md](references/character-state-contract.md).

Create the requested action matrix by actor, equipment, direction and variant. Count requested actions, table bindings, unique streams, unique poses, exports and runtime-verified clips separately. Atlas order does not establish animation order. For extraction, retain aliases, branch/wait/event semantics and undecoded exits. For authored art, mark actions needing references or new poses. Unknown labels stay unknown.

When extending a user-approved character to attacks, jumps or equipment variants, read [approved-character-new-actions.md](references/approved-character-new-actions.md). It preserves the accepted identity/motion, explicit action framing, physical versus visual clocks, modular equipment and honest planned-versus-delivered coverage.

For tested pitfalls when generating those new actions, read [approved-character-action-experiments.md](references/approved-character-action-experiments.md): shared neutral controls, silhouette gates, pose contamination from appearance inputs, fixed whole-clip registration, explicit timing repairs and lossless review exports.

Read [source-and-authoring.md](references/source-and-authoring.md) to choose references and compare routes. A static photo needs no 3D model; Blender needs geometry, a rig for articulated motion and fixed rendering. Use AI for reference sheets, key poses and targeted repairs; independent generated frames need temporal review before becoming a finished cycle.

For actual artist/shipped-game samples, native timing recovery, visible-paint measurements and independent semantic annotation checks, read [professional-motion-study.md](references/professional-motion-study.md). It separates useful finished art from geometry controls, source clocks from runtime modifiers, and measured trajectories from hidden anatomy or physical contact.

For a coherent modern prerendered sprite route, read [textured-model-sprites.md](references/textured-model-sprites.md). It covers actual licensed rig/UV inputs, source equipment context, fractional source timing, camera-relative directional lighting, packed-scene reproduction, source-attached fine edits and soft-alpha Godot verification. This requires a real model and authored motion; it does not generate missing 3D anatomy from a flat image.

For native behavior discovery, read [runtime-observation.md](references/runtime-observation.md). Combine decoded tables/scripts with consecutive runtime observations of actual inputs; record controlled setup, conditional waits, actor slots and effect cleanup separately.

When learning a game's methods for a reconstruction, read [method-learning.md](references/method-learning.md). Build source-bound cases linking selectors, script controls, pose/part assembly, palettes/effects, displayed ticks and cleanup. Confirm causal claims with controlled replay/intervention; keep call coverage, unknown branches and semantic art approval separate. The reference includes the atomic discovery queue and demonstrated width, hold-sliding and clock failures.

## Fine construction and editing

For static image generation plus articulated bridges and replacement poses, use the construction skill's `references/hybrid-painted-masters.md`. Keep coherent source design, actual perspective changes, frozen rig replay and downstream pixel overrides separate. The tested calibrated-arm prototype received7.1/10; a better-looking side extreme reduced full-clip quality because its construction changed at switches. Do not turn correct sampling or journals into an art pass.

For precise programmable layered sprite construction and pixel repairs, use the installed sprite-construction-editing companion skill. It supplies a source-placement constructor, atomic mask/pencil/eraser/palette/translation operations, undo/replay, an interactive fine editor and actual LibreSprite layered exchange. Preserve upstream textures/rig/anchors separately from downstream cel journals; changed project hashes invalidate stale edits and reviews.

Measure actual rendered sole/attachment pixels during declared contact phases in the world-motion model. IK targets and centroid scores alone missed a demonstrated one-pixel boot gap. AI patches must pass preservation and material/anatomy/temporal reviews separately; an exact mask still admitted a rejected pink-strap/trouser edit. The companion case study binds these failures to the real-game control and tested tools.

For reusable-part rigging and deterministic baking without a 3D model, follow the companion's `references/rig-bake-workflow.md` and self-contained toolkit. It includes source-track editing, 12-action Godot snapshots, five layered fine-edit samples, a fixed-camera contact test and independent visual effect clocks. Keep mirrored views, sample coverage and prototype art status explicit.

For source-conditioned generated geometry and evidence-based rig repair, read [generated-model-repair.md](references/generated-model-repair.md). It covers neutral joint registration, fixed UV paint, captured-foot basis, exact pixel-to-source-face diagnosis, bounded owner patches, real cape collision/anchor checks and portable module exchange. Its Captain examples remain visually rejected; the diagnostic methods do not establish finished art quality.

## Build clips

For a broad action set from one approved hero, read [common-rpg-library.md](references/common-rpg-library.md). It covers source/state/view coverage, dependent seated/downed entries, fixed registration, full-return timing repairs, portable lineage, held input and the tested mixed-rate Godot clock fixture.


For separate painted body/equipment tracks with a shared cycle period, read [component-clock-union.md](references/component-clock-union.md). The source-hashed scheduler preserves every rational component boundary without resampling; masks, hidden-paint assumptions, phase coordination and the combined artwork require their own checks.

For a continuous rig guide plus separate appearance reference, read [continuous-guide-to-painted-sprites.md](references/continuous-guide-to-painted-sprites.md). It covers physical shoe controls, reference transport, complete native video retention, model-input alpha handling and the separate geometry/color/timing/performance gates.

When substituting ImageGen key poses for a video provider, read [imagegen-key-pose-alternative.md](references/imagegen-key-pose-alternative.md). It covers measured atlas registration, compositor-owned anchors, a useful coarse pickup and a rejected walk-inbetween test; attractive drawings and correct clocks did not establish motion parity.

For a tested, source-hashed offline reconstruction from a saved native video, read [offline-native-bake.md](references/offline-native-bake.md). The portable CLI and self-contained hero fixture retain full native timestamps, source-coordinate samples, literal despill edits and an explicit frame window; they do not find or approve a loop automatically.

For manual sprite refinement, exact-clock video delivery and separate live-engine/render tests, read [manual-sprite-delivery.md](references/manual-sprite-delivery.md). Use `scripts/project_delivery.py` to bridge an edited animation into video/Godot input schemas; `scripts/exact_cfr.py` verifies rational holds, actual video timestamps and every decoded pose. The referenced guarded-walk pilot received 8/10 and 7/10 from independent reviewers; this is one action/view, not unanimous acceptance or a reusable art score.

For a still/reference → native generated video → explicit sprite poses → fine-edit workflow, read [native-video-sprites.md](references/native-video-sprites.md). It covers exact presentation timestamps, fast-phase selection, cutout/palette boundaries, producer receipt closure and actual browser/Godot checks. Its original generic-hero video candidates remain visually unapproved; the separately authored walk above has its own scoped reviews. Successful transport and reversible edits do not certify a seamless gait.

Read [manifest.md](references/manifest.md). Freeze source hashes, view, actor scale, coordinate conventions, render/ground pivots and layers. Encode positive holds, an explicit clock, loop behavior, frame identity and events. Native conditional waits and external effects are stateful behavior, not invented durations. Label nominal projections and preserve their omitted dependencies.

For a lossless animated PNG with source rational holds, use `scripts/exact_apng.py manifest.json FRESH_OUTPUT_DIRECTORY`. It verifies actual APNG delay fields and every decoded RGBA frame before writing. Unlike an integer-millisecond export, it preserves a native1/24s hold exactly. The portable diagnostic is `assets/apng-smoke/manifest.json`; see [native-video-sprites.md](references/native-video-sprites.md) for limits.

Use deterministic exports or the requested sprite editor for ordering, atlases and mechanical transformations. Use image-generation tools for semantic raster creation/edits unless the user requests another authoring tool. Keep editable sources and rejected attempts. Don't recenter every pose independently: this destroys intentional motion and attachments.

Bundled helper (requires Pillow):

```sh
python3 scripts/animation_assets.py validate /path/to/clips.json --report /path/to/validation.json
python3 scripts/animation_assets.py review /path/to/clips.json /path/to/review --select actor/walk
```

It checks cells, hashes, timing, identity and events, then creates checkerboard contact sheets and temporal metrics. Scores flag differences; they do not approve anatomy, attachments or motion.

## Test engine and gameplay

For actual start/stop/collision use, source-owned contact masks, one-time draw-origin rounding and separate input/GPU/live-capture evidence, read [locomotion-runtime-and-contact.md](references/locomotion-runtime-and-contact.md). It includes a tested finite transition-bank contract and a forward-test clock failure; neither proves finished art quality.

For baked humanoid frames moving through the world, read [held-pose-world-contact.md](references/held-pose-world-contact.md). It covers variable-hold pose/physical clocks, source-attached whole-boot GPU evidence, fixed stance targets and matching the packaged preview to the tested correction policy.

Read [godot-and-browser.md](references/godot-and-browser.md). Import real SpriteFrames, reload resources and check every region, duration and loop. Test actual playback and JSON/browser boundaries.

assets/build_godot.gd imports the portable manifest. The optional assets/clip_driver.gd demonstrates movement, attack locking, interruption and frame events using one explicit simulation clock. It requires gameplay_bindings and infers no franchise names. It's a tested small top-down fixture; adapt collision shapes, cancellation, buffering and extra states to the requested game.

Test loop preservation, one-shot completion, replay, speed changes and low-rate frame crossings. Render and rules share the tested clock; duplicated JavaScript animation state can conceal engine defects. Hit events are authored unless native trigger evidence exists.

For independent palettes/projectiles/status effects, read [stateful-effects.md](references/stateful-effects.md). The optional palette helper is a tested timer example; rendering/lifetimes still need explicit layers and proof.

## Review and refine

For protected-body complete-arm paint, equal-clock extension/recoil experiments and small source-pixel path repairs, use the construction companion's `references/masked-arm-paint-and-motion.md`. Retain differing frozen scores and distinguish a compact-jab preference from numeric or full-library acceptance.

For strong static keys plus individually drawn extension/recoil cels, use the construction companion's `references/pose-specific-cel-refinement.md`. Compare new drawings against an equal-clock source-cel control; report internal consistency, reference match and motion separately. A scoped8.5 consistency review in that test did not establish an8.5 animation or video-provider parity.

For source-bound human playback feedback and reported loop freezes, read [human-playback-and-loop-diagnosis.md](references/human-playback-and-loop-diagnosis.md). Separate encoded timing from pose plateaus and media restart behavior; preserve an approved baseline and use equal-duration controls for timing experiments.

For an anonymous independent art review, read [blind-review-card.md](references/blind-review-card.md) first. It is deliberately free of case histories and previous scores. Do not open scored case studies, producer reports, root mappings or historical visual-quality anecdotes until the review is frozen. Report accidental exposure instead of calling a history-informed review perfectly blind.

For exhaustive predecessor/current checks, equipped state contracts and actual timed playback evidence, read [adjacent-frame-review.md](references/adjacent-frame-review.md). It includes the tested local player and review gate, plus demonstrated failures that pixel hashes and IK alone missed.

Inspect references, every affected frame and runtime sequences at intended game scale. Use contact sheets for identity/pose and timed playback for motion. Check silhouette, limbs/equipment, feet, attachments, alpha/framing, palette, seams and interruption artifacts. One screenshot doesn't establish motion quality.

Read [review-and-queue.md](references/review-and-queue.md) for atomic claims, stage receipts, recovery and review binding. Use independent review when requested or after a material workflow change. Separate worker outputs/worktrees. Record a demonstrated defect, repair the appropriate layer, rerun affected checks and view the replacement.

Review receipts require explicit clip_ids and input_fingerprint. Run check-review before handing off reviewed assets. Changed manifests/atlases invalidate old reviews. Partial visual coverage stays partial.

## Deliver

Provide assets, editable inputs where available, manifest, coverage ledger, reproduction commands and evidence paths. A local AI needs relative assets and a folder handoff. Publish real Web exports through the chosen hosting workflow when requested.

Keep source discovery, artifact correctness, engine behavior, native fidelity and visual acceptance separate. Report missing actions/effects/conditions instead of calling a viewer a complete animation library. Read [mana-case-study.md](references/mana-case-study.md) only for that extraction and its failure recipes.

## Blocking visual quality

For production orchestration, read [visual-quality-gates.md](references/visual-quality-gates.md). Anonymous reviewers should use the case-free card above instead of its historical narratives. The former Copper Scout V2 prototype art approval was superseded by user rejection. Its mechanical checks remain useful, but its anatomy, directional volume and motion were insufficient. Do not inherit that aesthetic acceptance. Require a strong native-size design, authored directional anatomy, believable key-pose progression and actual timed visual review before expanding a library. Richer AI-generated sheets also remain unapproved when gait phase, material shape or registration drifts.
