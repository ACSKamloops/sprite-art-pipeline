# Camera-relative lighting candidate v11

The actual Ranger source Walk retains its bone-parented bow. Twelve unique pose keys per true camera view preserve the original 24 fps, 30-frame/1.25-second cycle. Frame 30 is the duplicated cycle endpoint, excluded from the twelve keys and separately rerendered for the eight packed-scene reopening checks.

Key/Fill/Rim move with the camera orbit (front 0, right −90, back 180, left +90 degrees). Their camera-space transforms match within 2.3842e−6 Float32 residual, checked with a 1e−5 bound. This fixes v10's rotating screen-space light direction. It does not require left/right pixels or anatomical surfaces to have identical brightness. The world remains isotropic, no ground plane is in the sprites.

Exact frozen source: `../source/renderers/render_walk_game_light-v11.py`; pre-invocation receipt: `renderer-v11-freeze.json`. Rendering is Blender 4.5.9 Cycles CPU, eight threads, 128 samples, no denoise, AgX. Original model, rig, UV textures and Walk are intact. Sparse face UV shader marks and tonal lift remain declared authored changes. Generic licensed Ranger is a benchmark, not completed Copper Scout production art.

Actual 48 PNGs, native/2x contact sheets, four timed GIFs, packed editable scene and projected evaluated landmarks are included. `byte-validation.json` checks 207 source/clock/image/landmark/light conditions; `reopen-validation.json` binds eight actual native reopened renders. No artistic acceptance, locomotion/world contact or new action coverage is implied.

From the model folder, reproduce into a NEW output folder:

```sh
blender -b -t 8 --python render_walk_game_light.py -- fresh-output
```

The archive is intentionally in a subdirectory; the renderer resolves inputs beside itself. For standalone reproduction copy its exact bytes to the model folder under a new script name, preserve the original `source/original/` and `face_detail.json`, then render to a new directory. Current `render_walk_game_light.py` is byte-identical and already correctly located. The verifier restores saved lamp location/Euler/scale, not recomposed observed matrices; the first matrix-only failure remains preserved locally and is superseded.
