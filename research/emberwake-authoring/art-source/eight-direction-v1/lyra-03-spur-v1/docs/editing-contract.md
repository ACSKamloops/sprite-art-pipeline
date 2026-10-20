# Precise editing API v1

`validate_project(project)` checks CONTRACT.md shape and references. `project_hash(project)` is SHA256 of canonical UTF8 JSON without trailing newline. Objects use UTF16 code-unit key order, arrays retain order, strings use JSON escaping without ASCII escaping, finite doubles use ECMAScript shortest numeric spelling (fixed at1e-6 through below1e21), negativezero becomes0, integer values must stay in JavaScript's exact range. The canonicalization is shared with the browser implementation; PNG hashes are distinct from project/pixel hashes. `cel_hash(project,id)` hashes the entire `{layer_id,pixels}` object.

`render_frame(project,frame_id)` returns full-canvas PIL RGBA. Layers are ordered back-to-front; missing frame bindings are transparent. No automatic cropping, recentering, inferred pivots or animation timing. Palette RGB is unrestricted RGBA bytes, including partial alpha. Source-over is explicitly integer-defined: `N=sa*255+da*(255-sa)`, outputalpha=`floor((N+127)/255)`, channel=`floor((src*sa*255+dst*da*(255-sa)+floor(N/2))/N)`; N0 yields transparent black. This avoids implicit tool-specific rounding. Opaque native sprites remain exact.

`apply_transaction(project,transaction)` returns `{project,receipt}` and never changes its input. Every operation is applied to an isolated copy, then complete project validation runs before acceptance. Rejection raises `EditError`. Transaction requires exactly `schema:'sprite-edit-transaction/v1'`, `expected_project_sha256`, nonempty `reason`, and nonempty `operations`. Operation fields are strict; unknown fields fail. Coordinates are integer full-canvas locations, palette indices integer, stroke order explicit (last point at repeated coordinates wins). Masks are unique `[x,y]` coordinate lists.

Supported operations:

|op|required fields|optional fields|
|---|---|---|
|paint|cel_id,points:[[x,y,index],…]|mask|
|erase|cel_id,points:[[x,y],…]|mask|
|replace_color|cel_id,from_index,to_index,mask|none|
|translate|cel_id,dx,dy|allow_clip (defaultfalse)|
|translate_layer|layer_id,dx,dy|allow_clip (defaultfalse)|
|palette|index,rgba:[r,g,b,a]|none|
|palette_add|rgba:[r,g,b,a]|none|
|candidate_patch|cel_id,mask,candidate_pixels,expected_cel_sha256|none|
|frame_timing|frame_id,duration_ticks|none|
|pivots|render_pivot,ground_pivot|none|

Every operation also includes `op`. Transparent entry0 stays `[0,0,0,0]` and cannot be edited. Locked layers reject cel edits and palette edits affecting their used indices. Translation rejects any clipped nonzero index unless allow_clip is explicitly true; layer translation updates each owned cel once, including shared or unbound cels. A cel edit intentionally affects all frames referencing that stable cel ID. Other frames and all timing/pivots/landmarks/provenance remain unchanged. Timing or pivot changes require their named operations.

Candidate patches use a full-canvas dense indexed array. Every index outside the explicit mask must equal the live cel, and both project and cel preconditions must match. `candidate_transaction(project,cel_id,PILimage,mask)` converts modern RGBA candidates, appends needed palette colors and preserves original outside-mask indices. A candidate PNG that changes any outside-mask RGBA is rejected; no quiet crop/rescale/recenter. This is an import gate, not visual approval of AI art.

Receipt is `{schema:'sprite-edit-receipt/v1',before_sha256,after_sha256,transaction,diff}`. Diff includes changed cel index coordinates, changed composited RGBA coordinates/bounds perframe and unchanged frameIDs. Pixel coordinates are row-major sorted; bounds are `[xmin,ymin,xmaxExclusive,ymaxExclusive]`. Metadata changes remain explicit in the transaction and canonical afterhash. `History(project).apply(tx)/undo()/redo()/journal()` preserves snapshots and exact preconditions. `History.replay(initial,journal)` recomputes every receipt, rejects tampering, restores its cursor and retains redo; editing after undo discards the abandoned redo branch.

`export_project(project,directory,columns=8)` writes canonical editableJSON, deterministic fullcanvas PNGs, atlas and manifest containing source/canvas/clock/events/landmarks/PNG and rawRGBA hashes. Atlas uses paste, not alpha composition, preserving partially transparent pixels exactly. `export_ora(project,frame_id,path)` creates standard layer PNGs/stack.xml/mergedimage.png, deterministicZIP timestamps and embedded original project/bindings. `import_ora(path)` reopens layers losslessly, incorporates external per-pixel RGBA edits, rejects locked changes, resizing/reordering/transforms/blend modes, and preserves animation metadata. If an externally edited selected cel was shared by other frames, import forks that cel to preserve other frames. Embedded metadata is required; tools that discard it need a separate explicit metadata-restoration adapter. This limitation is reported rather than silently inventing timing/pivots.

