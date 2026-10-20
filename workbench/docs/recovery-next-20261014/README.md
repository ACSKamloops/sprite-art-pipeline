# PixelLab recovery: palette construction, dithering and cutout

This pass adds controlled measurements and reusable verification to the [previous recovery](../recovery-depth-20261014/README.md). It does **not** complete private inference recovery or approve an animation pipeline. Twelve new public API POSTs completed with HTTP200, reporting **5.7 generations** total. No H3 animation or new artwork was generated in this pass. Full sanitized producer captures, exact returned PNGs and twelve REA Evidence records remain local.

## What the new evidence establishes

| Area | Measured result | What remains unknown |
|---|---|---|
| Automatic palette | Changing the second frame changes the first frame's palette/mapping. Two differently partitioned sequences with the same combined histogram return the same palette/mapping on this fixture. | General frame weighting, clustering initialization, convergence, ties and private implementation. |
| Palette mapping | The previously calibrated `0.25*dL²+da²+db²` Oklab rule reproduces all 32,768 RGBA entries across the four automatic-palette calls when supplied each returned palette. | How to independently construct the exact service palette. These comparisons reuse observed palettes and contain repeated colors/frames. |
| Palette centers | All four centers in each 4-color case equal rounded pixel-frequency-weighted Oklab cluster means; 24/32 centers match in the 32-color case. | The eight 32-color discrepancies and precise iteration/rounding rules. This is a consistency measurement, not source recovery. |
| Shipped palette helper | The unchanged website 32-color helper and a separately labeled weighted-distance variation both disagree with the service 32-color palette. | Exact service palette construction is not recovered. Standard tested Pillow candidates also disagree. |
| Dithering | At strength 0.000001, the 2×2 result exactly matches ordinary equal-weight sRGB nearest black/white, while differing from nondithered Oklab at 1,591 pixels/frame. Gray-only and cube-tail ramps agree at the same phase. | Positive-strength dither math. The best tested new relative-distance candidate is still inexact; do not deploy it as a recovered method. |
| Initial cutout | Simple/Complex on one RGB design and Simple on its alpha variant return identical PNGs. Source foreground alpha 0/64/128 becomes 255; removed pixels become zeroRGBA. | Whether the same policy applies to other inputs or internal animation processing. |
| Corrected cutout | The verified connectivity fixture separates Simple/Complex by 89 pixels. Neither matches the predeclared flood-fill candidates exactly. | The precise mask/semantic/morphology implementation. A near-match is insufficient. |
| Retained paired outputs | Twenty exposed main/quantized pairs are PNG-byte identical: 15 animation-related frames and five UI/terrain outputs. One changed Pro Flash still pair is consistent with the calibrated palette mapper. | No changed animation pre/post sequence is exposed, so the private de-flicker transform cannot be reconstructed from those pairs. |

These public endpoints constrain observable behavior. Nothing in these probes proves that PixMiniMax calls either endpoint internally. REA decodes our retained producer HARs and binds their contents; it does not attest the vendor's private code, weights or network execution independently.

## Detailed findings and review

- [Automatic/shared palette measurements](PALETTE-FINDINGS.md), including exact-source rejection, candidate comparisons, centroid residuals and all source/response bindings.
- [Dithering investigation](DITHER-INDEPENDENT.md), including counterexamples, phase/context controls and bounded candidate failures.
- [Initial cutout measurements](CUTOUT-FINDINGS.md), including the corrected interpretation of the first fixture's blocked channel.
- [Corrected topology plan](CUTOUT-CONNECTIVITY-PLAN.md) and [measured mode comparison](CUTOUT-CONNECTIVITY-FINDINGS.md).
- [Same-job paired color recovery](PAIRED-COLOR-RECOVERY.md), including the 1,367-file bounded search and missing pre/post animation evidence.
- [Independent capture-verifier review](CAPTURE-REVIEW.md), including deliberate corruption tests and fixes made before final verification.
- [Final independent cross-review](FINAL-REVIEW.md), including pixel-level counterexamples and the animation/UI counting correction.
- [Verification receipt](VERIFICATION.json) and [external artifact manifest pin](ARTIFACT-MANIFEST-PIN.json).

## Local channels and repeatable checks

