# A limb disappears during playback

Use this when a user reports a missing leg, hand or equipment part even though
individual drawings looked plausible. Preserve the rejected clip and its scores.
Do not defend a still-image pass as proof of temporal readability.

## Trace the same limb across the boundary

Inspect predecessor, suspect pose and successor at native size and the actual
holds. Name the visible thigh/knee/shin/cuff/boot route, or the equivalent chain
for an arm or attachment. Record which cues remain, become occluded or disappear.
Legitimate overlap does not require every limb to be fully visible at all times.
However, "could be occluded" is not enough when the timed sequence loses the
limb's continuity. A two-boot → one-boot → two-boot sequence needs a legible tuck,
rotation or occlusion path. Do not insert an unrelated shoe merely to meet a count.

Keep human playback feedback separate from source geometry and still review.
The source may lift a hand or reposition a foot in depth; the bottommost alpha
pixel does not identify a persistent ground contact. Check the source joint or
paint landmarks before shifting a whole pose to align apparent ground rows.
An importer error, intended source movement and generated pose drift require
different remedies.

## Repair the missing connection

Start with the smallest connected surface that explains the limb: attachment,
joint, cuff and foot as needed. A complete owned neighbouring part can help,
but compositing it behind an opaque silhouette may hide its attachment again.
If the required view is missing, paint it explicitly with ImageGen using the
suspect pose as edit target and both neighbours as context. Preserve the raw
return and inspect model compliance before importing it.

If the returned canvas shifts the figure, retain that failure. A patch can use
an explicitly measured registration to its edit target; record the transform
and mask. Do not silently fit each animation pose to its bounding box. Restore
all original pixels outside the allowed mask, including transparent pixels,
then inspect the new joint and occlusion boundary at native size.

Define masks by component ownership, not a convenient row cutoff alone. In the
tested recovery, copying the old lower rows restored the grounded hand as well
as the legs, creating an extra hand below the newly lifted arm. Narrowing the
owner region excluded that stale hand. A valid edit journal cannot catch this
semantic mistake by itself.

Use the construction toolkit's `candidate_transaction` and `History` to retain
project/cel preconditions, exact changed coordinates, undo and replay. Export
the complete clip through the normal rational-clock path. Compare against the
unmodified control with identical holds and neighbouring poses. Obtain a fresh
temporal review; old scores do not transfer across an edit or override rejection.

## Tested study and limits

The public [recovery study](https://github.com/ACSKamloops/sprite-art-pipeline/tree/main/examples/recovery-refinement-20261023)
contains three actual ImageGen returns, ordered references, prompts, discarded
underlap/row-copy trials and a portable replay. Its final pose03 repair uses a
250-pixel polygon, changes167 RGBA pixels, and preserves the surrounding pose,
other nine drawings and all rational holds. Those exact values apply only to
the frozen inputs. The study's source-paint registration is(0,-10) after one
whole-canvas nearest sample to80x80 with an explicitly chosen alpha200 threshold.

The earlier8.2/10 still-only comparison was superseded by the user's report of
a vanishing leg. It is retained as evidence of a missed temporal fault. File,
LibreSprite, browser and Godot checks verify their declared scopes; the repaired
art needs its own human normal-speed acceptance. This is not a9/10 recipe.
