# Delivery and review after manual sprite refinement

Use after an existing sprite has been refined with source pixels, newly drawn poses or editable parts. For the art decisions and source ownership, read the companion construction skill's [manual-gait-refinement.md](../../sprite-construction-editing/references/manual-gait-refinement.md). This reference covers clocks, external-editor exchange, consumer evidence and review scope.

## Encode the authored clock exactly

Keep native/source timing, authored timing and a preview's container clock distinct. Each output pose needs a positive rational hold, frame hash, fixed canvas and declared pivot. A new cadence is an authored revision, not recovered game timing. Never hide it by recentering poses or relabeling a requested duration as measured.

The toolkit's editable export is a different schema: its canvas is an object and frames have `png` and `duration_ticks`. Do not pass that manifest directly to the exact video encoder. The bundled `scripts/project_delivery.py` reads an authoritative editable `project.json`, selects one animation, and writes full-canvas PNGs, an atlas, rational `manifest.json`, Godot `clips.json`, source pins and a fresh Godot resource-test project. It preserves animation order and repeated bindings instead of sorting or deduplicating them. It derives dimensions, frame count, holds, loop and names from the project; no hero-specific constants are required. It needs the companion construction toolkit, discovered beside this skill or supplied with `--toolkit`.

```sh
ANIMATION_SKILL=/home/astra/.codex/skills/sprite-animation-pipeline
python3 "$ANIMATION_SKILL/scripts/project_delivery.py" \
  /path/to/edited-project.json /path/to/fresh-delivery \
  --animation walk --actor my_hero --columns 8
python3 "$ANIMATION_SKILL/scripts/exact_cfr.py" \
  /path/to/fresh-delivery/manifest.json /path/to/fresh-video --scale 3
godot --headless --path /path/to/fresh-delivery --editor --import --quit
godot --headless --path /path/to/fresh-delivery --script build_godot.gd
```

The generated Godot project tests resource import/save/reload; it supplies no gameplay controller or live/render proof. Source pivots remain in `manifest.json` and the copied project; apply the intended Sprite2D offset/root convention in the actual consumer because SpriteFrames itself does not apply these pivots. `video_fps` and `duration_video_frames` are legacy Godot-importer field names here: their units are the source tick rate and pose ticks, not the encoded MP4's CFR clock. The adapter interprets a noninteger `animation.fps` as the exact stored decimal value. An incompatible video clock must be rejected, not silently rounded or claimed to recover native timing. Select the animation explicitly when a project has multiple bindings.

The bundled `scripts/exact_cfr.py` needs Python, Pillow, NumPy, FFmpeg with libx264, and ffprobe. It reads a manifest with `canvas: [width,height]` and ordered `frames` containing `file`, `sha256` (or `png_sha256`) and `hold: [numerator,denominator]`. The PNG hashes and canvas are checked. The output folder must be fresh.

```sh
python3 /home/astra/.codex/skills/sprite-animation-pipeline/scripts/exact_cfr.py \
  /path/to/manifest.json /path/to/fresh-preview --scale 3
```

It finds an exact common CFR clock within its supported bounds (up to 240 fps), repeats each source pose by its rational hold, and verifies actual stream/frame PTS, frame duration and total length after encoding. It then decodes every actual video frame, classifies it against every prepared RGB source template and requires the declared pose plus a quality bound. Identical template groups are permitted, with their boundaries explicitly unobservable. Incompatible clocks are rejected instead of silently rounding them. `--fps` must exactly represent every hold; do not assume 60 fps always works.

Outputs include `preview-exact.mp4`, prepared templates, ffprobe output, `frame-timing.json`, `decoded-classification.json` and `RECEIPT.json`. This is a lossy, checker-matted H.264 preview. It does not prove source RGBA equality, native fidelity, human viewing or art quality. Keep transparent PNGs authoritative. The portable script removes the historical local baseline-file dependency; it records the source script digest in its receipt.

Example: sixteen holds of 6/120 seconds produce an 800 ms loop with 48 frames at 60 fps, three presentations per pose. The older seven-pose cycle had holds 16/14/14/10/6/14/16 ticks at 120 Hz, totaling 750 ms; its exact 60 fps runs were 8/7/7/5/3/7/8. Neither clock should be replaced by a convenient 125 ms-per-pose encoder.

## Check the files the user actually receives

In the browser, preload the PNGs, await the intended project fingerprint and compare every displayed frame with its source. Check step, pause, both clips' own clocks, normal/slow playback, scale, and last→first onions. The existing fine editor's neighbor checkbox does not wrap at the endpoints; verify that explicitly or use a wrapped comparison player. A correctly moving frame index is not proof that the corresponding image was drawn.

