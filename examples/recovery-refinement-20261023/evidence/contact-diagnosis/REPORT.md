# Bounded 02→03 contact diagnosis

**The guide does not support correcting painted 03 with an automatic +11 px vertical translation.** The earlier measured contour changes are real, but interpreting them as two continuously planted contacts was not justified. Source frame 10→17 lifts the screen-left hand, keeps the other hand approximately stationary, and repositions one foot in world depth. The painted leg arrangement also departs substantially from the guide. These effects cannot be reduced to a single support-plane jump.

**Evidence favors a mixture of encoded source movement and generated pose/layout drift. There is no positive evidence here of an importer registration error.** A smaller additional upward placement change in the paint is plausible, but remains unproven without tracing the retained raw cells through the importer.

The independent baseline report remains frozen and unchanged. This follow-up tests its contact-displacement interpretation using newly authorized source evidence; it is not another blind review or a new art score.

## Evidence and method

Read the nominated guide's `JOINT-PATHS.json`, `GEOMETRY.json`, `manifest.json`, and `build.py`; inspected existing source renders `0010.png` and `0017.png` against painted `inputs/02.png` and `03.png`. Read the public replay `recipe.json`. Examined source joint samples 10 through 17 to avoid drawing a contact conclusion from endpoints alone. No source edits, Blender execution, or new 3D renders were performed.

The guide records one fixed orthographic camera at (-4,-6,4.5), 33.64223 native pixels per world unit, with no per-frame fit. The build changes only the Head scale curves by 2.05; the measured non-Head joint-world error is zero. Its declared export pivot is (40,72), distinct from the projected world origin (40,67.71858).

The replay recipe declares the same transform for every generated cell:

`dest = (40,72) + 0.90 × (guide_or_raw_local_stage - (40,72))`

Applying that transform to the guide supplies a common comparison coordinate system; it does not imply that generated paint actually followed each guide joint. The recipe was inspected, not an importer implementation/raw-to-output pixel replay. Its declaration alone cannot prove the implementation bug-free.

`measurements.json` contains inputs and SHA-256 fingerprints, world/projected landmarks, projection decomposition and intermediate paths. `guide-paint-comparison.png` composites the existing guide renders, their shared-scale versions and painted poses. The comparison uses 80 × 80 coordinates, y downward. No continuous playback or physics simulation was observed.

## What the source actually moves

“Palm” in `JOINT-PATHS.json` is explicitly **the hand-bone tail proxy, not a measured skin contact**. Ankle and toe joints are also geometric landmarks, not contact flags.

| Landmark | Source world change 10→17 | Projected change after shared 0.90, px (x,y) | Supported interpretation |
|---|---|---:|---|
| Right palm proxy; screen-left hand | Z 0.02140→0.26272; ΔXYZ=(+0.04824,-0.05688,+0.24131) | (+2.17,-6.15) | The source lifts this hand. It is not continuously planted. |
| Left palm proxy | ΔXYZ=(+0.00220,+0.02027,-0.01413) | (-0.28,+0.12) | Approximately stationary in projection and near its previous low world height; a plausible remaining support, not proven contact. |
| Left ankle; screen-right leg | ΔXYZ=(+0.00817,+0.18119,+0.00074) | (-2.84,-2.23) | Foot repositioning in the world plane; projected rise is almost entirely depth, not vertical lift. |
| Right ankle; lower screen-left leg | ΔXYZ=(-0.00475,+0.01014,+0.00064) | (-0.29,-0.10) | Nearly stationary; samples 11–17 are particularly stable. |
| Pelvis | ΔXYZ=(+0.03026,-0.00517,+0.13103) | (+0.85,-3.68) | Torso/hip rise, not a whole-rig camera shift. |

The right-hand lift progresses within the interval: its proxy Z rises from 0.0214 at frame 10 through 0.0724 at 15 and 0.1454 at 16 to 0.2627 at 17. The left-hand proxy stays near Z=0.027–0.041. The source therefore encodes a transfer away from the visible screen-left hand.

