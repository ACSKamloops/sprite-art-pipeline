# Optional offline PixelEngine preprocessing

`offline-pixelengine.cjs` is an explicit candidate-making step for a chosen PNG
or registered sequence. It never runs as part of setup, generation, native-sprite
import or the repository's default pipeline. Inspect and preserve the source;
classification does not trigger processing. Processing can change the palette,
grid, dimensions and original paint, including images classified as real pixel
art. Keep the source beside the candidate and review the actual result.

Requires Node.js 22+ and two separately retained external files. There are no npm
dependencies, downloads, model calls, account actions or network requests. The
genuine wrapper's `fetch` throws. The VM provides a runtime for the pinned trusted
artifact; it is not a general sandbox for arbitrary JavaScript.

## Artifact boundary

The adapter executes the **actual retained wrapper module 21436**, not a rewritten
quantizer or replacement scaler. Both complete file hashes must match before any
third-party JavaScript or WASM executes:

| External file | Required SHA-256 |
| --- | --- |
| `0kq99w3kf_p3k.js` | `d825c148b2dec6067f8d33754d40151582b3ece33ac27d8ec3dbeaaf8abae99b` |
| `pixel_engine_pixel_tools_bg.08nhkq70kh3-e.wasm` | `29a31b9f9c5fc4ab28b5830d2a73a7182601f40c483ab350059b313ba6efe14a` |

These third-party files, private captures, cookies and credentials are not included
or automatically retrieved. Supply files you already have authorization to use.
Changing either artifact requires a separate review and a new binding, rather
than an option that bypasses verification. This adapter does not recover private
Rust source, model weights or hosted preprocessing.

The retained investigation found one exact-source, colors=24 case in which the
local artifact returned **15×15** and hosted pixelation returned **18×18**. This
disproves universal hosted/local equality for that version and case. The cause
and behavior on other cases remain unproved. Classification is heuristic and
does not establish image quality or conversion suitability.

The local implementation authority is the retained investigation's
`wasm/probes/run-wasm.cjs`, `wasm/REPORT.md`, and
`wasm/stage2-consistency/REPORT.md` under the externally retained
`pixelengine-analysis-workers-20261020` artifact directory. They are local-only
evidence, not shipped dependencies. The smoke test independently constructs its
own procedural PNG and checks the exact retained gradient/colors=2 output hash.

## Commands

Run from the repository root. Set the two paths explicitly; the example below
uses the retained local artifacts. Choose an output path that does not exist;
its parent directory must already exist. Existing paths are always refused.

```bash
PIXELENGINE_WRAPPER=/home/astra/artifacts/pixelengine-analysis-workers-20261020/client/fetched/0kq99w3kf_p3k.js
PIXELENGINE_WASM=/home/astra/artifacts/pixelengine-analysis-workers-20261020/client/fetched/pixel_engine_pixel_tools_bg.08nhkq70kh3-e.wasm
PIXELENGINE_TOOL=research/pixelengine-imagen/tools/offline-pixelengine.cjs

node "$PIXELENGINE_TOOL" classify \
  --wrapper "$PIXELENGINE_WRAPPER" --wasm "$PIXELENGINE_WASM" \
  --input /absolute/path/source.png --output-dir /absolute/path/fresh-classification

node "$PIXELENGINE_TOOL" process-image \
  --wrapper "$PIXELENGINE_WRAPPER" --wasm "$PIXELENGINE_WASM" \
  --input /absolute/path/source.png --colors 24 \
  --output-dir /absolute/path/fresh-candidate

node "$PIXELENGINE_TOOL" process-frames \
  --wrapper "$PIXELENGINE_WRAPPER" --wasm "$PIXELENGINE_WASM" \
  --input /absolute/path/frame-00.png --input /absolute/path/frame-01.png \
  --palette '["#162238","#fff0c8"]' \
  --timing-sidecar /absolute/path/original-timing.json \
  --output-dir /absolute/path/fresh-sequence
```

For processing, require exactly one of `--colors` or `--palette`; there is no
implicit color default. Colors must be integer 1..256. A palette must be a JSON
array of 1..256 six-digit RGB hex strings, optionally prefixed with `#`. These
are deliberately bounded adapter guards, not a claim about every value the
binary accepts. Empty palettes and zero colors are rejected before execution
because they can trap the genuine module. The binary clusters then snaps palette
colors; supplied palette length is not a promise that all colors appear.

All inputs must be independently encoded, static PNGs. APNG is rejected. Repeated
`--input` order is the frame order; there is no glob expansion, sorting, splitting,
video decoding or duplicate removal. Sequence input dimensions must match. There
is no per-frame fitting or recentering. The WASM's shared-grid sequence path can
produce different results from processing each image separately.

