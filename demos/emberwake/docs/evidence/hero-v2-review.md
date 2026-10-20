# Hero art v2: independent follow-up

Frozen review, 2026-10-15. Initial report preserved unchanged. Scope is the revised selected hero art, all 24 declared clips, and the front/back painted passing keys versus the equal-clock held-pose control. Runtime game behavior and environment remain outside scope.

**Overall: 7.4/10, uncertainty about ±0.7.** The large walk registration errors and north phase reversal are visibly improved. This is a more usable sprite set. The new leg cels add an actual support/swing cue over the held control, but my preference is modest: their high lifted foot and upright support leg can read as marching/jogging in place, and the north walk still shifts sideways on entering idle/actions, while the north cast itself migrates laterally. The existing east/west profile changes also remain.

| Dimension | Rating /10 | Basis and uncertainty |
|---|---:|---|
| Drawing, materials and anatomy | 8.0 | The same attractive hero, readable silver armor and blue/gold clothing. New legs preserve identity but do not transform the set's drawing quality. No detached cuff/fist found. ±0.6. |
| Temporal and view consistency | 7.5 | Walk loops are registered much better; north state placement, north cast migration and side-profile yaw remain. ±0.7. |
| Motion and action readability | 6.9 | North phase order is coherent; painted lift poses give a clearer change than holds, but natural continuous gait remains uncertain and somewhat stiff in the still sequence. ±1.0. |
| Practical use at game size | 7.5 | Removal of lateral/vertical loop jumps and stray alpha columns materially helps. Remaining state pops limit polish. ±0.7. |
| Scoped overall | 7.4 | A drawing-and-motion judgment, not a frame-count/export/ROI-integrity score. ±0.7. |

## Scope, independence and perception limit

No target score was provided. I did not open producer reports/specifications, raw generation sheets, case studies or prior external scores. The parent described the attempted changes before the review, so the revision goals and selected-versus-control identity were not blind. After the initial v2 draft, the parent flagged a possible north cast migration; I independently measured that claim in the nominated atlas before freezing this report. No producer numerical measurements were substituted for these observations. The initial review's incidental exposure to embedded lineage metadata remains disclosed in `hero-initial.md`; this pass parsed only declared cell/scale/pivot/animation fields and did not inspect lineage.

All 24 revised clips were viewed in chronological order at native game height approximately 63 px and at 2× nearest enlargement on light gray and dark green. Every adjacent pose and all eight loop wraps were included. Idle-to-action and action-to-idle comparisons were repeated; representative walk entry/exit phases were compared to idle, attack and cast. This is not certification of every arbitrary gameplay interruption. Supplied current selected contact and game-scale proofs were viewed as well.

For the controlled comparison, both atlases use exactly the same declared playback: south `F5,F0,F1,F112,F2,F3,F4,F113`; north `F48,F49,F51,F114,F50,F52,F53,F115`; eight exposures of 56.25 ms = **450 ms per cycle**. All declared animation fields, cell, pivot and draw scale match between selected and control. Pixel differences are confined to F112–115. Therefore differences between those two candidates cannot be attributed to speed, extra exposure count, upper-body redesign or the common registration repair. That is an attribution constraint, not a quality award.

Continuous human video perception is unavailable through these still-image tools. I reconstructed chronology from the decoded atlas and explicit holds. I do not claim normal-speed viewing, controller feel, physical foot contact on the game ground or a live runtime acceptance test. Any claim about how stiff it will feel at normal speed is qualified below.

## Visible result of the earlier repairs

