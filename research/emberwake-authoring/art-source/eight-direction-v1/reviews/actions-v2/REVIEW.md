# Diagonal action review — frozen candidate-v2

**Scoped overall: 8.1/10.** These are strong, polished compact chibi heroes with coherent costume/material identity and readable punches. They are usable body-animation candidates. The most useful polish is better idle attitude continuity for Brann, clearer rear hurt/dodge separation, and a cast body silhouette that depends less on tiny fingers.

Only the four new diagonals for idle, attack, cast, hurt and dodge were graded: **60 clips, 288 scheduled exposures**. Every frame, adjacent pair, idle entry/recovery from both breathing phases, and idle loop wrap was inspected in chronological sheets. The coverage ledger contains 480 labeled comparisons, including identical and alternate neutral comparisons. Both cardinal idle phases were used for the eight-facing turn ring. **Walk is not graded.**

Inputs are bound by [input-hashes.json](input-hashes.json), [SHA-256 ledger](input-hashes.sha256), and the copied `inputs/` packet. All 15 original source files still matched their frozen copies when the review was saved. No canonical source was edited.

## Viewing and limits

Compared the nominated appearance references with every pose at native 128-stage, nearest 2x, and requested .66 game scale (rounded to an 84-pixel stage), on dark `#1e222b` and light `#dcdacf` grounds. The exact timelines in [coverage.json](coverage.json) preserve atlas frame IDs, exposure starts/ends and holds. Durations are idle 1.16 s, attack .41 s, cast .50 s, hurt .29 s, dodge .26 s.

**Perception was decoded stills and chronology with known holds.** This does not claim continuous human normal-speed playback, controller feel, in-engine effects, root-motion behavior, collision, or physical foot contact. The lower motion/usefulness confidence is explicit: roughly ±1 point, versus ±.5 for drawing/identity. No extra art credit was given for frame count, timing, metadata, or extraction success.

Only the nominated case-free blind-review card and nominated asset inputs were read. No prior score, producer report, other skill, or other-agent review was opened. The initial animations JSON output inadvertently exposed its lineage and construction notes; that provenance contained no prior grades and was excluded from visual scoring.

After the initial REVIEW.md and review.json and all numeric ratings were written, but before final report checksums were frozen, root sent confirmation of its related walk-key and Brann guard observations. Root supplied no numeric target or other reviewer scores. Those messages were not used to change the already assigned ratings or initial visual findings. This is a declared independence limitation for the final packet.

Ratings are absolute judgments: 5 recognizable with substantial deficiencies, 7 competent with noticeable limits, 8 strong, 9 exceptional. No target was supplied. Matched mirrored-view scores follow inspection of both views; they do not assume that mirroring is automatically acceptable.

| Scope | Appearance | Identity consistency | Motion | Usefulness |
|---|---:|---:|---:|---:|
| Rowan mean | 8.75 | 8.65 | 7.46 | 8.06 |
| Lyra mean | 8.68 | 8.68 | 7.25 | 7.76 |
| Brann mean | 8.68 | 8.59 | 7.30 | 7.77 |
| All scoped clips | 8.70 | 8.64 | 7.34 | 7.86 |

These means are summaries of separate art dimensions, not certification thresholds. The 8.1 overall uses equal weights and rounded judgment precision.

## Material findings and exact pairs

### F01 — moderate polish

SE/SW fists are raised in front of the body, with bent elbows; neighboring S/E/W neutral drawings hang the gloves lower beside the body. Turning alone changes readiness. The costume and person still match. This is also visible in phase 1: S15, SE159, E43, W99, SW255.

Classification: demonstrated pose-attitude discontinuity, not an anatomical failure. Confidence: high for the pose difference; effect on controller feel is untested.

Exact phase-0 pairs: Brann **S14 → SE158 → E42**, and **W98 → SW254 → S14**. The same difference exists at S15 / SE159 / E43 / W99 / SW255. Look at bent elbows and glove height in stage region x38–91, y56–96. [Turn ring](views/brann-reference-turn-ring.png).

Expected benefit: A steadier idle attitude as the player changes facing.

Smallest next experiment: Paint one SE neutral with relaxed forearms matching S/E while retaining the current diagonal view; compare S14 -> proposed SE -> E42 at .66. If combat-ready idle is the desired design, test the opposite experiment on the cardinal neutral.

