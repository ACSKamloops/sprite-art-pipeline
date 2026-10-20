# Bounded v7 recovery camera diagnosis

**Fixed camera yaw alone does not solve the obscured recovery. Stop here and choose a structural motion/composition experiment.** The frozen independent v7 review (1a0737be) and its score are unchanged. This folder is diagnosis production, not independent approval of a new candidate.

Viewed all 30 actual rendered colour poses and their alpha-derived silhouettes, arranged as three rows (original24.7°,35°,45°) and five columns (cels41/46/51/56/60 = source83/93/103/113/121), at native256 and true384. These are bounded still poses, not a new animation or timed playback.

At35° a small black rear boot becomes more visible in cels46/51, and at45° it is somewhat clearer in46/51/56. However, the alpha silhouettes still show one thick connected leg column with no useful open separation between the legs. Cels56/60 retain the poorly exposed return. The skull knee and boot are mostly hidden, so these yaw changes do not reveal a complete release/passing/support story. Colour overlap cues improve a little; silhouette readability does not improve enough to justify a full65-frame camera candidate.

The45° view also narrows the visible chest and face, expands the visual dominance of the shield and cape, and makes the halo appear more elliptical. This changes the master composition without fixing the principal gait blocker.35° has less of that cost but still no sufficient recovery separation. The same soft armour treatment, broad cream ankle collar and rear curtain remain. No new camera score is assigned.

## Controlled setup and source binding

Input is the exact frozen native384 packed blend SHA256 **b320480050d6c87cb6c0ef1a8114c9dcb4606b29b6a2a9db69df099f57e57f09**, package producer commit d18d070. Camera original location (2.3,-5,1.9), target approximately (0,0,0.15), yaw24.7024°, elevation17.6392°, orthographic scale3.0. Source camera scale includes its original floating-point Z value0.9999999404. Baseline restoration uses saved location, rotation mode/Euler/quaternion/axis-angle and scale components; it does not decompose or restamp a matrix. Actual comparison against frozen source PNGs gives **zero changed RGBA pixels for all ten baseline renders**, both resolutions and all five poses. This is a reproduction check, not an art-quality point.

Variant camera positions orbit the same fixed target at unchanged distance/elevation; EulerZ changes by the global yaw delta. Scale, lights, original full visible body geometry and props, materials, actions, pose time, orthographic framing and render settings are retained. Native256 is a direct render, not downsampled384. Silhouettes derive from the full colour render alpha without masks or hidden near legs. No saved scene, producer files, bones, target tracks or motion were changed. Blender4.5.9 CPU six threads; render.py/assemble.py reproduce the evidence. source-binding.json and render-receipt.json bind inputs and actual output PNGs. No ray visibility metric was performed.

## Next bounded structural experiment, not implemented

A modest wider foot track could be tested at the current camera before changing character composition. Use a declared **authored layer**: anatomical right foot outward−50mm worldX and left foot outward+50mm worldX, relative to each original phase target; verify anatomical axes against the rig before applying. This adds100mm between targets rather than scaling the character or relabelling the captured human walk. Apply real hip/knee/ankle IK with rigid boots and controlled knee poles, not render offsets. Preserve source sagittal trajectory and orientation as the initial control; solve stance world targets and transitions continuously, verify sole placement/limb reach/joint clearance and the65-frame wrap, then inspect both recovery halves with all equipment. If boot separation alone fails because the shin/knee remains behind the near leg, the knee path and loaded guard composition need a separate declared layer. Do not apply a per-pose camera fit or hide the near leg.

Actual sampled foot-bone head X separation is341.9mm atcel41,381.0mm46,384.2mm51,384.5mm56,379.3mm60. These are bone-head distances, not sole centres or tread widths. Consequently, a claim that the captured walk has an absolutely narrow track is not established here; it may be narrow relative to the oversized armour volumes and projected sagittal overlap. The proposed100mm increase would produce approximately442–485mm bone-target separation before the solve. At ortho3.0,100mm has an upper bound of8.5native256 pixels /12.8native384 pixels before yaw projection and occlusion. It is a testable intervention, not a promised fix. The receipt records all sampled right/left thigh/shin/foot heads/tails, including the right knee trajectory; no sole-contact or reach feasibility is inferred from those five samples.

## Evidence

- comparison-256-colour.png / comparison-256-silhouette.png: native game scale.
- comparison-384-colour.png / comparison-384-silhouette.png: true larger render.
- baseline-comparison.json: exact baseline pixel agreement.
- render-receipt.json: camera components, actual five phases, bone trajectories and output hashes.
- source-scene.json: original packed scene/camera inventory.

No optional full-cycle rendering was added after the bounded failure became clear. A new candidate needs a fresh independent reviewer after any chosen camera or authored motion layer.
