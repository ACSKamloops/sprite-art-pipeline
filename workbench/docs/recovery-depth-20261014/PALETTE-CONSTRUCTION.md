# Frozen shared-palette construction probes

Four small public-reducer requests are prepared, with **zero submissions and zero actual responses**. The current shipped palette-image clustering helper also executes unchanged offline. Its outputs are frozen as a comparison candidate; they are not attributed to the server.

Artifact root: `/home/astra/artifacts/pixellab-palette-construction-20261014`. [Frozen plan](PALETTE-CONSTRUCTION-PLAN.json), [fixture specification](PALETTE-CONSTRUCTION-FIXTURES.json), [preparation/source seals](PALETTE-CONSTRUCTION-MANIFEST.json), [original-code outputs](PALETTE-CONSTRUCTION-ORIGINAL-REPLAY.json). Earlier retained fixed-palette experiments characterize mapping onto a supplied palette, not how a palette is constructed. These new probes hold palette size fixed to examine construction/shared-frame effects. Automatic palette-size detection remains untested.

## Contract and exact input design

The retained public OpenAPI SHA `8cb24ecdd26e9fe48639dc789e44f32b3c78c29e8da8c3121f23ab360ade5dad` documents `POST https://api.pixellab.ai/v2/reduce-colors`: same-size frames share one palette; `num_colors` is2–256; it is mutually exclusive with `palette_image`; omitting both asks for automatic size detection. A completed response has `images`, `palette` and `n_colors`; the palette is documented as a1px-high strip ordered by frequency. The exact projected schemas/route are retained in artifact `PUBLIC-CONTRACT.json`. No fresh API request was made here.

Each source PNG is **64×64 RGBA, fully opaque, 512 distinct RGB colors**. Eight separated color families have64 colors each, formed by the fixed Cartesian offsets `[-7,-3,1,5]` around the eight recorded RGB bases. Every color occurs in every frame. Per-color occurrence counts for each family are:

| Frame | Family counts, in fixture-base order |
|---|---|
| A | 16,8,12,8,8,4,4,4 |
| B | 4,4,4,4,8,12,12,16 |
| C | 10,6,8,6,8,8,8,10 |

All sum to4096 pixels. A fixed odd modular permutation distributes the repeated colors spatially; no RNG is involved. **`hist(A)+hist(B) == 2*hist(C)` exactly**, including alpha. Source PNG bytes, raw RGBA bytes and hashes are retained. Pillow independently decoded all three PNGs to their pinned raw RGBA hashes. Fixtures are supplied diagnostics, not generated art.

## Four predeclared cases

| Variant directory | Frames | `num_colors` | Discriminating question |
|---|---|---:|---|
| `joint-ab-4` | A,B | 4 | Baseline shared construction under two differing frequency distributions |
| `histogram-cc-4` | C,C | 4 | Same combined color histogram; different pixel order/frame partition |
| `weighted-aa-4` | A,A | 4 | Does replacing B change A's output or the shared palette? |
| `joint-ab-32` | A,B | 32 | Does the palette RGB set match the unchanged shipped32-color helper? |

Each request contains exactly two `Base64Image` objects with `type:"base64"`, a `data:image/png;base64,` value and `format:"png"`. Each has `dithering:"none"` and `dithering_strength:5.0`; `palette_image` is absent. Each case contains8192 total source pixels, below the documented512×512 total budget. No default-auto case is included: this bounded plan prioritizes shared construction and an exact original-helper comparison over mixing palette-size estimation into the same observations.

`PLAN.json` retains the existing parent helper's `requests[{variant,request_sha256}]` convention and adds `frames`, `num_colors` and the exact compact submitted-body SHA. The frozen request is `<artifact-root>/<variant>/request.json`. The existing parent submission helper already expects two returned frames and writes `response.json`, `output-00.png`, `output-01.png`, `palette.png` and an actual producer HAR. It needs the four new variant names added to its whitelist; this preparation code contains no submission, credential or HTTP capability. Root owns any authorized submission, persistent attempt guard and producer capture. The predeclared maximum is four POSTs, with no automatic retries.

## Unchanged original helper, with a disclosed adapter

Original public `create-9c5cec3372075418.js`, SHA `819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d`, contains the single **palette-image import** helper. Its unchanged reducer UTF-8 range `[133221,134695)` has SHA `f98a7aa044b03fbd50096ae0c8af0c6d9ea01f6565b75bd8326f1bfb6bd8fa61`. The sRGB transfer and Oklab distance function pins are included in the replay receipt and [earlier color-method ledger](COLOR-METRIC-REVIEW.json).

The original path uses5-bit RGB bins, frequency-weighted representatives, standard Oklab with unweighted Euclidean distance, dark/light initial anchors, a hard maximum of32 centers and20 refinement iterations. It chooses representative **existing input colors** and sorts by Oklab lightness. Its second argument is unused. The replay asserts that passing0,4 or32 leaves the output identical; it does not patch the source to implement `num_colors:4`.

[The replay script](replay_palette_helper.cjs) verifies the complete asset SHA and each unchanged selected source-text SHA before executing the original expressions in an empty Node VM. Only lexical names needed by the original function are bound. There are no HTTP/Node/provider interfaces in that context. Original source slices are retained in artifact `original-helper/`.

The host builds an RGB occurrence Map from supplied RGBA, skipping zero alpha just as the visible canvas loop does. Combining frames into one Map is an **experimental host adapter**, not recovered shipped multi-frame behavior: the visible UI originally accepts one palette image. Single-frame A/B/C results are also retained. Every replay gives32 colors, repeats identically in fresh contexts and selects only existing input RGBs. The unchanged helper32 result is directly comparable in target size only to `joint-ab-32`; the4-color cases cannot match that32-color output by construction.

The original helper produces **different palette sets for AB and CC despite their equal combined histograms**; their intersection is15 of32 colors. Its first-seen bin representatives and tied decisions are order-sensitive. Consequently a server AB/CC difference alone cannot prove per-frame palette construction or disprove shared histogram use. Equality alone would not identify a unique algorithm either. AB versus AA differs offline as well. These limitations were recorded before any service submission.

## Reproduction and pending comparison

Prepare into an absent directory using the retained public asset/schema:

```bash
python docs/recovery-depth-20261014/prepare_palette_construction.py /absolute/new/root \
  --asset /home/astra/artifacts/pixellab-recovery-web-20261014/assets/2713c302f049-create-9c5cec3372075418.js \
  --schema docs/readiness/ANALYSIS-public/openapi.json
```

After root has real completed responses, [the offline comparison script](compare_palette_construction.py) can compare the predeclared palette RGB multisets, per-source-color output relations, alpha preservation and original32-helper palette set without parameter fitting:

```bash
python docs/recovery-depth-20261014/compare_palette_construction.py \
  /home/astra/artifacts/pixellab-palette-construction-20261014 \
  --output /absolute/new/PALETTE-CONSTRUCTION-COMPARISON.json
```

It checks frozen request/compact-body hashes, both frame counts, dimensions and saved-output/response equality. It uses response PNGs in original order. This is offline comparison, not independent HTTP attestation; the parent producer HAR/verification remains separate. Output creation is exclusive. Four offline test-double tests passed for comparison behavior, request tampering, missing frame rejection and saved-PNG mismatch. Test doubles exist only in temporary test directories and are never written into the prepared artifact root.

No claim is made about private server source, automatic size detection, dithering, nonopaque palette construction, learned segmentation, checkpoint identity, H3 conversion or animation consistency. Matching one candidate on this finite fixture would establish that observation only.
