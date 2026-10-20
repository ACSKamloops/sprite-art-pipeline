# Brann SE three-pose candidate

Unselected source-pixel lower-body experiment. Only03/04/05 change from frozen near-attachment-v5. No new model call, rear edit, other-hero edit, or physical-contact claim. The earlier ImageGen04 cleanup remains rejected in its separate evidence folder.

Start with `proof/02-03-04-05-06-native.png`, `proof/full8-066.png`, and `normal-clock-v5-vs-trial-8loops.mp4` (v5 left, candidate right). Actual128x128 exposures are `frames/00.png`–`07.png`; the clock remains8×9/160 seconds=.45 seconds. APNG contains exactRGBA exposures and exact56.25ms holds. MP4 is a lossy2x nearest display preview.

| Exposure | Source-pixel operation |
| --- | --- |
|03 rear/right | Actual02 screen-right visible leg/boot translated(-1,-3). |
|03 passing/left | Actual07 screen-right pitched visible boot: x-17; vertical5/6 projection about source y93→target y91, inverse nearest. **This changes the silhouette and is not an unscaled source-perfect boot.**379 positive source pixels become319 placed positive pixels before upper occlusion. |
|04 | Earlier source-guide04 PNG exact:00 right boot→left forward(-15,0);00 left folded boot→right rear(+24,-1). |
|05 rear/right | Actual07 screen-left bent visible boot translated(+16,-3), behind foreground leg and the literal06 rounded rear-thigh surface. |
|05 foreground/left | Actual06 foreground visible leg/boot translated(-1,+1). |

The projected roles are an authored gait hypothesis. Labels identify source view, phase and screen position; they do not establish persistent anatomical left/right limbs or measured ground planting. Cutouts retain visible source surfaces; hidden anatomy is unavailable. Complete upper-body and arm owners remain exactRGBA v5 in all8. Exposures00/01/02/06/07 remain exact v5 PNG bytes. All palette colors and transparent contour removal have explicit owners. The existing v5 upper masks, including exterior arm space, are preserved.

I inspected03/04/05 hip, knee/cuff and boot joins on light and dark12x crops and native/.66 chronology. No art pixels changed after the root's inspected candidate. This inspection supplies no acceptance or anatomy certification.03→04 still changes boot pitch/projection;05's rear thigh and boot rely on overlap rather than a fully exposed complete limb. These are visible review points.

`RECIPE.json` owns03/05 transformations and literal charcoal-trouser donor pixels. `inputs/guide04-recipe.json` owns04. Every raw source cel is in `inputs/v5-frames/`; complete v5 upper layer witnesses are in `inputs/v5-layers/`. `maps/*.npz` store actual destination→sourceXY and sourceRGBA witnesses. `masks/` distinguish source scope, preserved upper, old-lower erasure, positive final contribution and later opaque occlusion. A contribution mask means nonzero source contribution under straight-alpha compositing: alpha255 later owners fully occlude;1–254 partially overlay. It is not a perceptual visibility or anatomy score.

`project.json` is the actual five-layer editor project: baseline with lower erasure, authored charcoal, rear source part, proximal source thigh, foreground source part. `initial-project.json` renders exact v5. `journal.json` contains three actual expected-hash guarded editor transactions, with literal masks and paint points including transparent erasure. The portable toolkit is copied in `toolkit/sprite_lab/`; no canonical checkout changes are required.

Replay into a fresh absolute directory:

```bash
python scripts/replay.py --output /absolute/fresh/replay-folder
```

Replay independently recomputes declared part transforms, validates raw sourceRGBA and every literal join, reconstructs all layers, compares all8 actual PNGs and editor renders, checks full upper/endpoints/timing, and exercises journal undo/redo. `EDITOR-RECEIPT.json`, `replayed-frames/REPLAY-RECEIPT.json`, `GUARD-RECEIPT.json`, `MEDIA-RECEIPT.json` and `MANIFEST.json` record the exact checks. `SHA256SUMS` freezes the files. No further expansion is selected.
