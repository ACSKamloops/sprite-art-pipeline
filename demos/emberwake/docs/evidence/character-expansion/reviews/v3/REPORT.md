# Frozen v3 follow-up art review

**V3 is a real local improvement. Lyra: 7.4/10 overall. Brann: 7.1/10 overall.** Both are usable prototype sets; this is not a polished-motion or human normal-speed acceptance. Keep the new passing geometry. Brann still needs a small waist-feature closure in south dodge.

| Character | Drawing | Brief fit | Consistency | Motion | Usefulness | Overall |
|---|---:|---:|---:|---:|---:|---:|
| Lyra | 8.0 | 7.7 | 7.7 | 6.8 | 7.4 | 7.4 |
| Brann | 7.8 | 7.6 | 7.2 | 6.4 | 7.1 | 7.1 |

Drawing/brief-fit ratings are unchanged from v1. Improvements are localized to the changed gait, feature consistency, and attachment usefulness. Unchanged clips did not earn new motion or drawing points. Whole-set scores are holistic; confidence per dimension is in `scores.json`.

## What was verified and transferred

Nominated v3 files were each character's atlas, `animations.json`, selected contact sheet and walk proof. All eight were hashed; source files were read only. V1's original six source hashes still match its frozen ledger. No receipts, generator inputs or source code were used as art-approval evidence.

`COMPARISON.json` compares every selected RGBA cell, every hold and loop flag against v1. All holds and loop flags are identical. **Lyra transfers 22 complete clips**; only south/north walk pixel sequences change. All 112 original Lyra cells are exact matches, with new cells 112–115 added. **Brann transfers four complete clips**: east/west walk and attack. Twenty clips need fresh review because of changed selections or waist pixels. Brann has exactly 27 changed original cells, each bounded to the waist feature, plus four added passing cells. Transfer does not cover altered idle/action joins merely because the action itself matches.

Fresh inspection included all changed walk pairs/wraps, both idle phases into/out of the front/back walks, all Brann action/idle joins, the changed garment pixels, full changed clip chronology, and release-palm markers. Native crops, nearest 2× sheets, light-background approximate 0.66 draw scale (84 px cell), and 3×/4× diagnostic lower-body/waist crops were inspected. Existing v1 acceptance limits remain for transferred clips.

**Motion assessment reconstructs decoded chronology and exact holds. No human normal-speed perception, browser/gameplay, world-foot-contact or export approval is claimed.** Root's separate browser QA contributes no art points. Exact-hold APNGs were generated, every decoded frame checked against source crops, and actual rational delays verified. The player was not launched. All walk presentations still last 56.25 ms and each walk remains 0.45 s.

This is a disclosed v1→v3 follow-up, not a blind review. V1's incidental general-skill/early-lineage exposure qualification persists. I did not open other scored reviews or unselected regeneration candidates.

## Passing geometry and boot fit

The new f112/f113 (south) and f114/f115 (north) bring the feet closer through passing instead of switching straight between long extended-leg silhouettes. Thighs connect plausibly to the preserved pelvis and the ankles remain connected; no gross cut line or detached-foot defect was demonstrated. This is a genuine drawing/chronology improvement. Lyra's mirrored lower-leg reuse is explicit and is judged on the selected result, not counted as separately authored anatomy.

The new boots remain in the correct brown-leather family, but are **smaller/rounder and slightly warmer/brighter** than adjacent extended-contact boots. This is clearest around Brann north f58→114→61 and f63→115→56, and milder in Lyra. Some size change is plausible foreshortening, so this is a low-to-medium polish concern rather than a claim that every smaller boot is anatomically wrong. At draw scale the contrast is less intrusive. Keep the passing relationship; refine cuff/boot volume and highlight vocabulary against the neighboring poses, then compare at the same 0.45 s duration. A source-preservation proof does not answer this visual fit question.

Brann's previous f56→57→58 right-left-right contradiction is removed. Current north walk begins f56,f56,f58, then the new passing cel. The repeated f56 is one pose shown for 112.5 ms; it fixes the contradictory phase but creates no new geometry. Whether that plateau is perceived as a hitch requires normal-speed A/B. I do not infer a hitch solely from duplication.