| Earlier issue | Current result | Exact current evidence |
|---|---|---|
| North walk lateral migration/wrap | **Corrected within the loop.** | F48/49/50/51/52/53 head centroids are x≈64.0/63.8/64.3/64.1/64.4/63.7. Previously the endpoints differed about 12 atlas px. Current F115→48 has no comparable lateral reset. |
| Smaller south lateral reset | **Corrected to small bounded sway.** | Existing F0–5 head centroids now span x≈62.7–64.4. F113→5 does not show the old one-way drift/reset. |
| Side-walk half-cycle height jump | **Corrected to small pose-level variation.** | F96–103 opaque soles end at local y112–113 throughout; the old roughly 5 px half-cycle step at F99→100 and F103→96 is absent. West mirrors this outcome at F107→108 and F111→104. |
| North extra visible leg-role reversal | **Corrected by ordering.** | F48→49→51 retains one visible role, passing F114, then F50→52→53 the opposite role, passing F115, wrap F48. The earlier F50→51→52 alternation is no longer the chronology. |
| Disconnected alpha columns | **Corrected in the nominated examples.** | Old columns F1 x11, F2 x117, F19 x11 and F22 x116 are now alpha0 throughout their cells. Gray/dark/magenta/black composites show no old vertical hairlines. I did not infer art quality from component counts. |

The new painted keys' differences from the held control occupy these inclusive local atlas regions: F112 `(46,81)-(77,114)`, F113 `(49,81)-(79,114)`, F114 `(48,81)-(84,114)`, F115 `(49,81)-(78,114)`. All other atlas frame IDs match the control. The visible benefit is judged below, separately from this measured preservation fact.

## Painted passing keys versus the held control

**A small, qualified preference for the selected painted version; not a large motion-quality gain.** The control visibly prolongs a separated, contact-like leg drawing at slots3 and7. Selected F112/F113 and F114/F115 create a clearly raised foot and a straighter supporting leg at those instants. At native scale this is a real silhouette cue, particularly the brown sole seen from behind in F114/F115. It gives a readable transition away from the repeated old boot shape. I do not regard more slots or unique pixel counts as proof of better movement.

The same evidence limits the result. The raised boot is pulled high and compact while the opposite boot becomes a long upright post. In south F1→112→2 and F4→113→5, the new key emphasizes knee/heel lift more than a gradual foot passage under the hip. North F51→114→50 and F53→115→48 emphasize a rear-facing sole/heel kick. All four occur for 56.25 ms, at t=0.16875–0.225 and 0.39375–0.450 s. The silhouette is more distinct, but does not prove smooth transfer of support.

**Does it look march-like?** In reconstructed chronology, somewhat: the strong upright boot and high compact opposite foot suggest marching or a brisk jog-in-place. This is most obvious in **F112/F113 and F114/F115**, local x≈49–80/y≈81–113. The surrounding keys still show a relatively long extended boot and a tucked opposite boot, so the new key can read as a brief heel kick between contact-like poses rather than a fully rounded walk. It is not obviously worse than the held control, and it is not an anatomical failure. My confidence in a normal-speed preference is low/moderate; the control may feel less punctuated despite having less phase information.

**Smallest useful next experiment:** keep all head/torso/art timing fixed and try one alternative passing cel for F112 and its corresponding back-view role: bring the lifted foot closer beneath the hip, reduce the compact high knee/heel silhouette, and retain a little knee softness in the supporting leg. Compare the three-key neighborhoods above at the same 450 ms cycle. Do not regenerate the upper body or add more exposures before this comparison. If human normal-speed viewing finds the current brisk step suits the intended hero, there is no need to replace it merely to satisfy an abstract gait diagram.

## Remaining demonstrated state/view issues

Coordinates are local to each 128×128 atlas cell. Frame global origin is `((F%8)*128,(F//8)*128)`.

### North state placement and in-place cast migration — medium/high priority

The large in-loop drift is fixed, but the stable walk and the other north states retain different lateral placements. **F66→F48** moves the head centroid x≈69.8→64.0 and blue back-panel centroid x≈71.7→65.2: roughly **6 atlas px / 4 game px left**. F67's head centroid is farther right at≈71.8. Returning from the walk moves the body right again. North F54 attack and F60 cast have back-panel centroids≈71.7/71.9, so a direct walk-to-attack/cast join has the same placement discrepancy.

This is visible around the spine/back panel at local y48–65, not solely a hand bounding-box fluctuation. The corresponding whole-pose comparisons appear in `v2-state-joins.png`. Some stance-width change is appropriate on stopping; a sideways move of the shared head/torso deserves separate registration attention. The runtime may transition through idle, but that does not remove this art join.