The frame API has **no timing/fps parameter**. Optional `--timing-sidecar` is
copied unchanged to `timing.sidecar`, with source and destination SHA-256 hashes.
Its bytes remain opaque: no clock is invented, interpreted, checked or retimed.
Without that option, no timing data is emitted. A successful frame conversion
does not validate registration, ground contact, the clock or a loop seam.

Each fresh output contains `receipt.json` with input/artifact/adapter hashes,
requested options, Node version, complete parsed runtime metadata, ordered input
mapping, and exact output-byte hashes. `metadata.json` or `classification.json`
contains the runtime's **exact original JSON string**, without reserialization.
The single-image output is `image.png`; sequence outputs are `frame-000000.png`,
`frame-000001.png`, and so on. PNG dimensions are recorded. Source files are only
read. A runtime failure exits nonzero and retains an error receipt and any
already-written evidence in its fresh output directory. Validation failures
before runtime execution do not create an output directory.

## Bounded verification

This explicitly requested test performs three real-module smoke/replay operations
and focused negative checks. It makes no generation/API/account calls. Supply a
fresh artifact directory outside the checkout; all fixtures and results stay
there. Existing artifact directories are refused.

```bash
node research/pixelengine-imagen/tools/test-offline-pixelengine.cjs \
  --wrapper "$PIXELENGINE_WRAPPER" --wasm "$PIXELENGINE_WASM" \
  --artifacts-dir /home/astra/artifacts/pixelengine-adapter-smoke-UNIQUE
```

The test checks exact genuine output bytes for a known procedural gradient,
classification, shared-palette frames, opaque timing preservation, source
immutability, hash mismatches, invalid options, mixed dimensions, existing output
refusal and a genuine transparent-image error. `TEST-RESULTS.json` records the
bounded scope. It is mechanical verification, not visual acceptance or hosted
equivalence.

## Declared RPG action inspector

`build-rpg-preview.py` reads the package's declared actions and requires every
selected action in all eight directions. It supports idle, walk, run, punch,
cast, guard, hurt, stun, dash, dodge, jump, land, crouch, knockdown, get_up, death
and interact. Unsupported actions and incomplete/duplicate declarations fail.
The historical six-action package retains J punch, K cast, L dodge, H hurt and
Space in-place walk. Expanded libraries use Z punch, V cast, Shift run, Q dash,
Space dodge, J jump, G held guard, C held crouch, H hurt, T stun, K knockdown,
X death, F interact, R reset and I in-place walk. The UI lists actual declared
actions, supports held buttons, and provides Reset.

```bash
python3 research/pixelengine-imagen/tools/build-rpg-preview.py \
  --package /path/to/package --output /fresh/inspector --check

godot --path /fresh/inspector
```

Defaults are explicit in `bank.json`: jump completes into land, knockdown into
get_up, then idle; punch/cast hold their own configured ready frame. Guard and
crouch stop root movement while held and release into idle/movement. Non-looping
held clips retain their final frame. Interrupt priority is death > knockdown >
stun > hurt; normal actions cannot restart or replace locked one-shots. Death
holds its final frame until reset. Facing locks during one-shots, with independent
aim metadata. There is no collision, damage, invulnerability or weapon behavior.

Dash integrates a fast-start cubic displacement profile; dodge integrates a
smooth accelerate/decelerate profile. Directions normalize before travel, so
cardinal, diagonal and fractional stick inputs cover the configured distance.
Jump stays grounded for the declared `jump_takeoff_delay` (default 0.1s), so the
painted crouch anticipation does not float. After takeoff it moves the ground
anchor separately from a parabolic sprite height and stationary ground shadow;
landing resets height. The delay must be shorter than every jump clip. Travel
integrates only elapsed airborne time, including steps crossing takeoff. These are inspector mechanics,
not proof of painted motion quality. Ground speeds/distances are in inspector
canvas units; the UI scales artwork 3x. Reset returns the preview actor to its initial
ground position below the header.

`--check` runs the actual headless Godot resource writer and validator. The saved
resource is reloaded and every clip's speed/loop and every frame's rational hold,
PNG hash and decoded RGBA hash are checked. Runtime checks cover all declared
actions/directions, fractional clock carry, completion routes, locks, held
release, interruption priority, terminal death, dash/dodge distance and delta
subdivision, jump height/landing, run speed and physical input dispatch. Reports
are retained in the generated inspector alongside invocation logs and a build
receipt. Headless checks do not constitute GPU or human playback acceptance.

A reproducible compatibility check creates a visibly labelled temporary alias
fixture from the historical six-action package. It tests 136 resource bindings
and controller behavior, **not new action artwork**. Both original and expanded
outputs and the aliased fixture are retained for inspection:

```bash
python3 research/pixelengine-imagen/tools/check-rpg-preview.py \
  --package /path/to/historical/six-action/package \
  --output /fresh/regression-output
```

The script also checks rejection of missing bindings, unknown actions and duplicate
directions, plus negative or full-duration takeoff delays. It never calls a provider and leaves the supplied package unchanged.
