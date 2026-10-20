# PixelLab recovery: frozen predictions and a usable manual selector

This pass moves palette construction from output-derived fits to **predictions frozen before the corresponding requests**. It also exposes a reusable manual selection tool around recovered editor code. Six public reducer POSTs completed with HTTP200 and reported usage **0.6 generations**. No image/animation generation or new public cutout calls occurred. Private inference, full palette construction, dithering and production UI integration remain incomplete.

The [previous recovery pass](../recovery-next-20261014/README.md) retains the earlier source replays, calibrated mapper, cutout counterexamples and capture-verifier review.

## What changed

| Work | Result | Boundary |
|---|---|---|
| Fresh low-K palette predictions | First four calls match every predicted palette entry/order and all 8,192 RGBA entries, without receiving the service palette as an input. | Deliberately separated 2/3-color clusters; reversed frames share data, and alpha policies are competing hypotheses. No unique initialization or general high-K claim. |
| Invisible-only background | Two adaptive calls still match all 4,096 frozen RGBA predictions, but both raw palette-strip predictions fail. Requested K3 returns two visible palette colors; K2 returns one. | Reveals an important palette/hidden-RGB boundary; do not relabel these as complete palette predictions. |
| Visible-only strip hypothesis | After the K3 failure, a visible-only strip prediction was frozen before the K2 call and matches its one-entry strip exactly. | Adaptive same-image/changed-K test, not a new-color heldout or source disclosure. K3 visible-only matching is post-hoc. |
| Earlier 32-color discrepancies | A bounded float-centroid candidate explains all eight earlier mean-rounding discrepancies, but still fails three other centers and 768/8,192 output pixels. | A partial explanation does not recover the complete clustering algorithm. No center splicing or arbitrary fixes. |
| Dithering | Exact witness pixels reject a gray-linear perturbation proportional to strength, regardless of fixed phase coefficient. All 21 specified distance/bin hypothesis families also fail. | These finite formulas are ruled out; no exact replacement was recovered. |
| Manual selection | A bounded PNG→mask CLI runs the whole recovered FloodFill method and original RGBA similarity function without translating their bodies. | Recovered Pixelorama host manual selection. No proof of compiled-GDC equivalence, automatic PixelLab cutout or animation cleanup. |

All **12,288 frame pixel entries** match the primary frozen full-RGBA predictions. Only **4/6 raw palette strips** match; the separately frozen adaptive visible-only rule matches the sixth strip. Counts include repeated colors, correlated frames and reused images. They are not independent samples or a whole-pipeline completion score.

## Transparency affects the usable color budget

On the fresh alpha fixture, all-RGB frequency weighting matches the palette and pixels exactly while excluding alpha-zero pixels or weighting by alpha fails. Source alpha remains exact, including 720 hidden pixels across those two frames. This constrains construction behavior on those inputs; it does not identify a unique private implementation.

The subsequent fixture has an entirely invisible black family plus two visible warm/green families. With three requested colors, the returned strip contains only warm `[219,174,87]` and green `[44,151,85]`. With two requested colors, it contains only merged `[165,167,87]`. The predicted full-RGBA frames match both calls exactly. These observations support an all-RGB construction stage followed by a strip limited to visible output colors, but internal ordering/mechanism remains inferred.

Consequently, **a returned palette strip is not always sufficient to reproduce full hidden RGBA**. On the K3 fixture, remapping with only that strip changes the 512 hidden pixels per frame while reproducing the visible pixels. The earlier explicit fixed-palette mapper and its calibration are unchanged; do not generalize its successful returned-palette comparisons to every automatically constructed strip. Retain full frame bytes, source alpha and provenance separately.

## Detailed evidence

- [First four frozen-prediction audit](FROZEN-PREDICTION-REVIEW.md): archived source commit, input/receipt/PNG hashes, exact replay and REA bindings.
- [Adaptive transparency audit](HIDDEN-PALETTE-REVIEW.md): the two raw-strip failures and separately frozen K2 visible-only prediction.
- [Bounded palette inference](PALETTE-INFERENCE.md): initialization candidates, float/rounded assignments and unresolved 32-color counterexamples.
- [Dither interval falsifications](DITHER-INTERVALS.md): exact rational contradictions and finite hypothesis coverage.
- [Cutout route provenance](CUTOUT-ROUTE-PROVENANCE.md): remote request paths versus actual host manual tools, PCK-member identity and recovered-method replay.
- [Manual selector guide](HOST-MANUAL-SELECTOR-CLI.md), [independent review](HOST-SELECTOR-REVIEW.md) and two retained mask examples.
- [Verification](VERIFICATION.json) and [artifact manifest pin](ARTIFACT-MANIFEST-PIN.json).

