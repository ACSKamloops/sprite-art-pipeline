# Local sprite workbench

This implements the accessible deterministic and supplied-art portions of our PixelLab investigation in one local tool. It provides immutable image/document storage, guarded pixel editing, preparation, explicit layered animation, procedural effects, durable jobs, candidate libraries, editable exchange and Godot export. It does **not** include PixelLab's private generative models. Artwork and motion quality are unreviewed.

Start with this file, then [coverage and remaining work](docs/COVERAGE.md), [command grammar](docs/COMMANDS.md) and [source-analysis index](docs/ANALYSIS-INDEX.md). The source analysis and original failed experiments remain separate from this implementation.

## Run locally

Python3.11+, NumPy, Pillow, jsonschema and Node are required. Godot is needed for the engine checks. The current WSL environment already has these. From this checkout:

```bash
python -m pip install -e .
cp -r examples/supplied-motion /home/astra/projects/my-supplied-motion-test
sprite-workbench --workspace workspaces/my-test run /home/astra/projects/my-supplied-motion-test/plan.json
```

The example writes `output/body/` and `output/composed/` beside the copied plan. Each contains exact frames, a sheet, rational timing manifest, APNG, editable artifact closure, a Godot project and a frame/pair/playback review. Open `review/review.html` locally, or open `godot/project.godot` in Godot. These are asymmetric diagnostic markers, not proposed character art. No provider calls or credits are used.

Use a fresh output directory for another execution; existing files are preserved. A failed run returns a structured error, retains its run receipt and never silently becomes a success. Unsupported preview formats are recorded; exact PNG/manifest remain authoritative. Explicit `allow_unsupported_formats:true` acknowledges an unsupported requested format rather than marking it passed.

```bash
python scripts/verify_workbench.py --output runs/my-verification
python -m pip wheel --no-deps --no-build-isolation . -w dist
```

The wheel includes frozen contracts and the pinned JavaScript renderer. It still requires the declared Python dependencies and a Node executable. Installation does not contact PixelLab or supply its private handlers.

## Inputs needed for actual character animation

Supply approved native-resolution artwork, named directions, full-canvas registration/pivots, owned part masks, explicit anchors and strong poses or tracks with durations. Paint hidden surfaces and missing views deliberately. Provide palette/protection policies and event timing separately from visual artwork. A frontal still does not contain a back view, hidden anatomy, gait, weapon contact or authentic in-between poses.

Parts move under explicit local transforms and sampled tracks. You can replace an individual cel, change an anchor/key, or apply expected-color pixel edits without regenerating the whole animation. Every edit retains its parent, change list, source pixels and clock. Rotation/resampling may still require hand correction at native size; mechanical success does not establish good anatomy or movement.

The sequence can be reopened in a fresh Store from its editable export, including original imported bytes, preparation images/references/masks, layered sources, tracks, edits and effect recipes. Cross-run raw raster IDs do not magically identify an original encoded file: include explicit source-sequence lineage if that identity is needed.

## Acceptance discipline

Check all ordered frames, adjacent pairs and replay/loop seam at native and integer scales. Watch complete body-only and effects-on playback at the declared clock. Independently inspect directional identity, volume, grip, exposed seams, ground contact, clipping and action readability. Record exactly which artifacts were viewed. Generated review pages and automated engine checks are not proof that a person/AI watched the motion or rated it9/10.

The next art/model comparison must freeze inputs, strong poses, clocks, baseline hashes, expected behaviors and failure criteria before running. H3/backend testing remains after the outstanding comparison prerequisites; credentials have not been read during this implementation pass.
