# Anonymous full-walk review

**Verdict: slight preference for B; retain both as usable candidates for human playback.** B's cel 03 gives the boot a more convincing intermediate turn between 02 and 04. This is a small benefit in one eighth of each walk, not a wholesale gait improvement. I would choose B if a single anonymous candidate must advance. Neither candidate earns continuous-playback or engine/contact acceptance from this review.

| Variant | Appearance / 10 | Identity / 10 | Motion / 10 | Game use / 10 |
| --- | ---: | ---: | ---: | ---: |
| A | 8.2 | 9.0 | 7.6 | 7.9 |
| B | 8.2 | 9.0 | 7.8 | 8.0 |

The motion scores assess reconstructed full-cycle chronology, pose readability and continuity. The game-use scores assess presentation at the reviewed sizes and grounds. These are scoped judgments, not an overall production quality certificate. Confidence is moderate in the small preference and high in the shared identity assessment.

## Scope and independence

Read the anonymous review card at `/home/astra/.codex/skills/sprite-animation-pipeline/references/blind-review-card.md`, then used only the nominated packet input and review derivatives made here. No producer folder, reports, source mapping, score history, parent state, canonical art, browser, model or new art was opened or edited. No accidental exposure occurred. The manifest itself reveals that A/B differ only at 03 in each direction; that is legitimate input evidence, not unblinding.

Reviewed all 32 walk PNGs: A/B, northeast/northwest, 00–07, and all 32 cyclic adjacent pairs including 07→00. Cardinal east/north/west imagery and the appearance reference informed identity and turn context only. They did not approve the walk motion.

The original stage is 128×128 with pivot (64,112). Diagnostic composites preserve whole-canvas registration and use nearest-neighbor 128×128, 256×256 and 84×84 presentations. Grounds are light `#e7e3d6`, dark `#22252b`, and game `#27392f`, as supplied by the parent after clarifying that the packet contains no diagnostic sheets or ground images. The initial temporary sheets used other neutral swatches; they were replaced before final judgments. The frozen construction script records the final exact settings. An extra 6× lower-body crop identifies local contours; it did not replace native/reduced-size evaluation.

The frozen manifest declares eight equal holds of 9/160 second (56.25 ms), a duration of 9/20 second (450 ms), and no interpolation. Declared cel starts are 0, 56.25, 112.5, 168.75, 225, 281.25, 337.5 and 393.75 ms. The loop boundary is 450 ms. There is no encoded playback clip in the nominated inputs, so there were no actual video presentation timestamps to inspect. The timing arithmetic and cyclic order were checked against the manifest; visual motion judgments reconstruct chronology from stills and known holds. I did not perceive normal-speed continuous playback or test controller response, travel speed, foot locking or physical contact.

## Drawing, identity and practical scale

Both candidates preserve Rowan's spiky copper hair, compact rear three-quarter head, blue-and-gold tunic, bright rounded shoulder plates, segmented forearm metal, brown gloves, cream trousers and substantial brown boots. Head mass, shoulder attachment and costume colors remain stable across the cycle. The back-facing diagonal silhouette connects naturally to the cardinal identity context. There is no demonstrated disconnected knee, orphaned boot or persistent wrong-way joint.

The arm/torso construction remains legible while the legs alternate extension and tuck. Metallic highlights remain distinct from leather; boots retain their dark underside and cuff bands. Framing has comfortable room without visible clipping. On the dark/game grounds the darkest boot underside is less distinct, but the cream thighs, copper hair and metal keep the actor readable at 84×84.

At A03 the low boot preserves a stronger lateral toe projection and a more upright shaft. B03 shortens that projection and turns the boot into a more frontal, compact intermediate volume before 04's diagonal boot. In 02→03→04 this reduces the visual jump in toe orientation, especially at 128 and 256; the same benefit remains modestly visible at 84. B's wider cuff read at the passing pose is compatible with foreshortening. It does not, by itself, demonstrate a swollen leg or material identity change. A's more lateral toe remains plausible and is not a reject.

