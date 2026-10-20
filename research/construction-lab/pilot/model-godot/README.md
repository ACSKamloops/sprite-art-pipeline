# Local model-rendered sprite audition

Standalone Godot 4.7.2 project for a corrected licensed-source Walk export: 160×160 RGBA, twelve poses in each of four views. Supply a frozen pack containing `manifest.json`, `landmarks.json` and its 48 PNGs. One player serves unequipped and bow-equipped inputs; it does not infer equipment from the folder name or change source images.

```sh
godot --rendering-method gl_compatibility --path pilot/model-godot -- \
  --manifest /absolute/frozen-pack/manifest.json

xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility \
  --audio-driver Dummy --path pilot/model-godot --script res://test_runtime.gd -- \
  --manifest /absolute/frozen-pack/manifest.json \
  --output /absolute/fresh-proof-directory
```

WASD/arrows translate and choose direction. Space or Play/Pause holds/resumes the clock; Replay resets phase; Next pose advances to the next source-sample boundary while paused. Direction can also be selected while paused. Native 1× and integer 2×/3× use nearest sampling without stretching the preview to fit. Fixed and follow cameras preserve the same projected world origin. A subtle world XY grid and reference crosses expose camera/movement changes; they are not foot-contact markers and can be toggled off. The visual image origin is rounded once per draw for crisp texel placement, not fitted per pose. The fixed spawn point (240,170) is a viewport presentation choice that leaves the whole sprite visible at 3×; it does not alter source projection or fit individual poses.

The authoritative source clock is **24 source frames/s** over the original frames 0–30: a **1.25-second loop**. Twelve samples are spaced 2.5 source frames apart, so each image holds for 5/48 second (6.25 ticks at 60 Hz). A real SpriteFrames resource uses 9.6 poses/s, duration 1 per pose. The continuous clock chooses the held image and fractional progress; it does not round each hold to six ticks. The old 30 fps / one-second metadata rejects. Near-boundary normalization is limited to scaled floating-point roundoff; a genuine early sample stays on the previous pose.

The test saves a binary `walk-frames.res`, reopens it without resource cache reuse, and verifies every source texture, loop and timing. Actual GPU output is compared to independently computed straight-alpha compositing on opaque dark and light neutral backgrounds. The world grid is disabled explicitly for neutral-background fixtures. Soft alpha remains soft; acceptance allows at most one byte per color channel from GPU rounding. The proof also checks visible UI pixel scale, continuous/variable-rate loops, pause/resume, keyboard movement, mouse pause, replay/step signal behavior and deliberate texture-order, hold-duration and source-clock corruptions. Snapshots and the saved resource live in the fresh output folder; the JSON binds input and code hashes.

Movement at 48 pixels/s is an audition setting. It is **not** calibrated to the source stride, and no zero-drift world-contact claim is made. Foot-control projections are not presumed toes or planted sole points. This project has only Walk; it does not imply idle, combat, equipment changes, recovery, collision, or a full authored-character library. Engineering checks are independent of the visual review and user acceptance. No professional-source or license status automatically approves artwork.

Final tested input is the producer's `candidate-walk-bow160-game-light-v11/manifest.json` (manifest SHA `03fa079e0495dd83f81ad6a00d1778f57e4b7effa885c4d5d54498ebd7c226c8`). From the repository root, launch the frozen local pack with:

```sh
godot --rendering-method gl_compatibility --path pilot/model-godot -- \
  --manifest /home/astra/projects/sprite-construction-lab/pilot/model-sprite-quality-v1/candidate-walk-bow160-game-light-v11/manifest.json
```

Current proof: `proof/final-v11-runtime.json`, **310 checks passed**, including 96 real GPU composites with maximum channel error one byte. Full screenshots and the saved resource are in `/home/astra/artifacts/model-godot-bow-game-light-final24-v2/`. Earlier failed fixtures remain private historical receipts; they have not been relabelled as passing. The independent current visual decision and limits are in `final-art-review.md` and its hash-bound JSON.
