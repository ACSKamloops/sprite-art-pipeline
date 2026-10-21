# PixelEngine findings in the ImageGen sprite pipeline

This is an optional, explicitly selected experiment. It combines the existing
sprite construction, palette mapping, exact timing, native editor exchange and
Godot export tools with the **actual retained PixelEngine client WASM**. It does
not reproduce the hosted generative models or establish hosted/local equality.
No generator runs from these scripts, setup, imports or tests.

[Follow-on refinement](REFINEMENT.md) records the stronger scarf guide, owned
head/body composition, mixed-rate cloth, source-bound leg experiments and
subsequent independent reviews. The9/10 target remains unmet; this first
comparison below is retained history.

[Source-preserving native controls](NATIVE-CONTROLS.md) retain PixelEngine's
strong torso/scarf motion beside exact connected-matte cutouts and two small
manual pixel candidates. They provide a source-bound motion template, editable
journals and exact exports without claiming new drawing quality from transparency.

[Two lower-body bridge probes](LOWERBODY-BRIDGES.md) add genuine source-colored
inbetweens to two difficult ImageGen gait intervals while preserving all eight
keys and the one-second period. Original/timing-only/candidate controls remain
separate; a full 16-frame bank is not approved by the local probe.

The local experiment is retained outside Git at
`/home/astra/artifacts/pixelengine-imagen-comparison-20261020`.
Third-party bundles, account material, private captures and generated originals
are not vendored here. [tools/README.md](tools/README.md) defines the exact external
artifact hashes and the no-network adapter.

## What was tested

Three built-in OpenAI ImageGen calls produced one back-facing still, one text-led
eight-pose walk, and one walk repainted from a captured PixelEngine pose guide.
All use the same generic hero reference. There was no H3, local generative model,
new PixelEngine generation or additional PixelEngine credit expenditure.

Six frozen walk cases were compared at 80×80, eight exact 1/8-second holds:

| Case | Paint and processing |
| --- | --- |
| A | Retained PixelEngine 1.5, original decoded pixels/timing |
| B | Retained PixelEngine 1.1, original decoded pixels/timing |
| C | Text-led ImageGen, one fixed affine and the reference palette |
| D | Pose-guided ImageGen, one fixed affine and the reference palette |
| E | Guided ImageGen, genuine full-resolution shared-frame WASM, then fixed affine |
| F | E with explicit low-alpha preparation before WASM |

F removes alpha 1–7 and canonicalizes RGB under alpha 0. It preserves every
input RGBA value with alpha at least 8. This is a measured candidate, not a
default alpha threshold or a general transparency recipe. The original generated
alpha is preserved in C/D and all raw art remains immutable.

Processing the 80px ImageGen stage again inferred a 23px grid in the first walk
and a 15px grid for the back still. These failures remain retained. Processing
the large 418px cells first gave a 93px grid for the text walk and 84px for the
guided walk before authored stage transport. The output grid and exact metadata
are retained; stage normalization is not prompt compliance or recovered source
cut coordinates. Do not silently repixelate a native sprite.

The existing 24-color authored palette fitter did not converge within its
32-iteration guard. That failed run was kept. The nominated comparison explicitly
uses the original hero's 20-color palette through the existing fixed mapper;
no hidden iteration extension or substitute clustering was used. Shared palette
mapping cannot repair an incorrect gait, facing drift or missing anatomy.

## Replay without generation

Run from the repository, using its existing Pillow/NumPy environment. Every
output path must be fresh; the artifact root must contain the preserved raw
and reference files. The runner measures the actual square sheet and requires
three exactly divisible rows and columns. It never finds arbitrary sheet cells.

```bash
python research/pixelengine-imagen/tools/run-comparison.py \
  --artifacts /home/astra/artifacts/pixelengine-imagen-comparison-20261020 \
  --output-dir /absolute/fresh/output \
  --wrapper /absolute/retained/0kq99w3kf_p3k.js \
  --wasm /absolute/retained/pixel_engine_pixel_tools_bg.08nhkq70kh3-e.wasm \
  --palette-mode reference \
  --walk raw/imagegen-walk-guided-original.png \
  --wasm-alpha-floor 8
```

Omit the alpha flag for the raw-alpha experiment; select
`raw/imagegen-walk-original.png` for the text-led walk. `--palette-mode fit24`
replays the bounded fitting attempt and may fail rather than substitute an
unreviewed policy. `make-review.py --help` packages the retained named runs into
the labelled and anonymous comparative players. It does not regenerate them.
The local `requests/` folder retains exact prompts, ordered image roles/hashes
and byte-hash-verified runner snapshots used by the nominated runs. Archived
runner snapshots are evidence copies: their module paths assume placement in
this repository's `research/pixelengine-imagen/tools/` directory when executed.
Earlier exploratory run01/run02 lack recovered source snapshots and are not
the reviewed replay authority.

## Verification boundary

All six PNG/APNG deliveries preserve 8×1/8-second holds and source pixels. Actual
Godot import/save/reload checks covered 48 frame regions and durations. Candidate
D additionally passed a real LibreSprite batch save/reopen, exported atlas and
sidecar reimport with all eight RGBA frames and 125ms holds unchanged.

The browser check exercised every frame and wrap, native/2×/4× scale, contrasting
mattes, normal playback and half speed. Browser canvas RGBA matched the binary
alpha cases; partial-alpha C/D had canvas rounding differences and do not have
literal browser RGBA equality. PNG/APNG and LibreSprite equality are separate.
The five-second MP4 has independently verified PTS, holds and source-template
classification; it is a lossy preview, not a pixel master.

Cold art review is bound to the anonymous packet fingerprint. Its judgments
reconstruct motion from chronology and exact holds; they are not human
continuous-playback acceptance. A single tested right-facing walk does not
approve a full character, action library, world contact or other directions.
The back-facing still remains a separate, unapproved appearance test. Captured
PixelEngine motion also needs review; it is not automatically a gold standard.

Use the existing [sprite animation skill](../../skills/sprite-animation-pipeline/SKILL.md)
for exact exports and scoped review, and the
[ImageGen skill](../../skills/imagegen-sprite-animation/SKILL.md) for appearance/
pose reference roles. Prefer a proven motion guide plus constrained repaint and
source-bound editing over trying to fix phase errors through palette reduction.