The one-shot [prepared capture runner](../../scripts/probe_pixellab_prepared.py) accepts only the public reducer/cutout endpoints. It validates the SHA-pinned whole plan, every request and exact wire body before credentials/network, uses persistent atomic submission claims, refuses existing capture evidence, makes no automatic retry, denies redirects and bounds response size. It retains sanitized producer HAR, raw-before-scrub hashes, response JSON, usage, output PNGs and ambiguity state. Its 26 offline tests use fake credentials and fake transports. **The completed slots must not be resubmitted.**

The offline [phase verifier](../../scripts/verify_pixellab_probe_phase.py) checks request/claim/response/PNG correspondence and complete REA decoded-record equality. It rejects duplicate phase variants and repeated resolved slots, uses explicit checks under Python `-O`, and never reads credentials or calls providers. Its result establishes these file bindings, not private algorithm identity or independent billing reconciliation.

The nine corruption/counting cases from independent review are now executable [regression tests](../../tests/test_verify_pixellab_probe_phase.py), alongside a valid baseline and duplicate-JSON rejection. These 11 tests construct explicitly synthetic fixtures with mocked transport; their adapter-shaped records are not real service/REA evidence. They make the verifier checks repeatable without paid calls or external artifact dependencies.

Recheck the existing captures into fresh receipt files:

```sh
cd /home/astra/projects/pixellab-local-workbench
.venv/bin/python -O scripts/verify_pixellab_probe_phase.py \
  /home/astra/artifacts/pixellab-recovery-next-20261014/PLAN.json \
  --phase-sha 5ac105207201a715b401c1ae287250ff3341421724fceaa9e9aa33ef574a25cd \
  --output /tmp/pixellab-probe-recheck-new.json
.venv/bin/python -O scripts/verify_pixellab_probe_phase.py \
  /home/astra/artifacts/pixellab-recovery-next-20261014/CONNECTIVITY-PHASE-PLAN.json \
  --phase-sha f58aeee4a67c04455a8e5a3f52202bffc6102d76d6f95c66f38a14e4ce9eaaf5 \
  --output /tmp/pixellab-connectivity-recheck-new.json
.venv/bin/python -m pytest -q tests/test_probe_pixellab_prepared.py
.venv/bin/python -m pytest -q tests/test_verify_pixellab_probe_phase.py
```

Expected final bindings: first phase 10 calls/24 PNGs/3.7 reported generations; second phase 2 calls/2 PNGs/2.0 reported generations. Palette strips count as returned PNGs. The final full suite, including the capture runner and verifier regressions, passed **666 tests** with 1,398 warnings. Offline analysis and adversarial checks are documented separately. The independent cross-review records the earlier 655-test snapshot; the final suite adds the 11 verifier regressions. Frozen original research, runtime files and the prior wheel are preserved and checked through the current handoff validator.

## Evidence locations

- `/home/astra/artifacts/pixellab-recovery-next-20261014`: phase plans, final binding receipts, test logs, verifier review receipts and full artifact manifest.
- `/home/astra/artifacts/pixellab-palette-construction-20261014`: four palette requests, source-exact helper outputs, returned frames/palettes and analysis.
- `/home/astra/artifacts/pixellab-dither-followup-20261014`: gray-context, tiny-strength and 4×4 requests/results.
- `/home/astra/artifacts/pixellab-cutout-characterization-20261014`: initial three cutout calls and preserved original annotations.
- `/home/astra/artifacts/pixellab-cutout-connectivity-20261014`: corrected topology proofs, two calls and comparison.
- `/home/astra/artifacts/pixellab-paired-color-recovery-20261014`: retained capture inventory, source-pinned decoded pairs and ledgers.

## Next gates

1. Treat only the source-exact replays and the bounded nondithered mapper as available recovered/calibrated channels. Keep automatic clustering, ordered dither and segmentation candidates visibly experimental.
2. Exact palette construction needs initialization, iteration/rounding and held-out prediction evidence. A post-hoc palette fit cannot replace that test.
3. Dithering needs an interpretable rule that survives these existing counterexamples before another held-out paid call is useful.
4. Internal animation sampling/cutout/de-flicker needs additional same-stage evidence or accessible implementation. Separate generated sequences cannot isolate a hidden correction step.
5. Integrate tested channels into the local workbench with provenance labels, then compare generic RPG hero animations at native frame timing and inspect the final video. This pass changes analysis/capture tooling; it does not deliver those UI integrations or accepted animation art.
