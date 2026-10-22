---
name: imagegen-sprite-animation
description: Create consistent game sprites, directional character banks and short animations from OpenAI ImageGen key art, then refine them with source-pixel deformation and precise edits. Use for ImageGen sprite production, reference-matched animation, and alternatives to video generation.
---

# ImageGen Sprite Animation

For licensed authored motion used as a visual pose guide, read
[authored-motion-guides.md](references/authored-motion-guides.md). It covers
source/action verification, one-camera projection, explicit proportion edits,
source-versus-candidate clocks and an ImageGen grid-intrusion repair. This is an
optional guide route when the user has authorized 3D reference work.

For whole-character action coverage, failed run-half generation, pose-state
reuse and source-conditioned fall/get-up repairs, read
[action-coverage-and-recovery.md](references/action-coverage-and-recovery.md).

When an action changes character on its way into neutral, read
[canonical-reference-and-head-track.md](references/canonical-reference-and-head-track.md)
for appearance-authority checks, newly painted mechanics, source-owned heads,
whole-track joins and component-depth failures.

For incorrect bracer/hand assignments, protected-body controls, connected painted
arm bridges and occluded-shirt cleanup, read
[material-owned-arm-refinement.md](references/material-owned-arm-refinement.md).
Its portable three-layer journal/editor fixture is an unapproved art study.

For multi-action sheets, measured atlas gutters, shared column/row corrections
and exact guard/gather/idle state bindings, read
[atlas-registration-and-combat-states.md](references/atlas-registration-and-combat-states.md).
It separates a corrected state endpoint from a still-missing recovery bridge.

For controlled comparisons with provider pose guides and recovered pixel processing, read [provider-comparison.md](references/provider-comparison.md). It separates appearance, motion and timing, records a guided-paint improvement, and shows why grid inference and faint alpha noise need explicit tests before use.

For scarf ownership, protected head paint and mixed-rate component experiments,
read [component-refinement.md](references/component-refinement.md). It records
why preserved pixels and added poses can still lose to the reference, and why
support-foot trajectory must be checked before optimizing boot clearance.

Use ImageGen to supply coherent painted keys, then preserve their identity through bounded source-pixel bridges and requested fine editing. In this project the user calls the built-in OpenAI ImageGen tool “imagen”; this is not a Google Imagen integration. A generated sheet is a candidate, not a finished animation.

Use the system-provided `imagegen` skill for tool execution. Codex supplies it separately; it is not vendored in this repository. Built-in generation needs no API key. Do not substitute a local model, video provider, CLI/API runner or 3D stack without the corresponding user request. No generation call is needed when documenting, verifying or replaying saved work.

## Production sequence

1. **Freeze the brief and inputs.** Record accepted reference versus pose guide versus edit target; native painted height, stage, view, costume/materials, equipment, light, pivots, action/endpoints and requested directions. For refinements, preserve the actual user-preferred original clip and its recorded clock beside experiments; an earlier experiment is not automatically that baseline. A still reference does not supply hidden anatomy or an approved neutral pose. Preserve approved files; create a fresh work area.
2. **Make strong keys with ImageGen.** Read [production-recipe.md](references/production-recipe.md) for reference roles, prompt templates, complete-limb painting, registration and alpha. Inspect local edit targets before sending them. Save actual request, all actual inputs and raw return inside the project, not only the generated-images cache.
3. **Register once and protect ownership.** Measure returned dimensions rather than assuming the requested size. Use one declared grid transform; do not independently fit/recenter each pose. If a character crosses its nominal cell, retain full-image ownership and diagnose clipping before cropping; a recoverable overscan is different from missing paint. Restore the existing body outside the authorized limb mask, including transparent pixels needed to remove old parts. Inspect every join and material volume.
4. **Bridge compatible poses with source pixels.** Read [source-pixel-refinement.md](references/source-pixel-refinement.md). Keep the glove/boot/accessory on a rigid plateau while continuously deforming only its attached proximal part. Freeze donor/body roles, control points, triangles and integer source maps. This supports small compatible-view changes; it does not create turns, hidden paint or a general anatomical rig.
5. **Repair the actual defect.** For user-requested manual/programmatic work, use literal masked source-colored edits and the [construction toolkit](../sprite-construction-editing/SKILL.md). Keep editable layers, exact project/cel preconditions, journals and undo/replay. Rebase edits when upstream maps/paint change. Actual changed pixels differ from requested stroke coordinates.
6. **Compare with a fair control.** Keep original key times and duration fixed while comparing genuine new bridge art against repeated old poses in those same slots. Added exposures, more FPS, correct endpoints and exact pixels earn no art points. Inspect native and nearest enlargement, every adjacent pair, entry/exit and contrasting backgrounds.
7. **Verify and review separately.** Read [quality-and-delivery.md](references/quality-and-delivery.md). Bind art reviews to exact inputs; keep honest dissent and perception limits. Verify editor exchange, rational media holds and actual game-engine/browser rendering separately. Do not transfer one action/view's score to an entire library.
8. **Deliver a reproducible asset.** Include selected PNGs/atlas, editable source and timing sidecar, rational manifest, source maps/ownership, literal journal, prompt/reference provenance, scoped reviews and actual runtime receipts. Read [case-evidence.md](references/case-evidence.md) only for the tested example, hashes and known limits.