Palette predictions use the standard forward/inverse [Oklab transforms](https://bottosson.github.io/posts/oklab/), with the previously calibrated quarter-lightness squared distance, deterministic farthest-point initialization and frequency-weighted Lloyd means. This is an authored hypothesis, not recovered service source. The [current public API schema](https://api.pixellab.ai/v2/openapi.json) and [API index](https://api.pixellab.ai/v2/llms.txt) were retained locally; their public declarations do not disclose clustering or internal animation code.

## Use the recovered manual editing channel

Run from the workbench with an existing PNG and a new output directory:

```sh
cd /home/astra/projects/pixellab-local-workbench
.venv/bin/python scripts/recovery_round3/host_flood_mask.py \
  --image /absolute/path/to/sprite.png \
  --seed-x 0 --seed-y 0 --tolerance 0.03137254901960784 \
  --output-dir /absolute/path/to/new-selection
```

This writes a white/transparent selection mask and a source-pinned receipt. The source image is preserved. A subsequent explicit editing operation can consume that mask. The wrapper supports a seed and normalized RGBA tolerance, bounds input to 512×512/4MiB and Godot execution to 60 seconds, and refuses an existing output directory. Active selection, tilemap and undo behavior are outside this harness.

The recovered code has a measured float precision boundary: tolerance 8/255 excludes a color differing by eight red-byte levels because the decoded float difference slightly exceeds the supplied tolerance. The original method selects 5,761 pixels where an integer-distance approximation would select 5,825. Preserve this behavior when claiming recovered-method replay; do not silently replace it with a Python flood-fill approximation.

Independent review corrected one wrapper metadata error: unselected mask pixels are transparent **white** `[255,255,255,0]`, not transparent black. Consume mask alpha. Two fresh executions reproduce the original PNG bytes exactly; only the receipt's description changed. Original receipts remain historical with an explicit [correction](MASK-CONVENTION-CORRECTION.json).

## Repeat the comparisons without paid calls

The six paid slots already have persistent claims and must not be resubmitted. Recheck the initial four into a fresh receipt:

```sh
.venv/bin/python -O scripts/analyze_palette_predictions.py \
  /home/astra/artifacts/pixellab-recovery-round3-20261014/PHASE-PLAN.json \
  --phase-sha 612055f7f53bf6eadeb71b24f9d4573f8d1bccf9707f2027d1dd293c16cddcaf \
  --output /tmp/new-palette-prediction-check.json
.venv/bin/python -m pytest -q tests/test_palette_predictions.py
```

The two follow-ups use `HIDDEN-PHASE-PLAN.json` / SHA `5fbb7df9e4a9c8dc90976df5018e7ebbfa84a167dd320ecd23c47f4511cbad90` and `BUDGET-PHASE-PLAN.json` / SHA `02d1edba4e8cb6fe6c9b0b87ef7151c1d4b77a507405c37b4235d2d226d8ad09`. Use the same analyzer with a fresh output path. It binds archived prediction source, frozen requests, predicted PNGs, actual responses and full REA decoded records.

Full current-pass artifacts are under `/home/astra/artifacts/pixellab-recovery-round3-20261014`; additional inference/review artifacts are pinned by the manifest. REA independently parses our retained HARs; it does not independently witness their network origin or attest vendor internals. Local timestamps and commits demonstrate recorded ordering, not external notarization.

The full suite passed **673 tests** with 1,398 warnings. Seven new offline tests check the palette hypothesis and discriminating fixtures. Independent audits replayed frozen predictions and the manual selector; final handoff and artifact hashes are recorded in the verification receipt. No runtime package/UI files were changed.

## Remaining gates

1. General automatic palette construction still needs exact initialization/refinement/rounding evidence and complex held-out predictions; the 32-color counterexample remains.
2. Positive-strength dithering needs a source implementation or a new interpretable rule surviving existing witness pixels before further paid validation is useful.
3. Host manual masks can now feed precise edits, but automatic cutout/private animation segmentation and de-flicker remain unknown. Preserve these distinct labels in the eventual UI.
4. UI integration, animation generation/refinement and final native-timing video inspection remain future work. This pass provides an executable selection channel and stronger palette evidence, not accepted animated game art.
