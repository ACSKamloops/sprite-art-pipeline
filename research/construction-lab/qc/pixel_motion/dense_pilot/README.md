# Dense walking pilot — changes requested

This is the unchanged cutout rig/source parts sampled at **60 phases**, each held for **one tick at 60 FPS**. It does not redraw knees, repair materials, change anatomy or approve the art. The layered indexed project is **19,218,480 bytes** with 455 shared cels, below the 25 MB project bound. Source colors and parts are preserved.

Actual Godot 4.7.2 OpenGL framebuffer readback (Mesa llvmpipe software device, not a hardware GPU claim) compares three moving-world models at five fractional samples per tick over the full 60-tick cycle and exact wrap:

| Model | Analytic full-hold slip bound | Actual rendered stance/within-hold maximum | 0.5 px rule |
|---|---:|---:|---|
| Original 12 poses × 5 ticks, cached raster frames | 4 px | 4 px | Fails |
| Dense 60 poses × 1 tick, cached raster frames | 0.8 px | 1 px | Fails |
| Continuously evaluated original rig, no held raster frames | Not a held-frame model | 0 px | Contact/slip rule satisfied |

Both front and rear boots stay on opaque row139 (ground boundary140) in every measured stance. Actual raster snapping and the continuous-root analytic bound are separate measurements: denser frames reduce slipping but **do not satisfy the unchanged threshold**. The continuous rig meets this contact rule over the captured times; that does not accept its anatomy/material seams or prove a different engine's policy. Five finite fractional samples do not prove every possible real-valued timestamp. Full half-open hold bounds are analytic; actual pixel maxima refer to captured surfaces.

`comparison-report.json` contains exact sampled tick/phase/root positions, rendered boot centers, source/script/project hashes, GPU raw RGBA hashes, model-specific findings and scope. `gpu-observations.json` is the original renderer ledger; `renders/<raw-rgba-sha256>.png` deduplicates identical native readbacks. All 60 independent layered composites match native draw surfaces; all 12 phases shared with the original baseline match exactly. Source-part RGBA membership is verified; fully transparent pixels are canonical zero.

Inspect `gpu-foot-contact-6x.png` (captured fractional-tick boot displacement), `gpu-contact-comparison.png` and `old_12_hold5.gif`, `dense_60_hold1.gif`, `continuous_rig.gif`. GIFs deliberately show one source tick per100ms (6× slow), including wrap. Analytic/native timing remains60 FPS in JSON. `diagnostics/` holds source-composition/contact checks against the dense GPU captures; its analytic contact rules also retain the original 0.01 px frame-boundary drift and0.5px within-hold limits. Dense local raster quantization can violate the boundary drift rule as well.

Reproduce from repository root:

```bash
godot --headless --editor --import --path qc/pixel_motion/dense_pilot
xvfb-run -a godot --path qc/pixel_motion/dense_pilot --script render_dense.gd --rendering-method gl_compatibility --audio-driver Dummy
python3 qc/pixel_motion/dense_pilot/analyse.py
python3 -m unittest qc.pixel_motion.dense_pilot.test_dense_pilot -v
```

The capture project intentionally reads newly generated PNGs from disk to upload exact source RGBA textures. It is a local verification project, not a Web-export player; runtime textures/exports need their own resource packaging. The first retained capture log records an unused audio driver falling back to Dummy; draw surfaces and capture completeness are validated independently. Copied inputs retain their original hashes in `inputs.json`.

Status remains **changes_requested**. Required next decisions: use truly continuous procedural placement or explicitly choose a tolerated raster-slip policy; review unchanged knees/materials at native scale over the full walk; verify target-engine root/camera snapping and playback. Neither adding frames nor meeting a contact rule constitutes art approval.
