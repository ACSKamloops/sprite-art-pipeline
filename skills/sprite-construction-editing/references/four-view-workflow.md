> This bundled example is a mechanically verified **rejected visual baseline**. The user rejected its anatomy, directions and animation quality. Reproduce its engine tests as engineering examples; do not treat its old prototype art approval as a quality target. Follow the companion animation skill's visual-quality gates for new artwork.

# Four-view rig, export and review workflow

Copy `assets/toolkit` into one isolated work folder. The examples require Python3, Pillow and NumPy, Godot4 with GL Compatibility, and an actual GPU display or Xvfb; Chromium/Playwright is used for actual browser verification. Keep source on the Linux filesystem. Do not copy `.godot`, generated packs, private ROMs or old acceptance receipts into a new source template.

The original Copper Scout example contains 12 body actions and 96 bindings: 48 default-gear inspection clips and 48 equipped idle/walk/run/hurt/knockdown/recover variants. Right is authored, left mirrors it, front/back are authored orthographic planar views. Bake 6000 held 192×192 images at60Hz from continuous contours and rigid parts. This is not weighted texture skinning, independently authored left handedness, or pose blending.

From the copied toolkit root:

```sh
LP_NUM_THREADS=8 python3 pilot/rigged-character-v2/build_exports.py --private-output /absolute/fresh/bake-evidence
python3 pilot/rigged-character-v2/verify_exports.py pilot/rigged-character-v2/generated
xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility --audio-driver Dummy --path pilot/rigged-character-v2 --script res://verify_api.gd -- /absolute/fresh/api.json
xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility --audio-driver Dummy --path pilot/rigged-character-v2 --script res://verify_render.gd
python3 pilot/tools/make_motion_reel.py --help
python3 pilot/tools/serve_local.py --root "$PWD" --port 8144
```

The builder emits `generated/manifest.json`, source-bound PNGs, atlases and real SpriteFrames. GPU verification reads every held atlas frame and four source poses per binding; results are under `generated/gpu-validation`. The final reel helper needs a fresh output directory; the exact PNG player opens at `/pilot/review-player/?pack=../rigged-character-v2/generated/`. The quiet local server supports media byte ranges, required for real seeking. A generic static server without range support reset MP4 seeks to tick0; actual seek-and-play testing caught it. The optional final reel page expects `generated/review/animation-reel.mp4` and `animation-reel-receipt.json`; use the reel helper's output files there and retain its source receipt.

Build a fresh source-bound measured boot/contact cache and launch the four-view game test using [the bundled world runbook](../assets/toolkit/pilot/rigged-character/qc/world-v2/README.md). Its separately tested state, contact, action and negative fixtures are independent of art acceptance. Bind input/output SHA256, actual rendering context, frame clocks, persistent equipment, collision/event rules and observed endpoint frames in every receipt. Cache paths reference immutable source files; copying a cache alone is insufficient.

Use the companion animation skill's adjacent-frame review process. Render every predecessor/current, loop, replay and supported state boundary at fixed full-canvas size. Review every changed comparison; inherit observations only after exact RGBA, complete pose/timing and equipment equality. Test missing/stale evidence rejection. Review actual timed playback at native scale as well as enlarged screenshots, retaining clearly stated coverage. Prototype approval does not imply depth polish, production art or a complete real-game reconstruction.

For precise source paint and complete layered clips, follow [source-paint-and-clip-editing.md](source-paint-and-clip-editing.md). One complete binding per editable project avoids huge browser documents. Keep source edits and baked overrides separate; source edits invalidate dependent bakes/cache/reviews. Preserve failures and previous exports before replacing derived output.
