# Independent ordered-dither investigation

No exact public dither replay was found. A new, interpretable **relative-distance threshold candidate** improves the earlier two-case fit from538to426mismatches out of32,768pixel entries, but still fails the old and new captures. It is a posthoc authored hypothesis, not recovered PixelLab source, a heldout validation, or a production replacement.

The strongest new observations are simpler: tiny positive strength selects behavior matching raw sRGB nearest black/white rather than the nondithered Oklab result; removing the preceding RGB cube leaves the phase-aligned gray outputs unchanged; and the4×4request produces a stable four-row gray pattern. No additional service/model/credential calls were made by this reviewer. Root supplied the three new captures; only this isolated methods worktree was written.

## Capture bindings and scope

[DITHER-INDEPENDENT.json](DITHER-INDEPENDENT.json) retains all candidate results, actual source/output PNG hashes, source helper/shader pins and new capture bindings. The three followups are under `/home/astra/artifacts/pixellab-dither-followup-20261014`; PLAN SHA256 is `771d4dfccafe8ddbaf7728a64682f5744a90ef5b8c0efd97b3008afb6f3daad4`. For each case, the frozen request-file SHA, exact compact wire SHA, actual POST URL,200response JSON, extracted PNG bytes, REA subject/HAR SHA, record count and **complete normalized reported record equality** were checked. REA files are named `REA-EVIDENCE.json`:

| Case | REA ID |
|---|---|
| gray-context-2x2 | `ev_f7845bd880b4160e77fe916845c25ea04a2d2ed39c494acd822a55811c781fbd` |
| epsilon-2x2 | `ev_86e7eddb73f0a6943862bee2d7b25225284eeb7a9e443c9e6ed9e9f903b272ce` |
| cube-4x4 | `ev_4f39c6cc5a4a8f23e44ce5ae9bc26c5c82d00adaa3b212b6a242b5b16f070765` |

These REA records have `historical-reference` authority and bind locally retained HTTP records. They are not independent witnessing of live traffic or proof of server internals. No headers/base64/credentials are exposed in this report. Each request supplies the same opaque black/white palette. Each case has two8192-pixel images sharing RGB but varying alpha, so counts include repeated RGB observations and are not independent-color counts.

The prior source reading and378-combination grid are in root `docs/recovery-depth-20261014/DITHER-CHARACTERIZATION.md` and its executable harness. Their538best mismatch is revalidated here for the corresponding candidate. This pass adds structural diagnostics,222bounded cache/bin parameter combinations and105relative-distance parameter combinations. These are combination counts, not327distinct algorithms, and neither family claims exhaustive coverage.

## New controlled observations

**Epsilon branch.** At `dithering_strength=0.000001`, both returned RGB arrays exactly equal plain equal-weight sRGB nearest black/white: white iff `R+G+B>382.5`. There are zero mismatches over16,384pixel entries and alpha remains exact. The results differ from retained nondithered outputs at1,591pixels **per image**. Together with the previous zero-strength/nondithered equality, this supports a discontinuity between zero and tiny positive strength on these fixtures. It does not establish behavior at every positive strength or reveal an actual branch in source. The observation is consistent with a separate RGB-oriented dither path, not continuous tiny perturbation of the fitted nondithered Oklab mapper.

**Gray context.** New gray-only rows0–15 match the old cube-tail gray rows16–31 at all4096phase-aligned RGBA pixels per image. Row16is divisible by2, and input gray RGB and phase are identical. The new gray image repeats every two rows. No observed disagreement therefore requires the preceding cube, first-hit cache contamination from it, neighborhood diffusion or other context. This does not prove universal spatial independence or rule out stateful implementations that coincide on these inputs. Reordered images, arbitrary patches and changed widths/origins were not tested.

**Four-by-four phase.** Gray rows repeat every four rows. The first observed white x by `(y%4,x%4)` is:

```
136 129 134 127
124 133 122 131
132 125 138 127
120 129 122 131
```

Each number is a sampled position in its residue class, not a continuous scalar threshold. These coarse intervals are compatible with conventional Bayer rank ordering; they do not identify the exact normalization, offset, rounding or matching function. The conventional matrix tested is `[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]`.

## Why plain RGB noise still fails

On the old cases, identical `(RGB,x%2,y%2)` occurrences never give conflicting outputs, including cube/gray overlap. Same-parity gray rows repeat, each with one monotone black→white transition. That makes phase-local ordered candidates reasonable; it does not establish a private implementation.

