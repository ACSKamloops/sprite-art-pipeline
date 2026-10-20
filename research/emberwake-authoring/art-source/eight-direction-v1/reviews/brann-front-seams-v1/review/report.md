# Scoped seam follow-up

**Prefer B very slightly for static seam continuity. All scores stay unchanged.** The charcoal additions read as small clothing continuations without a new attachment or material defect. Their effect is negligible at the 84px stage proxy. They provide no new gait evidence.

| Variant | Appearance | Identity | Motion readability | Game usefulness |
|---|---:|---:|---:|---:|
| A — frozen control | 8.0 | 8.5 | 7.3 | 7.6 |
| B — seam follow-up | 8.0 | 8.5 | 7.3 | 7.6 |

A’s 16 PNGs independently match all 16 exact prior-B PNG bytes, and the eight 9/160-second holds and 9/20-second duration match. A’s scores are carried unchanged; the control was not rerated. B’s tiny static improvement does not justify any numerical increase. The first judgment and original review remain frozen and unchanged. This follow-up judgment was assigned once at 2026-10-17T01:22:53.531366+00:00.

## Seam anatomy and clearances

Coordinates are zero-based native 128×128 source coordinates.

| Site | Static perception |
|---|---|
| SE02 `(50,83),(50,84)`; SW02 `(78,83),(78,84)` | A tiny ground-colored notch at the dark hem/upper-leg junction becomes a slightly more continuous charcoal contour. This is easiest to see on the light/muted 2× close-ups. The surrounding limb/hip read stays coherent; no broad bridge across leg space appears. This preference does not establish that A had a severed limb. |
| SE06 `(80,79),(80,80)`; SW06 `(48,79),(48,80)` | The opposite waist/side-seam notch becomes a continuation of the existing dark clothing. The added pixels introduce no conspicuous material switch, floating piece, or glove-to-torso weld. |
| Retained SE06 `(50,83),(50,84)`; SW06 `(78,83),(78,84)` | These remain transparent in A and B. The opening reads as legitimate clearance beside the hanging arm/hip contour and should remain open. Alpha-zero pixels/components alone are not anatomy errors. |

At the 84px proxy, the A/B seam distinction is too small to support a practical game-usefulness difference. Both retain the prior crowded similar-brown passing-pose boots in SE03/04, native region roughly `[53,86,84,115]`, and mirrored SW region `[44,86,75,115]`. The edits leave that foot-order readability limit intact.

No new attachment/material defect is visible in the reviewed stills. The patches preserve clothing, hip, glove and boot identity. Natural arm/leg negative space is retained; no blanket hole-filling rule is warranted.

## Exact scope and cyclic coverage

Verified exactly four changed native pixels in SE, plus four mirrored pixels: two in frame 02 and two in frame 06 per direction. All other RGBA pixels are identical. Details and exact colors are recorded in [control-and-diff-verification.json](control-and-diff-verification.json). The retained opening is recorded in [retained-clearance-check.json](retained-clearance-check.json).

Viewed all 32 animation cels and all 32 cyclic adjacent pairs, including four 7→0 wraps, with `view_image`: native 128px stage, nearest 2×/256px, and nearest 84px, each on light RGB(234,231,222), dark RGB(27,31,38), and muted RGB(111,123,113). Each of the nine coverage sheets contains all cels and all explicit pairs. [The seam anatomy sheet](seam-anatomy-2x.png) provides compact unpainted 2× crops on all three grounds. Exact pair sheet origins are in [coverage.json](coverage.json).

| Pair | A SE / SW control | B SE | B SW |
|---|---|---|---|
| 00->01 | Both viewed; carried control, no rerating. | A/B pair is unchanged. Static attachment and material read retained. | Mirrored case independently viewed; same finding. |
| 01->02 | Both viewed; carried control, no rerating. | Entering edited 02: B gives a slightly more continuous dark hem/upper-leg junction; no broad glove-to-body or leg-to-leg bridge is apparent. | Mirrored case independently viewed; same finding. |
| 02->03 | Both viewed; carried control, no rerating. | Leaving edited 02: small B seam continuation gives no extra discontinuity apparent in the still pair; boot-overlap limit persists. Timed flicker was not tested. | Mirrored case independently viewed; same finding. |
| 03->04 | Both viewed; carried control, no rerating. | A/B pair is unchanged; the crowded same-brown passing boots remain a shared readability limit. | Mirrored case independently viewed; same finding. |
| 04->05 | Both viewed; carried control, no rerating. | A/B pair is unchanged; torso/glove/hip material read retained. | Mirrored case independently viewed; same finding. |
| 05->06 | Both viewed; carried control, no rerating. | Entering edited 06: B closes the tiny opposite waist/side-seam notch; the existing open arm/hip clearance remains visible. | Mirrored case independently viewed; same finding. |
| 06->07 | Both viewed; carried control, no rerating. | Leaving edited 06: no new attachment/material break is apparent in the still pair; no timing or gait advantage established. | Mirrored case independently viewed; same finding. |
| 07->00 wrap | Both viewed; carried control, no rerating. | A/B wrap pair is byte-identical. No new entry/exit or loop-boundary change exists. | Mirrored case independently viewed; same finding. |

Every table entry was viewed at all nine size/ground combinations. At 01→02, 02→03, 05→06, and 06→07 the small drawing change fits the adjacent pose without a new broad discontinuity apparent in the still pair. This statement does not establish absence of timed flicker. The 7→0 wrap and entry/exit images are byte-identical between A and B.

## Static perception limits

Exact holds are 56.25 ms each, with a 0.45-second loop. Timing was read from the manifests. No continuous animation playback, engine/browser run, world travel, foot locking, floor loading, grounded contact, renderer filtering, or live turn blending was observed. Four seam pixels do not imply better gait. The 84px stage approximates 128×0.66=84.48 and does not certify actual engine sampling.

Read only the new nominated input and the prior input B files/manifest needed for the explicit control check. No producer directories, root project/docs, other grades, case-history skills, or prior review files were read. Wrote only `/home/astra/artifacts/emberwake-brann-front-seams-review-v1/review`. No generation model, runtime control, input edits, canonical asset writes, or source changes were used. Work amount, pixel count, exposure count and preservation earn no points.

## Integrity

**All 63 PNGs and INPUTS.json were hashed before and after. Every binding matches; all 64 files remain unchanged.** Prior control PNG hashes were rechecked at completion. Manifest SHA-256: `6488a06a61b2157180413e4865aa45e29bb30815219c2e9cd8c498a48bc66c7b`.

Ledgers: [before JSON](hashes-before.json), [after JSON](hashes-after.json), [before SHA-256](hashes-before.sha256), [after SHA-256](hashes-after.sha256). Structured judgment: [report.json](report.json). Useful full views: [native light](coverage-128-light.png), [2× light](coverage-256-light.png), [84px light](coverage-84-light.png), [84px dark](coverage-84-dark.png).
