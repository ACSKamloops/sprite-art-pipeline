# Palette inference: bounded initialization and latent assignments

Two authored deterministic Oklab Lloyd candidates **independently construct the exact palettes and final RGB mappings for all three retained4-color calls**. No tested candidate exactly constructs the32-color palette. The closest yields29/32 palette RGBs and misses768/8192 final mapped RGB entries. This is offline inference on already observed fixtures, not recovered source or held-out validation.

The eight previously unexplained32-color means can all be reconciled with **float-center assignments from that29/32 candidate**. This establishes a concrete reason that computing means from assignments to rounded output colors need not expose construction-time clusters. Three pale-family centers remain unexplained; the candidate is not an exact service implementation.

## Fixed bounded methods

[Method plan](METHOD-PLAN.json), [summary results](PALETTE-INFERENCE.json) and [eight-center explanation](FLOAT-ASSIGNMENTS.json) are committed. Complete iterations, float centers, final palette RGBs, unchanged inferred-mapper snapshot and script copies are in `/home/astra/artifacts/pixellab-palette-round3-20261014`. The complete `RESULTS.json` is SHA `0b69f272898a6f733d2ed0fd1dd900ea806bad00827f073fe3936def8bbee8b9`; the summary pins all script/plan/prior-receipt hashes. All four old request/response/source/output/palette identities are checked against the earlier bound receipt before analysis. No old evidence/script was changed and no provider/credential/network call was made.

The plan is written before candidate execution, while the service outputs are already known. There are exactly **three initializers × two centroid spaces × four retained cases =24 runs**, plus eight explicitly output-conditioned refinements. AB4/CC4 have identical histograms and are not independent observations.

* **Frequency/farthest:** start at the highest-frequency input RGB; add the farthest point by minimum weighted squared distance.
* **Lightness/weighted-farthest:** start at minimum/maximum Oklab L; fill using maximum minimum-distance-squared × pixel frequency.
* **Histogram topK:** start at the K most frequent source RGBs.

All use fixed Oklab assignment distance `.25*dL²+da²+db²`, exact pixel counts, lexicographic RGB tie order, and first-center distance ties. Centroid updates are either frequency-weighted **Oklab means** or frequency-weighted **sRGB means converted back to Oklab**. Presentation uses the published inverse matrices/sRGB transfer, clipping and `numpy.rint`. Empty clusters retain their center; there are no random seeds, restarts, reseeding, fitted weights or fine grids. Each run stops at unchanged assignments or20 updates. All independent runs converged within2–6 updates; output-conditioned runs took1–3. All Oklab-mean objectives were nonincreasing.

## Palette construction results

| Initializer / centroid space | AB4 | CC4 | AA4 | AB32 |
|---|---|---|---|---|
| Frequency/farthest, Oklab | Exact | Exact | Exact | 15/32 RGBs;3728 mapped mismatches |
| Lightness/weighted-farthest, Oklab | Exact | Exact | Exact | **29/32 RGBs;768 mapped mismatches** |
| Histogram topK, Oklab | 1/4 RGBs | 1/4 RGBs | 1/4 RGBs | 3/32 RGBs;7432 mapped mismatches |
| Frequency/farthest, sRGB | 1/4 RGBs | 1/4 RGBs | 1/4 RGBs | 12/32 RGBs;4960 mapped mismatches |
| Lightness/weighted-farthest, sRGB | 1/4 RGBs | 1/4 RGBs | 1/4 RGBs | 23/32 RGBs;2592 mapped mismatches |
| Histogram topK, sRGB | 1/4 RGBs | 1/4 RGBs | 1/4 RGBs | 3/32 RGBs;7432 mapped mismatches |

“Exact” means equal palette RGB set, ignoring the service's frequency order, and zero final RGB-mapper disagreements on8192 pixel entries per case. It does not predict the palette strip's order or PNG encoding. Final mapping here independently assigns source RGB to the **candidate's rounded palette**, with the fixed quarter-lightness metric. There are no source alpha variations in these old cases. Histogram-topK/sRGB has6912/6912/6144 mismatches on AB4/CC4/AA4, as do the other failed4-color families.

The closest32 candidate's missing service colors are `[222,216,192]`, `[223,220,188]`, `[224,210,192]`; it instead constructs `[222,220,189]`, `[223,216,191]`, `[224,210,193]`. No per-family splice or special-case correction was made.

## What float-versus-rounded assignments explain

Starting a fresh Lloyd run at the **observed rounded service32 palette** is explicitly output-conditioned. Oklab refinement converges after3 updates to25/32 exact colors and1048 final mapper mismatches; sRGB refinement converges after2 to21/32 and2552 mismatches. Step0's exact32/32 is trivial because it starts with the answer. The first Oklab mean update gives the previously measured24/32; ordinary iterative refinement does not restore the full service palette.

The already tested lightness/weighted-farthest Oklab candidate provides a more specific partial explanation. Its32 float centers converge to a weighted Lloyd fixed point. Assigning pixels to those floats versus its rounded RGB centers changes152 pixel entries. **Every one of the eight service centers whose rounded-output-assignment mean previously missed is present exactly in this candidate**. For each, recomputing its Oklab mean from the candidate's latent float assignments agrees with its stored float center within1e−14 and rounds to the service RGB. The explanation ledger records all original/latent means and gained/lost pixel counts.

This is a counterexample to interpreting the old eight residuals as proof that the construction cannot use Oklab means. It does not prove those candidate assignments are the service's actual latent assignments. The selected candidate still fails three other centers; output-conditioned analysis and choosing the closest member after seeing results cannot substitute for a fresh prediction.

## Boundary and reproduction

This supports a bounded Oklab-centroid hypothesis and supplies explicit initialization counterexamples. It does not identify private initialization, sampling, convergence thresholds, seeds, tie rules, automatic palette-size detection, alpha weighting, dithering or use inside PixMiniMax. New separated low-K predictions are prepared and owned by root separately; this worker did not create duplicate fixtures or submit requests. Their evidence must retain its own pre-response freeze and limits.

```sh
python scripts/recovery_round3/infer_palette_construction.py \
  /home/astra/artifacts/pixellab-palette-construction-20261014 \
  --output /absolute/new/round3-output \
  --mapper /home/astra/artifacts/pixellab-palette-construction-20261014/analysis-20261014/inferred-fixed-palette-mapper.source.py
python scripts/recovery_round3/explain_float_assignment.py \
  /home/astra/artifacts/pixellab-palette-construction-20261014 /absolute/new/round3-output \
  --mapper /absolute/new/round3-output/inferred_mapper.source.py
```

Only completed JSON receipts are evidence. A partial explanation serialization attempt is preserved as `.partial.json` and is not counted as another result.
