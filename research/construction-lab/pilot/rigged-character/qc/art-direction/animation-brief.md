# Replacement animation brief — original four-direction pixel character

Keep the original character identity, but establish a stronger pixel-art body model and a deliberate walk. Draw a coherent front, back, right and left turnaround first, at the intended native resolution. Agree the hood/head, neck, shoulder, ribcage, pelvis, thigh, calf, glove and boot volumes before animating. Use one ground projection and one perspective convention. The side pair may mirror only if equipment, lighting and costume asymmetry permit it; front/back require authored shapes.

## Eight designed key poses per direction

| Pose | Body and feet | Opposing arm and overlap |
|---|---|---|
| 1. A contact | A heel/front sole arrives ahead; B finishes its rear support. Pelvis between the feet, not permanently crouched. | B hand forward, A hand back; clear near/far overlap. |
| 2. A down | Weight settles onto A; modest knee/hip compression and controlled head drop. B releases support. | Opposing swing continues; shoulder/pelvis rotate subtly against each other. |
| 3. A passing | B passes the planted A leg, with visible clearance and an intentional knee shape. | Hands pass neutral; changing overlap explains which limb is nearer. |
| 4. A up | A extends through late stance; B travels forward with a readable raised heel/toe. | B leg forward pairs with A hand forward; torso rises without stretching its volume. |
| 5. B contact | Exchange limb roles; preserve the same stride, masses and ground convention. | Reverse the phase relationship, not the character's identity. |
| 6. B down | Weight settles on B; A releases. | Counterrotation and silhouette remain readable. |
| 7. B passing | A passes B with the opposite leg clearly supporting the body. | Near/far overlap changes intentionally. |
| 8. B up | Finish the second stance and prepare the next A contact. | Loop into pose 1 without a silhouette, volume or stance jump. |

For front/back, place those same *actions* in the chosen depth projection: the incoming foot is drawn nearer/farther, the swing boot shows appropriate top/sole exposure, and thigh/calf overlap changes. Do not reuse side soles or a single horizontal ground-row test for depth motion. Keep head/body scale and costume volumes consistent throughout the cycle; use purposeful cluster redraws where rotations would otherwise make jagged rods.

Start with eight discrete designed frames, not 60 interpolated rig samples. A provisional full cycle of 48 authored ticks at 60 Hz gives two steps in 0.8 seconds; initially use six ticks per key pose, then adjust compression/passing holds only after native-size timed viewing. Bind world travel to the approved planted-foot displacement. Timing and stride are a review choice, not a universal anatomical rule. Add in-betweens only when they improve a demonstrated silhouette or contact transition.

## Gates before expanding the library

1. **Turnaround:** review a fixed-scale native 1× and nearest 3× sheet. The four views must read as the same solid character, with credible front/back anatomy and equipment attachment. Reject inconsistent body volumes or side pieces masquerading as depth views.
2. **Pose sheet:** identify all eight phases without labels from silhouette and support leg alone. Check contralateral hand/leg progression and near/far overlap. Reject ambiguous support, repeated crouching poses, rubber joints or disappearing limb mass.
3. **Timed cycle:** view at authored speed for at least three cycles in-place and moving in the intended ground projection. Include first/last adjacent frames. Reject shuffling, skating, foot snaps, unexplained head bob, volume flicker or a loop hitch; slow-motion alone is insufficient.
4. **Pixel clusters:** inspect every key and adjacent pair at native size, then enlarged nearest. Reject isolated contour noise, crawling diagonals, broken hands/boots and shading that changes volume accidentally. A palette or pixel-count threshold cannot approve cluster quality.
5. **World contact:** after the art passes, measure each view's actual boot pixels in its own projection. Retain the 0.5 native-pixel planted-episode range gate. Compensation must be a bounded whole-character visual translation, with physical motion separate; it cannot hide a bad support pose.
6. **Independent decision:** publish a source-bound review with visible examples and explicit accepted/rejected findings. User rejection overrides a prototype receipt. Mechanical correctness, identity hashes and producer approval never replace actual animation viewing.

Approve the unarmed four-direction walk first. Then review sword/blaster carry as real altered arm poses while maintaining the accepted leg mechanics; only afterwards expand run, combat and interruption/recovery. This is a bounded original-character art pipeline, not a promise to regenerate a full commercial game's library.
