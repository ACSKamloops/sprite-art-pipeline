# Cold independent diagonal-walk review

Frozen: 2026-10-16T18:47:40+00:00

These are recognizable, attractive provisional game sprites. I would use the set in a playable prototype. Polished final-art acceptance still needs targeted front-thigh cleanup, clearer front pose progression, and clearer rear passing legs. Identity is the strongest category; motion is the weakest.

| Loop | Appearance | Identity | Motion* | Usefulness* |
|---|---:|---:|---:|---:|
| Rowan southeast | 7.0 | 8.5 | 5.5 | 6.5 |
| Rowan northeast | 7.5 | 8.5 | 6.5 | 7.0 |
| Rowan southwest | 7.0 | 8.5 | 5.5 | 6.5 |
| Rowan northwest | 7.5 | 8.5 | 6.5 | 7.0 |
| Lyra southeast | 6.5 | 8.5 | 5.5 | 6.0 |
| Lyra northeast | 7.5 | 8.5 | 6.5 | 7.0 |
| Lyra southwest | 6.5 | 8.5 | 5.5 | 6.0 |
| Lyra northwest | 7.5 | 8.5 | 6.5 | 7.0 |
| Category mean | 7.1 | 8.5 | 6.0 | 6.6 |

All scores are independent judgments out of 10. 5 means serviceable with conspicuous issues; 8 means strong with minor issues; 10 means exceptional polish. File counts, metadata, process effort, and correctness of packaging earn no art credit.

*Motion and usefulness are qualified: I inspected the full static chronology, including every cyclic predecessor, but did **not** observe continuous playback. I did not watch the 450 ms loop running or see translated in-engine motion. These scores judge pose continuity and readability; smoothness, cadence, contact, and sliding remain unverified. `playback.html` is an offline aid for a subsequent human check, not evidence of a performed playback check.*

## Scope and coverage

Only sibling `input-v1/INPUTS.json`, its listed PNGs, and `rowan-reference.png` / `lyra-reference.png` were read. No `REVIEW-CARD.md` was present. No producer reports, prior scores/reviews, parent history, or other producer folders informed this review.

All 64 diagonal keys and all 64 ordered cyclic edges were inspected in the order **07→00→01→02→03→04→05→06→07→00**. Each loop was viewed on light, dark, and patterned ground at native size, nearest 2×, and game size. Native sheets retain the 128×128 stage; 2× sheets enlarge an alpha-enclosing 80×112 crop, with no sprite alpha clipped. Game sheets use a nearest-rounded84 px stage, an effective .65625 scale: the nominal .66 stage is84.48 px. Fractional engine sampling and pixel snapping were not tested. The HTML aid uses exact .66 CSS dimensions.

Timing authority is eight equal 9/160-second holds (56.25 ms), total 9/20 second (450 ms), pivot (64,112). Adjacent cardinal art was examined for identity and view-turn context only. All 144 supplied expected PNG hashes match. The two reference PNGs were also hashed; no expected reference hashes were supplied. See `source-hash-ledger.json` / `.tsv`.

## What reads well

Rowan retains the warm spiky hair, blue-and-gold costume, pale trousers, and silver armor. Lyra retains the silver hair, dark green/teal clothing, scarf/cape and brown boots. Both match the reference and cardinal family and remain distinguishable at game scale. Hair and armor/glove/boot shading generally describe solid forms; the rear upper bodies stay especially stable. The directions and alternating strides are usable.

## Remaining visible local defects

**V1 — rowan, southeast, southwest, keys 01, 07.** The cream edge folds into a squared, bracket-like notch with a flat dark slit. Key 07 has the clearest rectangular opening. This edge looks cut out beside the rounded shaded near thigh; it is a local contour/material problem, not proof of a missing limb. The precise notch is reduced at game scale; the angular light/dark flash remains easier to see on light and ground than on dark.
Region: inner edge of raised/far cream thigh, immediately below the foreground glove and above/alongside its boot. Evidence: `diagnostics/rowan-southeast-nearest2x.png`, `diagnostics/rowan-southwest-nearest2x.png`, `diagnostics/rowan-local-lowerbody-4x.png`.

**V2 — lyra, southeast, southwest, keys 01, 07.** Key 01 has a flat charcoal horizontal block across the far thigh; key 07 expands it into a squared dark tab with a thin vertical spur at the inner edge. These planes do not share the curved shading/volume of the adjacent trouser leg and boot. The blocky seam is particularly clear against light and ground. At game scale it becomes a dark bar under the coat rather than a clear bent thigh.
Region: far upper trouser leg below the coat hem; screen-left for southeast and screen-right for southwest. Evidence: `diagnostics/lyra-southeast-nearest2x.png`, `diagnostics/lyra-southwest-nearest2x.png`, `diagnostics/lyra-local-lowerbody-4x.png`.

