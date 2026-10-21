# Standalone Godot inspector

This extends the bank packaging task with a native inspector, not a new game.
Source is `../tools/build-rpg-preview.py` and `../tools/rpg-preview/`.
Root owns integration. No artwork or source delivery manifest was changed.

```sh
python3 research/pixelengine-imagen/tools/build-rpg-preview.py \
  --package /home/astra/artifacts/hero-rpg-expansion-20261021/delivery/current \
  --output /absolute/fresh-preview --godot godot --check
godot --path /absolute/fresh-preview
```

The builder requires exactly the selected 8 directions × 6 actions. It validates
source manifests/PNG hashes, copies only selected80px PNGs unchanged, and creates
a portable Godot project. Runtime assets use only relative `res://` paths;
original absolute source-package paths remain provenance, not dependencies.
The original selected SE walk is mandatory. Experiments never silently replace it.

Default controls: arrows/WASD move and face in eight directions; J punch, K cast,
L dodge, H hurt; Space toggles idle/in-place walk. Buttons and a direction selector
offer the same routes. Right mouse sets an independent aim direction; it changes
neither body facing nor attack art. Playback speed can be changed in the UI.
The fixed80px stage uses ground pivot40,72, nearest texture filtering and integer
4x enlargement. Preview movement has no collision/contact interpretation.

`bank.json` explicitly configures completion routes:

```json
{
  "completion_return": {"punch":"punch_ready","cast":"cast_ready","hurt":"idle","dodge":"idle"},
  "ready_states": {
    "punch_ready":{"source_action":"punch","frame":0},
    "cast_ready":{"source_action":"cast","frame":0}
  }
}
```

Ready states hold existing action paint; they add no claimed animation or neutral
transition. Cast never returns through punch frame0. Hurt/dodge return to idle0.
The selected source clips already finish on those exact pixels. Guard/gather to
relaxed idle remains an art-transition gap. Hand/grip/release anchors remain
pending; authored hit/release events are shown as metadata and have no damage,
weapon, projectile or VFX behavior. `--config` can supply an explicit alternative
full config; its source/return endpoints must satisfy the validator.

One common tick rate is the LCM of every rational hold denominator. SpriteFrames
stores that speed and exact integer frame weights. A single manual controller
clock drives the paused AnimatedSprite2D, retains fractional carry across return
to idle, and reports current/finished state. Direct PNG decoding avoids texture
importer alpha-border repair; the saved embedded SpriteFrames resource is reloaded
and every RGBA byte, duration, loop and speed is compared with selected sources.

Generated project commands can be run independently:

```sh
godot --headless --path /absolute/preview --script res://build_resources.gd
godot --headless --path /absolute/preview --script res://validate.gd
```

Each invoked check has a45-second timeout. Reports are
`RESOURCE-VALIDATION.json`, `RUNTIME-VALIDATION.json`, `ENGINE-INVOCATIONS.json`
and `BUILD-RECEIPT.json`. The receipt binds builder/template/bank/source hashes;
the source delivery is checked unchanged after the build. Initialization never
depends on an `assert` expression.

## Actual verification

Installed executable: `/home/astra/.local/bin/godot`.
Actual version: `4.7.2.stable.official.ed1daf0bf`.
Final artifact: `/home/astra/artifacts/hero-rpg-expansion-20261021/engine-preview/validated-final/`.
The input was the actual immutable `delivery/current/`, not the synthetic fixture.

- All 48 selected animations/223 exposures decoded, saved and reloaded exactly.
- Rational holds use one400Hz clock; loops/speeds/hold sums match.
- 316 checks passed: 32 one-shot action/view completions, all 8 movement directions,
  actual Godot dispatch for 8 physical arrow combinations and 4 action keys, Space
  toggle/release, independent aim, original SE selection and pending anchors.
- All 32 one-shot last-frame pixels equal the configured ready/idle return pixels.
- Native inspector also rendered and captured successfully through Mesa llvmpipe
  (software OpenGL4.5) at1100×760. Capture:
  `engine-preview/current/INSPECTOR.png`; the initial native launch reported only
  an unsupported V-Sync-setting warning. This is software-renderer visibility,
  not hardware-GPU or whole-timeline contact evidence.

`engine-preview/fixture-package` and `fixture-preview-v2` are clearly synthetic
preflight data. The first `fixture-preview` retains the diagnosed GDScript `ready`
property-name collision; it was fixed before actual-package testing. These are
bounded task evidence, not production art. Earlier `engine-preview/current`
preserves the first actual-package pass/capture; `validated` retains the next pass,
and `validated-final` is the final build after mouse-aim sector quantization.

No engine/browser export, game combat, collision, root-motion/sole contact or human
animation-quality approval is claimed. Static idle exposures do not claim breathing.
No runtime process is left running. The clean worktree stays owned by root until
its authored commit is integrated, then can be removed through normal worktree
cleanup; recover source from branch `codex/rpg-pack`.
