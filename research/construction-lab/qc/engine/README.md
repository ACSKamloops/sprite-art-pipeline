# Actual Godot timeline QC

Run from this worktree root:

```sh
python qc/engine/run.py
# Refresh declared sources, optionally use a corrected controller:
python qc/engine/run.py --prepare --player-source /absolute/path/native_obj_player.gd
godot --headless --path qc/engine --script rounding_repro.gd
```

`run.py` rejects engine script errors as well as failed checks. Source paths and byte hashes are recorded in `source-bindings.json`. Copied assets make the existing sandbox independently runnable; `--prepare` intentionally requires the declared original sources. Generated import caches are excluded.

## Failing baseline

The stable 100-microsecond-boundary run has 9,881 checks, with 14 failures: one clock failure for every native route. The remaining 9,867 checks pass. This is a failing baseline, not approval. `baseline/stable-*` preserves it before any corrected controller rerun; `baseline/native_obj_player.gd` preserves original controller SHA256 `64808a9645307c978705f45337fd9a357d01ea84145933f1ddb835290854b5e5`.

Original source: `/home/astra/projects/som-sprite-lab-site/native-godot/scripts/native_obj_player.gd`. `_process(delta)` multiplies delta by native FPS and playback speed, then calls `advance_ticks`. Its exact `elapsed_ticks >= duration_ticks` boundary misses an integral target under floating-point rounding. The standalone reproduction advances `4 / 60.098811862348406` seconds at speed 2: actual frame 7 with elapsed 0.999999999999999, versus frame 8/elapsed 0 using `advance_ticks(8)`. Reproduction exits 2 and writes `rounding-repro.json` until corrected.

The first-run receipt is also retained (`baseline/first-run-with-fuzzy-probes.json`). It had 44 additional test failures from probes only 10 microseconds away from AnimationPlayer keys. Those probes were corrected to 100 microseconds, without weakening one-video-tick perturbation detection. It is superseded by the stable baseline.

## What executes

Four saved/reloaded SpriteFrames clips use distinct real AnimatedSprite2D nodes and isolated frame/loop/finish signals. Full frame order, hold timing (25ms process-sampling tolerance), pause/resume, replay and double speed are checked. Real AnimationPlayer discrete tracks use independent source-manifest oracles for complete holds, two cycles where looping, one-shot completion, pause/resume, mid-play speed changes and large low-rate advances. Thirteen deliberate duration/order/clock/event perturbations must all be detected, including a one-native-video-tick event shift.

Fourteen unmodified copied native OBJ controller routes cover charge-1 glove/sword/axe/spear/whip/bow/boomerang/javelin, charge-3 bow, map-loaded Popoi Freeze, transformation inputs, damage recovery, lethal reaction, and Cup of Wishes revival. Every captured video tick checks controller actor/palette/source-clock readback and actual Sprite2D texture, visibility, position, draw order and palette-material properties. Fractional holds, terminal completion, pause/resume, replay, speed changes, low-rate crossing and invalid-delta rejection are checked. The capture route JSON retains original staged setup and native execution provenance.

## Limits

These checks validate engine playback of existing captured routes, not fresh gameplay or every charge level/target/resistance/spell combination. The separate full spell-catalog audit remains separate. Actor and palette dictionaries are scalar readback; Sprite2D property checks are actual engine objects but do not constitute new GPU screenshot comparison. Full-screen backgrounds, color math and hardware OBJ limits are outside this run. Synthetic AnimationPlayer method tracks prove scheduling of declared observed events, not gameplay hit windows or native spell/action VM behavior. Authored clips provide no independent gameplay event/controller contract.

`editor-boundary-report.json` separately records an actual browser API check: one-shot final tick is correct, but Pause at tick 8 followed by Play resets to tick 0. No editor code was changed here. `editor_boundary_check.js` can be rerun with the existing editor browser session and a read-only local editor server.

## Corrected isolated controller

`corrected/native_obj_player.gd` adds only near-integer normalization after accumulating ticks: `abs(elapsed - round(elapsed)) <= 1e-12 * max(1, abs(elapsed))`. This is an explicit numerical tolerance, not a whole tick grace period. At eight accumulated ticks it is 8e-12 ticks; genuine inputs outside that tolerance keep their fractional phase. Inputs inside the bound are intentionally indistinguishable from roundoff. Existing maximum-advance validation remains unchanged.

The corrected byte hash is recorded in current source bindings and both reproduction reports. All 9,881 engine checks pass against it, including all 13 deliberately perturbed fixtures. `roundoff_guard.gd` independently tests just-below-boundary inputs and process-clock early arrival; original failing receipts remain under `baseline/`. Run:

```sh
python qc/engine/run.py --prepare --player-source "$PWD/qc/engine/corrected/native_obj_player.gd"
godot --headless --path qc/engine --script rounding_repro.gd
godot --headless --path qc/engine --script roundoff_guard.gd
```

For the separate editor defect, recommend explicit transport semantics: Play from Pause resumes current tick and retained fractional phase; Replay resets phase/tick and event ledger intentionally; Play after completed one-shot may replay explicitly. Pausing must not discard already-fired events or change the selected final frame. This is a recommendation only: no app/editor source was changed.
