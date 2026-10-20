# Torso motion ownership audit

The exact current scene loses substantial captured torso axial motion before the guard is authored. Its existing `spine` bone can support a coherent first torso authoring change; editing `neck` alone cannot coherently rotate the mixed-owner chest, shoulders, head and back equipment. This is a motion/ownership finding, not an art score or a physical-balance verdict.

## Source and coverage

- Read-only target: `/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-cloth-volume-v1/crease/full-captain-diagnostic.blend`.
- SHA256 before and after: `bfbdbef0b2b0281b854746b05be8018484376d250c0ac2429a6a492c5011bbcd`.
- Blender 4.5.9 LTS, background CPU, four threads. No rendering, GPU, rerig, blend save or preferences change. Outputs only in this audit directory.
- Full reads: `blender_body_rig.py`, `build_calibrated_body.py`, `apply_carry.py`, `condition_cycle.py`, `prepare_motion.py`, `cmu_fk.py`, CMU ASF and conditioned cycle. Historical rejected-owner evidence read only from `exact-source-owner-proof.json`; no opinion report read.
- Extracted all 131 integer times, including closed endpoint: current root/spine/neck/head/clavicle/hip matrices and positions; conditioned CMU lowerback/upperback/thorax/neck/head/clavicle rotations and positions. No all-mesh per-pose JSON.
- `bounded-extract.json` contains scene hierarchy, actual bone rest matrices, fixed rest-region weight aggregates and current pose data. `rotation-analysis.json` contains definitions, all angular metrics and bounded source rows. Hash coverage is in those receipts.

## What is lost

`blender_body_rig.py` consumes `global_rotations['root']` only. Spine uses the measured root→thorax direction; neck uses thorax→upperneck; head uses upperneck→head. Every nonroot segment gets the minimum swing from its fixed rest axis. Clavicle offsets use the resulting spine orientation, rather than measured clavicle rotations. This both collapses the multi-segment source trunk and discards rotation about each surviving segment axis. `build_calibrated_body.py` changes pelvis/hip/knee rest anchors but preserves this implementation.

All peak-to-peak values below use the actual conditioned cycle, including its endpoint, mapped to Blender Z-up. Axial twist is swing–twist decomposition about the native ASF/rest segment axis. Heading is the azimuth of transformed rest X. Source thorax native rest axis mapped to Blender is (0.027864, 0.077764, 0.996582), slightly tilted from world vertical; target spine rest axis is exactly +Z. Therefore native-axis twist and world-Z heading are separately reported, not conflated. Static source and target anatomies have not been equated.

| Measurement | Conditioned CMU | Current target |
|---|---:|---:|
| Root global heading | 11.064795° | 11.064796° |
| Thorax / spine global axial twist | 12.004651° | 0.0000076° |
| Thorax / spine global heading | 11.753448° | 0.046392° |
| Thorax / spine heading relative to root | 20.363554° | 12.605175° |
| Thorax axial twist relative to root | 19.883983° | See full metric ledger |

Source root/thorax heading correlation is **−0.805638**, establishing actual counterrotation in this cycle. The target retains root heading while the spine is almost heading-fixed. Thus a target root-relative angle can remain nonzero, largely as the inverse of moving pelvis heading; that alone does not show that captured chest counterrotation was preserved.

Current spine deformation rotation matches the original direction-only recipe to **4.84e−7 maximum matrix element error**, or **0.000013°** after projection to a rotation matrix. Current neck global axial twist spans only **0.0000031°**. Source lowerback/upperback/thorax axial spans are 6.025°, 7.896°, 12.005°; lowerneck/upperneck spans are 8.603°, 5.441°. These are conditioned-source measurements, not untouched raw AMC amplitudes.

The guard author intentionally replaces six arm bones (`upperarm`, `forearm`, `hand` each side) and two prop roots. It caches/preserves spine, neck, head, clavicles, hips and the armature world transform. Wrists/elbow bends are expressed in the existing spine frame. Therefore lack of free unarmed arm swing is expected guard authorship; lost torso axial volume response is an earlier and distinct retarget limitation. These measurements are armature-relative and independent of DrawRoot XY preview compensation. Removing lateral root sway from an in-place preview can alter perceived stiffness, but cannot explain the measured missing spine twist. No unsupported balance inference follows.

## Actual deformation owners

