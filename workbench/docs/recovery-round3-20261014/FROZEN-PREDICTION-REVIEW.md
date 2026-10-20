# Frozen low-K palette predictions: independent offline audit

The first four fresh calls match the frozen **ignore-alpha construction** predictions exactly: **four palette orders,8192 RGBA entries, zero mismatches**. Saved predicted palette/frame PNG bytes also equal the returned PNG bytes. The predictor did not receive an observed service palette. This validates these separated low-K predictions, not general palette construction or private code identity.

[Audit receipt](FROZEN-PREDICTION-REVIEW.json) SHA `543c5c2aa44fbf0da9d459d0cd4106aa0ac7cde0ae64fbe553658ce35bf32711`; full local audit, archived source and independent binding receipt are under `/home/astra/artifacts/pixellab-palette-round3-20261014/fresh-prediction-audit`. [Executable audit](../../scripts/recovery_round3/audit_frozen_palette_predictions.py) made no network, credential or provider calls. The canonical checkout/captures were read only.

## Freeze and replay checks

* Phase SHA `612055f7f53bf6eadeb71b24f9d4573f8d1bccf9707f2027d1dd293c16cddcaf` pins subplan `c0e9e5cea611a96c50e8e7843d70e3c950f86f7efaea1130db5a3fdb8ab2d2eb` and all six competing prediction receipts.
* Archived commit `7f17ca694c659ef0aa69e64ae9dec0ac4b2b7e13` contains the exact current predictor SHA `15bfb938f4050a3a35362cebc9633ec4288ae1b1a08cbf85216bdf3510d93807` and inferred mapper SHA `6272a72903dd4a7d330e7eeb5c8e7df321cbc84c6ba9f9485404a640857ba742`. Source is explicitly authored hypothesis, not original PixelLab code. The audit copied those archived bytes into its own artifact scope before import.
* Every frozen input PNG, request/wire and prediction receipt/output hash matches. Unchanged archived code independently replays all six frozen palettes and RGBA outputs; float centers agree within1e−14. It uses source images and requested count only. Returned palettes are used exclusively for comparison.
* The final capture verifier passes under Python `-O`: **4 cases,12 returned PNGs including strips,0.4 response-reported generations**, no binding failures. It binds producer request/response/full SHA, exact returned PNGs and complete REA records.
* The recorded phase preparation time `05:16:52.894593Z` precedes all producer starts (`05:16:59.321427Z` through `05:17:13.813231Z`). Local source/plan pins and timestamps support the retained pre-response account; they are not third-party notarization or independent observation of network execution.

## Outcomes and counter-hypotheses

| Case | Requested colors | Ignore-alpha palette/order and output |
|---|---:|---|
| Opaque A,B | 2 | Exact: `[29,48,74]`, `[217,172,83]` |
| Same RGB, correlated source alpha | 2 | Same exact palette; source alpha preserved |
| Opaque C,D | 3 | Exact: `[39,146,82]`, `[28,47,72]`, `[217,172,83]` |
| Opaque B,A | 2 | Same exact palette; frame outputs permute exactly |

In the correlated-alpha case, **420 and300 alpha-zero source pixels** respectively have their hidden RGB changed to palette RGB while retaining alpha0. The full source alpha arrays, including64/128/255, are preserved. Two competing **pre-frozen** construction policies—excluding alpha0 or weighting counts by alpha—both predict different palettes and fail at1024 RGBA entries in each frame. This distinguishes these three policies on this correlated fixture; it does not establish every possible alpha rule.

The A,B versus B,A palette PNG bytes are equal and both corresponding output PNGs are equal after permutation. Palette order agrees with the predictor's greatest cluster-mass first policy here; these fixtures do not test equal-mass presentation ties.

REA IDs: AB `ev_eff91e032583e29fae7eb0f5761bd44d372629aa2f6cd745c2aa773e5148d61c`; alpha `ev_525c53ccf5e601bfd7892d9d83e778b000ef43aebe5221076273a0fa518d7c26`; CD `ev_f816d6face7e22a4c5cd0cb026e49f05ccfed11bd0167e19528ac99163e1798c`; BA `ev_995212948fefb6d54d488a5d730668ade8da17ba60c98d7f50819f31b74d153c`. They decode retained producer HARs and do not attest vendor internals or independently witness the calls.

## Remaining boundary

These deliberately separated2/3-color families make centroid transformation, frequency weighting and alpha hypotheses discriminating while making initialization relatively easy. They do not identify service initialization or general convergence. The four calls reuse RGB between opaque/alpha and AB/BA;8192 entries are not8192 independent colors. The three alpha policies are competing frozen alternatives, not three separate held-out successes. No automatic palette-size detection, dither, nonopaque target palette or animation-internal behavior is validated.

The [older32-color counterexample](PALETTE-INFERENCE.md) remains: the closest bounded independent candidate matches29/32 colors and misses768/8192 mapped entries. No exact general constructor is supplied. Root's later adaptive hidden-black follow-up is a separate fifth call and is not included in this four-call receipt or its pre-response scope.
