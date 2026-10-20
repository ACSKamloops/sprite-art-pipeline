# Editable construction and checkpoint history — v0.4.0

This stage connects the existing sprite-construction skill to the local workbench: indexed palettes, ordered layers, shared cels, exact pixel transactions, persistent undo/redo, rendered sequences and layered native editor exchange. It is a local editing model with explicit rules. It does not reproduce PixelLab's private model or every native host behavior, segment a character automatically, create missing poses, or establish visual quality.

The [source and acceptance review](SOURCE-AND-ACCEPTANCE.md) separates retained native source observations from the reusable toolkit. [TOOLKIT-ORIGIN.json](TOOLKIT-ORIGIN.json) pins the eight original modules. The exchange report describes any subsequent parser hardening; original byte identity must not be confused with the current patched parser.

Current integrated code `846e391` passed **430 mechanical tests with no failures/errors/skips**; these documentation edits follow that run. [Current test receipt](../readiness/evidence/TESTS.xml), [latest verification](../LATEST-VERIFICATION.md), [checkpoint history implementation](../readiness/HISTORY-IMPLEMENTATION.md) and [independent history review](../readiness/HISTORY-INDEPENDENT-REVIEW.md) state the scope. The [333-test report](evidence/verification/REPORT.json), [installed-package comparison](evidence/PACKAGE-PARITY.json) and [consistency check](evidence/FINAL-SPOTCHECK.json) remain historical v0.3.0 construction evidence; they do not certify the newer package by inheritance.

## Entry points

The same twelve methods are available through CLI, persistent JSONL, declared plans and the [local browser/HTTP controller](../readiness/README.md):

```bash
.venv/bin/sprite-workbench --workspace workspaces/art construct METHOD request.json
.venv/bin/sprite-workbench --workspace workspaces/art channel --base-dir "$PWD" --result-ref render.sequence
.venv/bin/sprite-workbench --workspace workspaces/web-control/store web --base-dir workspaces/web-control/files --port 8874
```

The CLI reads a small JSON request file and resolves filesystem paths beside that request file. The persistent channel accepts one JSON object per line, for example `{"id":1,"method":"local.construction.read","params":{"path":"source.json"}}`. Channel paths resolve relative to `--base-dir`. `system.capabilities` returns the bound request schemas. These are trusted local filesystem operations; the base directory is a convenience, not a sandbox.

The browser's Workspace controls existing supplied cels, palette indices/additions, frame timing, undo/redo and rendering. Methods exposes the same schemas and request JSON for precise operations. Browser file paths must remain within its configured base folder, unlike the trusted CLI/channel. Captured vendor methods remain unavailable. These are output/parameter refinement controls, not a complete graphical rig/pose authoring tool or a generative model backend.

A declared plan step uses `{"id":"project","action":"construction","method":"read","request":{"path":"source.json"}}`. Later steps can refer to `project.project` and `project.project_hash`. See the [complete runnable example](../../examples/local-construction/README.md).

| Method | Required request fields | Result or purpose |
|---|---|---|
| `save` | `document` | Validate a raw `sprite-edit-project/v1` object and store it immutably |
| `read` | `path` | Load bounded portable JSON from a file; useful for larger projects |
| `get` | `project` | Compact project summary, without dense pixel arrays |
| `write` | `project`, `path` | Export raw editable JSON to a new file; existing files/symlinks are preserved |
| `history` | `project` | Create an immutable history at cursor zero |
| `edit` | `history`, `transaction` | Apply a guarded transaction and return a new project, history and receipt |
| `undo` / `redo` | `history` | Verify the history and move to its exact checkpoint; cold loading replays the complete retained journal |
| `from_sequence` | `sequence` | Convert supplied RGBA frames to one indexed layer; optional `animation_id` and integer `fps` |
| `render` | `project`, `animation_id` | Render a workbench sequence; optional matching `history` and `import_provenance` retain their typed dependencies |
| `ase_export` | `project`, `directory` | Write a layered RGBA ASE file, bound metadata sidecar and report; optional `animation` |
| `ase_import` | `path`, `sidecar` | Validate a changed native file against its bound sidecar and create a new project with import provenance |

Unknown request fields are rejected. Construction methods do not publish heads or promote candidates. A completed channel envelope means the synchronous request completed; queued jobs retain their separate status rules.

## Exact editing and history

`project` is the SHA256 ID of a typed Store envelope. `project_hash` is the different canonical hash of the editable document, used in transaction guards. Do not interchange them. An example transaction is:

```json
{
  "schema": "sprite-edit-transaction/v1",
  "expected_project_sha256": "REPLACE_WITH_PROJECT_HASH",
  "reason": "Correct the selected highlight pixel",
  "operations": [{"op":"paint","cel_id":"marker-a","points":[[1,1,3]]}]
}
```

Supported operations include paint/erase, masked color replacement, cel/layer translation with explicit clipping policy, palette changes/additions, guarded candidate patches, frame timing and pivots. A transaction operates on supplied indexed data. Palette edits affect every use of that index, and shared-cel edits affect every frame bound to that cel. Locked layers block both direct edits and palette changes that would affect them. Candidate patches must preserve every pixel outside the specified mask.

