# Source-preserving native controls

The retained PixelEngine 1.5 walk (A) is the strong motion control. Its native
shoulder rotation, varied silhouettes and scarf follow-through are retained.
These small manual candidates do not establish ImageGen parity or an improved
native animation. Cutting away an opaque background is presentation hygiene;
it contributes no new drawing or motion quality.

The [offline runner](tools/refine-native-control.py) takes the original external
comparison artifact directory and the explicit [recipe](tools/native-control-recipe.json).
It verifies the immutable WebP hashes, the appearance reference, all eight
decoded pixels against the retained editable projects, and the exact clock.
Originals are copied beside candidates. There is no scaling, recentering,
registration, retiming, palette quantization, new generation or provider call.
Run from this repository with the existing Pillow environment:

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/refine-native-control.py \
  --inputs /home/astra/artifacts/pixelengine-imagen-comparison-20261020 \
  --output /absolute/fresh-output \
  --native-editor /home/astra/.local/bin/libresprite
```

The output contains six variants, their lossless editable projects and ASE files,
source-bound pencil/eraser journals, exact PNGs and rational APNGs. Journals replay,
undo to the original project and redo exactly. The optional real LibreSprite
save/reopen checks all eight actual rendered frames, 125 ms holds and the whole
reimported project. This establishes editing/export mechanics, not art approval.
Source baselines need no new external editor roundtrip; their original decoded
RGBA is checked against the retained source projects and new exports.

The runner writes `RESULTS.json`, `SHA256.json`, per-variant receipts, source/diff
coordinates, source-color witnesses and explicit masks. `index.html` provides
synchronized normal/half-speed playback, frame stepping, native/2×/4× scale and
contrasting mattes. Every cutout/refined variant also has a full eight-pair sheet
including 7→0. Serve the fresh output with a local HTTP server to use the player.
Writing a player does not establish a browser or human playback check.

## Exact matte policy

A's background is opaque RGBA `[125,125,125,255]`; B's is
`[126,126,126,255]`. The cutout erases only exact matches in a four-connected
component with a canvas-border witness. There is no tolerance or global gray
deletion. All other visible colors, including gray material, remain byte exact.
Enclosed exact-gray pixels are conservatively protected and listed individually:
A f4 `(42,44)`; B f1/f5 `(41,44)` and f4 `(42,44)`. They are not silently treated
as background solely because their RGB matches the matte. On the frozen inputs,
each frame has one large border-connected matte region and at most one enclosed
one-pixel component. The masks bind the actual erased coordinates.

## Two small candidates

`A-scarf-transition` retains every pixel in frames 0, 1, 3, 4, 5 and 6 after
cutout. It adds nine pixels in f2 as a short reveal behind the turning shoulder.
In f7 it changes eight pixels around the original dark-red sliver: six were
transparent and two were black outline pixels. It samples the original ink,
scarf red and dark red, preserving all existing colored torso/shoulder pixels.
The broad native f3–f6 scarf shapes remain unchanged. A short cue may soften the
entry/exit; whether it improves the excellent original motion remains open.

`B-boot-separation` changes twelve pixels in f3 only: nine erase the rightmost
three columns of the lower, planted boot's toe and three close its shortened
outline. The overpassing boot, both knees/cuffs and upper body remain unchanged.
This separates the two toe levels locally. The nested leg/boot overlap remains
a native pose limitation; a small contour edit does not recover hidden anatomy
or guarantee better playback.

## Native scarf motion template

`A-source-scarf-track.json` records the original scarf's visible collar proxy,
rear-tail colored coordinates, source-color tip and every adjacency. Its fixed
measurement window is x20..30/y26..39; the proxy is a visible red pixel and is
not an inferred rig anchor. The original sequence is:

| Frame | Visible colored tail tip | Observed state |
| --- | --- | --- |
| 0 | none | Near shoulder broad; rear tail absent in this window |
| 1 | none | Rear tail remains absent |
| 2 | none | Before the source reveal |
| 3 | (25,35) | Rear/down reveal as the shoulder turns |
| 4 | (24,33) | Largest leftward extension and lifted end |
| 5 | (24,35) | Left extent held; end drops two pixels |
| 6 | (25,37) | End trails down and starts tucking behind the sleeve |
| 7 | (26,35) | Only two dark-red pixels remain before f0 occlusion |

The rear free end reads behind the shoulder while the collar wraps in front of
the tunic. Absence of visible paint is not reconstructed hidden cloth. A new
painted animation using this guide should preserve the changing shoulder volume
and delayed free-end response, then receive its own native-scale pair and timed
review. A rigid full-body replacement would discard the source's useful motion.

## Retained run boundary

The completed source-control run is external at
`/home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/run04`.
Earlier runs remain evidence: run01 stopped on a mistyped source-color witness;
run02 corrected it; run03 added the source scarf track/player. The final runner
preflights every source-color witness before making an output directory.
The final PNG/APNG pixels equal run02/run03 for all six variants. No numerical
art score, human continuous-playback acceptance or new engine integration is
claimed. Root coordinates comparative review and final selection.
