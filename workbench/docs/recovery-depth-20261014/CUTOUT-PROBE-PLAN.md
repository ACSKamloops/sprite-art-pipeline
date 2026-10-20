# Remove-background: frozen three-request plan

**Prepared and verified; zero requests submitted by this reviewer.** This is a controlled public-endpoint experiment, not recovered segmentation source. The frozen artifact root is `/home/astra/artifacts/pixellab-cutout-characterization-20261014`. PLAN SHA256: `7fe6dea39aead1e171caa7239ce1b8e08b766b45568873faa3e7da61e89b8260`.

The [portable frozen snapshot](cutout-frozen/PLAN.json) retains the exact two PNGs, region annotations, readable requests and exact wire bytes. [prepare_cutout_probe.py](prepare_cutout_probe.py) only prepares, verifies and analyzes local files; it has no submit action, HTTP imports or credential resolver. Parent reviews and submits through its existing approved helper.

## Prior evidence reviewed

The previous `analysis-art/FEATURE-EXAMPLE-COVERAGE.md:23` recorded no available remove-background input/output pair. `CLIENT-PIXEL-OPERATIONS.md`, `CLIENT-LUA-PIXEL-COMPARISON.md`, and this branch's [PIXEL-CONVERSION-RECOVERY.md](PIXEL-CONVERSION-RECOVERY.md) establish client masks, hidden-RGB normalization and placement, but no executable cutout method. The later reducer/dither experiment concerns a different endpoint and does not establish cutout behavior.

Known shipped wrappers remain the boundary: Lua `extension-extracted/PixelLab/generate-remove-background.lua:69–95` maps Simple/Complex to remote task names and retains text only for Complex. Godot `pixelorama-recovered/src/Extensions/PixelLab/ui/tools/RemoveBackground.gd:69–120` submits these modes remotely. Neither inspected wrapper implements segmentation. Exact source hashes/lines are retained in [PIXEL-CONVERSION-LEDGER.json](PIXEL-CONVERSION-LEDGER.json).

The public `RemoveBackgroundRequest` schema permits PNG/JPEG base64, required image dimensions, optional text and nonnegative seed, with task enum `remove_simple_background` / `remove_complex_background`. Schema SHA256 is `af8ddcf710e1044455a31f091500f4381d2c89da667b2751744f734520ae93ec`, JSON pointer `/components/schemas/RemoveBackgroundRequest`. These requests use the same successful Base64Image PNG descriptor shape as the prior reducer helper. No optional text is sent, so task mode comparison is not confounded by a different description.

## Fixed slots

| Slot | Input | Task | Purpose |
| --- | --- | --- | --- |
| `simple-opaque` | 96×96 opaque synthetic robot | Simple | Connected background, enclosed identical-RGB patch, dark and near-background details. |
| `complex-opaque` | Exact same PNG bytes | Complex | Change only task enum; same omitted text and seed 123. |
| `simple-alpha` | Exact same RGB; small armor patches at alpha 0/64/128/255 | Simple | Change alpha only; measure alpha and visible-RGB preservation against opaque case. |

The RGB design is deterministic rectangles, not generated art or an invented segmentation algorithm. No Warhammer material or existing hero image is included. Exact source PNG SHA256s:

- `inputs/opaque.png`: `96816d261e63f65f5a25a6da9e890c79888b03cf316f91db2a2695c3fa53e4ba`.
- `inputs/alpha-patches.png`: `93cade3423b49a1dd5cd93dddfb52632d7467576efa29ea55b664732424954f9`.

Both variants have identical RGB arrays. Direct uploaded PNG retains the armor RGB beneath alpha 0; this deliberately tests the endpoint directly, without Godot's separate hidden-RGB serialization cleanup. The region JSON defines right/bottom-exclusive rectangles for border, enclosed background-colored patch, open channel, dark chest detail, near-background decoration, opaque armor and alpha patches. These are source-design annotations, **not** an estimated or asserted groundtruth semantic removal mask.

## Guard contract for the parent's submission helper

- At most three POST attempts total, one per named frozen slot; no automatic retries or task fallback.
- Verify all request/input pins and the reviewed PLAN hash before submission. Send exact `request-wire.json` bytes. Each wire hash is recorded in PLAN.
- Atomically create and retain each slot's `.submission.lock` with `O_CREAT|O_EXCL` before sending; record attempted state before POST. Timeout, transport error, rejection and ambiguous outcome all consume the slot. Do not remove a lock and retry.
- Reuse the previous helper's credential resolver and response redactor; deny redirects; 60s timeout; 4MiB response cap; retain actual wire hashes, sanitized one-entry HAR, response JSON and exact returned PNG bytes. Do not retain authorization/cookies.
- Actual generation charge is not estimated here. Parent reviews the budget and stops if returned usage is unexpected. Preparation and analysis spend zero provider calls.

The preparer uses `exist_ok=False` for a new artifact root and verifies all three allowlisted requests and inputs. Its verifier does not claim slots or call a provider. Persistent submission locks are the parent's responsibility because this utility intentionally contains no submission path.

## Reading the results without overclaiming

Removing the connected border/open channel while preserving the enclosed same-color patch would be consistent with a boundary-connected color removal policy on this fixture; it would not prove a flood-fill implementation. Removing both connected and enclosed same-color regions is consistent with global color masking or semantic hole removal and cannot distinguish them alone. Removal of near-background details, retention of dark details, and differences between Simple/Complex constrain behavior but do not identify a neural model, color-distance metric or exact tolerance. The enclosed patch can also read as a robot panel: its semantic status is deliberately ambiguous.

The analyzer reports actual regional alpha values, pixels changing alpha, newly invisible/visible pixels, changed RGB where input/output are both visible, all RGB changes including hidden pixels, and nonzero RGB beneath output alpha 0. It checks response PNG bytes against any retained output file before reporting metrics and rejects dimension mismatches. It makes no automatic quality score or segmentation classification. Repeated seed 123 does not establish deterministic behavior without a repeat request, which is outside this three-slot plan.

Even a complete successful public cutout measurement would **not** prove that PixMiniMax internally invokes this endpoint, uses these task modes, receives the same preprocessing, or applies the same matte/alpha restoration. Its public `no_background` contract and actual internal worker implementation remain separate evidence levels.

## Ready commands and current validation

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python docs/recovery-depth-20261014/prepare_cutout_probe.py verify
/home/astra/projects/pixellab-local-workbench/.venv/bin/python docs/recovery-depth-20261014/prepare_cutout_probe.py analyze
```

The verifier passed with zero locks. Analyzer currently records all three cases as `not-executed-or-no-response`. Seven offline fixture/analyzer assertions passed: identical RGB between inputs, planned alpha set, unchanged identity comparison, alpha-only change accounting, visible-RGB-only change accounting, no submission locks, and preparer SHA matching PLAN. The 96px opaque input was visually inspected as a small recognizable robot on flat green. No endpoint result or segmentation behavior is yet claimed.
