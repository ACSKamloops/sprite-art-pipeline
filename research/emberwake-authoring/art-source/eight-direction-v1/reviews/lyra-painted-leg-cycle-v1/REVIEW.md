# Anonymous full-cycle review: Lyra A / B

Frozen while A and B remain anonymous. No source mapping, producer report, prior grade, target score, history, model, browser or engine was used. The only procedural reference read was `sprite-animation-pipeline/references/blind-review-card.md`; art inputs were limited to the nominated `packet/input` directory. No accidental exposure is known. No input or canonical art was changed.

**Verdict: prefer A for this diagonal walk.** A is usable with modest temporal polish. B preserves the character but its frame 06 in both directions is a less coherent walk transition. I would decline B as the replacement walk in this comparison. Its 06 drawing is individually useful as a tucked, bent-leg action pose, so this is a sequence-fit judgment rather than a claim that the pose is impossible.

| Scoped grade / 10 | A | B |
| --- | ---: | ---: |
| Appearance, anatomy and material drawing across the cycle | 8.0 | 7.7 |
| Character and costume identity across frames and turn context | 8.5 | 8.5 |
| Motion and step readability reconstructed from the cels | 7.0 | 6.2 |
| Practical game-scale visual use for this walk | 7.5 | 6.8 |

These are scoped visual judgments, not computed measures or certification. Confidence is high in the identity tie, moderate in the A preference for motion. The difference is local: 14 of 16 corresponding diagonal cels are byte-identical between variants. An attractive one-frame action silhouette does not automatically improve its neighboring walk phases.

The painted, shaded chibi style reads well. Silver hair, face direction, teal scarf and coat, brass trim, gloves, dark trousers and brown boots remain recognizable throughout. Head and torso attachment are stable. The hands remain plausible at the sleeves; raised knees and overlapping boots can legitimately obscure part of a limb. I found no demonstrated detached limb, missing-foot failure, framing crop, or conspicuous light/dark alpha fringe in the inspected presentations. I did not require a permanent gap between legs, mirrored diagonal silhouettes, or soles on a common horizontal line.

The main distinction is the near leg in 06: screen-left for southeast and screen-right for southwest. In A the dark trouser volume leads into a substantial boot shaft and toe, with that leg still extending beneath the body. In B the thigh swings outward and the boot/shin compress into a shorter, sharply bent shape. The connection can be understood as a bent leg; it is not evidence of a detached boot. In isolation it suggests a compact hop, dodge or tucked action. Beside 05 and 07, however, the leg departs laterally and then returns to the longer boot silhouette instead of tracing a clear passing path. This creates a conspicuous extra crouched/splayed beat in the chronology. It remains visible at 84 pixels on all three grounds. The changed source regions are southeast `x=41..62, y=77..110` and southwest `x=66..87, y=77..110` (inclusive bounds, native 128 canvas). The numerical difference bounds locate the evidence; they do not establish anatomy or motion quality by themselves.

The other boot and trouser forms in both variants generally retain their material distinction. Boots have a broad toe, a darker sole and folded shaft highlights; trousers retain softer, charcoal rounded volumes. B/06's near boot presents much less of the familiar shaft and a different foot angle. Foreshortening could account for some volume change, but the adjacent poses do not clearly prepare or resolve that particular bend. This is primarily a temporal material/readability weakness, not a blanket rejection of perspective or occlusion.

Every cyclic pair was inspected for both variants in both directions. The following observations apply to both diagonal directions; the A/B distinctions are explicitly named:

