# Read-only gait cause audit

The strongest diagnosed difference is **extra knee flexion introduced by the contact-conditioning layer**, not by the later widening and not by a lack of mandatory arm swing. Whether its visual magnitude is unacceptable for this armored guard remains an art decision; the motion is demonstrably larger than the input.

Inspected all 65 current native384 frames, chronologically in six 3-column sheets at original pixel size. Their rear-leg tuck/forward sole presentation is conspicuous around frames000–005/024–033 and 012–020/048–052, respectively. The leg actions alternate coherently; I did not see a discontinuous knee reversal in those sheets. I checked all65 decoded normal and half-speed first-cycle frames against independent fixed-checker composites: both differ by at most2 RGB LSB. I did not ingest continuous video, so temporal feel/speed acceptance remains untested by this audit.

Current blend independently hashes to `bfbdbef0b2b0281b854746b05be8018484376d250c0ac2429a6a492c5011bbcd`. All viewed native hashes are in `viewed-frame-hashes.json`; source/blend/sheet hashes are in `evidence-hashes.json`.

## Motion ranges

Knee flexion means angle between hip→knee and knee→ankle, with0° straight. These numbers are recomputed from existing source/pose ledgers, not a fresh evaluation of the current packed scene. Current integration/preservation receipts say its inherited521 bone poses remain exact; the intervening sole04/head/cape changes preserve pose/geometry and concern paint/materials. Detailed inputs and range results are in `motion-ranges.json`.

| Layer | Left knee° | Right knee° | Root-relative ankle vertical excursion, left/right |
|---|---:|---:|---:|
| Original selected CMU cycle |0–67.89|0–68.78|191/178mm|
| Seam-conditioned CMU |0.41–65.40|1.25–68.78|185/174mm|
| Calibrated direction retarget |0.41–65.40|1.25–68.78|252/251mm|
| Contact/source-hinge solve |15.09–85.78|15.09–89.94|302/347mm|
|125mm wide-track solve |6.05–84.62|12.53–89.54|Not directly comparable: saved wide ledger uses hip-relative points|

The calibrated retarget preserves knee angle but changes lengths/proportions: thigh383mm, shin581mm, translation scale1.1919. The sum of lengths is scaled; individual segment ratio differs from the source, so ankle excursions need not be uniform-scaled. Original cycle stride1.498m becomes1.786m per1.083s. There is no armor-specific cadence/stride conditioning.

## Matched hip comparison and limits on the diagnosis

All layers measured on the same anatomical basis, ankle minus ipsilateral hip, with the source mappedY-up→Z-up:

| Layer | Left vertical range | Right vertical range | Range / leg length L,R |
|---|---:|---:|---:|
| Raw capture |199.93mm|186.25mm|.247,.231|
| Conditioned capture |194.63mm|181.75mm|.241,.225|
| Calibrated direction |271.31mm|266.14mm|.281,.276|
| Contact/source hinge |318.42mm|360.49mm|.330,.374|
|125mm wide |318.42mm|360.49mm|.330,.374|

Thus the change survives common anatomical basis and normalization for total leg length. Widening leaves vertical ankle/hip excursions unchanged to micrometer-scale ledger precision. Its new knee angles follow the extra lateral reach, and do not explain the vertical lift. Source leg lengths areL808.83/R806.27mm versus target964.05mm, with different thigh/shin proportions.

Removing only the recorded pelvis lowering mathematically from the hip points would increase those contact vertical ranges to332.49/365.45mm. This is a coordinate attribution, not a feasible alternate solve: the lowering helps leg reach and cannot simply be deleted. Its maximum41mm is not the primary cause of the enlarged vertical range.

The increased motion is diagnosed relative to the source; **inappropriate loaded-gait recovery is not yet proved**. Some higher ankle position is geometrically necessary to keep this large rigid pitched boot above the floor. The floor-safe support term, captured vertical excess, declared25mm arch, nonlinear knee solve and pelvis lowering must be separated before judging the surplus. Saved floorcontact passes support the geometric necessity claim for the current targets, not their uniqueness. I did not inspect force/mass data, which is absent here.

## Causal ownership

