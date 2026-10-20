# Local sprite workbench

Version **0.5.0** exposes actual recovered PixelLab browser VFX code through an **Original PixelLab VFX** workspace. Load either authentic retained `get_preset` response (`slash_arc` or `energy_orb`), adjust its declared sliders or colour ramp, render asynchronously and play the stored frames. The 17 procedural layer families execute unchanged source functions for validation, controls and rendering; 46 pinned factory slices carry original-source hashes and ranges. [Source workflow](docs/source-faithful/SOURCE-UI.md) and [control provenance](docs/source-faithful/SOURCE-CONTROLS.md) describe the boundary.

The local indexed editor, scene/track plans, storage, jobs and export tools remain available for supplied art. They are our local implementations with their own contracts. PixelLab replication paths use recovered original methods; an unavailable original method stays unavailable. Invented heuristics or similarly named local crafts do not stand in for PixelLab behavior. Private model generation, complete product parity and accepted character-animation quality remain unresolved.

See [current source-workflow verification](docs/source-faithful/VERIFICATION.json) and [latest verification](docs/LATEST-VERIFICATION.md) for exact tested source and package identities. Earlier v0.4 test/browser/package receipts remain historical evidence. Passing mechanics does not close the **63 original analysis questions**, the incomplete hosted grammar or artistic review. [Coverage](docs/COVERAGE.md) records those limits.

## Open the local controls

From the canonical checkout:

```bash
cd /home/astra/projects/pixellab-local-workbench
bash scripts/setup_local.sh
.venv/bin/python -m sprite_workbench --workspace workspaces/web-control/store web \
  --base-dir workspaces/web-control/files --port 8874
```

Open **http://127.0.0.1:8874**. Keep the server terminal running; stop it with Ctrl+C. The existing live controller may already use this port and Store. Use another port and a separate Store for an independent instance; do not run two managers against one Store.

The setup script creates a dedicated Python 3.14 environment from hashed dependency pins. The package supports Python 3.11+, but that script specifically requests 3.14. `uv` must already be available. Node, Godot and LibreSprite are separate host dependencies; actual setup verification exercises them instead of treating version probes as execution proof.

- **Original PixelLab VFX:** select a retained original preset or load recipe JSON, read original controls, change sliders/ramps, render, scrub/play frames, reopen a completed result, download the declared recipe or send the sequence to the local editor. Rendering retains source, recipe and control hashes; editable export includes the control receipt.
- **Readiness:** run source-bound setup diagnostics, inspect their job and read the remaining comparison blockers.
- **Flows & grammar:** inspect 63 requirements, 23 feature families, 30 transport flows, 28 commands, documented grammar and current public API drift.
- **Workspace:** upload PNG/APNG or editable project JSON; edit supplied indexed cels, palette entries and frame holds; undo/redo and render a stored animation.
- **Jobs:** save an explicit local plan, submit it and inspect durable results, cancellation or retry.
- **Methods:** inspect exact bound request schemas and invoke implemented local services. Captured vendor contracts remain unavailable.

`setup_ready` means the local diagnostics passed for this exact package source fingerprint. **`comparison_ready` remains false** while analysis, grammar, implementation and backend prerequisites remain unresolved. Restart the controller after package-source changes and verify again. The comparison button and `/api/compare` do not run original-art/model experiments. Supplied-art editing and mechanical diagnostics are separate available operations.

See [readiness and browser operation](docs/readiness/README.md), [CLI/plan/HTTP grammar](docs/COMMANDS.md), [construction editing](docs/construction/README.md), and the [complete handoff](docs/consolidation/START-HERE.md).

The original VFX panel exposes the sliders and ramps declared by its two retained presets. Other method parameters and scene/track plans use their explicit JSON schemas; this is not a graphical rig/pose authoring system. Workspace provides direct pencil/erase, exact palette-index selection, palette additions, frame timing and undo/redo for existing supplied cels. Changing a method's inputs or editing its output is refinement, not training model weights. Unsupported captured methods remain unavailable rather than falling back to a different algorithm.

## Repeat an existing diagnostic

```bash
.venv/bin/sprite-workbench lab doctor
.venv/bin/sprite-workbench lab replay --output runs/my-local-replay
.venv/bin/sprite-workbench lab verify-run runs/my-local-replay
```

Choose an absent output directory. The eleven F01–F11 recipes use supplied diagnostic markers, exact clocks and explicit positive/negative checks. Their local `index.html` links receipts, full frames, adjacent pairs and playback pages. The recipes cover bounded portions of the broader [comparison specification](docs/WHOLE-FLOW-COMPARISONS.md); they do not generate or rate character art.

For a declared supplied-motion example, copy `examples/supplied-motion` to a fresh folder and run its `plan.json` using the [command guide](docs/COMMANDS.md). Existing output directories are preserved. A failed or cancelled run can retain immutable candidate artifacts and files for inspection; it does not roll back the entire Store or silently become a success.

## Editing and animation capability

The construction channel retains indexed palettes, aliases, layers, shared cels, guarded transactions and portable undo history. Version 2 history avoids repeatedly compositing the entire old journal during warm editing, while fresh-process loads still verify the complete retained history. The declared 256×256/24-frame benchmark passed for one and eleven shared layer cels; the eleven-layer cold load remained about **13.8 seconds**. [Measurements and limits](docs/readiness/HISTORY-IMPLEMENTATION.md).

Explicit scene/track methods can move supplied parts and sample authored poses. Native exchange uses layered RGBA ASE plus an authoritative sidecar. Editable exports retain typed source, project and history dependencies; PNG alone is not an editable rig. Events, ground pivots and contact landmarks remain metadata rather than implemented Godot event/contact logic.

Useful character animation still needs coherent registered directions, deliberately painted hidden surfaces, owned parts, strong key poses, correct overlaps/grip/contact and normal-speed review. A frontal still cannot supply unseen artwork or a convincing gait by itself. Independent visual reviews of complete body-only and effects-on animation remain required before any 9/10 claim.

## Analysis and experiment boundary

The [reconciled catalog](sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json) preserves every original question. Its 18 source-associated, 24 runtime-only and 21 private-server questions remain unclosed as whole requirements. The complete documented nine-primitive table is available, but the hosted nested drawing grammar still has missing rules. Fifteen help commands lack local equivalents; thirteen have partial local routes. Historical 111 public/101 MCP definitions remain separate from the current 112-operation public snapshot.

The next work is resolving or explicitly settling those prerequisites and acquiring missing original methods before our own art/model comparisons. Local editor improvements are tracked separately from source replication. Image generation, H3/provider testing and external publication were not performed by this implementation stage. Historical failed animations and earlier test/package receipts remain preserved as dated evidence.
