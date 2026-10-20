# Paired Brann NE/NW jab review

**Decision: slight preference for B for same-action hand consistency.** In frame 03, B keeps a compact closed-glove silhouette that relates more clearly to extension 02 and recoil 04. I found no convincing new wrist, arm attachment, anatomy, alpha or material regression in that replacement. This is a modest local drawing/readability improvement, not evidence of smoother normal-speed playback or a general upgrade to the whole action library. A is not rejected as anatomically broken.

## Independence and prior exposure

This reviewer previously audited the original v10 Brann attack and raised the follow-through glove-shape concern. An early description overstated that original hand as a fully splayed casting palm; detailed inspection subsequently reduced the finding to ambiguous finger/knuckle lobes. That history may prime this reviewer to value a closed silhouette. The supplied A/03 is recognizable from its pixels and fingerprint as the previously seen control. **This is independent of the repair producer, but it is not a cold or fully control-blind review.** No earlier numeric action scores exist to inherit, and no walk grades were used.

For this paired task, I read only the nominated anonymous `action-review/input` packet and the case-free `blind-review-card.md`. I did not open this repair's producer mapping, scripts, receipts, other reviews or canonical sources. The judgment was frozen before any producer unblinding. Recognition of the control is disclosed rather than treated as accidental independence.

## Separate judgments

| Dimension | A | B | Comparison |
|---|---|---|---|
| Drawing / material / anatomy | Credible shaded glove and connected arm; the end silhouette has small finger-like lobes that can also be read as knuckles | More compact closed fist, rounded leather mass and visible cuff connection | Slight B preference; no demonstrated new structural/material failure |
| Identity / temporal consistency | Dark rounded hair, bronze pauldrons, indigo costume, belt and boots remain stable | Same identity and body volumes | Tie |
| Action chronology | Ready → anticipation → extension → follow-through → recoil → settle → neutral is reconstructable | Same body, timing and main arm progression; 03 reads more explicitly as continued fist | Body chronology tie; local gesture consistency favors B |
| Practical readability | Attack silhouette is clear; exact glove state in 03 is less certain at reduced size | Closed glove reads a little more consistently beside 02 | Slight B locally; small difference at 84 pixels, especially on dark/game grounds |

No score target or whole-library numeric grade is assigned. The comparison supports keeping B as the preferred scoped hand candidate, with moderate confidence. It does not prove the original's lobes were open fingers or require rejecting A.

## Exact inspected scope and drawing evidence

The packet contains **57 PNGs plus one manifest: 58 actual files**. I checked every listed image hash, bound all files before and after, and found no changes. The PNG count consists of 32 A/B NE/NW action cels, 24 cardinal attack context cels and one appearance reference. The manifest SHA-256 is `f3990c3afa46db4c4c86ee2b770e276d57840a8bc247b2a85d88643d948c00c4`.

All 32 action cels, all 28 within-action adjacent pairs, and four neutral-to-ready entry comparisons were inspected at every combination of 128/256/84 pixel whole-canvas size and light `#e7e3d6`, dark `#22252b`, game `#27392f`. The appearance and all 24 cardinal context cels were also inspected. Context establishes character and action identity; it receives no transferred acceptance. The cardinal attacks use compact glove silhouettes in their extension/return sequence, supporting a clear closed-jab interpretation without requiring diagonal poses to duplicate their projection.

Only frame 03 differs between A and B. The full changed bounding rectangle is native x=97–113, y=29–48 inclusive for NE and x=15–31, y=29–48 for NW. It covers the distal glove/cuff area; the head, shoulder, torso, legs and boots are unchanged. There are 234 changed pixels per view. Counts and preservation bounds locate the change and earn no art credit.

At 256 and 128, A/03's upper glove edge has several short lobes and its distal silhouette looks more relaxed than 02's compact block. B/03 preserves a rounder enclosed glove. Its highlight and dark edge still read as brown leather, with the bronze cuff visibly continuing into the wrist. On light, dark and game grounds I do not see a transparent wrist gap, a floating glove, a new long wrist spike, or a sudden new metal/skin color patch. The hand/forearm alignment remains plausible in both NE and NW. The small form reads as a continued fist in 02→03 and a retracted fist in 03→04.

