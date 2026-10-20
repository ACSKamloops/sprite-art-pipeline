# Godot and browser evidence

Use AnimatedSprite2D/SpriteFrames for frame art. Add AnimationPlayer for methods/audio/parallel tracks and AnimationTree when transitions warrant it. State rules and bindings remain explicit. AtlasTexture regions sample declared cells; nearest filtering suits pixel art, not every smooth raster style.

Copy assets/build_godot.gd into a project with clips.json and sheets. Validate the JSON first:

```sh
godot --headless --path /project --editor --import
godot --headless --path /project --script build_godot.gd
```

The importer saves resources/<actor>.tres, reloads and checks counts, durations, loops and regions. Speed is source video_fps; weights are duration_video_frames. Absolute hold=weight/(fps*playing_speed); don't divide twice.

assets/clip_driver.gd uses paused AnimatedSprite2D driven by an explicit simulation clock to deliver every crossed event. This optional fixture demonstrates idle/walk/attack, movement, locking, interruption and timestamps. Choose one clock; adapt collision shapes, extra states and game rules explicitly.

Test saved textures/metadata, actual rendered progression, preserved walking phase, one-shot cleanup/replay, held input, interruption, speed changes, crossed events and invalid commands. Manually driven state snapshots alone can't prove correct texture sampling.

Web export requires matching templates. Single-thread export suits simple hosting without cross-origin isolation. Retain JavaScriptBridge callbacks and use serialized commands/request IDs plus engine read-back. Test JSON floats even for integral-looking values.

Drive the actual browser engine through UI and programmatic controls; inspect errors and desktop/mobile captures. Duplicated HTML-side animation state can conceal a Godot failure. Native WebMCP support and the tested command bridge are separate.

Use the chosen hosting skill when publishing is requested. Keep local ROMs/savestates/credentials outside the public bundle. Native hosting success establishes deployment; local browser QA establishes prepublication behavior.

Primary docs:

- https://docs.godotengine.org/en/4.7/classes/class_spriteframes.html
- https://docs.godotengine.org/en/4.7/classes/class_animatedsprite2d.html
- https://docs.godotengine.org/en/4.7/classes/class_characterbody2d.html
- https://docs.godotengine.org/en/4.7/classes/class_javascriptbridge.html
- https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html

Release and preview lessons from the exercised authoring/native workbenches:

- Never perform required initialization inside `assert(...)`. Godot release exports remove assert expressions, including function calls. Assign/check the result explicitly, and require engine read-back to report a loaded route before showing readiness.
- Native keyboard restart, UI restart and programmatic restart must all clear completed/paused state. Test each after a completed one-shot.
- Preview held keys and exported atlas frames must use the same discrete frame selection. An attractive continuous preview is insufficient evidence for a different exported animation.
- Check event landmarks against visible frames. A punch's first extended pose at frame 4 cannot use an active-start marker at frame 5 without an explicit gameplay reason.
- Keep audit-only expected images outside the runtime import tree with `.gdignore`. They remain independent evidence, not required shader textures.
- When a hosting service limits individual static file size, gzip a large PCK and stream it through `DecompressionStream('gzip')` before passing the decoded bytes to Godot. Keep the engine's original file-size metadata. Test actual startup and every route after this change; compression does not reduce the decoded memory requirement.

Godot texture import can repair RGB in fully transparent border pixels. Compare alpha exactly and compare RGBA for every nonzero-alpha pixel; canonicalize RGB to zero only where alpha is exactly zero before a visible-pixel hash. Do not discard partial-alpha differences. If the application requires byte-identical texture data, explicitly disable alpha-border repair and reimport instead. A fresh two-clip authored-art forward test found 1,661 alpha-zero-only RGB differences while every visible RGBA sample matched; raw file/image hashes and canonical rendered hashes answer different questions.
