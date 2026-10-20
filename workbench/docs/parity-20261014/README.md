# Recovered client operations — v0.9.0

Open **[Parity Lab](http://127.0.0.1:8874/#parity)** to upload a PNG, inspect the
supplied raster, run original palette/pixel methods, evaluate a source footprint
or paint an existing Workspace cel through guarded history. Every operation is
explicit and returns retained source/result IDs. Palette/shape implementations
are original shipped/recovered code; the host controls, admission bounds,
indexed history and receipts are local adapters. No provider is called.

**Full PixelLab parity is unresolved.** Current progress establishes selected
client subflows and exact finite outputs. It does not recover private weights,
automatic animation alpha/sampling, high-K palette construction, positive-strength
dither, hosted argv/nested grammar or accepted game art. Read the independent
[scope/gaps](PARITY-SCOPE-AND-GAPS.md), [red-team accounting](PARITY-RED-TEAM.md),
[pixel review](PIXELS-ADVERSARIAL.md), [palette review](PALETTE-ADVERSARIAL.md)
and [channels review](CHANNELS-ADVERSARIAL.md). The [latest verification](../LATEST-VERIFICATION.md)
contains final test, package, browser and installed-source identities.

## Use the same methods in every channel

CLI: `sprite-workbench --workspace STORE parity METHOD REQUEST.json`.
JSONL/HTTP: `local.parity.METHOD` with the same JSON body. Local plans:
`{"id":"step","action":"parity","method":"METHOD","request":{...}}`.
The catalog response supplies exact JSON Schemas and pinned source boundaries.

| Method | Request | Result |
| --- | --- | --- |
| `catalog` | `{}` | Exact schemas, source pins, operation boundaries and current public API delta. |
| `palette` | `{"raster":"ID"}` | Original palette-image importer result: `colors`, `palette_rgba`, `accepted`, original `warning`/`error`, receipt. Supplied canvas-equivalent RGBA; partial-alpha browser PNG decoding is separate. |
| `pixels` | `{"operation":"OP","request":{...}}` | Original Godot method output, immutable receipt and output raster/raw bytes where applicable. |
| `footprints` | `{"commands":[COMMAND]}` | Original ordered points, duplicates/quirks, source pins and footprint ID. |
| `paint` | `{"history":"ID","cel_id":"CEL","command":COMMAND,"palette_index":1}` | Existing guarded indexed paint, updated history/project, source footprint bound to exact journal index. |
| `to_sequence` | `{"receipt":"ID","duration":[1,1]}` | Explicit one-frame still with an authored hold; original method is re-executed before promotion. Sources stay in portable closure. |

`pixels` operations and inner requests:

```json
{"operation":"serialize","request":{"raster":"ID"}}
{"operation":"transparency","request":{"raster":"ID"}}
{"operation":"reference_palette","request":{"raster":"ID"}}
{"operation":"mask","request":{"mask":"ID","art":"ID","fill_background":false,"inpaint_empty_image":false}}
{"operation":"decode","request":{"media":"RAW_OR_PNG_BLOB_ID","width":32,"height":32}}
{"operation":"place","request":{"source":"ID","destination":"ID","origin":[0,0],"extent":[32,32],"preserve_mask":"OPTIONAL_ID"}}
```

Omit `preserve_mask` to copy all source pixels; omit `extent` to use the source
size. PNG decoding honors actual PNG dimensions; raw decoding uses the declared
dimensions. The six operation bodies, admission bounds, host stubs and all three
mask formats are documented in [original pixel methods](ORIGINAL-PIXEL-METHODS.md).
An opaque black/white inpainting mask is **not** a placement alpha mask.

The four source shape commands have exact controls and no inferred defaults:

```json
{"method":"ellipse-outline","pos":[3,2],"size":[5,4]}
{"method":"ellipse-filled","pos":[3,2],"size":[5,4],"thickness":1}
{"method":"rounded-rect-outline","pos":[3,2],"size":[5,4],"radius":1,"thickness":1}
{"method":"rounded-rect-filled","pos":[3,2],"size":[5,4],"radius":1}
```

Painting refuses out-of-canvas points and locked cels, keeps existing palette
alpha and shared-cel references, and retains its original ordered footprint
through subsequent edits/branching/undo/redo/export. Cold history verification
re-runs the source command before trusting its geometry. See the
[source footprint oracle](../parity-commands-20261014/README.md).

## Actual PixelLab reference match

The packaged original `image_to_base64` method exactly matches decoded RGBA
from slot0 of all three retained matched PixelLab jobs: walk, slash and
margin-slash. Raw source/reference differences were 49, 49 and 30 alpha-zero
hidden-RGB pixels. The original method normalizes those to zero and preserves
all visible/partial-alpha pixels. This is an exact finite **reference transport**
match, not generated-frame or animation-conversion parity. Reproducible input,
output and receipt hashes are in
`/home/astra/artifacts/pixellab-parity-20261014/MATCHED-REFERENCE-PARITY.json`.

The [public contract refresh](PUBLIC-CONTRACT-DELTA.md) matches the already
retained earlier analysis snapshot. It exposes the known 112-operation current
document beside the historical 111-public/101-MCP registry without modifying
original captures. The [catalog pin receipt](CATALOG-PIN-UPDATE.json) records the
single intentional current pipeline-source hash update and its preserved original.
