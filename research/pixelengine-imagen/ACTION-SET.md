# Unarmed hero action set — 2026-10-22

The user requested run, walk, attacks, dash/dodge and the other states needed for
a game character. The follow-on package extends the previous six-action bank to
17 declared states across eight directions, preserving the exact preferred SE
walk and the current source-owned SE jab.

Local delivery: `/home/astra/artifacts/hero-action-set-20261022/`.
Start with `START-HERE.md`, `package-v1/library.json` and `COVERAGE.json`.
`play/` is an actual Godot Web export; `godot-v1/` is its editable engine project.
Generation remains built-in OpenAI ImageGen; no H3/local model was run.

New painted families: run, dash, dodge, jump, knockdown, get-up and interaction.
Guard, stun, crouch, landing and death are explicit source-pose/state bindings.
Jump anticipation stays grounded for 0.1 s; the engine applies flight height and
root travel afterward. Death holds its final drawing; knockdown gets up.

Known failures remain in the comparison bank: repeated leading leg in several
runs, S dash turning diagonally, head/hand drift and flat lower silhouettes in
some northern raw outputs. No source pixels were lost for those flat cuts; they
are generated-art defects. A focused SW run retry failed and remains unselected.
A partial NE retry supplies only some opposite-support poses and remains separate.

Selected bounded repairs: the S run mirrors a declared body region for the
opposite half-cycle while retaining head/scarf paint; exactly17 neighbouring
fragment pixels were erased from S dash without claiming to fix its facing;
SE get-up was repainted from the actual fallen pose to avoid reversing the body.
Source maps, masks, prompts, raw outputs and literal journals are retained locally.

The native Godot run checks 136 selected resources/544 exposures, exact decoded
RGBA, 1,001 controller assertions and actual input/state transitions. Web PCK
loading and browser execution have separate receipts. These checks establish
transport and state behavior, not art quality, collision, damage, invulnerability,
modular weapon compatibility or the requested9/10 acceptance.

Reusable lessons are in the ImageGen skill's
[coverage/recovery reference](../../skills/imagegen-sprite-animation/references/action-coverage-and-recovery.md)
and animation skill's
[state contract](../../skills/sprite-animation-pipeline/references/character-state-contract.md).

## Follow-on refinement

Local comparisons now live at `http://localhost:8903/quality-round2/`, with
sources and reports under the same artifact root's `quality-round2/` directory.
The original `package-v1/` and preferred walk remain preserved. This pass adds
S-run bridge/scarf trials, a front-facing low dash with recovery bridges,
SE get-up bridges into the actual idle, targeted northern fall completions and
several SE-run lower-body experiments. Trials and rejected paint are retained.

Frozen cold reviews favour the newer frontal dash recovery and NW fall/get-up
join, but do not establish the requested 9/10. The N-fall repaint lost narrowly
to its control. SE-run reviews disagree; a repaired source mask is not an art
promotion. Exact frame/hash/clock checks and real browser playback transport are
documented separately from these ordered-still judgments. New captures and
selectors belong to their own receipts; the earlier Godot numbers above apply
to the original package, not automatically to follow-on art.

The subsequent canonical-reference audit found that the old SE idle was broader
and offset from the preferred walk. A source-only neutral now preserves the
preferred complete upper and uses a planted source stance. A coupled get-up
approach and its literal hurt/landing neutral dependencies were rebuilt together.
This corrects a shared reference mismatch; it does not certify all action exits.

`package-v2/` selects nine changed bindings, including the dependent states:
S run/dash; SE idle/get-up/hurt/land; NW fall/get-up/death. There are still136
selected states, now553 exposures. Original package-v1, all other selections and
the preferred walk remain intact. The experimental SE-run repaints and N-fall
repaint were not promoted. The latest get-up still has an abrupt07→08 rise.

`http://localhost:8903/play-v2/` is the separately built Godot Web inspector.
Godot4.7.2 resource save/reload verified136 animations/553 exposures, and the
controller check passed1,001 assertions. Actual Web PCK loading and Chromium
keyboard captures passed separately. LibreSprite batch save/reopen preserved31
frames across four changed clips; no editor GUI painting is claimed. The
comparison page loaded115 distinct source PNGs with exact browser RGBA and
working controls. Full receipts are in `quality-round2/browser-proof/`,
`quality-round2/editor-proof/`, and `godot-v2/`.

Cold review6 preferred the canonical neutral at8/10 consistency/usefulness and
the new dash at6.5/10 usefulness. The disclosed-context review7 preferred the
rigid-upper get-up at7/10 usefulness. These are scoped ordered-still judgments;
there is no whole-set9/10 acceptance or continuous-motion human approval.
