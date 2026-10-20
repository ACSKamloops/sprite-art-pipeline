# Independent integration review of local source operations

Scope: callable parity services, schemas, CLI, JSONL, loopback HTTP, source-pixel still promotion and editable closure. This review owns only this document and `tests/test_parity_services_adversarial.py`. No production implementation edits, paid calls, provider/browser-auth activity or full-suite run.

## Findings requiring correction

1. Initial `to_sequence` accepted a fabricated CAS JSON containing only the expected kind/version, public manifest hash, any existing raster/hash and arbitrary operation. A manifest string alone does not validate a source execution receipt. Missing/type-malformed execution objects could also escape as `AttributeError`. Promotion must validate operation/request/execution structure, expected source-method hashes, preserved input identity, actual source/output hashes and operation-specific artifacts before writing the still sequence. This establishes local receipt consistency, not private server attestation or authenticity against an actor able to construct every matching local artifact.
2. Initial `paint_primitive` stored and returned its source footprint after editing history, without binding it to history/project/sequence. Editable export followed history/checkpoints but could omit the footprint. A cold replay could retain painted pixels while losing the source command, original ordered/duplicate point list and provenance. A source-paint evidence edge must survive history rendering, export and cold restore; separately returned IDs alone are insufficient.

The first two findings were identified by source inspection and sent to the implementation owner before integration commit; this reviewer did not execute that uncommitted baseline. Integration `b9dffe0` corrected promotion with strict source/execution validation plus actual Godot replay, and bound footprint evidence to guarded history/export closure.

3. The first integrated footprint validator checked command syntax, source pins, point hash and transaction mask but did not establish that the recorded command generated those points. An executable regression changed a genuine ellipse command position `[3,3]→[4,4]` while retaining original points/hash/transaction. `construction.load_history` accepted it. This is an evidence-consistency failure even though painted pixels were unchanged. Fix `6e424de` replays source commands for newly attached/cold evidence and compares the actual result rows, with dependency-aware reuse for already certified immutable history. The exact regression now rejects.

## Independent acceptance coverage

- Schema negatives reject extra fields, wrong scalar/container types, boolean integers, unknown operations, invalid geometry and invalid duration before accepted artifact publication.
- Alter a genuine pixel receipt's operation, request, version, source/method/input/output hashes, raw artifact or input-preservation declaration. Missing execution and nonobject execution must produce validation errors. A minimal public-manifest-stamped raster must not be promoted.
- For serialize/decode/place/mask/reference conditioning, promote an exact authored 1/7-second still; retain the receipt plus every input/output raster, decoded PNG/raw media and serialized raw bytes through editable export into a cold Store. Compare every closure byte and exact frame pixels/holds.
- Run real CLI dispatch and extra-field rejection. JSONL and actual loopback HTTP expose explicit `local.parity.*`; invalid local requests and vendor-route attempts reject without paid fallback. Catalog and capability metadata retain false whole-system/vendor equivalence and forwarding declarations.
- Paint an actual source ellipse footprint through guarded history, render with history bound, export/editable cold restore, retain the exact footprint/source provenance and verify undo reaches the original project.

Provider disabled metadata and rejected vendor identifiers are the observed routing boundary. These checks do not prove arbitrary network noninterference, live vendor compatibility or all application launch paths. Channel plumbing does not promote source fixtures into private-model parity.


## Completed verification

Reviewed integration `b9dffe0` plus corrective `6e424de`, with palette and original-shape dependencies. They were cherry-picked into the isolated review worktree; this change adds only independent tests/report. The final focused command was:

```bash
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest -q tests/test_parity_services_adversarial.py tests/test_parity_pixels_adversarial.py tests/test_parity_pixels.py tests/test_parity_commands.py
```

**125 passed in 15.20 seconds, exit 0.** This combines 44 new integration cases, 52 previously authored pixel adversarial cases, 13 owner pixel cases and 16 owner shape cases. The separate new integration run completed 44 passed in 8.60 seconds before one metadata assertion was added; the final combined run includes that assertion. These are focused mechanical tests, not a full-suite count, private behavior match or parity percentage.

The 44 integration cases cover 16 schema negatives, 11 genuine-receipt alterations, one minimal forged receipt, five output/closure cold restores, CLI, JSONL, actual loopback HTTP, shape footprint cold restore/undo, pipeline dispatch/export and six altered shape-evidence cases. All malformed pixel promotions reject before new blobs in these fixtures. Full source executions and receipt replays use installed Godot. CLI launches a fresh Python process; JSONL uses the real channel handler with in-memory streams; HTTP uses a real local server and token. No external network or provider call is part of these tests.

All six local capability entries declare no provider forwarding or vendor equivalence. Catalog/palette/pixels/footprints are `deterministic-source`; paint/still promotion remain supplied-art operations. Explicit vendor-route attempts reject: JSONL rejects its nonlocal namespace and HTTP reports `unsupported`. A malformed request does not prevent subsequent JSONL ping.

Editable cold restore checks all closure bytes, not only output pixels: source requests/raster payloads, PNG media, output raster, serialized raw transport, source-pixel execution receipt and original ordered shape footprint/source provenance are retained. Authoring hold 1/7 remains exact and one-shot. The source-paint path retains history evidence and undo to the initial project. Altered command controls, source pins, point hash, boolean receipt index, extra fields and nonobject artifact reject.

Remaining limits: receipt replay is local deterministic consistency on the recorded engine, not provider attestation; a different engine requires explicit new execution. Tests do not cover every source command/control combination, every channel, OS exhaustion or private model/source behavior. The original source methods' flattened-capture/undo-sink boundaries remain unchanged. No original whole requirement or artistic acceptance is closed by these channel checks.