| Pair | Full-cycle reading |
| --- | --- |
| 00→01 | The leading boot arrangement is retained with small body and limb changes. A/B equal. This is a restrained progression, not a new large step. |
| 01→02 | The leading leg lengthens downward while the other leg remains bent/partly obscured. Coherent attachments and material transitions. A/B equal. |
| 02→03 | The feet gather toward a narrower under-body arrangement; boot shafts remain legible. A/B equal. |
| 03→04 | The opposite leg's raised/bent role becomes clear. This larger phase change still reads as an alternating step through legitimate overlap. A/B equal. |
| 04→05 | The down-reaching near leg and raised other leg retain their roles, with modest changes. A/B equal. |
| 05→06 | A continues that arrangement with rounded trouser volume and a substantial down-reaching boot. B abruptly shortens and moves the near leg outward, adding a splayed/tucked action beat. |
| 06→07 | A has a relatively large exchange into the next split-step silhouette; it is readable but is the preferred version's least gradual phase change. B exits its short lateral bend into the restored long boot/forward-step arrangement, making the local detour more apparent. |
| 07→00 | The leading/trailing arrangement continues across the wrap. No separate head, costume, canvas or attachment reset was demonstrated. A/B equal. A modest pose change here is not itself a loop-break defect. |

Smallest meaningful next experiment: revise only the near leg in frame 06 of each diagonal, using 05 and 07 simultaneously as neighbors. Keep the boot's recognizable shaft/toe volume and bring the knee/foot along an under-body passing path between those neighbors. Compare the resulting 05→06→07 triplet and the full eight-frame cycle with the same holds. A's current 06 is the stronger retained option; any attempt to make its 06→07 exchange more gradual should be rejected if it weakens that volume or introduces a sideways tuck. This calls for a local drawing study, not more frames, new timing, a flat-sole rule, or a repaint of the stable head/costume.

Exact inspection coverage: all 32 variant PNGs (A/B × southeast/southwest × 00..07) and all 32 cyclic adjacent pairs (00→01 through 07→00 for each variant/direction) were viewed at whole-canvas 128×128, 256×256 nearest enlargement and 84×84 nearest reduction on each of light `#e7e3d6`, dark `#22252b`, and game `#27392f`. This is 288 pose presentations and 288 pair presentations, in 9 pose sheets and 36 pair sheets. No tight crop, recentering, silhouette masking, recoloring, interpolation, or sprite paint edits were used. Sheets add only labels, margins and the specified compositing ground. All 1,134 image cells in the complete generated sheet set were checked byte-for-byte against independently recomposed whole-canvas nearest presentations by the builder. This mechanical check validates the diagnostics, not the art grade.

The 31 context PNGs were limited to appearance/identity/turn comparison: `appearance.png` was viewed at its original 768×256; all 30 cardinal idle/walk cels were viewed in `context-128-light.png`, `context-256-dark.png` and `context-84-game.png`. Six additional context sheets were generated but were not part of visual inspection. Cardinal gait quality was not graded and cardinal imagery was not used as physical-contact evidence. The nominal manifest game scale is 0.66; the requested 84-pixel diagnostic canvas is exactly 84/128 = 0.65625 of the source canvas.

Timing is the manifest's eight rational holds of 9/160 seconds = 56.25 ms each, for a 9/20 second = 450 ms loop. Reconstructed frame starts are 0, 9/160, 18/160, 27/160, 36/160, 45/160, 54/160 and 63/160 seconds; the wrap is at 72/160 = 9/20. No encoded animation, independently observed presentation timestamps or continuous playback was supplied or used. Motion judgments reconstruct chronology from still cels and these known holds. They do not claim human normal-speed continuous perception, actual speed judder, foot contact, root motion, controller feel, browser playback or engine integration. Other directions/actions/equipment and transitions remain outside this review.

All 63 input PNG hashes matched the supplied ledger before inspection. `input-hashes-before.json` and `input-hashes-after.json` bind all 64 files, including the manifest, and are identical. `INPUTS.json` SHA-256 is `d6f3d3c299b327b235bedcebdcbc58f011691898d08b5126a2ec56108356d7a4`. `input-integrity.json` records the successful comparison. `sheet-index.json` names every generated diagnostic. `judgment.json` is the structured frozen verdict. Changed art or timing needs a new scoped review.
