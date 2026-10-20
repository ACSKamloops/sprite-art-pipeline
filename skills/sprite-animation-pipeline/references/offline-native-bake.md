# Rebuild sprites from a retained native video

Use `scripts/bake_native_sprites.py` for a source-hashed, uniform-native-clock video that has an explicitly reviewed integer whole-canvas sample, green-screen matte and selected frame window. Requires Python3, NumPy, Pillow, ffmpeg and ffprobe. This is an offline transformation; it has no provider client or credentials.

The caller supplies the actual video SHA, size, frame count, first timestamp, positive rational hold and duration; sample stride/offset; matte rule; explicit selection/order/loop flag; and expected despill edit count. Inspect the native return before authoring this recipe. The tool does not find a good loop, infer missing poses or judge an animation. Its current contract rejects nonuniform holds; use a different explicit timestamp-preserving route for those sources.

The retained generic-hero fixture is self-contained in `assets/native-bake-hero/`. Create the output's parent, choose an output that does not yet exist, then run:

```bash
python3 scripts/bake_native_sprites.py \
  --video assets/native-bake-hero/native-video.mp4 \
  --recipe assets/native-bake-hero/recipe.json \
  --output /absolute/path/to/fresh-output
```

From that output directory, verify all278 expected raw/matte/selected PNG files using the absolute path to `assets/native-bake-hero/EXPECTED-PNG-SHA256SUMS` with `sha256sum --status -c`. `EXPECTED-PIXELS.json` additionally retains array hashes. Exact PNG encodings were checked in the recorded environment; distinguish encoder-version byte differences from changed decoded pixels.

The successful fixture retains all124 returned frames at1/24s (31/6s), samples source(6x+3,6y+3) from768² to128², then explicitly selects0..29 at their unchanged native clock. Hard alpha is zero only when G>=90 and G-R>=45 and G-B>=45. All RGB, including hidden RGB, remains intact. Only opaque green-dominant pixels then set G=max(R,B):3525 literal changes with actual replay/undo and source-coordinate witnesses. These thresholds and this selection are case choices for a blue/brown character; they can destroy green costume paint and must not be inherited blindly.

Preflight rejects stale source/geometry/timing/contracts and existing outputs without changing them. Decoder failure or a wrong expected edit count can leave a new incomplete output; require the completed receipt. Relative output manifests retain all native timestamps and the selected rational holds. Clock Hz is the normalized hold denominator, with the numerator representing held ticks; a2/3s hold is two ticks at3Hz, not a truncated1Hz clock.

Source evidence is consolidated at `/home/astra/projects/rpg-hero-animation`. The actual new-project run reproduced all124 matte and30 approved selected PNG bytes. A separate actual1.5fps fixture verified2/3s holds. Six preflight rejection cases were checked separately. No new stochastic provider result or character-art acceptance follows from these mechanical tests.
