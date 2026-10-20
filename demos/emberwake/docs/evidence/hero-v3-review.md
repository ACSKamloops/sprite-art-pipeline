# Hero art V3: frozen independent follow-up

Review frozen 2026-10-16. Scope: nominated hero art, all 24 clips, affected entry/recovery/loop joins at native game height approximately 63 px and 2×. Producer files remained read-only. Game environment, functionality, physical ground contact, controls and whole-game acceptance are outside scope.

**Overall: 7.7/10, uncertainty about ±0.7.** V3 substantially fixes the north cast migration and the north walk/stance origin mismatch without an evident new large foot pop. This is attractive, useful demo hero art. I would still stop short of confidently calling the full animation set polished high-quality work: the unchanged front/back gait is stiff and somewhat march/jog-like, and side profiles still turn visibly between walk and idle/action states. Those are drawing/motion limits that translation cannot resolve.

| Dimension | Rating /10 | Basis and uncertainty |
|---|---:|---|
| Drawing, materials and anatomy | **8.0, unchanged** | Same pixels and poses. Recognizable brown-haired hero; blue/gold clothing, silver armor and brown gloves/boots remain coherent. No new drawing credit for translation. ±0.6. |
| Temporal and view consistency | **8.0** | Large north migration/origin problems are removed; small pose changes remain. Profile-angle changes still limit continuity. ±0.7. |
| Motion and action readability | **6.9, unchanged** | Same gait drawings, phase order and timing. Punch/cast/hurt/dodge silhouettes remain legible; no claim of new natural gait quality. ±1.0. |
| Practical use at game size | **7.8** | Stable action staging and closer state origins make the set easier to use. Human normal-speed motion acceptance remains open. ±0.7. |
| Scoped overall | **7.7** | Improved registration and practical continuity, not a re-rating of identical drawing. ±0.7. |

## Independence, input binding and method

No score target was supplied or used. The parent described an intended translation-only repair before this review. I independently compared decoded V3 pixels with the nominated V2 atlas, without opening producer specs/reports, root landmark instructions, raw generation sheets or scored case histories. I used the same case-free blind-review rubric as prior passes. The review is therefore aware of the intended repair, not blind to revision identity. The initial pass's incidental embedded-lineage exposure remains disclosed in the preserved initial report; this pass parsed only playback configuration fields.

Current atlas SHA-256 is **`1dc65d4eb637ef35e5be3d3345b1a56d18af6ce041f7ce000c924848d569cb68`**, matching the nominated artifact. All seven start/end input fingerprints matched. Both previous reports remained byte-for-byte unchanged.

All selected frames were inspected in ordered rows with their explicit holds, every adjacent pair and all eight loop wraps. One-shots included their idle return; idle-to-action comparisons and representative first/last walk-phase joins were included, plus hurt/dodge transitions into the moved idle poses. This covers the 24 declared clips, not every possible arbitrary gameplay interruption.

Native packets resample each 128 px cell to 84 px by nearest sampling, matching draw_scale 0.66 to rounding, then double that native sample by nearest sampling for 2×. Light gray and dark green were used for every clip. The current supplied game-scale proof and selected contact sheet were also viewed. V2/V3 action comparison rows use fixed cell coordinates and a visible center guide.

**Perception limit:** judgments reconstruct chronology from decoded stills and known holds. I did not perceive continuous human normal-speed video and do not claim controller feel, ground-planted foot contact or runtime testing. This matters particularly when distinguishing a crisp low-frame step from an excessively stiff march.

## What changed, verified separately from art quality

Decoded comparison found **51 nonzero integer translations**, all horizontal, in the nominated idle/attack/cast stance banks. Each changed cel exactly matches a translated V2 cel; no scaling, recoloring, redrawing or within-pose deformation was needed to explain it. Five of the 56 stance slots are already in their current position and match V2 directly. All other atlas cells, including every walk and painted passing cel, match V2. Decoded alpha coverage is preserved by these shifts, so no visible edge was cropped. Declared animation order, holds, loops, pivot and draw scale match V2.

These are scope/preservation facts. They do not independently establish a better drawing, weight transfer or grounded animation. Full observed dx values are preserved in `hero-v3-observed-translations.json`.

