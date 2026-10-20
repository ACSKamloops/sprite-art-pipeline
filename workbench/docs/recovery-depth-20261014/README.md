# Deeper PixelLab method recovery

This pass adds **executable client-method recovery and a validated local replay of
one observed server behavior**. It does not establish that the whole PixelLab
pipeline, private model weights or animation conversion have been recovered.
No new character art or native H3 animation was generated in this pass.

The original matched-art comparison remains in
[the RPG hero pilot](../provider-preparation/h3-rpg-pilot/README.md).
This investigation addresses its remaining method questions with source recovery,
controlled reducer inputs and independent verification.

## What can now be run locally

| Stage | Evidence and local channel | Boundary |
| --- | --- | --- |
| Caption/request preparation | [Prompt/frame report](PROMPT-FRAME-RECOVERY.md); original Lua and web functions replayed with98 Lua assertions and5 web cases | Host/editor/network interfaces are explicit stubs; private caption writer is not recovered. |
| RGBA serialization, masks, decoding and placement | [Pixel-method report](PIXEL-CONVERSION-RECOVERY.md);18 assertions execute original recovered Godot function bodies | Selected methods run in a temporary headless harness; this is not full native editor acceptance. |
| Browser GIF conversion | Original shipped module5958 `quantize`, `applyPalette`, `GIFEncoder`;8 assertions and a byte-bound74-byte GIF | Its per-frame rgba4444/binary-alpha policy is GIF export, not the server animation converter. |
| Input-image classifier | [Original factory and worker replay](CLASSIFIER-REPLAY.md), five diagnostic fixtures | Detects the tested4x upscale; four other fixtures return null. This is not a general pixel-art quality or classification-accuracy gate. |
| Fixed-palette reducer behavior | [Reducer findings](REDUCER-BEHAVIOR.md); `scripts/replay_pixellab_fixed_palette.py` | Independently inferred and held-out validated; private source, auto-palette clustering and positive dithering remain unknown. |
| Public web/editor implementation | [Fresh source recovery](WEB-MODEL-RECOVERY.md), current public PCK and exact code anchors | Current scripts and wrappers cannot identify unshipped inference or weights. |
| Ordered dithering | [Offline characterization](DITHER-CHARACTERIZATION.md), all378 candidate results retained | Best tested candidate still misses538/32,768 RGBA entries; no exact implementation is claimed. |

The [independent reducer review](REDUCER-ADVERSARIAL-REVIEW.md) checks numerical
replay, chronology, actual HAR/REA bindings, sampling counts and what the finite
experiment cannot establish.

## Concrete new distinctions

The website's shipped GIF palette assignment uses squared **raw RGB or RGBA**
channel distances with packed-bin caching. The observed nondithered public
reducer instead agrees with a **weighted Oklab** nearest-palette rule on the
retained tests. These are separate implementations. Applying a GIF export helper
is not a reproduction of server Reduce Colors or PixMiniMax postprocessing.

The working local representative rule is:

```text
convert source RGB and supplied palette RGB from sRGB to Oklab
choose palette entry minimizing 0.25*dL² + da² + db²
retain every original alpha value, including partial alpha
map hidden RGB too; do not universally zero RGB at alpha0
```

This rule matched **73,728 RGBA entries**, including repeated calibration cases,
and a predeclared fresh holdout of8,192 entries. The holdout contains4,096 RGB
samples,4,094 distinct colors;4,093 were absent from calibration. Its nine-color
palette differs from the two- and six-color calibration palettes. These counts
are deliberately not all described as independent examples.

Weight0.25 is a successful representative of a narrow interval compatible with
the observations, not a uniquely recovered private numerical constant. Exact
distance ties, arbitrary/transparent palette entries and unseen inputs are not
covered by this finite proof. The local tie choice is explicitly first supplied
entry; the service's tie choice is untested. See the reducer report for the
counterexample to unweighted Oklab and the independent admissible interval.