### F02 — moderate polish

Rear hurt poses tuck the head/shoulders into a forward guard, with two similarly compressed exposures then a comparatively large change to standing. Rear dodge uses a related head/hand tuck with a deeper or wider leg stance. Both actions are coherent; the body-only .66 silhouettes distinguish them less strongly than their front counterparts. A belly-hit tuck can be valid, so this is not proof of wrong hit direction or broken anatomy.

Classification: demonstrated limited pose differentiation; playback consequence remains uncertain. Confidence: high for static similarity and neutral gap; medium for normal-speed salience.

Exact rear pairs (hurt0 → hurt1 → idle; comparison dodge1):

| Hero | NE | NW |
|---|---|---|
| rowan | 176 → 177 → 174; dodge 180 | 208 → 209 → 206; dodge 212 |
| lyra | 192 → 193 → 190; dodge 196 | 224 → 225 → 222; dodge 228 |
| brann | 192 → 193 → 190; dodge 196 | 224 → 225 → 222; dodge 228 |

This concerns the whole compressed head/torso/leg silhouette, broadly x34–98, y24–116; it is not a claim that hidden fingers or toes are missing.

Expected benefit: A quicker distinction between being struck and intentionally evading, and a less abrupt-looking rebound.

Smallest next experiment: On one rear hurt pair, test a more asymmetric shoulder/head recoil and make the second pose visibly unwind toward the existing neutral. Keep total duration fixed so drawing changes can be judged independently of timing. Compare with the current dodge at .66 and then perform continuous human playback.

### F03 — minor to moderate polish

The cast is a guarded preparation followed by one main open-palm extension. The fist-to-open-hand difference is clear at 2x, while the head/torso and reach occupy much of the punch silhouette at .66, particularly on rear views and the dark ground. No spell effects were supplied or graded.

Classification: demonstrated shared action silhouettes; body-only perceptual ambiguity is a hypothesis. Confidence: high for pose overlap; medium for practical confusion without continuous playback.

Exact release comparisons (attack exposure 2 versus cast exposure 3):

| Hero | SE | NE | NW | SW |
|---|---|---|---|---|
| rowan | 130 vs 139 | 162 vs 171 | 194 vs 203 | 226 vs 235 |
| lyra | 146 vs 155 | 178 vs 187 | 210 vs 219 | 242 vs 251 |
| brann | 146 vs 155 | 178 vs 187 | 210 vs 219 | 242 vs 251 |

Each cast preparation exposure 2 → release exposure 3 was checked as well; exact IDs and pair fingerprints are in the JSON findings and pair ledger.

Expected benefit: Recognition of casting from the body silhouette before relying on fingers or an external effect.

Smallest next experiment: Test one cast with a distinct elbow/forearm preparation and a different release torso angle while retaining the hero and timeline; compare it directly with its attack at .66.

Positive exact-pair result: every attack finishes through its guarding recovery into its nominated idle0. The penultimate-to-final sequence is listed under `P01` in [review.json](review.json). No head/costume replacement or detached striking arm was demonstrated. A suspected Brann NE hand issue was rejected after examining **178 → 179** beside open-hand **187**: the compact punch knuckle silhouette remains clear. [Closer hand diagnostic](views/brann-ne-hand-diagnostic.png).

Framing and alpha edges looked clean on both grounds. Dark hair/clothing naturally lose some contrast on the dark ground, especially behind Brann’s head, but gold shoulders, silver hair/armor and the outer pose still identify the hero. There is no evidence here for a severe halo or clipped-limb defect. Missing face detail in rear views is legitimate occlusion.

## All per-action / per-view scores

Each row has its own assessment and exact timeline in [review.json](review.json). `A` appearance, `I` identity consistency, `M` motion reconstruction, `U` practical body-only usefulness. Directions are SE, NE, NW, SW.

