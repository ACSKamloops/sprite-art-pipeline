# Anonymous walk-cycle visual review

**Frozen preference: B, by a small margin.** B gives a clearer upper-body rise at passing poses 02/06 and descent toward extended poses 00/04. Both keep the same convincing character and material identity. The shared boot-overlap limits remain. This preference is inferred from chronological stills; no timed continuous playback was performed.

| Variant | Appearance | Identity | Motion readability | Game usefulness |
|---|---:|---:|---:|---:|
| A | 8.0 | 8.5 | 6.8 | 7.2 |
| B | 8.0 | 8.5 | 7.3 | 7.6 |

Scores are absolute 0–10: 5 = recognizable with substantial defects; 7 = competent with noticeable limits; 8 = strong; 9 = exceptional. Work performed, pixel count, exposure count, and preservation earn no score. Judgment was assigned once after the full inspection and is frozen at 2026-10-17T01:19:31.660581+00:00.

## Visible findings and attachment checks

Both sets preserve the curly dark hair, face/beard, gold shoulder armor and bracers, navy tunic with gold trim, warm belt/tab, brown gloves, and heavy boots shown in the appearance/cardinal context. These material groups stay recognizable at the 84px proxy. Torso/hip, clothing, glove/bracer, and boot/leg relationships remain visually coherent. I found no conclusive floating glove, severed waist, or detached boot. Legitimate far-limb occlusion and arm-to-torso clearance should remain; they should not be filled merely to force separation.

All coordinates below use zero-based native 128×128 source coordinates, with approximate inclusive review regions [left, top, right, bottom].

| Finding | Type | Visible evidence / remaining limit |
|---|---|---|
| F1 — A | inferred motion | The shoulder/head/torso mass stays unusually level while the legs do most of the action. At passing frames 02/06 the head is slightly lower than at 00/04; the chronology gives a comparatively weak rise over the support leg. This reads more like legs cycling beneath a held upper body than a fully weighted walk. SE region `[38, 15, 94, 85]`; SW region `[34, 15, 90, 85]`. Frames: SE00..07, SW00..07. |
| F2 — A/B | static readability | The two similar-brown boots overlap into a compact lobed silhouette in the passing poses. At the 84px stage proxy, which boot leads is less immediate than in frames 00/07. The overlap is anatomically plausible and is not evidence of a detached leg. Do not fill valid negative clearance to force a split. SE region `[53, 86, 84, 115]`; SW region `[44, 86, 75, 115]`. Frames: SE03, SE04, SW03, SW04. |
| F3 — A/B | static material contrast | Hair edges and dark shorts/tunic edges lose contrast against the dark ground, most clearly at the 84px stage proxy. Gold armor and face highlights preserve recognition, but the lower torso/hip silhouette is less crisp there. This is a background-dependent presentation limit, not missing body material. SE region `[40, 15, 89, 94]`; SW region `[39, 15, 88, 94]`. Frames: SE00..07, SW00..07. |
| F4 — B | inferred motion | The clearer upper-body rise/fall does not resolve the compressed passing-pose boots or establish foot loading. Lower-leg and boot chronology remains broadly the same visual action as A; the added body motion gives a modest weight cue rather than a complete demonstration of grounded steps. SE region `[43, 83, 93, 117]`; SW region `[35, 83, 85, 117]`. Frames: SE00..07, SW00..07. |

B’s head top follows native y = 17,16,15,16,17,16,15,16; A follows 16,17,17,16,16,17,17,16 (alpha ≥128, within the head region). These measurements locate the visible rise/fall; pixel counts themselves do not determine scores. In the still chronology, B’s higher passing poses and lower extended poses give a more coherent weight cue. The difference remains modest, and the lower-body silhouette is substantially shared.

The 7→0 pairs show continued stride development without a distinctive head, armor, material, or direction reset. Cardinal context and walk entry/exit remain consistent in actor identity. Actual idle-to-walk or direction-changing blends were not tested. Both SW sets were inspected in full. A composite geometry check confirms the displayed SW view is the SE reflection about pivot x64 (flip-left-right plus +1 x offset).

