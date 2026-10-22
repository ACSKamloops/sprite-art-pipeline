# Current hero: portable selected character snapshot

This is the selected package-v4 character, including the latest SE get-up and
the preserved preferred SE walk: 17 states × eight directions, 136 bindings and
561 timed exposures. It includes PNGs, atlases, exact APNGs, editable project/cel
project data and ASE files. It excludes 18 unselected alternative clips.

These are generated character assets and pipeline outputs. The library is
provisional: art reviews are scoped, some states reuse poses, and SE run is an
explicit fast-walk alias. The requested whole-library 9/10 has not been reached.
There is no complete interchangeable-weapon or combat-collision system here.

The [snapshot receipt](package/SNAPSHOT.json) pins the original package-v4
library and this selected-only library. Clip files are byte-identical to the
source; only the library's alternative-clip list and viewer navigation changed.
[FILESET.json](package/FILESET.json) covers every distributed package file.
Original source paths in provenance are historical metadata, not runtime inputs.

## Inspect without a model or engine

From the repository root:

```bash
python3 scripts/verify_selected_hero.py
python3 -m http.server 8910 --bind 127.0.0.1
```

Open `http://127.0.0.1:8910/examples/current-hero/package/`. Select the action,
direction, scale and background; play, slow down or step frames. Each clip links
to its editable source, ASE and exact APNG. The latest recovery is `get_up`, SE.
The character's native stage is 80×80, with declared pivot (40,72).

## Build the Godot inspector

Install the repository's Python environment as described in
[SETUP.md](../../docs/SETUP.md), and provide Godot on PATH:

```bash
.venv/bin/python research/pixelengine-imagen/tools/build-rpg-preview.py \
  --package examples/current-hero/package \
  --output output/current-hero-godot --check
godot --path output/current-hero-godot
```

The output must be fresh. The builder uses repository-relative templates and
the supplied package; it does not read the original artifact workspace. Its
checks cover resource pixels/clocks, controls, state transitions and root motion.
The inspector has no collision, damage or invulnerability. Matching export
templates are needed if you subsequently export a Godot Web build.

Read [the AI handoff](../../docs/AI-HANDOFF.md) for the complete production flow,
skill installation, model requirements, review rules and the next repair targets.

The [get-up source study](recovery-study/README.md) also includes the actual
ImageGen inputs/prompt/raw, frozen owner maps, source-part edit journal and a
portable raw-to-ten-frame replay. It reproduces the selected frames exactly;
it does not promise identical output from another generation call.
