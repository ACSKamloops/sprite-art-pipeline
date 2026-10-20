# Optional Captain carried upper loading experiment

One bounded **unapproved** comparator. It changes upper parenting, preserving every baseline leg PNG and the1200ms physical root/holds. It is not a new art approval or a revision of earlier rejected grades.

`loading.py` uses source waist pivot130,125, roll−3sin(2πphase), and bounded2.25px upper settle centered at authored load phases.10/.60. Chest, shoulders/arms, shield and backpack/halo share the rigid parent. Head remains gaze angle0 while its position follows the transformed source neck point133,72. Cape top follows that chest parent; the frozen source-owned cloth lag trails the hem. No per-pose fitting or per-frame redraw is used. Waist/tabard and all lower layers remain baseline.

Preferred output: `artifacts/loading-v2/`. Compare baseline/experiment in `comparison-0.png` and `comparison-1.png`. Actual three-loop native/2x color/silhouette MP4s are in `artifacts/audition-v1/`; open `index.html` locally. Detailed metadata and candid creator observations: `experiment-notes.json`.

All72 leg layer hashes remain exact. Nearest-neighbor upper transformations preserve the supplied source-part palette, including declared source-owned underlaps; this does not claim all hidden source pixels were recovered from the approved portrait. Separate head/chest masks need not overlap because source ownership is exclusive. Actual edges near the neck remain within1pixel across72 poses. Carried anchor distances are rigid to2.85e-14px. World-stride translation yields identical local RGBA replacements. A static positional head misses the articulated neck by up to2.779px; a deliberately wrong phase changes the parent. Periodic parent math passes. These checks do not prove weight, appeal or game-art quality.

Actual output timestamp/export checks passed, with no clipping in allfour3.6s videos at stage1024×832/origin416,80. Videos have a1ms terminal packet and RGB→YUV conversion can differ by2LSB. The creator inspected all72 decoded native first-cycle source timestamps, eight enlarged/silhouette samples and wrap; not continuous video ingestion. The attachment/load direction is more coordinated, but the visual improvement is modest and inherited leg silhouette/volume defects remain. **Commercial walk approval stays false.**

## Reproduce without changing baseline

```sh
python pilot/captain-upper-loading-v1/build.py --output /tmp/captain-upper-loading-fresh
python pilot/captain-upper-loading-v1/verify.py
python pilot/captain-upper-loading-v1/export_review.py --spec pilot/captain-upper-loading-v1/artifacts/loading-v2/audition-physical.json --output /tmp/captain-upper-audition-fresh
python pilot/captain-upper-loading-v1/inspect_export.py
```

Requires Python/Pillow/NumPy/SciPy and ffmpeg/ffprobe. Builders refuse existing outputs. Own frozen source packet878649a6… and upper images are copied and hash-bound. Baseline is the existing repository's longstride-cloth-v1 artifact; `--baseline` accepts an explicitly provided compatible artifact. No other checkout is imported or written. The actual committed video spec/72 PNGs equal loading-v2 byte-for-byte; a path-only portability change did not regenerate motion pixels.

## Integrate optionally with a new leg packet

Import `loading.py` only when this source-anchored option is selected. Provide original source upper images, the new pose packet and matching source design. Call `cloth_packet(packet,cfg)` once, then `render(sources,packet,index,cfg,frozen_cloth,adapted)` per pose. It returns seven replacement layers and attachment metadata; composite in the caller's unchanged owned layer order. New caller must separately bind the new packet/leg pixels and recheck seams, palette, source timing, actual exported world motion and art. The module reads phase, upper pelvis, physical root, camera/stride and neutral upper bindings; no old pose indices/frame identities are inferred for a new packet.

True projected torso yaw is not implemented in this bounded experiment. No hidden anatomy/force or finished-character claim is made.