**V3 — rowan, lyra, southeast, southwest, keys 04, 05, 06, 07.** At 04 to 05 the broad chest/arm presentation changes to a much narrower, strongly side-presented pose. The near forearm crosses the waist and crowds the raised thigh; 05 to 06 separates the knee, then 06 to 07 restores the earlier arm/body presentation. The change is larger than the neighboring increments and reads as a body swivel in the static chronology. This silhouette change remains visible at game scale, even when the small surface defects are reduced.
Region: shoulders, near forearm/glove, waist, raised knee. Evidence: `diagnostics/rowan-southeast-game066.png`, `diagnostics/rowan-southwest-game066.png`, `diagnostics/lyra-southeast-game066.png`, `diagnostics/lyra-southwest-game066.png`.

**V4 — rowan, lyra, northeast, northwest, keys 05.** Key 05 gathers the two boot shafts into a tight crossed brown cluster at lower center. The inner thigh/shin connections are harder to follow than at 02, 03, or 06; at game scale the feet nearly merge into one lower mass. This is weak limb separation, not an asserted extra limb or impossible pose. The merged lower silhouette is visible on all three backgrounds, most strongly on dark.
Region: crossed lower legs and boots below the coat/tunic hem. Evidence: `diagnostics/rowan-northeast-nearest2x.png`, `diagnostics/rowan-northwest-nearest2x.png`, `diagnostics/lyra-northeast-nearest2x.png`, `diagnostics/lyra-northwest-nearest2x.png`.

These observations concern the actual visible anatomy, surfaces and pose changes. They do not establish broken rigging, missing limbs, or a particular production method. The bright/dark thigh defects are local; they do not invalidate the otherwise readable character identities.

## Full-chronology motion account

Both southeast and southwest loops were inspected independently for each actor. Their visible progression has the same broad strengths and weaknesses:

| Cyclic edge | Front-diagonal observation |
|---|---|
| 07→00 | similar upper-body presentation; boot extension gives a small cycle-boundary change. No conspicuous wrap-only discontinuity in the static pair. |
| 00→01 | near boot extends/downward while far leg compresses. The local thigh contour/tab changes described in V1/V2 are exposed here. |
| 01→02 | stance and shoulder/arm presentation open noticeably; readable stride change, but body exposure changes more than in the prior edge. |
| 02→03 | legs narrow toward passing; the near boot and glove placement progress in a comprehensible direction. |
| 03→04 | legs cross the body center while the broad torso presentation is retained. Occlusion increases but the leg order can still be inferred. |
| 04→05 | largest arm/waist silhouette change; chest narrows, forearm crosses the abdomen, knee crowds it. V3 is most evident here. |
| 05→06 | raised knee separates and the other boot extends; the high knee reads clearly as a pose, though the body remains strongly side-presented. |
| 06→07 | upper body returns to its earlier oblique presentation and the far leg swings back. This edge deserves more interpolation than the relatively quiet 07→00 wrap. |

Both northeast and northwest loops were likewise inspected independently for each actor:

| Cyclic edge | Rear-diagonal observation |
|---|---|
| 07→00 | oblique back view remains stable; a modest boot extension closes the cycle without a conspicuous wrap-only jump in the static pair. |
| 00→01 | legs compress toward passing while back/hair identity remains consistent. |
| 01→02 | rear boot sole becomes more exposed and the other leg lengthens; shoulder/back presentation also straightens slightly. |
| 02→03 | legs narrow; one longer supporting-looking boot remains readable. Actual support/contact cannot be established from this alone. |
| 03→04 | the advancing boot crosses the center line; tighter but still traceable. |
| 04→05 | both boot shafts collect at lower center; this is the least legible passing pose (V4). |
| 05→06 | the silhouette opens into a long leg and a bent other leg; the release from the preceding knot is fairly large. |
| 06→07 | legs return to the wide oblique stance and the back rolls toward its initial angle; a comprehensible but visible body/leg reset. |

The relatively small 07→00 change does not prove a smooth loop. The larger internal changes at 04→05 and 06→07 must be evaluated as part of the complete cycle. The machine-readable transition ledger contains an entry for every actor/direction/key and its predecessor.

## Playback and contact hypotheses

The front body-exposure changes may produce a swivel/pop when looped, and the high knees may read as a brisk march or skip. Those are playback hypotheses based on the full chronology. I cannot confirm their perceptual strength at 450 ms without watching timed playback. Foot sliding and actual supporting-foot contact cannot be judged from isolated stage images without world translation and ground contact evidence.

## Scoped result and next work

Use the set provisionally. Repair Rowan front 01/07 thigh contours and Lyra front 01/07 flat trouser tabs; soften the front 04→05→06→07 body/arm change; separate the rear 05 boot/shin connections. Then watch all eight loops at exact 450 ms, .66 draw, with translated ground and intended walking speed. This review does not grant runtime/contact acceptance.

`diagnostics/` contains 24 scale/background chronology sheets, two complete cardinal context sheets, two reference copies, and two supplementary 4× lower-body sheets. `SHA256SUMS` freezes the report, JSON, ledgers, diagnostics and local reproduction/playback aids. Hash verification is evidence of artifact integrity only.
