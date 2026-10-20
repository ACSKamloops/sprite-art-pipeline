# ImageGen alternative when video quota is exhausted

Use this when replacing a video-paint provider with reference-conditioned still-image generation. A visually strong atlas is insufficient: assess the intervening motion and both endpoint joins before scaling the route to other actions.

The tested case is `/home/astra/projects/rpg-hero-animation/work/imagegen-alternative-v1/README.md`. It used two built-in ImageGen calls and zero new H3 calls. The tool name does not establish that Google Imagen was used. Existing painted walk controls originally used H3 motion, so reusing them does not prove a fully new ImageGen-only gait.

## Tested separation of responsibilities

- Keep appearance, authored whole-body pose guide and exact endpoint PNGs as separate inputs. Label their roles in the literal prompt and retain their hashes and actual image bytes. In this case, the pickup guide had eight slots, including two identical neutral endpoints; the walk guide had two painted endpoints and two primitive intermediate poses.
- Ask for transparent output and retain the raw RGBA. Make declared native-resolution and alpha derivatives separately. This test used one whole-sheet nearest sampling map and a global alpha128 threshold. Main pickup paint had partial alpha even when visually opaque; counting only alpha255 would incorrectly call it empty.
- Measure atlas layout before extraction. The pickup output enlarged the hero and shifted its whole second row. A common row offset was supported by the two requested-identical neutral poses' hair/eye/belt/sole positions. One global body scale/translation then applied to all generated poses. Such evidence can support a layout correction; do not infer a common offset from unrelated airborne/crouching poses or fit every pose to its bounding box.
- Preserve source-coordinate maps and unregistered cells. Registration does not repair anatomy, contact or temporal spacing.
- Enforce immutable endpoints outside the generator by copying original PNG bytes. Both calls redrew the requested anchors. Exact compositor anchors are truthful preservation; they do not establish compatible interior anatomy or paint.
- Save positive rational holds, one-shot/loop semantics and editable sources. Inspect all predecessor/current pairs at native size and enlarged over light/dark/colored backgrounds. Use actual timed playback for human motion acceptance.

## What the experiment established

The new pickup followed a recognizable bend, low reach and return. Independent ordered-image review rated the eight-pose version7.5/10. Removing a generated upright overshoot while retaining every other PNG byte produced7.7/10. The deleted3/24s was assigned to final ready, preserving a1s action; the longer terminal hold might delay gameplay completion and is not a responsiveness approval. Broad bend/recovery steps and generated-to-reference paint changes remained. This is a useful coarse prototype, not H3 quality parity or finished contact behavior.

The walk call supplied two attractive full-body drawings, but both were broad extended steps rather than the requested passing-to-contact progression. Copying exact endpoints still left large torso/arm/stride changes at both joins. Its bounded four-pose,1/4s fragment received6.2/10 and failed the intended bridge role. Retiming or increasing frame count would not create the missing passing silhouette. Inspect both anchors against the generated interiors before using an interior as another generation's appearance authority.

An older16-paint walk had a similar-pose seam. Mapping holds back to source phases increased that seam neighborhood from5/16s to1/3s, despite preserving the1.25s period. Keep equal-duration timing controls; source-correct weighting and perceived smoothness are separate judgments. The older complete painted walk is not evidence that the new two-inbetween call succeeded.

Technical evidence included exact APNG delay/RGBA verification, a real LibreSprite save/reopen/import and atlas roundtrip, SpriteFrames save/reload and every source-clock tick,93 OpenGL pose readbacks and279 browser frame/background comparisons. These certify the declared pixels/export/clock, not artistic motion. Review ratings were history-disclosed ordered-image judgments; uninterrupted human motion acceptance remained open.

## Next experiment decision

For an accepted appearance with rejected motion, first repair the actual passing/contact key poses against both endpoints. A bounded local or generated pose repair should change one demonstrated defect and undergo the same pair review. Do not batch an entire action library from a failed bridge or claim deterministic image-generation reproduction. Retained raw outputs permit deterministic offline assembly; another generation can differ.
