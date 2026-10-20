Lyra frame03 spur cleanup: frozen nonregression review

**Prefer B for this cleanup.** The removed tab reads as a stray upper-leg-edge ledge below the glove. B keeps the glove/cuff mass, tunic/hip shape and boot intact. No hand, cloth or boot damage was found. No numeric motion scores were assigned.

Only03 changes in each view:17 pixels per view, comprising six opaque pixels removed, ten faint fringe pixels removed and one opaque edge pixel recolored. The other14 animation cels are byte-identical acrossA/B.

Coordinates are zero-based on the128px canvas:

| View | Opaque tab removed | Faint fringe removed | Edge recolor retained |
|---|---|---|---|
| SE03 | x44–49,y86 | x45–49,y87–88 | (50,86) |
| SW03 | x79–84,y86 | x79–83,y87–88 | (78,86) |

The actual brown glove and highlighted wrist/cuff above this region remain exact. InA03 the ledge projects laterally from the upper-leg edge beneath a transparent interval under the main glove. Its one-cel horizontal shape and repeated faint fringe are poorly supported by02/04. B removes that accent without truncating the rounded palm, cutting the cloth mass or shaving the boot. This is a raster-based anatomical reading; the nominated images do not provide semantic layer proof.

All32 animation cels and all32 cyclic pairs were inspected, including07→00 for both variants in both views, at native128px, nearest2× and nearest84px on light/dark backgrounds. Nineteen bounded diagnostic PNGs include local6× and alpha comparisons. All30 cardinal context images and appearance were used for identity/facing only. All63 input hashes match INPUTS.json before review and remain exact afterward; the manifest is unchanged.

The improvement is clearest at2× on light ground and subtle at84px. Frame03 lasts56.25ms within the450ms loop. Only static cels, chronology and pair sheets were observed: normal-speed visibility, flicker, engine presentation and world contacts were not tested. This verdict accepts a local cleanup and makes no new motion-quality claim.

No additional repair in this region is indicated. Source access stayed within the nominated input; no producer files, mappings, prior/other reports, skills or prior character grades informed the verdict. See exact-differences.json for every edited RGBA value, report.json for32 pair findings and input-hashes-before/after.json for preservation proof. This report and output ledger are frozen once.