| Hero | View | Action | A | I | M | U |
|---|---|---|---:|---:|---:|---:|
| rowan | SE | idle | 9.0 | 8.7 | 7.6 | 8.4 |
| rowan | SE | attack | 8.8 | 8.7 | 8.0 | 8.5 |
| rowan | SE | cast | 8.8 | 8.7 | 7.4 | 8.1 |
| rowan | SE | hurt | 8.6 | 8.5 | 7.1 | 7.8 |
| rowan | SE | dodge | 8.7 | 8.6 | 7.8 | 8.3 |
| rowan | NE | idle | 8.9 | 8.8 | 7.5 | 8.2 |
| rowan | NE | attack | 8.8 | 8.7 | 7.8 | 8.3 |
| rowan | NE | cast | 8.8 | 8.7 | 7.3 | 7.9 |
| rowan | NE | hurt | 8.5 | 8.5 | 6.7 | 7.3 |
| rowan | NE | dodge | 8.6 | 8.6 | 7.4 | 7.8 |
| rowan | NW | idle | 8.9 | 8.8 | 7.5 | 8.2 |
| rowan | NW | attack | 8.8 | 8.7 | 7.8 | 8.3 |
| rowan | NW | cast | 8.8 | 8.7 | 7.3 | 7.9 |
| rowan | NW | hurt | 8.5 | 8.5 | 6.7 | 7.3 |
| rowan | NW | dodge | 8.6 | 8.6 | 7.4 | 7.8 |
| rowan | SW | idle | 9.0 | 8.7 | 7.6 | 8.4 |
| rowan | SW | attack | 8.8 | 8.7 | 8.0 | 8.5 |
| rowan | SW | cast | 8.8 | 8.7 | 7.4 | 8.1 |
| rowan | SW | hurt | 8.6 | 8.5 | 7.1 | 7.8 |
| rowan | SW | dodge | 8.7 | 8.6 | 7.8 | 8.3 |
| lyra | SE | idle | 8.8 | 8.8 | 7.5 | 8.1 |
| lyra | SE | attack | 8.7 | 8.7 | 7.8 | 8.3 |
| lyra | SE | cast | 8.7 | 8.7 | 7.2 | 7.8 |
| lyra | SE | hurt | 8.6 | 8.6 | 7.0 | 7.6 |
| lyra | SE | dodge | 8.6 | 8.6 | 7.2 | 7.8 |
| lyra | NE | idle | 8.8 | 8.8 | 7.4 | 7.9 |
| lyra | NE | attack | 8.7 | 8.7 | 7.7 | 8.0 |
| lyra | NE | cast | 8.7 | 8.7 | 7.1 | 7.7 |
| lyra | NE | hurt | 8.6 | 8.6 | 6.6 | 7.0 |
| lyra | NE | dodge | 8.6 | 8.6 | 7.0 | 7.4 |
| lyra | NW | idle | 8.8 | 8.8 | 7.4 | 7.9 |
| lyra | NW | attack | 8.7 | 8.7 | 7.7 | 8.0 |
| lyra | NW | cast | 8.7 | 8.7 | 7.1 | 7.7 |
| lyra | NW | hurt | 8.6 | 8.6 | 6.6 | 7.0 |
| lyra | NW | dodge | 8.6 | 8.6 | 7.0 | 7.4 |
| lyra | SW | idle | 8.8 | 8.8 | 7.5 | 8.1 |
| lyra | SW | attack | 8.7 | 8.7 | 7.8 | 8.3 |
| lyra | SW | cast | 8.7 | 8.7 | 7.2 | 7.8 |
| lyra | SW | hurt | 8.6 | 8.6 | 7.0 | 7.6 |
| lyra | SW | dodge | 8.6 | 8.6 | 7.2 | 7.8 |
| brann | SE | idle | 8.8 | 8.2 | 7.5 | 7.8 |
| brann | SE | attack | 8.8 | 8.7 | 8.0 | 8.4 |
| brann | SE | cast | 8.7 | 8.6 | 7.3 | 8.0 |
| brann | SE | hurt | 8.6 | 8.6 | 6.9 | 7.5 |
| brann | SE | dodge | 8.6 | 8.6 | 7.3 | 7.8 |
| brann | NE | idle | 8.7 | 8.6 | 7.4 | 7.9 |
| brann | NE | attack | 8.7 | 8.7 | 7.8 | 8.1 |
| brann | NE | cast | 8.7 | 8.7 | 7.2 | 7.8 |
| brann | NE | hurt | 8.6 | 8.6 | 6.6 | 7.0 |
| brann | NE | dodge | 8.6 | 8.6 | 7.0 | 7.4 |
| brann | NW | idle | 8.7 | 8.6 | 7.4 | 7.9 |
| brann | NW | attack | 8.7 | 8.7 | 7.8 | 8.1 |
| brann | NW | cast | 8.7 | 8.7 | 7.2 | 7.8 |
| brann | NW | hurt | 8.6 | 8.6 | 6.6 | 7.0 |
| brann | NW | dodge | 8.6 | 8.6 | 7.0 | 7.4 |
| brann | SW | idle | 8.8 | 8.2 | 7.5 | 7.8 |
| brann | SW | attack | 8.8 | 8.7 | 8.0 | 8.4 |
| brann | SW | cast | 8.7 | 8.6 | 7.3 | 8.0 |
| brann | SW | hurt | 8.6 | 8.6 | 6.9 | 7.5 |
| brann | SW | dodge | 8.6 | 8.6 | 7.3 | 7.8 |

