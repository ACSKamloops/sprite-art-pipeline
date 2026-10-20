# Pixel and motion QC

This runner finds concrete violations under explicit annotations. It **does not approve artistic quality**, assign an anatomy score, infer materials from an entire palette, or treat source pixel equality as evidence of good art. It uses its own scalar indexed compositor and alpha/ownership measurements; it does not import `sprite_lab` or reuse the construction proof.

Current source: `study/layered-cutout/project.json` (24 frames, 11 parts), actual Godot per-part/composite PNGs, fractional rig observations and authored rig source. The source fingerprints are pinned in `study-annotations.json`. CLI report inputs also fingerprint the exact project/annotation files. Stale source files fail. Refreshing annotations is a deliberate new reference decision, not a way to accept a failing edit.

## Actual findings

- Both planted boots have opaque sole row **139**, with ground boundary **140**. At the sampled frame starts, each stance segment has **0 px** world-center drift at the declared **48 px/s** walk speed.
- The exported walk holds each pose for **5 ticks at 60 FPS**. With continuous actor translation, its stationary local sole moves through the world by a supremum of **4 px within each hold**. All 12 annotated planted-foot holds violate the declared 0.5 px hold-slip limit. The interval is half-open; 4 px is a supremum, not a fictitious included endpoint. This is a real limitation of the held-frame/continuous-root combination, not a failure of the separately sampled procedural rig. A stepped root policy is a different explicitly supported assumption; changing the policy must reflect real engine behavior, not hide slipping.
- The full walk wrap is measured for both feet. Rear stance frame 11 → swing frame 0 has 0 px world-center delta after adding the cycle displacement; front swing → stance has 6 px delta. Neither boundary is falsely evaluated as two samples in one uninterrupted stance segment. Fractional ticks immediately before/at/after wrap and both sides of every hold boundary are retained. Fractional FPS is used directly, without integer rounding.
- Actual composite and part RGBA match the pinned source images. Frame anchors, ordered layers, timing, animation order/loop/FPS, palette identity and alpha clipping are separate checks. Source matching is **construction integrity**, not art acceptance.
- Joint ROIs follow explicitly named rig knee/ankle anchors. Minimum opaque-part distance, overlap, visible ownership-boundary pairs and largest RGB transitions are exported with exact coordinates/colors. Connected alpha can coexist with an unattractive seam. No material/anatomical interpretation or automatic seam acceptance follows. Optional reviewer-annotated `max_gap_px` can enforce a specific attachment requirement.
- The actual rejected AI patch changes the three independently reviewed blue-trouser samples `(61,98)`, `(60,99)`, `(59,100)` to pink accessory colors. All three fail their local `B>R` cloth criterion. This predicate is limited to those reviewed locations: it does not reject pink elsewhere. Exact outside-mask preservation does not prevent this material error inside the mask.

Inspect `evidence/current/all-poses-contact.png`, `world-tick-strip.png`, and `continuous-world-contact.gif`; the JSON retains analytic positions and full cycle timing. GIFs are deliberately slowed: 250 ms per pose in the contact GIF and 100 ms per source tick in the world GIF (6× slow at 60 FPS). They are visual diagnostics, not precise native-rate playback. `actual-ai-material-knee-8x.png` shows the reviewed material error.

## Reproduce

```bash
python3 -m unittest qc.pixel_motion.test_qc -v
python3 qc/pixel_motion/check.py study/layered-cutout/project.json qc/pixel_motion/study-annotations.json --root . --output qc/pixel_motion/evidence/current
# Exit 1 is expected: the current continuous-world walk violates hold-slip rules.
python3 qc/pixel_motion/adversaries.py
```

`adversaries.py` keeps source files read-only. Its reports include mutation ledgers and exact before/after PNG hashes. It demonstrates failures using real artwork: retained original rear-foot row138, speed64 instead of48, ground anchor moved1px, sprite cropped after translation70px, wrong pose binding, reversed layer order and unexpected palette edit. The original defective rear-foot PNG is retained source evidence, not a synthetic recreation. A missing/clipped foot is reported as unknown contact, not silently skipped or measured as zero.

## Annotate another character

`annotations.schema.json` describes the reusable versioned format. Define the canvas/anchors, ordered named layers, alpha threshold, frame source references and landmarks. For each action specify expected sequence/FPS/loop if required, the actual world policy (`continuous` or `stepped`), speed, contact-foot layer, **explicit stance frame IDs**, physical ground row and tolerated row/boundary/hold errors. Use isolated foot layers, or manually annotated `sole_roi`/per-frame `sole_rois` to disambiguate a foot inside a larger layer. Never classify the whole body's bottom-row center as one foot without this evidence.

Joint annotations name two layers and a canvas ROI; default output is evidence only. Add `max_gap_px` only when a reviewer has defined the intended attachment tolerance. Material annotations are separately reviewed coordinates and a documented color predicate/exact RGBA expectation. The supplied material samples cite `native/authoring-review/localized-knee-review.json`. No automated mask segmentation claims are made.

Remaining review prerequisites: silhouette/readability at intended scale, anatomical/material seams across adjacent frames, attack windup/contact/recovery design, actual engine world-motion policy, and any intended modified material annotations. Exact math and artifact fidelity cannot settle those questions. The supplied art remains unapproved.

World measurements combine **actual rendered local boot pixels** with the **declared root-motion model**. The world GIF places that model on a nearest-pixel diagnostic canvas; fractional analytic positions remain in the JSON/text. It is not an independent capture of a moving Godot actor. A real moving-engine capture remains necessary to confirm the runtime's interpolation/root/camera snapping policy. The present report demonstrates the held-frame/continuous-motion defect under the user-specified policy without pretending that a diagnostic visualization is new runtime evidence.