**Minimal repair:** establish one north root/torso placement across the walk, idle, guard and cast-rest keys, then trial a translation of the non-walk north poses or the walk as a group. Choose which group to move by the intended support root; do not automatically undo the repaired walk loop. Compare F66/F67↔F48 and F48↔F54/F60 at native size, with the root fixed. This addresses the shared placement without repainting good anatomy.

The cast also has a separate **in-clip migration**, so a single whole-clip placement shift is insufficient. In current **F60→61→62→63→64→65**, head centroid x is approximately **72.2,71.9,69.4,68.1,65.4,59.9**. The blue back-panel centroid moves **71.9→72.1→69.3→67.1→66.2→60.6**. Head and back therefore migrate left together by about **11–12 atlas px / 7–8 game px** over the 500 ms cast; F65→idle F66 moves right again (back-panel x60.6→71.7). Inspect the spine/back panel at local y48–65 and the shared hair mass at y15–44 in the north cast row of `v2-north-chronology.png`. The hand spread in F63 does not explain the shared head/back displacement. This confirms a visible art-placement issue, without asserting any particular runtime root implementation.

**Smallest useful repair:** use a per-pose translation trial tied to the same pelvis/root landmarks across F60–65 and the idle return, preserving every pose's joints and timing. A single offset for the entire cast cannot remove its internal drift; fitting a changing silhouette bounding box could instead erase intended body lean. Audit the other non-walk north keys for the same placement pattern while making this trial, rather than assuming this measured cast example certifies them.

### Side profiles still change across walking phases and state joins — medium polish issue

**Yes, the profile pop remains.** East F98–102 and west F106–110 show a stronger side-on torso/head arrangement than idle F42/F90 and their guard/cast stances. The local near shoulder/chest region x≈45–82/y≈25–75 becomes a narrower side stack during the walk, then opens into the broader three-quarter idle/guard. The change is clear in **F42↔F96/F100/F102** and **F90↔F104/F108/F110**; the stronger profile interval occurs within both walks as well. Height correction makes it easier to separate this drawing change from the earlier vertical displacement.

This remains the same character and costume; it is not a material-identity collapse. Some torso yaw during gait is legitimate, so I cannot call every phase difference an error. The state return nevertheless looks like a small turn as well as a stop. **Minimal experiment:** compare one profile-matched idle/guard drawing with the existing walk; alternatively soften the strongest walk yaw. Keep root placement and450 ms timing fixed. Prefer a small angle adjustment over replacing the recognizable face or armor rendering.

## Other clips and character construction

The action silhouettes in all four idle pairs, attacks, casts, hurts and dodges remain useful and readable at native scale, subject to the north registration problem above. They do not earn drawing credit from unchanged exposure timing. The silver cuffs lead plausibly into brown fists/palms; I again found no defensible detached hand or obvious extra limb. Highlights and small clothing volumes vary but retain the intended material grouping.

Side punches F32–33/F80–81 read clearly. Front/back strikes use legitimate foreshortening and occlusion. Cast gathering/open-palms/release remains distinct from attack, with coherent return poses. Hurt explicitly returns to idle. Dodge still reads as a low braced dip/lunge, strongest in side views; the north/south art alone does not communicate travel distance or a roll. That remains a runtime playback question, not a new art rejection.

## Complete revised coverage and timing

Every row was inspected at native and 2× with its predecessor/current pairs and wrap or idle return.

