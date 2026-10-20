# Shared-palette construction: four retained diagnostic responses

The service's constructed palettes reproduce all **32,768 returned RGBA entries** under the previously inferred nearest-palette rule `.25*dL²+da²+db²` in Oklab. The three4-color palettes also equal rounded, pixel-frequency-weighted Oklab means of their observed assigned source clusters. The exact construction algorithm remains unresolved: the32-color case matches that centroid calculation for24/32 centers, and the recovered original client helper and three standard Pillow candidates all fail exact palette equality.

[Machine findings](PALETTE-FINDINGS.json) bind the complete265,417-byte artifact receipt by SHA `ec5cb611f070081c975906870873e85796de0f3801bcb5bbb3ae98dd2ab46dba`. Full per-center means/residuals and candidate RGB palettes are in `/home/astra/artifacts/pixellab-palette-construction-20261014/analysis-20261014/PALETTE-FINDINGS.json`. [Frozen preparation](../recovery-depth-20261014/PALETTE-CONSTRUCTION.md) preceded submission; original oracle outputs remain unchanged. This analysis made **no API or credential calls**. Inputs are supplied diagnostics, not generated art.

## Verified capture and scope

Four retained calls have HTTP200, completed states and reported usage0.1 generations each, totaling0.4. For each call, analysis verifies every prepared-file hash, frozen plan/request/compact-wire hash, actual producer-HAR body bytes and SHA, full original response-body SHA before scrubbing, parsed-response identity, both saved image PNGs and palette PNG against their response base64 bytes, and both64×64 dimensions. Each REA record exactly matches its producer HAR and HAR SHA. REA authority remains `historical-reference`: these are retained producer captures, not independent server-source or live browser attestation.

| Case | REA evidence ID |
|---|---|
| AB,4 colors | `ev_a555173dd2dd7c795ba27e73f6f7371237029fc01396c7c2ccc69ab68014f0be` |
| CC,4 colors | `ev_489ca51cca91f8efae42c06cd0db43bf74402d7616369571f18a7bf3d9ddef6f` |
| AA,4 colors | `ev_b17d27ff969de6389bced3972b47fd14fc6d606a0978b6f866487e8e852d2701` |
| AB,32 colors | `ev_deb6b9d47f3bd0d659ce898f1989e32f3c8425a508601da9f8476757c50ac04d` |

All frames contain the same512 RGB values but differing frequencies. AB and CC have exactly the same combined histogram, with different frame partition and pixel order. They return identical4-color palette RGBs/order and identical per-source-color mappings. Replacing the second B frame with A changes the palette and the first A frame's mapping. These observations are consistent with joint histogram/frequency-sensitive construction. They do not identify initialization, determinism over repeated identical calls, tie handling or a unique implementation.

## Mapping onto the constructed palette

The unchanged existing **inferred** fixed-palette mapper was snapshotted into the analysis artifact, SHA `6272a72903dd4a7d330e7eeb5c8e7df321cbc84c6ba9f9485404a640857ba742`. It is an empirical local rule, not recovered server code. Every constructed palette is opaque, every source alpha is255 and all output alpha bytes are preserved.

| Case | RGBA entries | Quarter-lightness Oklab mismatches | Unweighted Oklab RGB mismatches |
|---|---:|---:|---:|
| AB4 | 8192 | 0 | 0 |
| CC4 | 8192 | 0 | 0 |
| AA4 | 8192 | 0 | 128 |
| AB32 | 8192 | 0 | 892 |

No exact nearest-distance ties occur. These are repeated finite colors and correlated frames, not32,768 independent RGB samples. They extend the earlier supplied-palette observations to palettes constructed by this service, without identifying the exact distance weight uniquely over all inputs. Alpha-sensitive palette construction is not tested.

## Original code and bounded candidate rejection

The original shipped single-image palette-import reducer is pinned in [the source ledger](../recovery-depth-20261014/COLOR-METRIC-REVIEW.json): current create asset SHA `819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d`, reducer UTF-8 `[133221,134695)`, SHA `f98a7aa044b03fbd50096ae0c8af0c6d9ea01f6565b75bd8326f1bfb6bd8fa61`. It hardcodes at most32 existing-input representatives, uses unweighted Oklab and sorts by lightness. Its unmodified AB32 result has **zero RGB intersection** with the returned32-color palette. Only one of the service's32 entries occurs in the source RGB set; the three4-color palettes contain no exact source RGBs. Thus the observed service palette is not that unchanged representative-selection helper on this adapter/fixture.

A single [post-hoc inferred variation](PALETTE-WEIGHTED-VARIANT.json) multiplies the helper's lightness difference by0.5 while retaining original initialization, iterations and existing-input representative selection. It also has zero RGB intersection with service AB32. This **altered code is not recovered source**, and the experiment does not search arbitrary weights or change the original oracle.

Pillow12.1.1 `MEDIANCUT`, `MAXCOVERAGE` and `FASTOCTREE` were each tested once per case, on a vertical concatenation of the two opaque source frames, requested color count4/32, `dither=NONE`, `kmeans=0`. **None matches the service palette RGB multiset**, ignoring order. Median-cut/max-coverage share zero palette entries in every case; octree shares1/4 in each4-color case and0/32 in AB32. Their direct RGB output mismatch counts are retained. This rejects those precise installed candidates/settings, not every variant of their algorithm families or library versions. No free parameter fitting was performed.

## Centroid consistency narrows the hypothesis

Clusters are defined by the **observed returned output RGB**, pooling input pixels from both frames. Six predetermined mean models were checked: pixel-frequency-weighted and unique-RGB-only means in sRGB, linear RGB and Oklab. Linear/Oklab means are converted back through the standard inverse transforms, clipped0–255, then either floored or rounded using `numpy.rint` (ties to even). Both rounding outputs and unrounded values are retained; no model parameters were fitted.

| Mean model, rounding=`rint` | AB4 | CC4 | AA4 | AB32 |
|---|---:|---:|---:|---:|
| Pixel-frequency sRGB | 1/4 | 1/4 | 1/4 | 23/32 |
| Pixel-frequency linear RGB | 1/4 | 1/4 | 1/4 | 20/32 |
| **Pixel-frequency Oklab** | **4/4** | **4/4** | **4/4** | **24/32** |
| Unique-RGB-only Oklab | 3/4 | 3/4 | 1/4 | 24/32 |

Flooring pixel-frequency Oklab means matches2/4,2/4,1/4 and7/32 respectively. The4-color results favor frequency-weighted Oklab centroids with nearest rounding over the checked alternatives on this fixture. The32-color result is not a fully explained fixed point: eight reconstructed centers differ by one integer level in one or two RGB channels. Rounded output colors need not expose the assignments or float centers used internally, and finite iteration, sampling or other approximations remain possible. No such explanation is established here.

The useful next recovery target is construction initialization/refinement/rounding or a source disclosure; simply substituting the shipped palette-import helper is contradicted by these outputs. Automatic palette-size detection, nonopaque inputs/palettes, ordered dithering, repeated-call determinism, native H3 conversion and whether animation uses this endpoint remain untested by these four calls.

Reproduce into a new artifact directory:

```bash
python docs/recovery-next-20261014/analyze_palette_findings.py \
  /home/astra/artifacts/pixellab-palette-construction-20261014 \
  --output-dir /absolute/new/palette-analysis \
  --mapper /home/astra/projects/pixellab-local-workbench/scripts/replay_pixellab_fixed_palette.py
```