CLI examples:

```sh
python3 scripts/sprite_edit.py validate project.json
python3 scripts/sprite_edit.py apply project.json transaction.json --output live.json --receipt receipt.json
python3 scripts/sprite_edit.py export live.json exports
python3 scripts/sprite_edit.py ora-export live.json frame0 frame0.ora
python3 scripts/sprite_edit.py ora-import frame0.ora reopened.json
python3 scripts/sprite_edit.py candidate live.json cel0 candidate.png mask.json candidate-tx.json
python3 scripts/sprite_edit.py replay project.json journal.json replayed.json
python3 -m unittest discover -s tests -v
```

CLI validates before writing and each JSON output uses a temporary file plus atomic replacement. The project is authoritative; receipt/project pair is not a crash-atomic multi-file database transaction. The library commits no files. Tests measure actual RGBA/index coordinates and compare exported pixels, not just hash roundtrips. Native worker separately verifies these operations against independent real-game fixture pixels/coordinates/order/clock. Passing mechanics does not approve silhouette, attachment, readability or intended-scale temporal motion.

Actual layered LibreSprite exchange is supported through a bounded RGBA `.aseprite` adapter following the [official ASE file specification](https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md). Export selects one animation, writes ordered normal layers and compressed full-canvas cels, and creates `.sprite-lab.json` beside it. Import accepts normal full/cropped/linked RGBA cels, reads their actual pixels, adds exact new palette colors, and forks changed frame bindings while preserving untouched project frames. Locked layers reject changes. Resizing, reordered/renamed layers, blend/opacity transforms, groups, changed frame count and changed exported durations reject rather than invent corrections. Native index aliases are preserved when RGBA is unchanged.

ASE durations use differences of rounded cumulative boundaries: `boundary_i=floor(cumulative_ticks_i*1000/fps+0.5)` and `duration_i=boundary_i-boundary_(i-1)`, starting at boundary zero. Holds are not rounded independently. The sidecar records each duration's quantization error and cumulative boundary error, and preserves authoritative original ticks, pivots, landmarks, events, provenance and animations. For example, 72 one-tick poses at 60 Hz total 1200 ms with 16/17 ms holds, rather than 1224 ms from rounding every hold to 17 ms. Timing edits must use explicit core transactions. The adapter's 65,535 dimension/frame/duration bounds come from this exchange format; palette colors remain arbitrary modern RGBA. The selected animation can repeat frame IDs; inconsistent external edits to repeated instances reject. The sidecar is required when reopening a tool-resaved file under another filename.

```bash
python3 scripts/sprite_edit.py ase-export project.json edit.aseprite --animation walk
libresprite -b --list-layers edit.aseprite --save-as edited.aseprite --sheet tool.png --sheet-type horizontal --data tool.json --format json-array
python3 scripts/sprite_edit.py ase-import edited.aseprite imported.json --sidecar edit.aseprite.sprite-lab.json
python3 -m unittest discover -s tests -v
```

LibreSprite 1.3 actually opened/saved/reopened the two-frame test file; both rendered frames, layer names, quantized durations and complete imported project matched. The root study's 12-frame walk with 11 layers also passed actual tool sheet RGBA and exact whole-project reimport; see `libresprite-exchange-proof.json`. These results establish exchange mechanics, not art approval. LibreSprite failed to open ORA in this environment while returning exit status zero; tests therefore require output artifacts and pixel equality, never exit code alone. ORA remains a separate ZIP adapter, without a claim of external application acceptance here.

Exports and diffs validate complete projects once and use an internal trusted renderer. Public `render_frame` still validates. Safe indexed pixel arrays do not need redundant canonical serialization during shape validation; metadata, Unicode and arbitrary provenance still receive canonical validation. Exact opaque/transparent compositor fast paths retain partial-alpha integer arithmetic. On the real 24-frame, 11-layer, 5,406,720-index study: validation 0.302 seconds, complete PNG/atlas/JSON export 2.438 seconds on this WSL machine.

`browser-core-parity.json` records independent Python checks of the browser editor's ten transactions: exact resulting project, receipt and all actual browser RGBA frame arrays, plus mouse-edit journal replay (52 checks). Calibration fixtures establish mechanics, not visual quality. Public Python objects require actual `int` values for integer fields; decimal-spelled JSON such as `1.0` becomes a Python float and rejects there, while JavaScript parsing loses that lexical distinction. Canonical exports use integer spelling for integer-valued numbers, so files written by these tools do not introduce this edge.

Use `load_json(text)` at portable file boundaries (projects, transactions, masks and journals), or `load_project(text)` to decode and validate together. These normalize finite safe integral decimals such as `1.0`/`1e0` to actual Python integers while retaining fractional FPS. Unsafe integer literals, nonfinite JSON values and fractional pixel indices reject. The CLI uses this loader consistently; direct Python object APIs remain strictly typed. Tests prove decimal-spelled and integer-spelled input produce identical hashes, operations, receipts and pixels.
