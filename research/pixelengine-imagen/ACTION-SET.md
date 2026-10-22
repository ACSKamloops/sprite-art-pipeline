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
