# Independent swing-pitch skeleton ablation

**Valid sampled skeleton hypothesis; modest recovery-arc change, not an art improvement claim.** Damping only swing boot pitch reduces peak knee bend about4° and local bend up to6–6.5°, while preserving original root/hips/pelvis and stance targets. The largest local increases stay below0.7°. This supports a limited contribution from pitch-dependent support height of the large rigid boots. It does not remove the larger source→contact gait change or establish better armored walking.

This case starts from the original additive floor-support solve. The previous floor-safe-max candidate is not stacked into it. The recipe was written before evaluation in `recipe.json`; its frozen SHA and source hashes are in `receipt.json`. CPU Blender4.5.9,6 threads;521 times at quarter source intervals. No renders, saved scenes/actions, source writes, full-mesh exports, GPU work or art scoring.

## Fixed experiment

During inferred swing only, `theta_new=theta_original*(1−0.35*sin(pi*u)^2)`, where `theta_original` is the original **normalized ankle→ball sagittal boot pitch used by the contact solve**, not an ASF raw ankle joint channel. Off/landing pitch and first derivative of the blend multiplier are unchanged. Stance rotation/heel-toe pivots/contactXY and all swingXY are unchanged.

At each swing sample, floor support is recomputed from the new rotation and **all original rigid owned-boot vertices** selected by the existing anatomical rest mask, rather than heel/toe witnesses alone. AnkleZ remains `required_support_height + original_captured_vertical_excess +25mm*sin(pi*u)^2`. The arch/excess is unchanged. Both cases use the original common pelvis-lowering track exactly; candidate targets are rejected if unreachable, before invoking the two-link solve. No candidate pelvis lowering, reach clamp or arm change is allowed. Both apply the existing±125mm ankle offset and same projected source-hinge two-link solve.

`run_ablation.py` loads the frozen calibrated-rest scene only to read skeleton poses and bounded original owned-boot coordinates, with in-memory weight writes omitted. Original contact ankle targets reproduce the saved source ledger exactly, original knee≤0.367micrometers, root≤0.004micrometers and original lowering exactly. Original wide endpoints reproduce the independent wide ledger within1.476micrometers. This bounds roundoff rather than assuming equivalent anatomy.

## Full local changes

| Metric | OriginalL/R | CandidateL/R |
|---|---:|---:|
| Peak knee flexion |84.62°/89.54°|80.62°/85.61°|
| Ankle-minus-hip vertical excursion |318.42/360.49mm|310.66/352.38mm|
| Boot pitch over full cycle |−70.07..+33.32° /−75.16..+35.33°|−66.88..+33.32° /−68.10..+35.28°|
| Full local knee-flexion delta |baseline|−6.50..+0.145° /−6.05..+0.693°|
| Full local ankleZ delta |baseline|−33.94..+0.753mm /−34.07..+4.009mm|

Highest local flexion reductions: sourceframe75.25L,80.26→73.76°;8.75R,84.51→78.45°. Highest local flexion increases:57L,64.71→64.86°;122R,69.03→69.72°. Largest height decreases:74.25L,−33.94mm;7.5R,−34.07mm. Largest height increases:57L,+0.753mm;122.5R,+4.009mm. Those small increases show that the actual boot support envelope is not uniformly monotonic in pitch.

Maximum pitch attenuation occurs inside swing, while the most negative pitch extrema remain close to constrained off/landing windows. Thus the largest whole-cycle pitch angle falls only3.2°L/7.1°R despite the35% midpoint blend. The scientific comparison plot shows phase-dependent effects, not only peaks. `comparison-detail.json` includes every sample's signed delta and complete worst-case skeleton/rotation/support records. `targets-journal.json` contains both original/candidate521 targets for further bounded proof; it is not a promoted rig.

## Sampled geometry and reach gates

All samples are reachable. Minimum wide-leg reach marginsL1.286mm/R5.517mm remain unchanged. Bone-segment length errors≤0.121micrometers in the candidate. The knee plane agrees with the source hinge projected perpendicular to the ankle axis within1.81e−7 absolute unit-dot error. The unprojected hinge alignment is recorded separately; the source solve uses its projection.

All owned rigid boot vertices and fixed sole vertices remain above floor within1micrometer tolerance. Stance floor gaps are±0.030micrometers. Swing floor gaps are the same geometric clearance track up to float error: original/candidate maximaL146.72mm/R199.68mm, minimaL0.097mm/R0.035mm. These are minimum floor-clearance constraints, not zero-gap swing contact or measured force. The−50mm ankle-down negative control fails the same full-owned-boot floor guard at−50.000mm.

Candidate root, pelvis lowering, stance ankle, swingXY and stance boot rotation changes are all zero. RootZ range remains59.468mm; maximum common lowering41.004mm. Upper guard is not evaluated/mutated; its original chest-relative inputs remain untouched. The experiment is an authored loaded-boot pitch adaptation, not exact source capture or force truth.

## Loop and validation limits

Both cases preserve ankle loop position closure after physical stride removal within60nanometers, and boot pitch closes exactly. Candidate knee positions close within≤0.4micrometers. These are numerical target results, not saved relative-parent action interpolation proofs.

The source isC0-conditioned, with retained velocity residuals. Right ankle one-sided finite-difference velocity jump changes from(−.1046,+.1321,−.01164)m/s to(−.1046,+.1321,−.04975)m/s. Right knee-flexion velocity jump changes−37.80→−44.67°/s; right boot-pitch jump changes51.67→31.06°/s. Left ankle/boot-pitch jumps are0 and knee-flexion jump stays−3.79°/s. The damping factor's zero derivative at swing endpoints does not repair the original loop velocity seam. NoC1 claim is made. Full root, knee-position, ankle, pitch and angle seam metrics are in the receipt.

No latest articulated body/cape/prop collision, full latest boot-cap geometry, rendered character deformation, or continuous-time interpolation has been tested. Finite521 skeleton/support samples and static original owned-boot vertices do not establish full current-scene validity. A bounded actual-scene proof would be necessary before rendering/art review or any promotion. Numerical evidence supports examining this candidate further, with modest expectations; it is not a complete gait fix.

Reproduce in this isolated worktree:

```bash
'/home/astra/projects/Mech Warrior Test/tools/blender-linux/blender-4.5.9-linux-x64/blender' --background --threads 6 --python-exit-code 7 --python experiments/captain-swing-pitch-ablation-v1/run_ablation.py
python experiments/captain-swing-pitch-ablation-v1/summarize.py
```

The second command validates reach, fixed root/stance/XY and stance pitch, projected hinge, floor pass and the rejected penetration negative control; then regenerates the standalone plot and full local-delta journal. Earlier floor-safe-max case and original private causal-audit artifacts are unchanged.
