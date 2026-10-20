# Brann diagonal walk review

**Verdict:** Recognizable and attractive prototype set. I would repair the lower-body continuity, front arm/body resets and rear costume continuity before treating the four diagonals as finished locomotion. This conclusion comes from the visible drawings and ordered pairs; continuous playback and planted contact remain unverified.

## Separate ratings

Scores are subjective visual judgments on a 0–10 scale, with no supplied target. Overall scores are holistic judgments, not an arithmetic average. Hashes, diagnostic sheets, maps and work effort receive no art credit.

| Direction | Appearance | Identity | Motion readability | Practical usefulness |
|---|---:|---:|---:|---:|
| southeast | 7 | 8 | 5.5 | 6 |
| southwest | 7 | 8 | 5.5 | 6 |
| northeast | 6.5 | 8 | 5 | 5.5 |
| northwest | 6.5 | 8 | 5 | 5.5 |
| **Overall** | **7** | **8** | **5** | **6** |

- **Appearance:** Visible silhouette, drawing and material volume. Attractive rounded rendering; lower-body mass/hip defects reduce consistency.
- **Identity:** Recognizable hair, beard/face, gold armor and navy outfit; rear belt-strip omission prevents a higher score.
- **Motion readability:** Walk-like changes and some readable lift/sole cues; ambiguous branch continuity and abrupt changes weaken alternating support/swing. This rates ordered still/pair evidence, not observed playback.
- **Practical usefulness:** Useful as a recognizable prototype set at the small draw scale; affected leg/arm clusters and rear costume need repair and an engine playback/contact test before final locomotion sign-off.

## Verified scope and perception limits

All **73 listed PNG hashes match**: 32 nominated keys, 40 cardinal-context images and one reference. The 32 nominated frames are 128×128 RGBA. The input card and manifest hashes are in review.json; individual PNG verification is in input-verification.json. Inputs were not modified. No producer methods, other reviews or parent history were read.

