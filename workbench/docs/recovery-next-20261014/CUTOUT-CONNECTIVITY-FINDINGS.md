# Corrected cutout diagnostic: task modes differ; flood candidates fail

**Simple and Complex differ at exactly 89 pixels. None of the eight predeclared flood candidates reproduces either result exactly.** Simple removes the 64-pixel enclosed hole and 25-pixel diagonal-only patch; Complex preserves them. Both remove the true open channel and all three near-background strips, preserve retained visible RGB, and return binary alpha with zero RGB beneath alpha 0.

This updates, without replacing, [the initial findings](CUTOUT-FINDINGS.md): that first RGB design matched a small flood family exactly and produced identical mode outputs, but its supposed open channel was actually blocked by an arm. The [corrected plan](CUTOUT-CONNECTIVITY-PLAN.md) froze a new source with independently verified open, enclosed, diagonal-only and near-color regions. Results now falsify generalizing the initial exact-fitting family to this second design. They do not recover server source or identify the private PixMiniMax cutout route.

## Binding and measured coverage

Artifact root: `/home/astra/artifacts/pixellab-cutout-connectivity-20261014`.
Reviewed PLAN SHA256: `d23295b3af242446a5947db8ea626cbc8ad4ff432007bfbf10e2de7c80a692b3`.
Shared source PNG SHA256: `f8929723b17cdc39254ced84549817f4c36f9a71a7d66958f13bf27b1f566338`.

Parent submitted two requests, both HTTP 200 with reported usage 1.0 generations each, 2.0 total. Same 96×96 RGBA source, all source alpha 255, same seed 123, no text hint; only task enum differs. This reviewer made zero calls.

[Analysis wrapper](analyze_cutout_connectivity.py) checks the frozen PLAN/input/request/wire/source hashes and original offline-connectivity dependency hash. Before measuring, it requires the single actual HAR POST's body bytes to equal the frozen wire file; the request image to equal the retained source PNG; the HAR response and response.json image descriptors to decode to the exact `output-00.png` bytes; and HTTP 200/completed state. No auth/header fields are accessed or printed. [Machine findings](CUTOUT-CONNECTIVITY-FINDINGS.json) retain all hashes, regional measurements, eight candidate results per case, representative counterexamples and actual diagonal-chain pixels. Available REA receipt files are hashed for reference; this report's binding checks use the actual producer HAR/PNG records, not a claim of independent full REA review.

| Task | Returned PNG SHA256 | Removed pixels | Retained pixels | Retained visible RGB changes |
| --- | --- | --- | --- | --- |
| Simple | `5abfcec8e81c908a87cc859a13010e8cdc85f754fb837dc3be59f843eb865470` | 5977 | 3239 | 0 |
| Complex | `3792edcf774a75f390a109ae63b94f09e1a8d3452b577243e1353f20fc23500f` | 5888 | 3328 | 0 |

All 9216 pixels of each output were compared. Both output alpha sets are `{0,255}` and all removed pixels are zeroRGBA. No source transparency was present in this phase; foreground alpha restoration remains the separate measurement from the initial alpha-patch case.

## Regional outcomes

Counts below are alpha 0 pixels, with region sizes verified from source before submission.

| Source region | Pixels | Simple removed | Complex removed |
| --- | --- | --- | --- |
| True open channel inside body | 96 | 96 | 96 |
| Truly enclosed hole | 64 | 64 | 0 |
| Diagonal-only patch | 25 | 25 | 0 |
| Dark detail | 16 | 0 | 0 |
| Border strip, red distance 1 | 64 | 64 | 64 |
| Border strip, red distance 8 | 64 | 64 | 64 |
| Border strip, red distance 32 | 64 | 64 | 64 |

Exactly89 pixels differ between modes, all removed by Simple and retained by Complex: the 64-pixel hole and 25-pixel patch. There are no converse differences or changed retained RGB. This distinguishes task behavior on the corrected design, without assigning semantic correctness to either result.

The diagonal chain has 11 source-green pixels from `(20,48)` through `(30,58)`. Simple retains the first 10 and removes the endpoint within the 25-pixel patch. Complex retains all 11. That directly illustrates why either a pure global green lookup or the tested border-connectivity rule is incomplete here.

## Predeclared candidate test: no exact reconstruction

The frozen family is four/eight-neighbor border-connected pixels whose maximum RGB-channel distance from top-left source background is ≤0/1/8/32. Each candidate sets removed pixels to zeroRGBA and retained alpha 255. There is no tuned region mask, new fitted threshold, morphological patch, learned inference or production implementation.

| Connectivity | Threshold | Simple RGBA mismatches | Complex RGBA mismatches |
| --- | --- | --- | --- |
|4 | 0 |282 |193 |
|4 |1 |218 |129 |
|4 |8 |154 |65 |
|4 |32 |90 |1 |
|8 | 0 |266 |227 |
|8 |1 |202 | 163 |
|8 |8 |138 |99 |
|8 |32 |74 |35 |

Simple's closest candidate, eight-neighbor/32, incorrectly preserves the 64-pixel hole and incorrectly removes 10 diagonal-chain pixels: 74 full-RGBA discrepancies. Complex's closest candidate, four-neighbor/32, incorrectly removes just `(x=20,y=48)`: predicted `[0,0,0,0]`, actual `[30,160,80,255]`. One mismatch is still a failed exact hypothesis; it is not corrected with a special-case pixel.

All three near-green strips are removed, but that does not establish an actual 32 threshold or even a color-distance-based implementation. Thresholds between/above the samples, other RGB directions, other source geometry, repeatability and image-scale behavior remain untested. The source proof distinguishes candidate connectivity; it does not make the endpoint's semantic interpretation groundtruth.

No further calls were made. These standalone public endpoint outputs cannot establish the model, matte refinement, scheduler, segmentation architecture or implementation used internally when PixMiniMax requests transparency.

Reproduce offline:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python docs/recovery-next-20261014/analyze_cutout_connectivity.py
```