| Stance bank | V3 dx relative to V2, in declared order |
|---|---|
| South idle F18,19 | -1,-1 |
| South attack F6–11 | -3,+1,0,0,0,+3 |
| South cast F12–17 | -1,-1,0,+1,+1,+2 |
| East idle F42,43 | -3,+1 |
| East attack F30–35 | -2,+1,+4,+2,-1,+2 |
| East cast F36–41 | -4,-1,+4,+6,+1,+1 |
| North idle F66,67 | -7,-8 |
| North attack F54–59 | -7,-8,-8,-8,-4,-2 |
| North cast F60–65 | -9,-8,-6,-3,0,+2 |
| West idle F90,91 | -7,-2 |
| West attack F78–83 | -5,-7,-8,-9,-6,+1 |
| West cast F84–89 | -6,-2,-1,-1,-4,+2 |

Coordinates below are local to the 128×128 cell, x right/y down. Frame global cell origin is `((F%8)*128,(F//8)*128)`.

## North cast and state origin: visibly improved

**F60→61→62→63→64→65→F66:** the previous one-way left migration is absent. Current head centroid x is approximately **63.2,63.9,63.4,65.1,65.4,61.9**; the blue back-panel centroid is **62.9,64.1,63.3,64.1,66.2,62.6**. Compare the shared hair mass at local y15–44 and back panel/spine at y48–65. V2's head moved approximately 72.2→59.9 and back panel 71.9→60.6. V3 leaves small pose-dependent shifts rather than that 11–12 px migration. The F65→idle F66 back-panel change is approximately 62.6→64.7, a small settling difference rather than the previous 11 px return.

**F66↔F48:** idle versus walk back-panel centroid is now approximately 64.7↔65.2, about 0.5 atlas px, versus about 6.5 atlas px in V2. North guard F54 and cast-rest F60 stage near the same root. The shared head/body no longer makes the former roughly 4 game px lateral move simply on entering the walk.

This looks better in the native rows, not merely in centroid numbers. The numbers localize a result visible in `v3-north-chronology.png`, `v3-state-joins.png` and the V2/V3 action comparison. I am not treating an image centroid as an authored anatomical root.

## Did correction erase weight transfer or introduce feet pops?

**No convincing new large defect found in this scope.** The corrected attacks retain their stance widening, knee bends, torso turn and fist reach; their action is not reduced to a frozen upright body. The casts retain gathering, release and return. Examples worth checking are east F31→32→33 and west F79→80→81, around the torso/hips at y55–85 and boots at y88–112. Their within-pose relationships are intact, and the V3 sequence still reads as a braced strike. A translation can alter global travel, so identical limb pixels alone would not prove preserved force; the visual comparisons did not reveal a persuasive lost lunge that needs restoring.

The changed idle poses also meet the unchanged hurt/dodge keys acceptably in the inspected still sequence. North F69→F66 no longer has a large shared torso placement discrepancy. North hurt F68 still tilts the head right over a centered back panel (head x≈72.2 versus blue back x≈64.9); this is a legitimate recoil pose, not a registration error to erase by aligning heads. North F70/71 and the other dodges retain the braced lean. These differences are useful acting.

There are small drawn foot adjustments in the attack/cast/idle returns, including the settling of the north cast's F65 raised/turned boot into F66. They do not by themselves demonstrate a misplaced support foot. The correction made no y shifts, and I found no new large vertical pop. I cannot certify continuous foot planting or world-space travel from these stills and no ground plane.

No additional translation repair is requested merely to force every boot edge or head center onto a fixed coordinate. Such alignment could remove intentional pose differences.

## Remaining art limitations: unchanged, not repaired by V3

### Front/back gait still reads stiff or briskly marching

All walk cels and timing are exactly V2. The qualified small preference for the painted passing keys therefore stands; it does not gain another motion point here.

The strongest evidence remains **south F1→F112→F2 and F4→F113→F5**, and **north F51→F114→F50 and F53→F115→F48**. The high compact opposite foot and long upright supporting boot around local x49–80/y81–113 add a visible lift cue, but can read as a heel kick or march between separated contact-like poses. At 450 ms/cycle this may suit a brisk hero step; I cannot confidently call it a rounded natural walk from the still chronology. The north phase ordering and loop registration remain coherent, so this is not a recurrence of the original wrong role reversal.

