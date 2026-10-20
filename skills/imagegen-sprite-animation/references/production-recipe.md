# ImageGen key-art production

## Inputs and reference roles

For a new character, obtain or create a strong native-scale master first. An existing character needs an accepted appearance reference; an animation also needs a motion brief or pose guides. Record native painted height separately from canvas dimensions. A 192px stage does not imply a 192px tall actor. Keep the user's modern/painted/pixel style; do not impose a 16-color palette or a retro bit-depth.

Label every actual tool input:

- **Edit target:** the image whose composition and requested protected areas should persist.
- **Appearance reference:** identity, costume, palette, material treatment; not the replacement pose.
- **Pose guide:** shoulder/elbow/wrist/root positions and silhouette; not final paint.
- **Allowed-region guide:** where the requested replacement may be composited. A guide shown to the model is not proof that protected pixels survived.
- **Neighboring-pose context:** preceding/following keys and endpoints; prevents a good isolated drawing becoming inconsistent between frames.

If the user supplied only one still, do not imply it contains unseen side/back art. A proxy or simple rig may provide a pose guide, but actual Blender character rendering requires geometry, materials and a rig. Do not install/generate a local model just to fill a pipeline stage.

## Tool execution

Use the available built-in ImageGen tool and its actual schema. Inspect local edit images first. Pass exact local references when supported by that tool; otherwise use the supported recent-image edit mechanism. Do not invent seed, output-path, fidelity or mask parameters. Request actual transparency when appropriate, and preserve the returned alpha. Copy project assets from the actual returned location into the work area.

Record the **literal tool prompt**, actual input files/hashes, actual output bytes/dimensions, tool identity and later transformations. If a longer authoring brief was shortened before submission, retain both and distinguish them. Do not claim a prompt constraint was obeyed until inspecting the produced pixels. Do not make another paid call merely to repackage these methods.

## Adaptable complete-limb prompt

Use only the lines relevant to the requested work. Coordinates and proportions below are fields to measure, not universal sprite defaults.

```text
Use case: precise-object-edit.
Asset type: <game sprite key poses / missing bridge cels>.
Input1 is the edit target and authoritative layout: <rows/columns/cell size>.
Input2 is appearance/material reference only; it must not replace the poses.
Input3, if supplied, marks the allowed replacement region.

Repaint only <named limb/part> in <specified cells>. Paint the entire connected
<shoulder/upper limb/elbow/forearm/hand> as one coherent surface. Keep the
opposite limb distinct. Preserve <body/head/feet, stage scale, camera, light,
padding, costume and endpoint contract>. Match native pixel-cluster scale.

Required poses in reading order:
<one concrete description per cell, with distinct joint/reach relationships>.
Keep <closed hand / accessory> a consistent volume, with traceable wrist/elbow
and the same material shading. No detached parts, doubled cuff or old limb.

No labels, guides, words, floor, cast shadow or extra effects unless requested.
Transparent background. Keep the declared grid and proportions.
```

For a generation rather than an edit, change the role/intent accordingly; do not describe nonexistent edit targets. A modest sheet of related keys can preserve context, but individual unrelated assets need their own actual calls/prompts. Large “all RPG animations” sheets can conceal weak poses and drift: finish one useful action before scaling the bank.

The retained literal requests are under `assets/prompts/`. They are historical inputs, not guaranteed recipes: one requested bent elbow became straighter, and a requested recoil reach was only partly met. The fourth-call bridge prompt produced extra drawings but weaker glove/bracer continuity than the selected source-hand route.

## Registration and compositing

1. Read the actual raster dimensions, cell boundaries and alpha. The tested square return was1254px, with627px cells, despite a1536px input/request. Those dimensions are evidence from one call, not provider constants.
2. Establish one scale/placement for the sheet, recording any genuine row offset. Do not recenter each pose from its own bounding box. That hides motion drift and destroys attachment/ground relationships.
3. Use nearest-neighbor transport when preserving native pixel clusters. Evaluate at native game size and nearest 2x, not only a flattering large preview. A downsample is not proof of pixel-art quality.
4. Composite complete replacement paint under a declared native mask. Preserve outside-maskRGBA exactly. Include transparent replacement pixels so the old arm does not remain behind the new one.
5. Inspect silhouette, elbow/wrist join, glove/bracer mass, occlusion and neighboring keys. One alpha component does not prove good anatomy; a legitimate occlusion is not automatically a detached limb.

## Alpha is a visual choice

Modern sprites may use soft alpha. Compare against the established treatment on light/dark/colored backgrounds. Near-opaque generated interiors can accompany a soft fringe; do not call the whole limb transparent based on the count of partial-alpha pixels. A 128 threshold was a tested candidate for a binary-alpha source, not a general requirement. Record retainedRGB, removed fringe and actual changed pixels when thresholding. Normalize hiddenRGB under zero alpha explicitly if the target renderer requires it; distinguish that from literal rawRGBA equality.

Do not use alpha cleanup as a substitute for repainting a swollen glove or mismatched plate. The sprite's volume and material must stay coherent before transport is promoted.