| Clip | Selected order | Duration | Loop |
|---|---|---:|---|
| south_idle | F18 → F19 | 1.160s | yes |
| south_walk | F5 → F0 → F1 → F112 → F2 → F3 → F4 → F113 | 0.450s | yes |
| south_attack | F6 → F7 → F8 → F9 → F10 → F11 | 0.410s | no |
| south_cast | F12 → F13 → F14 → F15 → F16 → F17 | 0.500s | no |
| south_hurt | F20 → F21 → F18 | 0.290s | no |
| south_dodge | F22 → F23 → F22 → F18 | 0.260s | no |
| east_idle | F42 → F43 | 1.160s | yes |
| east_walk | F96 → F97 → F98 → F99 → F100 → F101 → F102 → F103 | 0.450s | yes |
| east_attack | F30 → F31 → F32 → F33 → F34 → F35 | 0.410s | no |
| east_cast | F36 → F37 → F38 → F39 → F40 → F41 | 0.500s | no |
| east_hurt | F44 → F45 → F42 | 0.290s | no |
| east_dodge | F46 → F47 → F46 → F42 | 0.260s | no |
| north_idle | F66 → F67 | 1.160s | yes |
| north_walk | F48 → F49 → F51 → F114 → F50 → F52 → F53 → F115 | 0.450s | yes |
| north_attack | F54 → F55 → F56 → F57 → F58 → F59 | 0.410s | no |
| north_cast | F60 → F61 → F62 → F63 → F64 → F65 | 0.500s | no |
| north_hurt | F68 → F69 → F66 | 0.290s | no |
| north_dodge | F70 → F71 → F70 → F66 | 0.260s | no |
| west_idle | F90 → F91 | 1.160s | yes |
| west_walk | F104 → F105 → F106 → F107 → F108 → F109 → F110 → F111 | 0.450s | yes |
| west_attack | F78 → F79 → F80 → F81 → F82 → F83 | 0.410s | no |
| west_cast | F84 → F85 → F86 → F87 → F88 → F89 | 0.500s | no |
| west_hurt | F92 → F93 → F90 | 0.290s | no |
| west_dodge | F94 → F95 → F94 → F90 | 0.260s | no |

Holds: idle `580,580 ms`; **all walks** eight × `56.25 ms`; attack `60,70,55,55,65,105 ms`; cast `60,80,100,80,80,100 ms`; hurt `90,100,100 ms`; dodge `45,105,55,55 ms`. No interpolated poses were inferred from these holds.

## Fingerprints and preserved evidence

All nine input start/end fingerprints matched. The initial report SHA-256 remains `b38a278acc4c34482bed905cb95fb7a9e5d8152e8c63c6a9dde1447d5d1910ac`.

| Input, relative to producer root | SHA-256 |
|---|---|
| `assets/hero/atlas.png` | `2196d13a2a080c0f3dc459ab8ae8441d9aba7b9c408e64e29c92e7e9464add92` |
| `assets/hero/animations.json` | `b16ff1e261d631a25c15838c1c0c4cc5504151bdf67693c4d89af3fc5511e0fe` |
| `assets/hero/game-scale-proof.png` | `5395eb9bb2703b30dde346e0cb6406eb822d9df80c35f7e59d9baf76f19abb1f` |
| `assets/hero/selected-contact-sheet.png` | `4c1426c37facd11255535f362e319011857c2b49e7f61bdf93ba7b4569711696` |
| `art-source/hero/candidates/hold-control/atlas.png` | `3124f0ea815a7db5f41fc97a3c64847b1f47475bc95d3b875ebeadbb6966bf9b` |
| `art-source/hero/candidates/hold-control/animations.json` | `b0b27c4d5881f737d259d11831e978c658aabbfbe73a6f676f3ceebe0cf0b0f5` |
| `art-source/hero/candidates/hold-control/game-scale-proof.png` | `c676eb437f25496ea69ac6d9a1c006a98180cc600a2de917cb11bb1ce1d5a9e4` |
| `art-source/hero/candidates/hold-control/selected-contact-sheet.png` | `da2d23d15928b32e001505dd8e7317afbc2b3fb26b2032c98c5b094a7b361ad9` |
| `art-source/hero/appearance-reference.png` | `1f9203ec653a5b9895e028c9b13e0748f16b22c5ba89fcbfa4545720264e9cce` |

Review output is confined to `/home/astra/projects/emberwake-review/`: `hero-v2.md`, v2 start/end fingerprint JSON, `v2-{south,east,north,west}-chronology.png`, `v2-passing-vs-hold-control.png`, `v2-passing-joins-detail.png`, `v2-state-joins.png`, and `v2-alpha-edge-detail.png`. Detail crops are diagnostic nearest enlargements; chronology packets contain native and 2× samples. No producer file was edited.

The next most useful art repair is north registration across state joins and the in-place cast trajectory. Keep the passing candidates available for a same-clock human playback comparison before investing in more gait cels. This report does not grant acceptance to later changed artwork, timing or runtime behavior.
