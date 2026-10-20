# Separate58%-stance 3D gait guide

This preserves `captain-3d-pose-guides-v1` and the frozen boot experiment. It changes the authored continuous geometry, not the source picture or existing boot pack. It is a skeletal diagnostic, not approved sprite art or validated dynamic balance.

Changes from the earlier model:

- stance0.58 / swing0.42, opposite limb phase offset0.5;
- heel strike0..0.08, flat0.08..0.48, toe release0.48..0.58;
- two finite double-support intervals per continuous cycle, phases0..0.08 and0.5..0.58 (16% total);
- common pelvis lateral transfer `T*6*sin(2*pi*phase)`, using true model transverse `T=[-.8,-.6,0]`, rather than mixing sagittal motion with world-X sway;
- stance endpoints and swing path re-authored for the new fractions, preserving44-unit physical stride, atomic heel/toe pivots, source camera and1200ms cycle.

The72 held samples quantize those contact labels to12/72 displayed frames (200ms,16.667% of1200ms). Continuous geometry and baked contact-label intervals are therefore declared separately; no exact58% physical-support claim is inferred from held images.

Both hips remain rigid offsets of one pelvis. Mean pelvis height112.8, fixed femur42/tibia48, loading amplitude1.7, swing clearance and rigid boot dimensions are unchanged. A1,441-phase preflight found minimum reach margin0.213906 with no adaptive hip motion, bone stretching or per-frame fitting. World selected contact material points remain fixed; loop and contact-role boundaries are continuous. Actual raster/GPU foot contact is not certified by these equations.

The fixed-source camera/hidden hip/true3D anatomy remain authored hypotheses, documented in `design.json`. The original image is byte-identical. `neutral_bind` changes because the second foot now remains in late toe release at phasezero; root must use this packet's bind and must rerender against it, **not restamp the previous boot/wholebody outputs**. The boot's local geometry/UV can be reused as a construction input, but new projected pixels require fresh evidence.

```sh
python pilot/captain-3d-pose-guides-v2/build.py --output /path/to/fresh-guide
python pilot/captain-3d-pose-guides-v2/check.py
```

Checker targets the committed `artifacts/frozen-v1`. `poses.json` exposes72 endpoint-excluded world/projected frames, fixed projection/basis, neutral bind, foot orientations/sole polygons and bone binding frames. Native256PNG skeleton guides, eight-key2x sheet, actual1200ms GIFs and neutral motion-audition specs are included. GIF timing uses cumulative10ms quantization; full source holds16/17ms total1200ms. The contact sheet was actually viewed. It shows a finite transfer/support interval and forward sagittal knees; upper centerline remains restrained and has no armor appeal judgment.

Root read-only neutral exporter produces actual normal/half-speed/native/2x colour/silhouette loops:

```sh
python /home/astra/projects/sprite-construction-lab/pilot/motion-review-harness/export_motion.py --spec pilot/captain-3d-pose-guides-v2/artifacts/frozen-v1/audition-in_place.json --output pilot/captain-3d-pose-guides-v2/artifacts/audition-in-place --loops 2
python /home/astra/projects/sprite-construction-lab/pilot/motion-review-harness/export_motion.py --spec pilot/captain-3d-pose-guides-v2/artifacts/frozen-v1/audition-physical.json --output pilot/captain-3d-pose-guides-v2/artifacts/audition-moving --loops 2
```

No3D armor, artistic score, physically complete gait/CoM claim or inherited visual approval. The current primitive foot boxes and upper centerline are constraints for authored surfaces, not a final game asset.
