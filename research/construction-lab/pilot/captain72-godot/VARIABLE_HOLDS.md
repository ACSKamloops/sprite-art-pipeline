# Variable-hold Captain audition

These are new runner variants. `lab.gd`, `test_runtime.gd`, `test_material.gd` and all their historical receipts remain unchanged. No art approval is inherited.

Input: `--source=/absolute/assembled-candidate` containing `manifest.json`,72 ordered256RGBA frames with `frame`, `file`, `sha256`, positive finite `duration_ms`, and `physical_root:[x,y]`. Root `cycle_ms` must equal the sum of holds (within1e-8ms); root `root_stride:[x,y]` is displacement per cycle. Integer holds are accepted without resampling. Fractional historical holds also work. Every PNG must match its declared SHA.

`lab_holds.gd` creates real SpriteFrames at60fps, with relative duration `duration_ms*60/1000`. Continuous seconds are authoritative; selection uses cumulative hold boundaries, not `floor(seconds*60)`. Step selects the next source-pose boundary. Only scaled machine-roundoff (`1e-12*max(1,absolute_ms)`) is normalized;10ns early probes remain in the previous pose. Pose index and within-hold progress give source phase `(cycle*72+index+progress)/72`, separate from wallclock timing.

Local lab:

```bash
godot --path pilot/captain72-godot --script res://lab_holds.gd -- --source=/absolute/frozen-pack
```

Fresh actual resource/save-reopen/clock/pixel run (use a new output directory):

```bash
xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility --audio-driver Dummy --path pilot/captain72-godot --script res://test_runtime_holds.gd -- --source=/absolute/frozen-pack --output=/absolute/fresh-engine-output
```

Fresh material run:

```bash
xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility --audio-driver Dummy --path pilot/captain72-godot --script res://test_material_holds.gd -- --legs=/absolute/frozen-leg-pack --actor=/absolute/frozen-pack --output=/absolute/fresh-material-output
```

Leg inputs retain the existing registered-design/material contract: exact actor `leg_source_manifest_sha256`, root stride agreement,72 frames, source-attached actual_sole and whole boot RGBA identity, `boot-isolates/{right,left}-NN.png`. It samples two cycles, each source pose at fractions0/.2/.4/.6/.8. Elapsed seconds are obtained from declared holds; physical root interpolates current→next declared pose root, and last→cycle stride. Stance phase remains the original source index/72. Both isolated boots and the full actor receive one shared draw translation. Numeric material acceptance measures actual complete GPU boot image identity, not just an extrema point. Variable timing is not an anatomical or art-quality proof.

Scaffold verification:

```bash
godot --headless --path pilot/captain72-godot --script res://test_hold_clock.gd
```

`proof/variable-hold-clock-scaffold.json` records3,032 actual Godot clock assertions against explicitly synthetic13/21/16ms holds totaling1,200ms: cumulative boundaries, true early/after probes, wraps, source-root interpolation, steps, order/missing/nonfinite/zero/sum negatives and a balanced1ms timing perturbation. This does **not** certify any pending art source, GPU material, final resource playback or final art rating. The three variant GPU scripts were parse-checked only until a final candidate is frozen.
