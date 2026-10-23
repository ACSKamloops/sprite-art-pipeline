# Frozen independent baseline review

**Scoped overall judgment: 7/10.** The supplied ten drawings communicate a recognizable get-up, with coherent character identity and attractive shaded costume volumes. The opening has weaker leg tracking than the later crouch-to-stand phase. On the supplied fixed 80 × 80 canvases, the largest demonstrated continuity problem is the abrupt movement of the apparent ground contacts at 02→03. I would use this as a promising action needing a registration check and a small opening comparison, rather than certify it as finished motion.

This is a still-based chronology assessment, not continuous playback. Ratings apply only to these inputs and known holds, not game feel, other animations, or an unseen runtime compositor.

## Scope and independence

Reviewed `inputs/chronology.png`, every numbered input `00.png` through `09.png`, and the subsequently nominated `inputs/boots-grid.png` coordinate diagnostic. The latter shows frame 02 only and introduced no candidate art or scores. No earlier reviews, producer notes, source mappings, state files, or candidate images were opened. The rubric was the nominated anonymous sprite review card.

`source.json` was accessed programmatically for frame holds. The timing extractor also printed the clip's declared total duration, 1.2 s; this is the same as the sum of the holds and exposed no qualitative assessment. No other source metadata was consulted. This report was frozen before consulting any other materials.

Input SHA-256 values are retained in `input-fingerprints.json`, including the late coordinate diagnostic. The report's companion timeline is `review-timeline.json`. Native coordinates below use each original 80 × 80 image, origin at its top left, x rightward and y downward; quoted coordinate boxes are approximate inclusive visual regions unless identified as exact support rows.

Reviewed every pose at native size and 4× nearest-neighbor enlargement on dark charcoal RGB(39,44,51) and warm light RGB(235,232,217). The opening was additionally inspected at 6× with coordinate grids and 8× with exterior rulers. The supplied chronology was also viewed. Enlargements clarify pixel ownership but do not substitute for the native-size judgment. These are composites of the supplied pixels, not new drawing or interpolated frames.

## Ratings

| Dimension | Score | Evidence and limit |
|---|---:|---|
| Drawing, material, anatomy | 8/10 | Face, hair, scarf, tunic, bracers, trousers and boots retain distinct shaded volumes. The crowded legs remain anatomically plausible; no definite extra limb or detached ankle is demonstrated. |
| Motion and readability | 6/10 | The overall stages are clear. Opening leg roles are harder to follow, and the raw-canvas 02→03 contact jump is conspicuous. Actual normal-speed smoothness has not been observed. |
| Temporal identity | 8/10 | Hair mass, face direction, scarf, sleeve trim and belt remain recognizable. The final turn and settling do not demonstrate a character-identity failure. |
| Practical use | 6/10 | Suitable to take into a one-shot runtime review. Common ground registration and the exit into the actual idle need checking. No clipping or conspicuous matte halo was seen on either background. |

The overall score is a scoped judgment, not a mathematical average or a production acceptance threshold. The registration finding could be resolved by unseen runtime offsets; if so, this packet alone understates practical use.

## Material findings and smallest useful experiments

### 1. 02→03 moves both apparent support contacts upward together

**Demonstrated in the raw input canvases; high confidence.** In 02, the planted screen-left palm reaches native row **74**, while the boots reach row **76**. In 03, the palm reaches row **63** and the boot row **64**. The palm is approximately x17–28 in both frames; the visible boot shifts only modestly horizontally. Thus the contact pair jumps upward by **11–12 px** at t=0.425 s, while the action still depicts a hand-supported seated/push-up stage. This is large at an 80-pixel canvas scale. It reads as a change of placement rather than solely a change in body articulation when the frames share their canvas origin.

**Smallest experiment:** in a diagnostic compositor, shift 03 down by 11 native pixels and compare only 02→03 at the supplied holds. Do this before redrawing anatomy. If that restores continuity, inspect the supplied anchors or registration across the remaining sequence before choosing final offsets. The one-pixel difference between palm and boot rows need not be forced away. Do not blindly apply this single-frame change to production: 03→04 then also needs a contact-path check.

**Expected benefit:** keeps attention on the torso raising and legs gathering, rather than a sudden upward translation of the support plane.

**Limit:** no runtime anchor, root movement, perspective floor, or collision behavior was available. If the engine already supplies compensating offsets, this is a diagnostic-packet placement issue rather than a drawing defect.

### 2. Opening leg ownership is briefly under-described in 01

**Visible ambiguity; medium confidence as a repair priority, not evidence of impossible anatomy.** In 00, a raised dark knee around x44–56, y48–59 sits above the lower trouser mass. In 01, the lower body compresses into one dominant trouser/boot silhouette: the knee/thigh around x44–57, y59–70 and the cuff/foot around x55–74, y63–75. In 02, two bent legs and two feet become much easier to separate. The sequence therefore reads as bent/overlapping → extended/strongly overlapped → tucked, while the head and torso rise more steadily.