For engine manifests, APNG/CFR export and Godot integration, use the installed [animation pipeline](../sprite-animation-pipeline/SKILL.md). The companion toolkits are real dependencies of those editor/export procedures; this skill's map helper runs independently with Pillow, NumPy and SciPy. If companions are unavailable, report that gap rather than claiming an editor or engine test ran.

When using the accepted top-down demo as evidence, read [game-demo-lessons.md](references/game-demo-lessons.md) for exact source paths/hashes, review scopes and unresolved limits. Keep its scored history away from a cold art review until that judgment is frozen.

For the actual front/back/side production recipe, prompt layout, phase selection, conditional mirroring and repeatable repairs, read [directional-character-banks.md](references/directional-character-banks.md). For the complete art-to-playable workflow, use the animation companion's [top-down Godot demo workflow](../sprite-animation-pipeline/references/topdown-godot-demo.md). The accepted demo is evidence for those methods; its overall score does not certify every action or direction.

For additional selectable identities, owned head/boot/garment repairs and character-specific spell origins, read [character-expansion-and-spells.md](references/character-expansion-and-spells.md). It distinguishes real production art from selector fixtures, collision from painted projection and frozen source maps from art acceptance.

For diagonal views, explicit projected knee/sole guides and gait-role checks, read [eight-direction-pose-guides.md](references/eight-direction-pose-guides.md). It records why a crossed hip label can still repeat the same visible lifted knee, and separates actual eight-bank runtime checks from unfinished motion quality.

When borrowing provider techniques or testing interpolation, read
[provider-contract-and-inbetweens.md](references/provider-contract-and-inbetweens.md).
It separates PixelLab editor/API controls from ImageGen capabilities and records
why a classical-flow pilot was rejected before engine packaging.

For source-part rigs, seam/underpaint decisions, native-editor compositor
qualification and actual ground-relative material-pixel checks, read
[painted-part-rigs-and-contact.md](references/painted-part-rigs-and-contact.md).
Its bundled GPU example replays locally without a model or running Godot.

## Portable source-map example

The bundled fixture retains two real frozen bridge outputs, inputs and maps. It needs no model call or credential. `scripts/source_warp.py` can reconstruct from control points or replay a frozen map. Default verification writes nothing; outputs require a fresh directory. See [source-pixel-refinement.md](references/source-pixel-refinement.md) for commands and configuration.

## Scope and stopping

Keep provider identity, generated paint, reused paint, deformation, pixel edits and timings explicit. Follow the user's target and approval scope. Preserve an accepted style instead of adding a stronger action to chase scores. Revise a demonstrated defect with a bounded experiment; do not rerate identical art until a target appears. If a trial is worse, retain its evidence and choose the better source. Label unresolved directions/actions, animation boundaries, physical contact, equipment and controller behavior separately.
