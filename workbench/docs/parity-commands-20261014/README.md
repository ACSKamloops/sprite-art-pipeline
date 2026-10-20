# Recovered editor shape footprints, not a fabricated command parser

This pass adds four **executed original editor methods**: ellipse outline/fill
and rounded-rectangle outline/fill. They can paint an existing indexed cel via
the existing guarded history. It does **not** recover the hosted pixel-art
workbench argv parser, nested draw grammar, seven edit operations, or nine
documented hosted primitive implementations.

The retained catalog still records28 commands:13 partial local routes and15
pending. None of their `vendor_handler_recovered`/conformance flags is changed.
This is a source-faithful editor primitive with separate local input plumbing,
not evidence of a closed hosted command or whole-feature parity.

## Exact source and its actual role

Runtime reads the existing packaged unchanged
`vendor/host_selection/DrawingAlgos.gd`, SHA256
`6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9`.
Original lines155–326, UTF-8 bytes `[5077,9151)`, form a4074-byte span, SHA256
`23d4a11762e56134fed1e63c456b998b805eda42dc390d2cd1b5c2b55e36f930`.
Both hashes are checked before execution; the span is appended unchanged to
a minimal Godot host. Only the authored caller uses tab indentation matching
the source. There is no Python implementation of the geometry or fallback.

The source came from retained PCK
`ebf9812ea474bddb84faa22183a1ec0178983cdc285674a4d0177c606e8a4a3f`.
The current public recovered PCK
`398455603cf39fc993c59fca3265ed180e246005da631e918018d0c44d497e4f`
has the **same complete DrawingAlgos bytes**. Current shipped callers confirm
the role: `EllipseTool.gd:5,9` calls ellipse fill/outline,
`RectangleTool.gd:7,11` calls rounded-rectangle fill/outline, and
`EllipseSelect.gd:71,135` uses the ellipse functions for selection. Their exact
file pins are in [SOURCE-LEDGER.json](SOURCE-LEDGER.json).
GDRE-recovered source execution is not compiled-bytecode equivalence.

## Available local API

```python
from sprite_workbench import parity_commands

command = {"method": "ellipse-filled", "pos": [3, 2],
           "size": [5, 4], "thickness": 1}
original = parity_commands.evaluate([command])
painted = parity_commands.paint_primitive(
    store, history_id, "cel-0", command, palette_index=2)
```

`describe()` reports source pins and scope. `evaluate()` accepts1..16 commands
and returns **original ordered points including duplicates**, counts, hashes
and actual engine version. Methods map directly to the four source functions;
`pos`/`size` are integer pairs. Rounded rectangles require `radius`;
ellipse-filled and rounded-rect-outline require `thickness`. These explicit
fields and bounded validation are our local contract, not original argv.

Limits: side1..128, positions±4096, radius0..128, thickness1..16, aggregate
grown area32768. Original arithmetic runs in Godot with Linux prlimit:
30s wall,20s CPU,4GiB address space,128descriptors,8MiB file ceiling and4MiB
result ceiling. Missing engine/source drift/timeout refuses; no guessed math.

`paint_primitive()` rejects locked layers, unknown indices and any returned
point outside the canvas. It applies a `candidate_patch` with exact project
and cel guards through `construction.edit_history`; palette alpha, outside
indices, shared cels and undo/redo remain under that existing transaction
system. It does not infer clipping, palette insertion, opacity or brush-stroke
semantics. The returned footprint artifact is separate evidence; registry/UI
wiring and a new portable-closure rule are not included in this commit.

## Direct source oracle and meaningful quirks

[FOOTPRINT-ORACLE.json](FOOTPRINT-ORACLE.json) freezes12 direct literal Godot
calls made by an independent tiny host against the unchanged span, without
the JSON dispatch wrapper. The runtime wrapper returns every point in exactly
that order on Godot4.7.2-stable official. Among the observed source behaviors:

- A1×1 ellipse outline returns four identical points.
- The tested1×7 ellipse outline contains five unique pixels; it is not locally
  repaired to an intuitive seven-pixel vertical line.
- Radius0 rounded-rectangle outlines ignore thickness and duplicate bottom
  corner points. The1- and3-thickness test outputs are identical.
- Filled5×5 ellipse with thickness3 expands the source footprint and returns
  37unique pixels. This is not reinterpreted as an ordinary internal stroke.

`python -m pytest -q tests/test_parity_commands.py`: **16 passed**. Tests compare
all direct-source points and exercise actual guarded paint, unchanged outside
indices/partial alpha/aliases/shared cels, real undo/redo, cold Store reopen,
out-of-canvas no-publication, locked-target refusal and source/resource guards.
The oracle is finite binding/regression evidence, not exhaustive malformed
input conformance across all Godot versions.

## What the grammar revisit actually established

The112 Lua files in the retained personal extension ZIP contain no literal
`argv`, `draw_commands` or `argparse` in the bounded screen. Three selected
routing/image-placement files were retained separately under
`/home/astra/artifacts/pixellab-parity-commands-20261014`; `package.json` and
credentials were excluded. Absence of those literals does not prove universal
parser absence or rule out dynamic names.

REA inspected the retained shipped editor JS tree: one16,612-byte file,
4379AST nodes, no parse failures, partial application coverage and837 semantic
unknowns. The producer exceeded transport response size; it was not rerun.
[Summary](REA-EDITOR-SUMMARY.json) and [exact argv trace](REA-ARGV-TRACE.json)
retain Evidence IDs and limits. The trace has no matching literal seed within
that partial graph. Static graph observations do not demonstrate execution or
an unavailable server's code.

Next genuine source pieces include the editor tools' stroke/brush application
and clipping/selection semantics, which must be recovered and replayed with
their own host contracts. The private hosted nested parser and command-level
rollback/validation cannot be filled in from these source primitives. No
provider calls, credential access, paid work, source/research mutation or shared
registry edits occurred.