The fresh public pack is version0.0.211, with378 recovered GDScripts:368 unchanged,
eight changed and two new relative to the retained source set. The H3 animation,
interpolation, transport and image-placement sources examined in the version
comparison are unchanged. Changed palette/tileset/GIF UI code is a separate
finding. Client H3 playback takes existing recipe FPS or falls back to12; a
cost helper's estimated seconds is not the native video clock or sampler.

The source-map follow-up tested all72 unique observed public JavaScript URLs
with the conventional adjacent `.map` suffix; all returned404. No maps were
recovered through that convention. [Exact retrieval bounds](ADJACENT-SOURCE-MAPS.md).

Prompt replay also qualified two edge cases: Lua validates numeric seed strings
without converting them, and selection placement tests whether either output
axis is smaller. Neither private request grammar nor that geometry predicate
should be silently replaced with the public REST schema or a safer invented rule.

## Reproduce without credentials or credits

From `/home/astra/projects/pixellab-local-workbench`:

```bash
python3 scripts/replay_prompt_frame_recovery.py
python3 docs/recovery-depth-20261014/replay_shipped_pixel_methods.py
node docs/recovery-depth-20261014/replay_shipped_gif_quantizer.cjs
node docs/recovery-depth-20261014/classifier_replay.cjs /home/astra/artifacts/pixellab-recovery-web-20261014/assets /tmp/pixellab-classifier-replay
python3 scripts/analyze_reducer_recovery.py /home/astra/artifacts/pixellab-reducer-recovery-20261014 --output /tmp/pixellab-reducer-recheck.json
python3 scripts/replay_pixellab_fixed_palette.py --source /home/astra/artifacts/pixellab-reducer-recovery-20261014-holdout/inputs/rgba-holdout.png --palette /home/astra/artifacts/pixellab-reducer-recovery-20261014-holdout/inputs/holdout-palette.png --output /tmp/pixellab-palette-replay.png
```

Replay outputs must be new files. Original client source hashes are checked before
execution; recovered source files remain unchanged. Original emitted receipts
stay under this directory, and separate root replays are retained at
`/home/astra/artifacts/pixellab-recovery-depth-20261014/`.

The probe submitter is separate from these offline channels. Seven explicit
`/reduce-colors` POSTs consumed **0.7 subscription generations** in total. Each
request is frozen before submission and has its own persistent duplicate guard;
actual producer HAR, original returned PNGs and complete REA Evidence are retained
in the three reducer artifact folders. No automatic retries or native H3 calls
were used. This finite local guard is not provider-side exactly-once execution.

The final software suite passed629 tests with1400 existing dependency
deprecation warnings. Original-method checks remain separate:98 Lua assertions,
five web-helper cases,18 Godot assertions, eight GIF assertions and five classifier
fixtures. These finite checks do not approve the entire client, private server
pipeline or game art.

## Where the evidence still stops

- **Inference and model identity:** H3 is the named engine family. Exact PixelLab
  deployment/checkpoint, fine-tuning, model weights and inference configuration
  are not identified by the inspected public/client artifacts.
- **Video-to-sprite extraction:** original provider duration/FPS/PTS, selected
  source indices and resampling remain unknown. Returned PNG order, client
  playback metadata and cost estimates do not recover them.
- **Cutout and de-flicker:** clients expose flags and consume returned pixels.
  Their server foreground masks, drift metric/default, correction transform and
  temporal filter remain unknown. Binary delivered alpha is an observation.
- **Automatic palette construction and positive dithering:** the fixed supplied
  palette result is narrower than those stages. Failed candidate replays remain
  evidence and are not promoted to implementations.
- **Integration and art:** the existing workbench runtime/UI and old package
  proof were not modified. These are research/replay channels, not production art
  acceptance or a completed interchangeable animation UI.

The next useful work is to use these specific source/replay channels in the
workbench with their distinct labels, then validate sprite edits and timing
against retained service outputs. The unknown server stages require further
discriminating evidence or access to original implementation; an invented
replacement must not be called recovered PixelLab code.
