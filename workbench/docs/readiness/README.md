# Operational browser workbench and readiness — v0.5.0

The **Original PixelLab VFX** view runs actual recovered website methods through 46 unchanged pinned factory slices. Choose the authentic retained `slash_arc` or `energy_orb` preset response, change its declared sliders/colour ramp, render in a durable background job and play or scrub the stored frames. Original functions handle recipe validation, control mapping and all 17 procedural layer families. Source and recipe/control hashes remain attached to results and portable editable exports. [Source workflow](../source-faithful/SOURCE-UI.md) records the UI and original-source boundary.

The Workspace indexed editor and scene/track tools are our local supplied-art tools, with their own contracts. Sending source-rendered frames to that editor enables exact local corrections. It does not make the editor a recovered PixelLab implementation. Replication uses available original methods; unavailable methods remain missing, without invented heuristics or substitute local crafts.

Original-art/model comparisons remain held until their analysis, implementation and backend prerequisites are settled. This stage adds no private generator, model-weight training, complete product parity or approved character-animation result. [Current source verification](../source-faithful/VERIFICATION.json) binds the tested source and package; older v0.4 evidence remains historical.

## Launch

```bash
cd /home/astra/projects/pixellab-local-workbench
bash scripts/setup_local.sh
.venv/bin/python -m sprite_workbench --workspace workspaces/web-control/store web \
  --base-dir workspaces/web-control/files --port 8874 --workers 2
```

Open **http://127.0.0.1:8874**. The controller prints a ready event and remains in the terminal until Ctrl+C. The canonical live session uses that Store/base/port. If it is already running, open its URL; use a separate Store, base folder and port for an independent instance. Two job managers must not operate on the same Store simultaneously.

The setup script requires `uv`, requests Python 3.14, installs hashed dependency pins into this checkout's `.venv` and installs the package locally. Node, Godot and LibreSprite remain explicit host dependencies. `lab doctor` checks presence/version; the setup verification action exercises actual renderer, engine and editor paths.

The server binds loopback only. Browser imports/exports are confined to its configured project folder, including resolved and resumed plan paths. Upload external PNG/APNG or editable JSON rather than using paths outside that folder. This local controller is not a public host or operating-system sandbox. The trusted standalone CLI/JSONL routes have different filesystem authority; their base directory resolves paths rather than confining them.

## Run an original VFX recipe

1. Open **Original PixelLab VFX** and load `slash_arc` or `energy_orb`. Each preset displays its retained original response identity; imported JSON remains caller-supplied.
2. Read the original control declarations, then adjust the exposed sliders and colour ramp. Recipe JSON edits require reading controls again. Subject and named image fields accept existing Store raster IDs when required by a supplied recipe.
3. Render and follow the durable source job to completion. The previous result stays available while settings change. Inspect source/control receipts, play or scrub ordered frames, and reopen completed results from the recent list.
4. Download the declared recipe to retain the chosen values, or send the completed sequence to Workspace for local pixel editing. Editable export/import retains the source-control receipt and exact stored frames.

The panel exposes slider/ramp controls used by the retained presets. Other declared control types remain available through the recorded Methods schema. CLI `pixellab-vfx`, the four `local.pixellab.vfx.*` JSONL services, asynchronous `local.pixellab.vfx.render` jobs and plan action `pixellab_vfx` share the original methods. They do not create missing character poses or replace unavailable PixelLab algorithms. [Command grammar](../COMMANDS.md).

## Use and refine an implemented workflow

