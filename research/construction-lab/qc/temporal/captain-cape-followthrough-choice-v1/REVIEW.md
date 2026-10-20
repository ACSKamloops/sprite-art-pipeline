# Independent cape follow-through choice

**Retain the crease baseline for this component choice.** Confidence is moderate. The candidate is coherent and does not visibly damage the Captain, but its whole-figure improvement is too small to select as the cloth-motion repair. This is not a new complete-sprite score or a 9/10 claim.

## Viewed evidence

CPU freeze `79e06eb`: visually viewed complete baseline/candidate pairs at native256 and native384 for actual source 49/65/93/113, plus source 1/131 endpoints. The384 support/recovery sheet was split into two 768×816 sheets without scaling. Independently verified all 56 CPU receipt assets with zero mismatches; receipt SHA256 `24f0ddbe249b370fa65a4346c9ca52ad177e00b996ee620cb72dd0691ad85d16`.

GPU audition freeze `a6a6866`: independently decoded and visually inspected all 66 chronological frames from each actual MP4: baseline normal, baseline half, candidate normal, candidate half. Each stream covers first-cycle indices 0–64 plus first next-cycle/wrap index 65: **264 actual decoded images total**, displayed in 44 bounded 840×768 native384 contact sheets. Normal encodes 60 fps and half 30 fps; their 195-frame/three-cycle files were not visually inspected beyond the first wrap. No crop-only motion review substitutes for these whole figures. Independently verified all 566 audition receipt assets with zero mismatches; receipt SHA256 `63faf0ae7eed1dd8eefcc92abe58b573d7ab4447a9171afbaeed172654830d4b`.

Exact videos, decoded images, sheets and hashes are recorded in `coverage.json` and bound in `EVIDENCE-SHA256.json`. Producer files were read-only; no source or production edits.

## Visual choice

The candidate changes the visible hem position and its lateral spread slightly. This is easiest to see around CPU 49/65 and the corresponding middle-cycle GPU poses. At native256 it is a small outline difference rather than a clear upgrade in cloth character. Native384 makes the shifted lower edge easier to follow, but the large tan/gray surface still reads as a broad panel behind the shield.

Across the chronological candidate frames, the visible lower cape progresses steadily rather than jumping. I see no obvious equipment break, clipping of a major feature, or seam snap at 64→65. The source 1/131 CPU endpoint pairs also look consistent. This supports coherent execution, not an excellent cloth-motion result.

The key visual limitation remains: the long outer edge and gold lower border preserve a comparatively straight, angular shape while the lower panel moves a little sideways. The visible movement reads primarily as small displacement of that broad panel. I do not get a clear progression of different folds yielding, lagging and settling that would make the material look appreciably softer. The candidate is not worse enough to reject for damage; it simply does not establish a worthwhile gain over the already readable baseline. Larger displacement alone would not necessarily address that concern.

The baseline already includes crease shading, compact-head and sole changes. Their clarity is not credited to the follow-through layer. Body and contact preservation checks receive no art points.

## Limits

Viewing decoded video images is discrete chronological inspection, **not continuous real-time video ingestion**. Perceived cadence, physical weight and small-detail shimmer remain provisional. No motion improvement at native256 beyond the covered CPU poses is established; the chronological audition is 384 only.

The CUDA preview is exploratory visual evidence, not CPU pixel proof. The producer's overlapping-key observation records GPU-versus-CPU maxRGBA differences 6–58 over 239–285 pixels. These are not covered by a universal 1 LSB repeat guarantee. The compared GPU variants were rendered under matched conditions, but the audition does not replace the separate authoritative CPU preservation/reopen gates. No future differential-fold trial is included or credited here.
