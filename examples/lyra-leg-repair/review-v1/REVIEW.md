Candidate-v1 improves boot rendering, but the leg exchange is not resolved. Continue the bounded repair, prioritizing passing poses 3 and 7 before treating this as a successful walk correction. This is a history-aware review, not blind review or continuous playback acceptance. No score is assigned.

Viewed the full character at native scale, every source/candidate frame, every adjacent lower-body pair, and the 7->0 wrap. The portrait remains the appearance reference. Brown leather shading, boot shaft bands, and toe highlights generally look steadier than the source; the preserved face, tunic, scarf, gloves, and silhouette retain the character. Better individual boots have not yet produced a consistently readable chain from thigh through cuff to foot.

Concrete corrections, in original 128x128 coordinates

1. **Frame 3 passing connection:** approximately x54..81, y81..99. The screen-left trouser mass bends toward the central/front cuff while the other upper thigh also terminates in that region. The boot behind at about x53..65, y91..105 lacks a clear visible connection. In 2->3->4 the leg branches become difficult to follow, producing a knotted/crossed reading rather than an intentional passing pose. This is visible-paint ambiguity, not a claim to have recovered hidden joints. Establish which thigh owns each cuff and a legible front/behind overlap before refining the leather.

2. **Frame 7 toe and wrap:** approximately x77..98, y91..111. The screen-right boot becomes longer and nearly side-on compared with the rounder three-quarter boots elsewhere. The 6->7 transition introduces this shape abruptly; 7->0 pulls it inward and down again. Preserve the boot's substantial rounded volume and make the returning/passing leg progress into frame 0 without that isolated long-toe excursion. Review both edges together after repair.

3. **Opposite-phase thigh/shaft proportions:** frames 0..2 expose a long, bulbous screen-right trouser/cuff column around x67..81,y81..96; frames 4..6 use a much shorter, squat screen-left column around x55..68,y82..92. The visible lower edge is around y116 in the first group and y111 in the second. The source phase extremes 0 and 4 had more comparable reaches. This is not a request to force equal sole screen-y or invent contact: check whether the opposite-phase thigh/shaft has been unintentionally shortened while upper-body height stays similar. Keep perspective differences, but avoid changing the apparent leg volume to solve overlap.

4. **Small silhouette changes need a clear phase purpose:** frames 0..2 retain the same screen-right-leading arrangement; 4..6 retain the screen-left-leading arrangement. All eight candidate frames are different images. A foot can remain in a stance phase for several exposures, so this is not evidence of duplicate holds or a reason to insert equal-distance inbetweens. The concern is that those small changes currently lead into unclear passing poses 3 and 7. Repair those transitions before changing the existing 56.25 ms clock.

Pair coverage

| Pair | Observation |
| --- | --- |
| 0->1 | Same lead arrangement; toe/cuff shape changes more than the leg relationship. |
| 1->2 | Rear boot/trouser changes modestly; still readable as the same half-step. |
| 2->3 | Thigh/cuff branches converge into the ambiguous passing connection. |
| 3->4 | Front/behind assignment switches without a clean readable leg bridge. |
| 4->5 | More consistent short front boot/shaft; small phase change. |
| 5->6 | Similar front boot persists; requires the next passing pose to explain the exchange. |
| 6->7 | Long side-on right toe and wide separation appear abruptly. |
| 7->0 | The right boot retracts inward/down while the other boot tucks back; inspect as one coupled transition with 6->7. |

Bounded preservation and cleanup

Independent pixel comparison confirms exact RGBA preservation at all y<78 and outside each supplied edit mask for all eight frames. The clock metadata remains eight exposures of 9/160 seconds, total 9/20 seconds. These are mechanical preservation checks, not an art/motion pass. No producer file was edited, locked, or frozen by this review.

There are also scattered alpha=1 pixels far outside the character, for example frame 0's positive-alpha extent reaches x7..125 while alpha>=8 stays within x33..91. These are visually minor and are not the gait defect, but can corrupt later positive-alpha trimming/bounds. Remove confirmed isolated background residue after the pose repair; preserve intentional soft edges rather than applying a blanket threshold.

Evidence is in FULL-NATIVE-ORDER.png, the source/candidate lower-detail and complete-pair sheets, and CANDIDATE-COORDINATE-WITNESSES.png. REVIEW-INPUTS.json records the reviewed frame hashes; it identifies this candidate revision and does not prevent continued producer changes. No continuous video perception, world foot locking, or finished-animation acceptance is claimed.
