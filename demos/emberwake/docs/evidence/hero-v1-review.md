# Hero art: independent initial review

Frozen review, 2026-10-15. Scope: selected hero sprite art and its declared timeline only. The producer workspace was read-only. Game environment, controls, collision, attacks dealing damage, spell effects, ground shadow and runtime functionality are outside this review.

**Overall: 7.0/10, uncertainty about ±0.8.** This is a recognizable, appealing JRPG hero with useful action silhouettes and convincing small armor shapes. It is usable for a demo, but the walking art has registration and phase defects that would remain even with perfect exposure timing. I would repair those before calling the full hero animation set polished.

| Dimension | Rating /10 | Basis and uncertainty |
|---|---:|---|
| Drawing, materials and anatomy | 8.0 | Brown hair, blue/gold tunic, silver armor, cream trousers and brown gloves/boots retain their intended material identity. Cuffs, fists and open palms generally attach plausibly. ±0.6. |
| Temporal and view consistency | 6.9 | The same character survives all views; lateral registration and side-walk yaw/height changes weaken continuity. ±0.8. |
| Motion and action readability | 6.1 | Punch and casting poses read; north gait reverses its visible leg roles extra times and locomotion wraps jump. This is a chronology reconstruction, not a normal-speed playback judgment. ±1.0. |
| Practical use at game size | 7.0 | At roughly 63 px high the face, blue tunic and metal shoulders remain distinguishable. The set covers the required actions, but walking pops and faint alpha columns are visible liabilities. Runtime movement/effects could improve dodge readability; they do not certify this art. ±0.8. |
| Scoped overall | 7.0 | Judgment across the above, not an arithmetic acceptance formula. No producer target or prior score was supplied. ±0.8. |

## Independence and method

Used only the nominated atlas, animation metadata, selected contact sheet, game-scale proof, appearance reference, the producer AGENTS.md ownership rules, and the case-free `blind-review-card.md`. No producer report, scored case study, review history, STATE file, rejected source sheet or model was consulted. Accidental exposure: the initial full print of `animations.json` included its embedded lineage filenames/transforms and final source note. I did not open those raw sources or use their historical intent as visual evidence. This makes source provenance non-blind; scores and desired results remained blind.

Inspected all 24 clips, every selected pose, adjacent chronological pairs, held repetitions, eight loop boundaries, and each one-shot's nominated idle return. Also inspected idle-to-action entries and four-view turns. This does not certify every arbitrary gameplay interruption or a transition out of every walk phase.

Native review used nearest sampling of each 128 px cell to an 84 px cell, matching `draw_scale=0.66` to rounding and yielding an approximately 63 px body. Each native sample was doubled by nearest sampling for the 2× view. Light gray and dark green backgrounds were used for every clip; black and magenta were additionally used for representative alpha edges. Three/four-times atlas detail crops were diagnostic only and did not set the native-size score. The supplied selected and game-scale sheets were also viewed.

I cannot establish continuous human video perception from these tool images. Motion judgments reconstruct chronology from decoded stills and the explicit holds below. No claim of watching normal-speed playback or feeling a controller is made. Hold lengths are metadata facts, not art-quality credit.

## Demonstrated defects and smallest useful repairs

Coordinates below are **local to the 128×128 atlas cell**, with x right/y down, unless explicitly called global. Frame `F` has global cell origin `((F % 8)*128, (F // 8)*128)`.

### 1. North walk migrates left and snaps right at its wrap — high priority

**Evidence:** F48→49→50→51→52→53→48. The opaque hair/head centroid x is approximately 74.0, 72.8, 70.3, 69.1, 66.4, 61.7 while centroid y stays around 31.4–32.1. The blue back-panel centroid moves from about x75.2 in F48 to x61.1 in F53. This is not only an arm bounding-box change: the head and torso migrate together. Opaque whole-character bounds change from `(50,16)-(98,113)` to `(38,15)-(86,113)`.

The F53→F48 boundary therefore moves the head about **12 atlas px right / 8 game px** within one 75 ms step. The smaller continuous changes make the reset especially discontinuous. Compare the spine/back panel around local y50–65 and the head around y20–43 in `north-chronology.png` and `gait-source-details.png`. South walk shows a smaller related effect: F0 head/tunic x≈66.9/66.6 versus F5 x≈60.8/59.3, followed by the reset.

**Minimal repair:** make a translation-only registration trial for the six north keys, using the torso/spine and the intended support root together, preserving a small cyclical sway instead of a one-way drift. Compare the adjusted F53→48 and idle F66→48 joins at native size. Apply the same check to south F5→0. This needs pixel placement work; changing holds cannot remove the reset. Avoid aligning only the head if that makes the support foot skate.