* **Capture:** `captain-3d-rig-lab/source/cmu07/07.asf` and `07_01.amc`, evaluated by `scripts/cmu_fk.py`;130-frame cycle selected from316 at120Hz. Six timestamp decodes of actual official `07_01.avi` are in `cmu-original-native.png`. This AVI is a small rendered yellow skeleton, not filmed human carrying armor. It visually contains ordinary free-arm walking and bent swing knees; it cannot certify a loaded guard's balance.
* **Seam:** `scripts/condition_cycle.py` closes source-channel endpoint drift with cubic position correction. It reduces rather than increases maximum knee flexion. It only closesC0; velocity continuity is not guaranteed.
* **Retarget:** `scripts/blender_body_rig.py` plus `scripts/build_calibrated_body.py`: properY-up→Z-up map `((1,0,0),(0,0,-1),(0,1,0))`; fixed authored rest anchors/lengths; global measured segment directions; minimal swing relative to rest, no recovered axial twist. Hip/clavicle offsets follow root/spine. One spine direction spans source root→thorax. This does not preserve every captured thoracic axial rotation. Any missing loaded torso compensation is therefore possible, but its necessity/degree is **unknown** from these references.
* **Contact:** `scripts/build_contact_source_hinge.py`: inferred stance episodesL98/82samples,R33/78; sagittal ankle→ball pitch normalized by mid-flat median; authored heel/flat/toe windows; swingXY calibrated from captured curve. Crucially swing ankleZ is `floor_ankle(R)+captured_excursion+25mm*sin(pi*u)^2`, where floor support depends on rotated actual large sole vertices. Maximum common pelvis lowering41mm. Two-link knees solve to these authored targets using source femur rotation and ASF tibia±20°Z C-axis hinge. This layer adds about20–21° maximum knee bend and retains15° minimum bend. It is the first causal owner to examine for excessive tuck/lift.
* **Widening:** `captain-rig-carry-art-v8/experiments/captain-wide-track-v2/apply_wide_track.py`: translates foot/toe±125mm in bodyX, preserves their3×3 rotations, re-solves thigh/shin around captured hinge. Saved1041-time audit bounds boot-vertex deviation from that pure offset at41micrometers, nonleg matrices0. It changes stance width and knees, but does not generate the large pitch arcs or significantly increase flexion peaks.
* **Boot ownership:** `scripts/build_articulated_ankle_v4.py`: boots rigid100% foot bone; greave foot influences transferred to shin, closed caps/flexible joint added. Large boot pitch/sole visibility is rigid geometry rotating about an authored ankle/foot basis, not deforming boot weights. Source toe motion is not separately expressed by this rigid boot. Saved physical-root mesh contact passes at1041times, maxfloor gap/penetration0.059mm: contact correctness does not establish loaded-gait quality.
* **Guard:** Current helper is `captain-3d-generation-lab/upper-author-clock-v2/apply_carry.py`, SHA`a4812e694d73a68199b1acae9a6dbd0420cf39c66ae541835859c61d1cb938cc`, recipe `carry-readability-v1/design.json`, SHA`135284d89df6e86a405c669d3d12e2c8284149acc8997f2a969c6d9a286d46e8`. It replaces six free-arm tracks with chest-relative two-linkIK/fixed palm mounts. The authored load curve ranges−18..+8mm, right hand0.7×left; spine/neck/head and legs preserved. Quiet guard is deliberate and already has a small response. The missing-captured-arm-swing claim is true by authorship, but does not diagnose a defect.
* **Camera/presentation:** fixed global camera elevation12°, yaw24.70°, ortho2.7; DrawRoot removes captured horizontal travel. These expose large soles/front leg depth and suppress actual forward translation, but do not create physical knee/pitch ranges. Cape additions preserve inherited bone action. Camera/cloth/material changes cannot remedy genuinely excessive knee targets.

## One minimal next test

Run a **skeleton-only vertical-swing ablation** in an isolated scratch copy, before any mesh/render work: retain floor-safe stance, sourceXY, original boot pitch, guard, widening and common pelvis policy; during swing compare current additive height with `max(floor_ankle(R), endpoint-calibrated_raw_ankle_Z+25mm*sin(pi*u)^2)` and solve the same two-link/source-hinge knees. Report knee peaks, ankle excursion, reach and floor-support feasibility across521times. This tests whether combining pitch-dependent full-boot support height with captured vertical excursion unnecessarily stacks lift. It is a hypothesis, not an approved change or a proven improvement; if it fails contact/reach or doesn't reduce the20° surplus, retain the baseline and investigate authored proportions/pitch normalization next.

No checkout edits, rerig, Blender evaluation, new GPU renders, art score, or other reviewers' ratings were used.
