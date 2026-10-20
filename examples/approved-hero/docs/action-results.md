# Same-hero unarmed action results

The existing walk remains user approved and unchanged. New action candidates passed scoped independent visual review and have exact PNG/APNG exports. They are ready for local review, with no new human acceptance or finished gameplay claim.

Open the local [jump](http://localhost:8889/game-ready-v6/current-project/work/action-production-v1/viewer.html?clip=jump_latest) or [punch](http://localhost:8889/game-ready-v6/current-project/work/action-production-v1/viewer.html?clip=punch_latest). The player supports native/2x/4x, slower playback, frame stepping, previous-pose overlay and contrasting backgrounds. One-shots stop on the final pose; Play restarts a completed action. Earlier experiments remain labeled separately.

## Current candidates

- `work/action-production-v1/jump-candidate-portable-v2/manifest.json`: 55 native 192-square PNGs, each1/24s, duration55/24s, non-looping. Explicit source28..82 from the complete second H3 return; no individual fitting, global resizing or pixel redraw. Review: `work/jump-art-review-v2/REVIEW.md`.
- `work/action-production-v1/punch-candidate-portable-v2/manifest.json`: 32 native 192-square PNGs, each1/24s, duration4/3s, non-looping. Explicit source30..44 plus50..66. This omits an unwanted embedded flash and some held samples. Edge-connected black background removal changes alpha only; every source RGB value remains exact. True hidden black contours cannot be recovered unambiguously. Review: `work/punch-refinement-review-v2/REVIEW.md`.
- Exact lossless playback: `work/action-production-v1/jump-apng-v2/animation.apng.png` and `punch-apng-v2/animation.apng.png`; each receipt verifies every decoded RGBA frame and rational hold. These are single-play presentations, not action-loop approvals.

## What was tested and learned

Both actions share a frozen authored primitive rest, camera, proportions and shoe controls. Visual key gates rejected fused boots and a pointing-like punch before full rendering. The final five-second guides contain160 actual32Hz frames; source geometry, timestamps and lossless decode were checked separately from drawing quality. These primitives specify motion; they are not recovered hero models.

Four H3 video calls tested two appearance references against the same punch/jump guides. All complete returns were retained:124 frames at24Hz, duration31/6s. The second pair changed only the appearance image; request comparisons prove guide/prompt/other fields unchanged. Stochastic generation prevents a causal claim about private model internals.

The first punch inherited a walking-style rest and held its extended arm too long. The first jump was oversized. A fixed whole-clip scale correction and a separate punch timing repair passed targeted review, but the later neutral-input returns provide more suitable planted rests. The second jump retained native detail and needed no scale correction. The second punch needed its black background and added flash handled explicitly.

Two built-in ImageGen still experiments produced ready/punch designs. The ready candidate supplied the second pair's appearance input. The punch still remains a design experiment: its fixed normalizations differed in scale and potentially striking arm. It is not an animation.

The existing lossy MP4 checker rejected the first refined clips because nearly identical source drawings could not be classified distinctly after compression. Those videos are not passed deliveries. PNG/player and verified APNG exports are authoritative here. The portable staging helper copies exact PNG bytes and preserves native lineage when an exporter requires all frames beneath the manifest folder.

## Remaining work

These reviews reconstruct chronology from decoded frames and rational timing; they do not claim human normal-speed perception. Human playback feedback is still needed. Actual walk/ready/action transitions, interactive attack events and interruption, state-driven jump physics/contact, gameplay GPU playback and interchangeable weapon/grip/occlusion tracks remain separate work. The first actions contain no weapon artwork. Existing attachment examples keep unmeasured anchors null.

Actual construction, forward export and LibreSprite save/reopen passed for all87 candidate frames. Fresh Godot4.7.2 imported two atlases and saved/reloaded two non-looping SpriteFrames animations with exact regions and holds, zero errors. Sources and executed receipts are under `work/action-editable-delivery-v1`; resource import does not establish gameplay or GPU playback. `jump/project.json` and `punch/project.json` there are the editable flat-cel projects; adjacent `roundtrip.aseprite` files have the native-clock sidecars.

## Reproduce

Provider requests, input media, literal prompts, root gates, sanitized responses and complete videos are retained under `providers/minimax_h3/jobs/{jump,punch}-v1` and `{jump,punch}-v2-neutral`. Never duplicate an already-submitted job. Runtime credentials remain outside this package.

`work/action-production-v1/inspect_native.py` and retained bake recipes reproduce full native sampling through `tools/bake_native_sprites.py`. Black punch matting has a separate tool/recipe/proof under `work/black-background-matte-v1`. Source-index selections, masks and all omitted frames remain retained. `stage_manifest.py` creates portable exact-byte copies; `tools/animation/scripts/exact_apng.py` builds lossless timed previews.

The installed sprite animation and construction skills now document these tested techniques and limitations. This is an authored local workflow informed by observed vendor behavior; it does not recover private PixelLab weights or establish complete feature parity.
