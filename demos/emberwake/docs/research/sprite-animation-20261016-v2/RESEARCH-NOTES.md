# Recent sprite animation research, checked 2026-10-16

This is a source study, not an installed tool, executed model, art score or
evidence of PixelLab's private implementation. Existing project restrictions
still exclude H3 and local generative models.

## Sprite-specific interpolation preprint

[Alonso and Patow, submitted 2026-10-12](https://arxiv.org/html/2610.16423v1)
studies learned midpoint interpolation with explicit alpha handling and
sprite-specific losses. Its reported comparison uses 42 test triplets. The
authors disclose unavailable training data, baselines not retrained on the
sprite dataset, no formal perceptual study, and no full-sequence temporal
evaluation. Extreme deformations remain a failure case. These are reported
results, not a reproduced benchmark or a production animation guarantee.

Our inference: alpha compositing, silhouette detail and occlusion should be
checked separately from motion correspondence. This supports inspecting every
new bridge and the full cycle; it does not justify increasing frame count or
replacing an anatomical drawing with a warped image. We have not downloaded
or run its model. Our earlier DIS/Farneback tests remain failed or tied for
their exact parameters.

## Public ImageGen, editor and Godot example

[SPA's hybrid wizard example](https://github.com/aigengame/aseprite-automation/tree/ee2ea8f027bafdbed4f040c8288a1095b287e8b8/examples/wizard_cast_v2)
at commit `ee2ea8f027bafdbed4f040c8288a1095b287e8b8` keeps generated
concept/key-pose inputs, explicit preparation, finite motion assembly, native
editable documents and Godot exports. Its final human acceptance is marked
pending. The repository needs a separate Aseprite installation; LibreSprite
compatibility has not been established here. No package was installed or run.

Source inspection of `art.py` confirms pose selection by authored frame ranges,
smoothstep position curves with explicit integer rounding, and independent
accessory/effect placement. `recipe.json` names phase timing, pose anchors,
attachment points, export crops and the gameplay emission frame. `prepare.py`
actually thresholds alpha and maps to a declared palette. Those last two are
example choices, not rules for our softer modern RGBA characters.

Our inference: keep drawing selection, local attachment motion, world travel
and gameplay events distinct. Preserve recipe and editable pixels so a model
can be replaced without changing animation semantics. Our portable Brann
replay already demonstrates this boundary with its own editor and exact
clock; the source study provides an independent workflow comparison, not
additional acceptance points.

`FETCH-RECEIPT.json` records six read-only source downloads, the commit, byte
counts and hashes. `spa-source/LICENSE` is the repository's fetched license.
Raw images and large example assets were not downloaded.

## Immediate application to the three active art lanes

1. Use one filled four-key guide with persistent leg owners and coherent body
   paint. Inspect actual returned contact and raised-boot roles before bridges.
2. Preserve the raw sheet. Clean only identified unwanted fringe and inspect
   light/dark/game backgrounds, both stage borders and mirrored destinations.
3. Use complete visible chains for replacement contacts. Paint newly exposed
   material when no supplied plane can represent it. A source map proves
   provenance, not anatomy.
4. Retain exact clock, stage, pivot and conditional mirror rule. Compare every
   neighboring pair and the wrap at native and intended display size.
5. Freeze an anonymous full-cycle packet before independent art review.
   Reviewer chronology inspection, human continuous playback, engine sampling
   and physical contact remain separate evidence.