**Smallest optional polish experiment:** retain all timing, upper-body art and root placement; test one passing cel with the lifted foot nearer beneath the hip and a slightly softer supporting knee. Compare the same three-key neighborhoods during human normal-speed playback before replacing the current candidate. Do not generate more frames merely to increase the count.

### Side profiles still turn between walk and stance

The angle change survives the placement correction. **East F98–102 versus F42/F30/F36**, and **west F106–110 versus F90/F78/F84**, still show a narrower side-on torso/head arrangement during walking and a broader three-quarter stance on stopping/acting. Inspect the head/shoulder/chest around local x45–85/y25–75. The effect is particularly clear at the walking extremes F100/F102 and F108/F110 compared with their idle. It remains the same recognizable costume and character.

Some yaw and a deliberate turn on stopping are legitimate. I do not label every angle difference an anatomy error. If the aim is seamless directional continuity, the visible angle change remains a polish limitation. **Smallest optional experiment:** compare one profile-matched idle/guard with the current walk, preserving the now-stable root. An angle adjustment is more relevant than another pixel translation.

### Other actions and construction

The four punch sequences remain readable unarmed strikes. Side extension is clearest; north/south arm occlusion and foreshortening are legitimate. Cast remains distinct from attack through gathering/open palms/relaxation. Hurt reads as recoil. Dodge reads as a low braced dip/lunge, with clearer lean from the sides; the art alone does not establish a roll or travel distance. No detached cuff/fist, extra limb, new material change or obvious alpha framing problem was found. Translation did not improve or degrade their underlying drawing quality.

## Complete declared timeline coverage

Every row below was inspected at native and 2× with its full order/holds, adjacent pairs, wrap or idle return. Current metadata is unchanged from V2.

| Clip | Selected frame order | Duration | Loop |
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

Holds: idle `580,580 ms`; all walks eight × `56.25 ms`; attack `60,70,55,55,65,105 ms`; cast `60,80,100,80,80,100 ms`; hurt `90,100,100 ms`; dodge `45,105,55,55 ms`. No interpolation or successful normal-speed playback was inferred from correct metadata.

## Fingerprints and preserved review artifacts

All start/end fingerprints matched; old reports were not rewritten.

| Input, relative to producer root | SHA-256 |
|---|---|
| `assets/hero/atlas.png` | `1dc65d4eb637ef35e5be3d3345b1a56d18af6ce041f7ce000c924848d569cb68` |
| `assets/hero/animations.json` | `f295492d3339af898ee49c117b753ac1f475e78e0022cc943feaecf46510965d` |
| `assets/hero/game-scale-proof.png` | `b75bd5a206a9dbed15b0ca27be0f39245584fc9c5b048cd6416a9082c0539002` |
| `assets/hero/selected-contact-sheet.png` | `7dad0b2613e6793966027192f248742c63c3838dd2a0d4ad666bd0987149a3d7` |
| `art-source/hero/candidates/v2/atlas.png` | `2196d13a2a080c0f3dc459ab8ae8441d9aba7b9c408e64e29c92e7e9464add92` |
| `art-source/hero/candidates/v2/animations.json` | `b16ff1e261d631a25c15838c1c0c4cc5504151bdf67693c4d89af3fc5511e0fe` |
| `art-source/hero/appearance-reference.png` | `1f9203ec653a5b9895e028c9b13e0748f16b22c5ba89fcbfa4545720264e9cce` |

Preserved earlier report hashes:

- `hero-initial.md`: `b38a278acc4c34482bed905cb95fb7a9e5d8152e8c63c6a9dde1447d5d1910ac`.
- `hero-v2.md`: `540179379ba132c85224ae979e353497dfffd694ee77b51e37154087930496a1`.

All new output is confined to `/home/astra/projects/emberwake-review/`: `hero-v3.md`, V3 start/end fingerprint JSON, `hero-v3-observed-translations.json`, four `v3-{direction}-chronology.png` files, `v3-state-joins.png`, and `v3-v2-action-comparison.png`. These are review packets, not replacement hero assets.

V3 clears the demonstrated north staging defects within this review. It does not silently certify later art/timing changes or convert the remaining gait/profile judgments into completed human playback acceptance.
