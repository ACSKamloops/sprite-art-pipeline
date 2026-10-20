# Offline native sprite bake

Reconstructs the accepted EO first30 sprites directly from the retained H3 MP4. The bake does not read EJ or EO outputs. Requires Python3, Pillow, NumPy, `ffmpeg` and `ffprobe`; no models, credentials, network or downloads.

```bash
python scripts/bake_native_sprites.py \
  --video /path/to/retained/native-video.mp4 \
  --recipe recipe.json \
  --output /path/to/FRESH-output
```

The output path must not exist, and its parent must exist. The CLI validates the recipe, source SHA, actual geometry,124 native frame timestamps, positive exact rational holds,24Hz and31/6s duration **before creating output**. Existing files/directories/symlinks are refused. Invalid selection ranges, unknown/stale schema and unsupported processing rules are rejected. A later decoder/runtime failure may leave an incomplete new output; such output has no completed receipt and must not be treated as a finished bake.

The checked recipe exposes the matte thresholds and explicit selection; it does not detect a loop automatically. Processing uses one four-thread bounded RGB24 decode stream and samples the whole768² canvas at source[6*x+3,6*y+3] to128². Hard alpha is0 iff G>=90 and G-R>=45 and G-B>=45, else255. All RGB survives, including under alpha0. It retains all124 raw RGB and matte RGBA PNGs with native timestamps, rational holds, array/file hashes and the fixed sourceXY witness.

It explicitly selects source0..29 in native order at1/24s each, marks loop=true and records5/4s duration. On opaque green-dominant pixels only, G becomes max(R,B). The3525 edits retain red/blue/alpha and all hidden RGBA. Each journal entry records source128 coordinates, source768 sample coordinates and exact before/after RGBA; actual replay and undo run during baking. No per-frame fit, reordering, changed canvas, timing interpolation or seamless-loop claim occurs.

Output entry points are `manifest.json` (selected30), `all-native-manifest.json` (all124), `recipe.json`, `actual-source.json`, `source-xy.npy`, `despill-journal.json` and `receipt.json`. All metadata paths are relative, with source identity carried by filename and SHA. The tool writes only within its supplied fresh output. `actual-output/` is the completed tested run retained here.

`VERIFICATION.json` records an independent comparison against retained references: all124 raw RGB and matte fullRGBA match EJ; all124 matte PNG bytes match; all30 selected fullRGBA **and PNG bytes** match EO; all native/selected PTS and holds match. The3525 journal changes replay and undo exactly. Six rejection tests preserve an existing sentinel or leave output absent: existing output, bad source SHA, invalid selection range, stale schema, wrong geometry and wrong timing.

To repeat that independent check when references are available:

```bash
python scripts/verify_against_retained.py \
  --video /path/to/retained/native-video.mp4 --tool-root . \
  --ej /path/to/retained/EJ-folder --eo /path/to/retained/EO-despill30-folder
```

The verifier expects the tested bake in `actual-output/`; it only reads the video/references and writes verification evidence inside `--tool-root`. Production baking needs none of those reference folders. Source/code/recipe pins and tested tool versions are retained in `SOURCE-PINS.json`, `ENVIRONMENT.json`, and `FREEZE.json`. Exact decoded reproduction was verified on this environment; no cross-version decoder equivalence is claimed. Verify the frozen packet with `sha256sum -c SHA256SUMS`.
