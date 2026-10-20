# Fixed-3D-bone walking reference — diagnostic only

This is a new authored anatomical model, not another tuning of the failed planar art rig. It projects one consistent 3D skeleton with forward sagittal knee bends into a fixed orthographic view. It does **not** recover true anatomy from the portrait, build a 3D armor character, or establish attractive finished movement. The guide is intended to constrain subsequent independently reviewed limb artwork.

The copied upright master is unchanged. Its observed image landmarks are listed separately in `design.json`. A single picture does not determine depth or true bone lengths. The hip joints here are deliberately authored inside the belt; walking tracks are narrower than the picture's combat stance. The camera elevation, heading, anatomical dimensions and ground-depth stagger are explicit hypotheses. Root's generated lower-body art has not been silently substituted for this source.

## Reproduce

From the assigned checkout:

```sh
python pilot/captain-3d-pose-guides-v1/build.py --output /path/to/new-output
python pilot/captain-3d-pose-guides-v1/check.py
```

The checker currently targets the committed `artifacts/final-v3` packet. Builder refuses an existing output. Python + Pillow suffice. `design.json` controls camera elevation, forward axis, stride, fixed bone lengths, common pelvis load/transfer, clearance and foot dimensions. The opposite support offset is half a cycle. Source is never rewritten.

Actual neutral timed auditions were built with the root read-only exporter:

```sh
python /home/astra/projects/sprite-construction-lab/pilot/motion-review-harness/export_motion.py --spec pilot/captain-3d-pose-guides-v1/artifacts/final-v3/audition-in_place.json --output pilot/captain-3d-pose-guides-v1/artifacts/audition-transparent-in-place --loops 2
python /home/astra/projects/sprite-construction-lab/pilot/motion-review-harness/export_motion.py --spec pilot/captain-3d-pose-guides-v1/artifacts/final-v3/audition-physical.json --output pilot/captain-3d-pose-guides-v1/artifacts/audition-transparent-moving --loops 2
```

`artifacts/final-v3/eight-keys-2x.png` is the personally inspected rendered contact sheet. The GIFs use cumulative 10ms quantization totaling 1.2 seconds, not 72 independently truncated 16ms holds. Neutral MP4s use the declared 16/17ms holds and explicit physical root. These are visible skeleton guides, not game sprites.

## Packet contract

`poses.json`: 72 endpoint-excluded samples at 60fps, one 1.2s cycle; fixed world origin and canvas. `camera.matrix_2x3` maps world deltas to pixels; add screen origin `[130,239]`. World Z is height, positive Y projects down; floor is world Z=0, **not a constant screen row**. Heading `[-.6,.8,0]` and transverse `[-.8,-.6,0]` define the sagittal plane and lateral width. Physical stride is `44*heading`; screen stride is approximately `[-26.4,10.88]`.

Each sample contains physical root, upper world/projected anchors, both legs' hip/knee/ankle/heel/toe, projected and true segment lengths, per-segment longitudinal/transverse/normal frames, and the boot's rigid orientation basis plus sole rectangle. `neutral_bind` includes the same fields at phase zero. The source upper registration is one explicit constant rest offset. Artwork adaptation must not fit each cell independently.

Contact roles: heel strike first .08 local phase, flat through .4, toe release through .5; swing through 1. A rigid boot rotates about the **selected fixed heel or toe**, then ankle position is derived from that transform before IK. Sole width16, heel-to-toe28, ankle height25.235 world units. Hip-to-knee42 and knee-to-ankle48 are fixed. No per-leg hip compression, bone stretching, extrema feedback, or independent foot pixel registration is used. Both hips follow the same pelvis. Swing clearance is a declared analytic trajectory; a small sinusoidal endpoint term prevents rigid foot corners crossing ground during the rotation transition.

`segment_frames` are a binding basis, **not known armor depth surfaces**. Source artwork may need separate thigh/kneecap/shell/boot drawings and believable cross-sections. In particular, projected longitudinal shortening is legitimate 3D foreshortening; stretching a flat noisy armor texture along that axis is not automatically a convincing render. Toe/heel markers are authored anatomical guide points, not a proven opaque source material feature.

## Evidence and limits

`geometry-check.json` samples 1,441 phases: minimum chain reach margin0.17985 units. `invariant-report.json` checks continuous contact episodes and role switches, fixed lengths, ground clearance, loop/root translation and source hashes. Selected world material contacts remain fixed to numerical precision. An epsilon around2e-16 below Z=0 is floating-point arithmetic, not measurable penetration. This proves the model equations; it does not prove GPU sprite soles or anatomical attractiveness.

The contact sheet was actually viewed: the model has upright support and distinct swing bend, unlike the old persistent combat squat. Upper detail remains a simple diagnostic centerline; no appeal score or visual acceptance is claimed. Head angle is stabilized but head position follows chest. Shoulder/chest counterrotation is mild. Arm/elbow/wrist carry, armor occlusion, cloth, exact source camera recovery, collision semantics and textured surface deformation are still open. A final art loop must be independently watched, not approved from these invariants.

Earlier trial packets remain private/untracked; trial-v1/v2/v3 had small swing sole crossings and were superseded. Failed narrow 2D art is preserved separately at commit13d4483.
