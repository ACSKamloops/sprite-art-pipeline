# Frozen v1 character art and animation review

Lyra has the stronger complete visual set: **7.1/10 overall**. Brann's attractive drawing is undermined by a changing waist ornament and a contradictory north-walk leg phase: **6.4/10 overall**. These are scoped art/chronology judgments, not a gameplay/export pass or human normal-speed acceptance.

| Character | Drawing | Reference fit | Consistency | Motion | Usefulness | Overall |
|---|---:|---:|---:|---:|---:|---:|
| Lyra | 8.0 | 7.7 | 7.8 | 6.2 | 7.0 | 7.1 |
| Brann | 7.8 | 7.6 | 6.2 | 5.7 | 6.3 | 6.4 |

Overall is a holistic judgment, not an arithmetic average or producer target. The written style brief was rich modern chibi, top-down, unarmed heroes. Both fit that brief well: shaded materials, readable proportions, strong identity separation. Rowan was not opened, so reference fit measures the written brief rather than exact reference parity. Per-dimension confidence is in each character's `scores.json`; motion confidence is lower than drawing confidence.

## Scope and perception limits

Nominated inputs only: `atlas.png`, `animations.json`, and `selected-contact-sheet.png` under each frozen v1 character root. Production files were read only. All review products are in this evidence folder. No generation/API calls, installs, production/source edits, browser launch, or subagents were used.

For **each character**, the review covered all 24 declared clips, four directions, six actions, 112 atlas cells (112 distinct RGBA cells), and 116 timeline presentations. Coverage included **92 internal adjacent pairs**, **8 declared loop wraps**, **16 diagnostic nonloop last→first pairs**, and **80 idle/action endpoint joins**. A diagnostic wrap is not alleged to occur in production: only idle and walk are declared loops. For joins, both idle poses were compared with the first and final pose of walk/attack/cast/hurt/dodge.

