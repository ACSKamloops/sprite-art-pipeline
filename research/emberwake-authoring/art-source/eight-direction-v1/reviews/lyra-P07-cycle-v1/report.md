# Anonymous whole-walk review — cycle critic

**Decision: tie. No confident full-cycle preference between A and B.** Both are usable-looking diagonal walk drawings within this static scope. B replaces one broad forward-boot pose with a more compact intermediate pose. That improves neither the entire gait nor the overall drawing unambiguously: it moves more of the boot's change in projection to the loop boundary. I would retain both as candidates for a timed playback comparison instead of declaring a winner from these stills.

| Variant | Appearance / drawing | Identity / temporal consistency | Motion / visible pose chronology | Practical game-size readability |
|---|---:|---:|---:|---:|
| A | 8/10 | 9/10 | 7/10 | 8/10 |
| B | 8/10 | 9/10 | 7/10 | 8/10 |

These are scoped judgments, with roughly one point of uncertainty in motion and half a point in the other categories. Equal scores are deliberate. Mechanical completion, pixel counts, file counts, and the coverage matrix earn no art credit.

## Scope and independence

I read only the nominated anonymous input directory and the anonymous review procedure at `/home/astra/.codex/skills/sprite-animation-pipeline/references/blind-review-card.md`. No producer mapping, canonical source, producer report, other review, prior grade, scored case, history, or STATE file was opened. No accidental exposure was observed. This report and `judgment.json` were frozen before any unblinding.

Inputs are the complete 63 PNGs and `INPUTS.json` under `/home/astra/artifacts/emberwake-lyra-P07-whole-walk-v1/packet/input`. All 63 image hashes match the manifest. `input-before.json` and `input-after.json` bind all 64 files, including the manifest, and are identical. The manifest SHA-256 is `5c72655108ae116447fecf6bd9eaf333615ed7b70c24d74b57e9c6274635dc10`.

I inspected all 32 nominated diagonal cels and all 32 cyclic adjacent pairs, including each 07→00 boundary, at exact 128, 256, and 84 pixel whole-canvas sizes on light `#e7e3d6`, dark `#22252b`, and game `#27392f`. I also inspected the appearance reference and all 30 east/south/west cardinal context cels. Context establishes identity and directional consistency only; it is not graded or certified here.

The diagnostic sheets preserve each complete 128×128 stage and do not recenter, crop, draw on, filter, or realign the sprite. Pillow nearest-neighbor resizing is applied to RGBA before alpha compositing onto the exact background. 256 is 2×; 84 is 84/128 of the canvas, the requested integer approximation to the manifest's 0.66 game scale. Labels and gutters sit outside the image canvases. The supplied pivot [64,112] was read as metadata and does not establish physical foot contact.

## Timeline and perception limit

Each of the eight declared holds is exactly 9/160 s = 56.25 ms; the complete cycle is 9/20 s = 450 ms. Declared frame starts are 0, 56.25, 112.5, 168.75, 225, 281.25, 337.5, and 393.75 ms; wrap is at 450 ms. Both variants have this same timeline. The packet contains PNGs plus timing metadata, not an encoded animation stream, so there were no independent video presentation timestamps to measure.

**Motion judgments reconstruct static chronology from these stills and known holds. I did not perceive continuous normal-speed playback.** There was no browser, engine, controller, root-motion or physical-contact test. This review cannot establish smoothness at speed, foot planting, actual support forces, sliding against a moving world, gameplay feel, other directions, transitions, equipment, or actions.

## Drawing, identity and anatomy

Both variants preserve the appearance reference's silver-white layered hair, youthful face, teal scarf and shoulder silhouette, gold-edged dark tunic, belt, metal cuffs, brown gloves, dark trousers and brown boots. The diagonal faces and costume sit convincingly between the front and side cardinal imagery. Head, torso, belt and shoulder proportions remain stable through all eight poses; the small vertical changes read as intentional walk bob in the still chronology. The pale hair and warm face remain recognizable at 84 pixels on every ground.

The boots stay visibly connected to trouser legs through cuffs in both variants. I did not demonstrate a detached boot, dislocated ankle, swapped leg, or disconnected hand. A tucked boot or partly hidden cuff can legitimately be occluded, and two projected legs do not need a permanent gap. The feet's differing heights and angled soles do not by themselves prove an error. I did not impose a flat sole baseline, mirrored silhouettes, or symmetric screen-space stride on the diagonal views.

