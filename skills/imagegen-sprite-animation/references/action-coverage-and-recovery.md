# Full character coverage and recovery repairs

Use this when the brief moves from one polished clip to the character's action
set. Start with explicit actor/equipment/view/state requirements. A useful
unarmed RPG core is idle, walk, run, punch, cast, guard, hurt, stun, dash, dodge,
jump, land, crouch, knockdown, get-up, death and interaction. This is a tested
example scope, not a universal checklist: weapon swings, combos, swimming and
climbing depend on the game.

Separate **state bindings, frame exposures, unique drawings and accepted
animations**. A static guard can intentionally reuse an attack-ready pose.
Death can share knockdown art while ending in a terminal hold. Crouch, stun and
land can reuse appropriate keys with explicit ownership and timing. Those are
useful state contracts, not newly generated animations. If an exporter requires
two exposures for a held pose, duplicate the drawing with split holds and report
one unique raster.

## Generate manageable related-key groups

The 2026-10-22 study used directional appearance references and two 4×4 sheets
per direction: eight run keys/four dash/four dodge; and four jump/four fall/four
get-up/four interaction. This supplied coverage quickly, but **did not establish
production quality**. Multiple runs repeated the same lead leg; some front
dash keys turned diagonally. Heads grew and hands became glove-like despite
written constraints. Inspect the actual pixels before scaling an accepted claim.

Review both half-cycle contacts, not just apparent energy or frame count. A
targeted opposite-leg ImageGen retry can still return the same leading leg.
Retain that failed retry; more frames or higher FPS do not fix the phase error.
A strictly front-facing, symmetric outfit can support a source-pixel opposite
body half-cycle, while preserving the literal face/scarf with an ownership mask.
That operation reverses body lighting and may introduce a shoulder seam; inspect
all pairs and wrap. It is not a general solution for diagonal views.

Registration remains one uniform sheet scale with declared shared anchors and
measured ownership gutters. Inspect alpha in the **raw** return when a lower
silhouette looks cut off. Several rear-view fall keys had flat lower edges in
the original generation even though the export lost no retained pixels. A clean
source-map replay cannot fix bad source drawing. Conversely, detached neighbour
fragments can be removed by literal, source-bound pixel journals after their
ownership is demonstrated. Keep these two causes separate.

## Treat action boundaries as part of the action

Review fall → down → get-up as one sequence. In the study, a good-looking fall
ended head-left/boots-right while the generated get-up began with the opposite
orientation. Reversing the fall or appending a neutral pose did not supply the
missing physical motion. A new eight-key get-up request used the actual last
fall drawing as the start reference and the retained standing appearance as the
identity reference. It painted palm support, sitting, planted-foot half-kneel,
weight transfer and standing. The exported first key retained the exact fall
endpoint. The reversal was corrected; remaining face/registration changes still
required independent review. Endpoint equality is not full transition approval.

For jumps, keep the body art relative to the ground pivot. Split anticipation,
takeoff, airborne and landing phases. The engine supplies ground travel and
height; a grounded anticipation must not immediately lift because a parabola
was applied across the entire clip. Keep the shadow at the ground position.

Local source-bound study: `/home/astra/artifacts/hero-action-set-20261022/`.
Its `START-HERE.md`, `package-v1/COVERAGE.json`, generation receipts, source maps,
literal edit journals and independent reviews retain successes and failures.
The 136-state-binding package is not 136 accepted animations or a 9/10 result.