Every pose/pair and join was inspected in native-size sheets, nearest 2× enlargements, and an approximate intended draw-scale rendering. Native cells are 128×128; draw scale 0.66 rounds to an 84×84 review cell. Dark teal (#193032) pair sheets and light gray (#d3d5d0) draw-scale contact sheets expose edge/silhouette behavior. This is a review approximation of the draw scale, not engine-render sampling validation.

**Temporal perception is reconstructed from decoded still chronology and exact holds. I did not observe human normal-speed playback.** The 48 APNGs preserve exact rational holds and were decoded and pixel-compared against their constituent source crops. Their actual APNG delay fractions were checked. A portable canvas player is provided for human playback follow-up; creating it does not establish that follow-up occurred. There is no claim about controller feel, world-space planted-foot contact, gameplay, effects, or exports.

Independence qualification: I inadvertently read the full pipeline SKILL.md alongside the requested blind card; it includes unrelated historical scores and quality anecdotes. An initial manifest schema inspection also printed several early lineage entries, including source filenames/transforms. I did not open the referenced source art, any candidate producer report, prior candidate ratings, or any other review. This remains an independent candidate assessment with incidental rubric/lineage exposure, **not a perfectly blind review**. Ratings use only the nominated candidate pixels and holds. Root later disclosed that another metadata-only version exists; it was not opened or scored.

Brann west is the disclosed symmetric east mirror. It counts as four-direction coverage, not eight directions or separately authored west poses. Mirroring itself is not penalized here.

## Timing inspected

Holds are identical across both candidates and all directions for each action.

| Action | Poses | Exact total | Loop | Review observation |
|---|---:|---:|---|---|
| idle | 2 | 1.16 s | yes | Each pose holds 0.58 s; costume changes can persist visibly. |
| walk | 8 | 0.45 s | yes | Each pose holds 9/160 s = 56.25 ms. |
| attack | 6 | 0.41 s | no | Full side extension occupies p2/p3, 110 ms combined. |
| cast | 6 | 0.50 s | no | Declared release is p3, starts at 0.24 s and holds 0.08 s. |
| hurt | 3 | 0.29 s | no | Final presentation reuses the first idle cell. |
| dodge | 4 | 0.26 s | no | Main lean p1 holds 0.105 s; only one recovery pose follows p2. |

## Lyra

The white hair, teal scarf, green shoulders, gold-edged coat and brown gloves/boots retain a convincing single identity. Camera elevation, body scale and registration are broadly consistent. Head/hair shapes vary a little with acting but do not produce a demonstrated identity swap. I found no gross detached limb, extra limb, clipping, or palette/material break requiring a broad redraw. The white hair and dark costume remain readable on both backgrounds and at draw scale.

Side punches have clear anticipation, extension and recovery. Hands stay attached to plausible wrists. South punches read as foreshortened unarmed gestures; the north strike is partly hidden by the head, so I do not infer missing anatomy from occlusion. Casting distinguishes gathered fists/preparation from open palms. East release f47 shows two overlapping forward hands; west f103 has one clearly visible lead palm and the other hand is less visible. I do not have enough evidence to call this a hand-switch defect rather than occlusion/directional acting.

Top three actionable fixes:

1. **Improve front/back walk support and passing (medium).** In `south_walk`, f0–3 retain an extended lead boot, then f4–7 favor the opposite one; f3→4 and f7→0 provide little readable passing/support bridge. `north_walk` has the same sparse progression at f59→60 and f63→56. The side walks show more readable passing at f30/f34 and f86/f90. Replace one drawing near each front/back half-cycle boundary with a genuine passing/support pose, preserving costume/head registration and the same 0.45 s total for an equal-time A/B. This is a drawing concern; changing exposure alone cannot supply missing support geometry. I cannot certify a physical contact error without world movement.
2. **Settle the attack exit (low to medium polish).** Pairs f13→14, f41→42, f69→70, and f97→98 change directly from broad raised guard to narrow arms-down idle. At y≥95, east f41's lower-sprite alpha spans x30..89 while f42 spans x45..85: the rear-foot outline relocates substantially in one switch. Add/substitute one short settle pose if polished continuity is required, keeping total responsiveness appropriate. This is less serious than an identity or phase error, and real-time perceptual severity needs A/B playback.
3. **Correct frozen-v1 palm attachment metadata (medium, no redraw).** `cast_hand` markers at release f47/f75/f103 sit low or outside visible palms, especially west (22,64). See `cast-palm-markers-2x.png`. Measure the chosen release-palm pixels and move the anchors. The palm drawings themselves are readable. Any later metadata fix is outside this score and earns no drawing improvement.

Retain this visual direction. The set is useful for a prototype; it is not yet a demonstrated polished motion library.

## Brann

Brann is visually distinct from Lyra, with curly dark hair, a beard, blue cloth, gold pauldrons and brown gloves/boots. The armor, cloth and leather separate well at the small draw scale. Overall camera and silhouette registration are reasonably stable, and side attacks/casts/dodges are useful readable gestures. No gross limb attachment failure was demonstrated.

Top three actionable fixes:

1. **Unify the waist ornament (high temporal-consistency issue).** The hanging feature changes between gold split strands/trim and a red-orange central cloth tab. This is especially clear inside `east_idle` f42↔43, `north_idle` f70↔71, and `west_idle` f98↔99, each pose held for 0.58 s. It also changes in `south_attack` f8→9; `east_cast` f45→46 and f48→49; `north_cast` f72→73 and f76→77; mirrored west cast f101→102 and f104→105. The central feature lies roughly around x54..76, y80..94 in south/north (side location varies). The gold strands and orange cloth are different shape/material identities, not merely a highlight changing with motion. South idle f14/f15 and the south cast bank mostly retain gold: do not assume every action uses red. Choose one design and repair only that source-attached feature consistently. Review every cited pair and all joins afterward. Evidence: all four `*-waist-crops-4x.png`.
2. **Repair the north-walk phase outlier (high motion issue).** `north_walk` p0/f56→p1/f57→p2/f58 switches the extended lower boot screen-right→screen-left→screen-right in three consecutive poses. The lower alpha silhouette's x centroid at y105..114 (alpha>128) is approximately 68.27→60.11→69.62. These are image-space measurements, not foot-contact proof, and the full-frame/foot-crop drawings support the leg-role reversal. Each pose is held 56.25 ms. The later opposite half appears at f61–63. Replace f57 with a same-support-leg bridge between f56/f58, maintaining coherent opposing arm swing; review all eight poses and the wrap. A translation cannot repair a reversed leg role. Evidence: `north-feet-4x.png`, `pairs/north_walk-2x.png`.
3. **Improve the remaining front/back gait progression (medium).** Beyond f57, long extended-boot silhouettes dominate the front/back timelines with little readable passing. South lead change is concentrated around f4→5 rather than a simple four/four progression; north f59→60→61 and wrap f63→56 also need clear support relationships. After fixing the outlier, author passing/support bridges and compare at unchanged 0.45 s duration. This is lower priority than the demonstrated outlier and should not trigger a wholesale art replacement.

The attack-to-idle stance closure noted for Lyra is also present in Brann (f13→14,41→42,69→70,97→98). Frozen-v1 cast anchors at f47/f75/f103 sit below/outside the palms; measure metadata rather than redraw these good release silhouettes.

Retain Brann's design and useful poses, but repair the local waist and phase defects before approving the full animation set as polished.

## Exhaustive clip ledger

All rows include their internal pairs and last→first diagnostic/loop pair. Endpoints were also compared to both idle phases. Frame numbers are atlas cells; `p` refers to zero-based pose index in a clip.

### Lyra

| Clip | Atlas frames | Pixel/chronology result |
|---|---|---|
| south_idle | 14,15 | Stable identity and understated idle; no material pop demonstrated. |
| south_walk | 0–7 | Sparse passing; prioritize f3→4 and loop f7→0. |
| south_attack | 8–13 | Foreshortened punch reads; wide guard f13→idle14 has no settle. |
| south_cast | 16–21 | Gathered hands→two open palms reads; large opening f18→19 is deliberate key change. |
| south_hurt | 22,23,14 | Clear flinch/recovery; final idle is reused. |
| south_dodge | 24–27 | Crouch/lean reads; f26→27 returns to upright in one change. |
| east_idle | 42,43 | Stable side identity and scale. |
| east_walk | 28–35 | Readable side progression; passing at f30/f34; no proven leg-role outlier. |
| east_attack | 36–41 | Strong unarmed extension f38/f39; direct guard→idle stance closure. |
| east_cast | 44–49 | Two forward palms read; frozen-v1 release marker is low/outside. |
| east_hurt | 50,51,42 | Readable flinch with coherent wrist/face and return to idle. |
| east_dodge | 52–55 | Useful lean f53; sharp final rise f54→55, a polish issue. |
| north_idle | 70,71 | Stable hair/costume volume. |
| north_walk | 56–63 | Sparse passing at f59→60 / wrap63→56; no Brann-like f57 reversal. |
| north_attack | 64–69 | Strike partly occluded by head; no missing-limb allegation. Guard exit abrupt. |
| north_cast | 72–77 | Preparation hands occluded, open release f75 clear; v1 marker is low. |
| north_hurt | 78,79,70 | Shoulder/body recoil readable; face correctly occluded. |
| north_dodge | 80–83 | Crouch/shoulder turn coherent; rapid last return to upright. |
| west_idle | 98,99 | Stable side identity; distinct view retained. |
| west_walk | 84–91 | Readable passing f86/f90; material registration stable. |
| west_attack | 92–97 | Lead arm remains connected through jab f94/f95; f97→idle98 closes stance. |
| west_cast | 100–105 | Lead palm f103 clear; other hand less visible, no proven hand switch; v1 anchor low. |
| west_hurt | 106,107,98 | Clear recoil; final idle reused. |
| west_dodge | 108–111 | Useful forward lean f109; upright return f110→111 is abrupt but coherent. |

### Brann

| Clip | Atlas frames | Pixel/chronology result |
|---|---|---|
| south_idle | 14,15 | Both primarily gold split waist trim; identity otherwise stable. |
| south_walk | 0–7 | Red-orange tab; prolonged lead silhouettes, change around f4→5. |
| south_attack | 8–13 | Waist changes gold f8→orange f9; punch itself readable. |
| south_cast | 16–21 | Gold trim generally stable; coherent gather/open-palm release. |
| south_hurt | 22,23,14 | Flinch returns from orange tab to gold idle trim. |
| south_dodge | 24–27 | Lean is readable; small waist design shifts and gold endpoint. |
| east_idle | 42,43 | Gold→orange waist design change inside idle loop. |
| east_walk | 28–35 | Side stride/passing readable; red tab differs from neutral gold phase. |
| east_attack | 36–41 | Clear jab f38/f39; direct guard→idle stance/material change. |
| east_cast | 44–49 | Waist switches f45→46 and f48→49; palms good; v1 anchor below palm. |
| east_hurt | 50,51,42 | Good recoil; orange tab to gold return f51→42. |
| east_dodge | 52–55 | Good lean; orange-to-gold waist at final neutral return. |
| north_idle | 70,71 | Gold split→orange tab every 0.58 s, definite internal-loop material swap. |
| north_walk | 56–63 | Definite opposite-leg outlier f57 between f56/f58; sparse passing elsewhere. |
| north_attack | 64–69 | Raised striking arm coherent; waist orange/gold changes (notably f67→68→69). |
| north_cast | 72–77 | Gold neutral→orange preparation/release→gold end; palms clear. |
| north_hurt | 78,79,70 | Shoulder recoil reads; orange f78→gold f79/70. |
| north_dodge | 80–83 | Coherent lean; waist changes around f80→81 and f82→83. |
| west_idle | 98,99 | Disclosed east mirror; repeats gold→orange waist swap. |
| west_walk | 84–91 | Disclosed mirror; side feet read; not independently authored poses. |
| west_attack | 92–97 | Disclosed mirror; readable jab, stance/waist join concern remains. |
| west_cast | 100–105 | Disclosed mirror; orange-tab switches f101→102 and104→105; v1 marker low. |
| west_hurt | 106,107,98 | Disclosed mirror; recoil clear, waist changes to neutral gold. |
| west_dodge | 108–111 | Disclosed mirror; lean useful, orange/gold return mismatch. |

## Reproduction and evidence

Run these installed-Pillow scripts from any directory. They only write beneath this review directory:

```bash
python3 /home/astra/artifacts/emberwake-character-review/v1/review_assets.py
python3 /home/astra/artifacts/emberwake-character-review/v1/supplemental_evidence.py
python3 /home/astra/artifacts/emberwake-character-review/v1/scaled_pairs.py
python3 /home/astra/artifacts/emberwake-character-review/v1/freeze_review.py
python3 /home/astra/artifacts/emberwake-character-review/v1/write_report.py
```

`review_assets.py` crops actual atlas cells, creates chronology and pair sheets, builds exact-rational APNG files, verifies decoded pixels, and provides `player.html`. `supplemental_evidence.py` builds waist/foot crops, compact 2× pairs, and local atlas copies for the player. `scaled_pairs.py` produces nearest enlarged/reduced pairs. `freeze_review.py` rechecks frozen input hashes and actual APNG delays and emits the score receipts. No external package installation is required.

Evidence navigation:

- `lyra/scores.json`, `brann/scores.json`: separate ratings, confidence, ranked repairs and scope.
- `INPUTS.json`: original file hashes and complete clip/hold/bounds ledger.
- `VERIFICATION.json`: all clip IDs, APNG hashes and actual delay fractions; final source hash comparison.
- `<character>/<direction>-native.png`, `*-2x.png`, `*-drawscale.png`: all six actions in declared order.
- `<character>/pairs/<direction>-all-native.png`: every internal pair and diagnostic/declared wrap.
- `<character>/pairs/<clip>-2x.png`: each clip's nearest 2× pairs.
- `<character>/pairs/<direction>-idle-joins-{native,drawscale,2x-all}.png`: all endpoint joins.
- `<character>/media/<clip>.png`: exact-hold animated PNG. Nonloops have a one-play APNG count.
- `player.html`: normal-speed human follow-up aid; repeats a review sequence with optional idle entry/return, and labels its nonloop repetition as review-only.
- `<character>/cast-palm-markers-2x.png`: overlay of the nominated v1 marker, not altered source art.
- `brann/*-waist-crops-4x.png`, `<character>/*-feet-4x.png`: targeted defect evidence.

The player can be opened locally or served from this folder. It was not launched for this review. Opening animated media in a viewer that only shows its first frame does not constitute motion perception.

## Frozen input hashes

Combined input fingerprint: `7eee41206a5fd632cd664a2dfef5c3cd327e1a5767bfa79d1226ca48162a7a2f`. This is SHA-256 over compact, key-sorted JSON of the per-character filename→SHA-256 input mapping. Final checks confirmed all six nominated files unchanged.

| Character | Input | SHA-256 |
|---|---|---|
| lyra | atlas.png | `a46d7ba7b260ce3a1a42f81ee3001325fee310a6284396e316476b0743a9624d` |
| lyra | animations.json | `3f823795e13e5d84571a84818042a17e421871944bac3baf4db3e8b03a5c6cde` |
| lyra | selected-contact-sheet.png | `97fd6d671dc5d4899839c0998732943d8cc7f2d22549e713c562269d32f6b3a6` |
| brann | atlas.png | `68d5ae1c846153bc0483beb4894069ed243db5998ed1e9733b7df212996134ff` |
| brann | animations.json | `610c8502b0d91323ad48c89b76e36d09649d16f452e7fc07301b1c1de8a70c2c` |
| brann | selected-contact-sheet.png | `a0cc10c706480305ec50f1c12b393a111e45e162cf3d0e8126c6d1697a10bc8c` |

Changed pixels or timing invalidate this review; a metadata-only correction must be identified separately. No approval is transferred to later versions.
