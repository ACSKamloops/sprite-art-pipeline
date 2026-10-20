# Copper Scout local world sandbox

Original authored character and combat, using the 96-binding final pack (6000 held video-tick images). This is a bounded local pipeline demonstration, not Secret of Mana gameplay or full-game coverage. Source artwork, exported assets, body-only viewing, and combat/controller tests remain separate evidence.

## Build and launch

Godot 4.7.2, GL Compatibility. Generate a new measured cache in the actual renderer context; cached source files must remain available and match their recorded hashes. Four source inputs are `rig.gd`, `rig_side.gd`, `design.json`, and `clips.json` in the V2 source directory.

From `pilot/rigged-character`:

```sh
godot --rendering-method gl_compatibility --path . --script res://world_v2_cache.gd -- \
  --source /absolute/path/pilot/rigged-character-v2 \
  --views right,left,front,back --equipment-variants --output /absolute/fresh-cache

godot --rendering-method gl_compatibility --path . res://world_v2.tscn -- \
  --cache /absolute/fresh-cache/cache.json
```

The recorded Linux tests use `xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility --audio-driver Dummy`, Mesa llvmpipe. This proof does not promise compressed-PNG byte identity or cross-renderer determinism.

Controls: arrows/WASD move, Shift runs; X slash, T thrust, Z shoot, Q charge/release, C cast, B celebrate, H hurt, K knockdown, V recover, Space pause, R replay. UI selects persistent none/sword/blaster equipment, playback speed, nearest 1×/2×/3× scale, and fixed/follow/scroll camera. Equip/stow is permitted in idle/walk/run; mismatched attacks and mid-action equip changes are rejected. Cast and celebration require explicit stow. Armed hurt/fall/recovery uses the matching baked equipment variants; no live fallback swaps equipment.

## Time, rendering, and contact contract

The clock is authored 60 ticks/s; each exported PNG is one held tick. `advance(ticks)` deterministically drives a real AnimatedSprite2D/SpriteFrames resource and separate original combat physics. Near-integer normalization accepts floating machine roundoff only. Pause freezes clock and markers; replay clears projectiles, hits, events, and effect state. Markers retain their original absolute birth tick when a low-rate update skips their displayed frame. Target contact/damage, projectile cleanup, and charge thresholds are independent gameplay rules, not consequences of pose names.

A nonloop action completes after its final hold and hard-cuts to the matching ready idle. Knockdown holds its final pose until recovery. Transitions are explicit phase resets, not artistic blending. A transition's `from_frame` is the last actually presented texture: a large advance can legitimately skip the terminal texture. The endpoint test explicitly renders hurt35, cast71, recover77, and thrust47 before completing the hold; this is distinguished from low-frame-rate skipped-endpoint evidence.

Physical XY motion stays continuous and independent of whole-sprite raster compensation. Contact uses separately rendered front/rear boot pixels in each view; depth movement uses planar XY contact, not the side ground row. One global actor translation locks a designated contacting boot; it never moves feet independently. The visual camera is quantized before integer scaling. Two-cycle, five-fraction-per-tick GPU stance checks retain the 0.5 native-pixel episode peak-to-peak gate.

## Reproduce bounded tests

Each output directory must be fresh. Run each script with the same `--cache` and a distinct absolute `--output`:

```sh
godot --rendering-method gl_compatibility --path . --script res://test_world_v2.gd -- --cache /absolute/cache/cache.json --output /absolute/contact-proof
godot --rendering-method gl_compatibility --path . --script res://test_world_v2_actions.gd -- --cache /absolute/cache/cache.json --output /absolute/actions-proof
godot --rendering-method gl_compatibility --path . --script res://test_world_v2_transitions.gd -- --cache /absolute/cache/cache.json --output /absolute/state-proof
godot --rendering-method gl_compatibility --path . --script res://test_world_v2_negatives.gd -- --cache /absolute/cache/cache.json --output /absolute/negative-proof
```

The negative-proof directory must be a sibling of the measured cache directory; its JSON mutations rebase relative paths to the immutable original PNGs. Its seven adversarial mutations test source binding, clock, duration, tick order, sole coordinates, root motion and event timing. This is a bounded trusted-asset audit, not comprehensive hostile JSON validation.

`delivery.json` binds the final source/cache/manifest/controller and report hashes. Raw GPU images, all held-tick observations, transition/event ledgers, and previous failed or superseded runs remain in the named private artifact directories. Historical proofs are not restamped after source edits. Mechanical pass counts do not grant production art approval.
