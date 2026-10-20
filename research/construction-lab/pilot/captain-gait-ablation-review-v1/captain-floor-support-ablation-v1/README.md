# Fixed-recipe skeleton floor-support ablation

**Do not promote this candidate as a gait fix.** Replacing additive swing height with the floor-safe maximum slightly reduces the largest knee bends, but locally raises ankles and prolongs folded recovery. Geometric feasibility alone does not establish better armored walking.

Recipe was written before solving in `recipe.json` and its SHA is in `receipt.json`. CPU Blender4.5.9,6 threads; no rendering, scene saves, action writes, mesh exports or upstream edits. `run_ablation.py` loads the frozen calibrated-rest scene, reads skeleton poses and bounded rigid owned-boot vertices once, and uses the unchanged original contact functions in memory. In-memory weight writes are omitted. No original scripts are modified.

Only candidate swingZ changes to `max(floor_ankle(R), endpoint-calibrated raw ankleZ +25mm*sin(pi*u)^2)`. The original smallest common pelvis-lowering policy is recomputed for pre-wide targets; then both cases apply the existing±125mm foot translation and identical source-hinge two-link knee solve. Stance targets, swingXY, boot pitch, fixed bone lengths and inferred stance episodes are identical. This follows the existing contact→wide layer order; no new widening clamp or pelvis adaptation is introduced. Upper guard is not mutated/evaluated. Its inputs and root motion remain unchanged because the common lowering happens to be identical in this case.

## Reproduction and sampled feasibility

At all521 times, original contact ankle targets match the saved source ledger exactly. Original contact knee error≤0.367micrometers, root≤0.004micrometers and pelvis lowering exact. Original wide endpoints reproduce the separate saved wide ledger within1.476micrometers. These bounds account for saved bone-matrix roundoff rather than assuming exact geometry.

Both original and candidate remain reachable after widening: minimum marginsL1.286mm/R5.517mm. Two-link length errors≤0.129micrometers. The knee plane agrees with the source hinge projected perpendicular to the new ankle axis within1.71e−7 in absolute unit-dot error. Unprojected source-hinge alignment is also recorded; the solve inherently uses its projection and does not guarantee perpendicularity to the original unprojected axis.

Actual fixed rigid owned-boot vertex minima, including the whole restZ<−.84 boot mask rather than only heel/toe points, stay above floor to float tolerance. Stance gaps are±0.030micrometers. Original maximum swing floor gapsL146.72mm/R199.68mm; candidateL123.92mm/R172.24mm. Swing gap is a **minimum geometric clearance**, not a force/contact measurement or required zero-gap assertion. Candidate swing minimaL1.209mm/R0.401mm. The maximum's floor-support branch is never active in these sampled swing intervals: calibrated rawZ plus arch is already above the pitched boot support requirement. Downshifting both candidate ankles50mm fails the same floor guard, reaching−50.000mm, so the guard demonstrably rejects penetration.

## What changes

| Metric | OriginalL/R | CandidateL/R |
|---|---:|---:|
| Peak knee flexion |84.62°/89.54°|82.61°/86.45°|
| Ankle-minus-hip vertical excursion |318.42/360.49mm|293.42/333.06mm|
| Maximum additional ankleZ at another phase |0/0|+88.29/+120.21mm|
| Maximum additional local knee flexion |0/0|+21.65°/+31.51°|

Largest local knee increases occur at sourceframe85.25L and19.75R:49.46→71.11° and40.55→72.06°. The candidate smooths away the pitch-dependent low ankle portion of recovery and keeps the leg folded longer. Peak-only statistics conceal that change. See `skeleton-comparison.png` and `comparison-detail.json`.

Root excursion remains59.468mmZ; maximum common pelvis lowering41.004mm. Candidate root/pelvis changes, stance ankle changes, swingXY changes and boot pitch matrix changes are all zero. The trial isolates a floor-support formulation, not a new upper-body gait or contact solution. It accounts for only2–3° of peak surplus relative to the original capture and cannot explain/cure the larger contact-layer20° surplus by itself.

## Loop seam and scope

After removing physical horizontal stride, ankle endpoints close within≤60nanometers. One-sided finite-difference ankle velocity jumps: left0, right original(−.1046,+.1321,−.01164)m/s and candidate(−.1046,+.1321,+.02066)m/s. Knee velocity jumpsL−3.79°/s in both cases;R−37.80°/s original and−33.75°/s candidate. These sampled one-sided approximations retain the sourceC0 conditioning; they do not certifyC1 continuity or playback quality. Root seam and full ranges are recorded in `receipt.json`.

The journal contains both cases'521 named skeleton/rigid-boot targets. It is numeric test evidence, not a saved rig or approved geometry-target promotion. No full articulated-body/cape/prop collisions or relative-parent action interpolation were evaluated; finite target samples do not certify all real times. No art rating or rendered character trial occurred. This candidate should remain an ablation result; do not use it as a replacement gait without a different evidence-supported recipe.

To reproduce from this worktree:

```bash
'/home/astra/projects/Mech Warrior Test/tools/blender-linux/blender-4.5.9-linux-x64/blender' --background --threads 6 --python-exit-code 7 --python experiments/captain-floor-support-ablation-v1/run_ablation.py
python experiments/captain-floor-support-ablation-v1/summarize.py
```

Source hashes and recipe hash are in `receipt.json`; original private audit outputs were untouched.