### 2. East/west walk second half sits higher than the first — medium/high priority

**Evidence:** east F99→100, held through F103, then F103→96; west F107→108, held through F111, then F111→104. F96–99 visible soles reach approximately local y114–115; F100–103 reach y109–110. Opaque top/bottom bounds for F99 are y21–115, for F100 y17–110. The head and feet both move upward at the half-cycle join. The change is around **5 atlas px / 3.3 game px**, and returns at the wrap, instead of presenting a smoothly resolved support/torso change.

Examples: F99 global cell origin `(384,1536)`; F100 `(512,1536)`. The sole levels are directly visible in `sidewalk-source-details.png`; the native row in `east-chronology.png` preserves the effect. West repeats it because its walk is the declared mirror; that is one shared issue, not two independent failures.

**Minimal repair:** trial a roughly +5 px y placement of F100–103 and mirrored F108–111, then compare both half-cycle joins and the walk-to-idle sole relationship. Use it as a registration experiment, not an automatic final correction: retain intentional torso bob by editing the leg pose if necessary. A global sprite/pivot adjustment would not correct the two halves relative to each other.

### 3. North gait makes an extra visible leg-role reversal — medium priority

**Evidence:** after allowing for the body's lateral drift, the lower/longer boot is on one side in F48–49, the other in F50, back to the first in F51, then the other in F52–53. Thus the visible sequence is **A,A,B,A,B,B**, rather than two coherent support/swing half-cycles. The strongest pair is **F50→51→52**, at t=0.150→0.225→0.300 s. The near-lower boot lies left of the torso in F50, right in F51, then left again in F52; inspect local x≈56–78, y≈80–112. This is an actual drawn silhouette change, not a requirement for mirrored toes or fully visible hidden feet.

**Minimal repair:** test a replacement F51 that continues the F50→52 leg roles, with one leg passing beneath the pelvis while the other supports, and preserve its corresponding arm role. Review F49→50→51→52 at the same 75 ms exposures. Reordering an arbitrary existing pose could create a new arm or registration pop. South's A,A,B,B,B,A ordering does alternate coherently around its wrap; I do **not** allege the same extra reversal there.

### 4. Disconnected vertical alpha lines survive outside the body — low/medium priority

**Evidence:** these are visible faint hairlines against gray/dark/magenta, not hidden RGB. Representative selected frames:

| Frame | Local affected column/extent | Global coordinates | Alpha evidence |
|---|---|---|---|
| F1 | x11, y10–116, with a small gap | x139, y10–116 | Main isolated run y10–103 has alpha24–38. |
| F2 | x117, intermittent y10–116 | x373, y10–116 | Isolated lower run y77–116 has alpha24–44. |
| F19 | x11, intermittent y10–116 | x395, y266–372 | Lower run y98–116 reaches alpha52. |
| F22 | x116, intermittent y10–116 | x884, y266–372 | Lower run y76–116 has alpha25–36. |

These columns are far from the hero silhouette. They flicker on/off between idle/walk/action keys. `alpha-edge-detail.png` exaggerates them for diagnosis; they are faint at native size, so this is not the main reason for the overall score.

**Minimal repair:** remove those disconnected line components from the selected atlas cells while preserving the character-edge alpha. Screen other selected cells for the same one-pixel-column pattern. Raising the alpha cutoff globally would unnecessarily damage soft legitimate contours. Verify native gray/dark compositing after the targeted cleanup.

## Other observations, not additional proven failures