The 01 overlap is physically possible. I do **not** infer that a leg disappears anatomically, and I would not prescribe a full redraw from these stills. At native size, however, it is hard to maintain confidence about which boot in 00 becomes which boot in 02 through that middle drawing.

**Smallest experiment:** make a separate 01-only candidate that preserves the existing pose and outer foot silhouette but clarifies one already intended leg-overlap boundary in the trousers/cuff junction, approximately x48–62, y60–70. Start with a short value/edge distinction, assessed at 1×; do not add an arbitrary extra toe. Compare 00→01→02 before considering any silhouette or knee-position change. If the clarified edge does not improve the native reading, keep the original rather than accumulating lines.

**Expected benefit:** allows the viewer to track two leg roles through the prop-up pose without replacing the action or its style.

**Preference, not defect:** a version that keeps the knees tucked through 01 might be more compact, but the existing extend-then-gather action is plausible. I cannot justify mandating that pose change from this packet alone.

### 3. Frame 02's boot overlap does not establish a broken ankle or extra boot

This is a specific non-finding because the region is visually crowded. The lower/front trouser branch meets the brown boot/cuff in approximately x47–55, y64–71; the lower boot then continues into the sole at x51–62, y72–76. The upper/right leg meets its cuff near x55–61, y60–65, and its boot reaches the separate rightward toe around x65–70, y65–71. The dark overlap around x55–59, y66–72 supports an occlusion reading. The contrast diagnostic makes these connections easier to inspect.

At 1× the brown cluster is dense, but the pixels support two overlapping boots. There is no confident anatomy repair to prescribe here. A stronger seam would be a readability preference and should be judged in an isolated candidate; it could also over-outline an otherwise valid overlap. Do not enlarge the repair area into the whole leg without a demonstrated improvement.

## Full chronology, exposure and boundaries

The supplied holds sum to **1.2 s**. These are ten held drawings; no supplied interpolation or actual video presentation timestamps were available. The following start/end times are reconstructed from the frame holds.

| Frame | Interval in seconds | Pose / predecessor-current assessment |
|---|---:|---|
| 00 | 0.000–0.100 | Reclined, curled start. Identity and material volumes read; overlapping legs are plausible. Left hair lies close to the canvas edge (x1) but is not visibly cut off. |
| 01 | 0.100–0.250 | 00→01: head and torso prop up and the arm relocates into support. The leg extension and stronger overlap weaken role continuity, as described above. No definite joint separation is visible. |
| 02 | 0.250–0.425 | 01→02: torso rises further and legs gather. Palm support stays at row 74. Two boots become readable; their crossing is plausible rather than proof of an extra foot. |
| 03 | 0.425–0.625 | 02→03: support-plane translation dominates the raw-canvas change. One boot is now occluded by the side-on leg arrangement; occlusion alone is not a missing-limb defect. |
| 04 | 0.625–0.725 | 03→04: both feet gather beneath the body into a crouch; the free forearm becomes visible over the knee. The change is large but directionally coherent as a held key pose. |
| 05 | 0.725–0.825 | 04→05: a higher crouch with hand support retained. Clear preparation for standing; no material identity failure observed. |
| 06 | 0.825–1.025 | 05→06: hand leaves the floor and the body extends into a forward-leaning half-stand. Readable support transfer. The 0.2 s exposure makes this an emphasized stage, not an in-between. |
| 07 | 1.025–1.0875 | 06→07: reaches near-full height; arms settle alongside the torso. Clear continuation of the rise. |
| 08 | 1.0875–1.150 | 07→08: small downward settling and stance adjustment. No new confident drawing defect. |
| 09 | 1.150–1.200 | 08→09: a more frontal, narrower resting stance and further settling. Plausible exit key; the actual following idle is absent, so the exit cannot be certified. |

The 09→00 wrap is a hard standing-to-ground reset. That is expected in a repeated preview of a one-shot get-up and is not, by itself, a defect in the action. It would be unsuitable as a seamless loop. The frame 00 incoming transition and frame 09 outgoing transition were not supplied.

The long 03 and 06 holds may make the rise feel deliberately segmented; this is a timing hypothesis requiring continuous playback, not a demonstrated fault. I would resolve contact registration and compare the small 01 candidate before changing timing. More frames or different holds would not by themselves improve the underlying drawings.

## Perception limits and preservation

I reconstructed chronology from stills, native-scale contact sheets, enlargements and known holds. I did not observe uninterrupted video, actual frame presentation timestamps, controller response, in-game ground contacts, or the camera. I cannot certify physical foot lock or distinguish intentional world movement from unprovided anchor offsets.

The most defensible first action is the 02→03 placement check. The lowest-risk art experiment is limited to leg-overlap clarity in 01. Preserve the recognizable face, hair, tunic, scarf, materials and the already plausible frame 02 boot connections. New art or timing requires a new scoped comparison; this report does not automatically transfer to any revision.
