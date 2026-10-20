# Fresh whole native384 baseline opinion

**8/10 for whole game-asset suitability at native384.** I would expect this Captain in a finished game with compatible shaded sprite art. It has a clear character identity, convincing equipment and a coherent armored walking sequence. I would not honestly give it 9/10 on the inspected evidence. This score stands on the updated baseline's actual images; it is not an inferred gain from an older version's score or a reward for tests.

## Exact version and coverage

Baseline source SHA256: `bfbdbef0b2b0281b854746b05be8018484376d250c0ac2429a6a492c5011bbcd`. This includes the compact eye, thinner sole and crease material. It includes neither uniform lag nor the differential-fold candidate.

Current visual evidence is the frozen `artifacts/cape-traveling-fold-gpu-audition-v1/baseline` export in read-only paint-lab, supplied freeze commit `89ef38f`. Receipt SHA256 `738cce2d7f04906105a41c708850a5e268d158e2172f04f0bd286385cd9d8479`; all 567 audition assets independently hash-verified, zero mismatches.

Visually inspected all 65 actual native384 source poses, consecutive export indices 0–64, using 11 bounded 837×760 whole-figure native sheets. Also independently decoded and visually inspected all 66 first-cycle-plus-wrap frames from baseline normal and half-speed MP4s: 132 actual encoded images, both indices 0–65. Inspected adjacent progression and 64→65 wrap. Normal is 60 fps and half 30 fps; second/third cycles after that first wrap were not visually reviewed. Exact nearest2x whole poses 0/16/51/58 were also viewed at 768×768. Reopened and viewed the original `pilot/space-marine-captain/upright-master-v1/nearest-512.png` in this task; its hash is in `coverage.json`.

This is a complete source-frame opinion at384, not a full256 review. The separate CPU256 phase pairs used for the component choice cannot establish complete256 quality. Hash-bound input, decoded-image and viewed-sheet records are in `coverage.json` and `EVIDENCE-SHA256.json`.

## Whole figure and master identity

The Captain reads immediately: red armor, black/gold ornament, bare pale face with the mechanical eye detail, halo, tall sword and skull shield. The anatomical RIGHT sword and LEFT shield remain attached and distinguishable throughout. The blade stays clear against both the neutral source display and decoded checkerboard. The shield's large skull and radiating motif give strong identification at actual native size. The face has a stern readable expression; it does not require the 2x inspection to be recognizable.

The large equipment, knees and boots preserve the figure's armored mass. Close leg overlap around 46–58 crowds the contour but leaves both knee surfaces and boot landmarks readable. It is not an invisible-knee defect, and forcing a detached silhouette is unnecessary. Dark soles are credible simple functional shapes. Their lack of elaborate ornament is not a quality deduction.

Major design fidelity is strong, although the master has more fine linework and a more ornate long central hanging belt/tabard area. In these rendered views, that area reads mostly as red cloth below the belt; the exact decorative hierarchy is weaker than in the master. This is a statement about visible fidelity, not proof that any concealed mesh detail is absent. Bright gold on the shield/shoulders commands more attention than smaller chest and belt decoration. Those smaller details remain recognizable at384, but the master's controlled graphic linework is not reproduced completely.

## Pose progression and weight

The two legs alternate clearly through extension, release and tucked recovery. Around 12–18 the right boot presents its sole as the leg advances, then turns down around 20–24 while the other shin folds behind. Around 42–51 the left boot advances; around 54–60 it turns down while the right leg recovers. The source and encoded images maintain this ordered progression. I see no conspicuous equipment pop or large adjacent pose discontinuity. The first wrap follows the surrounding cycle without an obvious snap.

The upper carry reads as deliberate: raised sword, held shield and stable gaze suit a guarded armored march. Restrained arm motion is not equivalent to missing upper-body animation, and more swing would not automatically improve the asset. There is comparatively little visible response in the carried mass to the larger leg cycle; stronger weight transfer might improve polish, but I cannot declare it physically wrong from discrete poses. Runtime ground contact and matched travel speed were not verified in this review.

## Why the score stops below 9

The primary limitation is the visible cape: a broad low-detail light surface with a comparatively straight angular outer edge and gold border. Crease shading supplies some volume, yet the whole presentation still leans toward a stiff panel rather than especially convincing cloth. It does not make the sprite unusable; it lowers its finishing polish.

The secondary limitation is precise master-decoration fidelity and finish. The rendered highlights and softened small ornament are attractive but less controlled than the master's strong outlined detail. Together with the provisional weight/cadence question, this supports a good finished-game asset rather than an excellent-tier verdict. These are bounded polish concerns, not a request for wholesale rebuilding or invented missing limbs.

## Practical limits

The tools expose discrete chronological video frames, **not continuous real-time ingestion**. Perceived cadence, weight, shimmer and actual game-world readability remain provisional. This review used neutral/source and checkerboard presentation, not a complete game scene or gameplay journey.

The 384 CUDA export is matched exploratory visual evidence. Its GPU-versus-CPU overlapping keys differ by up to 58 RGBA on a small subset of pixels; this is not CPU-equivalent rendering and does not certify exact CPU reopen. The separate authoritative CPU checks receive no art points and are not replaced by this opinion. No future cloth experiment is credited. No producer source was edited or publication authorized.