1. **Inspect the method.** In Methods, choose a registered local service and read its actual request schema. Input fields use JSON. All contracts also show frozen vendor definitions, whose invoke controls remain disabled. A similarly named local method is not silently substituted for one of them.
2. **Load supplied inputs.** In Workspace, upload a PNG/APNG or editable `sprite-edit-project/v1` JSON, or open a complete stored project/history/sequence ID. Sequence-to-project conversion is explicit and can reject unsupported clocks, hidden RGB or differing pivots/directions.
3. **Make precise corrections.** Choose an existing unlocked layer/cel, palette index and frame. Pencil/erase commits a guarded transaction; palette additions and frame-tick edits use the same immutable history. Undo/redo preserves earlier branches. A shared cel changes every frame bound to it; the editor does not silently create missing cels or derive hidden artwork.
4. **Run declared methods.** Use Methods for individual operations or Jobs for a JSON plan. Saving a plan stores a structurally validated declaration without executing it. Submit its actual `plan` object through `local.pipeline`; inspect the returned job's final state and candidate rather than the dispatch envelope alone.
5. **Inspect the result.** Render the selected supplied animation to the Store, open its returned sequence and play it at the stored clock. Review complete frames and adjacent pairs, with body-only and effects-on views where relevant. A generated review page is not evidence that anyone watched or approved it.
6. **Refine and repeat.** Change a method's parameters or plan declaration, use new output paths, or apply a narrow transaction to its result. Keep the prior artifact/history IDs. Repeat the same declared checks so a correction can be traced to its exact inputs and changed pixels.

This loop refines images, settings and explicitly authored motion. It does not train a neural network or make inconsistent independently generated frames into a coherent animation. Scene/track construction currently uses explicit JSON; the browser is not a complete graphical pose/rig/keyframe editor. New humanoid/model experiments still wait for the comparison prerequisites.

The [command reference](../COMMANDS.md) supplies exact CLI, plan, JSONL and HTTP grammars. [Construction](../construction/README.md) lists the twelve editing/exchange methods. [WEB-UI](WEB-UI.md) describes preview, keyboard, palette and responsive controls in detail.

## Where the controls are

| View | Available controls | Important limit |
| --- | --- | --- |
| Original PixelLab VFX | Two authentic retained presets, recipe JSON import/download, original slider/ramp controls, background rendering, playback/scrub, recent results and local editor handoff | Retained source revision only; no private models, all prepared constructors or current server parity |
| Readiness | Submit setup verification; inspect job identity, source fingerprint, checks and blockers | Setup success cannot close unresolved analysis or approve art |
| Flows & grammar | Filter feature flows, commands, grammar, transport, comparisons, interfaces and original requirements; inspect full selected records | Inventory presence is not algorithm or runtime completion |
| Workspace | PNG/APNG/project import, artifact open, existing-cel pencil/erase, exact palette indices/additions, timing, undo/redo, render and preview | No automatic anatomy segmentation, missing views/surfaces, strong poses or new cels |
| Jobs | Load/edit/save plans, submit, poll, cancel/retry and inspect candidate/run artifacts | Cancellation is cooperative; already-written immutable candidates/files may remain |
| Methods | Inspect schemas, edit request JSON, invoke implemented local services, inspect/copy results | Private cloud/model handlers remain unavailable |

The interactive canvas is limited to 1,048,576 pixels. Larger supported projects can use the JSON/native exchange routes without being silently downsampled into the editor. The palette grid shows the first 256 entries; the numeric index control selects higher entries. PNG/APNG upload is bounded to 32MiB and project JSON to 16MiB. Method request bodies have a separate 4MiB limit.

For native refinement, call `local.construction.ase_export` with a project, new output directory and selected animation. Edit the resulting layered RGBA ASE file in LibreSprite, keep its authoritative sidecar/binding and call `ase_import` with both paths. Untouched imports can retain project identity; changed native pixels create a new project and need a new local history. Render with `import_provenance` before making a portable editable bundle. [Exchange rules](../construction/EXCHANGE.md).

## Setup readiness and comparison readiness

`setup_ready` is true only when a retained proof matches the **current package source fingerprint** and its required checks passed: environment dependencies, all eleven local recipe subsets, recipe artifact integrity, exact undo/redo, native editable project identity, fresh-Store sequence/history/native dependency recovery and unchanged source during verification. Every recipe must have its own completed status; duplicate or failed rows do not count as success.