## Garment and attachment result

Brann's repaired idle/cast/return cells now retain a red-orange cloth feature much more consistently. The prior disappearance between north idle f70/f71 and cast neutral/action states is substantially reduced. Small shape/trim differences remain across body turns, but no broad redraw is justified.

**Top remaining concrete repair: south_dodge f24 and f26 still expose the short gold forked waist ornament; repaired f27 has the longer red-orange tab.** The change at f26→27 persists. Inspect partly occluded f25 without overwriting the glove. Use a source-attached patch only on the exposed feature, then recheck f24→25→26→27 and both idle joins. See `brann/south-waist-v3-4x.png` and `brann/south-2x.png`.

Cast markers now land on or much closer to the chosen glove/palm pixels, particularly the corrected east/west anchors and Brann north. The palm artwork is unchanged and receives no new drawing score. Lyra north's marker is unchanged from v1; it is on the lower hand/wrist area rather than the upper fingers, but not a demonstrated off-body attachment in the nominated release still.

Attack→idle stance closure remains unchanged: f13→14, f41→42, f69→70 and f97→98 still switch from wide raised guard to narrower arms-down neutral. Once the concrete waist gap is closed, a short settle drawing is the next whole-library polish task. The passing edit does not improve untouched attacks.

## Frozen evidence

- `lyra/scores.json`, `brann/scores.json`: ratings, confidence, improvements, ranked remaining repairs.
- `COMPARISON.json`: exact selected-pixel/hold transfer, changed cell bounds, metadata changes and canonical eight-file hashes.
- `INPUTS.json`, `VERIFICATION.json`: source fingerprint, unchanged-source verification and exact APNG delays.
- `*/pairs/*_walk-2x.png`: every current gait pair and wrap.
- `*/pairs/*-idle-joins-native.png`: explicit action endpoints against both idle phases.
- `*/{south,north}-lowerbody-3x.png`: selected gait anatomy bound to complete sprites.
- `brann/*-waist-v3-4x.png`: all original selected feature drawings; `changed-cells-v1-v3-native.png` binds patches to baseline.
- `*/media/*.png`, `player.html`: exact-hold follow-up media; creating these is not human motion acceptance.

Reproduce in order with installed Pillow; all writes stay in this review folder:

```bash
python3 /home/astra/artifacts/emberwake-character-review/v3/review_assets.py
python3 /home/astra/artifacts/emberwake-character-review/v3/compare_inputs.py
python3 /home/astra/artifacts/emberwake-character-review/v3/waist_evidence.py
python3 /home/astra/artifacts/emberwake-character-review/v3/freeze_v3.py
```

Canonical eight-file input fingerprint: `1106c8871388113f77aab2e77e7cec1efb452b3e2ec43469af5ec679eee1c509`.

| Character | File | SHA-256 |
|---|---|---|
| lyra | atlas.png | `d4237eba0003ada103b3e17ba76f14427c5a317fd847437aaf2ddae31f5619e8` |
| lyra | animations.json | `2936a6a5ad0b965f299cf50111e5964997c53dfb6a87ca485d8b157688bb783b` |
| lyra | selected-contact-sheet.png | `a8abb523777ff982ecbd66f73a4d218e78b1ef1a0cddcd336d52fc59092950e4` |
| lyra | walk-proof-2x.png | `ab04d61afd1294b1d4af1c4b4f7783fa9b9c565e3f76ecedf61f8ef8f83c794f` |
| brann | atlas.png | `5a5ab930c96c36ac5486e0337f7f3045e21cff25653448ca74c1d1cec7a23c4e` |
| brann | animations.json | `35eaaa5b894214b1642f9f81c2d010426ded1f09b3b658c9d86ec6ccc1ba91a6` |
| brann | selected-contact-sheet.png | `eaa1ee8822b29a134e94b6095fdd42f39dba58e2380ef1cca6fe7a936a1d758a` |
| brann | walk-proof-2x.png | `d4b268fb807aea591b28740e080a3a348bc62b9b12ed90cd525db45871ddb760` |

Changed art or holds invalidate the applicable scope. This review transfers no approval to a later candidate.
