# Exported Godot player acceptance

The exported local host player now drives AnimatedSprite2D from one elapsed clock. It does not recover or implement any private PixelLab animation method, infer art events, or certify sprite quality.

## Behavior and boundaries

- `timeline.json` retains the exact rational source manifest. `playback.json` contains the separately checked finite-float projection used by Godot; this is not a claim of exact rational arithmetic inside the engine. SpriteFrames remains independently loadable with second-valued hold weights at speed 1.
- The scene player disables native advancement with `speed_scale=0`, retains native play/pause flags, and selects the frame/progress and per-frame `offset=-pivot` from its elapsed clock. `play()`, `pause()`, `restart()`, `set_rate()` and `advance_seconds()` return whether the request was admitted. Completed finite clips hold the last frame; `play()` does not restart them. Explicit restart resets and starts playback.
- Authored metadata events require an explicit positive FPS and valid `{at_tick,name}` records inside the source clip. Tick zero fires once on initial start and each later play, not on pause/resume. Signals include the original tick/name, projected seconds, play index, absolute elapsed seconds and actual current frame. Simultaneous events retain source order. Invalid event metadata rejects publication instead of silently dropping events.
- A large admitted delta dispatches all crossed events and play boundaries, including multiple loops. Native-compatible `animation_looped`/`animation_finished` signals mark completed plays; `playback_completed` marks final finite completion. Boundary signals precede tick-zero events for the next play. Requests made reentrantly through control methods during dispatch reject; handlers must defer such changes.
- Excessive advancement rejects without state changes. The conservative crossing-work limit is 65,536 and the represented play index must fit the admitted integer range. This is a bounded playback utility, not unlimited event replay. Nonfinite/negative deltas and nonpositive rates reject.
- A fixed Camera2D fits the union of every pivoted full canvas with margin, using integer zoom where possible. It does not follow each moving pivot or hide registration changes. Per-frame pivot offsets and source pixels remain unchanged.

## Executed checks

Command: `python -m pytest -q tests/test_reliable_godot.py tests/test_geometry_flows.py tests/test_geometry_adversarial.py -k 'godot or Godot or invalid_exported'`

Result: **13 passed, 23 deselected in 19.84 seconds**, including 9 new cases and 4 existing Godot cases. No old test assertions were changed. This is a focused run, not a rerun of the full repository suite.

The three new engine runs import the actual exported project in headless Godot, save and reload SpriteFrames, and compare decoded AtlasTexture RGBA bytes against independently exported PNGs (including nonzero hidden RGB at alpha zero). They exercise play counts 0/infinite, 1 and 2; rational holds; frame-specific pivots; exact hold and third-loop boundaries; simultaneous and per-play authored events; large deltas; over-budget rejection; real timed process playback; pause freeze; rate changes; explicit restart; final completion and last-frame holding. Six negative metadata cases confirm no published output remains after rejection.

The receipt scope is headless resources, decoded textures and timed host-driver behavior. No GPU screenshot, user art approval, gameplay hit inference, unbounded long-duration precision, or private-server implementation parity is claimed. Existing older test receipts call their scope a real AnimatedSprite2D clock; for this implementation that means real timed engine execution of the exported driver with native advancement disabled, not a second native advancing clock.