There are 22 body bones, including `spine`, `neck`, `head` and two clavicles; **no Chest bone**. Parent chain: root→spine→neck→head; both clavicles parent to spine. `CaptainArticulatedBody` uses the actual body armature modifier. Fixed selections below were made once from undeformed rest vertices in armature coordinates, never from changing pose bounds; regions are geometric proxies, not certified plate segmentation.

| Fixed rest region | Vertices | Mean deformation weights |
|---|---:|---|
| Waist: absX<.23m, Z .08–.25m | 4,150 | spine 91.97%, neck 4.32%, thigh owners 3.71% |
| Chest: absX<.23m, Z .25–.55m | 3,581 | spine 74.50%, neck 25.50% |
| Neck: absX<.18m, Z .55–.70m | 684 | neck 95.19%, spine 4.81% |
| Left shoulder: X .23–.55m, Z .35–.65m | 4,645 | upperarm 38.18%, clavicle 28.74%, neck 19.67%, spine 13.33% |
| Right shoulder: X −.55–−.23m, Z .35–.65m | 4,669 | upperarm 39.65%, clavicle 29.57%, neck 20.47%, spine 10.22% |
| Head: absX<.23m, Z .70–1.15m | 4,675 | head 100% |

Chest has 1,155 vertices with multiple positive bone influences; shoulders have 2,034 left and 1,541 right. Moving only neck or only a rigid backpack mount would change the relative geometry of these overlapping owner fields.

Backpack/halo belong to `BackgearRoot`, below `Captain_BackgearRoot_SpineMount`. Cape cloth and its separate `CapeArmature` belong to `CapeRoot`, below `Captain_CapeRoot_SpineMount`. Both mounts have baked actions and are object-parented to the body armature; they are not live bone-parent constraints. Both authored shoulder connectors belong to the cape spine mount. Sword/shield roots likewise have baked actions and object parenting, with replacement craft/attachment descendants. A bone edit alone does not reliably update these baked object drivers.

Historical factual owner proof is bound to this same source hash: rejected candidate cape contacts changed 0→13 at frame45; backgear contacts 650→693 at frame113 and 561→628 at frame75. Newly intersecting body triangles include neck/spine/head/arm owners, while backpack components are rigid object descendants. The cape case involves rigid left-foot triangles and lower cloth vertices. These facts establish why a coherent transport proposal still requires contact checking; they do not establish a repair or an art judgment.

## Minimal coherent authoring change

A first trial can use the existing **spine as the torso frame owner**, adding a bounded, phase-anchored axial twist track derived from measured conditioned thorax twist while preserving its existing swing, head/tail positions and root/hips/lower-bone transforms. Use the source **global** thorax twist excursion, phase-calibrated as theta(f)−theta(1), rather than adding source root-relative twist to an already root-driven frame. The 19.884° relative span includes the pelvis/chest relationship; 12.005° is the absolute thorax twist span. Never sum the 12.005° chest and 11.065° root spans. If exact source global heading is required, solve the scalar twist against the preserved target swing to match phase-calibrated source heading; native tilted-axis twist and world heading are not numerically identical. This adds one missing rotational degree of freedom; it does not recover the discarded lowerback/upperback articulation or create an independent chest/waist joint. The current weights couple waist and chest strongly to this same spine owner.

The crucial scope is one coherent transport delta `D(f)=T_new_spine(f) * inverse(T_old_spine(f))`, in armature coordinates, with rotation around the preserved spinal axis. Declare the pivot as the baseline animated `spine.head` (rest (0,0,0.08)m), with axis from baseline spine head to tail (rest tail (0,0,0.43)m). Any pure rotation about that same line preserves both endpoints. Default head policy is baseline head pose **relative to the transported torso**, with no additional gaze/optic correction:

1. Cache actual baseline poses and object mount transforms. Apply the new spine rotation with the same pelvis origin and spine tail. Keep root, hips, lower-bone curves and draw compensation exact.
2. Transport neck/head/clavicle global poses and their positions by this delta, retaining their baseline relative poses, including authored head orientation. Avoid independently freezing their old world/global keys or recomputing minimum swing, either of which erases coherent twist or breaks owner agreement.
3. Transport the authored guard as a whole, or rerun its solver from the updated torso/clavicle frame with the same chest offsets. Preserve palm-relative sword/shield mounts and the actual craft replacement anchors; bake prop roots from transported palms.
4. Transport both baked spine mounts and their descendants through the same delta exactly once. Keep cape local animation and protected top attachment relationship; do not transport both a parent mount and its child coordinates a second time. Shoulder connectors, backpack/halo and cape attachment must agree with the same torso owner frame.
5. Verify unchanged lower-bone/root matrices, rest mesh/UV/material/weights, bone lengths, grips and both integer/subframe contact geometry against the actual source. Lower bone preservation alone does not prove contact preservation because changed torso volumes and cloth can contact legs, equipment or hands.

