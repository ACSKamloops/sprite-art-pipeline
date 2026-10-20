# Captain experimental local Godot lab

**Experimental, art not approved.** This freezes the current twelve-frame, one-view Captain layer walk probe; it does not approve its animation anatomy or recover missing views. No sole/contact measurements or full animation-library claims are made.

From the repository root:

```sh
godot --rendering-method gl_compatibility --path pilot/captain-godot

xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility \
  --audio-driver Dummy --path pilot/captain-godot --script res://test_runtime.gd -- \
  --output=/absolute/fresh-proof-directory
```

Controls: Play/Pause, Restart, Step (pauses at the next held frame), and native 1× / nearest 2×. Every frame remains on the original fixed 256×256 canvas. Full RGBA is retained. The authoritative continuous lab clock uses twelve 100-ms holds: 1.2 seconds, exactly 72 ticks at 60 Hz. A real SpriteFrames resource has twelve duration-1 frames at 10 fps; the lab explicitly selects its frame/progress from the continuous clock so no second animation clock competes.

The portable assets include the exact source manifest, twelve PNGs and encoded-file hashes. Frozen manifest SHA256: `c48c75cbb7e3de0d2d93cc117d15914eb9baf770fe52d9fa150d7b1c0bf08303`. Its declared source raster SHA256 is `017c988e1f92efef67c505212de7ced9db4c5b292602acbd4b1f43509c6bfcf4`; the lab only claims to freeze the provided probe, not independently reconstruct that earlier source. `assets/binding.json` records provenance. Future root probe changes do not silently update this frozen copy.

Actual Godot 4.7.2 GLCompatibility/llvmpipe verification saves and reopens a binary SpriteFrames resource, checks the reopened RGBA frames and duration/loop settings, renders all twelve frames over opaque and checker backgrounds, and compares them against independent Pillow RGBA composites. All 24 comparisons were exact (maximum channel error zero). It also exercises AnimatedSprite2D's own engine playback through two loops, pause/resume, lab boundary/step/restart behavior, and negative texture-order and duration controls. Near-boundary live engine samples exclude 20-ms scheduling uncertainty; exact lab boundaries and a genuinely early timestamp are checked separately.

The final run passed **357 checks**, including runtime samples whose count varies with actual engine scheduling. Current receipt and actual 1×/2× screenshots are in `proof/`. Full saved resource, frame readbacks and report: `/home/astra/artifacts/captain-godot-v2/`. The earlier 361-check run is retained at `captain-godot-v1`; it predates the added negative controls and has not been restamped. These are mechanical rendering/playback results, not art acceptance.