Version 2 history retains replayable receipts, cursor state and typed immutable checkpoints. Undo/redo survives process restart and Store transfer. Editing after undo starts a new immutable branch without modifying the old history. Cold loading verifies the initial project, every receipt/checkpoint and the redo tail beyond the cursor. Warm proof reuse re-reads and SHA-verifies its dependencies; it does not trust file timestamps or persist an unchecked disk cache. A hash-shaped string alone is not accepted as valid history. Read-only v1 loading remains compatible; mutation migrates only after complete legacy verification and source-provenance checks.

Rendering with `history` attaches it to the sequence. An `editable` sequence export then includes the typed project/history dependencies and original acquisition sequence where declared. Importing that bundle into a fresh Store permits further history operations. Exporting raw project JSON alone preserves the editable document but does not carry the separate Store history or source envelope.

## Editor and timing boundaries

Native exchange is **RGBA ASE plus an authoritative sidecar**, not native indexed ASE encoding. Untouched palette aliases and cel bindings are preserved using the sidecar. Duplicate layer names are refused where they would make layer identity ambiguous. Layer order, canvas geometry, locks, clock and supported ASE features are checked on import. See [EXCHANGE.md](EXCHANGE.md) for the actual editor command, supported subset, changed-pixel behavior and negative controls.

Keep the original Store, sidecar and exchange binding. A renamed editor output still uses the original sidecar explicitly. The initial rendered bundle predates native export and does not contain the later binding: perform the first import using the original Store. After that import, render with its `import_provenance` and export an editable bundle to carry the native input bytes, sidecar and binding into a fresh Store. The external ASE and sidecar files must also accompany that bundle for subsequent editor imports.

An unchanged native round trip preserves the original project identity, including typed source lineage, so its matching history remains usable. Changed native pixels create a new project; start a new history for subsequent local transactions. The import audit retains the source project for recovery, but external edits do not become transactions in the preceding local undo journal.

The editable document uses duration ticks and FPS. Rendered workbench sequences use exact rational holds. Native ASE milliseconds are a preview representation; they cannot replace the original clock. Conversion rejects cases that cannot be represented faithfully, including per-frame pivot/direction differences, finite play counts greater than one and alpha-zero hidden RGB in an incoming flattened sequence. Rendering follows the toolkit's documented transparent-black composite policy. The local indexed palette convention differs from the separately traced Pixelorama host convention.

Resource limits are explicit admission limits, not automatic resizing or truncation. See the implementation and verification reports for the frozen values and tested rejection cases. Existing files are preserved; failed native exchange receipts remain in the Store for diagnosis.

The current construction wrapper admits at most 128 layers, 4096 cels, 512 frames, 8,388,608 total indexed cel pixels, 256 transaction operations and 256 journal receipts. JSON documents are limited to 16MiB. V2 additionally bounds peak indexed work, 256MiB of unique checkpoint/source-raster dependency bytes and 536,870,912 aggregate cold replay work units, alongside operation/render limits. A history can reach an aggregate limit before 256 receipts. [Exact resource policy](../readiness/HISTORY-IMPLEMENTATION.md). Animation events, landmarks and the ground pivot remain preserved metadata; this stage does not emit Godot event callbacks or contact logic.

## Completion boundary

Use this channel for controlled edits and exchange of supplied artwork. A useful humanoid animation still needs approved directional parts/poses, action and contact timing, complete playback inspection, and independent visual review. Passing an editor round trip or a pixel equality test does not establish any of those artistic results. The diagnostic marker is deliberately not scored as game art.

The historical v1 [integration review](INTEGRATION-REVIEW.md) measured 0.90s first edit and 18.12s twentieth edit at 256×256/24 frames sharing one cel. That result is preserved; it is no longer the current warm-session performance result. Verified v2 checkpoints and an exactly checked compositor derivative resolve the demonstrated repeated-replay slowdown on the declared one-/eleven-shared-layer workloads.

| Shared layer cels,256×256/24 frames | First edit | Twentieth edit | Fresh-process cold load |
| --- | --- | --- | --- |
| 1 | 0.125s | 0.135s | 1.170s |
| 11 | 1.235s | 1.420s | 13.802s |

All declared warm edit/undo/redo gates passed; independent differential, cold-replay and tamper checks retained exact local semantics. [Benchmark and limitations](../readiness/HISTORY-IMPLEMENTATION.md). Fixture content differs from the historical run, so this is a workload-scale comparison rather than a byte-identical A/B test. Cold verification remains linear and its eleven-layer loading cost is visible.

A representative multilayer humanoid editing/action session and complete quality review remain future gates. The broader63 analysis questions, missing local command/flow implementations, hosted grammar and backend requirements also remain unresolved. [Readiness](../readiness/README.md) holds original-art/model comparisons separately from these available mechanical editing tools. No new generation is needed to relabel an incomplete pipeline as complete.
