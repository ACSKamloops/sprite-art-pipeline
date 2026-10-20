# Current local walk pipeline

The current accepted result is a **four-direction modern prerendered bow-carry walk benchmark**, made from the licensed Quaternius Ranger model. It has12 held poses per direction,48 transparent160×160 PNGs and a1.25-second cycle. This proves a coherent, editable and repeatable walk route; it does not complete our original character, all game animations or moving-world foot contact.

[Play the four views together](http://127.0.0.1:8144/pilot/model-walk-audition/) and click **Play**. Pause, previous/next pose, replay, speed, native/2× scale and previous-frame/difference displays are available. `?variant=studio` retains the earlier directional-lighting study; `?variant=guarded` retains the bow-hidden study. Neither replaces the final game-lighting input.

The final source pack is [candidate-walk-bow160-game-light-v11](../model-sprite-quality-v1/candidate-walk-bow160-game-light-v11/manifest.json). Its packed editable [Blender scene](../model-sprite-quality-v1/candidate-walk-bow160-game-light-v11/ranger-walk-render.blend) retains actual geometry, UVs, weights, constraints, source actions, textures and studio settings. Original source and CC0 provenance are in `../model-sprite-quality-v1/source/`. ManifestSHA: `03fa079e0495dd83f81ad6a00d1778f57e4b7effa885c4d5d54498ebd7c226c8`.

## What changed

The rejected contour and painted cutout approaches preserved engineering behavior but lacked convincing anatomy, directional volume and weight. AI pose sheets improved illustration while drifting in ground registration, clothing mass and gait phase. The model route keeps one actual character and motion, renders opposite views with real depth/occlusion and keeps equipment on its actual hand.

We corrected underlit legs, added explicitly authored source UV eye/brow marks, restored the source bone-parented bow to match its carrying arm, recovered the actual24fps source clock and fixed screen-space directional lighting. Key/Fill/Rim now orbit with the camera; their camera-space matrices agree within2.4e-6. Restoring lights from decomposed matrices caused small reopened image differences, so the final verifier restores exact location/Euler/scale properties. That failed study remains separate.

This route needs a real model, rig, UV materials and motion. Blender does not reconstruct those from a single sprite. A custom original character still needs an authored/obtained model or deliberately drawn directional parts and keys.

## Actual verification and visual review

[Primary independent review](../../qc/temporal/model-walk-game-light24-review/final-review.md) freshly inspects every adjacent pose/wrap at1×/2× plus all43 chronological and12 paused browser captures. The [second review](../model-godot/README.md) also examines actual Godot movement screenshots and accepts a local walk benchmark. Both decisions are limited; sparse facial identity, narrow feet and thin back-view bow remain. The old user rejection remains in force for the old art.

`proof-v11/` binds three actual source-clock loops at native and nearest2×. Capture timestamps bound each screenshot before/after; screenshots can cross pose boundaries. AI inspection of chronological screenshots is not continuous video ingestion. `control-checks.json` verifies playback/step/pause/loop/scale and deliberately rejects stale manifests and altered frame bytes.

The standalone [Godot audition](../model-godot/README.md) passed310 checks, including saved/reopened SpriteFrames,96 actual soft-alpha rendering comparisons within1/255 per channel, visible1×/2×/3× display, rational clock, input/negative checks and fixed/follow world-grid presentation. Neutral renderer comparisons exclude the grid. Movement speed is an audition setting; planted contacts and foot slip remain unmeasured.

```sh
godot --rendering-method gl_compatibility --path pilot/model-godot -- --manifest /home/astra/projects/sprite-construction-lab/pilot/model-sprite-quality-v1/candidate-walk-bow160-game-light-v11/manifest.json
```

WASD/arrows move; Space pauses; R replays. UI controls change pose, direction, scale, camera and grid.

## Repeat and refine

[Source render commands](../model-sprite-quality-v1/README.md) retain the exact frozen renderer and originals. `skills/sprite-animation-pipeline/assets/model-walk-example` is a self-contained licensed example. A fresh copied folder actually rendered all48 frames identically and reopened all8 loop endpoints; [receipt](skill-example-reproduction.json). It also passed copied atomic apply/stale-rejection/undo checks.

[Source-attached fine-edit demonstration](../model-sprite-quality-v1/fine-edit-eye-proof/README.md) changes eye/brow color and size once on the known face UVs. Twelve baseline/edited/reopened/rollback samples cover all four views at sourceframes0/10/20. Original textures and rig stay unchanged; no frame is redrawn. Alpha stays unchanged. Visible changes≥4/255 stay within the actual face-feature domain plus2px; ten remote1–3/255 render/GI differences are reported. This editing test is not a newly approved full cycle.

`export_atlases.py` losslessly bridges the model fixture into the existing portable sprite pipeline. [portable-v11/clips.json](portable-v11/clips.json) uses exact5/48-second holds, four atlases and explicit front→down/back→up bindings. All48 cells match original decodedRGBA; the existing validator and real Godot resource builder both pass. The atlas bridge's save/reload result is separate from the dedicated PNG player's full rendering/timing proof.

```sh
python pilot/model-walk-audition/export_atlases.py /absolute/final-pack/manifest.json /absolute/fresh-atlas-output
python skills/sprite-animation-pipeline/scripts/animation_assets.py validate /absolute/fresh-atlas-output/clips.json --report /absolute/validation.json
```

Changed source, pose, material or lighting needs a fresh output and affected-frame/timed review. Do not overwrite baseline exports or inherit an earlier art decision. Next library expansion still requires its own authored anticipation/contact/recovery, timing/events, transitions and quality checks. This pilot remains local; no publishing step is included.