The left ankle moves in depth while remaining at approximately Z=0.069–0.070; its toe proxy lowers from Z=0.2498 to 0.1755. The right toe lowers from Z=0.0498 to 0.0053 while its ankle stays near Z=0.0893. This is geometry consistent with foot repositioning and changing foot pitch. It does **not** prove heel lock, a particular replant event, friction, support forces, or physical validity.

Under this camera, the scaled screen-y change is approximately:

`Δy = -7.9102 ΔX - 11.8652 ΔY - 26.7096 ΔZ`

For the left ankle, world-plane movement contributes -2.214 px and vertical movement only -0.020 px. For the right palm, world-plane movement contributes +0.293 px while vertical movement contributes -6.445 px. Consequently, equal world height is not equal image y, and an image's lowest alpha is not a ground-contact measurement.

## What differs in the painting

1. **Hand:** the painted screen-left palm contour goes from bottom row 74 to row 63 (-11 px). The corresponding guide proxy rises about 6.15 px. A meaningful part of the visible rise is authored hand lift. The remaining roughly 4.85 px is a contour-versus-joint residual, not a measured registration error: hand shape, orientation, arm proportion and placement all differ. Painted 03 retains a rather flat, contact-like palm silhouette even though the source hand is lifting, which can make the hand's role unclear.

2. **Feet and knees:** the source retains two spatially separated lower-leg branches. After shared scaling, the right ankle is near (34.63,69.51) and its toe near (37.32,74.77) in frame 17. Painted 03 has no visible matching low foot in that region; its legs instead form one folded, rightward grouping with the visible boot ending at row 64. The source's other ankle is near (49.44,66.87). Paint also changes its knee/cuff arrangement. This is substantial pose/occlusion/layout departure from the guide, not evidence that the importer shifted a faithful pose bodily upward. It may be a deliberate stylized reinterpretation or generation drift; these files do not establish intent.

3. **The lowest boots are not a tracked common contact:** the combined source foot-owner geometry's lowest projected y moves **down** from about 74.17 to 75.08 after scaling. The paint's lowest brown contour moves **up** from row 76 to row 64, but the visible foot roles and silhouettes change. Subtracting those minima and naming the result “ground movement” would compare different geometry and potentially different feet.

4. **A possible smaller placement component:** the source head-owner top moves from y32.13 to y27.38 after scaling (-4.76 px), while painted hair/head top moves 32→22 (-10 px). Its approximately -5.24 px residual resembles the palm's roughly -4.85 px residual. This is compatible with an additional ~5 px upward placement component in 03, alongside nonrigid leg changes. It is not a fitted or proven translation: hair silhouettes and joint-to-skin distances change, and the generated proportions differ from the mannequin.

## Classification and next experiment

- **Importer registration error:** not demonstrated. The declared shared affine transform cannot itself introduce an isolated 02→03 translation; it scales all relative displacements by 0.90. No raw-cell or implementation trace was included in this bounded inspection, so an implementation error is not absolutely excluded.
- **Generated pose/layout drift:** supported relative to the nominated guide, especially in the leg arrangement and the missing visible counterpart of the guide's low foot. A common extra upward placement component is plausible but less certain.
- **Intentional source depth/repositioning and support change:** encoded by the joint paths. The visible hand lifts; one ankle moves in depth and the other is almost stationary. Calling this a specific physically valid contact/replant sequence would exceed the evidence.

**Smallest defensible next experiment:** perform a read-only correspondence panel for the retained raw cells behind painted 02 and 03, marking the neck/upper torso, visible wrist, and each distinguishable knee/ankle before and after the exact recipe transform. Do not fit each cell independently. This tests whether the differing placement and leg arrangement already exist in the generated raw material. If they do, retain the shared importer registration and address only an explicit pose/limb-role candidate. If they do not, investigate the transform/cell selection before touching the art.

Do not impose the earlier +11 px whole-frame shift or force both palm bottoms to a common screen row. Either would erase part of the documented hand lift and ignore the oblique camera. Any later art candidate should make the releasing hand and the two leg roles readable while checking a named ankle/foot trajectory, rather than aligning the lowest alpha.
