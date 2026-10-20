# Editable construction channel

This stage connects the existing sprite-construction skill to the local workbench: indexed palettes, ordered layers, shared cels, exact pixel transactions, persistent undo/redo, rendered sequences and layered native editor exchange. It is a local editing model with explicit rules. It does not reproduce PixelLab's private model or every native host behavior, segment a character automatically, create missing poses, or establish visual quality.

The [source and acceptance review](SOURCE-AND-ACCEPTANCE.md) separates retained native source observations from the reusable toolkit. [TOOLKIT-ORIGIN.json](TOOLKIT-ORIGIN.json) pins the eight original modules. The exchange report describes any subsequent parser hardening; original byte identity must not be confused with the current patched parser.

## Entry points

The same twelve methods are available through three entry points:

```bash
.venv/bin/sprite-workbench --workspace workspaces/art construct METHOD request.json
.venv/bin/sprite-workbench --workspace workspaces/art channel --base-dir "$PWD" --result-ref render.sequence
```

The CLI reads a small JSON request file and resolves filesystem paths beside that request file. The persistent channel accepts one JSON object per line, for example `{"id":1,"method":"local.construction.read","params":{"path":"source.json"}}`. Channel paths resolve relative to `--base-dir`. `system.capabilities` returns the bound request schemas. These are trusted local filesystem operations; the base directory is a convenience, not a sandbox.

A declared plan step uses `{"id":"project","action":"construction","method":"read","request":{"path":"source.json"}}`. Later steps can refer to `project.project` and `project.project_hash`. See the [complete runnable example](../../examples/local-construction/README.md).

| Method | Required request fields | Result or purpose |
|---|---|---|
| `save` | `document` | Validate a raw `sprite-edit-project/v1` object and store it immutably |
| `read` | `path` | Load bounded portable JSON from a file; useful for larger projects |
| `get` | `project` | Compact project summary, without dense pixel arrays |
| `write` | `project`, `path` | Export raw editable JSON to a new file; existing files/symlinks are preserved |
| `history` | `project` | Create an immutable history at cursor zero |
| `edit` | `history`, `transaction` | Apply a guarded transaction and return a new project, history and receipt |
| `undo` / `redo` | `history` | Replay and validate the journal, then move its cursor |
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

History retains replayable receipts and cursor state. Undo/redo survives process restart and Store transfer. Editing after undo starts a new immutable branch without modifying the old history. Replaying checks the entire journal against its initial project and current project/hash guards; a hash-shaped string alone is not accepted as valid history.

Rendering with `history` attaches it to the sequence. An `editable` sequence export then includes the typed project/history dependencies and original acquisition sequence where declared. Importing that bundle into a fresh Store permits further history operations. Exporting raw project JSON alone preserves the editable document but does not carry the separate Store history or source envelope.

## Editor and timing boundaries

Native exchange is **RGBA ASE plus an authoritative sidecar**, not native indexed ASE encoding. Untouched palette aliases and cel bindings are preserved using the sidecar. Duplicate layer names are refused where they would make layer identity ambiguous. Layer order, canvas geometry, locks, clock and supported ASE features are checked on import. See [EXCHANGE.md](EXCHANGE.md) for the actual editor command, supported subset, changed-pixel behavior and negative controls.

Keep the original Store, sidecar and exchange binding. A renamed editor output still uses the original sidecar explicitly. The initial rendered bundle predates native export and does not contain the later binding: perform the first import using the original Store. After that import, render with its `import_provenance` and export an editable bundle to carry the native input bytes, sidecar and binding into a fresh Store. The external ASE and sidecar files must also accompany that bundle for subsequent editor imports.

An unchanged native round trip preserves the original project identity, including typed source lineage, so its matching history remains usable. Changed native pixels create a new project; start a new history for subsequent local transactions. The import audit retains the source project for recovery, but external edits do not become transactions in the preceding local undo journal.

The editable document uses duration ticks and FPS. Rendered workbench sequences use exact rational holds. Native ASE milliseconds are a preview representation; they cannot replace the original clock. Conversion rejects cases that cannot be represented faithfully, including per-frame pivot/direction differences, finite play counts greater than one and alpha-zero hidden RGB in an incoming flattened sequence. Rendering follows the toolkit's documented transparent-black composite policy. The local indexed palette convention differs from the separately traced Pixelorama host convention.

Resource limits are explicit admission limits, not automatic resizing or truncation. See the implementation and verification reports for the frozen values and tested rejection cases. Existing files are preserved; failed native exchange receipts remain in the Store for diagnosis.

The current construction wrapper admits at most 128 layers, 4096 cels, 512 frames, 8,388,608 total indexed cel pixels, 256 transaction operations and 256 journal receipts. JSON documents are limited to 16MiB, with additional aggregate render, edit and replay budgets. A history can reach its aggregate limit before reaching 256 receipts. Animation events, landmarks and the ground pivot remain preserved metadata; this stage does not emit Godot event callbacks or contact logic.

## Completion boundary

Use this channel for controlled edits and exchange of supplied artwork. A useful humanoid animation still needs approved directional parts/poses, action and contact timing, complete playback inspection, and independent visual review. Passing an editor round trip or a pixel equality test does not establish any of those artistic results. The diagnostic marker is deliberately not scored as game art.
