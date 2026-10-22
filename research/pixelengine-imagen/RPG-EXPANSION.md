# Hybrid hero: directional combat expansion

The user preferred the exact Hybrid walk. This expansion preserves it and
creates new ImageGen paint for N, NE, E, SE, S, SW, W and NW. Each initial
24-pose direction bank contains walk, punch, cast, idle, hurt and dodge keys.
These are candidate drawings, not eight directions inheriting the walk's
acceptance. Jump, run, death/get-up and equipment-specific actions remain open.

Local source and all failed attempts:
`/home/astra/artifacts/hero-rpg-expansion-20261021/`.
`CONTRACT.json`, `recipes*/`, `selection-plans/`, `guided-jab/` and `reviews/`
retain prompts, actual references, raw returns, hashes, maps, clocks and findings.
No H3 or local model was executed. The guided jab uses an already saved motion
guide; its new paint comes from built-in OpenAI ImageGen.

## What changed the result

1. A full turnaround and a strong right-facing appearance reference pulled some
   left/profile action cells into the wrong view. A cropped target-view guide
   as the leading reference improved facing, especially with the conflicting
   full walk omitted. Explicit words alone did not guarantee the correct view.
2. Nominal equal atlas cells cut boots and introduced previous-row paint above
   heads. Measured whole-row/column empty gutters defined shared ownership
   partitions. Compensating rational offsets retained the nominal source roots;
   no pose was resized or centered independently.
3. Large lateral ramps repeated by column across unrelated actions. Shared
   column corrections and standing/walk row corrections removed those layout
   errors. All 168 corrected rasters matched exact integer-translated controls.
   This changed registration, not anatomy, leg ownership or palette quality.
4. Guard, spell-gather and relaxed idle are different states. Explicit source
   selections now bind punch/cast completion to their own ready pose and
   hurt/dodge to idle. Idle currently holds one neutral drawing; it is not a
   completed breathing animation. Reused endpoints are not new intermediate art.
5. The SE casting sheet changed the apparent acting arm. A localized ImageGen
   request repeated that failure and was rejected. The selected compact cast
   excludes the wrong-hand pose and uses a declared gather hold; a genuinely
   painted windup/recovery bridge remains a separate improvement.
6. The alternative genuine client grid rendition made SE combat smaller than
   the preferred walk. The primary fixed-scale rendition was retained. Neither
   grid processing nor palette snapping establishes motion parity.

## Reproduction tools

`tools/build-rpg-bank.py import-sheet` consumes an explicit pinned recipe and
contract. It saves prepared source, raw crops, frozen full-sheet coordinate maps,
PNG/ASE/APNG exports and registration diagnostics. `verify-bank` replays those
maps. Alpha128 and the preferred hero's 33 opaque palette colors are measured
candidate policies, not universal sprite import defaults.

`tools/compose-rpg-actions.py` selects exact existing poses with explicit holds,
lineage, unique-raster counts and endpoint bindings. It does not interpolate or
paint a missing pose. `tools/build-rpg-bank.py assemble` produces the local
viewer and coverage ledger while retaining the preferred original walk.

`tools/build-rpg-preview.py --package PACKAGE --output FRESH --godot godot --check`
builds a portable Godot inspector. The first selected package passed actual
Godot 4.7.2 resource/input/state checks for 48 animations and 223 exposures, plus
browser pixel checks for those exposures. These results are tied to that
package's receipts; a later selected variant requires a fresh readback. The
final round4 package has now passed a separate rerun: 48 selected animations,
226 selected exposures, a 1200 Hz common clock, 316 actual Godot resource/input/
state checks and browser RGBA readback of all 247 exposures across 51 variants.
These are transport/state proofs, not art acceptance.

## Remaining quality gaps

Independent ordered-frame reviews found substantial gains from registration
but did not establish production-quality motion. E/NE passing-leg readability,
smaller pose-volume changes and sparse extension/recovery remain concerns.
The first SE dodge endpoint repair left a seven-pixel support change inside the
recovery. A later simple-duck variant excludes that wrong-scale recovery drawing
and uses the exact preparation pose in reverse before the neutral stand. It has
three unique drawings, not a newly painted recovery bridge or rolling animation.
Reversing preparation alone still left the action row floating relative to idle.
A subsequent shared source translation of +9Y for SE and +2Y for S preserved
all visible pixels and aligned the selected support rows: 75/75/75/75 for SE,
71/70/71/71 for S. An independent addendum confirmed no clipping or relocated
large sole jump. SE still switches head height by 14 pixels at entry/stand,
so a newly painted lowering/recovery bridge remains necessary. Completion
correctness and support registration alone must not hide a coarse pose pop.

