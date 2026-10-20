# Held poses, timing and whole-foot contact

Use this when baked sprite frames accompany continuous actor movement. A sole point on a source pose is not proof that the whole rendered boot stays planted between poses. The detailed local humanoid case is `/home/astra/projects/sprite-construction-lab/pilot/captain-leg-rig-v1/`; current source-bound verdicts remain in the project handoff and review folders.

## Separate clocks

Keep elapsed time, sampled pose index and source motion phase explicit. Retiming the same72 images from uniform60Hz to12–21ms holds can preserve a1200ms loop while slowing the loaded pose and accelerating release. Interpolate declared physical_root between each source pose and the next, using cycle stride at wrap; a linear wallclock root no longer describes the retimed source gait.

Godot SpriteFrames can use fps60 with relative hold `duration_ms*.06`. Selection, stepping and events follow cumulative source boundaries. Normalize only machine roundoff; probes truly before a boundary must select the previous pose. Test actual resource playback, speed, pause, wrap and reload. A browser player is a separate implementation and requires its own readback proof.

Local tested helpers: `pilot/captain72-godot/hold_clock.gd`, `lab_holds.gd`, `test_runtime_holds.gd`, `test_material_holds.gd`; contracts and launch commands are in `VARIABLE_HOLDS.md`. The wrapper supports exactly72 poses in this case; adapt and verify that restriction for another asset.

## Material evidence

Freeze source-attached sole anchors, boot RGBA identity, stance episodes and physical root displacement. Keep flat-foot contact conservative unless actual heel/toe geometry is authored and measured. An IK endpoint and a lowest-row witness can falsely pass while the ankle/boot material jumps; the preserved feedback-based negative case demonstrated this.

For visual stance locking, use a fixed world target for the active stance episode and ONE complete-actor draw correction. Apply the same draw root to both boots and the whole actor, including double support. Do not independently fit boots, limbs or whole pose bounds. Measure every isolated boot material pixel in world GPU readback throughout stance, not only the chosen witness. Include the raw continuous-root negative, every pose, fractional samples, both cycles and wrap. Report the visual-versus-physical correction bound; this is a visual policy, not proven3D collision anatomy.

Raster conventions matter: Python round-to-even and Godot ties-away-from-zero can differ at half-pixel roots. Computing a fresh target from every rounded pose can move contact on a few poses despite a passing isolated-foot test. The delivered preview must use the SAME episode-fixed support target/correction policy as the test. Bind the target table to actor and leg manifests and test the actual packaged preview.

## Art review stays independent

Every-frame hashes and exact world material can coexist with poor proportions, a camera-facing disc kneepad, a rigid upper assembly or an unconvincing load/release. View native and nearest2x, all predecessor/current pairs and wrap, and fresh timed presentation. Give concrete visual defects and scoped source-bound ratings; do not manufacture scores from check counts. A reviewer disagreement keeps the requested gate open. Retiming a weak key pose is only a timing experiment; author the missing compression/counterrotation pose when that is the actual defect.


## Preserve import pixels in the delivered project

For the Captain's hard-alpha, nearest-filtered PNGs, strict imported RGBA checks caught Godot's `process/fix_alpha_border` changing RGB at fully transparent pixels (401006 pixels; zero visible/alpha changes). Keep the strict test. Set the existing frame `.import` entries to false and configure `[importer_defaults]` `texture={"compress/mode":0,"mipmaps/generate":false,"process/fix_alpha_border":false,"process/premult_alpha":false}`, then actually reimport before freezing and rerunning. Defaults alone do not rewrite existing sidecars. The [official texture importer documentation](https://docs.godotengine.org/en/stable/classes/class_resourceimportertexture.html) explains alpha-border behavior; this choice is for exact hard-alpha/nearest exchange, not a universal setting for soft filtered artwork.

The actual final release kept the same art and passed1043 checks with strict imported sourceRGBA, resource holds, control signals, independent episode targets, source ledgers and native/2× GPU images. Its source-bound art reviews were9.025/9.17; these ratings come from visual reviewers, not engineering counts. Preserve the failed import run and bind the passing report to the tested ledger. If adding proof reports to a delivery later, retain that original tested ledger alongside a fresh content ledger instead of rewriting the historical test claim.


## Superseding Captain video rejection

The user rejected Captain v20 after viewing the delivered video. Its9.025/9.17 ratings are historical failed aesthetic judgments, not accepted example art. Root inspected consecutive decoded native and2× loops: the gait stayed crouched, contact/passing/extension silhouettes were weak, the upper combat illustration dominated, and deformed armour clusters were busy. Precise partitions, contact tests and small chest motion did not produce a believable walk. See local `pilot/space-marine-captain/video-rejection-review.md` and `user-rejection-v20.json` for source-bound evidence.

The MP4 omitted the tested root/floor/stance-correction presentation and quantized variable source holds at60Hz (66of72poses percycle). Compare the actual final deliverable against its declared presentation policy, not only a separate engine lab. Inspect motion silhouette and whole-cycle support/load/push-off at intended speed before expanding/interpolating the pose count. Technical reproducibility stays useful; user rejection supersedes reviewer art acceptance even when every hash still matches. No template should inherit the rejected example's visual approval.


## Reject impossible whole-sprite contact correction

A later96px unarmed hero had two improved full-body drawings, sixteen and eight poses, with visible-art reviews around8. Conditional heel/forefoot/ankle traces still gave incompatible travel-speed fits for the two support legs. Those landmarks and contact intervals were authored hypotheses, not recovered anatomical truth. A whole-sprite offset could force zero residual at selected samples, but required roughly11px offset variation and backward body jumps. Reject that correction rather than presenting mathematical fit as a grounded walk. Report full-hold drift separately: continuously moving a root under a held raster always introduces within-hold displacement. Evidence: `foot-contact-diagnosis-DXDXDX` under the20261015 local case.

A continuous3D control can instead author fixed-world heel→flat→toe targets, a complete rigid shoe, root travel and reachable leg IK before rasterization. Check every boot vertex, rigid lengths, stage boundaries and periodic translation. Keep proxy anatomy and stylized shoe/head proportions under visual review: zero contact error can still produce a crouched or marching guide. The local EAE guide retains recovered upper-body template motion while replacing lower-body mechanics; it is a new authored method, not recovered private PixelLab inference. Generators receive these poses as reference pixels/video with empirical adherence, never a guaranteed foot lock.
