# Selected scene/export/review implementation review

Four baseline defects were reproduced against combined commit `711ca11` (geometry producer `92db439`). The owner is correcting them in the primary checkout; this receipt preserves the original observations. No producer modules were edited by this reviewer.

| Finding | Severity | Executed discriminator | Baseline result |
|---|---|---|---|
| R01 | Low | Scene position `[10**400, 0]` | `scene._point` converts the integer in `math.isfinite` before checking the bound; raw `OverflowError` escapes instead of `ValidationError`. |
| R02 | Medium | Replace a base-node raster in every frame, export editable, import into a fresh Store, remove the override | `_artifact_closure` omits never-sampled original base art. Current rendering survives, but reverting the edit cannot load the original raster. |
| R03 | Low | Editable `index.json` containing `[]` | `import_editable` calls `.get` on a list and leaks `AttributeError`. |
| R04 | Medium | Two positive rational holds `1 / 10**400` | Generated Godot weights are `0.0`; executing the generated player in an inert Node VM selects frame 1 at time zero. Both formats report written. |

R01's possible job classification as technical failure follows the source exception boundary; the job path was not separately executed. R04 concerns representability of an admitted rational clock, rather than ordinary codec rounding. Rational manifest and PNG authorities remain valid; unsupported playback formats should be reported separately. Other integer fields, malformed archive shapes, extreme overflow/cumulative clocks and full typed dependency families were not exhaustively tested.

The baseline command was:

```sh
python3 -m pytest -q tests/test_geometry_adversarial.py -rx --basetemp /tmp/pixellab-state-geometry-review
```

Result: **7 passed, 4 explicit known-reproduction xfails, zero failed/skipped**. A known reproduction is not a passed conformance test. Each test conditionally xfails only for its exact baseline failure, so owner corrections can turn the same tests into ordinary passing assertions.

The passing controls independently check straight-alpha compositing (`[106,95,136,136]`), hidden-RGBA protection, tampered editable rejection before ingestion, existing-output preservation, APNG chunk CRC/raw scanlines/exact rational holds, GIF centisecond error, unsupported partial-alpha/clock handling, and finite player boundary selection. Comparing the complete ownership source rectangle, including hidden RGB outside the owned mask, is a strong declared local policy; it is not classified as a defect.

The independent Godot fixture actually loaded exported resources in a fresh headless Godot 4.7.2 process, checked complete RGBA AtlasTexture crops, two finite plays and pivot restart. Completion times were `0.248721` and `0.497096` seconds against expected `0.25` and `0.5`, with an explicit 40 ms tolerance. This is resource/texture-readback and AnimatedSprite2D timing evidence, not GPU framebuffer or continuous visual acceptance. The generated-player test executes its actual script with inert DOM/image stubs, not browser painting.

Source hashes, exact command/outcome and limits are in `tests/evidence/state-geometry-adversarial/REVIEW-RECEIPT.json`; the original engine result is in `independent-engine-receipt.json`. This is selected mechanics review using synthetic controls, with no provider/model/network/art requests, no aesthetic acceptance and no claim of complete vendor reproduction.

## Owner-correction verification

The initial receipt and engine output remain unchanged. After applying prerequisite `ef7a941` and owner fixes `9ab16f9`, `e01a533`, `36938e2` (worktree equivalents ending `5540fcf`), the **same 11 independent controls passed with zero xfails/skips**. State-service and producer geometry suites also passed **29 tests**. `CORRECTION-RESOLUTION.json` binds the corrected source hashes, commands and exact selected resolutions; the second actual engine receipt is retained separately.

R01–R04 are resolved for their executed discriminators. Manual source inspection confirms bounded numeric admission, original scene dependency traversal, object-shaped index admission and separately checked float playback clocks. This does not extend the selected base-node case into full typed-lineage coverage or turn the synthetic controls into art acceptance.

## Store resource follow-up

A separate bounded process disabled garbage collection and performed 32 reads on the predecessor core. Store-related descriptors grew from 0 to 65 (69 after the controlled rollback/readback). Rollback itself preserved the head. This reproduces descriptor retention without attempting to exhaust descriptors or asserting a particular process-wide failure threshold.

Owner fix `24957ec` adds a closing transaction context: rollback/commit completes before `finally: db.close()`. The identical process-local probe recorded zero open Store descriptors after every read and rollback check. `python3 -m pytest -q tests/test_store_resources.py tests/test_state_flows.py` passed **14 tests**, including all 13 original state cases. Original and corrected small receipts plus core/probe hashes are retained in `STORE-RESOURCE-RESOLUTION.json`. No producer code was edited by the reviewer.
