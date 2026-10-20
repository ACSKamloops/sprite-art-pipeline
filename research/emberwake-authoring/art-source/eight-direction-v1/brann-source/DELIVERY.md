# Brann diagonal production delivery

Built-in OpenAI ImageGen only. Four calls total: SE initial, NE initial, SE walk-only repair, NE walk-only repair. Budget exhausted. No H3, local model, CLI generation, repo edits, runtime test, independent art score or acceptance.

## Raw deliverables

- `raw/brann-se-initial.png`: 1774x887 RGBA, 8x4 layout. SHA256 c6e2722e9a94e29f695a326526a832d1bc215058c21e5f363bb28c8a76f54d9a
- `raw/brann-ne-initial.png`: 1774x887 RGBA, 8x4 layout. SHA256 e631a1b0e7eb9e346f5d237a87830beed97f44bb3ef5e12857e18def8881cd0d
- `raw/brann-se-walk-repair.png`: 1774x887 RGBA, 4x2 walk-only layout. SHA256 aaf593b83cf4ba583eeac18ff59ad4908f67d0e1fa94d78645501cc99cdd2cc5
- `raw/brann-ne-walk-repair.png`: 1774x887 RGBA, 4x2 walk-only layout. SHA256 6dcb1cdda939ccd117d3181a4d2ef5535d88b00a0159d88b4d6788ef001119df

All prompts are literal actual submissions in `prompts/`. Input roles/hashes, output cache locations, raw byte counts, dimensions and alpha histograms are in `receipts/`. Original input appearance is copied and retained under `inputs/`; it is appearance only. Each repair has an extracted walk edit target and a magenta/cyan pose-only schematic guide, not generated identity art.

## Producer inspection

The SE initial is visibly front three-quarter, distinct from the source front/profile. NE is correctly back three-quarter across all32 cells: back hair/tunic remain visible and front face/chest are hidden. Identity, palette and costume read coherently at proposed96px painted native height. These are candidate appearance observations, not independent ratings.

The original walks repeat the leading boot at requested opposite contacts0/4; passing2/6 is weak. Both targeted repairs still fail to unambiguously deliver the required opposite contacts. Some intermediate leg poses changed, but neither sequence is accepted as repaired. The tool also rerendered upper bodies despite a preservation request. If any repair leg art is used, restore original body RGBA outside a declared leg ROI exactly; prompt wording is not pixel protection. Do not promote these repair sheets wholesale.

SE attack follow-through r1c3 extends over the right cell boundary; r1c4 contains a clipped fragment of that fist at x0. Connected source overflow could be extracted once before slicing, or the affected exposure rejected/replaced with a disclosed repeated valid contact. This report does not supply an approved reconstruction. Both attacks snap from extended contact to close guard rather than providing the requested gradual early recoil. SE punch also reads more horizontally eastward than the declared down-right aim.

Both casts have a visibly open release hand at r2c3. Recovery r2c4 is already close to guard, leaving limited halfway return. Dodge r3c4→5→6 shows rising head and knees in static sequence, with a larger last rise at5→6. Actual normal-speed motion and all action joins still need review.

## Proposed registration only

`receipts/registration-proposals.json` freezes one uniform scale per direction and declared row origins after one whole-sheet nearest resize to2048x1024. No per-pose bounding-box fitting. Destination128x128, pivot64,112; approximate96px neutral painted height.

- SE scale0.425; normalized row origins (x,y): (146,254),(146,245),(146,246),(146,242).
- NE scale0.457; normalized row origins: (136,247),(136,244),(136,247),(136,242).

`proofs/*native-proposed.png` and `*native-dark-light.png` are proofs using those proposals, not final integration. Their alpha is retained; no raw paint or threshold cleanup. `*walk-comparison-native.png` places original above raw repair at the same declared transform, showing that a tool return does not establish successful gait repair. Root owns the unified baker and final body/leg compositor.

No southwest/northwest art was separately generated. Conditional mirroring of this symmetric unarmed design is possible, but must be disclosed and reviewed for shading/hand consistency. Eight-direction motion8/10 is not demonstrated.
