# Pipeline skills for another AI

These are complete, current skill copies with supporting scripts, references,
toolkits and selected fixtures. Start with [the AI handoff](../docs/AI-HANDOFF.md).

| Folder | Purpose |
| --- | --- |
| [reference-art-production](reference-art-production/SKILL.md) | Art briefs, inspected references, collections, claim-next workers and export review |
| [imagegen-sprite-animation](imagegen-sprite-animation/SKILL.md) | Consistent painted keys, directional banks, licensed motion guides and source-part refinements |
| [sprite-construction-editing](sprite-construction-editing/SKILL.md) | Layered source construction, guarded pixel edits, undo/replay and editor exchange |
| [sprite-animation-pipeline](sprite-animation-pipeline/SKILL.md) | Rational animation clocks, media exports, component tracks and Godot integration |

From a repository clone:

```bash
python3 scripts/install_skills.py --destination "$HOME/.codex/skills"
```

The installer skips identical copies and refuses to overwrite differing local
skills. Choose a fresh destination to compare an existing installation. Other
AI clients can read the Markdown directly or use their own skill directory.
Relative companion links assume these four folders remain siblings.

[The downloadable skills bundle](https://github.com/ACSKamloops/sprite-art-pipeline/releases/tag/handoff-2026-10-22)
includes these same directories, the installer, a standalone installation guide
and a SHA-256 manifest. No model credential or original workstation is required
to install files and replay the bundled offline examples. New image generation
requires an actual image tool; the environment-provided OpenAI `imagegen` tool
and its system skill are not redistributed here. Editors, Godot, Blender,
codecs and licensed source models are supplied separately as each route needs.

[INDEX.json](INDEX.json) lists entrypoints and external capabilities. Full
historical evidence and every failed experiment are not bundled into the skills;
their references identify the available portable examples and local-only cases.