Use a fresh layered LibreSprite/Aseprite export plus the required `.sprite-lab.json` sidecar. Save and reopen it in the actual external editor, import it back with the original sidecar, and compare the complete project and every rendered pose. Millisecond quantization in the editor must not replace the rational source clock. A canonical project hash is different from the JSON file hash; name which one a receipt binds.

## Separate engine proofs

Treat these as distinct results:

1. Save/reload real SpriteFrames and check frame regions, order, loop and hold units. Use `assets/build_godot.gd` with its expected clip schema or an explicitly adapted importer.
2. Drive real AnimatedSprite2D elapsed playback and observe all expected poses and loops. A seek-only test or fixed capture is not live-clock proof. Retain pause/restart tests where relevant.
3. Render selected poses in the actual engine and compare source pixels. Headless dummy rendering does not establish GPU appearance. The retained case used X11 OpenGL compatibility with software llvmpipe; report that rather than implying a hardware-GPU test.
4. For world motion, declare continuous versus pose-stepped root movement, snapping, contact phases and the camera/ground convention. A coherent moving reel is not whole-timeline planted-foot proof. Reuse the held-pose contact reference when that stronger claim is required.

For reproducible movie sampling, assign the pose/root during `_process` before scene rendering and record each presented pose and root. A tested `frame_pre_draw` assignment was too late for queued CanvasItem updates: the receipt described one state while the image still showed the previous state. Keep that failure distinct from an art defect. Classify the actual captures after the fix; a callback count is insufficient.

A direct live-clock movie can also contain startup holds or missed early states. Explicit fixed-pose capture is useful, but label it separately from the live-clock test. Keep status overlays out of the actor's full trajectory; a retained initial reel obscured hair with its header. Preserve the raw PNG sequence and actual recorded order.

For an opaque nearest-scaled actor, compare every opaque source RGB texel expanded by the declared integer scale against the engine crop at the recorded root position. This checks actor filtering and source fidelity while allowing a different background. It does not validate pixels outside source coverage, arbitrary scaling, translucent edges or world contact. For partial alpha, use an appropriate compositing/colour tolerance rather than inheriting this exact opaque check.

## Bind review without manufacturing consensus

Give adversarial reviewers the rendered source and actual preview, not just procedural phase names, joint targets or passing mechanics. Ask for native/2× anatomy, silhouette, attachment, material, loading, all predecessor/current pairs and wrap. Keep exact source and export hashes with the covered clip IDs. Reviewers should state whether they inspected chronological frames or continuously perceived normal-speed playback. Video decode and timed browser readbacks are useful evidence; neither supplies continuous visual perception by itself.

Keep each independent score, uncertainty, verdict and concrete findings. If one gives 8/10 and another 7/10, a single-reviewer threshold may be met but unanimous approval is not. Do not average these into an invented agreement or rerun reviews until a desired number appears. Repair demonstrated defects, retain rejected versions and source-bound reviews, and make a new judgment after actual changed output. A stricter reviewer finding no further bounded pixel defect can be a reason to seek user playback feedback rather than keep making arbitrary subpixel changes.

## Retained local evidence

`/home/astra/artifacts/pixellab-hybrid-walk-20261015/gait-v5/` is the source-bound example. `candidate-7/` has the authoritative clip and reviewed exact preview. `reviews-candidate-7/` records 8/10; `reviews-independent-7/` records 7/10; `reviews-independent-7-scene/` retains the second judgment after inspecting the moving scene. The scope is one view/action, not a finished animation library or PixelLab method/quality parity. The candidate manifest retains its historical pending-review boundary; current review receipts and `CURRENT.json` carry the later status without mutating the frozen source.

`godot-candidate-7/` contains the actual resource builder, live-clock result and `render-verified/` PNGs/movie. Live playback covered all sixteen poses and two loops. The fixed 20 Hz OpenGL capture covered the sixteen poses twice; all 32 opaque source crops matched exactly. The root advances on the pose clock, so continuous world planting remains unverified. `render/` and `render-final/` are rejected preliminary capture attempts, not delivery movies.

The case's `root/package_godot.py` and `root/play.gd` hardcode the original hero's sixteen 96px poses, names, columns and clock. They reproduce that fixture only, even if passed another manifest. For a new actor or changed timing, use the generic delivery adapter above and adapt a runtime controller in a fresh owned project. Do not run builders or engine tests against the preserved art during a read-only assessment. Construction replay also needs the frozen manual-v4 source project, parent toolkit and leg-source files; the construction reference lists them.

`FINAL-VERIFY.json`, `root/REPRODUCTION.json`, `root/output/playwright/BROWSER-VERIFY.json` and the per-case handoff distinguish tested mechanics from art acceptance. Local paths and hashes are evidence pointers, not bundled art. When packaging for another machine, include its inputs/dependencies explicitly rather than implying those paths exist there.
