# Portable licensed model → modern sprites example

This is a tested adapter for the included Quaternius CC0 Ranger, not a universal autorigger. Original model/UV textures/license, authored Walk, fixed160px camera-relative lighting and source-attached facial descriptor are included. Linux Blender4.5.9LTS with Cycles and Python/Pillow were tested; Godot4.7.2 Compatibility was tested separately. Use another character only after adapting its actual mesh/material/action/bone mappings and reviewing a small pilot.

Copy this entire folder to a fresh work area; preserve original inputs. Set `BLENDER_PATH` to your Blender executable. The renderer uses8 CPU threads and refuses an existing destination.

```sh
"$BLENDER_PATH" --background --python render_walk_game_light.py
python make_preview.py candidate-walk-bow160-game-light-v11
"$BLENDER_PATH" --background candidate-walk-bow160-game-light-v11/ranger-walk-render.blend --python verify_game_light_reopen.py
"$BLENDER_PATH" --background candidate-walk-bow160-game-light-v11/ranger-walk-render.blend --python export_game_light_landmarks.py
python export_atlases.py candidate-walk-bow160-game-light-v11/manifest.json portable-clips
```

The last command creates four lossless atlases and a manifest for the animation skill's existing `scripts/animation_assets.py` and `assets/build_godot.gd`. Its exact clock is5/48 seconds per key (twelve keys,1.25seconds); it does not round6.25 simulation ticks to6. Model-fixture JSON and portable atlas JSON are different contracts. The bridge verifies all48 original encodedPNG hashes and decoded atlas cells before declaring them identical. The pivot is projected world origin, not a certified planted sole.

Validate portable clips with the installed animation helper. Copy `build_godot.gd` into a fresh Godot project containing `clips.json` and the four atlases, import textures, then run the script to create/reopen SpriteFrames. The standalone local lab's `pilot/model-godot` supplies the tested soft-alpha renderer/player; this example does not contain a complete game.

## Reversible fine edit

The included four-operation patch changes only the source eye/brow colors/radii on known face UVs. It checks exact renderer, descriptor and field preconditions, writes atomically and restores exact bytes. A second apply rejects as stale. To create another candidate without overwriting the original:

```sh
python apply_edit.py apply
"$BLENDER_PATH" --background --python render_walk_game_light.py -- edited-output
python apply_edit.py undo
```

Do not run the default render destination a second time; it deliberately refuses to replace baseline exports. The shared lab independently proved this edit at sourceframes0/10/20 through all four directions, actual edited packed reopening and actual rollback renders. Alpha was unchanged; all differences≥4/255 stayed in the visible face feature domain with2px antialias allowance. Ten remote1–3/255 render/GI differences were reported. This is a bounded editing demonstration; new edits and full cycles require fresh affected-frame/timed review.

`INPUTS.json` binds the example's original source and frozen renderer. A fresh copy of this example was actually rendered again: all48 decodedRGBA frames matched the final lab candidate, all8 reopened loop endpoints matched, and apply/stale-rejection/undo passed. Refer to the lab's current handoff for source-bound independent visual and engine receipts. Technical reproducibility does not approve a different character brief, moving-world foot contact or the other actions.