The changed RGBA region is x60–80/y84–111 inclusive in northeast and x48–68/y84–111 inclusive in northwest. Both contain 409 changed pixels. Head, torso and arms therefore receive no variant-specific identity credit.

## Full-cycle pair ledger

The ledger covers each row separately for both directions and both variants. Ground pair sheets place all three required scales beside every pair; light/dark cycle sheets additionally show every cel and wrap at all three scales.

| Pair | A northeast | B northeast | A northwest | B northwest |
| --- | --- | --- | --- | --- |
| 00→01 | Split pose compresses; boots remain attached. | Same as A. | Corresponding compression is coherent. | Same as A. |
| 01→02 | Clear extension/tuck exchange; a substantial pose change. | Same as A. | Clear extension/tuck exchange. | Same as A. |
| 02→03 | Knee/boot move under the hip; toe remains strongly lateral. | More intermediate toe turn and compact boot; slight gain. | Knee/boot move under hip; strong lateral toe. | More intermediate boot turn; slight gain. |
| 03→04 | Plausible crossing with a larger toe-direction change. | Turn into the diagonal 04 reads more gradual in still chronology. | Plausible crossing; larger toe-direction change. | More gradual turn into 04. |
| 04→05 | Lower silhouette compresses; overlapping boots are less distinct at 84. | Same as A. | Same reduced-size overlap limitation. | Same as A. |
| 05→06 | Boots separate into the opposite extension; role is readable again. | Same as A. | Clear opposite extension after overlap. | Same as A. |
| 06→07 | Extension folds back toward the split pose; attachments stable. | Same as A. | Corresponding fold is coherent. | Same as A. |
| 07→00 | Very similar split poses; no spatial reset or identity jump observed. | Same as A. | Very similar split poses; no reset observed. | Same as A. |

## Minimum meaningful remaining issues

1. **Shared minor reduced-size phase ambiguity at 05.** In both directions and variants, the two boots overlap into a narrow brown cluster under the hem. This is clearest on the dark/game grounds at 84, in 04→05 and 05→06. The raised-versus-lower boot distinction is weaker than at 02/06. The source region is approximately x58–76/y89–112 northeast and its corresponding northwest region. This is a readability limitation, not evidence that the limbs are fused or anatomically wrong. Genuine occlusion is allowed; I do not recommend forcing a permanent gap. The smallest next experiment is unchanged-clock human playback at 84 to determine whether the distinction is actually lost in motion. Only if it is lost, try a small value/edge adjustment inside the existing overlap rather than opening a gap or replacing the whole pose. Expected benefit: clearer alternating leg roles.
2. **Shared near-hold across 07→00, a pacing question rather than a proven defect.** These adjacent poses preserve almost the same broad split silhouette for two 56.25 ms holds. The pair does not show a hard reset. It could create a perceptual dwell at the boundary, but stills cannot establish an unwanted hitch. Compare several original-clock loops in human playback before changing timing or art. Expected benefit if a dwell is confirmed: more even perceived cadence. This hypothesis was not counted as a demonstrated broken loop.

There is no additional sole or cuff defect strong enough to justify another paint iteration from this review. The short stair steps in the reduced boot contours are compatible with nearest-neighbor reduction and remain readable as boot edges. I do not require a flat horizontal sole, and I do not penalize legitimate foot occlusion. The remaining evidence does not support rejection of either variant.

## Integrity and freeze

`input-hashes-before.json` and `input-hashes-after.json` cover all 63 input PNGs plus `INPUTS.json`. All 63 PNG hashes match the frozen manifest. The before/after ledgers match exactly, so no nominated input changed. `FREEZE.json` fingerprints the final report, structured judgment, ledgers, construction script and review images. The freeze is complete before any source unblinding.
