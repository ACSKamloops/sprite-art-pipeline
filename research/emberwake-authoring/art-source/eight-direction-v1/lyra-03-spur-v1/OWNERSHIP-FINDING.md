# SE03 compact spur proof

This is one bounded local cleanup trial, pending root inspection. No model calls, canonical writes, editor package, scores, or motion/contact acceptance.

The detached dark line is not the current pose's glove, cloth, boot, or new hidden anatomy. `inputs/maps/03-composition.npz` identifies SE03 x44–50,y86 as mapped left-leg layer2, donor coherent02 x44–50,y85. The source pixels are the bottom outline of the original key02 glove; the lower partial-alpha halo at source x44–48,y86 becomes target x45–49,y87 and y88. The leg-owner construction admitted these neutral dark glove colors because it relied on a neutral-color threshold above y87. The original glove source and claimed leg owner are shown beside the target in `proof/compact-source-owner-before-after.png`.

The trial has17 actual changed RGBA pixels:16 literal transparent erasures plus1 measured hip restoration. Target(50,86) was the last partial-alpha glove contour texel composited over actual02 hip underpaint. Its restored value is actual02(50,86)=[17,10,7,255], rather than an invented transparent hole. The target glove still ends at y83. Current hip/leg paint at x49,y85 and the continuing boot/leg contour x50+,y87+ are retained; this trial does not expand beyond the demonstrated detached line and halo.

The script verifies target gloves, upper and hem, the complete target boot mask, the donor boot mask at every edited source coordinate, and all pixels outside the literal mask. The other seven frames are byte-exact copies. The input freeze and `INPUT-HASH-CHECK.json` bind every local input and original canonical source before/after. `journal/03-literal-erasure.json` retains exact previous RGBA, replacement RGBA, source coordinates and output hash; replay and inverse undo are asserted by `repair_spur.py`.

Run `python3 repair_spur.py` from this folder. It writes only this isolated folder and re-verifies the canonical files read as inputs.

The six `proof/full8-{native,2x,84}-{light,dark}.png` sheets use fixed128px canvas registration and nearest resizing. Upper row is current05path control; lower row is this cleanup. No pose fitting or timing change occurs. The02→03 geometry remains unchanged. The compact source-owner proof is the intended first inspection; larger editor/animation packaging waits for root review.