## Scope, timing, and evidence

Read only: `/home/astra/artifacts/emberwake-brann-front-weight-review-v1/input`. Wrote only: `/home/astra/artifacts/emberwake-brann-front-weight-review-v1/review`. No parent mapping, producer directory, root project/docs, previous reviews/grades, or case-history skill was read. No generation model, engine, browser, or canonical/source edit was used.

Inspected every one of the 32 animation cels and 32 cyclic adjacent pairs, including four 7→0 wraps, with `view_image`: native 128px stage, nearest 2× (256px), and nearest 84px proxy; each on light RGB(234,231,222), dark RGB(27,31,38), and muted RGB(111,123,113) grounds. The nine coverage sheets each contain all 32 cels plus all 32 explicit pairs. The compact attachment crop sheet adds native coordinates. Appearance and all 30 cardinal sprites establish identity/context only. The appearance original was also viewed at its native 768×256 size.

Manifest timing is eight equal holds of **9/160 s = 56.25 ms**, totaling **9/20 s = 0.45 s**. That timing was read, not played back. The 84px stage is a diagnostic approximation of 128×0.66 = 84.48px. No claim is made about human-tested smoothness, real engine filtering, world travel, foot locking, floor contact, collision, or grounded weight. Game-usefulness scores concern visible art/readability only.

Useful starting sheets: [native muted](coverage-128-muted.png), [2× light](coverage-256-light.png), [84px light](coverage-84-light.png), [84px dark](coverage-84-dark.png), [attachment comparison](attachment-comparison-2x.png), [identity context](context-identity.png). All nine scale/background sheets are listed in [report.json](report.json). Exact pair locations are in [coverage.json](coverage.json).

## Complete cyclic coverage

| Pair | A SE | B SE | A SW | B SW |
|---|---|---|---|---|
| 00->01 | Stride begins to close; upper mass lowers slightly. Attachments remain readable. | Stride begins to close while upper mass rises slightly; clearer recovery cue. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 01->02 | Rear boot recovers; upper mass stays near the same height, limiting the passing-pose rise. | Rear boot recovers as the upper mass reaches its higher passing pose; attachment remains continuous in the still pair. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 02->03 | Feet enter the crowded passing cluster; no conclusive detached boot, but leading-foot clarity falls. | Feet enter the same crowded passing cluster; upper mass starts descending. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 03->04 | Overlap rolls into the alternate-foot pose; boot/toe separation remains limited. | Overlap rolls into the alternate-foot pose while upper mass descends; boot/toe separation remains limited. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 04->05 | Boot stack begins its next recovery; upper mass lowers rather than giving a clear passing rise. | Boot stack begins recovery and upper mass rises; hip/glove shapes remain coherent. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 05->06 | Far boot becomes partly hidden by the near leg/hip; legitimate occlusion, with limited foot-order clarity. | Far boot is partly hidden; upper mass reaches its higher passing pose. Negative clearance is retained. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 06->07 | Legs reopen and the two boots become easier to distinguish; no direction or material reset. | Legs reopen as upper mass descends; boots become easier to distinguish. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |
| 07->00 wrap | Wrap advances the extended stride with a small pose change; no special head/armor/identity reset visible. | Wrap continues the descent into the extended stride; no special head/armor/identity reset visible. | Viewed; mirrored A finding. | Viewed; mirrored B finding. |

Every table entry was inspected at all three requested sizes and all three grounds. Findings distinguish static readability from inferred motion; pair coverage is not continuous playback.

## Input integrity

**63 bound PNGs plus INPUTS.json were hashed before and after; all 63 bindings match and all 64 files are unchanged.** No extra input file appeared. The manifest SHA-256 is `e5b1edefb9bbc9862cd8df0e664325a00a76a7bb6d237fa3ef31303065ae8e9e`.

Ledgers: [before JSON](hashes-before.json), [after JSON](hashes-after.json), [before SHA-256](hashes-before.sha256), [after SHA-256](hashes-after.sha256). Structured judgment and limits: [report.json](report.json).
