# Same-job paired color recovery

The retained captures contain paired arrays, but **none exposes a changed animation before/after color sequence**. Twenty main/quantized frame pairs are identical PNG bytes and identical full RGBA. The one changed pair is a single Pro Flash conversion image. It constrains generic palette reduction, not animation de-flicker. No private de-flicker implementation was recovered and no provider, generation, credential or network operation was performed.

[PAIRED-COLOR-LEDGER.json](PAIRED-COLOR-LEDGER.json) binds source files, JSON Pointers, accepted job IDs, request hashes, exact extracted PNG hashes, observations and finite negative bounds. Full inventory and decoded PNGs are private under `/home/astra/artifacts/pixellab-paired-color-recovery-20261014/source-pinned-v3`. Source research and the canonical workbench were read only. The helper here is a new measurement utility, not a recovered PixelLab processing algorithm.

## What the same-job pairs actually expose

| Retained job | Response fields | Paired frames | Measured result |
|---|---|---:|---|
| edit-animation-pro | images / quantized_images | 4 | PNG bytes and full RGBA exact; visible RGB union43 |
| interpolation-pro-corrected | images / quantized_images | 2 | Exact; union51 |
| outfit-transfer-pro-corrected | images / quantized_images | 3 | Exact; union52 |
| r2-character-template-walk | images / quantized_images | 6 | Exact; union77; returned generation_model=`template` |
| feature-ui-panel | images / quantized_images | 4 | Exact; union51 |
| feature-connected-terrain | image / quantized_image | 1 | Exact;20colors; captured while status was processing |
| prep-pixelart-pro-flash | original_images / images | 1 | Changed RGB, unchanged alpha;127→29visible RGB colors |

Each canonical response's job ID matches the acceptance response for its request. Repeated polls and HAR copies were deduplicated by exact paired PNG hashes:18retained representations yield7distinct paired results. Canonical originals are the individual `*-response.json` files, not derived editor exports. Endpoint/request/acceptance bindings remain in the ledger. Template animation is not labeled MiniMax, and terrain/UI are not animation evidence.

The nominal animation pairs are not merely visually similar: even hidden RGB and PNG encoding bytes are identical. No per-pixel mapping conflict or sequence color change can be exposed by comparing each identical pair. The equal arrays also make identity affine fits and nearest-output-palette matches trivial; those fits are **not evidence of an identity de-flicker algorithm**.

The response metadata nevertheless reports larger `original_image_n_colors` values: edit115→43, interpolation112→51, outfit113→52, template285→77, UI287→51 and terrain201→20. The measured visible unions of **both** exposed variants agree with the smaller counts. Therefore `original_image_n_colors` is not a measurement of the exposed nominal main array in these packets. A hidden earlier image stage, server alias/reuse, or some other response-construction behavior could explain this; none is established. The larger count cannot reconstruct the missing colors or prove that a visible main/quantized difference was captured.

The historical capture utility's scrub/serialize/export functions were inspected and byte-anchored separately. They contain no variant swap or quantizer. Its PNG export deduplicates hashes; this pass decoded original response descriptors directly, preserving their exact source JSON Pointers. Historical HAR response text is scrubbed/reserialized structured data, not an original HTTP-byte archive. Matching HAR copies add provenance consistency, not independent observations.

## The changed still-image pair

The same `/image-to-pixelart-pro-flash` job returns one server-named `original_images` entry and one processed `images` entry, both126×124, fully opaque. These labels do not make the first array the uploaded source or a native neural intermediate. Exact source descriptors and hashes bind which arrays were compared.

Of15,624co-located pixels,3,945change RGB. Alpha is exact at every pixel. Visible distinct RGB colors reduce127→29. Every observed `original_images` RGB maps consistently to one processed RGB within this image; no spatially varying target for an identical source RGB was observed.

