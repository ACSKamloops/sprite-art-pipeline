# Observed effects and prompt quality comparisons

Version 0.10.0 makes 105 observed prepared-effect instances and three actual subject examples usable in Original PixelLab VFX. The original two presets remain separate. The packaged library retains authentic recipe data, source identities, response and native-atlas hashes, all 350 default controls, and per-frame native/source RGBA hashes. Its own R9 subject PNG is checked against the bytes returned in the three captured subject recipes.

An independent reviewer executed all 108 instances through the registered local service: **1,224 native frames and 6,648,075 RGBA pixels matched exactly**. Three subject examples also survived editable export and fresh-Store import. This establishes rendering and preservation for retained instances. It does not recover arbitrary private prepared constructors, automatic fitting or off-default cloud behavior. Three defaults are blank without a configured subject; choose their separately captured subject examples for visible output.

The UI supports original sliders, ramps (including retained custom arrays), boolean toggles and selectors with typed values. A reproduced asynchronous restore bug was fixed: a late recent-render or file response cannot overwrite a newer library choice or manual recipe edit. Source normalization, control binding and rendering functions were not rewritten.

## Prompt flow and quality

Evidence lives in `/home/astra/artifacts/pixellab-remaining-methods-20261014`.

- `prepared-parameter-coverage/extended-flows/PROMPT-FLOW-TRACE.md` traces actual raw and rewritten prompts, generator flags, manual-edit ownership limits, and 38 checked source slices. Explicit enhancement and remote automatic `enhance_prompt` are separate branches.
- `prompt-quality-comparison/PROTOCOL.json` freezes an original/rewrite comparison using the same Pixen settings and seed, plus an external imagegen comparison. Retained raw baselines avoid unnecessary extra calls. One new Pixen request consumes the exact actual rewritten string. The raw vendor baseline is older, so checkpoint/time drift remains a confound.
- `observed-library-ui/art-review` and `prompt-blind-review-2` independently review all four final 128-pixel candidates, enlarged with nearest sampling and composited on real black/white/gray backgrounds. Their rankings disagree slightly between the two Pixen sprites; both reject the external rewritten-prompt result for the requested sprite style. Detailed rendering is not automatically a quality improvement.
- PixelLab's actual rewrite omits the explicit pixel-art instruction. It remains sprite-like through Pixen, but produces a realistic illustration through the generic image generator. This is observed model-dependent behavior; private templates and weights remain unknown. The failed result is retained, rather than accepted after downsampling.
- `still-comparison/local-128-v2-binary.png` is a separately reviewed useful refinement using a vendor style reference. Its additional reference and changed prompt exclude it from the matched-prompt comparison.

All 350 controls were additionally exercised against the complete original source loader for value admission, normalized recipes, three rendered streams and exact source frame durations. Nineteen light controls and six particle controls are unchanged without a subject; their qualified equality is not discriminating visual proof. The 105 size wrappers are mapped separately. Blanket 455-case live-cloud expansion was deferred because it would repeat tests without resolving missing fitting behavior; the two selected live probes address a unique selector and a duplicate size name.

All 24 previously planned missing route and extension cases have actual API responses, including normal maps, isometric tile shapes, map objects, caption/prompt tools, object review/state/animation/export and Wang tilesets. Their local learned generation counterparts remain unimplemented. The normal map has real Godot moving-light/flat-normal controls. The object animation preserves five returned frames and opens the chest; it does not complete the requested open-and-close cycle. The cliff result returns 25 tiles, and its first failed retrieval remains beside the successful retry. The sidescroller's stored connection IDs reference missing tiles. These defects and limits remain separate from successful imports.

## Reproduce locally

```bash
cd /home/astra/projects/pixellab-local-workbench
.venv/bin/python -m sprite_workbench --workspace /tmp/my-vfx-store \
  pixellab-vfx observed_catalog /path/to/empty-object.json
```

The request file contains `{}`. Render a visible subject example with the `render_observed` method and `{"id":"observed.subject_hurt_flash"}`. CLI, JSON Lines channel and HTTP share the same registered services. The browser picker groups original presets, observed defaults and subject examples.

For an independent browser instance, use a fresh Store and input directory:

```bash
mkdir -p /tmp/my-vfx-inputs
.venv/bin/python -m sprite_workbench --workspace /tmp/my-vfx-store web \
  --base-dir /tmp/my-vfx-inputs --port 8878 --workers 4
```

No model provider is enabled by these commands. No publication was performed. Animation anatomy, directional consistency and normal-speed motion still require separate acceptance; still-image scores and exact VFX replay do not establish a production character-animation pipeline.
