# Independent Studio review

Read-only snapshot: canonical checkout `c785f1b`, following an initial read at `fb21f94`. This bounded review covers `studio.py`, `studio_services.py`, `web/studio.js` and the new Workspace handoff. It is separate from the browser integration and selection-agent acceptance suite.

## Finding: source correspondence on Workspace adoption

**Open at this snapshot.** `useWorkspace()` clears `sourceFrameIds` for a newly adopted project. `render()` then initializes that mapping from the current animation order whenever the source and current frame counts match. An animation reordered in Workspace before first Studio entry can therefore be reported as aligned with the original raw source order. Neither source nor working pixels are modified, but the displayed frame correspondence is unsupported.

An isolated Node probe executes the actual shipped `render()` method with two source frames and reversed current frame IDs. It observes:

```json
{"source_order":["source-frame-0","source-frame-1"],"current_order":["source-frame-1","source-frame-0"],"invented_mapping":["source-frame-1","source-frame-0"],"sourceAligned":true}
```

Private local replay: `/home/astra/artifacts/pixellab-reliable-acceptance-20261014/studio-source-mapping/probe.cjs`. This is a focused method replay with mocked host/DOM dependencies, not a browser screenshot. The original frame-order association is intentionally independent of the current order. The safe correction is to recover and validate the original association from retained import/project evidence, or leave source comparison unavailable for such adoptions. Existing saved Studio mappings correctly detect subsequent reorders.

## Other observed controls and limits

- Raw source and editable derivative identities are separate. Nonzero hidden RGB requires explicit generic-import opt-in; packaged demo loading declares its derivative normalization. Normalization changes only RGB where alpha is zero; source artifacts remain retained.
- Packaged example construction excludes slot zero from generated playback and retains source file byte hashes. The inspection clock is declared separately from unknown native sprite timing.
- Selection/UI context guards bind the project, cel, frame and history. Locked layers and shared-cel scope are displayed; applying a shared cel is explicitly labelled as updating linked frames. Backend receipt validation and cold receipt closure are separate requirements.
- Undo/redo uses immutable project/history revisions. Restore reloads those identities. Verification reports mechanical readiness and visual acceptance separately; art acceptance stays unreviewed.
- The export verifier reads actual emitted PNG/sheet/APNG and cold editable project/history. Complete file inventory and final package verification are checked. Cold selection/normalization provenance closure was still being completed by the root/selection agent during this review; this document does not claim that pending check passed.
- UI preview uses stored holds and finite play count; completed playback labels the button Replay. The independent Godot change is committed as `11afa65`: actual engine import, texture reload, pivots, authored events, elapsed-clock playback, finite repeats and final holds passed 13 focused checks. It does not establish GPU/art approval.

No further material defect was found in this bounded static review. This statement is not a full Studio acceptance result; the source-correspondence finding and pending cold provenance closure require final verification.


## Closure replay — 2026-10-14 UTC

**Resolved for the reviewed source-mapping paths.** Root fix `5eb11bf` is integrated at canonical HEAD `f84575a`. The original finding above remains a historical snapshot. The corrected `useWorkspace()` explicitly disables import-mapping capture for newly adopted projects; only `loadResult()` after fresh import enables one-time capture. Render clears that capability after use and retains the original association across later reorders. Saved mappings require the explicit `fresh-import-only-v1` policy, so older unproven associations are not restored as established correspondence.

A new independent test executes the actual `useWorkspace()`, `loadResult()` and `render()` methods with mocked DOM/transport. **1 passed in 0.07 seconds:** reordered Workspace adoption does not align, fresh imported order does align, and a subsequent reorder disables alignment without overwriting the original mapping. This extends the original focused replay; it does not claim browser integration or visual acceptance.

Reviewed UI SHA-256: `ebe865b50fcb970298b7104ac8d46b9cf18260e4b825c9eb6d0788e2fa5db09d`.

The previously pending cold provenance closure also passed one independent targeted run of canonical `test_export_cold_closure_final_inventory_and_download`: **1 passed in 0.86 seconds**. It actually exports and reopens a fresh store, validates the selection edit receipt and original selection/mask closure, compares normalization receipt and retained raw pixels, checks ZIP inventory, and rejects additional or corrupted exported files. Canonical export.py had the new selection/edit/normalization/session closure branches in its working tree; its SHA-256 at execution was `3d3ea9a037699768389f9c3538ce714754e0fe30eab65d148e93e9a608780fe8`. The exercised canonical test SHA-256 was `343f82f1939eaa260a079f4e94d8659b77c8670bdeaba82f7bf5e1ca4039f1be`. Temporary output was confined to `/home/astra/artifacts/pixellab-reliable-acceptance-20261014/studio-cold-final-review`; bytecode and pytest cache writing were disabled. This counts one independently rerun closure case, not the whole ten-case suite.

A read-only diff confirms the canonical Godot driver remains unchanged from its tested cherry-pick `baefeb6`; only the above artifact-closure branches differ in export.py. No additional material Godot risk emerged in this bounded review. Its checked float projection, conservative crossing budget, headless scope and absence of GPU/art approval remain as recorded in GODOT-ACCEPTANCE.md. No further full suite or engine run was repeated without a driver change.

There are no remaining blockers from this bounded independent review. Browser acceptance, broader test totals, package/wheel validation and art approval remain separate evidence owned by their respective reviewers.
