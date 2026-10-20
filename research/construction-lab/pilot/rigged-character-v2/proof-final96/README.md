# Final V2 producer checkpoint

Producer source: `bd766e0`. Current derived pack: `../generated/`, 96 bindings and 6,000 actual Godot GPU frames. The four authoritative art/engine inputs are rig.gd, rig_side.gd, design.json and clips.json; the manifest also binds bake.gd and build_exports.py. Source remains editable, and a changed input makes the pack stale.

The delivered scope is 48 clip-declared inspection bindings plus 48 persistent-equipment bindings: idle/walk/run/hurt/knockdown/recover × sword/blaster × four views. Variant names, base_clip and equipment_selection are explicit. Cast and celebration require explicit stow. Native-sized event clocks are authored and unchanged; they are not independently discovered gameplay collision windows.

Reproduce locally from the repository root using a fresh directory:

```
python pilot/rigged-character-v2/build_exports.py --private-output "$PWD/pilot/rigged-character-v2/private-reproduce96"
godot --headless --path pilot/rigged-character-v2 --script res://verify_api.gd -- "$PWD/pilot/rigged-character-v2/private-reproduce96/api-validation.json"
xvfb-run -a godot --path pilot/rigged-character-v2 --audio-driver Dummy --rendering-method gl_compatibility --script res://verify_render.gd
```

The last command rejects an existing GPU audit rather than overwriting it. Renderer equivalence is scoped to Godot4.7.2 GL Compatibility / Mesa llvmpipe at the same fixed192×192 origin with nearest sampling. GIFs quantize60Hz to10ms intervals; SpriteFrames retains exact1tick holds.

Evidence:

- `export-validation.json`:6,391 lossless atlas/clock/edge checks, all pass.
- `gpu-render-validation.json`:6,000 actual SpriteFrames atlas frames plus384 source-render samples match exact RGBA. Real SpriteFrames save/reopen/region/hold checks pass.
- `api-validation.json`:9,696 source-pose samples;9,704 checks pass, including atomic incompatible-action refusal, persistent gear, unchanged foot/world/contact metadata and zero target-reach error.
- `ground-actions-validation.json`:2,160 full-sprite hurt/fall/recovery images across all views/gear have no opaque pixel at or below row170.
- `before-ground-failures.json`:the first96pack had236 sword-guard ground failures. Before/after actual rendered2× images are retained here. Only eight intended sword fall/recovery bindings changed;88 other bindings remain byte-identical in RGBA.
- `unknown-selection.log`:unknown exporter selection is rejected with exit2.

`receipt.json` lists exact hashes and the affected-binding comparison. The first bad pack and its exact hash-matched input snapshot remain under `../private-final96-first/`; the complete repaired bake remains under `../private-final96-repaired/`.

These mechanical checks do not approve artistic quality, anatomy or moving-world raster contact. The independent reviewer must inspect every dense adjacent/boundary pair and actual timed playback. Front/back are authored orthographic views; left is explicitly mirrored from right. The world consumer owns the independent contact/camera proof.
