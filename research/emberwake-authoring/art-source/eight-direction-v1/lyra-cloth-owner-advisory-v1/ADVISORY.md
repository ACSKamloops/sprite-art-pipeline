# Lyra source cloth boundary advisory

Read-only material advice; no art edits, generated pixels, scores, proposed animation or complete boot certification. The eight source PNGs were copied byte-exact from `emberwake-lyra-se03-polish-v1/candidate`. All coordinates below are zero-based native 128px `(x,y)`; ranges include both endpoints. The sparse marks are diagnostic witnesses, **not a complete mask**. Dark shared outlines cannot all be assigned a material from RGB alone.

The rejected trial has two different faults. Its neutral-RGB selection includes visible brown leather/cuff pixels, and its flat terminal rows lie below diagonal cloth cuffs. Correct these before concluding that every hole requires new crotch paint.

## 02 tucked screen-left cuff

Last unequivocal charcoal by column: `54:87, 55:88, 56:89, 57:89, 58:89, 59:89, 60:89, 61:89, 62:88, 63:87` (`x:last y`). Preserve the darker lip separately: `(57..60,90)`, `(62,89)`, `(63,88)` (alpha245). These dark edge pixels need not move with core cloth. `(64,86..87)` is also a dark side boundary, not unequivocal core.

The other side of this sloping cuff is visibly warm: `(52,87)=[31,16,11,255]`, `(53,87)=[31,21,15,255]`, `(54,88)=[16,12,9,255]`, `(55,89)=[19,15,12,255]`, `(56,90)=[29,14,8,255]`. Core ends by row89; the lower dark lip reaches90, and row91 under the cuff is brown leather (for example `(54,91)=[88,44,24,255]`). A shared y93 terminal is below this attachment. Its problem is material/ownership, not just the amount of stretch.

The source screen-right extended cloth continues farther down: its central last neutral edge is around y94–95, before an unequivocally brown y96. This is a different cuff; do not reuse the tucked cuff endpoint.

## 06 raised screen-right cuff

Conservative last unequivocal charcoal by column: `72:84, 73:85, 74:85, 75:86, 76:86, 77:86, 78:86, 79:86, 80:85, 81:85, 82:84`. Dark transitions: `(71,83..84)`, `(72,85)`, `(73..74,86)`, `(76..79,87)`, `(80..81,86)`, `(82,85)`, `(83,84)`. In particular `(74,86)=[23,22,26,255]` is a dark transition rather than a high-confidence core texel. Keep these fixed if the current operation only stretches core charcoal.

Row88 is visibly brown across x71–79; for example `(73,88)=[70,33,16,255]`, `(77,88)=[122,61,32,255]`. `(66,85)=[17,7,2,255]`, `(65,86)=[20,8,3,255]`, `(64,89)=[10,4,3,255]` are warm leather/outline exclusions. A y90 anchor is at least three rows below the raised cuff's darkest bottom lip, and farther below its oblique sides.

The source screen-left support cloth is longer: its central dark lip reaches y94, with unequivocal brown below at y95. It needs its own oblique boundary; the raised-right cutoff must not be copied across it.

## Missing paint versus incorrect owner

I checked the actual frozen layer RGBA at the producer's reported new holes; this does not rely on the semantic upstream labels.

* **02: all 11 reported holes are lower paint that was already visible.** None has positive source-body RGBA. Four are warm cuff-boundary witnesses; the others are visible charcoal or dark boundary paint. Their disappearance does not demonstrate hidden crotch paint. The owner carve, endpoint constraint and exact mapping need correction first.
* **06: 9 of 22 holes are actual coat disocclusion.** `(66..70,82)` and `(67..70,83)` were opaque green/gold body pixels. After the body is translated up two rows, body and all retained lower/cloth layers are transparent there. This is genuinely uncovered area in that trial. The composite does not contain a visible charcoal donor underneath those coat pixels. Filling it would be declared new join/underpaint, or the occlusion/body motion must change; it is not recovered hidden source anatomy.
* **06: the other 13 holes were already-visible lower paint.** They include existing charcoal/outline and brown `(66,85)`, `(65,86)`, `(64,89)`. They are owner/raster coverage failures, separate from the nine coat-disocclusion pixels. Inspect `(62,88)=[43,42,42,255]` and `(63,88)=[11,10,11,245]` as real visible edge witnesses; neither is missing source anatomy.

`BOUNDARY-WITNESSES.json` contains literal RGBA for all marked endpoints and the same-location layer accounting for all 33 reported holes. The source-coordinate grids and source-versus-rejected proofs expose the exact rows. Green marks indicate conservative core endpoints; magenta marks are fixed dark boundary witnesses; orange marks are warm exclusions; red marks show the nine coat-owned exposure pixels. Dark outlines are deliberately qualified rather than assigned wholesale to trousers or boots. No conclusion is made about the ambiguous gray side flap in 00/01.

Recommendation to the producer: retain per-column conservative core owners, keep the actual cuff/outline seam fixed as a separate visible surface, and declare any bounded new connection at the nine exposed coat pixels. A positive-layer identity check alone cannot certify the whole boot when the carve has already removed brown paint from that layer.