Use **Verify setup** in Readiness, then open Jobs and inspect the returned `local.readiness.verify` job through completion. The diagnostic writes a separate folder under `setup-runs/` in the configured project base and retains its report/artifact. It uses supplied marker fixtures, not new character/model generation. If the source changes after server startup, restart the controller and verify that source version. Old setup evidence cannot certify newly loaded code.

`comparison_ready` additionally requires the individually reconciled analysis and implementation prerequisites. The baseline pins the exact original requirement/command/flow/interface/grammar identities; emptying a blocker summary, dropping records, changing `required_for` or relabeling a partial source answer cannot open the gate. An original question must actually be closed as a whole. [Independent gate review](GATE-REVIEW.md).

**Comparisons remain blocked.** `/api/compare` returns 409 and the comparison control has no original-art/model executor. This does not disable the independently available supplied-art editing/refinement tools or mechanical diagnostics. The CLI supplied-sequence difference tool also does not override the gate or call a provider.

## Analysis that is available and work that remains

The reconciled catalog includes 63 original questions, 23 feature families, 30 transport/lifecycle flows, 28 help commands, 9 documented primitives, 42 grammar claims and 56 conditionals. All 64 cited transport-source file/slice hashes were checked. The documented primitive inventory is complete; the full hosted nested parser/schema remains incomplete. Fifteen help commands have no local equivalent and thirteen have partial local routes.

The historical 111 public operations and 101 captured MCP definitions are separate from the current 112-operation public snapshot. Normal-map, smart palette, finer output grids and template billing changes are pinned current documentation claims, not newly implemented local methods or observed provider behavior. Open the current-drift inspector in Flows & grammar for those exact differences.

The original 63 questions remain unclosed: 18 include source-associated partial answers, 24 need broader runtime evidence and 21 need unavailable server source/disclosure. The older finite source gate only answered its selected named questions. [ANALYSIS-RECONCILIATION](ANALYSIS-RECONCILIATION.md) separates accessible source findings, missing documentation, local implementation gaps and private boundaries.

Remaining prerequisite categories are missing original methods/full flow adapters; incomplete hosted grammar; unsupported prepared VFX constructors; vendor/native runtime, persistence and broader worker/GPU/videoPTS behavior; an executable frozen backend/comparison protocol; and approved humanoid parts/directions/hidden surfaces/strong poses/contact/event timing with complete normal-speed review. Private weights, training data and undisclosed server algorithms cannot be inferred from client selector names. No new image/model comparison is needed to disguise those gaps as complete.

## Verification and performance evidence

Use [current source-workflow verification](../source-faithful/VERIFICATION.json) for exact runtime and result identities, and [latest verification](../LATEST-VERIFICATION.md) for the final package entry point. [Source package proof](../source-faithful/PACKAGE-PROOF.md) describes isolated installation, original-output fixture matching and fresh-Store portable closure.

The v0.4 implementation `846e391` historically passed 430 mechanical tests with zero failures/errors/skips. [Retained JUnit](evidence/TESTS.xml), [test log](evidence/TESTS.log), [controller review](WEB-CONTROLLER-REVIEW.md) and [gate review](GATE-REVIEW.md) retain their original scope. Those results cannot certify later source/UI changes.

The new checkpoint history passed its declared one-/eleven-shared-layer workload gates. At 256×256/24 frames the twentieth edit measured 0.135s/1.420s respectively; the eleven-layer fresh-process cold load was13.802s. Cold verification remains linear and bounded, and this marker benchmark does not approve a humanoid edit/animation session. [History implementation](HISTORY-IMPLEMENTATION.md), [performance gate](HISTORY-PERFORMANCE-GATE.md) and [independent review](HISTORY-INDEPENDENT-REVIEW.md).

Older 214/333-test and installed-package receipts remain linked in [STATUS](../local-replication/STATUS.md) as historical stages. Passing software tests, exact export pixels, browser control checks and art/motion approval are distinct evidence. Two independent complete visual reviews remain necessary for any 9/10 claim.
