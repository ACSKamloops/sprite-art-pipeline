# Independent current-art review — frozen character banks

Reviewed only the nominated Lyra and Brann `atlas.png` and `animations.json` files under `art-source/characters-v2/bake-v6`, plus the case-free blind review card. No checkout was changed. No other reviews, production reports, history files, network, provider/model/generator calls or runtime tests were used.

**Independence qualification:** an initial unfiltered manifest print accidentally exposed lineage source paths, transform fields, a repair-plan filename and edit metadata. No referenced files were opened and those fields were not used to judge quality. Subsequent review used source pixels and animation fields only. This review is independent of other reviews, with that incidental production-metadata exposure disclosed. It was frozen before seeing any other review.

## Judgment

Both are strong, usable art banks for the stated compact top-down adventure. Their rich shaded chibi style fits the brief; I have not applied a limited-palette or 16-bit standard. Lyra's silver hair, face and teal/gold costume remain cohesive across the four cardinal views. Brann's curls, beard, bronze armor and indigo/red costume retain a consistent identity. Full bodies, joint connections and materials read convincingly at native size, and the main action silhouettes survive reduction. I found no major anatomy, identity, alpha-edge or framing break in the reviewed clips.

Brann west is the disclosed mirror of symmetric east. It works visually within this brief; this review does **not** claim four independently painted Brann views. These are cosmetic alternatives with the same declared action structure; gameplay parity was not runtime-tested.

| Character | Drawing | Consistency | Motion | Game usefulness | Whole bank |
|---|---:|---:|---:|---:|---:|
| Lyra | 8.6 | 8.4 | 7.6 | 8.2 | **8.2 / 10** |
| Brann | 8.4 | 8.3 | 7.6 | 8.1 | **8.1 / 10** |

Scores are independent art judgments, not mechanical pass rates or an arithmetic average. Hashes, frame counts, exports and cell bounds earned no art points. Drawing/consistency confidence is high for the reviewed packet; motion confidence is medium because it is a reconstruction from still chronology. Game usefulness is medium-confidence without the actual map or controls. Treat whole-bank precision as approximately ±0.5 point.

## Main concerns and smallest useful experiments

1. **Dodge recovery spacing is concentrated into the first recovery pose, both characters.** The crouched/leaned body changes to a nearly centered, straight-legged pose before the final small rise. Lyra: `south_dodge f26→f128→f27`, `east f54→f129→f55`, `north f82→f130→f83`, `west f110→f131→f111`. Brann: `south f26→f128→f27`, `east f54→f117→f55`, `north f82→f118→f83`, `west f110→f119→f111`. The preceding pose holds 55ms, then each recovery pose 27.5ms. This is a modest pose-spacing concern, not proof that normal-speed playback looks bad. Test one side-view recovery pose with a more intermediate knee bend and torso lean, preserving the 260ms duration. The expected benefit is a more continuous weight transfer without slowing the dodge.

2. **The north strike is the least immediate attack silhouette, especially Lyra.** In `north_attack f65→f66→f67→f68`, the large rear head occludes much of the striking arm. At the game proxy size, the fist occupies only a small lobe outside the upper-right hair edge. Brann's bronze forearm helps, and neither character shows a demonstrated anatomical failure. Compare one alternate strike key pose with the fist slightly farther outside the head and a clearer arm diagonal, at unchanged timing on the actual map. The expected benefit is faster action recognition; the current side-view punches already read strongly.

3. **Brann's rear hair separation is conditional on dark ground.** In `north_idle f70/f71` and the other north-facing clips, curl detail and the outer hair edge recede against the tested `#192329` background after reduction. Bronze shoulders and costume still identify him. First test existing art on the darkest actual map ground. Only if the contour still disappears, try a restrained cool rim on a few outer clusters. This concern does not justify broadly lightening dark hair or skin.

I did not establish a detached limb, swapped support leg, lost costume element or severe drawing defect. The gait sequences show alternating feet, shortened swing legs/passing poses and opposing arm changes. Occlusion in north/south views is plausible. Physical foot planting against world displacement remains unverified.

## Coverage and presentation

Every one of the 24 clips per character was inspected in actual manifest order: south idle/walk/attack/cast/hurt/dodge, then east, north and west in the same action order. Every ordered pose, predecessor/current pair and loop wrap was examined. Native 128px cells on light `#d5d1c9`, nearest 2× 256px cells on dark `#192329`, and nearest 85px cells (~0.664, a rounded proxy for 0.66) on both backgrounds were inspected through original-detail image tools. Pivot is `(64,112)`.

Each character has 128 ordered frame exposures across 24 clips: 104 within-clip adjacent pairs, eight idle/walk wraps and 16 nonloop terminal-to-idle joins. Lyra uses 120 distinct source cells and Brann 116. In addition to idle-first entry/exit strips, six-by-six same-direction terminal-to-first state grids were inspected in each direction (144 pairs per character, including self pairs). These include idle-second-pose entries and walk-to-idle joins. This does not certify arbitrary mid-clip interruptions or cross-direction turn transitions.

| Action | All four directions, both characters | Visual assessment |
|---|---|---|
| Idle | 2 poses; 580ms each; 1.16s loop | Stable identity and clean wraps; quiet two-pose breathing rather than rich idle motion. |
| Walk | 8 poses; 56.25ms each; 450ms loop | Readable alternating leg/arm progression and coherent wraps; game ground-contact behavior not tested. |
| Unarmed attack | 8 poses; 410ms | Guard, strike and return read; strong side silhouettes, weaker north silhouette. |
| Cast | 6 poses; 500ms | Central gathering and open-hand release distinguish casting from punching. |
| Hurt | 3 poses; 290ms | Compact guarded recoil; eye closure helps front/side views; terminal pose is idle. |
| Dodge | 5 poses; 260ms | Low brace/lean reads; first recovery step concentrates the return to upright. |

The complete per-clip frame order, holds, presentation timestamps, coverage flags and individual visual notes are in `input-ledger.json` and `review.json`. All holds were considered, including the 35ms attack recovery poses and 27.5ms dodge recovery poses. No timed media was claimed as continuously perceived: **motion judgments reconstruct decoded still chronology and known holds, not human normal-speed playback or controller feel**.

No conspicuous fringe or clipping appeared against either background. Used-cell alpha bounds remain inside the source cell: Lyra `(19,14,110,113)`; Brann `(14,11,115,114)` (right/bottom exclusive). This supports framing only.

## Evidence and fingerprints

The `*_native_light.png`, `*_2x_dark.png` and `*_game_contrasts.png` direction sheets contain exact source-pixel chronological frames with idle entries and wraps/idle exits. The `*_state_joins.png` grids show terminal-to-first pairs. The `*_detail.png` sheets enlarge selected source pixels for the concerns above; they contain no newly drawn art.

| Input | SHA-256 |
|---|---|
| `lyra/atlas.png` | `f177d69482bac4c4a6c1c171e5679e5da1c1c45fa11fbf6b56a0fbf4f5fae901` |
| `lyra/animations.json` | `70b8de14097ecb82ba0ff9aec2d92e1c965c67f8010fbeffa82b50236658123f` |
| `brann/atlas.png` | `69dd1bf4061ee0f7c740bb6f2f9ec44166f13ca8d651293aa5e23b003d6451f4` |
| `brann/animations.json` | `2c9d6d1212eba569c8d705851a129180b633aaeccf2eac643c30acb964f35921` |

`FREEZE.json` binds the written report, review JSON, ledger and visual evidence. `SHA256SUMS` binds that freeze record and the same files. Changed input art or timing requires a new scoped review.
