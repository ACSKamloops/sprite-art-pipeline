# Neutral eight-key motion audition

Accepts arbitrary ordered uniform-canvas RGBA frames. No Captain rig dependency, inherited rating or art-generation code. Requires Python/Pillow and ffmpeg/ffprobe. Art inputs are copied byte-for-byte; only presentation videos/key sheet composite onto the declared neutral background.

```bash
python pilot/motion-review-harness/export_motion.py --spec /absolute/input/spec.json --output /absolute/new-output --loops 3
python pilot/motion-review-harness/serve_review.py --port 8153 --directory /absolute/new-output
```

Open `http://127.0.0.1:8153/`. The local server supports actual byte-range video seeking; it binds loopback only. The eight MP4s cover native/nearest2×, normal/half-speed, colour/silhouette. They retain the same source origin/root/floor/camera throughout. `source-frames/` preserves source PNG bytes; `source-keys.png` is the readable neutral-background sheet. `report.json` binds source/code/spec hashes, exact holds, every encoded timestamp, presentation state and clipping counts. Existing output directories are refused.

Spec:

```json
{
  "schema":"motion-audition/v1",
  "name":"UNRATED whole-body experiment",
  "canvas":[256,256], "stage":[960,760], "origin":[180,116],
  "root_stride":[-60,20], "root_policy":"shared_episode_target",
  "camera":"fixed", "cycle_ms":1200,
  "frames":[
    {"index":0,"file":"frames/00.png","sha256":"ACTUAL_FILE_SHA256",
     "phase_label":"near contact (authored claim)","duration_ms":150,
     "physical_root":[0,0],"support_order":["right","left"],
     "supports":{"right":{"world_target":[106,248],"material_sole":[124,242]}}}
  ]
}
```

The sample is illustrative/incomplete, not a working asset or measured contact claim. Supply all ordered frames and a hold sum matching `cycle_ms`. Paths must remain within the input folder; no per-frame canvas fitting or resizing to different actor proportions is supported. Phase labels are required and must be reviewed rather than trusted.

Policies: `in_place` keeps the actor root static; `physical` interpolates each declared `physical_root` to the next pose, wrapping to `root_stride`; `shared_episode_target` applies **one whole-actor draw root** from the first listed support's `world_target-material_sole+cycle*root_stride`. A frame with no support falls back to physical motion. `camera` is `fixed` or `follow_physical`; grid shifts with the physical camera, independent of visual correction. Inputs must use the same targets/material witnesses as their browser/runtime consumer for a valid comparison. Grid spacing default16; neutral colours configurable via `background`/`grid_color`.

Clock: union of17ms presentation samples and every exact integer pose boundary. Half speed doubles all hold/boundary times. VFR MP4 timestamps are actually inspected with ffprobe against that schedule at1ms timebase. Complete source loops end at the declared duration; one endpoint packet adds1ms to video duration and is recorded explicitly. The codec is lossless YUV444, but RGB/YUV conversion can change decoded channels by up to2LSB; first decoded canvas is measured, not asserted byte-identical RGBA. Exact source PNGs remain available. This is a rendered export harness, not a new GPU/physics/material test.

`REVIEW_PROTOCOL.md` defines the separate human motion review. A synthetic coloured-block fixture validated encoding only; no new sprite art has been reviewed. `test_harness.py` tests invalid source hashes/holds/order and root/clock contracts without manufacturing an art verdict.
