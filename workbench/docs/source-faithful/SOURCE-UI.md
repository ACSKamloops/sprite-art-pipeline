# Original PixelLab source workflow — v0.5

Open [PixelLab source](http://127.0.0.1:8874/#source) in the local workbench.
This page runs unchanged recovered browser functions. It does not substitute
new repair/shading/generation algorithms under PixelLab names.

1. Choose **Energy orb** or **Slash arc**, then **Load snapshot**. Both recipes
   came from retained PixelLab `get_preset` responses; the original requests
   contained no recipe. Their response and canonical recipe hashes are bundled.
2. Adjust the declared sliders or colour ramp. Their IDs, bounds, defaults,
   binding paths, rounding, expression handling and application come from the
   original validator/control functions. The UI supplies values to those
   functions without recreating the mapping math.
3. Choose **Render with original code**. A durable local job executes the pinned
   renderer, retaining final/back/front streams, recipe and control receipts.
   Cancellation/retry can be inspected in Jobs. Cancellation does not promise
   immediate termination of an already-running Node render.
4. Play or scrub the result. All frames are fetched and decoded before playback.
   Source frame pixels and rational holds stay authoritative; this preview uses
   a local display clock.
5. **Save recipe JSON** saves the raw declaration with your chosen values.
   **Recent retained renders** restores its raw recipe, controls and supplied
   raster IDs. Those IDs still require their bytes in this Store.
6. **Edit rendered pixels** opens the separate local indexed editor. This is our
   editing utility, not the missing private PixelLab pixel-workbench handler.
   The original recipe/receipt remain linked through the source sequence.

For a supplied subject or named images, enter existing raster IDs under
**Supplied raster inputs**. The renderer processes supplied subject frames with
its original threshold/playback/placement rules. It supplies no missing anatomy
or walking poses. Recipe-file imports are caller-supplied inputs, not certified
vendor presets.

## What is original, and what is local plumbing

The 46 factory slices match four retained original bundles byte-for-byte. The
original exports are `47381.W$` (normalizer), `47381.uY` (controls) and
`39852.sY` (renderer), with their original dependencies and 17 layer families.
Only reached factory dependencies execute; dormant account/UI modules are not
services. [Source/control details](SOURCE-CONTROLS.md),
[independent full-bundle oracle](FIDELITY-REVIEW.md), [REA evidence](REA.md).

Our HTTP/JSONL/CLI adapters, local jobs, resource limits, immutable storage,
preview UI, portable export and indexed editor are host plumbing. The VFX
profile narrows source admission to 16–512px sides, 1–32 frames and an explicit
time limit. These limits do not imply full source-validator admission parity.
The registry labels source execution separately from our own local utilities.

The original source has an important boundary: normalizing can introduce
`rng:null`, which is invalid as a fresh raw input. Applied mul/add controls would
also be applied again if reused as raw input. Receipts therefore preserve raw,
normalized and applied recipes separately. Rendering always passes the raw
declared recipe so the original renderer applies its controls once.

The captured presets come from an MCP response snapshot; the executed renderer
comes from a retained browser-code snapshot. Selected matching outputs do not
identify the current remote MCP/server build. Private neural models and missing
pixel-workbench handlers remain unavailable, and full art/model comparisons
remain gated.

## Verified scope

[The verification record](VERIFICATION.json) binds code, tests, package and
browser evidence. The 527-test suite passed at `f0af029`. The later four-line
host restoration fix `f4e10a7` received a fresh installed-package proof and
explicit browser/independent host checks; it is not relabeled as another full
suite execution.

[Fifteen browser artifact checks](evidence/browser/BROWSER-SOURCE-REPORT.json)
passed. They cover the two actual presets, Size 10→14, raw recipe download,
recent input restoration, separate editor opening, original future-version
rejection and a 390px viewport. The playing canvas exposed all eight exact
stored frames with successive transitions and three loop wraps. A separate
loader over full original bundles matched every final/back/front raster in the
three browser-produced results. A source-version rejection was intentional;
the canvas-readback performance warning came from the QA sampler.

The assistant viewed the retained effect and mobile screenshots. This is source
reproduction and preview transport evidence, not a 9/10 humanoid art/motion
approval. No provider calls, generation credits or image-model experiments were
used. [Package proof](PACKAGE-PROOF.md), [workflow review](WORKFLOW-REVIEW.md),
[final independent source review](FINAL-SOURCE-REVIEW.md).

To recheck the retained browser observations against this Store and the original
bundles while the local server is running:

```bash
.venv/bin/python docs/source-faithful/BROWSER-check.py
```

The checker validates saved observations and independently reruns original
source; it does not perform the browser interactions again.