This is the smallest coherent rotation-only authoring trial supported by the current ownership evidence. For independent pelvis/waist/chest motion or armor rigidity, a later explicit chest-owner/weight design may be needed; current data cannot claim that one spinal rotation reaches the requested quality. No neck-only residual is recommended.

Lower deformation ownership is explicit in `lower-owner-proof.json`: the body has **seven** vertices sharing spine with a lower owner, all `lthigh`: IDs 31962, 32185, 32458, 32462, 33040, 33044, 33046. Their spine weights range 0.000002410–0.023089478; rest Z spans −0.338488 to −0.228995m. A total of 1,724 body vertices below the rest pelvis Z=.08m have positive spine weight, mostly wholly spine-owned hanging/waist geometry; this geometric selection does not classify them as leg anatomy. Neither rigid boot nor either authored ankle joint has positive spine influence. Exact hips/leg-bone preservation therefore permits a torso-bone authoring trial, but does **not** imply all lower-looking body vertices are unchanged. Seven thigh-blended vertices and spine-owned skirt/waist volumes will move; contact and visual seam checks must include them. No weights are to be silently altered.

Exact object transport ledger:

| Authored owner requiring a new transported track | Descendants that follow automatically once that owner changes |
|---|---|
| `SwordRoot` / `SwordRootAction`, object-parented to body armature | `ClosedRidgedBlade`, `Grip`, `Guard`, `GripCollar*`, `Pommel`, plus `SwordRoot_FrozenCraftReplacement` with `ClosedRidgedBlade.001`, `BladeOuterSilverBevel*`, `BladeBlueRidgeBand*`, `Grip.001`, `GripCollar.002/.003`, `Pommel.001`, `GoldCrossguardSpine*`, authored skull/wing quillons and `RIGHT_Hand_Attachment.001` |
| `ShieldRoot` / `ShieldRootAction`, object-parented to body armature | `ShieldGrip`, `ShieldClosedCurvedPanel`, `Rim00`–`Rim95`, `GripBackMount*`, plus `ShieldRoot_FrozenCraftReplacement` with shield panel/rim replacements, `RearGripCantileverFoot*`, `RearGripCantileverDiagonal*`, `RearGripCantileverBridge`, and `LEFT_Hand_Attachment.001` |
| `Captain_BackgearRoot_SpineMount` / `Captain_BackgearRoot_SpineMountAction`, object-parented to body armature | `BackgearRoot` → `AuthoredBackpackBody`, `SideExhaust/.001`, `ExhaustGoldRim/.001`, `RearVent*`, `GoldPackRail*`, `ClosedGoldHaloRing/.001`, `RadialSpoke00`–`07`, `HaloMount*`, `AuthoredHaloBracket*`, `Halo_Centre`, `UpperBack_Attachment` |
| `Captain_CapeRoot_SpineMount` / `Captain_CapeRoot_SpineMountAction`, object-parented to body armature | `CapeRoot` → `CapeClothSurface`, `CapeArmature` with its existing `CapeArmatureAction`, neck/shoulder attachments; both `Authored_LEFT_CapeShoulderConnector` and `Authored_RIGHT_CapeShoulderConnector` directly under the mount |

All these mount/root parent types are OBJECT with empty parent-bone name and no bone constraints. None automatically follows a newly rotated body pose bone merely because its parent is the armature object. Children shown above have no independent object action; cape has its deliberate separate skeletal action. Keep those child local transforms/animation intact, and update the four authored root/mount tracks once. Convert old/new matrices through actual parent-world and matrix-parent-inverse transforms instead of assigning an armature-relative delta as if it were a world matrix. Full names, parent types and actions of all 295 applicable scene objects are in the bounded extraction.

Unknowns: equipped load changes the appropriate source twist amplitude/phase; measured unarmed capture is a starting driver, not the desired loaded motion. Exact contact-safe amplitude, subframe collisions, visual quality, chest plate boundary ownership and acceptability of waist/chest coupling remain untested. No candidate was created.
