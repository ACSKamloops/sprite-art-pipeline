# Start here: continue the sprite pipeline with another AI

For a self-contained message to paste into another AI, use
[Message for the next AI](MESSAGE-FOR-AI.md). This document is the detailed
continuation guide.

This repository contains the methods, all four pipeline skills and a portable
snapshot of the current generated hero. Read [AGENTS.md](../AGENTS.md),
[requirements](REQUIREMENTS.md) and [current status](STATUS.md) before changing
art. The current target is 9/10; it has **not** been achieved across the library.

## Obtain the files

```bash
git clone https://github.com/ACSKamloops/sprite-art-pipeline.git
cd sprite-art-pipeline
```

HTTPS cloning this public repository requires no account credentials. The
[handoff release](https://github.com/ACSKamloops/sprite-art-pipeline/releases/tag/handoff-2026-10-22)
also provides a skills-only ZIP with an installer, file hashes and instructions.
The complete current character lives in
[examples/current-hero](../examples/current-hero/README.md); it is included in a
normal clone, with editable sources and a browser frame viewer.

## Install or read the skills

```bash
python3 scripts/install_skills.py --destination "$HOME/.codex/skills"
```

The installer preserves differing existing skills. Choose a fresh destination
to compare versions before merging an existing installation. Keep WSL and
Windows Codex homes separate. Other AI clients can read the Markdown directly
or copy these directories to their own supported skill location. Installing
files does not add a model, editor, browser connector or image-generation tool.

| Skill | Load it for |
| --- | --- |
| [reference-art-production](../skills/reference-art-production/SKILL.md) | Briefs, reference selection, consistent collections, claim-next workers and source/export review |
| [imagegen-sprite-animation](../skills/imagegen-sprite-animation/SKILL.md) | Painted directional keys, authored-motion guides, source-part repairs and controlled comparisons |
| [sprite-construction-editing](../skills/sprite-construction-editing/SKILL.md) | Layer ownership, precise guarded pixel edits, undo/replay and editable editor exchange |
| [sprite-animation-pipeline](../skills/sprite-animation-pipeline/SKILL.md) | Rational clocks, APNG/video export, component tracks and actual Godot validation |

Load the relevant entrypoint and follow its reference links as needed. Do not
load all historical investigations into the context at once. These four folders
are complete copies, including their own helpers and portable fixtures.
[The skill index](../skills/INDEX.json) records dependencies and entrypoints.

## Run the current work without generating anything

Follow [setup](SETUP.md) for the hashed Python environment. Pillow is sufficient
for the current character integrity check and preview builder; the frozen-map
fixture also needs NumPy. Creating new warp triangulations needs SciPy.

```bash
bash scripts/setup.sh
.venv/bin/python scripts/verify_selected_hero.py
.venv/bin/python skills/imagegen-sprite-animation/scripts/source_warp.py replay \
  skills/imagegen-sprite-animation/assets/source-settle-fixture/settle.json
.venv/bin/python examples/current-hero/replay_recovery.py \
  --output output/my-recovery-replay
.venv/bin/python research/pixelengine-imagen/tools/build-rpg-preview.py \
  --package examples/current-hero/package \
  --output output/my-hero-inspector --check
godot --path output/my-hero-inspector
```

Use a fresh output name for another build. Godot 4.7.2 is the recorded/tested
baseline, not an assertion about the latest upstream release. `--check` runs
actual engine resource/input/state checks when Godot is installed. It does not
rate art. Browser Web export additionally needs matching Godot export templates.

The current snapshot has 17 states, eight directions and 561 exposures across
136 selected bindings. Its preferred SE walk remains unchanged. Some states
deliberately reuse poses; SE run is an explicit faster walk, not new running
art. The latest SE get-up has ten exposures over 1.2 seconds. Independent
ordered-still reviews remain around 7–7.5/10, with normal-speed human review
distinct. Collision, damage, invulnerability and interchangeable weapons are
not implemented by this character inspector.

## Create or refine art, step by step

| Step | Input and operation | Save and verify |
| --- | --- | --- |
| 1. Freeze the brief | Actor/style, native size, camera, action/view matrix, equipment, pivots, timing, intended engine | Immutable preferred examples and a list of missing/reused/unreviewed bindings |
| 2. Assign reference roles | Inspect identity, style, pose, material and edit-target images separately | Ordered paths, actual hashes and observations; missing surfaces remain unknown |
| 3. Paint useful keys | Use the selected image tool with exact reference roles; request complete connected figures | Actual prompt, inputs, raw return, provider and measured dimensions/alpha |
| 4. Register once | Use a declared sheet/clip transform; diagnose grid intrusion before cropping | Source ownership, inverse coordinate maps, framing and protected-region checks; no per-frame auto-fit |
| 5. Construct and edit | Reuse compatible owned parts; author missing paint explicitly; use guarded pixel operations | Editable project, literal journal, source hashes, undo/replay and actual changed pixels |
| 6. Define the clock | Order poses with positive rational holds, loop/one-shot behavior and authored events | Manifest, exact APNG, editor timing sidecar and decoded-frame checks |
| 7. Compare fairly | Preserve old onsets and duration for a bridge test; use repeated old keys as its control | Every pose/adjacency, entry/exit/wrap, native size and integer enlargement on contrasting backgrounds |
| 8. Review and integrate | Freeze review inputs; obtain independent critique when requested and human normal-speed judgment | Scoped findings and scores, retained rejected trials, then actual editor/Godot/browser receipts for the chosen version |

For many subjects, use the real
[claim-next runbook](../skills/reference-art-production/references/batch-runbook.md).
It initializes a plan, approves inspected references, reserves jobs with exclusive
tokens, saves successful tool receipts, publishes one stable review snapshot and
records acceptance by export hash. Its `generated` state is not `accepted`.
One writer owns manifests. Authorized agents need separate checkout/ownership
areas; never let two agents edit one checkout.

For small compatible-view movement, use
[source-pixel refinement](../skills/imagegen-sprite-animation/references/source-pixel-refinement.md).
It has real map replay/rebake commands. Keep complete cuffs/boots/head owners,
but inspect neighboring joints too: a protected boot does not protect a knee.
Newly exposed cloth is explicit underpaint, not recovered hidden source pixels.

For linked whole-body support, use
[authored-motion guides](../skills/imagegen-sprite-animation/references/authored-motion-guides.md)
when suitable licensed 3D motion is available. The Blender helper requires a
supplied GLB/license and a real standing reference. Head-only scaling is not a
general anatomical retarget. Keep one camera; do not fit run, attack and idle
independently to the same height. Verify painted pose compliance after generation.

For precise changes, use the construction skill's real toolkit APIs and
[editor workflow](../skills/imagegen-sprite-animation/references/source-pixel-refinement.md#literal-reversible-pixel-repairs).
Exporting an ASE is different from opening/saving it with LibreSprite. Integer
milliseconds in that editor are a preview; the rational manifest stays authoritative.

## Model and evidence boundaries

For the earlier investigation and command/flow findings, start with these
curated entrypoints rather than reading every dated experiment folder:

- [PixelLab investigation handoff](../research/pixellab-investigation/HANDOFF.md).
- [Workbench UI/CLI](../workbench/README.md) and
  [report catalog](../workbench/docs/consolidation/REPORT-CATALOG.md).
- [Question-by-question reconstruction catalog](../workbench/sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json).
- [PixelEngine/ImageGen comparison and adapter](../research/pixelengine-imagen/README.md).

The user's “imagen” means built-in **OpenAI ImageGen**. Its system skill/tool is
environment-provided and is not included here. Another AI needs actual image
generation/editing capability to create new paint. The workbench can prepare
prompts and import results; copying skills does not connect a generator.

H3/MiniMax and local generative models are disabled for current production.
Their older code/results are historical evidence, not an instruction to enable
them. No setup, replay, installer or CI step should submit provider jobs.

PixelLab/PixelEngine findings inform comparisons and exposed client techniques.
Private model weights, hidden prompts and complete server implementations were
not recovered. The authored-motion guide route is our tested method, not a
claim that a provider uses that exact implementation.

The current character package and portable fixtures work without the original
`/home/astra` tree. Historical notes/scripts can retain local paths and omitted
raw inputs; [provenance](PROVENANCE.md) distinguishes those cases. The full
authenticated investigation archives, raw browser captures and all rejected
art branches are not distributed. Do not claim they are available from a clone.

The [get-up source study](../examples/current-hero/recovery-study/README.md) is
explicitly included: actual ordered references, prompt/raw, ownership maps and
a guarded edit journal. Its replay reconstructs all ten current frames and holds.
The supplied geometry image is derived from licensed CC0 motion with its notice
included; rebuilding that 3D guide still needs the separately supplied GLB.

## Next useful work

First inspect the newer [recovery study](../examples/recovery-refinement-20261023/README.md)
and its recorded human rejection/leg repair. It replays into a separate candidate
package, preserving the snapshot below. Do not resume from the old still8.2
score as if it were human acceptance.

1. Improve the get-up's entry, overlapping boots and hand-to-feet load transfer.
   Preserve its literal downed/neutral endpoints and the preferred walk.
2. Repair the S fall-to-rise support acquisition separately. Do not treat every
   unequal endpoint as a fault.
3. Create genuine SE run phases if needed; keep the current fast-walk alias
   explicitly labeled until new art passes its own review.
4. Establish common character/camera calibration before extending 3D guides
   across actions. Review all other directions independently.

Read [the action findings](../research/pixelengine-imagen/ACTION-SET.md) for exact
history and failed approaches. Do not average packet scores, inherit one action's
acceptance across the library, or call hash/engine checks a visual 9/10 pass.

## Copy this task to another AI

> Read AGENTS.md, docs/AI-HANDOFF.md and docs/REQUIREMENTS.md. Use the four skills
> under skills/ as needed. Start from examples/current-hero/package and preserve
> its preferred SE walk. Verify the snapshot and build a fresh Godot inspector
> before editing. Use built-in OpenAI ImageGen plus explicit source-part/pixel
> repairs; do not enable H3 or a local generative model. Improve one demonstrated
> defect with frozen inputs, a fair control and scoped visual review. Keep all
> new outputs separate, retain rejected trials, and report art acceptance and
> file/editor/runtime evidence separately. The 9/10 library target remains open.