The more strongly guided SE jab has its own input hashes, true timing,
row-registration variant and cold review. The reviewer preferred its registered,
closed-guard variant and rated chronology/usefulness 7.6/10. It is selected for
the later inspection package; the earlier punches remain comparison variants.
This is a prototype score, not 9/10 or user acceptance. Inspect it at its own
pace beside the initial punch; added poses or more FPS earn no quality points.
Human normal-speed acceptance, hand/grip anchors, equipment compatibility,
hit contact, spell effects and a finished action/direction library remain distinct
gates. No numeric 9/10 or whole-library approval is claimed here.

## Follow-on material and body study

`/home/astra/artifacts/hero-rpg-quality-20261021/` preserves literal material
repair, protected-body painted arms, source-mapped bridges, narrower occluded
underpaint, projected torso turns and full-body generation/guard-repair controls.
The current requested acceptance target is9/10; it remains open. Review01
preferred the slight-lean painted-part candidate, scoring7.5 drawing/8 identity/
7 chronology/7 use. This calibration differs from the earlier review and must
not be averaged into an invented progress score. The separate clarification
identified no mandatory new motion fault in that compact jab; its drawing
half-point was holistic preference, not an extra repair obligation.

A procedural forearm assembly was rejected visually despite successful exports.
The jagged teal flap was traced to authored underpaint, narrowed in later
candidates. A new full-body paint pass lost the separate guarding arm at contact;
one same-sheet source-pixel repair restores it without changing silhouettes.
Palette and timing alternatives retain separate exact controls and reviews.
The ImageGen skill's material-owned-arm reference includes a portable replay
fixture from the first slight-lean experiment; it is explicitly unapproved art.

The second review preferred the narrower-underpaint/projected-torso candidate:
8 drawing, 8 identity, 7.5 chronology/use. The full-body alternative still moved
its rear sole footprint by about four pixels. Fixing the sole height alone had
missed this. A frozen frame00 lower-body component now keeps its complete boot
pixels fixed, with a separately reviewed hip/hem seam risk.

The generated combat heads also differed visibly from the preferred walk. Two
new controls reuse the literal approved SE head with an explicit one-pixel
attachment track. Dense source maps replay every output pixel; actual changes
remain inside declared old/new head ownership and all body rows31..79 remain
exact. These controls do not inherit combat acceptance from the walking head.
The painted-part control also retains four editable body/underpaint/arm/head
layers, verified RGBA-identical to the head-composite comparison input. Actual
LibreSprite save/reopen preserves every native layer cel and rendered frame.
Its integer-millisecond file clock rounds cumulative boundaries; the original
rational manifest/sidecar remains authoritative.

The new ten-exposure SE head/part jab has a separate Godot rerun in the local
`engine-head-components/` folder: 48 selected bindings, 228 exposures, 1200 Hz,
316 controller/input/state checks and exact saved-resource RGBA. The unchanged
preferred original walk remains selected. Browser readback of the four latest
controls covers all 112 tick-midpoint samples and every exposure. The media
preview retains the exact 48 Hz schedule. None of these checks establishes
continuous normal-speed human acceptance, contact/hit behavior or 9/10 art.

Review03 preferred the source-head painted-part candidate (L), with drawing8,
identity8.5 and chronology/use7.5. It found no actionable fault in L. These are
scoped holistic judgments from still chronology; do not invent a missing repair
or rerate identical art to reach the requested9. A separate one-pixel distal
scarf follow-through control tests secondary motion while preserving L's actual
body/head/arms/feet and clock. It is optional research, not a required repair or
an accepted improvement. The normal-speed human comparison remains pending.
The scarf delta review retained unchanged L: the optional wave introduced a
minor notch in two exposures around native(26,36), with no clear native-size
benefit. Its exact pixel/clock preservation does not earn art or motion credit.
