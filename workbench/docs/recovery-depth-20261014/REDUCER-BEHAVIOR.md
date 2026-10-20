# Fixed-palette behavior: empirical recovery and held-out replay

The public `/v2/reduce-colors` endpoint was tested with synthetic colors rather
than new art. A local **inferred** nondithered rule reproduces all retained
calibration/holdout RGBA pixels. This recovers a useful observable behavior,
without identifying a private implementation or establishing its use inside
PixMiniMax.

## Controlled phases

1. Fixed black/white palette: a complete16³ RGB cube plus repeated8-bit gray
   ramps; second image has the same RGB with alpha0,64,128,255. Tested no
   dithering, an identical repeat and ordered2×2 strength5.
2. The same inputs: fixed six-color palette without dithering; black/white with
   ordered2×2 strength0 and10. These distinguish color metric and dither paths.
3. Before submitting a fresh random source and nine off-axis palette colors,
   `PLAN.json` freezes the prediction `0.25*dL²+da²+db²` in Oklab, exact alpha
   preservation and hidden-RGB quantization. This phase contains one POST.

Total: seven POSTs, fourteen returned image PNGs,0.7 reported generations.
Every case has an actual producer HAR and full REA import with its own SHA-256.
The [offline analysis](evidence/REDUCER-ANALYSIS.json) rechecks frozen request,
compact submitted body, REA/HAR record, saved result and extracted PNG bindings.
The producer capture is offline evidence, not an independent network attestation
or access to server source. No native H3/model invocation occurred here.

## Results and a rejected hypothesis

The two-color calibration agrees with unweighted Oklab for all4,096 cube points;
nearest raw sRGB disagrees1,143 times and a CIELAB lightness midpoint disagrees578
times. That is insufficient to distinguish Oklab channel weights, because both
palette colors are achromatic.

The six-color calibration rejects plain Euclidean Oklab:372 of4,096 cube entries
disagree. Reducing the squared lightness contribution to0.25 yields zero
disagreements. The independent review reproduces this using a separate scalar
implementation rather than importing the parent's mapper.

The predeclared holdout then agrees exactly on8,192 RGBA entries:4,096 RGB samples
rendered once opaque and once with mixed alpha. It contains4,094 distinct RGB
colors,4,093 absent from the calibration set. All nine target colors are distinct
from the calibration palette. These inputs validate the fitted representative
against an additional finite case, not all possible palettes or images.

Across all no-dither/zero-strength cases, including repeats, the rule matches
73,728 RGBA entries. Repeat PNG bytes are identical, and strength-zero ordered
PNG bytes are identical to `none`. Alpha is exact in all fourteen returned PNGs.
Hidden RGB is quantized even at alpha0; it is not universally cleared as it is
in the separate recovered Godot serialization function.

The independent evidence admits an approximate lightness-weight interval
`[0.249909225276, 0.250040381755]` with chroma weights fixed at1. Therefore0.25
is not uniquely identified. No exact nearest-distance ties occur in these
fixtures. The local first-entry tie policy and nonopaque palette entries are not
validated against the service. See [independent review](REDUCER-ADVERSARIAL-REVIEW.md).

The Oklab conversion uses the author's [published matrices](https://bottosson.github.io/posts/oklab/).
The quarter-lightness weighting is an inference from these service responses,
not an attribution to that article or a recovered PixelLab source function.
Fresh shipped client palette clustering uses a different, unweighted Oklab
distance; its existence does not identify the private reducer implementation.

## Deliberately unresolved

Positive ordered dithering differs from the nondithered replay. The bounded
offline search retained378 parameterized candidates, including RGB nearest,
Pillow fixed-palette mapping and the verified original GIF cache. Best tested
candidate still differs538/32,768 RGBA entries across strengths5/10. It is not
installed as an implementation. [Dither findings](DITHER-CHARACTERIZATION.md).

Automatic/shared palette construction, palette-size detection, palette tie
behavior, backend changes and use of this stage in animation remain unproved.
The observed rule supplies a local controlled fixed-palette channel; it does
not reproduce segmentation, learned image-to-pixel conversion or de-flicker.
