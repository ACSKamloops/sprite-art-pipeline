# Canonical 3D guide v3: independent neutral motion audit

**The projected guide does make walking sense and is a substantially better anatomical motion foundation than the earlier planar plate motion. Neutral guide plausibility: 7/10, uncertainty +/-1. This is not an art score, heavy-character animation approval, or a dynamics certification.** It is usable to constrain a revised art prototype, with the transfer limitations below kept open.

## Strongest remaining limits

1. **Support transfer has no sustained double-support interval.** The far foot is heel/flat/toe-supported for the first half and the near foot for the second. At frame36/600ms, the far toe is at ground height but labeled air and the incoming near heel has just touched ground. The same instantaneous handoff occurs at phase zero/1200ms. Thus the guide has a moment of geometrical double touch, not a sustained period of load exchange. The photographed benchmark's contact poses visibly show an incoming and outgoing grounded foot before release. The guide can still read as a short walk, but its exact half-cycle relay makes a cautious heavy walk less convincing. Check a brief overlapping support interval against the human reference, rather than assuming the equations' contact flag supplies believable transfer.

2. **The guide does not establish dynamic weight or equipment balance.** The cyan torso remains an almost vertical centerline with mild shoulder counterrotation and a small lateral/vertical oscillation. At passing frames18/300ms and54/900ms, its pelvis projection is still between the leg tracks rather than fully aligned with the supporting leg. A geometric lateral check places the pelvis center about3 world units beyond the supporting sole rectangle's inner lateral edge in both poses. This is NOT proof of falling: pelvis location is not the complete center of mass, and moving balance need not be static. It is specific evidence that fixed contacts and valid bone lengths do not establish load-bearing balance. Shield, sword, backpack, cape and armor mass, trunk lean/rotation, and actual support forces remain absent.

3. **Cadence reads regular and procedural, with restrained extension.** The 1.2s two-step cycle is100 steps/min, near the photographed study's roughly107 steps/min. That broad cadence is plausible. The guide has smooth symmetric repeated paths and very small trunk motion, however, rather than convincingly loaded accelerations and gear response. Its22-world-unit step compared with90 total thigh/shin length is a deliberately short step. This can suit encumbrance, but should be checked with drawn armor volumes before declaring convincing movement. Short stride plus the camera's depth projection can reduce visible front/back separation considerably.

## What is visibly successful

- In the actual moving export, the stance foot stays spatially organized while the pelvis advances, rather than moving a static combat pose across the grid.
- Frame18/300ms shows the near knee bending in the forward sagittal direction with the foot lifted and passing; frame54/900ms repeats on the far side. The knees no longer splay sideways to manufacture clearance.
- First contact uses the heel and the boot lowers into flat support through approximately0-96ms, repeated600-696ms. The trailing foot pivots toward toe release through approximately480-600ms and1080-1200ms. Swing extension then brings the opposite heel forward. The foot rectangle visibly changes orientation rather than keeping a frontal boot cutout upright.
- The stance leg becomes more upright as the torso advances, while the other leg flexes and recovers. Small pelvis lowering near150/750ms and rising later in support gives a readable load rhythm. These observations come from the rendered sequence, not from accepting invariant reports.
- The endpoint-excluded last sample1183ms progresses into1200ms without a conspicuous pose reset. Moving-root continuation and the second-loop ending also remain coherent in the decoded samples.

## Camera and inferred anatomy

The fixed orthographic three-quarter projection is coherent for a diagnostic and lets opposite legs stay distinguishable. The floor is a world plane: different screen sole heights alone are not penetration, and depth-forward travel contributes screen-down displacement. An eighteen-degree elevation and authored heading[-.6,.8,0] are hypotheses, not a recovered camera from the master. The hips,90-unit leg chain and foot dimensions are similarly authored; a single portrait cannot validate them. Line segments and flat sole rectangles omit thigh/greave volume, boot upper geometry, armor collision and occlusion. A texture or shell may therefore look wrong despite good guide poses. This audit does not inspect or approve the pending master-plate art prototype.

## Evidence and coverage

Primary motion benchmark: the verified photographed eight-frame `Man_walk_1_4.gif`, inspected earlier at full chronological phase coverage. Human gait support/readability is the comparison, adapted to heavy gear rather than requiring unarmed arm swing.

All16 supplied actual MP4 variants were decoded consecutively after reports existed. Visual coverage: all72 first-loop projected poses plus first wrap and second-loop endpoint samples in moving color at normal speed and in-place color at half speed; an actual unnormalized2x moving export frame at900ms was inspected too. The normal/slower contact grids keep a common crop, with no per-pose fitting. The remaining redundant scale/silhouette variants were decoded but not all individually viewed; retained evidence hashes identify viewed grids. `poses.json`, design and README were inspected to clarify labels and coordinate hypotheses, not to derive approval from check results.

**Tool limit: decoded chronological still frames, not continuous video ingestion.** Timing/phase progression was inspected from actual source/video timestamps; perceived uninterrupted cadence remains less certain. No runtime physics, collision, force/CoM model, gear volume or additional camera was tested. No finished art score is assigned.

## Next calibration

Keep the sagittal leg and heel/toe basis. Evaluate support overlap and the associated whole-body transfer before freezing it as the heavy Captain's final motion. Then verify a modest volume-bearing neutral torso/boots against the same guide, particularly passing and incoming extension. Do not let a successful equations/contact test or this diagnostic assessment promote the later rendered art without fresh visual review.