- **View identity:** hair color, outfit and silver/gold armor remain recognizable when turning south/east/north/west. Back and side silhouettes are convincing enough to be one character. I found no defensible detached wrist, floating fist, extra visible limb or wrong material that needs an anatomy repair. Brown glove fingers in casting remain consistent with the glove material.
- **East/west profile consistency:** F98–102 / F106–110 turn more strongly into side profile than idle F42/F90 and their attack/cast stance, particularly the head/near shoulder around local x45–82, y25–65. This is perceptible yaw modulation and a possible state-join pop, not evidence of a different character or an impossible joint. After registration is repaired, compare a profile-matched idle trial; do not regenerate a good face merely to remove legitimate gait twist.
- **South/back passing poses:** the six front/back keys mostly retain separated contact-like legs and a short tucked rear boot. South does alternate sides coherently, but intermediate support-to-swing progression is limited; it can read as quick stepping/shuffling rather than a rounded walk. A targeted passing-pose trial would give more useful evidence than adding exposures. This is a motion-quality limitation, not proof that an occluded foot is anatomically missing.
- **Idle:** all four idle pairs make small breathing/settling changes, with no large identity break on their wraps. Their 580 ms exposures are restrained. Some highlight/hair variation remains, but I do not have a confident improvement preference strong enough to call a separate defect.
- **Attack:** all four guard/windup/extension/recovery sequences are readable as an unarmed strike. The side extension in F32–33 and F80–81 is especially clear. Front/back foreshortening and arm occlusion legitimately conceal some extension. The last guard pose→idle is a noticeable stance release, but not a demonstrated broken join.
- **Cast:** gathering hands, opening/releasing palms and relaxing are distinct from the punch. North F63 spreading the hands is broad and readable; F64 retracts before F65 lowers. South F15–16 and side F39–40/F87–88 retain plausible cuff-to-palm connections. Final cast→idle joins are modest. I do not infer a required spell direction or effect from the body alone.
- **Hurt:** four short recoil/settle sequences are legible, each explicitly returning to its idle key. No lasting equipment/face change found.
- **Dodge:** F22/23, F46/47, F70/71 and F94/95 all read as a low braced dip/lunge, followed by a repeat of the first crouch and idle. Side directions lean more clearly. They do not by themselves communicate a full roll or travel distance; a moving dodge can legitimately use this. Whether a stronger compressed/leaning north/south middle pose is necessary requires actual game-speed human playback with translation. I am not treating the two unique crouch keys or the repeated exposure as a drawing defect.

## Complete timeline coverage

For every row below, both native and 2× still chronology were inspected. Loop rows include last→first. One-shot rows include the final→first idle comparison (hurt/dodge already include that idle frame). Idle entry comparisons were also made for walk, attack, cast, hurt and dodge.

| Clip | Selected frame order | Duration | Loop |
|---|---|---:|---|
| south_idle | F18 → F19 | 1.160s | yes |
| south_walk | F0 → F1 → F2 → F3 → F4 → F5 | 0.450s | yes |
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
| north_walk | F48 → F49 → F50 → F51 → F52 → F53 | 0.450s | yes |
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

Holds, in frame order: idle `580,580 ms`; south/north walk `75 ms` each; east/west walk `56.25 ms` each; attack `60,70,55,55,65,105 ms`; cast `60,80,100,80,80,100 ms`; hurt `90,100,100 ms`; dodge `45,105,55,55 ms`. Thus attack extension keys 3–4 occur at t=0.130–0.240 s; dodge's second unique pose occupies t=0.045–0.150 s. No interpolated frame was inferred from the existence of these holds.

## Frozen inputs and output packet

Start/end SHA-256 fingerprints matched for all five nominated inputs. Atlas size is 1024×1792, 8 columns of 128×128 cells; selected IDs are listed above. Unused atlas cells were not certified.

| Input | SHA-256 |
|---|---|
| `assets/hero/atlas.png` | `d4fffce5545f76707140d0f8d14ac9217c0777fc4df044a951d4b299256f0af9` |
| `assets/hero/animations.json` | `1c516f55dc7c0ef6a21e905dfcc6b4fc68e1005d661b0908293c431e7f44c73f` |
| `art-source/hero/game-scale-proof.png` | `0fc34d8818eaf58b2b8d50a2bce9a555c4d57f348f72c408ed82c45bcdf83f98` |
| `art-source/hero/selected-contact-sheet.png` | `d6465a57d41e2a27747dad8feeb3fab69e2fae9e168d945f1979ef8574d02c0c` |
| `art-source/hero/appearance-reference.png` | `1f9203ec653a5b9895e028c9b13e0748f16b22c5ba89fcbfa4545720264e9cce` |

Review artifacts are all confined to `/home/astra/projects/emberwake-review/`: this frozen report, start/end fingerprint JSON, four direction chronology PNGs, `view-and-entry-joins.png`, `gait-source-details.png`, `sidewalk-source-details.png`, `action-joins-details.png`, `cuff-hand-details.png`, `legs-and-dodges-detail.png`, `gait-centreline-detail.png`, and `alpha-edge-detail.png`. These packets are atlas-derived observations, not edited replacement hero art.

Recommended first repair order: north lateral registration, side-walk vertical registration, north F51 leg-role continuity, disconnected alpha columns. Re-review those actual changes at native size and 2×, then use human game-speed playback to decide whether passing poses, yaw harmonization or a stronger dodge middle are worth additional drawing work. Timing-only revisions would not change this report's drawing rating.
