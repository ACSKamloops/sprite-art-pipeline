# Dither interval investigation: no exact rule

No tested rule fits all retained observations. This pass replaces amplitude grids with feasible-interval tests for **15specified pointwise distance hypotheses** and **6post-noise bin hypotheses**. It also supplies exact gray counterexamples showing why a gray-linear, strength-proportional perturbation cannot explain the captures, even with an arbitrary coefficient for each phase. No new provider/API/credential operations occurred; frozen reports, artifacts and canonical source were read only.

[DITHER-INTERVALS.json](DITHER-INTERVALS.json) records source/request/response/output hashes, formulas, amplitude bounds and the pixels imposing each bound. [The offline helper](../../scripts/recovery_round3/dither_feasible_intervals.py) uses NumPy/Pillow only, imports no provider code and prints a receipt. Only new `scripts/recovery_round3` and `docs/recovery-round3-20261014` paths were written.

## Exact gray contradictions

Consider a phase-local gray rule:

```
white iff gray - 127.5 + strength*n > 0
```

Here `n` can be **any constant for this phase**; it need not follow a Bayer matrix. Existing source-bound pixels at `(x=129,y=17)` and `(x=131,y=17)` imply:

| Case | Gray | Returned | Required coefficient |
|---|---:|---|---|
| strength5,phase11 |129|white| n > −3/10 |
| strength10,phase11 |131|black| n ≤ −7/20 |

The interval is empty:−3/10 exceeds−7/20 by1/20. This is a strict gap, not a floating-point/tie equality. The observed near-zero raw-RGB mapping remains compatible with several nonlinear rules, but it cannot rescue this particular strength-proportional gray rule.

Even within strength5, the conventional centered2×2Bayer rule with a single amplitude `A` fails:

```
white iff gray - 127.5 + A*5*((rank+0.5)/4 - 0.5) > 0
```

Gray122at phase10/rank3 is white, requiring `A>44/15`. Gray129at phase11/rank1 is white, requiring `A<12/5`. These bounds differ by8/15in the wrong direction. This stronger pair avoids any tie ambiguity in the earlier boundary example involving gray132.

Consequently, varying a single scalar amplitude, allowing an arbitrary *fixed* Bayer offset, or merely replacing that amplitude by a finite positive function of **channel variance only** cannot solve the gray-linear case: both witnesses have zero channel variance. Nonlinear strength response, a brightness-dependent function, per-channel/discrete behavior, bias terms, state or other mechanisms remain possible. This does not reject every adaptive method.

## Distance-space and variance-normalized hypotheses

The pointwise tests use `score(RGB)-127.5 + A*strength*phase >0`, `A≥0`, with one amplitude shared across the cases. Scores tested are:

* Mean RGB, algebraically equivalent to unnormalized squared-distance difference between black and white.
* `255*dBlack/(dBlack+dWhite)` for Euclidean distances.
* `255*dBlack²/(dBlack²+dWhite²)`, the earlier improved but inexact relative-distance candidate.
* `127.5+(dBlack-dWhite)/(2*sqrt(3))`.
* `127.5+(mean-127.5)/(1+channel_variance/(255²/4))`, one explicit variance-normalized candidate.

Each is tested under centered Bayer offset0.5, offset1 and offset0. These are **five score functions × three conventions**, not a finely sampled parameter grid. For each hypothesis, all admissible amplitudes are intersected directly from white/black inequalities. Empty intersections retain the strongest lower/upper pixel witnesses or fixed-zero-coefficient contradictions. No global feasible amplitude exists.

For the centered squared-distance ratio, strength5gray alone demands approximately `A>5.855770116` and `A<4.799335732`. Thus even a continuous amplitude search cannot make that normalization exact. Its improvement in the preceding report does not identify a hidden server distance ratio.

Offset1assigns zero perturbation to rank1; offset0assigns zero to rank2. Existing same-phase/same-RGB changes between strengths then supply fixed-coefficient contradictions independent of the chosen pointwise score. Those particular conventions cannot be repaired merely by choosing another amplitude.

Numerical bounds for nonlinear scores use double precision; they are finite-input falsifications of the written formulas, not universal algorithmic impossibility proofs. The gray-linear rational contradictions above are exact. A few restricted subsets admit amplitudes—for example centered mean RGB fits the strength10gray subset with `2.8≤A≤46/15`—but those amplitudes fail the other subsets. A subset interval is not an exact full replay.

## Reduced-resolution diagnostics

A deterministic lookup indexed only by an **unperturbed RGB bin plus phase** fails for444,555,565and666bins. At strength5, gray125at `(125,16)` is black and gray127at `(127,16)` is white. Both occupy the same bin for each listed layout and the same phase/rank2. No fixed entry for that key can supply both labels. This does not reject a lookup keyed after perturbation, exact-RGB keys, contextual state or an adaptive binning scheme.

For post-noise quantization, six specified candidates were tested without an amplitude grid: centered equal-channel Bayer noise,555/565/666bins, fixed bin midpoints, and either truncation or nearest-even conversion before binning. The first white noise transition is found at the exact discrete channel-bin boundary. It becomes an inequality on the shared amplitude. All six global amplitude intersections are empty. This covers those layouts/representatives only, not arbitrary caches, palette traversal or per-channel perturbations.

## Coverage and conclusion

The captures are the old strength5/10cube+gray pair and the new gray-context, epsilon and4×4cases. Their request-embedded palette is verified opaque black/white. Response PNG bytes, canvas, alpha and duplicate-RGB alpha frames are checked. The fit uses **40,960first-frame pixel observations**; second frames verify unchanged alpha/RGB correspondence but are not duplicated in the interval fitting. Gray tails contain repeated observations. Prior reports already bind HAR/REA; this pass adds no new live evidence or private source.

No tested hypothesis is exported as a PixelLab method or production reducer. The earlier426/32,768partial distance-ratio fit remains inexact, and no exact candidate emerged here to issue a fresh heldout prediction. Future source recovery should distinguish the order of channel conversion, noise formation, quantization and matching. If a future exact candidate is found, it still requires a frozen prediction on a genuinely new discriminating fixture before being described as independently validated. Root owns any such calls; none is requested or made here.

Reproduce:

```sh
python scripts/recovery_round3/dither_feasible_intervals.py
```
