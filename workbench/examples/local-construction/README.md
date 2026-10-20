# Local construction example

This tiny two-layer marker tests editable cels, a locked registration layer, shared-cel edits, unequal holds and an animation event. It is diagnostic input, not proposed game art.

Copy this directory to an absent working directory before running; exports never overwrite an existing output:

```bash
cp -a examples/local-construction runs/my-construction-example
.venv/bin/sprite-workbench --workspace runs/my-construction-store run runs/my-construction-example/plan.json
```

The response contains immutable project/history IDs and native exchange paths. `output/playback` contains a complete editable bundle, review player and Godot animation. `output/editor` contains a layered RGBA `.aseprite` file and its required metadata sidecar. Keep the original Store for the first native import: the earlier playback bundle does not contain the binding created by the later native export. After importing, render with `import_provenance` and export another editable bundle to transfer that binding too.

The plan demonstrates one exact pixel edit affecting both frames that intentionally share `marker-a`. Undo/redo use the returned history ID through the `construct` command or persistent JSON Lines channel. Keep `project` (Store envelope ID) distinct from `project_hash` (editable document precondition).

See [the construction guide](../../docs/construction/README.md) for command grammar, conversion boundaries and native editor import instructions. A flattened source image starts as one editable layer; this workflow does not infer body parts or invent missing poses.