Inspected **all 32 keys and all 32 cyclic pairs, including each 07→00 wrap**, on light (#e6e4d9), dark (#1b1e27) and muted ground (#5e603f), at 128px native, nearest 256px and nearest 84px intended-game approximation. This is 288 key-condition exposures and 288 pair-condition exposures. Those counts establish review coverage only.

- This is a cold static image review: every ordered key and cyclic pair was visually inspected; no continuous animated playback was observed.
- Each supplied hold is 9/160 seconds (56.25 ms); eight holds total 0.45 seconds, approximately 2.22 cycles/second. Still sheets cannot establish the actual cadence, perceived hitch severity, temporal persistence or repeated-loop fatigue at this speed.
- No moving ground, world translation, engine camera, sampling configuration, collision shape or in-game scale transform was supplied. Ground contact, foot sliding, root speed and whether an apparent support foot truly stays planted therefore remain unverified.
- An occluded leg can be correct. The observations describe visible branch evidence and do not infer correct limb identity from labels, symmetry, file order or intended pose roles.
- 84x84 nearest-neighbor stages represent rounded 128*0.66=84.48 sampling. A real subpixel .66 transform or other filtering can look different. All stage-scale inspection uses nearest-neighbor resampling; the ground background is a flat muted ground color, not a textured game scene.
- Cardinal walks and idles and the reference were used only for identity and turn context. No runtime directional transitions or idle-entry sequence were observed.

## Drawing, identity and scale

The strongest work is above the belt: readable rounded hair, compact brow/eye and beard shapes, bright convex pauldrons, layered bracers and a coherent navy/gold/brown palette. Armor highlights maintain material volume on all three backgrounds. The figure remains recognizable at the small game draw; the foot action is much less readable than the identity. The lack of a ground shadow in these transparent frames is not itself scored as an art defect.

Light backgrounds expose the angular hip contours most clearly. Dark backgrounds weaken the hair edge, trouser outline and overlapping boots, though the face and metal still identify the figure. The muted ground supports the costume palette, but does not rescue foot separation in the compressed poses. Enlarging to 2× reveals contour/volume problems; it does not add source detail.

## Exact defects and smallest useful repairs

### F1 — Lower-body ownership is ambiguous through both half-steps (high)

**Evidence:** southeast, southwest, northeast, northwest; keys/pairs 02, 03, 04, 05, 06. Approximate native region x=40–89, y=77–113. Front 03/05 compress the two boots into a nearly single column; front 06 adds a round far thigh without a clearly readable full lower branch. Rear 02/06 show a large sole while the other complete leg largely disappears; rear 03/04 then stack the boots. Neither occlusion alone nor a dark sole proves a defective gait, but these combined changes prevent confident tracing of two alternating anatomical branches.

**Effect:** Walk-like activity is visible, but alternating support/swing is not clearly established by the visible anatomy. At .66, the overlap becomes a single brown/dark cluster.

**Smallest repair:** Redraw the affected lower-body clusters, preserving a stable hip origin and trouser-to-calf width for each visible branch. Keep one small toe/heel or negative-space cue for the other branch in the passing poses; then make the second half-cycle a clear reciprocal action. Preserve the head and armor.

### F2 — Front 03>04 and 05>06 reset arm span and body width (high)

**Evidence:** southeast, southwest; keys/pairs 03>04, 05>06. Approximate native region x=27–102, y=47–86. SE near arm jumps out toward screen-left between 03 and 04; SW near arm jumps out toward screen-right. Chest and hip silhouette broaden simultaneously. The near arm opens again 05>06. The head facing stays much steadier, so body width changes dominate.

**Effect:** Static sequence suggests repeated pops or a direction wobble at 56.25 ms holds; exact playback severity remains untested.

**Smallest repair:** Adjust 03/04 and 05/06 near-arm positions and chest edges into an ordered arc with the same three-quarter chest volume. Do this while repairing the boot overlap, without adding extra keys or polishing every surface.

### F3 — Rear lifted-leg poses have squared hip/trouser flaps (medium)

**Evidence:** northeast, northwest; keys/pairs 02, 06. Approximate native region x=43–87, y=77–94. NE has a squared dark-gray projection on screen-right beneath the tunic; NW has the corresponding visible projection on screen-left. The contour expands laterally and does not give a convincing rounded hip-to-thigh-to-calf connection.

**Effect:** Especially clear on light/ground and at 2x; still a jutting dark shape at .66. It weakens both material volume and boot attachment.

**Smallest repair:** Round and reconnect the trouser mass into the lifting leg, retain consistent gold-edged tunic hem thickness, and expose a small coherent opposite support cue. Repair 02 and 06 together with F1.

### F4 — Rear costume hanging strip disappears on diagonal turns (medium)

**Evidence:** northeast, northwest; keys/pairs 00-07. Approximate native region x=57–76, y=67–92. The rear reference and cardinal north idle/walk show a conspicuous orange hanging strip below the belt. Both rear diagonals instead show an uninterrupted navy/gold lower-back panel and no comparable orange strip across the supplied keys.

**Effect:** Same person remains recognizable, but a costume feature vanishes when turning from north to a rear diagonal.

**Smallest repair:** Restore the orange hanging strip with appropriate three-quarter placement and occlusion, keeping it on a consistent attachment to the belt.

### F5 — Dark small-scale leg separation is weak (low)

**Evidence:** southeast, southwest, northeast, northwest; keys/pairs 02-06. Approximate native region x=40–89, y=78–113. At 84px stage on the dark background, brown boots, dark trousers and their internal outlines merge, especially front 05 and rear 03-06. Gold shoulders continue to read clearly.

**Effect:** Player identity survives better than footfall readability. This amplifies F1 rather than being a separate reason to replace the palette.

**Smallest repair:** After correcting shapes, retain a short warm rim or negative-space seam at the overlapping boot edges. Avoid a global bright outline or wholesale recoloring.

## Entry and turn compatibility

- **Identity:** Front diagonal face/hair/beard and gold/navy/brown/rust palette are compatible with south/east/west context. Rear head/pauldrons identify the same actor, with a missing orange hanging strip compared with north/reference.
- **Direction:** SE/SW and NE/NW face the expected quadrants. Torso narrowing in 02/03 versus widening in 04 can make facing feel unstable within a diagonal loop.
- **Entry:** Wide split poses 00/07 and narrow passing poses 02/03 have different foot extents. Idle-to-walk entry at an arbitrary key may visibly jump; exact severity requires an engine phase/entry test.
- **Turns:** Shared 128px stage and listed pivot provide a reference for comparison, but do not prove matched contact. Same-index cardinal/diagonal poses do not guarantee the same anatomical foot phase. Turn after a clearly planted pose once branch continuity is repaired; verify both directions of each adjacent turn.

## All-key ledger

“Left” and “right” below mean **screen-left and screen-right**, not anatomical identity. Pose indices establish chronology only. The notes describe the visible progression and do not assume the concealed anatomy is correct. All nine scale/background conditions were inspected for every key; scale/background effects are summarized above.

### southeast

- 00: Clear split: screen-left boot curls behind; screen-right boot has a broad outward toe. Sturdy torso and readable face.
- 01: Screen-left boot tucks upward/inward; screen-right shin remains broad. Identity and rounded metal remain coherent.
- 02: Torso becomes narrow; small screen-left boot sits directly below the glove while the other boot also shrinks. Two branches remain visible but their volume decreases.
- 03: Boots almost share an axis beneath the belt; a small brown branch crosses behind the larger toe. This is a hard pose from which to identify the supporting leg.
- 04: Chest and arms open abruptly. Curled boot remains behind the central shin; the visible shin/toe points down-right. Lateral arm spread is large compared with 03.
- 05: Lower body reads predominantly as one narrow central boot with a small oblique brown overlap above it. The second branch is difficult to follow.
- 06: Broad central boot is under a thick near trouser leg; a rounded dark thigh projects on the screen-right side without an equally clear complete calf-to-boot path.
- 07: Split returns: curled boot on screen-left, long angled boot on screen-right with a darker end/sole. Clearer two-leg silhouette than 05-06.

### southwest

- 00: Clear split: broad screen-left outward toe, curled screen-right boot. Face, beard and armor read well.
- 01: Screen-right boot tucks upward/inward while screen-left shin stays broad. Rounded volumes remain convincing.
- 02: Body becomes narrow; small screen-right boot is directly below the near glove; screen-left boot is reduced. Leg count remains visible but thickness changes.
- 03: Boots converge beneath the belt, with a small crossing brown branch beside the main toe. Supporting-leg identity is ambiguous.
- 04: Chest and arms open, particularly the screen-right near arm. Curled boot overlaps behind the central shin. The increase in arm span is conspicuous after 03.
- 05: Mostly one narrow central boot and an oblique brown overlap. Separate support/swing anatomy is difficult to read.
- 06: Thick central trouser/boot with rounded dark thigh projecting screen-left. Complete attachment of the hidden boot is unclear.
- 07: Broad split returns: long angled screen-left boot and curled screen-right boot. Toe/sole orientation differs from 00.

### northeast

- 00: Clear screen-left extended boot and smaller bent screen-right boot. Back view and shoulder armor identify the character.
- 01: Screen-left boot rotates to show a dark sole, with the other boot still visible on screen-right. This is a readable lift/recovery cue.
- 02: Large central/left-facing sole; opposite boot is almost lost. Squared dark-gray projection at screen-right hip/trouser edge reads as a flap rather than a rounded connected thigh.
- 03: Narrow body and close boots: a thin brown branch on screen-left sits beside the larger screen-right boot. Clear support ownership is lost.
- 04: Two boots remain stacked closely; a small bent screen-left boot is above/behind the broad lower screen-right boot. Leg separation is weak.
- 05: Two boots sit low and close with a thin central gap. Volume is more coherent than 02, but support versus swing is still hard to tell.
- 06: Prominent central sole and small boot beside it; squared screen-right hip/trouser projection returns. Distinct second leg path is weak.
- 07: Wide split returns with screen-left extended boot and screen-right bent boot. Clearer silhouette, but a large change from 06.

### northwest

- 00: Clear screen-right extended boot and smaller bent screen-left boot. Back silhouette and armor retain the character identity.
- 01: Screen-right boot rotates to show a dark sole; screen-left boot remains visible. Readable lift/recovery cue.
- 02: Large central/right-facing sole; opposite boot is almost lost. Squared dark-gray projection at screen-left hip/trouser edge looks like a flap.
- 03: Narrow torso and close boots: thin brown branch on screen-right beside the larger screen-left boot. Supporting-leg identity is ambiguous.
- 04: Boots remain closely stacked; small bent screen-right boot is above/behind the broad lower screen-left boot. Weak leg separation.
- 05: Two boots low and close with a thin gap. More coherent volume than 02, but contact ownership remains unclear.
- 06: Central dark sole with a small neighboring boot and squared screen-left hip/trouser projection. Second continuous leg branch is hard to follow.
- 07: Wide split returns: screen-right extended boot, bent screen-left boot. More readable, but much wider than 06.

## All cyclic-pair ledger

Each pair was inspected side-by-side in all nine conditions. A “pop” or “reset” here describes a discontinuity in the ordered drawings; whether it actually hitches in continuous playback is a hypothesis requiring playback.

### southeast

- 00>01: Screen-left boot tucks while the broad screen-right boot stays similar; modest, readable change.
- 01>02: Both lower-body width and boot size contract; screen-left arm moves inward. Some narrowing is plausible yaw, but material volume becomes inconsistent.
- 02>03: Boots converge/cross beneath the belt. A visible movement exists, but the branch that should carry weight cannot be identified confidently.
- 03>04: Largest front-view discontinuity: near arm opens to screen-left and chest/hip width increases at once. Reads as a pose reset rather than a clear continued swing.
- 04>05: Curled rear boot collapses into the central overlap; lower body loses a readable second branch.
- 05>06: Rounded far thigh appears screen-right and the near arm opens again. Changed overlap and boot mass obscure the anatomical handoff.
- 06>07: Legs reopen abruptly into a wide split and angled screen-right toe. A second leg is clearer, but its path through the preceding pose is weak.
- 07>00: Reasonably close split silhouettes; main visible difference is angled/downward boot end becoming a broad outward toe. Less disruptive than 03>04; not perfectly identical contact.

### southwest

- 00>01: Screen-right boot tucks while broad screen-left boot stays similar; modest, readable change.
- 01>02: Lower body and boots contract while the near screen-right arm moves inward. Volume narrows more than a simple boot swing.
- 02>03: Boots converge/cross beneath the belt; visible motion, but no confident support-leg assignment.
- 03>04: Chest and near screen-right arm open sharply together. Strong pose-reset impression.
- 04>05: Rear curled boot collapses into the central overlap, weakening the second branch.
- 05>06: Rounded far thigh appears screen-left while near arm opens again. The anatomical handoff is difficult to track.
- 06>07: Wide split and angled screen-left boot return abruptly. The preceding pose does not clearly establish that boot path.
- 07>00: Similar split silhouette; angled boot end becomes a broad outward toe. Relatively mild wrap change compared with internal resets.

### northeast

- 00>01: Screen-left extended boot rotates to a dark sole while screen-right boot stays visible. One of the clearest swing cues.
- 01>02: Opposite boot largely disappears and the squared screen-right hip projection enters. A full supporting branch is no longer readable.
- 02>03: Central sole reduces/turns into a thin adjacent brown branch as a broad screen-right boot dominates; torso also narrows. Attachment continuity is weak.
- 03>04: Closely stacked boots change overlap; no clear, visible weight transfer. Arm/chest width reopens somewhat.
- 04>05: Screen-left boot drops beside the other boot; small gap improves leg count, though support versus swing is uncertain.
- 05>06: Large central sole and squared screen-right hip projection arrive together. Hidden support branch is difficult to locate.
- 06>07: Close sole/boot cluster opens abruptly into a wide split. Major silhouette change without a clear intermediate leg path.
- 07>00: Similar wide split, extended screen-left boot and bent screen-right boot. Mild upper-body/foot change; the wrap is among the least concerning pairs.

### northwest

- 00>01: Screen-right extended boot rotates to show a dark sole while screen-left boot remains visible. Readable swing cue.
- 01>02: Opposite boot largely disappears and squared screen-left hip projection enters; support branch cannot be followed confidently.
- 02>03: Central sole contracts/turns beside a broad screen-left boot while torso narrows. Attachment continuity is weak.
- 03>04: Closely stacked boots change overlap without a readable visible weight transfer. Upper-body width opens somewhat.
- 04>05: Screen-right boot drops beside the other boot; narrow gap helps leg count, but not support/swing certainty.
- 05>06: Large central sole and squared screen-left hip projection appear. Opposite continuous support branch is unclear.
- 06>07: Close boot cluster abruptly reopens into a broad split. Large silhouette change with weak leg-path evidence.
- 07>00: Similar broad split with extended screen-right boot and bent screen-left boot. Wrap change is mild relative to internal transitions.

## Smallest useful repair pass and acceptance check

1. Repair connected lower-body silhouettes in 02-06, especially 03/05 front and 02/06 rear; make both half-steps visibly reciprocal.
2. Blend front near-arm/chest spans at 03>04 and 05>06 while retaining the existing face and armor.
3. Restore rear orange hanging strip and clean the squared trouser projections.
4. Check repaired eight-key loops at actual 56.25 ms holds, first pinned to stage then translated over a ground grid at the intended in-game speed; test idle entry and adjacent cardinal turns. Adjust contact/timing only from that playback evidence.

A useful pass preserves the successful face, hair, armor, palette and overall compact scale. It redraws the affected limb clusters and missing rear costume feature. Do not spend the first pass adding texture or extra keys. After repairs, actual repeated playback must establish alternate left/right support, sensible contact, tolerable loop cadence and turn/entry behavior; this still review cannot certify those outcomes.

## Frozen evidence

The diagnostics directory contains 12 all-key sheets and 12 all-pair sheets (four directions × three scales), cardinal context, turn/identity context, four coordinate strips and a lower-body enlargement. The nearest 4× crop is diagnostic only and is not an intended display condition. review.json contains the same ratings, findings, exhaustive ledgers, scope and limitations in structured form. SHA256SUMS freezes all report/diagnostic files other than the checksum file itself.

Frozen UTC: 2026-10-16T19:02:37.848769+00:00
