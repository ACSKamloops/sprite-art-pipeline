# Independent whole-figure art review: frozen Captain v8

Verdict: **8/10 overall.** I would expect this sprite in a finished strategy or action game with similarly rendered character art. It is convincing, readable game art, but I would not honestly call the complete walking presentation 9/10. Native384 is the preferable delivery when screen space permits; native256 remains usable and recognizably the same Captain.

This is a fresh independent visual opinion, not a production pass. No previous aesthetic score or review was opened. No source, game code, model, animation, or producer checkout was edited. Mechanical audits do not contribute points. The frozen source has no credit for subsequent head or sole changes.

## Bound inputs and exact viewing coverage

- Producer: `/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-wide-craft-v8`, supplied frozen producer commit `7ca64d8`.
- Manifest SHA256: `cac8ed35521c743cdbb3efa178a45c1f9121ba33ac58fe7bc689c5461d5dbfb8`. Independently hashed all 634 listed assets; zero mismatches.
- Master: `pilot/space-marine-captain/upright-master-v1/nearest-512.png`; exact hash in `coverage.json`. Viewed the complete master image.
- Source: visually viewed all consecutive `frame-000.png` through `frame-064.png`, separately at native256 and native384, in chronological bounded contact sheets. No downscaling was applied to the image tiles. Global crops only remove empty margins and preserve every source RGBA pixel.
- Encoded: independently decoded the actual 1x normal and 1x half-speed MP4s at each resolution with ffmpeg. Visually viewed all 66 consecutive decoded frames 0–65 for each of the four streams: complete first cycle 0–64 plus first next-cycle/wrap frame 65. Normal is 60 fps, half-speed 30 fps; both contain 195 encoded frames. The second and third cycles after the first wrap were not visually inspected.
- Display enlargement: visually viewed nearest-neighbor 2x source poses 16/51/58 at256 and 0/46/51/56/58/64 at384. The 2x encoded MP4s were hash-verified as manifest assets but not visually inspected; these display judgments are bound to the listed source enlargements.
- `coverage.json` names every inspected sheet, input hash, decoded frame hash and exact index range. `EVIDENCE-SHA256.json` binds all local review evidence.

**Tool limitation:** this review uses discrete chronological image viewing, including decoded video images. It is not continuous video ingestion or a human watching a real-time player. Cadence, perceived weight at speed, and whether small details shimmer perceptually are provisional. Neither frame labels nor joint metadata certify physical support. I did not inspect game-world ground contact, gameplay speed, or backgrounds beyond this dark neutral presentation.

## Whole figure, identity and equipment

The red plate armor, black and gold accents, bare pale head, halo, tall sword and decorated skull shield identify the master immediately. The sword remains on anatomical RIGHT and shield on anatomical LEFT. The equipment remains distinct and attached throughout the inspected cycle. The sword reads as a blade at native display, and the shield's central skull and radiating motif remain legible rather than dissolving into generic noise. The outline has clear major landmarks even when the legs pass.

Both stride halves show distinct knees and boots. In the close carry overlap around export46/51/56/58 (the supplied source-key93/103/113/117 context), the gold/black right knee and red left knee remain visible in the whole figure. Their silhouettes can merge without either knee disappearing. I do not find an invisible-knee blocker. The dark outsole is a credible functional dark shape at native display; elaborate sole ornament is not necessary, and its plainness is not a deduction.

Native384 retains more facial expression, small equipment marks and gold edge separation. Native256 compresses the face, belt ornament and chest decoration into softer groups, but the role and design remain clear. Nearest2x enlargement exposes that softness without inventing new detail; it does not turn the 256 export into a 384-quality render. The sprite's modern shaded rendering is allowed and judged on its own terms, not against a restricted palette requirement.

The figure remains faithful in its major design while its rendered finish is smoother and more volumetric than the master. Some of the master's finely outlined ornament and stronger facial linework become softer; this is a fidelity/polish limitation, not a character-identity failure.

## Support, release, recovery, adjacent frames and wrap

Across export0–10 the right boot advances from its tucked recovery position toward the next extension. Around12–18 its upturned sole and extending leg clearly announce the forward step. Around20–24 that boot turns down while the opposite leg releases behind; around24–36 the opposite shin visibly folds in recovery. Around42–51 the left boot extends forward; around54–60 it turns down while the right leg folds behind. This is a coherent alternating walk progression, not random foot swapping. There is no conspicuous pose discontinuity or equipment teleport in the inspected adjacent sequence.

The 64→65 encoded wrap is visually consistent with the surrounding late-to-early progression at both resolutions and both speeds. I see no obvious seam snap. The first-cycle decoded images preserve the source appearance with expected minor encoding differences; I see no new large corruption or missing figure detail.

Support is visually plausible at a broad pose level, but less persuasive than the very good equipment identity. The armor is heavy and the carry can reasonably be restrained; even so, the upper figure remains comparatively settled while the boots describe a large stride. The sheets establish ordered poses, not that the combined motion will feel sufficiently heavy at 60 fps or that a planted sole is locked to a moving game floor. Those are remaining runtime questions, not verified physics defects.

## What keeps the whole presentation below 9

1. **Cape material and secondary motion:** the broad gray/tan lower cape behind the shield reads as a relatively flat, stiff panel. This is visible through both halves, particularly24–36 and46–58, with large low-detail surfaces and an angular lower border. At native256 it can read almost like a rigid backing to the shield. More convincing cloth volume and restrained independent follow-through would improve the whole figure more than extra outsole decoration.
2. **Weight transfer and carried mass:** the restrained head, shoulders, halo, sword and shield give good consistency but comparatively little visual response to the changing support leg. The clear leg cycle and nearly settled upper assembly together feel more like an orderly march than an exceptionally weighty armored walk. This is a visual polish concern with provisional timing severity, not a claim of absent knees, impossible joint state, or proven floor skating.
3. **Fine-detail hierarchy:** the large bright shield is excellent for identification but dominates the quieter chest and face. At256, those smaller identity details are noticeably less crisp than the master. At384 this is reduced, though broad bright gold patches on the thigh/shoulders still have a more rendered, smooth finish than the master's controlled ornament. This is the smallest of the three limitations.

These are specific reasons to withhold an excellent-tier score, not a declaration that the asset is unusable or needs wholesale rebuilding. The sprite already earns its score through its whole-figure readability, equipment, identity and coherent stride. A credible next quality decision would require continuous playback in the intended game scene before changing animation or promising a higher score.
