# Sprite art pipeline

Methods, requirements, runnable tooling and evidence for creating consistent
game sprites, editing them precisely, animating them and testing them in Godot.
The workflow supports modern shaded sprites as well as low-resolution pixel art.

This repository consolidates the reference-art batches, PixelLab
investigation/local workbench, editable sprite toolkits, approved generic-hero
walk and Emberwake game work. It preserves failed techniques and open gaps.
It does **not** claim complete PixelLab reconstruction or uniformly accepted
eight-direction animation quality.

## Start here

1. **[Handoff for another AI: install, replay and continue](docs/AI-HANDOFF.md).**
2. [Requirements and acceptance rules](docs/REQUIREMENTS.md).
3. [Methods, routes and reproduction commands](docs/METHODS.md).
4. [Current status and unfinished work](docs/STATUS.md).
5. [Model/provider boundaries](docs/PROVIDERS.md).
6. [Environment and tests](docs/SETUP.md).
7. [Source provenance and local evidence](docs/PROVENANCE.md).
8. [Full methods reference catalog](docs/CATALOG.md).

## What is included

| Location | Contents |
| --- | --- |
| [skills/](skills/) | Four complete Codex skills, references, helpers and selected portable fixtures |
| [examples/current-hero/](examples/current-hero/README.md) | Current selected hero: 136 bindings/561 exposures, editable sources, frame viewer and portable Godot rebuild |
| [workbench/](workbench/README.md) | Local UI/CLI, editable projects, job storage, recovered client-method subsets, command grammar and tests |
| [demos/emberwake/](demos/emberwake/README.md) | Original Godot top-down game source, runtime artwork, gameplay tests and production notes |
| [examples/approved-hero/](examples/approved-hero/START-HERE.md) | User-approved historical H3 walk, original native return, bake recipe, editable source and action-method notes |
| [examples/lyra-leg-repair/](examples/lyra-leg-repair/README.md) | Latest ImageGen/painted-part leg repair, precise masks, editable animation and honest review status |
| [research/](research/README.md) | PixelLab findings, construction experiments, authoring programs and mech/Blender extraction methods |
| [provenance/](docs/PROVENANCE.md) | File hashes, original source revisions, import adjustments and local-only evidence index |

## Quick start

For another AI, use the [four skill copies](skills/README.md) or the
[downloadable skills bundle](https://github.com/ACSKamloops/sprite-art-pipeline/releases/tag/handoff-2026-10-22).
The [AI handoff](docs/AI-HANDOFF.md) includes a task prompt, required inputs,
the full production/review loop and the current quality gaps.

Python tooling and local UI:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/verify.py
cd workbench
../.venv/bin/python -m sprite_workbench --workspace workspaces/local/store web \
  --base-dir workspaces/local/files --port 8874
```

Open `http://127.0.0.1:8874`. Use a distinct Store and port if another instance
already runs. The command does not enable a paid motion provider.

Godot demo, with Godot installed:

```bash
godot --path demos/emberwake
```

Rebuild the current character inspector from the bundled snapshot:

```bash
.venv/bin/python scripts/verify_selected_hero.py
.venv/bin/python research/pixelengine-imagen/tools/build-rpg-preview.py \
  --package examples/current-hero/package \
  --output output/current-hero-godot --check
godot --path output/current-hero-godot
```

Use a fresh output for another run. The current snapshot preserves the preferred
walk and includes the latest get-up; it remains below the whole-library9/10
target. No model call or original workstation is needed to inspect/rebuild it.

Preserved Lyra leg-repair comparison:

```bash
python3 -m http.server 8808 --bind 127.0.0.1 --directory examples/lyra-leg-repair
```

Open `http://127.0.0.1:8808/delivery-v4/`. Normal/quarter speed, frame stepping,
native/integer scales, video and editable files are provided. V4 is a candidate
for human timed review, not an accepted replacement for the game's walks.

Install the four skills into a chosen Codex home:

```bash
python3 scripts/install_skills.py --destination "$HOME/.codex/skills"
```

Existing differing skills are preserved; the installer refuses to overwrite them.
The WSL and Windows Codex homes remain separate.

Tests and reconstruction commands make no model-generation requests. Creating
new artwork still requires the chosen image tool and explicit output review.
See [sharing and third-party notices](NOTICE.md) before redistributing contents.

[Current transfer checks](verification/AI-HANDOFF-RESULTS.json) cover fresh skill
installation, the selected character, raw-to-editable recovery replay and a
Godot rebuild outside the original workspace. These are reproducibility checks;
the whole-library9/10 target remains open.

[Original consolidation verification](verification/RESULTS.json): 989 workbench tests
passed (74 conditional skips), 23 editable-toolkit tests passed, the approved
30-frame walk and repaired eight-frame example replayed exactly, and Godot
passed 1,804 behavioral/resource assertions plus 378 route samples. These are
tool/artifact/engine results, not new animation-quality acceptance.

