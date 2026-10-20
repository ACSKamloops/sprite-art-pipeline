# Actual CUDA preview benchmark

This is a read-only rendering experiment, not art approval. Both backends load the
same frozen assembled Captain scene (`0a9b4f0926eec5b3ad0a56a2cf0304695392bfb4dcdf282c6733b086e972831d`).
The scripts select the actual RTX 5090 through CUDA for this process only; they do
not save Blender preferences or modify the input scene.

Blender 4.5.9 LTS, native384, 128 samples, seed19, no denoising, six CPU threads.
The resource probe requires at least16GB free GPU memory before starting. This
bounded test used one GPU render process; it is not a saturation benchmark.

| Source | CPU seconds | CUDA seconds |
| --- | ---: | ---: |
| 33 | 3.143 | 6.919 (first initialization) |
| 103 | 2.919 | 0.727 (warm) |

A fresh-process CUDA sequence33/103/33 subsequently took0.755/0.704/0.694seconds.
Times include PNG saving. Approximately4x applies to the measured warm phase;
startup costs and other scenes can differ.

CPU and CUDA are **different renderers**: phase33 differed at285RGBA pixels
(maximum channel error96), phase103 at278 (maximum13), despite nearly identical
whole-figure appearance. Preserve the actual PNGs; do not reuse CPU pixel receipts
for GPU output.

The independent exact-RGBA replay gate **failed**: phase103 differed at one pixel
by1LSB across processes. Phase33 was exact across processes and after revisiting
the timeline. No tolerance was added to make this failed gate pass. GPU output is
useful for faster exploratory motion auditions; current authoritative CPU exports
and exact reopen contracts remain separate. Godot still uses llvmpipe in the
tested environment; this establishes no Godot RTX acceleration.

Reproduce on this machine with new, nonexistent output folders:

```sh
BLENDER='/home/astra/projects/Mech Warrior Test/tools/blender-linux/blender-4.5.9-linux-x64/blender'
"$BLENDER" --background --python-exit-code 7 --python pilot/captain-renderer-benchmark-v1/render_probe.py -- --output /tmp/captain-render-probe
"$BLENDER" --background --python-exit-code 7 --python pilot/captain-renderer-benchmark-v1/verify_gpu_repeat.py -- --output /tmp/captain-render-repeat
python3 pilot/captain-renderer-benchmark-v1/compare_replay.py --original /tmp/captain-render-probe --repeat /tmp/captain-render-repeat --report /tmp/captain-render-repeat-check.json
```

The comparison command returns1 for the demonstrated exact-replay failure.
`evidence/` contains both original receipts, images, CPU/CUDA comparison and the
independent replay report. PNG hashes can differ through metadata: the gate
compares decoded RGBA values directly.
