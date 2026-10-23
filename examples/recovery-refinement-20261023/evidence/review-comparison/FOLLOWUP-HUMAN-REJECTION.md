# Follow-up after human playback rejection

The user watched the actual preview and reported: **“It's not great the leg vanishes in one of the frames it looks like.”** This is new playback evidence and rejects the current practical result. The earlier frozen still assessment remains historical; it does not override this observation. No new scores are assigned here.

**Common frame 03 is a strong visible match to the complaint.** Frame 02 paints two lower-leg/boot routes. In 03, one brown cuff/boot and its separately readable trouser route disappear; only the long diagonal trouser mass ending in the screen-right boot remains. Frame 04 again paints two knees and two boots. Thus the stills substantiate a two / one / two visible-leg sequence at 02→03→04. The missing cue occupies the full 200 ms of 03, from 0.425 to 0.625 seconds. The user did not identify a frame number, so this is the best corroborated location rather than proof that they referred to this exact exposure.

## What disappears

Use screen position to identify the limbs; the drawing does not justify confidently naming anatomical left/right. Call the leg ending in the rightmost boot **P**, and the leg ending in the lower, more central boot in 02 **T** (the leg being tucked).

Coordinates are zero-based native 80 × 80 image coordinates, x rightward and y downward. Boxes use `[x0, y0, x1, y1)`; they are diagnostic regions, not exclusive segmentation masks. Boxes can overlap where the painted limbs overlap.

| Frame | P: persistent leg/boot | T: disappearing tucked-leg cue |
| --- | --- | --- |
| 02 | Upper-right knee around `[47,54,58,63)` leads to the rightmost brown boot in `[54,60,70,74)`. | The lower central dark trouser lobe in `[37,59,51,74)` has a separate brown cuff/lower-leg region in `[47,65,56,73)` and lower boot in `[50,70,64,77)`. The second boot is visibly brown even though it overlaps P. |
| 03 | Knee around `[48,42,59,52)` and the continuous diagonal trouser mass lead to the large rightward brown boot in `[53,49,69,65)`. | No separate T boot is painted. At the lower end of the body, `[35,57,48,67)` contains teal hem, dark trouser/outline pixels and transparency, with no brown cuff/boot cue. The adjacent dark mass reads as P's uninterrupted thigh, not a second folded leg. |
| 04 | The right-side knee and brown boot occupy roughly `[43,48,58,66)`. | A distinct left-side knee returns in `[30,47,43,56)`, with brown cuff and boot in `[30,53,41,67)`. This is the reappearance the intervening drawing must prepare. |

The disappearing marker is therefore **the second brown cuff/boot together with a distinct short trouser continuation**, not just a gap between feet. The teal pointed hem at the low left of the hips is not a substitute for that leg. Full occlusion can be anatomically possible, but this drawing removes every strong cue at once; the human playback report establishes that this occlusion is not communicating successfully here.

## Smallest drawing repair to try

**Change frame 03 only first. Expose a small connected portion of T under/behind the existing diagonal thigh.** Keep P's existing knee, shin and rightward boot, the planted hand, the upper body and the frame placement intact.

Suggested initial editable region: **`[35,55,47,67)`**, a 12 × 12 native-pixel patch at the low hip/thigh end. This is a bounded starting experiment, not a demand to fill every pixel in that box.

1. Clarify a short folded trouser continuation within **`[36,56,43,63)`**, using the existing dark lower-body mass. A compact contour/value change should show that one portion turns behind the dominant diagonal thigh. Do not draw a second full long thigh parallel to P.
2. Connect a small brown cuff/heel to that continuation around **`[38,61,43,65)`**, then allow a short boot tip or heel edge to remain visible within **`[39,63,47,67)`**. Preserve an actual dark trouser-to-brown cuff connection. An isolated brown island attached only to the teal hem would trade the disappearing leg for a detached foot.
3. Let the existing diagonal thigh occlude most of T. The aim is one restrained second-foot marker and a credible attachment, with its position anticipating the left-side boot in 04. Retain the teal garment edge as cloth overlapping the limb; do not repaint the garment into an entire extra leg.

This places the small visible boot between the lower central boot in 02 and the under-body/left-side boot in 04. The required benefit is **continuity of ownership**, not a perfectly stationary foot or mirror symmetry. A tucked boot can move in depth and legitimately overlap the other leg.

If a cuff/boot peek in that patch cannot be attached convincingly, expand only the folded-leg contour a few pixels toward the hip; do not add a standalone shoe elsewhere to satisfy a two-boot count. The key check is whether a viewer can trace *two connected leg roles* through 02→03→04 without any frame appearing to grow a third limb.

## Recheck after the repair

- Show 02→03→04 at native and 2× on both supplied backgrounds, then the unchanged full 1.2-second action at normal speed. The user’s playback judgment is the acceptance evidence still needed.
- Check that T's brown cue survives at native scale and that its dark trouser connection is visible or clearly occluded, rather than floating.
- Count body-connected limb routes, not detached color blobs: P should remain unchanged and T should gain a continuous cue.
- Keep the 200 ms hold while comparing the drawing repair. Shortening 03 merely to hide the missing cue would not establish that the drawing has been repaired.

I also rechecked A's complete pose sequence. The other posed stages retain a readable second knee, leg, or boot cue consistent with their neighbours; 03 is the clearest complete loss of the secondary lower-body marker. This does not certify every other transition under continuous playback.

## Evidence and independence

This follow-up used the unchanged anonymous A packet and the parent-provided quotation of human feedback. No mapping, source implementation or production asset was opened or changed. The images `followup-02-03-04-light-4x.png` and `followup-02-03-04-dark-4x.png` are diagnostic nearest enlargements with native coordinate ticks; they are not repaired candidates and do not replace the native-scale inspection.

`followup-human-rejection-freeze.json` binds this follow-up and the diagnostic images to the numbered source frames. The original `REVIEW.md`, its scores and its original freeze were not overwritten.
