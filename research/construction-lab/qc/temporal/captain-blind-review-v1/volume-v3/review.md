# Independent full-sprite volume v3 review

**Needs source art and whole-body motion revision. Integrated game-sprite quality: 5/10, uncertainty +/-1. Not ready for finished-walk user approval.** The character shows an advancing alternating leg action in the physical export, but does not yet convincingly walk as a dimensional, heavily armored Captain. This verdict is independent of the guide's useful kinematics and any exact anchor/contact checks.

## Strongest observed blockers

1. **Boots lose the character's armored construction.** This is visible throughout the loop, particularly the raised plain boot at frame18/300ms and skull-side passing boot at frame54/900ms. They read as small red wedges with broad smooth faces and thick dark bottoms, rather than the master’s overlapping red armored toe/instep sections. The boots look undersized relative to the large greaves and shield mass. Their pitch changes, which is an improvement over a permanently upright cutout, but revealed side/underside surfaces lack convincing material detail. The full exported2x frames at300/900ms make this obvious; it is already in frozen source PNGs, not video color conversion.

2. **Projected painting does not retain dimensional greave volume.** The plain viewer-right flame shin behaves like a triangular hanging textured flap beneath the shield, strongest frame18-36/300-600ms and frame54/900ms. It has little convincing side wall or ankle-shell connection. The far skull medallion/cream trim flattens and skews into a thin oval plaque in frames48-60/800-1000ms, while the narrow red cuff beneath it reads disproportionately small. Some foreshortening is legitimate when a shin changes orientation; the failure is that the illustration flattens without corresponding thickness or revealed surfaces. This reads as deforming painted planes rather than rigid power armor. The fixed4x diagnostic crops of frames0,18,36,54 distinguish source material behavior from an export effect.

3. **Walking geometry is present, but its weight is weak in the finished silhouette.** The moving-root sequence visibly alternates supporting and lifted feet. The short stride, very upright trunk, nearly locked shield/sword/halo configuration and small smooth boot silhouettes make it feel like the ornate upper illustration rides above the foot mechanism. At frame18/300ms and54/900ms, the guide’s sagittal passing action is partly hidden by the rendered greaves/cape rather than becoming a strong whole-body pose. Contacts at0/600ms have little clear compression and transfer of the Captain’s heavy load. Equipment warrants restrained arm movement; believable pelvis/trunk response, a convincing supporting leg and delayed cape response are still needed.

4. **Art needs overlap and pixel-cluster cleanup after the volume repair.** The silhouette exposes narrow shoulder/head/chest and cape-inner-boundary slits, particularly around150-300ms and900-1100ms. Small contour and decorative clusters shimmer as projected planes change orientation. The shin/boot junction at the lifted far leg is visually narrow and awkward, though I do not claim an actual disconnected joint from that appearance. These are secondary to the flat armor/boot design issues; alpha equality or numerical anchor coincidence would not resolve them.

## Motion and identity that should be retained

The red armor, blond cyber-eye head, gold halo, cream cape, sword on viewer-left and black/gold shield on viewer-right remain recognizable. Sword grip and main gear ownership remain stable; I did not see disappearing equipment or a major grip separation. The richly textured upper source has substantially better material readability than the newly projected lower surfaces.

The advancing action is more coherent than the earlier v4 plate motion: the incoming foot advances, the opposite foot lifts, and the loop continues without a prominent reset. Unlike the six-key hybrid's abrupt held-picture changes, the72-pose progression is gradual. But the hybrid's explicit painted incoming soles were locally more legible; the new geometry does not automatically make the full sprite better. Preserve sagittal movement and stable identity while rebuilding the lower armor surfaces.

## Support, timing and wraps

The current guide uses half-cycle support: handoff at600/1200ms provides a moment of double touch rather than sustained load overlap. This was visibly inspected again in the full-sprite sequence rather than treated as solved by the guide audit. The small trunk bob and very regular paths remain procedural. The human benchmark provides contact/release/passing/incoming readability; it does not require unarmed arm swing or a long stride. A short encumbered walk is valid if load and foot contact remain clear.

Frame71/1183ms progresses into frame0/1200ms smoothly enough; the second and third loop boundaries were checked too. The principal defect is persistent material/weight readability, not an isolated wrap pop. Normal and half-speed timestamp sequences reinforce the same observation. Tool limitations mean this is not a claim of watching uninterrupted video cadence.

## Source versus export presentation

Producer supplied eight in-place videos. Root authorized an independent physical-root spec/export in this review worktree so moving claims could be checked. I copied all72 frozen PNGs and verified their declared hashes, changed only root_policy/name/path references in the spec, and exported three loops through the shared read-only harness. Renderer/source/producer checkout was not altered.

All physical1x variants have zero clipped samples. The late third-loop2x videos clip the sprite canvas/sword at the left stage edge:17 normal samples and25 slower samples in each color/silhouette pair. This is a review-stage framing issue, not a gait defect or source-art clipping. The first full2x loop and inspected900ms full export frame are unaffected; all moving1x samples remain usable. Widen or follow the review stage before presenting the three-loop2x moving reel to a user. Physical review exporter was not a gameplay controller or GPU sole test.

## Coverage and strongest repair

All72 actual frozen source frames were viewed in fixed-canvas native grids. All16 actual in-place/independent-moving color/silhouette normal/slower1x/2x variants were decoded consecutively. Visual sequence coverage includes every first-loop source pose in native in-place and physical color at normal speed, and every physical silhouette pose at half speed, with all three loop boundary/end packets; actual full exported2x color frames at300/900ms were inspected separately. Retained sheet hashes identify the exact visually inspected evidence. Redundant variants were decoded but not all individually visually viewed. Decode receipts bind timestamps/counts and hashes. No per-pose fitting was used.

**Interface limit: chronological decoded still frames, not continuous video ingestion.** No art runtime, interruption transitions, additional direction, CoM/support-force model, collision or GPU sole evidence is claimed. The primary benchmark is the verified photographed eight-frame walk; the new upright master supplies identity and material expectations.

Strongest repair: **build or paint actual greave and boot volume around the already useful sagittal guide**, preserving master boot scale/segmentation and consistent side surfaces. Check frame18/54 passing and frame0/36 contacts before expanding. Pair that with explicit heavy whole-body support transfer; more frames, anchor precision or a longer translating root cannot repair these flattened shells.