## Hero-specific reading

Rowan has the clearest front dodge through the low hand and strong body compression. Silver armor, blue tunic and cream trousers make attachment and leg grouping easy to follow. His front punch commits well; rear hurt has the least distinct rebound.

Lyra’s silver head and green scarf/cape preserve identity, with cape changes reinforcing attack motion. The front flinch has a readable closed-eye dip. The rear hurt and dodge share a forward lean, and the rear cast is most distinct through the small open hand.

Brann’s gold shoulder/forearm armor preserves volume particularly well through punches. His front diagonals introduce a raised fighting guard at idle, while cardinal neutrals relax the arms. His rear duck and hurt remain coherent but close in body vocabulary.

## Optional four-key pose diagnostic — not a walk grade

The new key images were compared only with the nominated registered Rowan 00/02 cells, at the same three scales and both grounds. This does not test a walk sequence, a wrap, or physical contact.

| New key | Assessment |
|---|---|
| southeast key 0 | Opposite ownership is possible but not demonstrated confidently. The new drawing opens the stride and crosses the cream trouser shapes under the coat, but still places a prominent forward boot toward screen-right. The hidden hip connection makes it unsafe to infer anatomical leg ownership from screen position alone. It is clearly a new pose, but new art does not by itself prove an opposite contact. |
| southeast key 1 | No convincing opposite passing/lift role. Both original02 and new key1 show a lifted cream knee/boot on screen-right and a lower planted-looking boot on screen-left. The new key is more frontal and steadier armed, but does not clearly reverse that visible role pattern. |
| northeast key 0 | Repeats the prominent screen-left leg and tucked screen-right-leg pattern. Both drawings emphasize the near large boot extending toward the lower-left, with the other boot small and tucked upper-right. The new key exposes a dark sole, which changes the contact impression but does not establish an opposite anatomical lead. |
| northeast key 1 | No demonstrated opposite leading/lift role. The dominant lower boot remains under the screen-left/central trouser leg while the other knee/boot stays lifted screen-right. Changing extension into a straighter plant does not provide the missing opposite half-cycle. |

The NE result is the clearest: the new pair still emphasizes the same visible leg and therefore does **not demonstrate the missing opposite half-cycle**. SE key0 may intend a swap through its crossed trouser shape; I cannot certify that ownership under the coat. SE key1 still repeats the visible raised-knee role. More separated boots alone do not prove a left/right role reversal.

Next small experiment: Before another full walk bank, make a temporary leg-ownership guide on the same camera pose: consistently mark each hip-to-knee-to-boot chain, and show one role-swapped contact plus its matching passing pose. Remove the guide for the final art. Re-review only those keys before assembling a walk.

[Full key comparison](views/opposite-key-diagnostic.png) · [Lower-body close-up](views/opposite-key-lower-body-diagnostic.png)

## Frozen artifacts and next step

- [Full machine-readable review](review.json): all 60 four-dimension ratings, per-clip assessments, timings, findings and input fingerprints.
- [Coverage](coverage.json): every nominated exposure, checked action pair, and 48 neighboring turn-ring idle pairs.
- [Exact pair pixel ledger](exact-pair-pixel-ledger.json): source-cell RGBA hashes, changed-pixel counts and changed bounds for the 480 comparisons. These numbers locate changes and earn no art points.
- [Exact changed-pair findings](exact-changed-pair-findings.json): visual findings bound to precise frame pairs.
- `views/`: 24 action sheets, three reference/turn rings and three small diagnostics, all made only from the frozen packet.

This review is frozen. Await a specifically nominated revised candidate before rerating. No source change or model call was made. Walk, normal-speed human playback, effects integration and controller acceptance remain outside this review.
