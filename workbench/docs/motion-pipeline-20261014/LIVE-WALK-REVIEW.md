# Independent review of the two fresh native walks

**Prefer the first-last sample for further walking-sprite authoring. Neither
sample is approved as a finished seamless walk.** This is a comparison of two
stochastic outputs, not evidence that adding a last frame generally improves
H3. No private PixelLab checkpoint, conversion or quality parity is claimed.

## Scope and evidence

Read-only review used the frozen `EXPERIMENT.json`, `LIVE-RESULTS.json` and
`LIVE-DECODED.json` under
`/home/astra/artifacts/pixellab-motion-pipeline-20261014`. Packet reads confirmed
the same literal prompt SHA
`2f078a8fd63d6c23ef8aacc95d5a051006cf0d1e3741f0af0b828e11a1b3070e`
and PNG SHA `e63340b333df3354948b4ee707b2e4bfa23ca901f6b464a941e2ff06281d4a5e`.
The second packet adds that same PNG as `last_frame`; no shared seed is known.

All214 decoded rasters were checked against their immutable Store hashes and
screened in the existing chronological107-frame grids and overviews. Enlarged
12-phase sheets per case and additional first-last boundary sheets were read
for gait/gear details. This is static chronological visual review, **not a
timed playback or gameplay foot-contact acceptance test**. Each case has107
opaque768×768 frames with1/24-second holds, total107/24seconds.

New diagnostic-only QA sheets, source pins and `REVIEW-INPUTS.json` are under
`/home/astra/artifacts/pixellab-motion-walk-review-20261014`.
They retain whole-canvas registration and use nearest resizing for viewing;
no masking, palette processing, recentering, interpolation or art repair was
performed. No provider, auth or paid call was made.

## Observations

| Criterion | First-only | First-last |
|---|---|---|
| Walk readability | Alternating steps are visible, but the torso repeatedly opens toward the viewer, changing the carried silhouette substantially. Frames24–36 show a markedly frontal shield-and-torso presentation. | Clearer side-oriented alternating stride, with forward extension, passing legs and recovery phases. Useful examples are16–28,34–46 and52–64. Some torso yaw remains. |
| Anatomy | No gross extra or detached limb is apparent in the screened sequence. Crossing legs and the changing torso view make support-leg identity less clear, especially around20/32/56. | Two-leg silhouette is generally easier to follow. Knees bend and boots recover, but crossing phases28–31 and68–71 occlude the far leg; exact knee/ankle mechanics and planted contact are not certified. |
| Gear | Sword changes from upward/horizontal carry12–20 to downward carry24–36, crossing the leg silhouette. Shield broadens substantially with the frontal turn. This is awkward carry motion; overlap alone does not prove blade penetration. | Sword, shield, blue tunic and shoulder armor remain recognizable. Blade pitch, apparent outline/length, grip region and shield exposure still change across phases. These are not proven rigid attachments or stable pixel details. |
| Framing | Whole character, boots, shield and blade remain inside the screened canvas. Background changes from black at0 to nearly white immediately afterward, despite opaque pixels. | Whole character and gear remain within the screened canvas; black background is retained. Adequate margins do not establish a fixed root, pivot or ground plane. |
| End behavior | Starts and ends in a standing presentation, with walking between. Whole107 frames do not form a constant walk loop. | Also transitions from/to the standing anchor around the useful walking middle. Endpoint resemblance does not establish pixel identity or a seamless internal cycle. |

Both preserve the broad hero identity. Neither has the stable indexed shapes,
joint declarations, foot-contact guarantees or immutable gear geometry of an
authored rig. Background removal or a77-color palette cannot repair a bad
native pose, sliding contact, grip change or loop seam.

## Candidate selection, explicitly provisional

Use **first-last `[14,94)`** as an80-native-frame active-walk region for
one-shot inspection: original duration80/24 =10/3seconds. Keep all107 original
frames and source PTS separately; trimming is an authored derivative.

For a single-cycle authoring trial, use **first-last `[18,58)`**:40 native
frames, duration40/24 =5/3seconds. This contains both leg advances and excludes
the anchored start/settle. Enlarged18/58 leg silhouettes align more closely
than the initially considered16/52 pair:52 remains in a higher-knee phase.
However,18 and58 have different sword pitch/shield exposure. **The proposed
crop is not approved as seamless.** Inspect its actual57→18 wrap in timed
playback before committing a loop, and repair only through explicit authoring.

An optional eight-pose diagnostic is native indices
`[18,23,28,33,38,43,48,53]`, with declared5/24-second holds each. These are
inspection samples, not inferred provider sprite FPS or approved final poses.
The last-to-first transition still needs inspection. Do not independently
recenter frames to hide root drift or silently shorten the cycle.

Verdict: **conditional walking-source candidate, first-last preferred in this
pair; production anatomy/contact/gear/loop acceptance remains open**. Review
the masked/palette derivative separately against these raw poses, then check
the intended game scale and clock. No numerical quality target is asserted.