The common 00–06 drawings retain leather color, broad cuff bands and rounded boot volume. Frame 06's high front thigh/knee is pronounced but remains connected to the hip and is followed by a lower leg; the overlap is not sufficient evidence of a limb-role failure. The light ground reveals small irregular silhouette pixels around gloves, scarf and cuff edges, but they follow the rendered source style; I found no persistent matte or catastrophic alpha halo across the grounds.

A and B are pixel-identical for 00–06 in each direction. Only frame 07 changes. The exact changed region is x=63–85, y=84–107 inclusive for southeast and x=43–65, y=84–107 inclusive for southwest. This is the advancing lower leg/boot, with nearby cuff/leg overlap; the identity-bearing head and torso are unchanged.

A's 07 has a broad, outward-reaching toe and continuous boot mass that resembles the full forward boot in 00. B's 07 has a narrower, more downward-directed boot beneath the hem. B is a plausible intermediate projection rather than an obvious anatomical break. A's larger projected forefoot is also plausible. The still packet does not establish that either projection is intrinsically correct.

## Full phase entry and exit

The following observations apply to both SE and SW and to both variants unless distinguished. All entries were inspected as individual cels and adjacent pairs at all nine size/ground combinations; `coverage.csv` records the concrete files. These are observations of visible pose order, not a force/contact model.

| Pair | Visible progression and finding |
|---|---|
| 00→01 | Maintains the leading-foot / tucked-other-foot arrangement with a small body and boot displacement. No identity or attachment break. It is a restrained change rather than a new step. |
| 01→02 | The lower leading leg becomes straighter and its boot projection narrows; the other boot remains visible and tucked. Limbs can still be followed. |
| 02→03 | Feet draw closer beneath the body and both lower legs become more vertical. The reduced gap is legitimate overlap, not disappearance evidence. |
| 03→04 | The visually dominant low boot changes side while the other leg folds. The leg overlap remains traceable in the full silhouettes. |
| 04→05 | Retains the low-boot / folded-other-leg arrangement with arm and bob changes. No fresh anatomy failure, though the pose change is again small. |
| 05→06 | The forward knee rises more prominently before the next extension. It is a stronger shape change than 04→05, but attachment and costume identity remain intact. |
| 06→07 A | The advancing leg unfolds into a much broader, outward toe silhouette. This is the largest local boot-projection change at cycle closure. It may look abrupt at 56.25 ms, but that perceptual pop was not observed in playback. |
| 06→07 B | Unfolds to a more compact, downward boot. This provides a more visibly distinct intermediate pose, while making the forward toe less clear in the individual 07 silhouette. |
| 07→00 A | The broad advancing boot already resembles 00, so the wrap continues its shape and direction with a relatively small change. No clear seam discontinuity in identity or canvas framing. |
| 07→00 B | The compact boot becomes broad and outward again. B therefore delays more of the projection change to this interval. It remains anatomically possible; the still comparison cannot determine whether this allocation feels smoother. |

At 84 pixels, A makes the advancing foot slightly more directional in 07, whereas B makes 07 more like a compact passing pose. Both then return to the same 00 and the remaining seven drawings. Neither gives a clear full-cycle silhouette advantage across every interval. This is why I do not turn a preference for one isolated 07 drawing into a confident gait preference.

## Minimum remaining concerns and smallest next experiment

1. **Unresolved distribution of boot shape change near closure, both variants.** Evidence is A's 06→07 versus B's 07→00, in the exact lower-leg regions above, visible at 128/256 and still detectable at 84. A places more broadening on entry to 07; B places more on exit. This is a demonstrated shape difference and a possible temporal pop, not a demonstrated physical or perceptual failure. The smallest next experiment is a controlled blind A/B presentation of the existing eight cels at the unchanged 9/160 s holds for several loops at 84 pixels. Compare both 06→07 and 07→00 before altering more art. Expected benefit: determine which distribution reads as a coherent advancing boot at speed. If neither wins, keep the existing art rather than manufacturing another revision.

2. **Shared low contrast in secondary dark forms at game size.** At 84 pixels on dark and game grounds, the scarf tail, dark thigh boundaries and shaded boot edges lose some separation, especially in 04–06 and the tucked boot in 00–01. Hair, face, gold trim and the broad stepping silhouette still read, so this is a limited readability concern, not rejection. The smallest optional art experiment is a restrained edge/value adjustment on those secondary forms, tested against the same backgrounds; expected benefit is tracking the tucked leg and scarf without changing the gait. No revision is required merely to force permanent leg gaps or bright outlines.

No fatal anatomical defect is demonstrated by this packet. Neither variant is rejected for drawing or identity. The minimum unresolved work before choosing a motion winner is the timed playback comparison above; the packet's still chronology alone is insufficient for that stronger decision.
