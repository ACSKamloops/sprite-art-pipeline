# Actual decoded VFR export inspection

`inspect_export.py` decodes **every actual frozen MP4 packet** with ffmpeg passthrough (`-fps_mode passthrough`), using actual ffprobe presentation timestamps. No fixed-FPS resampling or PNG-strip surrogate is used. Source/report/video SHA bindings, exact exporter code SHA, timestamp sequence and source PNG copies are required before comparison.

```bash
python pilot/motion-review-harness/inspect_export.py \
  --spec /absolute/frozen-source/audition-moving-root.json \
  --export /absolute/frozen-export \
  --output /absolute/fresh-inspection
```

Default selects all eight variants; `--variants rgba-1x-normal.mp4,silhouette-2x-normal.mp4` chooses exact filenames. Budget: at most8 variants,6,000 decoded packets total,1,024² stage pixels. The decoder streams one frame at a time. NumPy is required for bounded full-canvas comparison. Existing inspection directories are refused.

Actual decoded RGB is compared against the exact declared source scene at the encoded timestamp: source hold, nearest scale, physical root, camera, one shared support translation if declared, grid, silhouette and caption. Codec conversion tolerance is fixed at2RGB levels. All declared render-state coordinates/selected frames are independently recomputed. A matching source/report hash alone cannot approve a stale video.

Outputs: `receipt.json`, per-variant `decoded-observations.jsonl` with actual decoded RGB hashes and errors, and chronological `transitions-NNN.png` sheets. Every actual source-frame transition, initial pose and wrap is included in order across all exported cycles. Sheets resize the **entire original stage** with nearest filtering; they never fit/recenter the actor. Thumbnails are an overview, not the native-pixel detail oracle. The original video and sourceRGBA PNGs remain available for detailed review.

## Meaningful negative regression

```bash
python -m unittest discover -s pilot/motion-review-harness -p test_inspect_export.py
```

This self-contained test makes and actually encodes a small synthetic eight-key clip, verifies a positive full decode, then changes one source image and consistently rebinds its PNG/spec/report hashes and copied PNG. Video bytes and declared video hash remain correct. Decoded pixels must reject the stale video even though timestamps and root state still agree. It does not silently skip absent private artifacts.

## Current bounded results

- Synthetic export: `/home/astra/artifacts/motion-harness-synthetic-decoded-inspection-v1`.
- Producer moving-root export: `/home/astra/artifacts/captain-upright-decoded-inspection-v1`, from read-only `captain-upright-rig-v1/artifacts/audition-v4-dense-moving` and exact source `frozen-v4-dense/audition-moving-root.json`.

All8 producer variants contain2,796 decoded packets. Per variant, all145 source transitions including initial/endpoint and2 wraps are represented in7 chronological sheets. Total56 sheets, approximately13MiB. Colour maximum decoded difference2RGB levels; silhouette1. This validates the encoded scene, not its quality. The receipt has no art verdict and explicitly makes no continuous-video-watching claim.

Earlier initial inspections are preserved with `-initial` suffix; final requested paths bind the current budgeted inspector source. Compact source/report/video/count summaries are committed in `proof/decoded-inspection-summary.json`; large raw packets were streamed rather than stored.

## Optional fixed detail crop

Add `--detail-crop union --detail-scale 1` to retain full-stage sheets and also write native-size detail sheets. `--detail-scale 2` doubles every stage pixel with nearest filtering. There is no shrink-to-fit. Each detail page has at most12 chronological tiles.

The union uses **all observed full actor-canvas placements**, including their declared root/camera travel, then clamps to the stage. One common rectangle applies to every transition and wrap in that variant. It never uses alpha bounds, per-pose fitting or recentering. Automatic geometry asserts every visible actor-canvas intersection is enclosed. Off-stage canvas portions cannot be recovered from the video.

Alternatively `--detail-crop 100,80,500,430` declares a fixed stage-coordinate rectangle `(x0,y0,x1,y1)` with exclusive upper bounds. Explicit omissions are counted in the receipt; a partial explicit crop is not a full-actor view. Out-of-stage or empty rectangles are rejected. Receipt fields `fixed_crop_geometry`, `fixed_crop_integer_scale` and `fixed_crop_sheets` bind the rectangle, method, unclamped union, omission count and every sheet hash. Full-stage `sheets` remain available for world/floor judgment.

A moving actor can make even this common union wide; that preserves travel rather than pretending each pose occupies the same world location. These crops improve pixel visibility and provide no art verdict.
