# Primary-source workflow notes, checked 2026-10-16

The practical next step is to test coordinated full poses with durable phase ownership, then use generation for the missing paint or in-betweens. This is a proposed application of the sources below, not evidence that any provider has solved our six walks. No provider was called, no models were installed, and the guide/report remain frozen.

Recent means2026-04-16 through2026-10-16 in this note. Dated sources inside that window are identified below. PixelLab's live documentation is undated; its current contents are verified, but it cannot honestly be described as a release from the last six months. Public product/API descriptions establish supported interfaces and advertised behavior, not private model architecture or quality on our art.

## Verified PixelLab distinction

The **undated editor tutorial** recommends starting with one preserved frame and generating two; using custom frame freezing and regional inpainting; rough manual paint/skeleton correction; regenerating from corrected images; and increasing initialization strength during refinement. It also describes two-preserved/one-generated work for established animation. This is an explicitly iterative editor workflow, not eight unrelated still prompts. [Official skeleton editor tutorial](https://www.pixellab.ai/docs/tools/animate-with-skeleton), sections2.1–3, checked2026-10-16.

The **undated current API** has separate contracts:

| Public route | Verified interface fact |
|---|---|
|`animate-with-skeleton-v3` | Reference image plus matching reference skeleton, then3–15 ordered18-joint poses; maximum256px. Coordinates are normalized. Optional depth defaults from a template. Exactly one result per requested pose; reference is redrawn but not returned. No initialization-image, mask, or frozen-frame properties appear in this request schema. |
|`animate-with-skeleton` | Older three-frame window; initialization, masks and initialization strength are present. |
|`interpolation-v2` | Start/end key images plus action. Endpoint and size schema permit16–128px; output described as typically4–8 intermediate frames. |
|`edit-animation-v2` | Edit a supplied sequence. Endpoint prose limits81–256px to four frames, despite the generic array accepting2–16. |

The skeleton-v3 prose incorrectly names a GET estimate call; the actual OpenAPI path is POST. The API advertises version`dev`. The marketing page's broader interpolation size examples conflict with the128px request schema: follow the live schema for planning and validate before any integration. [Official API reference](https://api.pixellab.ai/v2/docs), [official OpenAPI schema](https://api.pixellab.ai/v2/openapi.json), checked2026-10-16. Small field-name evidence is retained in`RESEARCH-EVIDENCE.json`.

PixelLab's public product page explicitly labels the separate PixMiniMax animation route as powered by MiniMax H3. That route is outside this project's stated constraints. This does not identify the private implementation of other routes. [Official API product page](https://www.pixellab.ai/pixellab-api), undated, checked2026-10-16.

## Recent primary techniques worth carrying into our lanes

**Spine4.3, released2026-05-28.** Its sliders can apply a pose/animation state across multiple timelines; examples combine mesh shape, image swaps and draw order. The release adds separately keyed draw-order folders and shared linked meshes across slots. It also exposes volume-preserving constraint scaling. These are useful ways to coordinate a changing limb silhouette and its overlap under one motion control. [Official release article](https://en.esotericsoftware.com/blog/Spine-4.3-released); date independently shown on the [official blog index](https://esotericsoftware.com/blog). The article is recent; it does not imply all underlying rigging ideas were invented in2026.

**Adaptive Interpolation-Synthesis, submitted2026-05-04, accepted SIGGRAPH2026.** The authors combine learned interpolation with direct pose synthesis and a keypose schedule reflecting production data. This is3D keyframe in-betweening integrated with Maya, not a pixel-sprite generator. The applicable idea is to let deliberately authored keys determine the motion, rather than asking interpolation to invent every missing structural event. Its reported productivity result is not evidence for Emberwake. [Authors' paper](https://arxiv.org/abs/2605.02742).

**Sketch2Motion, submitted2026-05-27.** The authors combine skeletal transforms, skinned deformation and a generative motion prior with explicit smoothness/topology/contact constraints. It concerns2D-sketch-to3D animation, not fixed-palette, transparent sprite loops. It supports separating motion constraints from appearance synthesis as a research direction; it does not supply a ready production route or prove inferred hidden joints. [Authors' paper](https://arxiv.org/abs/2605.28394).

The bounded search found these relevant recent primary techniques; it did not establish a recent, turnkey tool that guarantees exact8-frame identity, alternating support and complete boot volumes for our128px art.

## Proposed decision for the current ImageGen lane

This is our application, not a claim about ImageGen implementing PixelLab controls.

1. Use the native128 guide as a motion contract and the current painted cel as identity/material reference. Resolve both opposite contact poses and both passing poses first. Retain A/B source-visible ownership; do not silently convert it to anatomical left/right through an occluded view.
2. Obtain the missing full thigh/boot shapes and changed arm/shoulder planes as pose-specific paint. Keep an approved pose immutable in local storage. If a generation changes unrelated paint, use the local compositor to retain approved source pixels; a preservation request in a prompt is not a hard pixel lock.
3. Work on one short phase gap at a time using its two neighboring painted poses plus the gap's filled guide. This borrows the preserve-neighbors / repair-gap discipline without assuming the built-in tool exposes initialization strength, a skeleton endpoint, or temporal state.
4. Regenerate after rough whole-shape correction only if the correction explains the intended silhouette. More detailed toe prompts are not an alternative to a missing hip/knee/boot progression.
5. Compare the complete eight-cel result to the original at the same0.45s clock before expanding to more characters/views. Accepted keys remain fixed inputs; intermediate failures do not authorize replacing the whole design.

A PixelLab-style18-joint adapter would not fully encode our cuff, heel and toe controls. Our own guide deliberately includes those extra shoe landmarks because a plausible ankle position alone can still yield a poor whole boot. Preserve the filled boot guide and paint checks even if a skeleton service is tried later. No such service call is part of this research assignment.

## Proposed decision for the manual/layered lane

Use a shallow2D rig with source-painted head, tunic, pauldrons, upper arms, forearms/gloves, thighs, cuffs and full boots as distinct owned layers. Keep the body root, hip motion and opposite arm phase on one clock. Author an overlap schedule so near/far attachments change order deliberately at each passing. Use replacement drawings for a boot side, thigh fold or limb foreshortening that the source never exposed; a mesh cannot reveal nonexistent paint.

For this pilot, the useful rig is small: both legs' knee/cuff/sole controls, pelvis loading, shallow torso counterphase, head compensation, and arm swing. Avoid adding a new bone for every paint correction. Keep silhouette corrections as alternate pose drawings keyed to the same phase. Bake eight cels, then paint edge/overlap repairs on those cels. The layered source remains upstream and the cel corrections remain downstream, so a rig edit cannot silently invalidate accepted paint.

Only after the keys read clearly should we test more actual in-between drawings or cadence changes. Contact and engine world motion still require the root's independent checks; neither these sources nor a motion guide proves that runtime acceptance.
