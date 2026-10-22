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

## Refine a weak action without changing the accepted control

The follow-on `quality-round2/` study found that a correct-looking pose guide
can itself repeat the same visible raised boot. Before generating, inspect the
projected hip–knee–ankle chain of each half-cycle, including which boot is visible
on each side of the body. Renaming a leg or reversing joint labels does not
change the picture the model receives. A revised guide elicited opposite passing
poses, but the resulting compact legs still did not win a full-cycle review.

For a limb replacement, separate material owners from broad color thresholds.
In this study a teal-shirt predicate also matched blue-gray trouser pixels,
retaining an old knee over the donor leg. Use explicit spatial/material masks;
check both the opaque surface that should occlude a limb and the transparent
area beside it, which should not erase the limb. Restoring the correct donor
paint fixed an ownership error but did not guarantee better anatomy.

Bridge trials need controls with the same exposure slots. The S run added four
source-pixel bridges while preserving every original key onset and total time;
the control repeated the preceding key in each new slot. A subsequent source
scarf repair changed one cel only. These were modest, separately reviewable
improvements; twelve exposures did not establish a polished run.

Include the actual engine-selected idle when authoring and reviewing a one-shot.
SE get-up originally ended in a newly painted standing pose, so its complete
exit had been omitted from the art judgment. Binding the exact idle endpoint
exposed a late head/cuff/torso change. Likewise, inserting a source-part rise
between a crouched dash brake and half-rise reduced the recovery gap while
leaving the final costume-model change unresolved. Endpoint equality, smooth
crown-height numbers and rigid boots are distinct from believable weight shift.

The existing idle is a dependency, not automatically an approved identity
reference. A subsequent fixed-grid audit found the selected SE idle larger and
farther right than the preferred walk; the earlier standing get-up key was
closer to that walk's proportions. Before forcing every action into an existing
neutral, compare neutral and action against the actual accepted art. If neutral
is the mismatch, develop a separate corrected neutral and recheck its dependent
entries/exits together. Do not silently replace that shared state or fit all
action frames independently to an incorrect reference.

The source-only neutral trial combined the preferred walk's complete upper with
a declared planted-leg donor. One rigid upper plateau in the late rise retained
head, shoulder and cuff proportions better than independently moving those
parts, but reached upright too abruptly. Treat this as a bounded compatible-pose
repair, not a general rig. The cold reviewer preferred the neutral against the
actual walk reference and the rigid upper over the earlier compressed approach;
neither result established the full animation target.

Changing a shared neutral also changes its dependents. The selected SE hurt and
landing clips contained literal copies of the old neutral. The provisional
package refreshed those exact endpoint slots, retained their other drawings and
clocks, and rebuilt their editor/export manifests. NW death likewise reused the
revised NW fall. Scan the selected library for literal endpoint aliases and
review the related state boundaries; replacing only the idle selector leaves
old neutral paint embedded in other actions. Different-looking frames require
art judgment, not automatic replacement based on similarity.

A frontal dash needs visible foreshortening and a consistent front camera. A
dynamic lateral pose does not satisfy that direction; a front-facing high-knee
march does not satisfy the action. The tested launch/glide/brake repaint kept
the required view but sometimes hid so much torso that a frame resembled a head
and outstretched arms. Review that key with its neighbours and intended travel.
Calibrate actor scale across the whole related-key group with explicit reference
measurements, then apply one common transform. Do not independently fit each cel
to erase intentional pitch or height change.

Literal head restoration preserves those source pixels, not the perceived whole
character. New shoulders, gloves, trousers or head-to-body proportions can still
make an exact head look different. Compare complete actors on light/dark at
native size and through the real exit. Preserve independent disagreement:
`review3-independent/`, `review4-independent/` and `review5-independent/` favour
some repairs but do not establish 9/10. Their ordered-still judgments are not
continuous-playback acceptance. `quality-round2/index.html` provides exact-clock
normal/slow playback and optional illustrative travel; its JavaScript travel is
not a Godot physics or ground-contact test.
