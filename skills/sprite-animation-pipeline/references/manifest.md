# Portable animation contract

JSON has video_fps and nonempty clips. Every clip has actor, name (unique per actor), action, direction, sheet (relative to manifest), frame_size [w,h], sheet_columns, pivot_pixels, loop and frames. Actor IDs used as resource filenames should contain only letters, digits, hyphens and underscores. Escaping sheet paths are rejected.

Each frame has atlas_index and positive duration_video_frames. Clip video_fps overrides the root clock. Optional duration_seconds must equal ticks/fps. Optional pixel_sha256 is the exact cropped RGBA cell hash. Repeated cells/order are valid; blanks and edge contact are review hints.

Optional ground_pivot_pixels separates the world anchor from render pivot. Record why they differ. A centered sprite at a ground anchor uses offset=frame_size/2-ground_pivot. Variable frame dimensions/trims need explicit per-frame transforms before using this simple importer.

timeline_events holds authored/verified events: [{"frame":1,"name":"hit_start"}]. Keep raw extracted opcodes in native_events; native palette/movement/status/external-object commands aren't automatically attack events.

```json
{"video_fps":60,"clips":[{
  "actor":"robot","name":"walk_right","action":"walk","direction":"right",
  "sheet":"sheets/robot.png","frame_size":[64,64],"sheet_columns":4,
  "pivot_pixels":[32,48],"ground_pivot_pixels":[32,48],"loop":true,
  "frames":[{"atlas_index":0,"duration_video_frames":6},{"atlas_index":1,"duration_video_frames":6}],
  "timeline_events":[]
}]}
```

The optional driver uses gameplay_bindings → actor → state → direction. Values are clip names or equipment-keyed dictionaries. Implemented states are idle/walk/attack:

```json
{"gameplay_bindings":{"robot":{
 "idle":{"right":"idle_right"},"walk":{"right":"walk_right"},
 "attack":{"right":{"sword":"slash_right","bow":"shoot_right"}}
}}}
```

Declare every direction the controller can select. Don't silently substitute wrong actions/views. The example retains a weapon key; rename it when the game's equipment model differs.

Preserve source hashes/IDs, mapping choices, confidence, assumptions, missing layers and runtime coverage. Aliases can share atlases with distinct bindings/provenance. Export consistency cannot establish a native mapping assumption.