At 84 pixels the distinction is restrained: B's outline is a slightly more compact termination of the arm, while the bright bronze shoulder/cuff and overall extended-arm silhouette carry most of the action. The difference is easiest on light and less decisive on dark/game grounds. There is no basis to credit an unchanged torso, foot path or timing with improved motion merely because the hand drawing changed.

Exact changed cel fingerprints:

| Cel | PNG SHA-256 |
|---|---|
| A NE 03 | `909c8cbb094d0a6108c2740adb394288501c91f4c154f2f5b4e531212ab71d98` |
| B NE 03 | `c68dd7f8f86a2d06b432b0c604e3014279316954649474680c7191105f507350` |
| A NW 03 | `4700bc9cf7c9017cf448ff74ec920f0cacc5327d4950eb66a31533ffe647ec4e` |
| B NW 03 | `da56ff43ca692481c6201b7916ecf2f99d456a2ba055c0a64ef044010938bb13` |

## Full entry, active and return chronology

Both variants have the exact eight holds [60,70,55,55,65,35,35,35] ms, totaling **410 ms, nonlooping**. The frame starts are [0,60,130,185,240,305,340,375] ms. Frame 03 occupies 185–240 ms. Timing is declared by the supplied manifest; the packet has no encoded video stream whose presentation timestamps could be measured independently.

| Comparison | Finding in both NE and NW |
|---|---|
| Neutral 07→ready 00 | Fists rise into a guard and the body adopts its ready posture. This is entry context from the supplied final neutral drawing, not an automatic next attack. No clear identity/framing break. |
| 00→01 | Short anticipation folds the front forearm higher while body and costume remain coherent. |
| 01→02 | Strong extension and torso lean establish the jab. Shoulder-to-forearm-to-glove remains traceable. |
| 02→03 | Continues the extended arm and body lean. A's glove is more ambiguous; B's remains compact and clearly closed. No demonstrated new cuff separation in B. |
| 03→04 | Strong retraction into guard. B preserves a fist through that retraction; neither provides an intermediate elbow pose within this pair. Actual perceived recoil smoothness was not tested. |
| 04→05 | Guard and body recentring continue; no second extension or identity change is introduced. |
| 05→06 | Small settling/body-straightening change with consistent shoulder, cuff and boot masses. |
| 06→07 | Arms lower to the supplied relaxed neutral. No new alpha, limb-role or stage-edge failure was demonstrated. |

The compared feet and lower body remain visibly connected throughout. Overlap and different sole projections are legitimate in these views; the packet does not establish actual support, foot planting or world contact. The 07→00 comparison does not certify an animation transition controller, buffering or combo. Repeated presentation would be a review transport, not evidence of an automatically chained action.

## Remaining work and limits

No new defect requiring another paint change is demonstrated in B. The minimum remaining experiment is a blind human timed comparison of these exact 0.410 s single attacks at 84 pixels, with a pause at neutral between invocations. It should check whether the local closed-glove preference is perceptible at speed and whether 03→04 retains a natural recoil. Preserve the current pixels and holds for that test so timing changes do not confound the hand comparison. The dark glove's limited contrast on dark/game grounds is shared; a brighter outline is not automatically warranted.

**Perception limit:** this review reconstructs static chronology from decoded PNGs and declared holds. I did not perceive continuous normal-speed playback and did not run a model, editor, browser, engine, controller or runtime. I make no claim about hit timing, damage, VFX, auto-combos, physical contact, other views/actions/equipment or full-library acceptance. `input-before.json`, `input-after.json`, `coverage.csv`, `differences.json`, the proof sheets and `FREEZE.json` bind the reviewed scope. All source inputs and earlier frozen reviews were left unchanged.