Using the **already observed**29-color output palette, the fitted weighted Oklab nearest-palette rule `0.25*dL²+da²+db²` predicts every returned RGB pixel. Unweighted Oklab differs at81pixels and sRGB Euclidean distance at50. This is an after-the-fact candidate comparison with an output-derived palette, not a supplied-palette prediction, recovery of palette clustering, proof of unique parameters, or proof this service shares the public reducer's internals. It provides another retained behavior consistent with that candidate mapping, with no new call.

A descriptive least-squares RGB3×3+bias fit has channel RMSE approximately4.00/3.58/4.34, maximum channel residual50.43, and74.48%exact pixel predictions after rounding/clipping. It does not replay the returned image. These numbers are not a recovered color-correction transform. There is only one frame, so they constrain neither a temporal rule nor foreground drift relative to frame0.

## Search bounds and unresolved animation processing

Read first: the existing animation-client closure, round4 animation geometry report, and `docs/recovery-depth-20261014/PIXEL-CONVERSION-RECOVERY.md`. They distinguish wrapper preference/placement from private processing and already disclose the main/quantized retention policies. This pass adds decoded same-job measurements rather than repeating those policies as new algorithms.

The final scan inspected1,367JSON/HAR/JSONL files,44,210,463bytes, under four explicit roots: retained `runtime/probes`, `runtime/captures`, `depth-round2`, and `/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014`. Name filters excluded credential/cookie/token/secret/profile/auth/balance paths; OpenAPI and noncapture formats were excluded. Embedded JSON in HAR/event text was inspected without exposing headers, credentials or base64 in tool output. No parse/decode qualification occurred. An additional literal-token scan of `evidence/rea-paid-sanitized.json` found zero `quantized_images`, `original_images` and `drift_threshold` tokens; it is only a bounded literal scan, not semantic absence proof. Full source inventory hashes remain private.

The ledger separately lists20retained animation-related request directories and every image-array packet they expose. The inspected direct MiniMax and V3 jobs contain main images without a paired pre/post array; no `drift_threshold` override was found in the selected parsed capture dictionaries. The newer H3 matched-comparison artifact likewise has no retained original/quantized pair. These are bounded negatives over these captures, not proof that other clients, jobs, private files or the server never expose intermediates. Balance directories, browser profiles, credential stores, private unsanitized captures, other arbitrary repositories, sessions and unseen server code were not searched.

Public declarations about foreground de-flicker, first-frame comparison, threshold zero and omitted defaults remain declarations. These retained pairs do not determine the foreground mask, drift metric/color space, default threshold, correction function/strength, temporal window, ordering relative to palette reduction or MiniMax checkpoint. Comparing temporal palette/mean/variance across moving frames would not recover the missing preprocessed sequence; for the exposed equal pairs any such before/after statistic is necessarily unchanged.

## Next discriminating evidence

1. Seek an authorized same-job capture with explicitly named **different** pre-correction and post-correction PNG arrays, their stage order and index correspondence, plus the exact effective threshold. A larger reported pre-stage color count without its pixels is insufficient.
2. A threshold0versus high-threshold experiment would need the **same bound pre-correction frame bytes**. Regenerating separate animations with equal seed does not itself establish identical native input pixels; output differences could come from generation, segmentation or sampling. Do not attribute them uniquely to de-flicker.
3. For standalone palette reduction, this still pair supplies127observed RGB→RGB associations and an output palette for candidate discrimination. Keep automatic palette derivation and animation use separate. Reordered/tied palettes, nonopaque entries and unseen inputs would require separately authorized probes; none was run here.

Reproduce only the offline measurement into a fresh output directory:

```sh
python scripts/recovery_depth/analyze_paired_color.py --output /new/private/output-directory
```

The helper refuses an existing output directory and imports no live-provider code. `source-pinned-v3` is the complete final receipt; initial measurements and an interrupted serialization attempt remain private and are not counted as additional evidence. The committed ledger pins the successful script/receipt. This work supplies observations and narrower unknowns, not a new PixelLab algorithm, accepted artwork or a whole-pipeline certificate.
