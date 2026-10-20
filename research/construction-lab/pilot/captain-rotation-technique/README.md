# Approved Captain shin — fixed-pivot rotation comparison

This local technique experiment rotates the user-approved extracted right shin/boot, not an invented replacement. The portable `source/right_shin.png` is the original 256×256 RGBA part. `source/provenance.json` binds its PNG SHA and the approved full-reference SHA. It is user-supplied Warhammer derivative artwork, not claimed CC0 or freely redistributable.

Five angles −30, −15, 0, +15, +30° share knee pivot (100,169), original 256 canvas and origin. Positive angles are counterclockwise on screen. Coordinates use pixel-boundary space with pixel centers at x+0.5/y+0.5. There is no fit, recenter, or changing camera. Output part PNGs contain no guide; contact-sheet pink crosses are pivot guides only.

## Compared methods

1. Native nearest affine rotation.
2. Exact RGBA-equality Scale2x repeated three times (8×), then nearest affine rotation around the correspondingly scaled pivot, then nearest downsampling to the original canvas.

The second is a **Scale2x×3 rotation approximation**, not claimed identical to Aseprite RotSprite. Aseprite's implementation also handles parallelogram mapping, masks and bounded destination transfer; those details are not reproduced here. The Scale2x neighbour rules follow the primary [Scale2x algorithm specification](https://www.scale2x.it/algorithm). [Aseprite's rotation documentation](https://www.aseprite.org/docs/rotate/) distinguishes its fast and RotSprite modes; its [current source implementation](https://github.com/aseprite/aseprite/blob/main/src/doc/algorithm/rotsprite.cpp) provided algorithm context, not proof that this experiment equals the complete implementation. Sources inspected 2026-10-07. No Aseprite CLI output is used as a golden control.

## Actual results and visual judgement

`final-results/comparison-2x.png` shows ten fixed full canvases at nearest display2×. `detail-4x.png` magnifies the same fixed crop in every cell; it is a diagnostic, not independently fitted sprite art. Both were actually viewed using the image tool. Final PNGs equal the originally viewed preview pixels exactly.

Both methods are exact original RGBA at 0° through their actual pipelines, without a special zero-angle passthrough. All ten results are repeatable and introduce **zero new RGBA colours**. This is a textured/antialiased 1,745-colour source, not a small indexed palette. No colour quantization or alpha normalization is introduced.

The methods differ at 238/250/0/244/233 pixels for −30/−15/0/+15/+30°. Those counts establish a change, not improvement. At the viewed 2× and diagnostic4× scales, native nearest produces more broken steps on the toe/sole arc and several sharp notches around the gold top rim. The Scale2x approximation makes those diagonal outline clusters less jagged while preserving the recognizable red plate, gold medallion and cream parchment. Some very fine trim/parchment pixels still shift, and the approximation is not uniformly superior at every angle. I would retain it as a selectable candidate for rigid plate rotation and compare the final overlapping body assembly at native scale before choosing it.

Rotation cannot reconstruct the hidden knee/cloth, bend a rigid boot, resolve foot contacts, or establish believable gait. There is no temporal or final animation acceptance here. No claim that keeping the palette proves anatomical/material fidelity. This experiment stays within the canvas at these sampled angles; another part/pivot may clip and needs new bounds checks.

## Repeat

Requires Python3 and Pillow (exact tested version in diagnostics). From this folder:

```sh
python compare.py --output fresh-results
python test_compare.py
```

The script rejects an existing output folder and a stale source hash. The test performs two fresh complete runs and compares every output byte, checks actual zero-angle identity, independently checks one known Scale2x neighbourhood and a +90° fixed-pivot marker, and verifies existing-output rejection leaves the report unchanged. `test-report.json` and `final-results/diagnostics.json` bind current implementation and source hashes. No root files or installed skills are modified.
