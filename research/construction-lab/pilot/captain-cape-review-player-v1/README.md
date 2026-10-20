# Synchronized original-frame motion audition

`build_player.py` verifies the frozen producer receipt before copying130 native
RGBA PNGs byte-exact into a new review folder. The self-contained HTML works by
opening the file directly: no fetch, authentication, public site or game build.
Normal/half playback, pause, frame stepping, seeking and nearest2x use one shared
clock. Both variants show the same source pose. This is an in-place art audition,
not Godot, physics, world-contact or finished-art approval.

The local Captain source has65 poses sampled at60Hz, lasting exactly65/60seconds.
The repeating player exports pose0 after64; it does not assert the original source
endpoint is pixel-identical. Native resolution stays384 under CSS2x zoom.

```sh
python3 pilot/captain-cape-review-player-v1/build_player.py \
  --audition /home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-followthrough-gpu-audition-v1 \
  --output /tmp/captain-cape-review
```

For another named variant use `--candidate traveling-fold`, `--candidate-label`
and `--description`. Paths in the producer receipt resolve against its lab root.
Existing destinations are refused to preserve old evidence.

Actual Chromium validation is in `evidence/receipt.json`: all130 native canvas
composites matched the original PNGs over a fixed checker within±1RGB rounding
step. It also verified rational loop wrap, stepping, pause, half-speed, nearest
zoom, keyboard controls and eight wall-time playback observations. The file-mode
launch was separately tested, loading all65 images for both variants and stepping
successfully. Browser tests used the Playwright CLI skill, explicitly selecting
the installed Chromium executable rather than requiring absent Google Chrome.

The current review copy is in
`/mnt/c/Users/killu/Downloads/Captain Cape Motion Tests - Unapproved`.
Both independent reviewers retained the crease baseline and rejected uniform hem
lag as a worthwhile motion repair. Original source poses and failed comparison
remain accessible; new trials must not replace this verdict or its source hashes.

A second launch exposed a real startup failure: its first RAF timestamp preceded the initializer and negative elapsed time stopped playback. The first launch pass remains historical. The corrected clock initializes on its first callback and resets on visibility changes. Fresh v2 receipts cover both uniform and differential players,130 composites each, actual wall-time motion and zero page exceptions. `evidence/startup-clock-failure` preserves the failed assertion and raw-capture hash.

The expanded v3 verifier measures actual normal and half-speed playback against wall time (2.1-frame sampling bound), checks a200ms paused clock, and rejects a negative elapsed input before state mutation. Its differential-player regression passed130composites and16actualtimed samples. The first v3 CLI file launch was blocked before page initialization; that failed launch is preserved separately from the passing HTTP test.
