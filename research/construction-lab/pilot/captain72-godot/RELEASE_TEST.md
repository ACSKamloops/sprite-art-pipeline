# Standalone Captain release integration test

Prepared before a release exists. Parse checking is not a release pass or art acceptance. Historical v18 art/engine/material reports remain unchanged and belong to their frozen input hashes.

The root-owned builder emits a standalone Godot project with `main.tscn`, `preview.gd`, `hold_clock.gd`, `captain-walk.tres`, `sprites/manifest.json` plus72 PNGs, `contact-policy.json`, `approval.json` and `release-files.json`. The resource animation is `combat_ready_walk`; speed60 with per-pose relative duration `duration_ms*.06`. This test expects the actual release scene controls and fixed viewport origin(180,116),960×760 presentation, not the earlier lab's animation name/origin.

Import first, then execute this absolute test script in the standalone project (do not copy historical tests or private PNGs over it):

```bash
godot --headless --path /home/astra/artifacts/space-marine-captain-walk --editor --import
xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility --audio-driver Dummy --path /home/astra/artifacts/space-marine-captain-walk --script /home/astra/projects/sprite-construction-lab-captain-runtime/pilot/captain72-godot/test_release.gd -- --output=/absolute/fresh-release-proof --legs=/absolute/exact-frozen-leg-pack
```

`--legs` is the exact source leg pack, read-only. If omitted, the original local source path in `approval.json` is used when available. The report explicitly records `episode_targets_independently_checked`; a moved portable release without its source leg pack can test hash binding, rendering and control integration, but cannot claim independent reconstruction of the episode target formula. For a final local proof supply the exact pack.

The test checks every release-file ledger hash, actual imported72 frame RGBA/order/relative durations, duration sum, resource save/reopen, a wrong declared PNG hash and1ms resource-duration negative. It instantiates the actual release scene and emits actual button signals for pause/play, restart, next cumulative hold, native/2×, speed, fixed/follow camera and raw/shared-contact policy. It samples all72 held interiors over two cycles, validates the complete-actor draw origin against an independent cumulative-hold/physical-root/policy calculation, and renders8 native/2× × camera × policy contexts. Actual opaque actor pixels are compared with source pixels over the visible moving grid; transparent grid/UI pixels are not compared against the separate uniform GPU fixture.

When source legs are available, targets are recomputed from `rest_sole + stride*(.3-phase_offset+episode)` with ties-away rounding, actor/leg contact flags are cross-checked, and a1pixel target corruption is rejected. One whole-actor translation is required. No per-boot or per-pose artwork fitting is introduced.

Proof output is a new `report.json`, reopened resource and8 actual scene screenshots. Limits: OS mouse input is not simulated (real Button signals are exercised); source alpha compositing/light-dark exhaustive comparison belongs to the separate engine test; finite integration samples are not a replacement for the1440-context material proof; only one combat-ready Walk exists. Passing integration provides no aesthetic rating, no other actions/directions, no full collision/terrain certification and no user visual acceptance.

Scaffold parse command (already passed on Godot4.7.2):

```bash
godot --headless --path pilot/captain72-godot --script res://test_release.gd --check-only
```
