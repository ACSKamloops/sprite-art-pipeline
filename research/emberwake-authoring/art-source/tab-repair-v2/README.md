# Brann south-dodge cloth repair candidate

This is a bounded second repair of the remaining gold split waist ornament in **south_dodge f24 and f26**. The v3 bank is the frozen input. Its whole f25 is deliberately unchanged: the foreground glove crosses the waist and the exposed cloth is already red. The reviewed final red-tab pose f27 is also unchanged.

No new paint/model call, whole-body transform, interpolation, palette conversion or automatic segmentation was used. The same-south-view f12 donor is byte-identical in the original v1 and current v3 banks. This revision reuses its existing literal 129-pixel red-tab mask and exact RGBA samples. Integer placement follows the posed belt buckle: f24 `[-3,-1]`, f26 `[-1,-1]`. The smaller changed cloth shape was judged from the full native cel, coordinate-labelled waist grid and alternative placements before selection. Those unselected offset trials are retained for transparency; they are not alternate final banks.

`repair-plan.json` binds the exact target/donor cel RGBA hashes and literal source rows. `repair_dodge_tabs.py` imports the exact copied v1 helper from `inputs/`; no root checkout is required. The helper checks the original target/donor hashes and all four channels outside the authorized masks before any result is written. This wrapper restricts the plan to only f24/f26 and audits all 120 stored cels, including unselected cels/padding. A caller may supply a larger derived bank only when the frozen target/donor hashes still match; the resulting source hash and frozen-v3 match status are recorded explicitly.

## Changed and protected pixels

- Exactly **258 changed RGBA pixels**, 129 in each target cel. Every replacement is an exact donor f12 sample at an integer offset.
- Authorized local-cell boxes, right/bottom exclusive: f24 `[57,74,68,91]`; f26 `[59,74,70,91]`. The actual masks are row-shaped, not full rectangles. PNG mask files and per-pixel donor witnesses are supplied.
- All 118 other 128×128 cels are byte-identical, including the entire f25 glove/hand occlusion, f27, every walk and the donor f12. All head, torso, arm, glove, trouser and background pixels **outside these cloth masks** stay exact; there is no whole-pose alteration.
- No alpha is reduced or erased. Completing the red hanging cloth adds 19 previously transparent pixels in f24 and 17 in f26, inside the declared cloth masks only. These are explicit cloth silhouette additions, not evidence that the old silhouette was unchanged. Another 10 existing partial-alpha samples per cel become more opaque. No new hole is introduced.

The PNG candidate is `candidate/atlas.png`, SHA-256 `88d75c80a1656aeadd9a894c62aa948bf73a3ecde1b128111b1000b8566fd013`. V3 source PNG SHA-256 is `5a5ab930c96c36ac5486e0337f7f3045e21cff25653448ca74c1d1cec7a23c4e`.

## Replay and verification

Requires Python and Pillow. Run from any directory, choosing a new output folder:

```bash
python3 /ABSOLUTE/PATH/tab-repair-v2/repair_dodge_tabs.py --output /ABSOLUTE/FRESH/OUTPUT
python3 /ABSOLUTE/PATH/tab-repair-v2/verify_repair.py
```

`VERIFICATION.json` records an independent coordinate scan, complete cel preservation, exact donor ownership, zero erased alpha, a fresh-process CLI replay producing the same PNG bytes, target/donor mutation rejection before output creation, and refusal to overwrite an existing candidate. The many coordinate assertions are mechanical checks, not independent perceptual ratings. `INPUTS.json` lists exact frozen source/helper hashes; `FILES.sha256` freezes this task folder.

Inspect `candidate/south-dodge-whole-before-after-{1,2}x.png` and `south-dodge-waist-before-after-6x.png` together. The source manifests and animation timing are unchanged. `south-transitions-normal.apng` uses the actual idle → dodge → idle holds: idle 580/580 ms, dodge **45/105/55/55 ms**, idle 580/580 ms. `south-transitions-slow-3x.apng` uses the identical cels with holds multiplied by three for seam inspection. `transition-sequence.json` is the literal order/clock receipt; no intermediate poses were invented.

This is a candidate for integration and independent visual re-review, with no art score. Whole-pose/waist stills were inspected here; the APNGs are timed review artifacts, not a claim of completed human playback acceptance. The parent must replay the changed south dodge and its entry/recovery in the actual selected bank/game after integration. No runtime assets, UI, root source or manifests were modified by this task.
