# Repaired walk: real Godot resource and clock proof

The actual exported resources/driver for repaired sequence
`9f9e1c53324ea567cb1bbd5be8c310691c0f87f45044279c1f37d81349e66d79`
passed **74 explicit checks** in Godot4.7.2-stable official,
build `ed1daf0bf001b61586d9930840f2f1394092c079`.

The original export was read only. Its seven Godot files and eight reference
PNGs were hashed before/after; all hashes match. The project was copied to
`/home/astra/artifacts/pixellab-repaired-walk-godot-20261014-final/project`.
The engine first performed an actual editor asset import into that copy;
the verification did not attempt plain unimported headless texture readback.
The exported `driver.gd` was executed unchanged.

Reproduction uses [verify_repaired_walk_godot.py](verify_repaired_walk_godot.py):

```bash
python docs/motion-pipeline-20261014/verify_repaired_walk_godot.py \
  --export-godot /home/astra/artifacts/pixellab-motion-pipeline-20261014/review/manual-repair/exports/studio-168c543224d144918d06edbcdc08319f/godot \
  --output /home/astra/artifacts/pixellab-repaired-walk-godot-20261014-final
```

Use a new absent output directory for another run. The proof invokes:

```text
godot --headless --path <copied-project> --editor --import
godot --headless --path <copied-project> --script res://verify.gd --max-fps 240
```

Exact resolved commands, source hashes, engine logs' hashes, engine version and
all74 results are pinned in [GODOT-WALK-PROOF.json](GODOT-WALK-PROOF.json).
The full external `PROOF.json` SHA256 is
`21c6cdd8111e4eab8850e125f36c122d39c37ae60c1b209ed4f9c082e92fec7a`.

Verified behavior:

- The imported scene loads eight atlas regions. Saving/reloading its real
  `SpriteFrames` retains looping; each256×256 texture's decoded RGBA is byte
  identical to the corresponding emitted PNG and has the same SHA256.
- The manifest retains exact holds5/24second and total5/3seconds. Godot resource
  hold values approximate5/24; the observed error is approximately−4.97e−9
  second per hold. The test allows1e−7 for resource float precision, while
  retaining exact rational manifest checks. The exported elapsed driver uses
  its converted timeline and disables the native sprite clock (`speed_scale=0`).
- Restart plus public `advance_seconds` checks every frame midpoint, every
  just-before boundary, every exact next-frame boundary, and the exact third
  wrap. There is no direct seek API; no test-only assignment to the displayed
  frame substitutes for the driver.
- Actual normal `_process(delta)` playback at rate1 runs over five measured
  wall seconds (5.133784s wall;5.152806s driver elapsed) and completes three cycles. All eight frame indices occur in
  `frame_changed` callbacks; three `animation_looped` callbacks observe the
  driver's boundary clock. Infinite playback emits neither finite-finish nor
  playback-completed signals. Normal processing while paused freezes the full
  state; restart resets elapsed time, play count and first frame.

The first preserved attempt under sibling
`pixellab-repaired-walk-godot-20261014` failed only an overly strict1e−9
resource-duration tolerance. Its texture, boundary and timed-playback checks
already passed. The final fresh-copy rerun uses the existing runtime-test
precision allowance; no exported resource or runtime implementation was changed.

This clip declares **zero authored timeline events**, so no event-payload
callback coverage is claimed. The engine warns about test-only
`Image.load_from_file` reads of reference PNGs; actual subject textures are
loaded through imported resources. This proves standalone headless project
resources and the exported elapsed driver, not a packaged Godot game/PCK, GPU
appearance, audio, world foot contact, articulated rigging, seamless motion or
art-quality acceptance. No provider or credential calls were made.