But a raw equal-weight RGB-sum separator cannot explain mixed colors at a fixed phase. At strength5, phase `(y%2=0,x%2=1)`, source `[136,119,119]` at `(119,8)` is black, while `[204,119,51]` at `(115,12)` is white. Both sums are374 and channels are interior34–221. With equal channel perturbation up to15these examples do not clip, so raw RGB noise followed by exact nearest black/white would classify them equally. Cache/bin behavior, nonlinear distance-based ordering, adaptive perturbation or other mechanisms remain possible.

The installed SciPy1.17.1 LP diagnostic maximizes margin for a nonnegative RGB-weight plane with weights summing to1 and a free intercept, separately for each phase. All eight full-cube phase/strength subsets have no positive maximum margin within numerical solver tolerances. This independently supports root's finding against a single plain positive RGB decision plane for each phase. It is a numerical finite-input diagnostic, not a symbolic proof against all clipping, cache, nonlinear, spatial or tie-sensitive implementations. Interior-only subsets have seven zero-margin cases and one positive-margin case; do not claim every restricted subset independently rejects a plane.

The222cache/bin combinations retain factor3and the two previously useful offsets0.5/1, with float/truncation/nearest-even variants. They test444/555/565/666bins; fixed bin lower/center/rescaled representatives before or after perturbation; global first-hit, per-phase first-hit, and source-bin/per-phase first-hit caches. None beats538mismatches. This excludes these specified candidates on these inputs, not all caches, all bit layouts, all traversal orders or all strength functions. It gives no positive reason to substitute an error-diffusion algorithm.

## Relative-distance candidate: better, still incorrect

Ordered thresholding can act on a relative distance to two palette colors rather than perturbing RGB before selecting the nearest one. For black/white, a squared-distance ratio has nonlinear phase boundaries while approaching ordinary RGB nearest at a zero threshold perturbation. That makes it a discriminating, interpretable candidate consistent with the epsilon observation.

The best tested prior-case candidate is:

```
dBlack2 = R²+G²+B²
dWhite2 = (255-R)²+(255-G)²+(255-B)²
q = 255*dBlack2/(dBlack2+dWhite2)
noise = ((BayerRank+1)/(matrixSide²)-0.5) * strength * 5
white iff q + noise > 127.5
```

Its old strength5case misses60pixels/image, strength10misses153, totaling426/32,768entries. On the new cases it misses32pixels/image for gray-only, zero for epsilon, and114pixels/image for4×4:292/49,152new entries. Combined718/81,920still fails exact replay. The formula's factor5and offset1are fitted representatives, not established service constants. New results were available during investigation; these comparisons must not be labeled preregistered or independent heldout validation.

The105scalar combinations compare mean RGB, Euclidean distance ratio, Euclidean distance difference, squared-distance ratio and L∞distance ratio, with seven coarse factors1.5/2/3/3.2/4/5/6and offsets0/0.5/1. No per-pixel lookup, learned surrogate, free color weights or enormous fine grid was fitted. The selected formula has no exact scalar-boundary ties in the tested cases; the actual service's tie policy remains unknown. Extending a two-color ratio to multiple palettes would introduce new unverified choices, so no general reducer is supplied.

## Original source remains a separate authority

The original GIF `applyPalette` helper in shipped chunk `4354-3a62375cb4c03823.js` was retraced at its exact byte-bound function. It uses squared channel distances and packed444/565first-hit caches, with a separate RGBA path. The earlier unchanged-factory oracle already validated the modeled565candidate, which still failed the service. This pass does not relabel a better authored distance-ratio hypothesis as original source.

The extracted original `lookup_similar.gdshader` loops over LUT entries with RGB `distance`; `lookup_color.gdshader` tests exact RGB equality. Neither contains a Bayer/noise or error-diffusion implementation. They belong to GIF export, with their own alpha/index policy. Their source pin does not prove the public reducer runs them. No original server dither code was recovered.

Reproduce offline, emitting JSON to a new review receipt if preserving this one:

```sh
python scripts/recovery_depth/investigate_dither_independent.py
```

It uses already installed NumPy/Pillow/SciPy and imports no provider code. The outcome is narrower hypotheses and counterexamples. Private dithering, palette construction, animation de-flicker and whole-PixelLab parity remain separate unresolved questions.
