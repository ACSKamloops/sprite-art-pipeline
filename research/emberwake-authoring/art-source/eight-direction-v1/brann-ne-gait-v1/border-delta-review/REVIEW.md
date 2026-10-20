# Brann border cleanup: frozen data and visual delta audit

**The NE cleanup is exact: 11 literal black alpha-1 border texels changed to transparent zero RGBA; all other RGBA values are unchanged.** No new visible character/anatomy/material/motion difference was found in the scoped still comparisons. This is a delta audit, not an art rerating, method change claim, or game/runtime acceptance.

The anonymous Rowan art review was frozen and its hashes delivered before this audit began. This report reads only the nominated `frames`, `cleaned-frames`, and `BORDER-CLEANUP.json`. No source or canonical files were written.

## Exact NE changes

All eight inputs and outputs are 128×128 RGBA. Independent array comparison agrees with the cleanup ledger's hashes and coordinate sets. Every listed change is **(0,0,0,1) → (0,0,0,0)**, and all are on the stage border.

| Cel | Changed NE coordinates (x,y) | Count |
|---|---|---:|
| 00 | (0,60), (127,67), (127,69) | 3 |
| 01 | (0,60), (127,67), (127,69) | 3 |
| 02 | (38,127) | 1 |
| 03 | none | 0 |
| 04 | (127,51) | 1 |
| 05 | (127,51) | 1 |
| 06 | (0,51) | 1 |
| 07 | (0,51) | 1 |
| **Total** | | **11** |

All **131,061 other texels** retain their complete RGBA, including hidden RGB under transparent alpha and every non-border texel. All **31,480 source texels with alpha ≥2** retain exact RGBA. The cleaned NE stage has **zero positive-alpha border texels**. Cel 03 is byte-identical as a PNG as well as decoded RGBA.

## Independent NE→NW derivation

Both raw and cleaned inputs were independently mapped using the declared rule **x_new = 128 − x_old**, with y unchanged, zero-initialized RGBA output and out-of-range destinations skipped. This differs from a conventional x_new = 127 − x_old flip.

| Cel | Raw→clean NW changed texels | Clean NW positive-alpha border texels |
|---|---:|---:|
| 00 | 2 | 0 |
| 01 | 2 | 0 |
| 02 | 1 | 0 |
| 03 | 0 | 0 |
| 04 | 1 | 0 |
| 05 | 1 | 0 |
| 06 | 0 | 3 |
| 07 | 0 | 3 |
| **Total** | **7** | **6** |

Four changed NE texels have x=0 and map to x=128, which is skipped in both derivations; the other seven changes survive. Independently derived raw/clean PNG and decoded-RGBA hashes are in DATA-AUDIT.json.

**The cleaned NW border is not empty.** In each of frames 06 and 07 it retains **(127,50), (127,51), (127,64)**, each exactly **(0,0,0,1)**. They originate at unchanged clean NE x=1. Thus the verified empty-border statement applies to NE; it does not extend to this NW derivation. This audit authorizes no additional removal and makes no production-baker claim.

## Visual delta

Inspected every raw/clean NE cel and every independently derived raw/clean NW cel at native **128 px** and nominal game-size **84 px**, nearest neighbor, against light `#e0e0d8`, dark `#1c2028` and muted game-like flat `#47523d` backgrounds. All six complete comparison sheets are in `evidence/`. Actual alpha was used, without amplification.

I perceived **no meaningful new character appearance, anatomy, material, silhouette or motion difference** attributable to the cleanup. The actor's drawn body pixels and their pose chronology are preserved. This does not rerate the original art, assert continuous motion perception, or grant previous acceptance to an untested derivative.

The light-background composites are mathematically different by at most **one 8-bit RGB code value** at sparse stage-edge display pixels: NE has 11 changed display pixels across all cels at both 128 and 84; NW has 7 at 128 and 1 at 84. The tested dark and game-like ordinary composites are byte-identical raw versus cleaned. These numbers depend on the specified nearest resampling and Pillow 8-bit alpha-compositing/rounding; they do not describe all possible renderers. COMPOSITE-DELTA.json records each frame/background/scale result.

Eighty-four pixels is a nominal review presentation, not a claim about this actor's actual engine scale. Game scenes, lighting, movement speed, animation timing, physical contact, controller feel, production baking and runtime acceptance were outside scope. Motion observations compare still chronology; no continuous playback was perceived. There is no new numerical art score and no changed-generation-method claim.

## Binding and reproducibility

`DATA-AUDIT.json` contains all 16 full source/output SHA-256 fingerprints, every changed coordinate/value, all remaining mirror border texels and both PNG/decoded-RGBA mirror fingerprints. `audit_delta.py` reproduces the data audit and ordinary contrast sheets in this report folder only. The source cleanup ledger SHA-256 is **f33a814ccbc479ee5401be0c160da7e42295bb67e1543bd21f117d4f77f67d70**. Source hashes were rechecked after visual inspection. `REVIEW.json` binds the data/composite evidence files; `SHA256SUMS` freezes the report and generated evidence. No game/runtime or provider files were changed.
